# Takes one recipe (row) from final_dataset.csv and parses it into a dict (for the database)

import ast      
import csv
import math
import pandas as pd
import re
from datetime import datetime
from ingredient_parser import parse_ingredient
from scripts.ingredient_match import resolve_canonical_name
from scripts.format_quantities import format_quantity, abbreviate_unit


UNITS = (
    r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|ml|l|kilogram|kilograms|milliliter|milliliters|liter|liters|"
    r"can|cans|box|boxes|clove|cloves|pinch|dash|package|packages|slice|slices|piece|pieces|head|bunch|sprig|sprigs|stick|sticks"
)

MANGLED_TO_FRACTION = {"12": "1/2", "14": "1/4", "34": "3/4", "13": "1/3", "23": "2/3"}

VOLUME_WEIGHT_UNITS = (
    r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|"
    r"ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|kilogram|kilograms|"
    r"ml|l|milliliter|milliliters|liter|liters|gallon|gallons|quart|quarts|pint|pints|"
    r"pinch|dash|fluid ounce|fluid ounces|fl oz"
)

COUNT_UNITS = r"clove|cloves|slice|slices|piece|pieces|head|heads|bunch|bunches|sprig|sprigs|stick|sticks"
COUNT_UNITS_SINGULAR = r"clove|slice|piece|head|bunch|sprig|stick"

def convert_str_to_list(s):
    """ 
    given: string; return list
    """

    try:
        lst = ast.literal_eval(s)   # "['milk', 'eggs']" -> ['milk', 'eggs']
        if isinstance(lst, list):
            return lst
        else:
            return []
    except:
        return []

def parse_time(t):
    try:
        time = int(t)
        return time
    except:
        return None
    
def extract_ingredient_name(parsed):
    """
    pick the best ingredient name span from parser output.
    joins all name parts; for multiple parts the joined string beats a single adjective span.
    """
    if not parsed or not parsed.name:
        return None

    parts = [n.text.strip() for n in parsed.name if getattr(n, "text", None) and n.text.strip()]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]

    joined = " ".join(parts)
    longest = max(parts, key=len)
    return joined if len(joined) >= len(longest) else longest


def extract_container_size(parsed, text):
    """
    pull container size from a second amount (ex. 14 ounce in "1 (14 ounce) can ...") or parenthetical
    """
    if parsed and parsed.amount and len(parsed.amount) > 1:
        second = parsed.amount[1]
        if second.quantity and second.unit:     # both quantity and unit should exist
            qty = format_quantity(str(second.quantity))
            unit = abbreviate_unit(str(second.unit))
            if qty and unit:
                return f"{qty} {unit}"

    if text:
        m = re.search(r"\(([^)]+)\)\s*(?:can|cans)\b", text, re.IGNORECASE)
        if m:
            inner = m.group(1).strip()
            parts = inner.split(None, 1)
            
            if len(parts) == 2:
                qty = format_quantity(parts[0])
                unit = abbreviate_unit(parts[1])
                
                if qty and unit: return f"{qty} {unit}"
            return inner

    return None


def get_quantity(text):
    """ 
    get quantity of ingredient (e.g. "2" given "2 eggs")
    """

    text = clean_ingredient_text(text)
    if not text:
        return None, None, None, None
    
    try:
        res = parse_ingredient(text)
        quantity, unit = None, None
        if res.amount:
            raw = str(res.amount[0].quantity) if res.amount[0].quantity else None
            quantity = format_quantity(raw)
            unit = abbreviate_unit(str(res.amount[0].unit)) if res.amount[0].unit else None
        
        ingredient = extract_ingredient_name(res)
        
        # try stripping units manually if parser fails
        if not ingredient:
            ingredient = strip_units(text)

        container_size = extract_container_size(res, text)

        return quantity, unit, container_size, ingredient
    except:
        return None, None, None, strip_units(text)

NUTRITION_DV = {
    "total_fat": 65,
    "sugar": 25,
    "sodium": 2400,
    "protein": 50,
    "saturated_fat": 20,
    "carbs": 300,
}


def pdv_to_amount(pct, daily_value):
    if pct is None:
        return None
    return round(float(pct) / 100 * daily_value, 1)


def pdv_to_whole_grams(pct, daily_value):
    if pct is None:
        return None
    return math.ceil(float(pct) / 100 * daily_value)


def parse_nutrition(info):
    """ 
    given: Food.com nutrition list [%DV for macros except calories]; returns dict in grams/mg
    """

    try:
        vals = convert_str_to_list(info)
        if not vals or len(vals) < 7:
            return None

        return {
            "calories": math.ceil(float(vals[0])) if vals[0] is not None else None,
            "total_fat": pdv_to_whole_grams(vals[1], NUTRITION_DV["total_fat"]),
            "sugar": pdv_to_whole_grams(vals[2], NUTRITION_DV["sugar"]),
            "sodium": pdv_to_amount(vals[3], NUTRITION_DV["sodium"]),
            "protein": pdv_to_amount(vals[4], NUTRITION_DV["protein"]),
            "saturated_fat": pdv_to_amount(vals[5], NUTRITION_DV["saturated_fat"]),
            "carbs": pdv_to_whole_grams(vals[6], NUTRITION_DV["carbs"]),
        }
    except:
        return None
    

def parse_date(date):
    """
    given: string; returns datetime obj
    """

    try:
        return datetime.strptime(str(date), "%m-%d-%Y")
    except:
        return None


def load_servings_by_recipe_id(csv_path):
    by_id = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            recipe_id = row.get("recipeid", "").strip()
            raw = row.get("recipeservings", "").strip()
            if not recipe_id or not raw or raw.lower() == "na":
                continue
            try:
                servings = int(float(raw))
            except (TypeError, ValueError):
                continue
            if servings > 0:
                by_id[recipe_id] = servings
    return by_id


def parse_servings_from_link(link, servings_by_id):
    match = re.search(r"-(\d+)$", str(link or "").strip())
    if not match:
        return None
    return servings_by_id.get(match.group(1))


def parse_row(row, servings_by_id=None):
    """
    parse recipe (1 row in csv file)
    given: list; return dict
    """

    foodcom_ingredients = convert_str_to_list(row['foodcom_ingredients'])
    recipenlg_ingredients = convert_str_to_list(row['recipenlg_ingredients'])

    # parse directions into list of dicts
    instructions = convert_str_to_list(row['directions'])
    directions = []
    for i, step in enumerate(instructions):
        directions.append({'step_num': i + 1, 'direction': step.strip()})

    total_time = parse_time(row['minutes'])
    nutrition = parse_nutrition(row['nutrition'])
    tags = convert_str_to_list(row['tags'])
    date = parse_date(row['date'])
    link = row['link']
    servings = parse_servings_from_link(link, servings_by_id) if servings_by_id else None
    recipe_data = {'name': row['name'], 'directions': directions, 'total_time': total_time, 'nutrition': nutrition, 'tags': tags, 'date': date, 'link': link, 'servings': servings}
    ingredients_data = []
    used_fc_indices = set()

    for nlg_text in recipenlg_ingredients:
        if not nlg_text:
            continue

        ing_name = resolve_canonical_name(
            nlg_text, foodcom_ingredients, used_fc_indices
        )
        if not ing_name:
            continue

        quantity, unit, container_size, _ = get_quantity(nlg_text)

        ingredients_data.append({
            'text': nlg_text,
            'quantity': quantity,
            'unit': unit,
            'container_size': container_size,
            'ingredient': ing_name,
        })

    return recipe_data, ingredients_data


def fix_mangled_fractions(text):
    """
    recover fractions where RecipeNLG dropped slashes (1/2 -> 12, 1/4 -> 14, etc.)
    """
    if not text:
        return text

    parens = []

    def save_paren(match):
        parens.append(match.group(0))
        return f" __PAREN_{len(parens) - 1}__ "

    text = re.sub(r"\([^)]*\)", save_paren, text)

    for mangled, fraction in MANGLED_TO_FRACTION.items():
        text = re.sub(
            rf"(?<![-/])\b(\d+)\s+{mangled}\s+({VOLUME_WEIGHT_UNITS})\b",
            rf"\1 {fraction} \2",
            text,
            flags=re.IGNORECASE,
        )

    for mangled, fraction in MANGLED_TO_FRACTION.items():
        text = re.sub(
            rf"(?<![-/])\b{mangled}\s+({VOLUME_WEIGHT_UNITS})\b",
            rf"{fraction} \1",
            text,
            flags=re.IGNORECASE,
        )

    for mangled in ("14", "34", "13", "23"):
        text = re.sub(
            rf"(?<![-/])\b{mangled}\s+({COUNT_UNITS})\b",
            rf"{MANGLED_TO_FRACTION[mangled]} \1",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        rf"(?<![-/])\b12\s+({COUNT_UNITS_SINGULAR})\b",
        r"1/2 \1",
        text,
        flags=re.IGNORECASE,
    )

    for i, original in enumerate(parens):
        text = text.replace(f"__PAREN_{i}__", original)

    return re.sub(r"\s+", " ", text).strip()


def clean_ingredient_text(text):
    """
    pre-clean recipenlg line before parsing quantity, name
    """

    if not text:
        return None
    
    text = text.lower().strip()
    text = fix_mangled_fractions(text)
    text = re.split(r"\s+or\s+", text, maxsplit=1)[0]
    text = re.sub(
        r"\([^)]*(?:\bif\b|\byou can\b|\bi like\b|\bi vary\b|\btype\b|\bamt\.?\b|\byour choice\b|\bor equivalent\b)[^)]*\)",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r",\s*(for garnish|optional|to taste|divided|as needed|pressed and drained|pressed|drained|thawed|at room temperature|room temperature)\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text or None


def get_display_name(raw):
    """
    ingredient name for display: strip qty/unit and NLG filler from raw line
    """
    cleaned = clean_ingredient_text(raw)
    if not cleaned:
        return None

    stripped = strip_units(cleaned)
    if stripped and stripped != cleaned:
        name = stripped
    else:
        _, _, _, parsed = get_quantity(raw)
        name = parsed or stripped or cleaned

    if not name:
        return None

    name = re.sub(r",\s*(if desired|optional|to taste|as needed).*$", "", name, flags=re.IGNORECASE).strip()
    return name or None

def strip_units(text):
    """
    strip leading quantity and unit when ingredient parser fails
    """

    if not text:
        return None
    text = text.strip()
    stripped = re.sub(rf"^[\d\s./\-]+(?:{UNITS})\b\.?\s*", "", text, flags=re.IGNORECASE).strip()
  
    # handle lines that begin with an unit but not a number
    stripped = re.sub(rf"^(?:{UNITS})\b\.?\s+", "", stripped, flags=re.IGNORECASE).strip()
    return stripped or None


if __name__ == "__main__":
    csv_path = "/Users/sruthiperumalla/Desktop/yummer/backend/data/final_dataset.csv"
    print(f"Loading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Total recipes: {len(df)}")
    
    none_count, total_ingredients_checked = 0, 0
    recipes_with_none = []

    
    for idx, row in df.iterrows():
        name = row['name']
        
        recipenlg_ingredients = convert_str_to_list(row['recipenlg_ingredients'])
        
        # check each ingredient
        for i, recipenlg_text in enumerate(recipenlg_ingredients):
            total_ingredients_checked += 1
            
            # check for none values
            if recipenlg_text is None:
                none_count += 1
                recipes_with_none.append({'row': idx, 'recipe': name, 'ingredient_index': i, 'recipenlg': recipenlg_text})
    
    print("SCAN RESULTS")
    print(f"rows scanned: {len(df)}")
    print(f"total ingredient positions checked: {total_ingredients_checked}")
    print(f"total None values found: {none_count}")
    if recipes_with_none:
        print(f"\nfirst 20 None values:")
        for item in recipes_with_none[:20]:
            print(f"row {item['row']}: '{item['recipe']}' - Ingredient {item['ingredient_index']}")
            print(f"\trecipenlg: {item['recipenlg']}\n")


