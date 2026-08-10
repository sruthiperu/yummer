# Backfill recipes.directions with section_title from recipeNLG direction headers
# python -m scripts.backfill_scripts.backfill_direction_sections --dry-run
# python -m scripts.backfill_scripts.backfill_direction_sections --commit

import argparse
import csv
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe
from scripts.parse_recipe import convert_str_to_list, parse_directions

DEFAULT_CSV = "data/final_dataset.csv"


def load_directions_by_link(csv_path):
    """
    load and parse recipe directions from the csv
    """

    by_link = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            link = row.get("link", "").strip()
            if not link:
                continue
            instructions = convert_str_to_list(row.get("directions", ""))
            parsed = parse_directions(instructions)

            # skip recipes with no parsed directions
            if not parsed:
                continue

            # skip recipes without any direction section headers
            if not any(step.get("section_title") for step in parsed):
                continue
            by_link[link] = parsed

    return by_link


def directions_equal(a, b):
    """
    compare 2 direction lists
    """

    if len(a) != len(b):
        return False
    for left, right in zip(a, b):
        if left.get("direction") != right.get("direction"):
            return False
        if left.get("section_title") != right.get("section_title"):
            return False
        if left.get("step_num") != right.get("step_num"):
            return False
    return True


def backfill_direction_sections(csv_path, commit=False, batch_size=2000, sample_size=30):
    """
    backfill directions using the section titles parsed from the csv
    """

    print("Loading parsed directions for recipes with section headers", flush=True)
    directions_by_link = load_directions_by_link(csv_path)
    print(f"\t{len(directions_by_link)} recipes in CSV with direction sections", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    section_links = set(directions_by_link.keys())
    last_id = 0

    try:
        while True:
            # fetch recipes in batches
            recipes = db.execute(
                select(Recipe)
                .where(Recipe.id > last_id, Recipe.link.in_(section_links))
                .order_by(Recipe.id)
                .limit(batch_size)
            ).scalars().all()
            if not recipes:
                break

            for recipe in recipes:
                stats["recipes_processed"] += 1
                link = (recipe.link or "").strip()      # normalize recipe link
                expected = directions_by_link.get(link)
                if not expected:
                    stats["no_csv"] += 1
                    continue

                current = recipe.directions or []
                if directions_equal(current, expected):
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if len(samples) < sample_size:
                    sections = sorted({s.get("section_title") for s in expected if s.get("section_title")})
                    samples.append(
                        f"\t{recipe.name[:50]!r}: {len(current)} -> {len(expected)} steps, "
                        f"sections {sections!r}"
                    )

                if commit:
                    recipe.directions = expected

            last_id = recipes[-1].id        # save last processed id, so query begins after it
            if commit:
                db.commit()
                print(f"\tprocessed through recipe id {last_id} ({stats['updated']} updated)...", flush=True)

        if commit:
            db.commit()

        print("BACKFILL DIRECTION SECTIONS", "COMMIT" if commit else "DRY RUN")
        for key in sorted(stats.keys()):
            print(f"\t{key}: {stats[key]}")
        if samples:
            print(f"\nsample updates (up to {sample_size}):")
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
    parser.add_argument("--batch-size", type=int, default=2000)
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_direction_sections(args.csv, commit=commit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
