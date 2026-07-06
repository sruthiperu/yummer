# Creates endpoint to fetch a recipe by id

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from app.schemas.recipe import RecipeResponse
from scripts.format_quantities import format_quantity, abbreviate_unit
from scripts.parse_recipe import get_display_name


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
        display_name = get_display_name(recipe_ing.raw_ingredient) or (ing.name.strip() if ing.name else None)
        recipe.ingredients.append({"id": ing.id, "name": display_name, "quantity": format_quantity(recipe_ing.quantity), 
                                   "unit": abbreviate_unit(recipe_ing.unit), "container_size": recipe_ing.container_size,
                                   "raw_ingredient": recipe_ing.raw_ingredient, "food_type": ing.food_type, "allergens": ing.allergens or [], 
                                   "is_vegan": ing.is_vegan, "is_vegetarian": ing.is_vegetarian, "is_gluten_free": ing.is_gluten_free})
    

    return recipe