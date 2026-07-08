from pydantic import BaseModel

from datetime import datetime


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
    link: str | None
    class Config:
        from_attributes = True
