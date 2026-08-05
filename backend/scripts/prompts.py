import yaml
import os
import json

_prompts = None

def load_prompts():
    global _prompts
   
    if _prompts is None:
        path = os.path.join(os.path.dirname(__file__), "..", "prompts.yaml")
        with open(path) as f:
            _prompts = yaml.safe_load(f)
    
    return _prompts


def build_clean_prompt(name, ingredients, directions):
    prompts = load_prompts()
    p = prompts["clean_recipe"]
    template = p["user"]
    return (template.replace("__NAME__", name).replace("__INGREDIENTS__", ingredients).replace("__DIRECTIONS__", directions))


def build_modify_prompt(name, ingredients, directions, message, total_time=None, servings=None, nutrition=None):
    prompts = load_prompts()
    p = prompts["modify_recipe"]
    template = p["user"]

    time_str = str(total_time) if total_time is not None else "unknown"
    servings_str = str(servings) if servings is not None else "unknown"
    if nutrition is None:
        nutrition_str = "unknown"
    elif isinstance(nutrition, str):
        nutrition_str = nutrition
    else:
        nutrition_str = json.dumps(nutrition)

    return (
        template
        .replace("__NAME__", name or "")
        .replace("__TOTAL_TIME__", time_str)
        .replace("__SERVINGS__", servings_str)
        .replace("__NUTRITION__", nutrition_str)
        .replace("__INGREDIENTS__", ingredients or "")
        .replace("__DIRECTIONS__", directions or "")
        .replace("__MESSAGE__", message or "")
    )


def build_clarify_modify_prompt(message, servings=None):
    prompts = load_prompts()
    p = prompts["clarify_modify_request"]
    template = p["user"]
    servings_str = str(servings) if servings is not None else "unknown"
    return (
        template
        .replace("__SERVINGS__", servings_str)
        .replace("__MESSAGE__", message or "")
    )
