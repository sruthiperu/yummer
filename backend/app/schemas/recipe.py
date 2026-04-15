from pydantic import BaseModel

from datetime import datetime


class IngredientResponse(BaseModel):
    id: int
    name: str
    quantity: str | None
    unit: str | None
    raw_ingredient: str | None
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
    date: datetime | None
    link: str | None
    class Config:
        from_attributes = True
