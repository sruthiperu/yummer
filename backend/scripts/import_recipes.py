# Import all recipes in dataset into database

import pandas as pd
import sys
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe, Ingredient, RecipeIngredient

from .normalize_ingredients import normalize_ingredient, get_flags
from scripts.parse_recipe import parse_row


def get_ingredient(db_session, name):
    """
    given: SQLAlchemy session, string (ingredient); returns ingredient object from database
    if ingredient not in database, creates it
    """

    canonical_name = normalize_ingredient(name)

    # search for ingredient's canonical form in database
    in_db = db_session.execute(select(Ingredient).where(Ingredient.name == canonical_name)).scalar_one_or_none()

    if in_db:
        # add alias if name != canonical_name and not in the ingredient's aliases list already
        if name != canonical_name:
            ing_aliases = in_db.aliases if in_db.aliases is not None else []
            if canonical_name not in ing_aliases:
                ing_aliases.append(canonical_name)
                in_db.aliases = ing_aliases
                db_session.flush()
        
        return in_db

    flags = get_flags(canonical_name)
    ingredient = Ingredient(name=canonical_name, aliases=[name] if canonical_name != name else None,
                            food_type=flags['type'], is_vegan=flags['vegan'], is_vegetarian=flags['vegetarian'], is_gluten_free=flags['gluten_free'])

    db_session.add(ingredient)
    db_session.flush()
    return ingredient


def import_recipes(dataset_path, limit):
    """
    given: dataset_path (path to csv file) and limit (number of recipes to import into database)
    imports the first 'limit' number of recipes from dataset into database
    """

    df = pd.read_csv(dataset_path)
    # print(f"length of dataset: {len(df)}, limit: {limit}")

    db = SessionLocal()
    inserted, skipped, failed = 0, 0, 0

    try:
        for i, row in df.head(limit).iterrows():

            try:
                recipe_data, ingredients_data = parse_row(row)
                if not recipe_data or not ingredients_data: 
                    skipped += 1
                    continue
                    
                # create recipe
                recipe = Recipe(**recipe_data)        # no ingredients
                db.add(recipe)
                db.flush()

                # for each ingredient
                for ing_data in ingredients_data:

                    if ing_data['ingredient'] is None:
                        continue
                    ing = get_ingredient(db, ing_data['ingredient'])
                    if not ing:
                        continue

                    # link recipe and ingredient
                    link = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=ing_data.get('quantity'), 
                                            unit=ing_data.get('unit'), raw_ingredient=ing_data.get('text'))
                    db.add(link)
                inserted += 1

                if inserted % 100 == 0: db.commit()

            except Exception as e:
                print(f"row {i} | error: {e}")
                # raise
                failed += 1
                db.rollback()
                continue
        
        db.commit()

        print("IMPORT DONE")
        print(f"inserted {inserted}, skipped {skipped}, failed {failed}")
    
    except Exception as e:
        print(f"error: {e}")    
        db.rollback()
        raise

    finally:
        db.close()



if __name__ == "__main__":
    import_recipes("/Users/sruthiperumalla/Desktop/yummer/backend/data/final_dataset.csv", limit=1000)      # absolute path for now

