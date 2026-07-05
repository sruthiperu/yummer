# Ingredient normalization and food_type consistency across all recipes
# python -m scripts.audit_ingredients
# python -m scripts.audit_ingredients --full
# python -m scripts.audit_ingredients --strict

import argparse
import re
import sys

from collections import Counter, defaultdict
from sqlalchemy import func, select
from app.database import SessionLocal
from app.models.recipe import Ingredient, Recipe, RecipeIngredient
from scripts.normalize_ingredients import get_flags, normalize_ingredient

DELETE_PATTERNS = [r"juice of", r"zest of", r"sweetonion", r"^\d+\s", r",\s"]       # pulled from observed recipes, keep adding as we go (?)


def audit_ingredients(full=False, strict=False, sample_size=30):
    db = SessionLocal()
    stats = defaultdict(int)
    unnormalized = Counter()
    stale_types = Counter()
    bad_pattern_hits = Counter()
    other_linked = Counter()

    try:
        rows = db.execute(
            select(Recipe.id, Recipe.name, Ingredient.id, Ingredient.name, Ingredient.food_type)
            .join(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id).order_by(Recipe.id)).all()

        recipes_with_issues = set()

        for recipe_id, recipe_name, ing_id, ing_name, food_type in rows:
            stats["links_checked"] += 1
            canonical = normalize_ingredient(ing_name)
            expected_type = get_flags(ing_name)["type"]
            current_type = food_type or "other"

            if ing_name != canonical:
                stats["unnormalized_names"] += 1
                unnormalized[ing_name] += 1
                recipes_with_issues.add(recipe_id)
                if not full and len(unnormalized) <= sample_size: pass

            if current_type != expected_type:
                stats["stale_food_types"] += 1
                stale_types[f"{ing_name!r} ({current_type} -> {expected_type})"] += 1
                recipes_with_issues.add(recipe_id)

            for pat in DELETE_PATTERNS:
                if re.search(pat, ing_name):
                    stats["bad_pattern_hits"] += 1
                    bad_pattern_hits[ing_name] += 1
                    recipes_with_issues.add(recipe_id)
                    break

            if expected_type == "other": other_linked[ing_name] += 1

        stats["recipes_with_issues"] = len(recipes_with_issues)
        stats["recipes_total"] = db.execute(select(func.count()).select_from(Recipe)).scalar()

        print("INGREDIENT AUDIT")
        print(f"\trecipes total: {stats['recipes_total']}")
        print(f"\trecipe_ingredient links: {stats['links_checked']}")
        print(f"\trecipes with issues: {stats['recipes_with_issues']}")
        print(f"\tunnormalized names: {stats['unnormalized_names']}")
        print(f"\tstale food_types: {stats['stale_food_types']}")
        print(f"\tdelete pattern hits: {stats['delete_pattern_hits']}")
        print(f"\tlinked ingredients typed 'other': {sum(other_linked.values())} links")

        if unnormalized:
            print(f"\ntop unnormalized names (up to {sample_size}):")
            for name, count in unnormalized.most_common(sample_size):
                print(f"  {name!r} ({count} links) -> {normalize_ingredient(name)!r}")

        if stale_types:
            print(f"\ntop stale food_types (up to {sample_size}):")
            for label, count in stale_types.most_common(sample_size):
                print(f"  {label} ({count} links)")

        if bad_pattern_hits:
            print(f"\ndelete pattern hits (up to {sample_size}):")
            for name, count in bad_pattern_hits.most_common(sample_size):
                print(f"  {name!r} ({count} links)")

        if full and other_linked:
            print(f"\ntop 'other' linked ingredients (not errors, up to {sample_size}):")
            for name, count in other_linked.most_common(sample_size):
                print(f"  {name!r} ({count} links)")

        print()

        has_issues = stats["unnormalized_names"] or stats["stale_food_types"]
        if strict and has_issues: sys.exit(1)

        return stats

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Audit ingredient normalization")
    parser.add_argument("--full", action="store_true", help="Include top 'other' ingredients list")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if unnormalized or stale types remain")
    args = parser.parse_args()
    
    audit_ingredients(full=args.full, strict=args.strict)


if __name__ == "__main__":
    main()
