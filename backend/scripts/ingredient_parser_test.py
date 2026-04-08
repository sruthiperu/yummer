from ingredient_parser import parse_ingredient

# Test with a simple ingredient
try:
    result = parse_ingredient("2 cups flour")
    print(f"Success: {result}")
    print(f"Amount: {result.amount}")
    print(f"Name: {result.name}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")