# Backfill recipes.tags with curated tag vocabulary
# python -m scripts.backfill_scripts.backfill_tags --dry-run
# python -m scripts.backfill_scripts.backfill_tags --commit
# python -m scripts.backfill_scripts.backfill_tags --commit --from-csv data/final_dataset.csv   # rebuild source tags from dataset
# python -m scripts.backfill_scripts.backfill_tags --commit --dietary-only --from-csv data/final_dataset.csv

import argparse
from collections import defaultdict

import pandas as pd
from sqlalchemy import select, text

from app.database import SessionLocal
from app.models.recipe import Recipe

from scripts.parse_recipe import convert_str_to_list
from scripts.recipe_tags import (
    compute_curated_tags,
    compute_dietary_tags,
    merge_dietary_tags,
)


def load_source_tags_by_link(csv_path: str) -> dict[str, list]:
    """
    map recipe link -> original Food.com source tag list from the dataset CSV
    """

    df = pd.read_csv(csv_path, usecols=["link", "tags"])
    mapping: dict[str, list] = {}
    for link, tags in zip(df["link"], df["tags"]):
        if isinstance(link, str):
            mapping[link] = convert_str_to_list(tags)
    return mapping


def load_ingredient_agg_by_recipe(db) -> dict[int, dict]:
    """
    load ingredient dietary flags grouped by recipe
    """

    rows = db.execute(
        text("""
            SELECT ri.recipe_id,
                   bool_or(i.is_vegetarian IS FALSE) AS has_nonveg,
                   bool_or(i.is_vegetarian IS TRUE)  AS has_veg,
                   bool_or(i.is_vegan IS FALSE)      AS has_nonvegan,
                   bool_or(i.is_vegan IS TRUE)       AS has_vegan,
                   bool_or(i.is_gluten_free IS FALSE) AS has_gluten,
                   bool_or(i.is_gluten_free IS TRUE)  AS has_gf
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            GROUP BY ri.recipe_id
        """)
    ).mappings().all()
    return {
        row["recipe_id"]: {
            "has_nonveg": row["has_nonveg"],
            "has_veg": row["has_veg"],
            "has_nonvegan": row["has_nonvegan"],
            "has_vegan": row["has_vegan"],
            "has_gluten": row["has_gluten"],
            "has_gf": row["has_gf"],
        }
        for row in rows
    }

def load_ingredient_names_by_recipe(db) -> dict[int, list[str]]:
    """
    map recipe_id -> list of ingredient name strings
    """
    
    rows = db.execute(
        text("""
            SELECT ri.recipe_id,
                   array_agg(ri.raw_ingredient) FILTER (WHERE ri.raw_ingredient IS NOT NULL) AS raw_names,
                   array_agg(i.name) AS canonical_names
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            GROUP BY ri.recipe_id
        """)
    ).mappings().all()
    result = {}
    for row in rows:
        raw = row["raw_names"] or []
        canonical = row["canonical_names"] or []
        result[row["recipe_id"]] = raw + canonical
    return result


def backfill_tags(commit: bool = False, sample_size: int = 20, batch_size: int = 500, from_csv: str | None = None, dietary_only: bool = False):
    """
    rebuild recipe tags using the curated tag vocabulary
    """

    db = SessionLocal()
    stats = defaultdict(int)
    samples: list[str] = []

    try:
        source_tags_by_link: dict[str, list] = {}
        if from_csv:
            source_tags_by_link = load_source_tags_by_link(from_csv)
            print(f"loaded source tags for {len(source_tags_by_link)} recipes from {from_csv}")

        ingredient_agg_by_recipe: dict[int, dict] = {}
        ingredient_names_by_recipe: dict[int, list[str]] = {}
        if dietary_only:
            ingredient_agg_by_recipe = load_ingredient_agg_by_recipe(db)
            ingredient_names_by_recipe = load_ingredient_names_by_recipe(db)
            print(f"loaded ingredient aggregates for {len(ingredient_agg_by_recipe)} recipes")

        recipes = db.execute(select(Recipe).order_by(Recipe.id)).scalars().all()
        pending = 0

        for recipe in recipes:
            if dietary_only:
                source_tags = source_tags_by_link.get(recipe.link, []) if from_csv else []
                agg = ingredient_agg_by_recipe.get(recipe.id)
                new_dietary = compute_dietary_tags(
                    source_tags,
                    recipe.name,
                    ingredient_agg=agg,
                    ingredient_names=ingredient_names_by_recipe.get(recipe.id),
                )
                curated = merge_dietary_tags(recipe.tags, new_dietary)
            else:
                if from_csv:
                    source_tags = source_tags_by_link.get(recipe.link, [])
                    if recipe.link not in source_tags_by_link:
                        stats["no_csv_match"] += 1
                else:
                    source_tags = recipe.tags

                curated = compute_curated_tags(
                    source_tags,
                    recipe.total_time,
                    recipe.nutrition,
                    recipe.name,
                    ingredient_names=ingredient_names_by_recipe.get(recipe.id),
                )

            old_tags = recipe.tags or []

            if old_tags == curated:
                stats["unchanged"] += 1
                continue

            stats["updated"] += 1
            if len(samples) < sample_size:
                samples.append(
                    f"\t{recipe.id} {recipe.name!r}: {old_tags!r} -> {curated!r}"
                )

            if commit:
                recipe.tags = curated or None
                pending += 1
                if pending >= batch_size:
                    db.commit()
                    pending = 0

        if commit and pending:
            db.commit()

        mode = "DIETARY ONLY" if dietary_only else "FULL"
        print(f"BACKFILL TAGS {mode}", "COMMIT" if commit else "DRY RUN")
        print(f"\ttotal: {len(recipes)}")
        for key in sorted(stats.keys()):
            print(f"\t{key}: {stats[key]}")
        if samples:
            print(f"\nsample tag changes (up to {sample_size}):")
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
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--from-csv", default=None, help="Rebuild source tags from dataset CSV (matched by link)")
    parser.add_argument(
        "--dietary-only",
        action="store_true",
        help="update only vegetarian/vegan/gluten-free tags. leave all other tags untouched.",
    )
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_tags(
        commit=commit,
        from_csv=args.from_csv,
        dietary_only=args.dietary_only,
    )


if __name__ == "__main__":
    main()
