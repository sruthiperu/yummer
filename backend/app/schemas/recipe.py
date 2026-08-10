from pydantic import BaseModel

from datetime import datetime
from typing import Optional


class IngredientResponse(BaseModel):
    id: int
    name: str
    quantity: str | None
    unit: str | None
    container_size: str | None = None
    raw_ingredient: str | None
    section_title: str | None = None
    food_type: str | None = None
    allergens: list[str] | None = None
    is_vegan: bool | None = None
    is_vegetarian: bool | None = None
    is_gluten_free: bool | None = None
    is_vegan: bool | None = None
    is_vegetarian: bool | None = None
    is_gluten_free: bool | None = None
    class Config:
        from_attributes = True

class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    ingredients: list[IngredientResponse] = []
    directions: list[dict]      # list of dictionaries
    servings: int | None
    total_time: int | None
    nutrition: dict | None
    tags: list | None
    rating: float | None
    num_ratings: int | None
    date: datetime | None
    image: str | None = None
    link: str | None
    class Config:
        from_attributes = True


class RecipeBatchItem(BaseModel):
    id: int
    name: str
    total_time: Optional[int] = None
    nutrition: Optional[dict] = None
    tags: Optional[list] = None
    rating: Optional[float] = None
    num_ratings: Optional[int] = None
    image: Optional[str] = None
    link: Optional[str] = None
