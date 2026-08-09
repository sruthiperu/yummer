# Creates endpoint to fetch a recipe by id

import json
import re
import openai
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_optional_user_id
from app.config import settings
from app.database import get_db
from app.models.recipe import Recipe, RecipeIngredient, Ingredient
from app.schemas.recipe import RecipeResponse
from app.token_limits import (
    DAILY_TOKEN_LIMIT,
    LIMIT_MESSAGE,
    add_tokens,
    attach_anon_cookie,
    ensure_under_limit,
    get_tokens_used,
    resolve_subject,
)
from scripts.format_quantities import format_quantity, abbreviate_unit, scale_quantity
from scripts.parse_recipe import get_display_name
from scripts.prompts import build_clean_prompt, build_modify_prompt, build_clarify_modify_prompt


router = APIRouter(prefix="/recipes", tags=["recipes"])

SERVINGS_INTENT = re.compile(
    r"\b(servings?|yield|portion|portions|double|halve|half|triple|"
    r"single[\s-]?serving|makes?\s+\d+|for\s+\d+\s+people)\b",
    re.IGNORECASE,
)
TIME_INTENT = re.compile(
    r"\b(quicker|faster|slower|speed\s*up|cut\s+(?:the\s+)?time|"
    r"total\s*time|cook\s*time|prep\s*time|minutes?|hours?|"
    r"make\s+it\s+(?:quick|fast|slow))\b",
    re.IGNORECASE,
)
NUTRITION_KEYS = ("calories", "protein", "carbs", "total_fat", "sugar")

# more specific patterns first
_SERVINGS_TARGET_PATTERNS = [
    re.compile(r"(\d+)\s*servings?\b", re.IGNORECASE),
    re.compile(r"\bservings?\s*(?:to|=|:)?\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\bonly\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bfor\s+(\d+)\s+people\b", re.IGNORECASE),
    re.compile(r"\bmakes?\s+(\d+)\b", re.IGNORECASE),
]

def _wants_servings_change(message: str) -> bool:
    return bool(SERVINGS_INTENT.search(message or ""))

def _wants_time_change(message: str) -> bool:
    return bool(TIME_INTENT.search(message or ""))

def _parse_target_servings(message: str, base_servings) -> int | None:
    """
    extract servings from the user message, or None if not clear
    """
    text = message or ""
    lower = text.lower()

    base = None
    try:
        if base_servings is not None:
            base = int(float(base_servings))
            if base <= 0:
                base = None
    except (TypeError, ValueError):
        base = None

    if re.search(r"\b(half|halve|halved)\b", lower):
        return max(1, base // 2) if base else None
    if re.search(r"\bdouble[d]?\b", lower):
        return base * 2 if base else None
    if re.search(r"\btriple[d]?\b", lower):
        return base * 3 if base else None
    if re.search(r"\bsingle[\s-]?serving\b", lower):
        return 1
    if re.search(r"\b(?:another|one\s+more)\s+servings?\b", lower):
        return (base + 1) if base else None

    for pattern in _SERVINGS_TARGET_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                n = int(match.group(1))
                if n > 0:
                    return n
            except (TypeError, ValueError):
                continue
    return None

def _scale_ingredients(ingredients: list, ratio: float) -> list:
    """
    return a new ingredient list with numeric quantities multiplied by ratio
    """
    if not ingredients or ratio == 1:
        return ingredients or []
    scaled = []
    for ing in ingredients:
        if not isinstance(ing, dict):
            scaled.append(ing)
            continue
        qty = ing.get("quantity")
        new_qty = scale_quantity(str(qty) if qty is not None else None, ratio)
        scaled.append({**ing, "quantity": new_qty})
    return scaled

def _nutrition_is_invalid(nutrition) -> bool:
    """
    true if nutrition is missing, all zeros, or unusable
    """
    if not nutrition or not isinstance(nutrition, dict):
        return True
    values = []
    for key in NUTRITION_KEYS:
        try:
            values.append(float(nutrition.get(key)))
        except (TypeError, ValueError):
            return True
    if all(v <= 0 for v in values):
        return True
    return False

def _coerce_int(value, fallback):
    if value is None:
        return fallback
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback

def _as_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in ("true", "1", "yes"):
            return True
        if lower in ("false", "0", "no", ""):
            return False
    return default

def _unwrap_value_modified(raw, fallback_value=None) -> tuple:
    """
    accept either a bare value or {value, modified}
    returns (value, modified)
    """
    if isinstance(raw, dict) and ("value" in raw or "modified" in raw):
        return raw.get("value", fallback_value), _as_bool(raw.get("modified"), False)
    return raw if raw is not None else fallback_value, False

def _normalize_nutrition(raw) -> tuple:
    """
    unwrap nutrition {key: {value, modified}} or flat numbers -> (flat, flags)
    """
    flags = {key: False for key in NUTRITION_KEYS}
    if not raw or not isinstance(raw, dict):
        return None, flags

    flat: dict = {}
    for key in NUTRITION_KEYS:
        if key not in raw:
            continue
        value, modified = _unwrap_value_modified(raw.get(key))
        flat[key] = value
        flags[key] = modified

    for key, val in raw.items():
        if key in NUTRITION_KEYS:
            continue
        if isinstance(val, dict) and "value" in val:
            flat[key] = val.get("value")
        else:
            flat[key] = val

    return flat if flat else None, flags


def _mark_scaled_ingredients(before: list, after: list) -> list:
    """
    set modified=true when servings scale changed an ingredient quantity
    """
    if not after:
        return after or []
    before_qtys = []
    for ing in before or []:
        if isinstance(ing, dict):
            before_qtys.append(str(ing.get("quantity") or ""))
        else:
            before_qtys.append("")

    marked = []
    for i, ing in enumerate(after):
        if not isinstance(ing, dict):
            marked.append(ing)
            continue
        new_qty = str(ing.get("quantity") or "")
        old_qty = before_qtys[i] if i < len(before_qtys) else new_qty
        if new_qty != old_qty:
            marked.append({**ing, "modified": True})
        else:
            marked.append({**ing, "modified": _as_bool(ing.get("modified"), False)})
    return marked


def _normalize_item_modified_flags(items: list) -> list:
    """
    coerce each item's modified field to a boolean (default false)
    """
    if not isinstance(items, list):
        return []
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            normalized.append(item)
            continue
        normalized.append({**item, "modified": _as_bool(item.get("modified"), False)})
    return normalized


_AMBIGUOUS_FOR_N = re.compile(
    r"\bmake\s+(?:it|this)\s+for\s+(\d+)\b",
    re.IGNORECASE,
)
_TIME_AFTER_FOR_N = re.compile(
    r"\bfor\s+\d+\s*(?:minutes?|hours?|mins?|hrs?|seconds?)\b",
    re.IGNORECASE,
)
_MSG_MORE_SPECIFIC = "Not quite sure what you mean? Could you make a more specific request?"

def _ambiguous_make_for_n(message: str) -> bool:
    """
    true for 'make it for 3' without servings/people/portions (not a time phrase)
    """
    text = message or ""
    if not _AMBIGUOUS_FOR_N.search(text):
        return False
    if _TIME_AFTER_FOR_N.search(text):
        return False
    if re.search(r"\b(servings?|people|persons?|guests|portions?)\b", text, re.IGNORECASE):
        return False
    return True


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")

    ingredients = (
        db.query(RecipeIngredient, Ingredient)
        .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .filter(RecipeIngredient.recipe_id == recipe_id)
        .order_by(RecipeIngredient.id)
        .all()
    )

    recipe.ingredients = []
    for recipe_ing, ing in ingredients:
        display_name = get_display_name(recipe_ing.raw_ingredient) or (
            ing.name.strip() if ing.name else None
        )
        recipe.ingredients.append(
            {
                "id": ing.id,
                "name": display_name,
                "quantity": format_quantity(recipe_ing.quantity),
                "unit": abbreviate_unit(recipe_ing.unit),
                "container_size": recipe_ing.container_size,
                "raw_ingredient": recipe_ing.raw_ingredient,
                "section_title": recipe_ing.section_title,
                "food_type": ing.food_type,
                "allergens": ing.allergens or [],
                "is_vegan": ing.is_vegan,
                "is_vegetarian": ing.is_vegetarian,
                "is_gluten_free": ing.is_gluten_free,
            }
        )

    return recipe


class ModifyRequest(BaseModel):
    message: str = ""
    recipe: dict | None = None  # optional on-screen snapshot (cleaned/modified)


def _build_text(recipe, db):
    """build ingredient and directions text from DB recipe"""

    ingredients = (
        db.query(RecipeIngredient, Ingredient)
        .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .filter(RecipeIngredient.recipe_id == recipe.id)
        .order_by(RecipeIngredient.id)
        .all()
    )

    ings_lines = []
    for recipe_ing, ing in ingredients:
        name = get_display_name(recipe_ing.raw_ingredient) or (
            ing.name.strip() if ing.name else "unknown"
        )
        qty = f"{recipe_ing.quantity or ''} {recipe_ing.unit or ''}".strip()
        line = f"{qty} {name}".strip() if qty else name
        ings_lines.append(f"- {line}")

    directions = recipe.directions or []
    dirs_lines = [f"{j+1}. {d['direction']}" for j, d in enumerate(directions)]

    return "\n".join(ings_lines), "\n".join(dirs_lines)


def _build_text_from_snapshot(snapshot: dict):
    """build ingredient and directions text from a client-provided recipe snapshot"""
    ings_lines = []
    for ing in snapshot.get("ingredients") or []:
        name = (ing.get("name") or "").strip() or "unknown"
        qty_parts = [
            str(ing.get("quantity") or "").strip(),
            str(ing.get("unit") or "").strip(),
        ]
        qty = " ".join(p for p in qty_parts if p)
        container = (ing.get("container_size") or "").strip()
        if container:
            qty = f"{qty} ({container})".strip() if qty else f"({container})"
        line = f"{qty} {name}".strip() if qty else name
        section = ing.get("section_title")
        if section:
            ings_lines.append(f"- [{section}] {line}")
        else:
            ings_lines.append(f"- {line}")

    dirs_lines = []
    for j, d in enumerate(snapshot.get("directions") or []):
        text = d.get("direction") if isinstance(d, dict) else str(d)
        if text and str(text).strip():
            dirs_lines.append(f"{j + 1}. {str(text).strip()}")

    name = (snapshot.get("name") or "").strip()
    return name, "\n".join(ings_lines), "\n".join(dirs_lines)


def _call_openai(prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> tuple[dict, int]:
    """Send prompt to OpenAI and return (parsed JSON dict, total_tokens)."""

    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        parts = content.split("```")
        content = parts[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    total_tokens = 0
    if response.usage is not None:
        total_tokens = int(response.usage.total_tokens or 0)

    return json.loads(content), total_tokens


def _classify_modify_request(message: str, servings) -> tuple[dict, int]:
    """LLM gate: {action: modify} or {action: clarify, message: ...}."""
    prompt = build_clarify_modify_prompt(message, servings=servings)
    result, tokens = _call_openai(prompt, max_tokens=200)
    if not isinstance(result, dict):
        return {"action": "modify"}, tokens
    action = (result.get("action") or "").strip().lower()
    if action == "clarify":
        msg = (result.get("message") or "").strip()
        if msg:
            return {"action": "clarify", "message": msg}, tokens
    return {"action": "modify"}, tokens


def _ai_json_response(payload: dict, anon_id: str | None = None) -> JSONResponse:
    response = JSONResponse(content=jsonable_encoder(payload))
    attach_anon_cookie(response, anon_id)
    return response


def _sanitize_directions(directions) -> list:
    """Drop blank direction rows and renumber step_num per section starting at 1."""
    if not isinstance(directions, list):
        return []

    cleaned = []
    step_num_by_section: dict = {}
    for step in directions:
        if not isinstance(step, dict):
            continue
        text = str(step.get("direction") or "").strip()
        if not text:
            continue
        section = step.get("section_title")
        key = section if section is not None else ""
        step_num_by_section[key] = step_num_by_section.get(key, 0) + 1
        cleaned.append({
            **step,
            "direction": text,
            "step_num": step_num_by_section[key],
            "section_title": section,
        })
    return cleaned


def _attach_metadata(
    ai_result: dict,
    recipe: Recipe,
    is_modify: bool,
    baseline: dict | None = None,
    message: str = "",
) -> dict:
    """merge AI output with original metadata; guard time/servings/nutrition on modify"""

    name = ai_result.get("name", recipe.name)
    ingredients = ai_result.get("ingredients", [])
    directions = _sanitize_directions(ai_result.get("directions", []))

    base_nutrition = (baseline or {}).get("nutrition") if baseline else recipe.nutrition
    base_time = (baseline or {}).get("total_time") if baseline else recipe.total_time
    base_servings = (baseline or {}).get("servings") if baseline else recipe.servings
    base_ingredients = (baseline or {}).get("ingredients") if baseline else None
    if base_time is None:
        base_time = recipe.total_time
    if base_servings is None:
        base_servings = recipe.servings
    if base_nutrition is None:
        base_nutrition = recipe.nutrition

    nutrition_modified = {key: False for key in NUTRITION_KEYS}
    total_time_modified = False
    servings_modified = False

    if is_modify:
        ai_servings_raw, ai_servings_modified = _unwrap_value_modified(
            ai_result.get("servings"), base_servings
        )
        ai_time_raw, ai_time_modified = _unwrap_value_modified(
            ai_result.get("total_time"), base_time
        )
        ai_nutrition_flat, ai_nutrition_flags = _normalize_nutrition(
            ai_result.get("nutrition")
        )

        if _wants_servings_change(message):
            target = _parse_target_servings(message, base_servings)
            if target is not None:
                servings = target
                servings_modified = True
                try:
                    current = int(float(base_servings)) if base_servings is not None else 0
                except (TypeError, ValueError):
                    current = 0
                if current > 0 and target != current:
                    ratio = target / current
                    dietary = bool(re.search(
                        r"\b(vegan|vegetarian|keto|gluten[\s-]?free|substitute|replace|swap)\b",
                        message or "",
                        re.IGNORECASE,
                    ))
                    # Servings-only: scale the on-screen snapshot (avoids double-scaling AI qtys).
                    # Mixed dietary+servings: scale AI ingredients (may include substitutions).
                    if dietary and ingredients:
                        source = ingredients
                    else:
                        source = base_ingredients if base_ingredients else (ingredients or [])
                    scaled = _scale_ingredients(source, ratio)
                    ingredients = _mark_scaled_ingredients(source, scaled)
            else:
                servings = _coerce_int(ai_servings_raw, base_servings)
                servings_modified = ai_servings_modified and servings != base_servings
        else:
            servings = base_servings
            servings_modified = False

        if _wants_time_change(message):
            total_time = _coerce_int(ai_time_raw, base_time)
            total_time_modified = ai_time_modified
        else:
            total_time = base_time
            total_time_modified = False

        # servings-only requests keep per-serving nutrition unchanged
        if _wants_servings_change(message) and not re.search(
            r"\b(vegan|vegetarian|keto|gluten[\s-]?free|substitute|replace|swap|less\s+cal|lower\s+cal|healthier)\b",
            message or "",
            re.IGNORECASE,
        ):
            nutrition = base_nutrition
            nutrition_modified = {key: False for key in NUTRITION_KEYS}
        elif _nutrition_is_invalid(ai_nutrition_flat):
            nutrition = base_nutrition
            nutrition_modified = {key: False for key in NUTRITION_KEYS}
        else:
            nutrition = ai_nutrition_flat
            nutrition_modified = ai_nutrition_flags

        ingredients = _normalize_item_modified_flags(ingredients)
        directions = _normalize_item_modified_flags(directions)
    else:
        nutrition = recipe.nutrition
        total_time = recipe.total_time
        servings = recipe.servings
        ingredients = _normalize_item_modified_flags(ingredients) if ingredients else ingredients
        directions = _normalize_item_modified_flags(directions) if directions else directions

    return {
        "name": name,
        "ingredients": ingredients,
        "directions": directions,
        "nutrition": nutrition,
        "nutrition_modified": nutrition_modified if is_modify else None,
        "total_time": total_time,
        "total_time_modified": total_time_modified if is_modify else None,
        "servings": servings,
        "servings_modified": servings_modified if is_modify else None,
        "image": recipe.image,
        "link": recipe.link,
        "tags": recipe.tags,
        "date": recipe.date.isoformat() if recipe.date else None,
        "id": recipe.id,
        "rating": None if is_modify else recipe.rating,
        "num_ratings": None if is_modify else recipe.num_ratings,
    }


@router.post("/{recipe_id}/clean")
def clean_recipe(
    recipe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int | None = Depends(get_optional_user_id),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")

    subject_key, anon_id = resolve_subject(request, user_id)

    if recipe.cleaned_recipe:
        return _ai_json_response(
            _attach_metadata(recipe.cleaned_recipe, recipe, is_modify=False),
            anon_id,
        )

    ensure_under_limit(db, subject_key)

    ings_text, dirs_text = _build_text(recipe, db)
    prompt = build_clean_prompt(recipe.name, ings_text, dirs_text)

    try:
        result, tokens = _call_openai(prompt)
        response = _attach_metadata(result, recipe, is_modify=False)
        recipe.cleaned_recipe = {
            "name": response["name"],
            "ingredients": response["ingredients"],
            "directions": response["directions"],
        }
        db.commit()
        add_tokens(db, subject_key, tokens)
        return _ai_json_response(response, anon_id)
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{recipe_id}/modify")
def modify_recipe(
    recipe_id: int,
    body: ModifyRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int | None = Depends(get_optional_user_id),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="recipe not found")

    if not body.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Modification message cannot be empty. Use /clean for cleaning.",
        )

    subject_key, anon_id = resolve_subject(request, user_id)
    ensure_under_limit(db, subject_key)

    snapshot = body.recipe or {}
    if body.recipe:
        name, ings_text, dirs_text = _build_text_from_snapshot(body.recipe)
        if not name:
            name = recipe.name
    else:
        name = recipe.name
        ings_text, dirs_text = _build_text(recipe, db)

    total_time = snapshot.get("total_time", recipe.total_time)
    servings = snapshot.get("servings", recipe.servings)
    nutrition = snapshot.get("nutrition", recipe.nutrition)

    baseline = {
        "total_time": total_time,
        "servings": servings,
        "nutrition": nutrition,
        "ingredients": snapshot.get("ingredients") if body.recipe else None,
    }

    try:
        tokens_used = 0
        decision, classify_tokens = _classify_modify_request(body.message, servings)
        tokens_used += classify_tokens

        if decision.get("action") == "clarify":
            add_tokens(db, subject_key, tokens_used)
            return _ai_json_response({"conflict": decision["message"]}, anon_id)

        # ambiguous "make it for N" must not silently no op
        if _ambiguous_make_for_n(body.message):
            add_tokens(db, subject_key, tokens_used)
            return _ai_json_response({"conflict": _MSG_MORE_SPECIFIC}, anon_id)

        # classify tokens are not committed yet
        # block modify if they would exhaust the day
        if get_tokens_used(db, subject_key) + tokens_used >= DAILY_TOKEN_LIMIT:
            add_tokens(db, subject_key, tokens_used)
            raise HTTPException(status_code=429, detail=LIMIT_MESSAGE)

        prompt = build_modify_prompt(
            name,
            ings_text,
            dirs_text,
            body.message,
            total_time=total_time,
            servings=servings,
            nutrition=nutrition,
        )
        result, modify_tokens = _call_openai(prompt)
        tokens_used += modify_tokens
        add_tokens(db, subject_key, tokens_used)
        payload = _attach_metadata(
            result,
            recipe,
            is_modify=True,
            baseline=baseline,
            message=body.message,
        )
        return _ai_json_response(payload, anon_id)
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
