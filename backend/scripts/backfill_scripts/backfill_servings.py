# Backfill servings from Food.com recipes.csv via link recipe ID
# python -m scripts.backfill_scripts.backfill_servings --dry-run
# python -m scripts.backfill_scripts.backfill_servings --commit

import argparse
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe
from scripts.parse_recipe import parse_servings_from_link, load_servings_by_recipe_id

DEFAULT_CSV = "data/recipes.csv"


def backfill_servings(csv_path, commit=False, batch_size=5000, sample_size=30):
    """
    backfill Recipe.servings from the csv
    """

    print("Loading servings from recipes.csv", flush=True)
    servings_by_id = load_servings_by_recipe_id(csv_path)
    print(f"\t{len(servings_by_id)} recipes with servings in CSV", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    last_id = 0

    try:
        while True:
            recipes = db.execute(select(Recipe).where(Recipe.id > last_id).order_by(Recipe.id).limit(batch_size)).scalars().all()

            if not recipes:
                break

            for recipe in recipes:
                stats["total"] += 1
                link = (recipe.link or "").strip()
                if not link:
                    stats["no_link"] += 1
                    continue
                
                # extract recipe ID from link
                new_servings = parse_servings_from_link(link, servings_by_id)
                if new_servings is None:
                    stats["no_csv_match"] += 1
                    continue

                if recipe.servings == new_servings:
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if len(samples) < sample_size:
                    samples.append(
                        f"\t{recipe.name[:50]!r}: {recipe.servings!r} -> {new_servings!r}"
                    )

                if commit:
                    recipe.servings = new_servings

            last_id = recipes[-1].id

            if commit:
                db.commit()
                print(f"\tprocessed through id {last_id} ({stats['updated']} updates)...", flush=True)

        print("BACKFILL SERVINGS", "COMMIT" if commit else "DRY RUN")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_servings(args.csv, commit=commit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
