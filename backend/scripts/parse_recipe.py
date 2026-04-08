# Takes one recipe (row) from final_dataset.csv and parses it into a dict (for database)

import ast      
import re
import hashlib
from ingredient_parser import parse_ingredient
from datetime import datetime


# given: string; return list
def convert_str_to_list(s):
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
    
# returns only quantity of ingredient (e.g. returns "2" given "2 eggs")
def get_quantity(text):
    try:
        res = parse_ingredient(text)
        quantity, unit = None, None
        if res.amount:
            quantity = str(res.amount[0].quantity) if res.amount[0].quantity else None
            unit = str(res.amount[0].unit) if res.amount[0].unit else None
        
        ingredient = text
        if res.name:
            ingredient = res.name[0].text
        
        return quantity, unit, ingredient
    except:
        return None, None, text

# given: list; returns dict
def parse_nutrition(info):
    try:
        vals = convert_str_to_list(info)
        if not vals or len(vals) < 7:
            return None
        
        return {"calories": vals[0], "total_fat": vals[1], "sugar": vals[2], "sodium": vals[3], "protein": vals[4], 
                "saturated_fat": vals[5], "carbs": vals[6]}
    except:
        return None
    
# given: string; returns datetime obj
def parse_date(date):
    try:
        return datetime.strptime(str(date), "%m-%d-%Y")
    except:
        return None


# parse entire row
# given: list; return dict
def parse_row(row):
    name = row['name']
    
    # parse ingredients
    foodcom_ingredients = convert_str_to_list(row['foodcom_ingredients'])
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
    

    # ingredients are in the same order in Food.com and RecipeNLG
    ingredients_data = []
    for foodcom_text, recipenlg_text in zip(foodcom_ingredients, recipenlg_ingredients):
        quantity, unit, _ = get_quantity(recipenlg_text)
        ingredients_data.append({'text': recipenlg_text, 'quantity': quantity, 'unit': unit, 'ingredient': foodcom_text.strip()})
    
    return recipe_data, ingredients_data
