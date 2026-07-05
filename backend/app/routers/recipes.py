# Creates endpoint to fetch a recipe by id

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from app.schemas.recipe import RecipeResponse
from scripts.format_quantities import format_quantity, abbreviate_unit


router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/{recipe_id}", response_model=RecipeResponse)

def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")
    
    # get ingredients
    ingredients = db.query(RecipeIngredient, Ingredient).join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id).filter(RecipeIngredient.recipe_id == recipe_id).order_by(RecipeIngredient.id).all()

    recipe.ingredients = []
    for recipe_ing, ing in ingredients:
        recipe.ingredients.append({"id": ing.id, "name": ing.name, "quantity": format_quantity(recipe_ing.quantity), 
                                   "unit": abbreviate_unit(recipe_ing.unit), "raw_ingredient": recipe_ing.raw_ingredient,
                                   "food_type": ing.food_type})
    

    return recipe