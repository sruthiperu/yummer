# Recipe tags from source tags, time, nutrition, ingredients

import re

TAGS: list[str] = ["main-course", "side-dish", "protein", "vegetarian", "vegan", "gluten-free", "keto", "low-calorie", "under-15-min", "under-30-min", "under-45-min", "under-60-min"]
TAG_SET = frozenset(TAGS)
DIETARY_TAGS = frozenset({"vegetarian", "vegan", "gluten-free"})

# food.com source tag
SOURCE_TAG_MAP: dict[str, str] = {"vegetarian": "vegetarian", "vegan": "vegan", "gluten-free": "gluten-free", "low-calorie": "low-calorie",
                                  "high-protein": "protein", "main-dish": "main-course", "side-dishes": "side-dish",
                                  "main-course": "main-course", "side-dish": "side-dish", "keto": "keto",       # not from food.com
}

TITLE_KEYWORD_MAP: dict[str, list[str]] = {"keto": [r"keto"], "vegan": [r"vegan"], "vegetarian": [r"vegetarian"], "gluten-free": [r"gluten[\s-]?free"], "low-calorie": [r"low[\s-]?calorie", r"low[\s-]?cal"],
                                           "protein": [r"high[\s-]?protein", r"protein"], "main-course": [r"main[\s-]?course", r"main[\s-]?dish"], "side-dish": [r"side[\s-]?dish"]}
TITLE_KEYWORD_PATTERNS: dict[str, list[re.Pattern]] = {tag: [re.compile(rf"\b{p}\b", re.IGNORECASE) for p in patterns] for tag, patterns in TITLE_KEYWORD_MAP.items()}

# keto macro thresholds
KETO_MAX_CARB_CAL_PCT = 0.10
KETO_MIN_FAT_CAL_PCT = 0.60

# high protein threshold
PROTEIN_MIN_CAL_PCT = 0.20

TIME_BUCKETS: list[tuple[int, str]] = [(15, "under-15-min"), (30, "under-30-min"), (45, "under-45-min"), (60, "under-60-min")]


def time_bucket(total_time: int | None) -> str | None:
    if total_time is None:
        return None
    
    for limit, tag in TIME_BUCKETS:
        if total_time <= limit:
            return tag
    
    return None


def is_keto(nutrition: dict | None) -> bool:
    if not nutrition:
        return False
    
    calories = nutrition.get("calories")
    carbs = nutrition.get("carbs")
    total_fat = nutrition.get("total_fat")
    if not calories or calories <= 0 or carbs is None or total_fat is None:
        return False
    
    carb_pct = (float(carbs) * 4) / float(calories)
    fat_pct = (float(total_fat) * 9) / float(calories)
    
    return carb_pct <= KETO_MAX_CARB_CAL_PCT and fat_pct >= KETO_MIN_FAT_CAL_PCT


def is_high_protein(nutrition: dict | None) -> bool:
    if not nutrition:
        return False
    
    calories = nutrition.get("calories")
    protein = nutrition.get("protein")
    if not calories or calories <= 0 or protein is None:
        return False
   
    return (float(protein) * 4) / float(calories) >= PROTEIN_MIN_CAL_PCT


def dietary_tags_from_ingredients(ingredient_flags: list[dict] | None) -> set[str]:
    """
    derive vegetarian/vegan/gluten-free from linked ingredient flags
    """
    if not ingredient_flags:
        return set()

    has_nonveg = any(f.get("is_vegetarian") is False for f in ingredient_flags)
    has_veg = any(f.get("is_vegetarian") is True for f in ingredient_flags)
    has_nonvegan = any(f.get("is_vegan") is False for f in ingredient_flags)
    has_vegan = any(f.get("is_vegan") is True for f in ingredient_flags)
    has_gluten = any(f.get("is_gluten_free") is False for f in ingredient_flags)
    has_gf = any(f.get("is_gluten_free") is True for f in ingredient_flags)

    found: set[str] = set()
    if not has_nonveg and has_veg:
        found.add("vegetarian")
    if not has_nonvegan and has_vegan:
        found.add("vegan")
        found.add("vegetarian")
    if not has_gluten and has_gf:
        found.add("gluten-free")
    
    return found


def dietary_tags_from_ingredient_agg(agg: dict | None) -> set[str]:
    """
    derive dietary tags from ingredient booleans
    """
    if not agg:
        return set()
    
    ingredient_flags: list[dict] = []
    
    if agg.get("has_nonveg"):
        ingredient_flags.append({"is_vegetarian": False})
    elif agg.get("has_veg"):
        ingredient_flags.append({"is_vegetarian": True})
    if agg.get("has_nonvegan"):
        ingredient_flags.append({"is_vegan": False})
    elif agg.get("has_vegan"):
        ingredient_flags.append({"is_vegan": True})
    if agg.get("has_gluten"):
        ingredient_flags.append({"is_gluten_free": False})
    elif agg.get("has_gf"):
        ingredient_flags.append({"is_gluten_free": True})
    
    return dietary_tags_from_ingredients(ingredient_flags)


def compute_dietary_tags(source_tags: list | None, title: str | None, ingredient_flags: list[dict] | None = None, ingredient_agg: dict | None = None) -> set[str]:
    """
    union dietary tags from source tags, title keywords, and ingredients
    """

    found: set[str] = set()
    tag_set = {str(t).lower() for t in (source_tags or [])}

    for src, curated in SOURCE_TAG_MAP.items():
        if curated in DIETARY_TAGS and src in tag_set:
            found.add(curated)

    found |= tags_from_title(title) & DIETARY_TAGS
    found |= dietary_tags_from_ingredients(ingredient_flags)
    found |= dietary_tags_from_ingredient_agg(ingredient_agg)

    if "vegan" in found:
        found.add("vegetarian")
    
    return found


def merge_dietary_tags(current_tags: list | None, new_dietary: set[str]) -> list[str]:
    """
    replace only dietary tags; keep all other tags in canonical order
    """
    current = set(current_tags or [])
    non_dietary = current - DIETARY_TAGS
    final = non_dietary | new_dietary
    
    return [t for t in TAGS if t in final]


def tags_from_title(title: str | None) -> set[str]:
    """
    deturn tags whose keywords appear in the recipe title
    """
    
    if not title:
        return set()
    found: set[str] = set()
    
    for tag, patterns in TITLE_KEYWORD_PATTERNS.items():
        if any(p.search(title) for p in patterns):
            found.add(tag)
    
    return found


def compute_curated_tags(source_tags: list | None, total_time: int | None, nutrition: dict | None, title: str | None = None, ingredient_flags: list[dict] | None = None) -> list[str]:
    """
    derive tags from raw food.com tags, time, nutrition, title, and ingredients
    """
    
    found: set[str] = set()
    tag_set = {str(t).lower() for t in (source_tags or [])}

    for src, curated in SOURCE_TAG_MAP.items():
        if src in tag_set:
            found.add(curated)

    if is_high_protein(nutrition):
        found.add("protein")

    if is_keto(nutrition):
        found.add("keto")

    bucket = time_bucket(total_time)
    if bucket:
        found.add(bucket)

    found |= tags_from_title(title)
    found |= compute_dietary_tags(source_tags, title, ingredient_flags=ingredient_flags)

    return [t for t in TAGS if t in found]
