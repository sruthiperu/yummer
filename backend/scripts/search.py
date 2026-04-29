from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_

from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from scripts.normalize_ingredients import normalize_ingredient


def search_recipes(db: Session, query: str, filters: dict, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit     # limit: per 20 recipes

    base = db.query(Recipe, 
                    func.ts_rank_cd(Recipe.search_vector, 
                                    func.plainto_tsquery("english", query))     # convert to search terms
                                    .label("rank")
                    ).filter(Recipe.search_vector.op("@@")(func.plainto_tsquery("english", query)))


    # apply filters
    if filters.get("time"):
        base = base.filter(Recipe.total_time <= filters["time"])
    if filters.get("max_calories"):
        base = base.filter(Recipe.nutrition["calories"].astext.cast(float) <= filters["max_calories"])
    if filters.get("min_calories"):
        base = base.filter(Recipe.nutrition["calories"].astext.cast(float) >= filters["min_calories"])

    if filters.get("is_vegan"):
        base = base.filter(Recipe.tags.contains(["is_vegan"]))
    if filters.get("is_vegetarian"):
        base = base.filter(Recipe.tags.contains(["is_vegetarian"]))
    if filters.get("is_gluten_free"):
        base = base.filter(or_(Recipe.tags.contains(["gluten-free"]), Recipe.tags.contains(["is_gluten_free"])))

    # sort by rank
    results = (base.order_by(text("rank DESC")).offset(offset).limit(limit).all())
    
    total = base.count()

    return results, total


def search_by_ingredients(db: Session, ing_names: list[str], page: int = 1, limit: int = 20):
    offset = (page - 1) * limit

    # normalize ingredients
    # normalized = [name.lower().strip() for name in ingredient_names]
    ing_matches = find_ingredient_ids(db, ing_names)
    
    # make list of all ingredient matches
    matched_ids = []
    for ids in ing_matches.values():
        matched_ids.extend(ids)
    if not matched_ids: return [], 0

    # find recipes with any of ingredient matches
    # score -> % of user ingredients recipe already has
    scored = db.execute(text("""
        WITH matched_recipes AS (
            SELECT
                r.id,
                r.name,
                r.total_time,
                r.nutrition,
                r.tags,
                r.link,
                r.description,
                COUNT(DISTINCT ri.ingredient_id) AS matched_count       -- count recipes using any of user ingredients
            FROM recipes r
            JOIN recipe_ingredients ri ON ri.recipe_id = r.id
            WHERE ri.ingredient_id = ANY(:ingredient_ids)
            GROUP BY r.id
        ),
        recipe_totals AS (          -- count num ingredients per recipe
            SELECT
                recipe_id,
                COUNT(*) AS total_ingredients
            FROM recipe_ingredients
            GROUP BY recipe_id
        )
        SELECT
            mr.*,
            rt.total_ingredients,
            ROUND(
                mr.matched_count::numeric / :user_ingredient_count * 100
            ) AS user_match_pct,
            ROUND(
                mr.matched_count::numeric / NULLIF(rt.total_ingredients, 0) * 100
            ) AS recipe_match_pct
        FROM matched_recipes mr
        JOIN recipe_totals rt ON rt.recipe_id = mr.id
        ORDER BY user_match_pct DESC, recipe_match_pct DESC         -- rank recipes with more user ingredients first
        LIMIT :limit OFFSET :offset
    """), {
        "ingredient_ids": matched_ids,
        "user_ingredient_count": len(ing_names),
        "limit": limit,
        "offset": offset,
    }).fetchall()
    

    results = []
    for row in scored:
        r = row._mapping
        missing = get_missing_ingredients(db, r["id"], matched_ids)

        results.append({"id": r["id"], "name": r["name"], "total_time": r["total_time"], "nutrition": r["nutrition"], "tags": r["tags"],
                        "link": r["link"], "matched_count": r["matched_count"], "total_ingredients": r["total_ingredients"], 
                        "user_match_pct": float(r["user_match_pct"]), "recipe_match_pct": float(r["recipe_match_pct"]), "missing_ingredients": missing})

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

        # matches[name] = [row.id for row in diff_res] if diff_res else []
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