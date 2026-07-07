import re
from difflib import SequenceMatcher
from scripts.normalize_ingredients import normalize_ingredient
# from scripts.parse_recipe import clean_ingredient_text, strip_units


UNITS = r"cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|oz|lb|lbs|pound|pounds|g|gram|grams|kg|ml|l|kilograms|milliliters|liters|can|cans|box|boxes|clove|cloves|pinch|dash|package|packages|slice|slices|piece|pieces|head|bunch|sprig|sprigs|stick|sticks"
MATCH_THRESHOLD = 0.5
FILLERS = ("you can also", "throw some", "health conscious", "if desired", "as needed", "as necessary")

# section headers for ingredients
HEADER = re.compile(
    r"^(sauce|ingredients?|topping|filling|marinade|dressing|"
    r"glaze|frosting|batter|crust|stuffing|garnish(?:es)?|fish)\s*\d*:?\s*$",
    re.IGNORECASE,
)
FOR_THE_HEADER = re.compile(r"^for the\s+.+$", re.IGNORECASE)
FOR_NOUN_HEADER = re.compile(r"^for\s+(?!the\s).+$", re.IGNORECASE)
WORD_FOR_HEADER = re.compile(r"^[A-Z][\w\s&'-]*\s+for\s+.+$")
TO_HEADER = re.compile(
    r"^to\s+(?:serve|assemble|garnish|accompany|finish|decorate|top|grill|"
    r"complete|accompany when serving)(?:\s+.+)?\s*\d*:?\s*$",
    re.IGNORECASE,
)
FOR_SUBSECTION = re.compile(
    r"^for\s+(sauce|ingredients?|topping|filling|marinade|dressing|"
    r"glaze|frosting|batter|crust|stuffing|garnish(?:es)?)\s*\d*:?\s*$",
    re.IGNORECASE,
)
SUCH_AS_HEADER = re.compile(r"^.+\ssuch as\s*$", re.IGNORECASE)
SECTION_SUFFIX = (r"sauce|filling|topping|marinade|dressing|glaze|frosting|batter|crust|garnish|stuffing")
MULTIWORD_HEADER = re.compile(rf"^[a-z][a-z\s&'-]*\s+(?:{SECTION_SUFFIX})\s*\d*:?\s*:?\s*$", re.IGNORECASE)

# most likely not ingredient section headers
CONDIMENTS = frozenset({"soy sauce", "fish sauce", "tomato sauce", "hot sauce", "barbecue sauce", "worcestershire sauce", "oyster sauce", "hoisin sauce", "chili sauce", "pizza sauce", "applesauce"})

def format_section_title(text):
    text = re.sub(r"\s+", " ", str(text).strip())
    text = text.rstrip(":").strip()
    if not text:
        return text
    if text.isupper():
        return text.title()
    return text[0].upper() + text[1:]

def begins_with_quantity(text):
    from scripts.parse_recipe import clean_ingredient_text, strip_units
    cleaned = clean_ingredient_text(text) or str(text).strip()
    stripped = strip_units(cleaned)

    return bool(stripped and stripped != cleaned)


def parse_section_header(text):
    """
    return normalized section title if text is an nlg section header, or else None.
    """
    if not text or not str(text).strip():
        return None

    raw = str(text).strip().rstrip(":").strip()
    from scripts.parse_recipe import clean_ingredient_text
    lower = (clean_ingredient_text(text) or raw).lower().strip()
    words = lower.split()

    if HEADER.match(lower):
        return format_section_title(raw)
    if FOR_THE_HEADER.match(lower):
        return format_section_title(raw)
    if (FOR_NOUN_HEADER.match(lower) and len(words) <= 5 and "," not in lower and not begins_with_quantity(text)):
        return format_section_title(raw)
    if (WORD_FOR_HEADER.match(raw) and len(words) <= 5 and "," not in lower and not begins_with_quantity(text)):
        return format_section_title(raw)
    if TO_HEADER.match(lower) and "," not in lower and not begins_with_quantity(text):
        return format_section_title(raw)
    if FOR_SUBSECTION.match(lower):
        return format_section_title(raw)
    if SUCH_AS_HEADER.match(lower) and len(words) <= 4:
        return format_section_title(raw)
    if begins_with_quantity(text):
        return None
    if "," in lower or re.search(r"\b(your|favorite|favourite|optional)\b", lower):
        return None
    if lower in CONDIMENTS:
        return None
    if MULTIWORD_HEADER.match(lower) and len(words) <= 4:
        return format_section_title(raw)

    return None


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
    if parse_section_header(text):
        return True
    
    from scripts.parse_recipe import clean_ingredient_text
    cleaned = clean_ingredient_text(text)
    text = cleaned or str(text).strip()
    lower = text.lower()
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