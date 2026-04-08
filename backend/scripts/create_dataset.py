# Create a csv file with all the recipes in BOTH the Food.com and RecipeNLG datasets (226891 recipes)
# columns: name (RecipeNLG), ingredients_nlg (RecipeNLG), ingredients_foodcom (Food.com), directions (RecipeNLG),
#          nutrition (Food.com), link (RecipeNLG)

import pandas as pd
import re
import ast


foodcom_df = pd.read_csv("Foodcom_dataset.csv")         # 'id' 
recipenlg_df = pd.read_csv("RecipeNLG_dataset.csv")       # 'link' 

# pd.set_option('display.max_rows', None)      # show all rows
# pd.set_option('display.max_columns', None)   # show all columns
# pd.set_option('display.max_colwidth', None)  # show all of column

# find foodcom_id of each recipe in RecipeNLG
def get_id_from_link(link):      # get foodcom_id from RecipeNLG link
    if isinstance(link, str) and 'food.com' in link:
        match = re.search(r'-(\d+)$', link)
        if match:
            return int(match.group(1))
    return None

# get only Food.com recipes in RecipeNLG
recipenlg_df['foodcom_id'] = recipenlg_df['link'].apply(get_id_from_link)
foodcom_in_nlg = recipenlg_df[recipenlg_df['foodcom_id'].notna()]

foodcom_selected = foodcom_df[['id', 'minutes', 'ingredients', 'nutrition', 'tags', 'submitted']]
recipenlg_selected = recipenlg_df[['foodcom_id', 'title', 'ingredients', 'directions', 'link']]


merged_with_id = pd.merge(foodcom_selected, recipenlg_selected, left_on='id', right_on='foodcom_id', how='inner')
merged = pd.DataFrame({'name': merged_with_id['title'], 'foodcom_ingredients': merged_with_id['ingredients_x'],
                       'recipenlg_ingredients': merged_with_id['ingredients_y'], 'directions': merged_with_id['directions'],
                       'minutes': merged_with_id['minutes'], 'nutrition': merged_with_id['nutrition'], 
                       'tags': merged_with_id['tags'], 'date': merged_with_id['submitted'], 'link': merged_with_id['link']})        # without id columns

merged.to_csv("../data/final_dataset.csv", index=False)
# merged.to_json('final_dataset.json', orient='records', indent=3)  -> too long
# foodcom_ingredients -> ingredients w/o quantities; recipenlg_ingredients -> ingredients w/ quantities


