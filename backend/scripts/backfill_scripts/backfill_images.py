# Backfill images from Food.com recipes.csv
# python -m scripts.backfill_scripts.backfill_images --from-foodcom --dry-run
# python -m scripts.backfill_scripts.backfill_images --from-foodcom --commit

import argparse
import re

from collections import defaultdict
from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe
from scripts.parse_recipe import load_images_by_recipe_id

DEFAULT_CSV = "data/recipes.csv"
FOODCOM_IMAGE_HOST = "sndimg.com"


def parse_image_from_link(link, images_by_id):
    """
    extract recipe ID from link suffix and return first image URL
    """
    
    if not images_by_id:
        return None
    match = re.search(r"-(\d+)$", str(link or "").strip())
    if not match:
        return None
    urls = images_by_id.get(match.group(1), [])
    return urls[0] if urls else None


def is_foodcom_image(url: str | None) -> bool:
    return bool(url) and FOODCOM_IMAGE_HOST in url.lower()


def backfill_foodcom_images(csv_path, commit=False, batch_size=5000, sample_size=30):
    print("Loading images from recipes.csv", flush=True)
    images_by_id = load_images_by_recipe_id(csv_path)
    print(f"\t{len(images_by_id)} recipes with images in CSV", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    last_id = 0

    try:
        while True:
            recipes = db.execute(
                select(Recipe)
                .where(Recipe.id > last_id)
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

                new_image = parse_image_from_link(link, images_by_id)
                if new_image is None:
                    stats["no_csv_match"] += 1
                    continue

                if recipe.image == new_image:
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if len(samples) < sample_size:
                    samples.append(f"\t{recipe.name[:50]!r}: {recipe.image!r} -> {new_image[:60]}...")

                if commit:
                    recipe.image = new_image

            last_id = recipes[-1].id

            if commit:
                db.commit()
                print(f"\tprocessed through id {last_id} ({stats['updated']} updates)...", flush=True)

        print("BACKFILL FOODCOM IMAGES", "COMMIT" if commit else "DRY RUN")
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
    parser.add_argument("--from-foodcom", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()

    if args.from_foodcom:
        commit = args.commit and not args.dry_run
        backfill_foodcom_images(args.csv, commit=commit, batch_size=args.batch_size)
    else:
        parser.error("Specify --from-foodcom")


if __name__ == "__main__":
    main()
