import re
from app.models.recipe import Ingredient
from sqlalchemy import select
from .ingredient_patterns import patterns, food_types, allergens


UNITS = (
    r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|"
    r"ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|ml|l|"
    r"pinch|dash|can|cans|clove|cloves|package|packages|slice|slices|"
    r"piece|pieces|head|bunch|sprig|sprigs|stick|sticks"
)
MERGED = {"sweetonion": "sweet onion", "hashbrown": "hash brown", "hashbrownpotato": "hash brown potato", "greenonion": "green onion", "redonion": "red onion", "basmatirice": "basmati rice"}


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

    # make plural ingredients singular
    if name.endswith("ves"):
        name = name[:-3] + "f"
    elif name.endswith("ies"):
        name = name[:-3] + "y"
    elif name.endswith("es") and len(name) > 4 and not name.endswith(("bles", "ches", "ges", "les", "mes")):
        name = name[:-2]
    elif name.endswith("s") and len(name) > 3 and not name.endswith(("ss", "us", "is")):
        name = name[:-1]

    return name.strip()


def _flags_from_key(name, key):
    ing_info = dict(food_types[key])
    ing_info["allergens"] = allergens.get(key, allergens.get(name, []))
    return ing_info


def get_flags(name):
    """
    given: string (ingredient's canonical form); returns food type and diet flags
    """
    default_vals = {"type": "other", "vegan": False, "vegetarian": False, "gluten_free": False, "allergens": []}

    if not name:
        return default_vals.copy()

    name = normalize_ingredient(name)

    if name in food_types:
        return _flags_from_key(name, name)

    # longest-key suffix match: "mexican oregano" -> "oregano"
    for key in sorted(food_types, key=len, reverse=True):
        if name == key or name.endswith(" " + key):
            return _flags_from_key(name, key)

    return default_vals.copy()


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
    name = re.sub(
        r"\b(lemon|lime|orange|grapefruit)s?\s*,?\s*"
        r"(?:juice and (?:zest|rind) of|juice and rind of|rind of|juice of|zest of)\b", r"\1", name)
    name = re.sub(
        r"\b(lemon|lime|orange|grapefruit)\s*,?\s*(?:juice|zest)\s+of\b",
        r"\1", name)
    name = re.sub(r",\s*(?:juice|zest)\s+of\b", "", name)

    for bad, good in MERGED.items():
        if bad in name: name = name.replace(bad, good)

    # temperature/state before broth/stock: "hot chicken broth" -> "chicken broth"
    name = re.sub(
        r"\b(hot|warm|cold|boiling)\s+(?=(?:chicken|beef|vegetable|fish|bone)\s+(?:broth|stock)\b)",
        "",
        name,
    )
    name = re.sub(r"\s+", " ", name).strip()

    return name.strip()


def get_allergens(name):
    name = normalize_ingredient(name)
    if name in allergens: return allergens[name]

    for key in sorted(allergens, key=len, reverse=True):
        if name == key or name.endswith(" " + key): return allergens[key]
    
    return []