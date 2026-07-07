# Import all recipes in dataset into database

import pandas as pd
import sys
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe, Ingredient, RecipeIngredient

from .normalize_ingredients import normalize_ingredient, get_flags, apply_flags
from scripts.parse_recipe import parse_row, load_servings_by_recipe_id
from scripts.recipe_tags import compute_curated_tags


def get_ingredient(db_session, name):
    """
    given: SQLAlchemy session, string (ingredient); returns ingredient object from database
    if ingredient not in database, creates it
    """

    canonical_name = normalize_ingredient(name)
    if not canonical_name:
        return None

    # search for ingredient's canonical form in database
    in_db = db_session.execute(select(Ingredient).where(Ingredient.name == canonical_name)).scalar_one_or_none()

    if in_db:
        # add alias if name != canonical_name and not in the ingredient's aliases list already
        if name != canonical_name:
            ing_aliases = in_db.aliases if in_db.aliases is not None else []
            if name not in ing_aliases:
                ing_aliases.append(name)
                in_db.aliases = ing_aliases
                db_session.flush()

        if apply_flags(in_db, get_flags(canonical_name)):       # call apply_flags on existing rows
            db_session.flush()

        return in_db

    flags = get_flags(canonical_name)
    ingredient = Ingredient(name=canonical_name, aliases=[name] if canonical_name != name else None,
                            food_type=flags["type"], is_vegan=flags["vegan"], is_vegetarian=flags["vegetarian"],
                            is_gluten_free=flags["gluten_free"], allergens=flags["allergens"] or None)

    db_session.add(ingredient)
    db_session.flush()
    return ingredient


def import_recipes(dataset_path, start, limit):
    """
    given: dataset_path (path to csv file) and limit (number of recipes to import into database)
    imports the first 'limit' number of recipes from dataset into database
    """

    df = pd.read_csv(dataset_path)
    df = df.iloc[start:]
    if limit is not None:
        df = df.head(limit)

    servings_by_id = load_servings_by_recipe_id("data/recipes.csv")

    db = SessionLocal()
    inserted, skipped, failed = 0, 0, 0

    try:
        for i, row in df.iterrows():

            try:
                recipe_data, ingredients_data = parse_row(row, servings_by_id)
                if not recipe_data or not ingredients_data: 
                    skipped += 1
                    continue
                    
                # create recipe
                recipe = Recipe(**recipe_data)        # no ingredients
                db.add(recipe)
                db.flush()

                ingredient_flags: list[dict] = []

                # for each ingredient
                for ing_data in ingredients_data:

                    if ing_data['ingredient'] is None:
                        continue
                    ing = get_ingredient(db, ing_data['ingredient'])
                    if not ing:
                        continue

                    ingredient_flags.append({
                        "is_vegetarian": ing.is_vegetarian,
                        "is_vegan": ing.is_vegan,
                        "is_gluten_free": ing.is_gluten_free,
                    })

                    # link recipe and ingredient
                    link = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=ing_data.get('quantity'), 
                                            unit=ing_data.get('unit'), container_size=ing_data.get('container_size'),
                                            raw_ingredient=ing_data.get('text'),
                                            section_title=ing_data.get('section_title'))
                    db.add(link)

                recipe.tags = compute_curated_tags(recipe_data.get("tags"), recipe_data.get("total_time"), recipe_data.get("nutrition"), recipe_data.get("name"), ingredient_flags=ingredient_flags) or None
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
    import_recipes("/Users/sruthiperumalla/Desktop/yummer/backend/data/final_dataset.csv", start=1000, limit=None)      # absolute path for now

