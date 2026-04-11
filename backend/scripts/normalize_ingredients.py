from app.models.recipe import Ingredient
from sqlalchemy import select
import re
from .ingredient_patterns import patterns, food_types, allergens


def normalize_ingredient(name):
    """
    given: string (ingredient); returns string (ingredient's canonical form)
    "white flour" -> "flour"
    """

    name = name.lower().strip()
    for pattern, canonical in patterns:
        name = (re.sub(pattern, canonical, name)).strip()
    
    return name


def get_flags(name):
    """
    given: string (ingredient's canonical form); returns all flags (food type, vegan, vegetarian, gluten_free, allergens) for ingredient
    """

    default_vals = {"type": "other", "vegan": False, "vegetarian": False, "gluten_free": False}

    ing_info = food_types.get(name, default_vals)
    ing_info['allergens'] = allergens.get(name, [])

    return ing_info

