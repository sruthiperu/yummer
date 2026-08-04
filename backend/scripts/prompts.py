import yaml
import os

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


def build_modify_prompt(name, ingredients, directions, message):
    prompts = load_prompts()
    p = prompts["modify_recipe"]
    template = p["user"]
    return (template.replace("__NAME__", name).replace("__INGREDIENTS__", ingredients).replace("__DIRECTIONS__", directions).replace("__MESSAGE__", message))