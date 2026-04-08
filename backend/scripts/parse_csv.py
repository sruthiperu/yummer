import pandas as pd
from parse_recipe import parse_row

df = pd.read_csv("../data/final_dataset.csv")

for i, row in df.head(5).iterrows():
    recipe_data, ingredients_data = parse_row(row)
    print(f"recipe_data: {recipe_data}\n")
    print(f"ingredients_data: {ingredients_data}")
    print("\n\n")