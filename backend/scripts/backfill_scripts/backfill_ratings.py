# Backfill ratings and num_ratings from food.com recipes.csv via link recipe ID
# python -m scripts.backfill_scripts.backfill_ratings --dry-run
# python -m scripts.backfill_scripts.backfill_ratings --commit

import argparse
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe
from scripts.parse_recipe import parse_ratings_from_link, load_ratings_by_recipe_id

DEFAULT_CSV = "data/recipes.csv"


def backfill_ratings(csv_path, commit=False, batch_size=5000, sample_size=30):
    """
    backfil Recipe.rating and Recipe.num_ratings from the csv
    """
    
    print("Loading ratings from recipes.csv", flush=True)
    ratings_by_id = load_ratings_by_recipe_id(csv_path)
    print(f"\t{len(ratings_by_id)} recipes with ratings in CSV", flush=True)

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

                new_rating, new_num_ratings = parse_ratings_from_link(link, ratings_by_id)
                
                # skip if no rating data found in CSV
                if new_rating is None and new_num_ratings is None:
                    stats["no_csv_match"] += 1
                    continue

                # check if anything changed
                rating_changed = recipe.rating != new_rating
                count_changed = recipe.num_ratings != new_num_ratings

                if not rating_changed and not count_changed:
                    stats["unchanged"] += 1
                    continue

                # track what changed for stats
                if rating_changed and count_changed:
                    stats["updated_both"] += 1
                elif rating_changed:
                    stats["updated_rating"] += 1
                else:
                    stats["updated_count"] += 1

                stats["updated"] += 1
                
                if len(samples) < sample_size:
                    old_rating = f"{recipe.rating!r}" if recipe.rating is not None else "None"
                    old_count = f"{recipe.num_ratings!r}" if recipe.num_ratings is not None else "None"
                    new_r = f"{new_rating!r}" if new_rating is not None else "None"
                    new_c = f"{new_num_ratings!r}" if new_num_ratings is not None else "None"
                    samples.append(
                        f"\t{recipe.name[:50]!r}: "
                        f"rating {old_rating} -> {new_r}, "
                        f"num_ratings {old_count} -> {new_c}"
                    )

                if commit:
                    if rating_changed:
                        recipe.rating = new_rating
                    if count_changed:
                        recipe.num_ratings = new_num_ratings

            last_id = recipes[-1].id

            if commit:
                db.commit()
                print(f"\tprocessed through id {last_id} ({stats['updated']} updates)...", flush=True)

        print("BACKFILL RATINGS", "COMMIT" if commit else "DRY RUN")
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

    backfill_ratings(args.csv, commit=commit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()