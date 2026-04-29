from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_

from app.models.recipe import Recipe, RecipeIngredient, Ingredient


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


def search_by_ingredients(db: Session, ingredient_names: list[str], page: int = 1, limit: int = 20):
    offset = (page - 1) * limit

    # normalize ingredients
    normalized = [name.lower().strip() for name in ingredient_names]
    
    results = db.execute(text("""
        SELECT
            r.id,
            r.name,
            r.total_time,
            r.nutrition,
            r.tags,
            r.link,
            COUNT(DISTINCT ri.ingredient_id) as matched_count,       -- count num of user ingredients in recipe
            (
                SELECT COUNT(*) FROM recipe_ingredients ri2
                WHERE ri2.recipe_id = r.id
            ) as total_ingredients,
            ROUND(
                COUNT(DISTINCT ri.ingredient_id)::numeric /          -- calculate match % (for ranking)
                NULLIF((
                    SELECT COUNT(*) FROM recipe_ingredients ri2
                    WHERE ri2.recipe_id = r.id
                ), 0) * 100
            ) as match_pct
        FROM recipes r
        JOIN recipe_ingredients ri ON ri.recipe_id = r.id
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE LOWER(i.name) = ANY(:ingredients)         -- displayed recipes should have >= 1 user ingredients
        GROUP BY r.id
        ORDER BY match_pct DESC, matched_count DESC
        LIMIT :limit OFFSET :offset
    """), {
        "ingredients": normalized,
        "limit": limit,
        "offset": offset,
    })
    
    results = results.fetchall()
    
    return results



    