# Backfill ingredients.food_type and flags from food_types
# python -m scripts.backfill_scripts.backfill_food_types --dry-run
# python -m scripts.backfill_scripts.backfill_food_types --commit

import argparse
from collections import defaultdict
from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Ingredient

from scripts.normalize_ingredients import get_flags, apply_flags


def backfill_food_types(commit=False, sample_size=30):
    """
    reassign food type and dietary flags + allergens for each ingredient
    """
    
    db = SessionLocal()
    stats = defaultdict(int)
    samples = []

    try:
        ingredients = db.execute(select(Ingredient).order_by(Ingredient.id)).scalars().all()

        for ing in ingredients:
            flags = get_flags(ing.name)
            old_type = ing.food_type or "other"
            new_type = flags["type"]

            new_allergens = flags.get("allergens") or None
            old_allergens = ing.allergens or None
            if (old_type == new_type and ing.is_vegan == flags["vegan"] and ing.is_vegetarian == flags["vegetarian"]
                    and ing.is_gluten_free == flags["gluten_free"] and old_allergens == new_allergens):
                stats["unchanged"] += 1
                continue

            stats["updated"] += 1
            if old_type != new_type:
                stats["type_changed"] += 1
                if len(samples) < sample_size:
                    samples.append(f"\t{ing.name!r}: {old_type!r} -> {new_type!r}")
            if old_allergens != new_allergens:
                stats["allergens_changed"] += 1
                if len(samples) < sample_size and old_type == new_type:
                    samples.append(f"\t{ing.name!r}: allergens {old_allergens!r} -> {new_allergens!r}")

            if commit: apply_flags(ing, flags)

        if commit:
            db.commit()

        print("BACKFILL FOOD TYPES", "COMMIT" if commit else "DRY RUN")
        print(f"\ttotal: {len(ingredients)}")
        for key in sorted(stats.keys()):
            print(f"\t{key}: {stats[key]}")
        if samples:
            print(f"\nsample type changes (up to {sample_size}):")
            for line in samples: print(line)
        print()

        return stats

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_food_types(commit=commit)

    if commit:
        db = SessionLocal()
        try:
            for name in ("baby arugula", "arugula", "blue cheese"):
                ing = db.execute(select(Ingredient).where(Ingredient.name == name)).scalar_one_or_none()
                if ing:
                    print(f"quick check {name!r}: food_type={ing.food_type!r}")
                else:
                    print(f"quick check {name!r}: not in DB")
        finally:
            db.close()


if __name__ == "__main__":
    main()
