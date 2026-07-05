# Remap canonical ingreedient names in databse using food.com content matching
# python -m scripts.remap_ingredients --dry-run
# python -m scripts.remap_ingredients --commit

import argparse
import csv
from collections import defaultdict
from sqlalchemy import select, delete, exists

from app.database import SessionLocal
from app.models.recipe import Ingredient, Recipe, RecipeIngredient

from scripts.import_recipes import get_ingredient
from scripts.parse_recipe import convert_str_to_list, get_quantity
from scripts.ingredient_match import resolve_canonical_name


DEFAULT_CSV = "data/final_dataset.csv"

def load_csv_by_link(csv_path):
    by_link = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            link = row.get("link", "").strip()
            if not link:
                continue
            by_link[link] = convert_str_to_list(row.get("foodcom_ingredients", ""))
    
    return by_link


def dedupe_rows(db, rows):
    """
    remove duplicate ingredient_id rows, keep lowest ID
    """
    seen = set()
    removed = 0
    for row in rows:
        if row.ingredient_id in seen:
            if db: db.delete(row)
            removed += 1
        else:
            seen.add(row.ingredient_id)

    return removed


def delete_orphan_ingredients(db):
    subq = select(RecipeIngredient.ingredient_id).where(RecipeIngredient.ingredient_id == Ingredient.id)
    result = db.execute(delete(Ingredient).where(~exists(subq)))
    
    return result.rowcount


def remap_ingredients(csv_path, commit=False, limit=None, sample_size=50):
    print("Loading CSV", flush=True)
    csv_by_link = load_csv_by_link(csv_path)
    print(f"\t{len(csv_by_link)} recipes in CSV", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    ingredient_cache = {}
    quantity_cache = {}

    def resolve_ingredient(canonical):
        if canonical in ingredient_cache: return ingredient_cache[canonical]
        ing = get_ingredient(db, canonical)
        ingredient_cache[canonical] = ing
        return ing

    def cached_get_quantity(nlg):
        if nlg not in quantity_cache: quantity_cache[nlg] = get_quantity(nlg)
        return quantity_cache[nlg]

    try:
        print("loading ingredients", flush=True)
        ingredient_names = dict(db.execute(select(Ingredient.id, Ingredient.name)).all())

        print("loading recipe ingredients", flush=True)
        ri_by_recipe = defaultdict(list)
        for ri in db.execute(select(RecipeIngredient).order_by(RecipeIngredient.recipe_id, RecipeIngredient.id)).scalars():
            ri_by_recipe[ri.recipe_id].append(ri)
        
        print(f"  {sum(len(v) for v in ri_by_recipe.values())} recipe_ingredient rows", flush=True)

        query = select(Recipe.id, Recipe.name, Recipe.link).order_by(Recipe.id)
        if limit is not None: query = query.limit(limit)
        
        recipes = db.execute(query).all()

        for recipe_id, recipe_name, recipe_link in recipes:
            if not recipe_link:
                stats["no_link"] += 1
                continue
            foodcom_list = csv_by_link.get(recipe_link.strip())
            if foodcom_list is None:
                stats["no_csv_match"] += 1
                continue

            stats["recipes_processed"] += 1
            used_fc_indices = set()
            if stats["recipes_processed"] % 10000 == 0:
                print(f"\tprocessed {stats['recipes_processed']} recipes", flush=True)

            ri_rows = ri_by_recipe.get(recipe_id, [])

            for ri in ri_rows:
                nlg = ri.raw_ingredient
                if not nlg:
                    stats["no_raw_ingredient"] += 1
                    continue

                canonical = resolve_canonical_name(nlg, foodcom_list, used_fc_indices)
                if not canonical:
                    stats["skipped_unresolved"] += 1
                    continue

                old_name = ingredient_names.get(ri.ingredient_id)
                new_ing = resolve_ingredient(canonical)
                quantity, unit, _, _ = cached_get_quantity(nlg)

                if old_name == new_ing.name and ri.quantity == quantity and ri.unit == unit:
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if old_name != new_ing.name:
                    stats["renamed"] += 1
                    if len(samples) < sample_size:
                        samples.append(
                            f"  {recipe_name[:50]!r}: {old_name!r} -> {new_ing.name!r} | {nlg[:70]!r}"
                        )

                if commit:
                    ri.ingredient_id = new_ing.id
                    ri.quantity = quantity
                    ri.unit = unit
                    ingredient_names[ri.ingredient_id] = new_ing.name

            if commit:
                stats["deduped_rows"] += dedupe_rows(db, ri_rows)
            if commit and stats["recipes_processed"] % 1000 == 0:
                db.commit()

        if commit:
            stats["orphans_deleted"] = delete_orphan_ingredients(db)
            db.commit()

        print("REMAP INGREDIENTS", "COMMIT" if commit else "DRY RUN")
        for key in sorted(stats.keys()):
            print(f"\t{key}: {stats[key]}")
        if samples:
            print(f"\nsample renames (up to {sample_size}):")
            for line in samples: print(line)
        print()
        return stats

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def audit_bad_names(db):
    """
    count ingredients whose names look like they cen be parsed
    """
    
    bad_patterns = ["cup", "tbsp", "tsp", "ounce", "oz", "lb", "tablespoon","teaspoon", "garnish", "throw some", "you can also",]
    adjective_only = {"blue", "good quality", "french blue", "quality"} 
    ingredients = db.execute(select(Ingredient.name)).scalars().all()
    bad = []
    for name in ingredients:
        lower = name.lower()
        if lower in adjective_only:
            bad.append(name)
        elif any(p in lower for p in bad_patterns):
            bad.append(name)
    return bad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run: args.dry_run = True

    remap_ingredients(args.csv, commit=commit, limit=args.limit)

    if args.audit or commit:
        db = SessionLocal()
        try:
            bad = audit_bad_names(db)
            print(f"from audit: {len(bad)} suspicious/adjective-only ingredient names")
            for name in bad[:30]:
                print(f"\t- {name!r}")
            if len(bad) > 30: print(f"\tand {len(bad) - 30} more")
        finally:
            db.close()


if __name__ == "__main__":
    main()
