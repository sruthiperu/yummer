from sqlalchemy.orm import Session
from sqlalchemy import text, func, Float        # or_
from typing import Optional

from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from scripts.normalize_ingredients import normalize_ingredient
from scripts.recipe_tags import TAGS

from enum import Enum    


def search_recipes(db, query, filters, page=1, limit=20): # sort="relevance"):
    # results, total = _search(db, query, filters, page, limit, sort)
    results, total = _search(db, query, filters, page, limit)

    if total == 0:
        # search with no filters
        # results_no_filters, total_no_filters = _search(db, query, {}, page, limit, sort)
        results_no_filters, total_no_filters = _search(db, query, {}, page, limit)

        if total_no_filters > 0:
            return [], 0, "filters_too_strict"
        else:
            return [], 0, "no_matches"
        
    return results, total, None


def _search(db: Session, query: str, filters: dict, page: int = 1, limit: int = 20): # sort="relevance"):

    offset = (page - 1) * limit     # limit: per 20 recipes

    base = db.query(Recipe, func.ts_rank_cd(Recipe.search_vector, 
                    func.plainto_tsquery("english", query))     # convert to search terms
                    .label("rank")
                    ).filter(Recipe.search_vector.op("@@")(func.plainto_tsquery("english", query)))

    # apply tags
    selected_tags = parse_validate_tags(filters.get("tags"))
    for tag in selected_tags:
        base = base.filter(Recipe.tags.contains([tag]))

    # apply filters
    if filters.get("min_time"):
        base = base.filter(Recipe.total_time >= filters["min_time"])
    if filters.get("max_time"):
        base = base.filter(Recipe.total_time <= filters["max_time"])
    if filters.get("max_calories"):
        base = base.filter(Recipe.nutrition["calories"].astext.cast(Float) <= filters["max_calories"])
    if filters.get("min_calories"):
        base = base.filter(Recipe.nutrition["calories"].astext.cast(Float) >= filters["min_calories"])

    base = order_by_rating(base)
    results = base.offset(offset).limit(limit).all()

    return results, base.count()


def search_by_ingredients(db: Session, ing_names: list[str], filters: dict = None, page: int = 1, limit: int = 20):    # sort="relevance"):
    offset = (page - 1) * limit

    # normalize ingredients
    # normalized = [name.lower().strip() for name in ingredient_names]
    ing_matches = find_ingredient_ids(db, ing_names)
    
    # make list of all ingredient matches
    matched_ids = []
    for ids in ing_matches.values():
        matched_ids.extend(ids)
    if not matched_ids: return [], 0

    selected_tags = parse_validate_tags(filters.get("tags", "")) if filters else []
    tag_filter = ""
    if selected_tags:
        import json
        tag_filter = f"AND r.tags @> '{json.dumps(selected_tags)}'::jsonb"

    max_time = filters.get("max_time") if filters else None
    time_filter = f"AND r.total_time <= {max_time}" if max_time else ""

    # matched_count priority, then rating
    # order = "matched_count DESC, mr.rating DESC NULLS LAST, mr.num_ratings DESC NULLS LAST"
    order = """matched_count DESC, ((mr.num_ratings * mr.rating + 10 * 4.0) / NULLIF(mr.num_ratings + 10, 0)) DESC NULLS LAST"""

    # find recipes with any of ingredient matches
    # score -> % of user ingredients recipe already has
    sql = f"""
        WITH matched_recipes AS (
            SELECT
                r.id,
                r.name,
                r.total_time,
                r.nutrition,
                r.tags,
                r.rating,
                r.num_ratings,
                r.image,
                r.link,
                r.description,
                COUNT(DISTINCT ri.ingredient_id) AS matched_count
            FROM recipes r
            JOIN recipe_ingredients ri ON ri.recipe_id = r.id
            WHERE ri.ingredient_id = ANY(:ingredient_ids)
            {tag_filter}
            {time_filter}
            GROUP BY r.id, r.name, r.total_time, r.nutrition, r.tags, r.rating, r.num_ratings, r.link, r.description
        ),

        recipe_totals AS (
            SELECT
                recipe_id,
                COUNT(*) AS total_ingredients
            FROM recipe_ingredients
            GROUP BY recipe_id
        ),

        recipe_ings AS (
            SELECT
                ri.recipe_id,
                array_agg(i.name) AS ingredients
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            GROUP BY ri.recipe_id
        )

        SELECT
            mr.*,
            rt.total_ingredients,
            ri.ingredients,

            ROUND(
                mr.matched_count::numeric / :user_ingredient_count * 100
            ) AS user_match_pct,

            ROUND(
                mr.matched_count::numeric / NULLIF(rt.total_ingredients, 0) * 100
            ) AS recipe_match_pct

        FROM matched_recipes mr
        JOIN recipe_totals rt ON rt.recipe_id = mr.id
        JOIN recipe_ings ri ON ri.recipe_id = mr.id

        ORDER BY {order}
        LIMIT :limit OFFSET :offset
    """

    scored = db.execute(text(sql), {"ingredient_ids": matched_ids, "user_ingredient_count": len(ing_names), "limit": limit, "offset": offset}).fetchall()
    

    results = []
    for row in scored:
        r = row._mapping
        missing = get_missing_ingredients(db, r["id"], matched_ids)

        results.append({"id": r["id"], "name": r["name"], "total_time": r["total_time"], "nutrition": r["nutrition"], "tags": r["tags"],
                        "rating": r["rating"], "num_ratings": r["num_ratings"], "image": r["image"], "link": r["link"], "matched_count": r["matched_count"], 
                        "total_ingredients": r["total_ingredients"], "user_match_pct": float(r["user_match_pct"]), "recipe_match_pct": float(r["recipe_match_pct"]), 
                        "ingredients": r["ingredients"], "missing_ingredients": missing})

    total = len(scored)

    return results, total


def find_ingredient_ids(db: Session, ing_names: list[str]):
    """
    given a list of ingredient strings from user
    returns dict that maps each ingredient name to a list of matching ingredient ids
    """

    matches = {}
    for name in ing_names:
        normalized = normalize_ingredient(name)

        # try exact ingredient name first
        exact_name = db.query(Ingredient).filter(Ingredient.name == normalized).first()
        if exact_name:
            matches[name] = [exact_name.id]
            continue

        # find ingredient names similar to user's ("chiken" -> "chicken")
        diff_res = db.execute(text("""
            SELECT id, name, similarity(name, :query) AS sim
            FROM ingredients
            WHERE similarity(name, :query) > 0.3
            ORDER BY sim DESC
            LIMIT 3
        """), {"query": normalized}).fetchall()

        matches[name] = [row._mapping["id"] for row in diff_res]

    
    return matches
    

def get_missing_ingredients(db: Session, recipe_id: int, matched_ing_ids: list[int]):
    """
    return ingredient names that recipe needs but aren't provided by user
    """
    missing = db.execute(text("""
        SELECT i.name
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = :recipe_id
          AND ri.ingredient_id != ALL(:matched_ids)
        LIMIT 5
    """), {
        "recipe_id": recipe_id,
        "matched_ids": matched_ing_ids,
    }).fetchall()

    # return [row.name for row in missing]
    return [row._mapping["name"] for row in missing]


# give user suggestions if their input isn't accepted
def build_empty_result(reason: str):
    return {"results": [], "total": 0, "reason": reason, "suggestions": get_suggestion(reason)}

def get_suggestion(reason: str):
    suggestions = {
        "no_matches": ["Try fewer ingredients", "Check for spelling mistakes", "Try a broader search term"],
        "bad_input": ["Enter at least one ingredient", "Use common ingredient names like 'chicken' or 'pasta'"],
        "filters_too_strict": ["Try removing some filters", "Increase the maximum cook time", "Try a different dietary filter"],
    }
    return suggestions.get(reason, [])


VALID_TAGS = set(TAGS)  # tags list

def parse_validate_tags(tags_str: Optional[str]) -> list[str]:
    """
    parse comma-separated tags string, return validated list
    """
    
    if not tags_str:
        return []
    
    selected = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
    invalid = [t for t in selected if t not in VALID_TAGS]
    if invalid:
        raise ValueError(f"invalid tags: {', '.join(invalid)}")
    
    return selected

def order_by_rating(query):
    # return query.order_by(Recipe.rating.desc().nullslast(), Recipe.num_ratings.desc().nullslast())
    return query.order_by(((Recipe.num_ratings * Recipe.rating + 10 * 4.0) / (Recipe.num_ratings + 10)).desc().nullslast())         # weighted score


class SortRecs(str, Enum):
    rating = "rating"
