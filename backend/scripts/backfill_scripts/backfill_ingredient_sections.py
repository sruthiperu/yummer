# Backfill recipe_ingredients.section_title from final_dataset.csv recipeNLG order
# python -m scripts.backfill_scripts.backfill_ingredient_sections --dry-run
# python -m scripts.backfill_scripts.backfill_ingredient_sections --commit

import argparse
import csv
import re
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import Recipe, RecipeIngredient
from scripts.ingredient_match import parse_section_header
from scripts.parse_recipe import convert_str_to_list

DEFAULT_CSV = "data/final_dataset.csv"

# patterns for ingredient section titles (to avoid processing section titles as ingredient names)
HEADER_HINT = re.compile(
    r"(for the|to serve|to assemble|to garnish|to finish|to decorate|such as|"
    r"sauce|filling|topping|marinade|dressing|glaze|frosting|batter|crust|garnish|stuffing)",
    re.IGNORECASE,
)


def line_might_have_section(text):
    if not text:
        return False
    return bool(HEADER_HINT.search(str(text)))


def load_nlg_by_link(csv_path):
    """
    load NLG ingredient lists only for recipes that contain section headers
    """

    by_link = {}
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            link = row.get("link", "").strip()
            if not link:
                continue
            nlg_lines = convert_str_to_list(row.get("recipenlg_ingredients", ""))
            if not any(line_might_have_section(line) for line in nlg_lines):
                continue
            if not any(parse_section_header(line) for line in nlg_lines if line):
                continue
            by_link[link] = nlg_lines
    return by_link


def is_bogus_header_row(raw):
    return bool(raw and parse_section_header(raw))


def build_nlg_ingredient_order(nlg_lines):
    """
    return ordered (raw_line, section_title) pairs for NLG ingredient lines
   
    example:
        "For the frosting"
        "1 cup unsalted butter"
        "4 cups powdered sugar"
        "For the cake"
        "1 1/2 cup all-purpose flour"
        
        ("1 cup unsalted butter", "For the frosting") ("4 cups powdered sugar", "For the frosting") ("1 1/2 cup all-purpose flour", "For the cake")
    """

    current_section = None
    ordered = []

    for line in nlg_lines:
        if not line or not str(line).strip():
            continue
        line = str(line)

        header = parse_section_header(line)
        if header:
            current_section = header
            continue

        ordered.append((line, current_section))

    return ordered


def process_recipe(nlg_lines, ri_rows, commit, db, stats, samples, sample_size):
    """
    match recipeNLG ingredients to RecipeIngredient rows
    """

    nlg_order = build_nlg_ingredient_order(nlg_lines)
    ri_idx = 0

    for nlg_line, section_title in nlg_order:
        while ri_idx < len(ri_rows):
            row = ri_rows[ri_idx]
            raw = row.raw_ingredient or ""
            if is_bogus_header_row(raw):
                stats["header_deleted"] += 1
                if len(samples) < sample_size:
                    samples.append(f"\tdelete header row: {raw!r}")
                if commit:
                    db.delete(row)
                ri_idx += 1
                continue
            break

        if ri_idx >= len(ri_rows):
            break

        row = ri_rows[ri_idx]

        # only match when the raw ingredient text is the same as the current RecipeNLG ingredient line. # # If it doesn't match, leave the DB row untouched and continue # with the next NLG ingredient.
        if (row.raw_ingredient or "") != nlg_line:
            continue
        
        # update the section title when the recipeNLG source differs from what's stored in the database
        if row.section_title != section_title:
            stats["section_updated"] += 1
            if len(samples) < sample_size:
                samples.append(
                    f"\t{nlg_line[:50]!r}: section {row.section_title!r} -> {section_title!r}"
                )
            if commit:
                row.section_title = section_title
        else:
            stats["section_unchanged"] += 1
        ri_idx += 1

    while ri_idx < len(ri_rows):
        row = ri_rows[ri_idx]
        raw = row.raw_ingredient or ""
        if is_bogus_header_row(raw):
            stats["header_deleted"] += 1
            if len(samples) < sample_size:
                samples.append(f"\tdelete trailing header row: {raw!r}")
            if commit:
                db.delete(row)
        ri_idx += 1


def cleanup_remaining_header_rows(db, commit, stats, section_links, samples, sample_size, batch_size=5000):
    """
    delete leftover header tiles for recipes known to have NLG sections
    """
    
    last_id = 0
    while True:
        rows = db.execute(
            select(RecipeIngredient, Recipe.link)
            .join(Recipe, RecipeIngredient.recipe_id == Recipe.id)
            .where(
                RecipeIngredient.id > last_id,
                Recipe.link.in_(section_links),
            )
            .order_by(RecipeIngredient.id)
            .limit(batch_size)
        ).all()
        if not rows:
            break

        for row, _link in rows:
            raw = row.raw_ingredient or ""
            if not HEADER_HINT.search(raw):
                continue
            if not is_bogus_header_row(raw):
                continue
            stats["header_deleted"] += 1
            if len(samples) < sample_size:
                samples.append(f"\tdelete orphan header row: {raw!r}")
            if commit:
                db.delete(row)

        last_id = rows[-1][0].id
        if commit:
            db.commit()
            print(f"\tcleanup through id {last_id} ({stats['header_deleted']} deletions)...", flush=True)


def backfill_ingredient_sections(csv_path, commit=False, batch_size=2000, sample_size=30):
    print("Loading NLG lists for recipes with section headers", flush=True)
    nlg_by_link = load_nlg_by_link(csv_path)
    print(f"\t{len(nlg_by_link)} recipes in CSV with sections", flush=True)

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    section_links = set(nlg_by_link.keys())
    last_id = 0

    try:
        while True:
            recipes = db.execute(
                select(Recipe)
                .where(Recipe.id > last_id, Recipe.link.in_(section_links))
                .order_by(Recipe.id)
                .limit(batch_size)
            ).scalars().all()
            if not recipes:
                break

            recipe_ids = [r.id for r in recipes]
            ri_by_recipe = defaultdict(list)
            for ri in db.execute(
                select(RecipeIngredient)
                .where(RecipeIngredient.recipe_id.in_(recipe_ids))
                .order_by(RecipeIngredient.recipe_id, RecipeIngredient.id)
            ).scalars():
                ri_by_recipe[ri.recipe_id].append(ri)

            for recipe in recipes:
                stats["recipes_processed"] += 1
                link = (recipe.link or "").strip()
                nlg_lines = nlg_by_link.get(link)
                if not nlg_lines:
                    stats["no_nlg"] += 1
                    continue

                process_recipe(
                    nlg_lines,
                    ri_by_recipe.get(recipe.id, []),
                    commit,
                    db,
                    stats,
                    samples,
                    sample_size,
                )

            last_id = recipes[-1].id
            if commit:
                db.commit()
                print(
                    f"\tprocessed through recipe id {last_id} "
                    f"({stats['section_updated']} section updates, {stats['header_deleted']} deletions)...",
                    flush=True,
                )

        print("Running global header-row cleanup", flush=True)
        cleanup_remaining_header_rows(db, commit, stats, section_links, samples, sample_size)

        print("BACKFILL INGREDIENT SECTIONS", "COMMIT" if commit else "DRY RUN")
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
    parser.add_argument("--batch-size", type=int, default=2000)
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_ingredient_sections(args.csv, commit=commit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
