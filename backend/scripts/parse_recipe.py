# Takes one recipe (row) from final_dataset.csv and parses it into a dict (for the database)

import ast      
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
        
        size = None
        if res.size:
            size = res.size.text
        
        return quantity, unit, size, ingredient
    except:
        return None, None, None, strip_units(text)

def parse_nutrition(info):
    """ 
    given: list; returns dict
    """

    try:
        vals = convert_str_to_list(info)
        if not vals or len(vals) < 7:
            return None
        
        return {"calories": vals[0], "total_fat": vals[1], "sugar": vals[2], "sodium": vals[3], "protein": vals[4], 
                "saturated_fat": vals[5], "carbs": vals[6]}
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


def parse_row(row):
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
    recipe_data = {'name': row['name'], 'directions': directions, 'total_time': total_time, 'nutrition': nutrition, 'tags': tags, 'date': date, 'link': row['link']}
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

        quantity, unit, size, _ = get_quantity(nlg_text)

        ingredients_data.append({
            'text': nlg_text,
            'quantity': quantity,
            'unit': unit,
            'size': size,
            'ingredient': ing_name,
        })

    return recipe_data, ingredients_data


def clean_ingredient_text(text):
    """
    pre-clean recipenlg line before parsing quantity, name
    """

    if not text:
        return None
    
    text = text.lower().strip()
    text = re.split(r"\s+or\s+", text, maxsplit=1)[0]
    text = re.sub(
        r",\s*(for garnish|optional|to taste|divided|as needed|"
        r"pressed and drained|pressed|drained|thawed|at room temperature)\s*$",
        "", text)
   
    # remove leading size in parens (e.g. 1 (6 1/2 ounce) box of quinoa)
    text = re.sub(r"^\d*\s*\([^)]+\)\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text or None

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


