import re
from app.models.recipe import Ingredient
from sqlalchemy import select
from .ingredient_patterns import patterns, food_types, allergens, substitute_markers, vegan_markers, animal_allergens, non_veg_markers, dairy_egg_markers, gluten_markers, plant_markers, embedded_non_veg_markers


UNITS = (r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|ml|l|pinch|dash|can|cans|clove|cloves|package|packages|slice|slices|piece|pieces|head|bunch|sprig|sprigs|stick|sticks")
MERGED = {"sweetonion": "sweet onion", "hashbrown": "hash brown", "hashbrownpotato": "hash brown potato", "greenonion": "green onion", "redonion": "red onion", 
          "basmatirice": "basmati rice", "chickenpiec": "chicken", "chickenpiece": "chicken", "chickene": "chicken", 
          "canned stewed tomatoes": "stewed tomatoes", "canned stewed tomato": "stewed tomatoes", "chif": "chives", "clof": "cloves", "cilantroleaf": "cilantro", 
          "greekyogurt": "greek yogurt", "plainyogurt": "plain yogurt", "frozenyogurt": "frozen yogurt", "nonfatyogurt": "nonfat yogurt", "lowfatyogurt": "low-fat yogurt", "low-fatyogurt": "low-fat yogurt", "fat-freeyogurt": "fat-free yogurt", "vanillayogurt": "vanilla yogurt"}
UNCHANGED_PLURALS = frozenset({"chives", "cloves"})


def normalize_ingredient(name):
    """
    given: string (ingredient); returns string (ingredient's canonical form)
    "white flour" -> "flour"
    """
    if not name:
        return name

    name = pre_clean_ingredient(name)
    for pattern, canonical in patterns:
        name = re.sub(pattern, canonical, name).strip()

    name = re.sub(r"\s+(pieces?|pcs?)\s*$", "", name)
    name = re.sub(r"^(\w+)(pieces?|piec)$", r"\1", name)
    if name in UNCHANGED_PLURALS or any(name.endswith(f" {p}") for p in UNCHANGED_PLURALS):
        return name.strip()

    name = re.sub(r"\bleaves\b", "leaf", name)

    # make plural ingredients singular
    if name.endswith("ies"):
        name = name[:-3] + "y"
    elif name.endswith("es") and len(name) > 4 and not name.endswith(("bles", "ches", "ges", "les", "mes", "ces")):
        name = name[:-2]
    elif name.endswith("s") and len(name) > 3 and not name.endswith(("ss", "us", "is")):
        name = name[:-1]
    # name = re.sub(r"\bstewed tomato\b", "stewed tomatoes", name)

    return name.strip()


def _flags_from_key(name, key):
    ing_info = dict(food_types[key])
    ing_info["allergens"] = allergens.get(key, allergens.get(name, []))
    return ing_info


def infer_dietary_flags(name: str, flags: dict) -> dict:
    """
    fill NULL dietary flags from keyword patterns; non-veg overweights plant
    """
    
    if not name:
        return flags

    if non_veg_markers.search(name) or embedded_non_veg_markers.search(name):
        flags["vegetarian"] = False
        flags["vegan"] = False
        if flags.get("gluten_free") is None:
            flags["gluten_free"] = True
        return flags

    if dairy_egg_markers.search(name):
        if flags.get("vegan") is None:
            flags["vegan"] = False
        if flags.get("vegetarian") is None:
            flags["vegetarian"] = True

    if gluten_markers.search(name):
        if flags.get("gluten_free") is None:
            flags["gluten_free"] = False

    if plant_markers.search(name):
        if flags.get("vegetarian") is None:
            flags["vegetarian"] = True
        if flags.get("vegan") is None:
            flags["vegan"] = True
        if flags.get("gluten_free") is None:
            flags["gluten_free"] = True

    return flags


def get_flags(name):
    """
    given: string (ingredient's canonical form); returns food type and diet flags
    """
    default_vals = {"type": "other", "vegan": None, "vegetarian": None, "gluten_free": None, "allergens": []}

    if not name:
        return default_vals.copy()

    original_name = name
    name = normalize_ingredient(name)
    flags = default_vals.copy()

    if name in food_types:
        flags = _flags_from_key(name, name)
    else:
        for key in sorted(food_types, key=len, reverse=True):
            if name == key or name.endswith(" " + key):
                flags = _flags_from_key(name, key)
                break

    resolved = get_allergens(name)
    if resolved:
        flags["allergens"] = list(dict.fromkeys(resolved + (flags.get("allergens") or [])))
    else:
        flags["allergens"] = flags.get("allergens") or []

    flags = infer_dietary_flags(name, flags)

    if substitute_markers.search(original_name):
        flags["allergens"] = [
            allergen for allergen in (flags.get("allergens") or [])
            if allergen not in animal_allergens
        ]
        flags["vegetarian"] = True
        if vegan_markers.search(original_name) or flags.get("vegan") is True:
            flags["vegan"] = True

    return flags


def apply_flags(ingredient, flags):
    """
    update ingredient model fields from get_flags; returns true if anything changed
    """
    
    changed = False

    if ingredient.food_type != flags["type"]:
        ingredient.food_type = flags["type"]
        changed = True
    if ingredient.is_vegan != flags["vegan"]:
        ingredient.is_vegan = flags["vegan"]
        changed = True
    if ingredient.is_vegetarian != flags["vegetarian"]:
        ingredient.is_vegetarian = flags["vegetarian"]
        changed = True
    if ingredient.is_gluten_free != flags["gluten_free"]:
        ingredient.is_gluten_free = flags["gluten_free"]
        changed = True
    
    new_allergens = flags.get("allergens") or None
    if ingredient.allergens != new_allergens:
        ingredient.allergens = new_allergens
        changed = True

    return changed


def pre_clean_ingredient(name):
    """
    strip NLG unnecessary additions before regex normalization
    """
    if not name:
        return name

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s*,\s*", ", ", name)

    # leading quantity/unit accidentally stored in ingredient name
    name = re.sub(rf"^[\d\s./\-]+(?:{UNITS})\b\.?\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(rf"^[\d\s./\-]+\s+", "", name)

    # formatting error: "lime , juice of" / "lemon, rind of" / "lime, juice and zest of" -> change to fruit noun
    name = re.sub(r"\b(lemon|lime|orange|grapefruit)s?\s*,?\s*"
                  r"(?:juice and (?:zest|rind) of|juice and rind of|rind of|juice of|zest of)\b", r"\1", name)
    name = re.sub(r"\b(lemon|lime|orange|grapefruit)\s*,?\s*(?:juice|zest)\s+of\b", r"\1", name)
    name = re.sub(r",\s*(?:juice|zest)\s+of\b", "", name)

    for bad, good in sorted(MERGED.items(), key=lambda x: len(x[0]), reverse=True):     # process longer phrase first
        if bad in name: name = name.replace(bad, good)

    # temp/state before broth/stock; ex. "hot chicken broth" -> "chicken broth"
    name = re.sub(r"\b(hot|warm|cold|boiling)\s+(?=(?:chicken|beef|vegetable|fish|bone)\s+(?:broth|stock)\b)", "", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name.strip()


def get_allergens(name):
    name = normalize_ingredient(name)
    if name in allergens: return allergens[name]

    for key in sorted(allergens, key=len, reverse=True):
        if name == key or name.endswith(" " + key): 
            return allergens[key]
    
    return []