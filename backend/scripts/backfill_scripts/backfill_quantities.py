# Re-parse quantity, unit, and container_size from recipe_ingredients.raw_ingredient
# python -m scripts.backfill_scripts.backfill_quantities --dry-run
# python -m scripts.backfill_scripts.backfill_quantities --commit
# python -m scripts.backfill_scripts.backfill_quantities --commit --start-after-id 12345

import argparse
from collections import defaultdict

from sqlalchemy import select

from app.database import SessionLocal
from app.models.recipe import RecipeIngredient
from scripts.parse_recipe import get_quantity


def backfill_quantities(commit=False, batch_size=5000, sample_size=30, start_after_id=0):
    """
    re-parse ingredient quantities from raw_ingredient
    """

    db = SessionLocal()
    stats = defaultdict(int)
    samples = []
    cache = {}
    last_id = start_after_id

    def cached_get_quantity(raw):
        """
        return the parsed quantity information for a raw ingredients
        cache results, so that identical ingredients are only parsed once
        """

        if raw not in cache:
            cache[raw] = get_quantity(raw)
        return cache[raw]

    try:
        while True:
            rows = db.execute(
                select(RecipeIngredient)
                .where(
                    RecipeIngredient.id > last_id,
                    RecipeIngredient.raw_ingredient.isnot(None),
                )
                .order_by(RecipeIngredient.id)
                .limit(batch_size)
            ).scalars().all()

            if not rows:
                break

            for ri in rows:
                stats["total"] += 1
                raw = ri.raw_ingredient
                if not raw or not str(raw).strip():
                    stats["no_raw"] += 1
                    continue

                quantity, unit, container_size, _ = cached_get_quantity(raw)

                if ri.quantity == quantity and ri.unit == unit and ri.container_size == container_size:
                    stats["unchanged"] += 1
                    continue

                stats["updated"] += 1
                if ri.quantity != quantity:
                    stats["quantity_changed"] += 1
                if ri.unit != unit:
                    stats["unit_changed"] += 1
                if ri.container_size != container_size:
                    stats["container_size_changed"] += 1

                if len(samples) < sample_size:
                    samples.append(
                        f"\t{raw[:70]!r}: qty {ri.quantity!r}->{quantity!r} "
                        f"unit {ri.unit!r}->{unit!r} size {ri.container_size!r}->{container_size!r}"
                    )

                if commit:
                    ri.quantity = quantity
                    ri.unit = unit
                    ri.container_size = container_size

            last_id = rows[-1].id

            if commit:
                db.commit()
                print(f"\tprocessed through id {last_id} ({stats['updated']} updates)...", flush=True)

        print("BACKFILL QUANTITIES", "COMMIT" if commit else "DRY RUN")
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
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--start-after-id", type=int, default=0)
    args = parser.parse_args()

    commit = args.commit and not args.dry_run
    if not args.commit and not args.dry_run:
        args.dry_run = True

    backfill_quantities(
        commit=commit,
        batch_size=args.batch_size,
        start_after_id=args.start_after_id,
    )

    if commit:
        db = SessionLocal()
        try:
            null_qty_can = db.query(RecipeIngredient).filter(
                RecipeIngredient.quantity.is_(None),
                RecipeIngredient.unit.in_(["can", "cans"]),
            ).count()
            has_size = db.query(RecipeIngredient).filter(
                RecipeIngredient.container_size.isnot(None)
            ).count()
        finally:
            db.close()


if __name__ == "__main__":
    main()
