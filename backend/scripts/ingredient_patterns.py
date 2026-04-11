# Contains patterns to normalize ingredients, food types (with vegan, vegatarian, gluten-free tags), and common allergens

import re

patterns = [
    # milk
    (r'\b(almond|soy|oat|coconut|pea|rice|macadamia|cashew|pistachio|flax|flaxseed|hazelnut|hemp)\s*milk\b', r'\1 milk'),      # keep type
    (r'\b(whole|2%|skim|lactose[- ]?free|organic|reduced[- ]?fat|low[- ]?fat|fat[- ]?free|raw)\s*milk\b', 'milk'),     # discard type

    # eggs
    (r'\b(duck|quail|ostrich)\s*eggs?\b', r'\1 egg'),
    (r'\b(organic|pasture[- ]?raised|cage[- ]?free|free[- ]?range|farm[- ]?fresh|brown|white|vegetarian[- ]?fed)?\s*egg\b', 'egg'),

    # flour
    (r'\b(all[- ]?purpose|plain|white|unbleached|enriched|self[- ]?rising|self[- ]?raising|ap)?\s*flour\b', 'flour'),
    (r'\bwhole\s*wheat\s*flour\b', 'whole wheat flour'),
    (r'\b(bread|cake|pastry|almond|coconut|rice|oat|chickpea|buckwheat|quinoa|tapioca|cassava|potato|spelt|rye|teff|amaranth|sorghum)\s*flour\b', r'\1 flour'),

    # cheese
    (r'\b(cheddar|mozzarella|parmesan|swiss|provolone|gouda|brie|camembert|feta|goat|blue|ricotta|cottage|cream)\s*cheese\b', r'\1 cheese'),
    (r'\b(shredded|grated|sliced|pre[- ]?shredded|block)\s*(cheddar|mozzarella|parmesan)\s*cheese\b', r'\2 cheese'),
    (r'\b(fresh|shredded|grated|sliced|pre[- ]?shredded|block)\s*cheese\b', r'cheese'),

    # butter
    (r'\b(clarified|ghee|brown)\s*butter\b', r'\1 butter'),
    (r'\b(unsalted|salted|organic|sweet cream|grade a|grade aa|grass[- ]?fed|european[- ]?style|cultured|whipped|plant[- ]?based)?\s*butter\b', 'butter'),

    # yogurt
    (r'\b(greek|icelandic|australian|french|skyr|kefir|plant[- ]?based|soy|coconut|non[- ]?dairy|frozen)\s*yogurt\b', r'\1 yogurt'),
    (r'\b(plain|vanilla|strawberry|blueberry|raspberry|peach|cherry|lemon)\s*yogurt\b', r'\1 yogurt'),
    (r'\b(traditional)?\s*yogurt\b', 'yogurt'),

    # vegetables
    (r'\b(yellow|white|brown|spanish)?\s*onion\b', 'onion'),
    (r'\b(red)?\s*onion\b', r'\1 onion'),
    (r'\b(green|spring|scallion)\s*onions?\b', 'green onion'),
    (r'\b(fresh)?\s*garlic\s*cloves?\b', 'garlic'),
    (r'\b(russet|idaho|baking)?\s*potatoes?\b', 'potato'),
    (r'\b(yukon|gold|yellow)?\s*potatoes?\b', 'yellow potato'),
    (r'\b(red|new|baby)?\s*potatoes?\b', 'red potato'),
    (r'\bsweet\s*potatoes?\b', 'sweet potato'),
    (r'\b(roma|plum|cherry|grape)?\s*tomatoes?\b', r'\1 tomato'),
    (r'\b(bell|sweet)\s*peppers?\b', 'bell pepper'),
    (r'\b(jalapeno|habanero|serrano|poblano|anaheim|cayenne|thai)\s*peppers?\b', r'\1 pepper'),
    (r'\b(romaine|iceberg|butter|bibb)\s*lettuce\b', r'\1 lettuce'),
    (r'\b(broccoli|cauliflower|asparagus|zucchini|cucumber|celery|carrot)\b', r'\1'),

    # fruits
    (r'\b(lemon|lime|orange|grapefruit|clementine|tangerine)\s*(juice|zest)?\b', r'\1 \2'),
    (r'\b(strawberry|blueberry|raspberry|blackberry|cranberry)\s*berries?\b', r'\1'),

    # meat
    (r'\b(boneless|skinless)?\s*chicken\s*breast\b', 'chicken breast'),
    (r'\b(boneless|skinless)?\s*chicken\s*thigh\b', 'chicken thigh'),
    (r'\b(boneless|skinless)?\s*chicken\b', 'chicken'),
    (r'\b(lean)?\s*(ground|minced)\s*beef\b', 'ground beef'),
    (r'\b(ground|minced)\s*(turkey|pork|lamb|chicken)\b', r'ground \2'),
    (r'\b(beef|ribeye|sirloin|tenderloin)\s*steak\b', 'beef steak'),
    (r'\b(pork|boston)\s*shoulder\b', 'pork shoulder'),

    # broth, stock
    (r'\b(chicken|beef|vegetable|fish|bone)\s*(broth|stock)\b', r'\1 broth'),

    # seafood
    (r'\b(salmon|tuna|halibut|cod|tilapia|trout|mackerel|sardine|anchovy)\s*(fillet|steak)?\b', r'\1'),
    (r'\b(shrimp|prawn)s?\b', 'shrimp'),
    (r'\b(crab|lobster|scallop|mussel|clam|oyster)s?\b', r'\1'),    # make singular

    # sugar
    (r'\b(white|refined|granulated|table|caster|superfine)?\s*sugar\b', 'sugar'),
    (r'\b(powdered)\s*sugar\b', 'powdered sugar'),
    (r'\b(light|dark|golden|demerara|turbinado|muscovado)\s*brown\s*sugar\b', 'brown sugar'),

    # syrup
    (r'\b(agave|maple|date|coconut|brown rice|malt|golden)\s*syrup\b', r'\1 syrup'),

    # honey
    (r'\b(manuka|clover|wildflower|orange blossom)\s*honey\b', r'\1 honey'),

    # oil
    (r'\b(avocado|sesame|coconut|walnut|grapeseed|sunflower|safflower|canola|peanut|palm|flaxseed|hemp|pumpkin seed)\s*oil\b', r'\1 oil'),
    (r'\b(virgin|extra[- ]?virgin|light|pure|refined)?\s*olive oil\b', r'\1 olive oil'),
    (r'\b(vegetable|cooking|frying)\s*oil\b', 'vegetable oil'),

    # nuts
    (r'\b(chopped|sliced|slivered|roasted|raw|salted|unsalted)\s+(almond|walnut|pecan|cashew|peanut|pistachio|hazelnut|macadamia)s?\b', r'\2'),
    (r'\b(almond|walnut|pecan|cashew|peanut|pistachio|hazelnut|macadamia)s?\s+(chopped|sliced|slivered|roasted|raw|salted|unsalted)\b', r'\1'),
    (r'\b(sesame|sunflower|pumpkin|chia|flax|hemp)\s*seeds?\b', r'\1 seed'),

    # rice
    (r'\b(brown|basmati|jasmine|arborio|calrose)\s*rice\b', r'\1 rice'),
    (r'\b(white)?\s*rice\b', 'rice'),

    # oats
    (r'\b(old[- ]?fashioned|rolled|steel[- ]?cut|instant|quick)?\s*oats?\b', 'oat'),

    # pasta
    (r'\b(pasta|noodle|spaghetti|penne|rigatoni|fettuccine|linguine)\b', 'pasta'),

    # beans
    (r'\b(black|kidney|pinto|navy|great northern|cannellini)\s*beans?\b', r'\1 bean'),
    (r'\b(green|french)\s*beans?\b', 'green bean'),
    (r'\b(chickpea|garbanzo)\s*beans?\b', 'chickpea'),
    (r'\b(lentil|pea)\b', r'\1'),

    # seasoning
    (r'\b(table|sea|himalayan|pink|kosher)\s*salt\b', 'salt'),
    (r'\b(red|green|black|white)\s*pepper\b', r'\1 pepper'),
    (r'\b(oregano|thyme|rosemary|basil|parsley|cilantro|dill|mint|sage|bay)\s*(leaves?)?\b', r'\1'),
]


food_types = {
    # vegetables
    "onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "yellow potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sweet potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "garlic": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "roma tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cherry tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "grape tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "jalapeno": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "habanero": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "serrano": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "poblano": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "romaine lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "iceberg lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "spinach": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "kale": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "broccoli": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cauliflower": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "carrot": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "celery": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cucumber": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "zucchini": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "squash": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "butternut squash": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "acorn squash": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "asparagus": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green bean": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "pea": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "corn": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mushroom": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    
    # protein
    "chicken": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "chicken breast": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "chicken thigh": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "ground chicken": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "turkey": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "ground turkey": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "beef": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "ground beef": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "beef steak": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "pork": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "pork chop": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "bacon": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "sausage": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": False},  
    "ham": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "lamb": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "salmon": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "tuna": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "shrimp": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "crab": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "lobster": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "fish": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "duck egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "quail egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "ostrich egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "tofu": {"type": "protein", "vegan": True, "vegetarian": True, "gluten_free": True},
    
    # dairy
    "milk": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "butter": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "unsalted butter": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "salted butter": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cheddar cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "mozzarella cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "parmesan cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "swiss cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "feta cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "goat cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "blue cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "ricotta cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cottage cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cream cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "greek yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "sour cream": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cream": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "half and half": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    
    # fat (oils)
    "oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "olive oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "vegetable oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "coconut oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "avocado oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sesame oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "canola oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "grapeseed oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "walnut oil": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    
    # seasoning
    "salt": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "pepper": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "black pepper": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "white pepper": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cumin": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "paprika": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cinnamon": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "nutmeg": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "turmeric": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "ginger": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "coriander": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cardamom": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "clove": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "allspice": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "oregano": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "thyme": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "rosemary": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "basil": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "parsley": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cilantro": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "dill": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mint": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sage": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "chili powder": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cayenne": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red pepper flakes": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    
    # sweeteners
    "sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "brown sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "powdered sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "maple syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "agave syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "corn syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "honey": {"type": "sweetener", "vegan": False, "vegetarian": True, "gluten_free": True},
}


allergens = {
    # dairy
    "milk": ["dairy"], "butter": ["dairy"], "unsalted butter": ["dairy"], "salted butter": ["dairy"], 
    "cheese": ["dairy"], "cheddar cheese": ["dairy"], "mozzarella cheese": ["dairy"], "parmesan cheese": ["dairy"], "swiss cheese": ["dairy"], 
    "feta cheese": ["dairy"], "goat cheese": ["dairy"], "blue cheese": ["dairy"], "ricotta cheese": ["dairy"], "cottage cheese": ["dairy"], "cream cheese": ["dairy"], 
    "yogurt": ["dairy"], "greek yogurt": ["dairy"],
    "sour cream": ["dairy"], "cream": ["dairy"],
    "half and half": ["dairy"],
    
    # eggs
    "egg": ["eggs"], "duck egg": ["eggs"], "quail egg": ["eggs"],
    
    # fish
    "fish": ["fish"], "salmon": ["fish"], "tuna": ["fish"], "cod": ["fish"], "trout": ["fish"], "mackerel": ["fish"],
    "tilapia": ["fish"], "halibut": ["fish"],
    "sardine": ["fish"], "anchovy": ["fish"],
    
    # shellfish
    "shrimp": ["shellfish"], "clam": ["shellfish"], "oyster": ["shellfish"], "prawn": ["shellfish"], "crab": ["shellfish"], 
    "lobster": ["shellfish"], "scallop": ["shellfish"], "mussel": ["shellfish"],
    
    # tree nuts
    "almond": ["tree nuts"], "walnut": ["tree nuts"], "pecan": ["tree nuts"], "cashew": ["tree nuts"], "pistachio": ["tree nuts"],
    "hazelnut": ["tree nuts"], "macadamia": ["tree nuts"], "almond flour": ["tree nuts"],
    "coconut": ["tree nuts"], "coconut oil": ["tree nuts"],
    
    # peanuts
    "peanut": ["peanuts"], "peanut oil": ["peanuts"],
    
    # wheat/gluten
    "wheat": ["wheat", "gluten"], "bread": ["wheat", "gluten"], "pasta": ["wheat", "gluten"], "noodles": ["wheat", "gluten"],
    "spaghetti": ["wheat", "gluten"], "couscous": ["wheat", "gluten"], "seitan": ["wheat", "gluten"],
    "flour": ["wheat", "gluten"], "whole wheat flour": ["wheat", "gluten"], 
    "bread flour": ["wheat", "gluten"], "cake flour": ["wheat", "gluten"], "pastry flour": ["wheat", "gluten"],
    "soy sauce": ["wheat", "gluten"],  
    
    # soy
    "tofu": ["soy"], "tempeh": ["soy"], "soy milk": ["soy"], "soy sauce": ["soy"], "edamame": ["soy"],
    
    # sesame
    "sesame seed": ["sesame"], "sesame oil": ["sesame"], "tahini": ["sesame"],
}