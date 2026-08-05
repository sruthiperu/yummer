# Format quantities of ingredients
# ex. 9/4 cup -> 2 1/4 cup

from fractions import Fraction


def _parse_quantity(qty: str) -> Fraction | None:
    """
    parse int/float/simple fraction/mixed number into a Fraction, or None
    """
    text = qty.strip()
    if not text:
        return None

    # Mixed number: "1 1/2"
    if " " in text and "/" in text:
        parts = text.split(None, 1)
        if len(parts) == 2:
            try:
                whole = Fraction(parts[0])
                rem = Fraction(parts[1])
                return whole + rem
            except (ValueError, ZeroDivisionError):
                return None

    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        pass

    try:
        return Fraction(float(text))
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def format_quantity(qty: str | None) -> str | None:
    if not qty:
        return qty
    text = qty.strip()

    if " " in text and "/" in text:
        return text

    if "/" in text:
        try:
            f = Fraction(text)
            whole = int(f // 1)
            rem = f % 1
            if rem == 0:
                return str(whole)
            if whole == 0:
                return f"{rem.numerator}/{rem.denominator}"
            return f"{whole} {rem.numerator}/{rem.denominator}"
        except (ValueError, ZeroDivisionError):
            return text

    return text     # whole numbers, decimals left as is


def scale_quantity(qty: str | None, ratio: float) -> str | None:
    """
    multiply a quantity string by ratio; return unchanged if not numeric
    """
    if not qty or ratio == 1:
        return qty
    parsed = _parse_quantity(str(qty))
    if parsed is None:
        return qty
    try:
        scaled = parsed * Fraction(str(ratio))
    except (ValueError, ZeroDivisionError):
        return qty
    
    if scaled.denominator == 1:
        return str(int(scaled))

    approx = scaled.limit_denominator(16)
    whole = int(approx // 1)
    rem = approx % 1
    if rem == 0:
        return str(whole)
    frac = f"{rem.numerator}/{rem.denominator}"
    if whole == 0:
        return frac
    return f"{whole} {frac}"


UNIT_ABBREVIATIONS: dict[str, str] = {
    "teaspoon": "tsp", "teaspoons": "tsp", "tsp": "tsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp", "tbsp": "tbsp",
    "fluid ounce": "fl oz", "fluid ounces": "fl oz",
    "ounce": "oz", "ounces": "oz", "oz": "oz",
    "pound": "lb", "pounds": "lb", "lb": "lb", "lbs": "lb",
    "gram": "g", "grams": "g", "g": "g",
    "kilogram": "kg", "kilograms": "kg", "kg": "kg",
    "milliliter": "ml", "milliliters": "ml", "ml": "ml",
    "liter": "L", "liters": "L", "L": "L",
    "cup": "cup", "cups": "cups",
    "pint": "pt", "pints": "pt",
    "quart": "qt", "quarts": "qt",
    "gallon": "gal", "gallons": "gal",
    "can": "can", "cans": "cans", "box": "box", "boxes": "boxes",
    "clove": "clove", "cloves": "cloves",
    "pinch": "pinch", "dash": "dash", 
    "package": "pkg", "packages": "pkg", 
    "slice": "slice", "slices": "slices", 
    "piece": "pc", "pieces": "pc", 
    "head": "head", "bunch": "bunch",
    "bun": "bun", "buns": "buns",
    "sprig": "sprig", "sprigs": "sprig",
    "stick": "stick", "sticks": "stick",
}

def abbreviate_unit(unit: str | None) -> str | None:
    if not unit:
        return unit
    key = unit.strip().lower()
    return UNIT_ABBREVIATIONS.get(key, unit.strip())