from pydantic import BaseModel

from datetime import datetime

class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    directions: list[dict]      # list of dictionaries
    servings: int | None
    total_time: int | None
    nutrition: dict | None
    tags: list | None
    date: datetime | None
    link: str | None

    class Config:
        from_attributes = True