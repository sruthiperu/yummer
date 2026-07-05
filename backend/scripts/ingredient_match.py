import re
from difflib import SequenceMatcher
from scripts.normalize_ingredients import normalize_ingredient


UNITS = r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|ml|l|kilograms|milliliters|liters|can|cans|box|boxes|clove|cloves|pinch|dash|package|packages|slice|slices|piece|pieces|head|bunch|sprig|sprigs|stick|sticks"
MATCH_THRESHOLD = 0.5
FILLERS = ("you can also", "throw some", "health conscious", "if desired", "as needed", "as necessary")

HEADER = re.compile(
    r"^(sauce|for the|ingredients?|topping|filling|marinade|dressing|"
    r"glaze|frosting|batter|crust|stuffing|garnish)\s*\d*:?\s*$",
    re.IGNORECASE,
)


def normalize_text(text):
    """
    helper for ingredient_similarity function
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[\d/().,\-]+", " ", text)
    text = re.sub(rf"\b(?:{UNITS})\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def ingredient_similarity(foodcom_name, nlg_line):
    """
    score how well food.com ingredient name matches recipenlg ingredient name 
    """
    if not foodcom_name or not nlg_line:
        return 0.0

    fc = normalize_text(foodcom_name)
    nlg = normalize_text(nlg_line)
    if not fc or not nlg:
        return 0.0

    # foodcom name appears in recipenlg name
    if fc in nlg:
        return 1.0
    
    fc_flat = fc.replace(", juice of", " juice").replace(",", " ")
    nlg_flat = nlg.replace(",", " ")
    if fc_flat in nlg_flat:
        return 1.0

    # when order of words differs (e.g. {apple, orange} vs. {orange, apple})
    fc_words = set(fc.split())
    nlg_words = set(nlg.split())
    if fc_words and nlg_words:
        overlap = len(fc_words & nlg_words) / max(len(fc_words), len(nlg_words))
    else:
        overlap = 0.0

    ratio = SequenceMatcher(None, fc, nlg).ratio()
    return max(overlap, ratio)


def match_foodcom_name(nlg_line, foodcom_list, used_indices, threshold=MATCH_THRESHOLD):
    """
    find best unused food.com name for one recipenlg name/line
    """

    # no food.com names for this recipe
    if not foodcom_list:
        return None, None, 0.0

    best_name = None
    best_idx = None
    best_score = 0.0

    for i, fc_name in enumerate(foodcom_list):
        if i in used_indices or not fc_name:        # skip name
            continue

        score = ingredient_similarity(fc_name, nlg_line)
        if score > best_score:
            best_score = score
            best_name = fc_name
            best_idx = i

    if best_score < threshold:
        return None, None, best_score

    return best_name, best_idx, best_score


def nlg_line_not_ing(text):
    """
    returns true for nlg names that are not actual ingredients
    """

    if not text or not str(text).strip():
        return True

    text = str(text).strip()
    lower = text.lower()
    if HEADER.match(lower):
        return True

    if any(phrase in lower for phrase in FILLERS):
        return True

    # multiple sentences implies instruction (not ingredient)
    if lower.count(". ") >= 1 and len(lower) > 40:
        return True

    # remove unusually long lines
    if len(lower) > 120:
        return True

    return False


def is_valid_canonical(name):
    """
    check if canonical name is an actual ingredient
    """
    if not name:
        return False

    lower = name.lower().strip()
    if len(lower) > 80:     # unusually long
        return False

    if re.search(r"\d", lower):
        return False
    if re.search(rf"\b(?:{UNITS})\b", lower):
        return False
    if any(phrase in lower for phrase in FILLERS):
        return False

    return True


def resolve_canonical_name(nlg_line, foodcom_list, used_indices, threshold=MATCH_THRESHOLD):
    """
    skip fillers, try food.com content match, fall back to parsing recipenlg to return canonical ingredient name
    """
    
    if nlg_line_not_ing(nlg_line):
        return None

    fc_name, idx, score = match_foodcom_name(nlg_line, foodcom_list, used_indices, threshold=threshold)
    if fc_name is not None and idx is not None:
        used_indices.add(idx)
        canonical = normalize_ingredient(fc_name.strip())
        if is_valid_canonical(canonical):
            return canonical
        used_indices.discard(idx)

    # parse recipenlg
    from scripts.parse_recipe import get_quantity
    _, _, _, parsed = get_quantity(nlg_line)
    if not parsed:
        return None

    canonical = normalize_ingredient(parsed)
    if is_valid_canonical(canonical):
        return canonical

    return None