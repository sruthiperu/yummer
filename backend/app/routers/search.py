from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from scripts.search import search_recipes, search_by_ingredients


router = APIRouter(prefix="/search", tags=["search"])


# find recipes with ingredients in recipe name
@router.get("")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    is_vegan: bool = False,
    is_vegetarian: bool = False,
    is_gluten_free: bool = False,
    max_time: Optional[int] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None,
    db: Session = Depends(get_db)):

    filters = {"vegan": is_vegan, "vegetarian": is_vegetarian, "gluten_free": is_gluten_free, "max_time": max_time, 
               "min_calories": min_calories, "max_calories": max_calories}

    results, total = search_recipes(db, q, filters, page, limit)

    return {     
        "results": [{"id": recipe.id, "name": recipe.name, "total_time": recipe.total_time, "nutrition": recipe.nutrition,
                     "tags": recipe.tags, "link": recipe.link, "match_score": round(float(rank), 4),
                    } for recipe, rank in results
        ], "total": total, "page": page, "limit": limit}


# find recipes with ingredients in ingredients list
@router.get("/by-ingredients")
def search_by_ingredients_endpoint(
    ingredients: str = Query(..., description="Comma separated ingredient list"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)):

    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]

    if not ingredient_list: return {"results": [], "total": 0, "page": page}

    # results = search_by_ingredients(db, ingredient_list, page, limit)
    results, total = search_by_ingredients(db, ingredient_list, page, limit)

    return {"results": [{"id": r["id"], "name": r["name"], "total_time": r["total_time"], "nutrition": r["nutrition"], 
                         "tags": r["tags"], "link": r["link"], "matched_count": r["matched_count"], "total_ingredients": r["total_ingredients"],
                         "user_match_pct": r["user_match_pct"], "recipe_match_pct": r["recipe_match_pct"], "missing_ingredients": r["missing_ingredients"],
                         } for r in results
                         ], "total": total, "page": page}