from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from scripts.search import SortRecs, search_recipes, search_by_ingredients as search_ings
from scripts.clean_input import clean_query, clean_ingredients


router = APIRouter(prefix="/search", tags=["search"])


# find recipes with ingredients in recipe name
@router.get("")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    sort: SortRecs = SortRecs.relevance,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    is_vegan: bool = False,
    is_vegetarian: bool = False,
    is_gluten_free: bool = False,
    min_time: Optional[int] = None,
    max_time: Optional[int] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None,
    db: Session = Depends(get_db)):

    clean_query_res = clean_query(q)
    print(f"DEBUG: q={q}, clean_query_res={clean_query_res}")  # DEBUGGGGGGGGG

    if not clean_query_res:
        return {"results": [], "total": 0, "empty_reason": "bad_input", "suggestions": ["Enter at least two characters to search"]}
    
    filters = {"vegan": is_vegan, "vegetarian": is_vegetarian, "gluten_free": is_gluten_free, 
               "min_time": min_time, "max_time": max_time, "min_calories": min_calories, "max_calories": max_calories}

    results, total, empty_reason = search_recipes(db, clean_query_res, filters, page, limit, sort=sort)

    res = []
    for recipe, rank in results:
        res_dict = {"id": recipe.id, "name": recipe.name, "total_time": recipe.total_time, "nutrition": recipe.nutrition,
                     "tags": recipe.tags, "rating": recipe.rating, "num_ratings": recipe.num_ratings, 
                     "link": recipe.link, "match_score": round(float(rank), 4)}
        res.append(res_dict)

    return {"results": res, "total": total, "page": page, "limit": limit, "empty_reason": empty_reason}


# find recipes with ingredients in ingredients list
@router.get("/by-ingredients")
def search_by_ingredients(
    ingredients: str = Query(..., description="Comma separated ingredient list"),
    sort: str = "relevance",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    is_vegan: bool = False,
    is_vegetarian: bool = False,
    is_gluten_free: bool = False,
    max_time: Optional[int] = None,
    db: Session = Depends(get_db)):


    ing_list = clean_ingredients(ingredients)

    if not ing_list: 
        return {"results": [], "total": 0, "empty_reason": "bad_input", "suggestions": ["Enter at least one ingredient name"]}

    filters = {"vegan": is_vegan, "vegetarian": is_vegetarian, "gluten_free": is_gluten_free, "max_time": max_time}
    results, total = search_ings(db, ing_list, filters, page, limit, sort)


    if total == 0:
        return {"results": [], "total": 0, "searched_ings": ing_list, "empty_reason": "no_matches",
                "suggestions": ["Try fewer ingredients", "Check spelling — use simple names like 'chicken' not 'chicken breast'"]}
    else:
        return {"results": results, "total": total, "page": page, "limit": limit, "searched_ings": ing_list, "empty_reason": None}

