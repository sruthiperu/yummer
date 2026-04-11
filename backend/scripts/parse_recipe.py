# Takes one recipe (row) from final_dataset.csv and parses it into a dict (for database)

import ast      
import pandas as pd
import hashlib
from ingredient_parser import parse_ingredient
from datetime import datetime


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
    
def get_quantity(text):
    """ 
    get quantity of ingredient (e.g. "2" given "2 eggs")
    """

    try:
        res = parse_ingredient(text)
        quantity, unit = None, None
        if res.amount:
            quantity = str(res.amount[0].quantity) if res.amount[0].quantity else None
            unit = str(res.amount[0].unit) if res.amount[0].unit else None
        
        ingredient = text
        if res.name:
            ingredient = res.name[0].text
        
        size = None
        if res.size:
            size = res.size.text
        
        return quantity, unit, size, ingredient
    except:
        return None, None, None, text

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

    name = row['name']
    
    # parse ingredients
    # foodcom_ingredients = convert_str_to_list(row['foodcom_ingredients'])
    recipenlg_ingredients = convert_str_to_list(row['recipenlg_ingredients'])
    
    # parse directions into list of dicts
    instructions = convert_str_to_list(row['directions'])
    directions = []
    for i, step in enumerate(instructions):
        directions.append({'step_num': i + 1, 'direction': step.strip()})

    # parse total time
    total_time = parse_time(row['minutes'])

    # ADD DIFFICULTY

    # parse nutrition info
    nutrition = parse_nutrition(row['nutrition'])
    # parse tags
    tags = convert_str_to_list(row['tags'])

    # parse date
    date = parse_date(row['date'])


    recipe_data = {'name': row['name'], 'directions': directions, 'total_time': total_time, 'nutrition': nutrition, 'tags': tags,
                   'date': date, 'link': row['link']}
    

    ingredients_data = []
    for text in recipenlg_ingredients:
        if not text:
            continue

        quantity, unit, size, ing_name = get_quantity(text)

        if not ing_name: ing_name = text      # use original text when needed
        
        ingredients_data.append({'text': text, 'quantity': quantity, 'unit': unit, 'size': size, 'ingredient': ing_name})


    return recipe_data, ingredients_data


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
            
            # Check for None values
            if recipenlg_text is None:
                none_count += 1
                recipes_with_none.append({'row': idx, 'recipe': name, 'ingredient_index': i, 'recipenlg': recipenlg_text})
    
    print("\n" + "="*60)
    print("SCAN RESULTS")
    print("="*60)
    print(f"Rows scanned: {len(df)}")
    print(f"Total ingredient positions checked: {total_ingredients_checked}")
    print(f"Total None values found: {none_count}")
    
    if recipes_with_none:
        print(f"\nFirst 20 None values:")
        print("-"*60)
        for item in recipes_with_none[:20]:
            print(f"Row {item['row']}: '{item['recipe']}' - Ingredient {item['ingredient_index']}")
            print(f"   recipenlg: {item['recipenlg']}\n")