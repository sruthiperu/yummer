# Creates endpoint to fetch a recipe by id

import os
import json
import openai
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from app.schemas.recipe import RecipeResponse
from scripts.format_quantities import format_quantity, abbreviate_unit
from scripts.parse_recipe import get_display_name
from scripts.prompts import build_clean_prompt, build_modify_prompt


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
                                   "raw_ingredient": recipe_ing.raw_ingredient, "section_title": recipe_ing.section_title,
                                   "food_type": ing.food_type, "allergens": ing.allergens or [], 
                                   "is_vegan": ing.is_vegan, "is_vegetarian": ing.is_vegetarian, "is_gluten_free": ing.is_gluten_free})
    

    return recipe



class ModifyRequest(BaseModel):
    message: str = ""

def _build_text(recipe, db):
    """
    build ingredient and directions text
    """

    ingredients = (db.query(RecipeIngredient, Ingredient).join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
                   .filter(RecipeIngredient.recipe_id == recipe.id).order_by(RecipeIngredient.id).all())

    ings_lines = []
    for recipe_ing, ing in ingredients:
        name = get_display_name(recipe_ing.raw_ingredient) or (ing.name.strip() if ing.name else "unknown")
        qty = f"{recipe_ing.quantity or ''} {recipe_ing.unit or ''}".strip()
        line = f"{qty} {name}".strip() if qty else name
        ings_lines.append(f"- {line}")

    directions = recipe.directions or []
    dirs_lines = [f"{j+1}. {d['direction']}" for j, d in enumerate(directions)]

    return "\n".join(ings_lines), "\n".join(dirs_lines)


def _call_openai(prompt: str) -> dict:
    """
    send prompt to OpenAI and return parsed JSON dict
    """

    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        parts = content.split("```")
        content = parts[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    return json.loads(content)


def _attach_metadata(ai_result: dict, recipe: Recipe, is_modify: bool) -> dict:
    """
    merge AI output with original metadata
    """

    name = ai_result.get("name", recipe.name)
    ingredients = ai_result.get("ingredients", [])
    directions = ai_result.get("directions", [])
    nutrition = ai_result.get("nutrition", recipe.nutrition) if is_modify else recipe.nutrition
    if is_modify:
        total_time = ai_result.get("total_time", recipe.total_time)
        servings = ai_result.get("servings", recipe.servings)
    else:
        total_time = recipe.total_time
        servings = recipe.servings

    return {
        "name": name,
        "ingredients": ingredients,
        "directions": directions,
        "nutrition": nutrition,
        "total_time": total_time,
        "servings": servings,
        "image": recipe.image,
        "link": recipe.link,
        "tags": recipe.tags,
        "date": recipe.date.isoformat() if recipe.date else None,
        "id": recipe.id,
        "rating": None if is_modify else recipe.rating,         # keep rating + number of reviews if clean_recipe, remove if modify_recipe
        "num_ratings": None if is_modify else recipe.num_ratings,
    }

@router.post("/{recipe_id}/clean")
def clean_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")

    ings_text, dirs_text = _build_text(recipe, db)
    prompt = build_clean_prompt(recipe.name, ings_text, dirs_text)

    try:
        result = _call_openai(prompt)
        return _attach_metadata(result, recipe, is_modify=False)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{recipe_id}/modify")
def modify_recipe(recipe_id: int, request: ModifyRequest, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Modification message cannot be empty. Use /clean for cleaning.")

    ings_text, dirs_text = _build_text(recipe, db)
    prompt = build_modify_prompt(recipe.name, ings_text, dirs_text, request.message)

    try:
        result = _call_openai(prompt)
        return _attach_metadata(result, recipe, is_modify=True)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))