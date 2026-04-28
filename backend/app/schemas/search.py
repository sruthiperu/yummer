from pydantic import BaseModel
from typing import Optional


class SearchFilters(BaseModel):
    is_vegan: bool = False
    is_vegetarian: bool = False
    is_gluten_free: bool = False
    min_time: Optional[int] = None      # minutes
    min_calories: Optional[int] = None
    max_calories: Optional[int] = None

class RecipeSearchResult(BaseModel):
    id: int
    name: str
    total_time: Optional[int]
    nutrition: Optional[dict]
    tags: Optional[list]
    link: Optional[str]
    match_score: float                  # relevance of result
    class Config:
        from_attributes = True
