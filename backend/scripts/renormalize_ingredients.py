# Renormalize all ingredient canonical names, sync flags of food_type
# python -m scripts.renormalize_ingredients --dry-run
# python -m scripts.renormalize_ingredients --commit

import argparse
from collections import defaultdict
from sqlalchemy import delete, exists, select, update

from app.database import SessionLocal
from app.models.recipe import Ingredient, RecipeIngredient

from scripts.normalize_ingredients import apply_flags, get_flags, normalize_ingredient


def delete_orphan_ingredients(db):
    subq = select(RecipeIngredient.ingredient_id).where(
        RecipeIngredient.ingredient_id == Ingredient.id
    )
    result = db.execute(delete(Ingredient).where(~exists(subq)))
    return result.rowcount


def dedupe_recipe_ingredients(db):
    """
    remove duplicate ingredient_id per recipe, keep lowest link ID
    """
    rows = db.execute(select(RecipeIngredient).order_by(RecipeIngredient.recipe_id, RecipeIngredient.id)).scalars().all()

    seen_per_recipe = {}
    removed = 0
    for row in rows:
        seen = seen_per_recipe.setdefault(row.recipe_id, set())
        if row.ingredient_id in seen:
            db.delete(row)
            removed += 1
        else:
            seen.add(row.ingredient_id)
    return removed


def renormalize_ingredients(commit=False, sample_size=40):
    db = SessionLocal()
    stats = defaultdict(int)
    samples = []

    try:
        ingredients = db.execute(select(Ingredient).order_by(Ingredient.id)).scalars().all()
        name_to_id = {ing.name: ing.id for ing in ingredients}
        stats["total"] = len(ingredients)

        # compute target names
        plans = []
        for ing in ingredients:
            new_name = normalize_ingredient(ing.name)
            plans.append((ing, new_name))

        for ing, new_name in plans:
            old_name = ing.name

            if not new_name:
                stats["skipped_empty"] += 1
                continue

            if new_name == old_name:
                flags = get_flags(new_name)
                if ((ing.food_type or "other") != flags["type"] or ing.is_vegan != flags["vegan"]
                    or ing.is_vegetarian != flags["vegetarian"] or ing.is_gluten_free != flags["gluten_free"]):
                    stats["flags_updated"] += 1
                    if commit: apply_flags(ing, flags)
                else:
                    stats["unchanged"] += 1
                continue

            target_id = name_to_id.get(new_name)
            if target_id is not None and target_id != ing.id:
                stats["merged"] += 1
                if len(samples) < sample_size:
                    samples.append(f"  merge {old_name!r} -> {new_name!r} (id {ing.id} -> {target_id})")
                if commit:
                    db.execute(update(RecipeIngredient).where(RecipeIngredient.ingredient_id == ing.id).values(ingredient_id=target_id))
                    del name_to_id[old_name]
                    db.delete(ing)
                    db.flush()
                    target = db.get(Ingredient, target_id)
                    apply_flags(target, get_flags(new_name))
            else:
                stats["renamed"] += 1
                if len(samples) < sample_size: samples.append(f"  rename {old_name!r} -> {new_name!r}")
                if commit:
                    if old_name in name_to_id: del name_to_id[old_name]
                    ing.name = new_name
                    name_to_id[new_name] = ing.id
                    apply_flags(ing, get_flags(new_name))
                    db.flush()

        if commit:
            stats["deduped_links"] = dedupe_recipe_ingredients(db)
            stats["orphans_deleted"] = delete_orphan_ingredients(db)
            db.commit()

        print("RENORMALIZE INGREDIENTS", "COMMIT" if commit else "DRY RUN")
        for key in sorted(stats.keys()):
            print(f"\t{key}: {stats[key]}")
        if samples:
            print(f"\nsample changes (up to {sample_size}):")
            for line in samples:
                print(line)
        print()

        return stats

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Renormalize ingredient names and food types")
    parser.add_argument("--commit", action="store_true", help="Apply changes")
    parser.add_argument("--dry-run", action="store_true", help="Report only (default)")
    args = parser.parse_args()
    commit = args.commit and not args.dry_run
    
    if not args.commit and not args.dry_run: args.dry_run = True

    renormalize_ingredients(commit=commit)


if __name__ == "__main__":
    main()
