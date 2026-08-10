# Re-parse nutrition from final_dataset.csv (%DV -> grams)
# python -m scripts.backfill_scripts.backfill_nutrition --dry-run
# python -m scripts.backfill_scripts.backfill_nutrition --commit

import argparse
import csv
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe
from scripts.parse_recipe import parse_nutrition

DEFAULT_CSV = "data/final_dataset.csv"


def load_nutrition_by_link(csv_path):
    """
    load nutrition strings from the csv using recipe link
    """

    by_link = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            link = row.get("link", "").strip()
            if not link:
                continue
            by_link[link] = row.get("nutrition", "")
    return by_link


def backfill_nutrition(csv_path, commit=False, batch_size=5000, sample_size=30):
    """
    re-parse recipe nutrition from the csv
    update Recipe.nutrition
    """

    print("Loading CSV nutrition by link", flush=True)
    nutrition_by_link = load_nutrition_by_link(csv_path)
    print(f"\t{len(nutrition_by_link)} recipes in CSV", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    last_id = 0

    try:
        while True:
            recipes = db.execute(
                select(Recipe)
                .where(Recipe.id > last_id, Recipe.nutrition.isnot(None))
                .order_by(Recipe.id)
                .limit(batch_size)
            ).scalars().all()

            if not recipes:
                break

            for recipe in recipes:
                stats["total"] += 1
                link = (recipe.link or "").strip()
                if not link:
                    stats["no_link"] += 1
                    continue

                raw = nutrition_by_link.get(link)
                if raw is None:
                    stats["no_csv_match"] += 1
                    continue

                new_nutrition = parse_nutrition(raw)
                if not new_nutrition:
                    stats["parse_failed"] += 1
                    continue

                if recipe.nutrition == new_nutrition:
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if len(samples) < sample_size:
                    old = recipe.nutrition or {}
                    samples.append(
                        f"\t{recipe.name[:50]!r}: protein {old.get('protein')!r}->{new_nutrition.get('protein')!r} "
                        f"carbs {old.get('carbs')!r}->{new_nutrition.get('carbs')!r}"
                    )

                if commit:
                    recipe.nutrition = new_nutrition

            last_id = recipes[-1].id

            if commit:
                db.commit()
                print(f"\tprocessed through id {last_id} ({stats['updated']} updates)...", flush=True)

        print("BACKFILL NUTRITION", "COMMIT" if commit else "DRY RUN")
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

    backfill_nutrition(args.csv, commit=commit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
