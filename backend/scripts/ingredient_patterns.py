# Contains patterns to normalize ingredients, food types (with vegan, vegatarian, gluten-free tags), and common allergens

import re

patterns = [
    # milk
    (r'\b(almond|soy|oat|coconut|pea|rice|macadamia|cashew|pistachio|flax|flaxseed|hazelnut|hemp)\s*milk\b', r'\1 milk'),      # keep type
    (r'\b(whole|2%|skim|lactose[- ]?free|organic|reduced[- ]?fat|low[- ]?fat|fat[- ]?free|raw)\s*milk\b(?!\s*yogurt)', 'milk'),     # discard type

    # eggs
    (r'\b(duck|quail|ostrich)\s*eggs?\b', r'\1 egg'),
    (r'\b(large|medium|small|organic|pasture[- ]?raised|cage[- ]?free|free[- ]?range|farm[- ]?fresh|brown|white|vegetarian[- ]?fed)?\s*eggs?\b', 'egg'),

    # flour
    (r'\b(all[- ]?purpose|plain|white|unbleached|enriched|self[- ]?rising|self[- ]?raising|ap)?\s*flour\b', 'flour'),
    (r'\bwhole\s*wheat\s*flour\b', 'whole wheat flour'),
    (r'\b(bread|cake|pastry|almond|coconut|rice|oat|chickpea|buckwheat|quinoa|tapioca|cassava|potato|spelt|rye|teff|amaranth|sorghum)\s*flour\b', r'\1 flour'),

    # cheese
    (r'\b(fresh|shredded|grated|sliced|pre[- ]?shredded|block)\s+', ''),
    (r'\b(cheddar|mozzarella|parmesan|swiss|provolone|gouda|brie|camembert|feta|goat|blue|ricotta|cottage|cream)\s*cheese\b', r'\1 cheese'),
    (r'\b(monterey|pepper)\s*jack\s*cheese\b', r'\1 jack cheese'),
    (r'\bcheese\b', 'cheese'),

    # nut/seed butters (before generic butter)
    (r'\b(?:(?:smooth|creamy|natural(?:[- ]style)?|chunky|crunchy|unsalted|salted|organic|low[- ]fat|no[- ]sugar[- ]added|old[- ]fashioned|super[- ]chunky|extra[- ]chunky|reduced[- ]fat)\s+)?(peanut|almond|cashew|sunflower|hazelnut|macadamia|walnut|pecan|pistachio)\s+butter\b', r'\1 butter'),

    # butter
    (r'\b(clarified|ghee|brown)\s*butter\b', r'\1 butter'),
    (r'\b(unsalted|salted|organic|sweet cream|grade a|grade aa|grass[- ]?fed|european[- ]?style|cultured|whipped|plant[- ]?based)\s+butter\b', 'butter'),
    (r'^butter$', 'butter'),

    # repair merged nut butters (glued forms, brand prefixes)
    (r'\b(?:(?:smooth|creamy|natural(?:[- ]style)?|chunky|crunchy|unsalted|salted|organic|low[- ]fat|no[- ]sugar[- ]added|old[- ]fashioned|super[- ]chunky|extra[- ]chunky|extra[- ]crunchy|reduced[- ]fat|all[- ]natural)\s+)?(peanut|almond|cashew|sunflower|hazelnut|macadamia|walnut|pecan|pistachio)butter\b', r'\1 butter'),
    (r'\b[\w\-\'\.]+\s+(peanut|almond|cashew|sunflower|hazelnut|macadamia|walnut|pecan|pistachio)\s+butter\b', r'\1 butter'),
    (r'\b(peanut|almond|cashew|sunflower|hazelnut|macadamia|walnut|pecan|pistachio)butter\b', r'\1 butter'),

    # sour cream
    (r'\b(?:fat[- ]?free|light|reduced[- ]?fat|nonfat|non[- ]?fat)\s+sour cream\b', 'sour cream'),

    # yogurt (use \s+ before yogurt — optional \s* eats the space after modifiers)
    (r'\b(greek|icelandic|australian|french|skyr|kefir|plant[- ]?based|soy|coconut|non[- ]?dairy|frozen)\s+yogurt\b', r'\1 yogurt'),
    (r'\b(plain|vanilla|strawberry|blueberry|raspberry|peach|cherry|lemon)\s+yogurt\b', r'\1 yogurt'),
    (r'\b(?:low[- ]?fat|nonfat|non[- ]?fat|fat[- ]?free|reduced[- ]?fat|light|whole[- ]?milk|full[- ]?fat)\s+(?:(?:greek|plain|vanilla|strawberry|frozen)\s+)?yogurt\b', 'yogurt'),
    (r'\bwhole\s+milk\s+yogurt\b', 'yogurt'),
    (r'\b(?:low[- ]?fat|nonfat|non[- ]?fat|fat[- ]?free|reduced[- ]?fat|light)\s+yogurt\b', 'yogurt'),
    (r'\btraditional\s+yogurt\b', 'yogurt'),
    (r'^yogurt$', 'yogurt'),
    (r'\b(greek|plain|vanilla|frozen|nonfat|icelandic|australian|french|strawberry|blueberry|raspberry|peach|cherry|lemon)yogurt\b', r'\1 yogurt'),
    (r'\b(low[- ]?fat|fat[- ]?free|reduced[- ]?fat|light|non[- ]?fat)yogurt\b', r'\1 yogurt'),

    # vegetables
    (r'\bcanned\s+', ''),
    (r'\b(?:texas\s+)?sweet\s+onion\b', 'sweet onion'),
    (r'\b(vidalia|walla walla|spanish|yellow|white|brown|red|sweet)\s+onion\b', r'\1 onion'),
    (r'\b(green|spring|scallion)\s*onions?\b', 'green onion'),
    (r'\bonions?\b', 'onion'),
    (r'\b(fresh)?\s*garlic\s*cloves?\b', 'garlic'),
    (r'\b(russet|idaho|baking)?\s*potatoes?\b', 'potato'),
    (r'\b(yukon|gold|yellow)?\s*potatoes?\b', 'yellow potato'),
    (r'\b(red|new|baby)?\s*potatoes?\b', 'red potato'),
    (r'\bsweet\s*potatoes?\b', 'sweet potato'),
    (r'\b(roma|plum|cherry|grape)?\s*tomatoes?\b', r'\1 tomato'),
    (r'\b(bell|sweet)\s*peppers?\b', 'bell pepper'),
    (r'\b(jalapeno|habanero|serrano|poblano|anaheim|cayenne|thai)\s*peppers?\b', r'\1 pepper'),
    (r'\b(romaine|iceberg|butter|bibb)\s*lettuce\b', r'\1 lettuce'),
    (r'\b(?:frozen\s+)?(broccoli|cauliflower)\s+florets?\b', r'\1 floret'),
    (r'\b(broccoli|cauliflower|asparagus|zucchini|cucumber|celery|carrot)\b', r'\1'),
    (r'\b(?:baby\s*)?arugulas?\b', 'arugula'),
    (r'\b(?:shredded|sliced|chopped|finely|thinly|grated)?\s*(?:green|red|napa|savoy|purple|white|chinese)\s+cabbages?\b', 'cabbage'),
    (r'\bcabbages?\b', 'cabbage'),
    (r'\b(leek)s?\b', 'leek'),
    (r'\b(?:(?:chopped|pitted|sliced|drained|stuffed|garlic[- ]?stuffed)\s+)*(?:(?:green|black|kalamata|spanish|ripe|pimento)\s+)*olives?\b(?:\s*\([^)]*\))?(?:\s+in\s+brine)?(?:\s+with\s+pimento)?(?! oil\b)', 'olive'),

    # mustard, buns, chips, breadcrumbs
    (r'\b(?:dijon|stoneground|stone[- ]ground|prepared|yellow|brown|whole[- ]grain|hot|spicy)\s+mustard\b', 'mustard'),
    (r'\bprepared\s+\w+\s+mustard\b', 'mustard'),
    (r'\b(?:hamburger|burger|hot dog|hotdog|sesame)\s+buns?\b', 'hamburger bun'),
    (r'\bveggie\s+burger\b', 'veggie burger'),
    (r'\b(?:baked|blue|white|red|yellow|corn|flour)\s+tortilla\s+chips?\b', 'tortilla chip'),
    (r'\btortilla\s+chips?\b', 'tortilla chip'),
    (r'\b(?:plain|dry|italian|panko|seasoned|fine|soft|fresh)\s+breadcrumbs?\b', 'breadcrumb'),
    (r'\bbreadcrumbs?\b', 'breadcrumb'),

    # herbs
    (r'\b(?:mexican|italian|greek|dried|fresh|chopped|minced)\s+(oregano|basil|parsley|cilantro|thyme|rosemary|dill|mint|sage)\b', r'\1'),

    # fruits
    (r'\b(lemon|lime)\s+wedges?\b', r'\1'),
    (r'\b(lemon|lime)\s+slices?\b', r'\1'),
    (r'\b(lemon|lime|orange|grapefruit|clementine|tangerine)\s*,?\s*(?:juice|zest)\s+of\b', r'\1'),
    (r'\b(lemon|lime|orange|grapefruit)\s+juice\b', r'\1'),
    (r'\b(lemon|lime|orange|grapefruit|clementine|tangerine)\b', r'\1'),
    (r'\b(strawberry|blueberry|raspberry|blackberry|cranberry)\s*berries?\b', r'\1'),

    # broth, stock
    (r'\b(?:hot|warm|cold|boiling)\s+(chicken|beef|vegetable|fish|bone)\s+(?:broth|stock)\b', r'\1 stock'),
    (r'\b(chicken|beef|vegetable|fish|bone)\s+broth\b', r'\1 stock'),
    (r'\b(chicken|beef|vegetable|fish|bone)\s+stock\b', r'\1 stock'),

    # meat
    (r'\b(?:(?:boneless|skinless|fresh|frozen|organic|cooked|raw|chopped|sliced|diced)\s+)*chicken(?:\s+(?:breast|thigh))?s?\b(?!\s+(?:broth|stock)\b)', 'chicken'),
    (r'\b(lean|extra|lean|organic|grass-fed|fresh|frozen|cooked|raw)?\s*(ground|minced)?\s*beef\b', 'beef'),
    (r'\b(beef|ribeye|sirloin|tenderloin)\s*steak\b', 'beef'),
    (r'\b(lean|extra-lean|fresh|frozen|cooked)?\s*(ground|minced)\s*(turkey|pork|lamb|chicken)\b', r'\3'),
    (r'\b(fresh|frozen|organic|boneless)?\s*(pork|boston)\s*shoulder\b', 'pork'),
    (r'\b(center-cut|bone-in|boneless|thick-cut|thin-cut)?\s*pork\s*chop\b', 'pork'),
    (r'\b(fresh|frozen|organic|grass-fed)?\s*(ground|leg|leg[- ]?of|chop)?\s*lamb\b', 'lamb'),

    # seafood
    (r'\b(?:fresh|frozen|raw|cooked|grilled|baked|smoked|white|firm|mild)?\s*fish\s+(?:fillet|steak|filet)s?\b', 'fish'),
    (r'\b(?:white|oily|saltwater|freshwater)\s+fish\b', 'fish'),
    (r'\b(salmon|tuna|halibut|cod|tilapia|trout|mackerel|sardine|anchovy)\s*(?:fillet|steak|filet)?\b', r'\1'),
    (r'\b(shrimp|prawn)s?\b', 'shrimp'),
    (r'\b(crab|lobster|scallop|mussel|clam|oyster)s?\b', r'\1'),    # make singular

    # sugar
    (r'\b(light|dark|golden|demerara|turbinado|muscovado)\s+brown\s+sugar\b', 'brown sugar'),
    (r'\b(white|refined|granulated|table|caster|superfine)\s+sugar\b', 'sugar'),
    (r'\b(powdered)\s+sugar\b', 'powdered sugar'),

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
    (r'\b(brown|basmati|jasmine|arborio|calrose)\s+rice\b', r'\1 rice'),
    (r'\bwhite\s+rice\b', 'rice'),

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
    (r'\b(?:red wine|white wine|apple cider|balsamic|rice wine|cider|distilled white|white|red wine|champagne)\s+vinegar\b', 'vinegar'),
    (r'\bvinegar\b', 'vinegar'),
    (r'\b(?:prepared\s+)?mayonnaise\b', 'mayonnaise'),
    (r'\bmayo\b', 'mayonnaise'),
    (r'\bsoy\s+sauce\b', 'soy sauce'),
    (r'\bketchup\b', 'ketchup'),
    (r'\bcornstarch\b', 'cornstarch'),
    (r'\b(?:prepared\s+)?horseradish\b', 'horseradish'),
    (r'\b(?:fresh|homemade|prepared|store[- ]?bought)?\s*guacamole\b', 'guacamole'),
    (r'\b(?:fresh|homemade|prepared)?\s*pico de gallo\b', 'pico de gallo'),
    (r'\b(?:table|sea|himalayan|pink|kosher)\s*salt\b', 'salt'),
    (r'\b(garlic|onion|ginger|chili|celery|mustard|paprika|onion)\s+powder\b', r'\1 powder'),
    (r'\b(red|green|black|white)\s*pepper\b', r'\1 pepper'),
    (r'\b(oregano|thyme|rosemary|basil|parsley|cilantro|dill|mint|sage)\s*(?:leaves?|leaf)\b', r'\1'),
    (r'\bcilantroleaf\b', 'cilantro'),
    (r'\bbay\s+leaves?\b', 'bay leaf'),
    (r'\b(dried|fresh|ground|whole)\s+(\w+)\b', r'\2'),
]


food_types = {
    # vegetables
    "onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sweet onion": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "yellow potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sweet potato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "garlic": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "roma tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cherry tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "grape tomato": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "stewed tomatoes": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green bell pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "jalapeno": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "jalapeno pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "habanero": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "habanero pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "serrano": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "serrano pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "poblano": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "poblano pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "anaheim pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "thai pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cayenne pepper": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cayenne": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "romaine lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "iceberg lettuce": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "spinach": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "kale": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "broccoli": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cauliflower": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "broccoli floret": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cauliflower floret": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
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
    "chickpea": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "corn": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mushroom": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "arugula": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "baby arugula": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "leek": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "avocado": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "oregano": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "thyme": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "rosemary": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "basil": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "parsley": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "chives": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cilantro": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "coriander": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cabbage": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "guacamole": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "pico de gallo": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "dill": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mint": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sage": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "olive": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "green olive": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "black olive": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "kalamata olive": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},

    # fruits
    "lime": {"type": "fruit", "vegan": True, "vegetarian": True, "gluten_free": True},
    "lemon": {"type": "fruit", "vegan": True, "vegetarian": True, "gluten_free": True},
    "orange": {"type": "fruit", "vegan": True, "vegetarian": True, "gluten_free": True},
    "grapefruit": {"type": "fruit", "vegan": True, "vegetarian": True, "gluten_free": True},
    
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
    "cod": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "halibut": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "tilapia": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "trout": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "mackerel": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "sardine": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "anchovy": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "duck egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "quail egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "ostrich egg": {"type": "protein", "vegan": False, "vegetarian": True, "gluten_free": True},
    "tofu": {"type": "protein", "vegan": True, "vegetarian": True, "gluten_free": True},
    "veggie burger": {"type": "protein", "vegan": True, "vegetarian": True, "gluten_free": False},
    "chicken stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "beef stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "fish stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "bone stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "turkey stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "pork stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "lamb stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "meat stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    "seafood stock": {"type": "protein", "vegan": False, "vegetarian": False, "gluten_free": True},
    
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
    "monterey jack cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "pepper jack cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "ricotta cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cottage cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cream cheese": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "greek yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "plain yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "frozen yogurt": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "soy yogurt": {"type": "dairy", "vegan": True, "vegetarian": True, "gluten_free": True},
    "coconut yogurt": {"type": "dairy", "vegan": True, "vegetarian": True, "gluten_free": True},
    "plant-based yogurt": {"type": "dairy", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sour cream": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "fat free sour cream": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "cream": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},
    "half and half": {"type": "dairy", "vegan": False, "vegetarian": True, "gluten_free": True},

    # grains
    "bread": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "hamburger bun": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "tortilla chip": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "breadcrumb": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "white bread": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "whole wheat bread": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "sourdough bread": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "white rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "brown rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "jasmine rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "basmati rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "arborio rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "calrose rice": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "quinoa": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "millet": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "buckwheat": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "amaranth": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "sorghum": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "teff": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "oats": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "barley": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "pearled barley": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "wheat": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "whole wheat": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "bulgur": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "farro": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "spelt": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "couscous": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "rye": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "cornmeal": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "polenta": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "grits": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "flour": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "whole wheat flour": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "pasta": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "macaroni": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "egg noodles": {"type": "grain", "vegan": False, "vegetarian": True, "gluten_free": False},
    "tortilla": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "flour tortilla": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": False},
    "corn tortilla": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    
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
    "cardamom": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "clove": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cloves": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "allspice": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "chili powder": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "garlic powder": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "onion powder": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mustard": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "dijon mustard": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "red pepper flakes": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "vinegar": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},
    "soy sauce": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": False},
    "cornstarch": {"type": "grain", "vegan": True, "vegetarian": True, "gluten_free": True},
    "horseradish": {"type": "vegetable", "vegan": True, "vegetarian": True, "gluten_free": True},
    "mayonnaise": {"type": "fat", "vegan": False, "vegetarian": True, "gluten_free": True},
    "peanut butter": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "almond butter": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "cashew butter": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "hazelnut butter": {"type": "fat", "vegan": True, "vegetarian": True, "gluten_free": True},
    "ketchup": {"type": "seasoning", "vegan": True, "vegetarian": True, "gluten_free": True},

    # sweeteners
    "sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "brown sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "powdered sugar": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "maple syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "agave syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "corn syrup": {"type": "sweetener", "vegan": True, "vegetarian": True, "gluten_free": True},
    "honey": {"type": "sweetener", "vegan": False, "vegetarian": True, "gluten_free": True},
}


substitute_markers = re.compile(r"\b(substitute|substitutes|imitation|mock|meatless|meat[- ]?free|plant[- ]?based|vegan|vegetarian|egg[- ]?free|eggless|dairy[- ]?free|faux|fake)\b", re.IGNORECASE)
vegan_markers = re.compile(r"\b(vegan|plant[- ]?based|dairy[- ]?free|egg[- ]?free|eggless)\b", re.IGNORECASE)
animal_allergens = frozenset({"dairy", "eggs", "fish", "shellfish"})
non_veg_markers = re.compile(r"\b(chicken|turkey|duck|goose|quail|cornish hen|beef|steak|veal|lamb|mutton|goat|venison|bison|pork|ham|bacon|sausage|prosciuttopancetta|salami|pepperoni|chorizo|fish|salmon|tuna|cod|halibut|"
                             r"trout|sardine|anchovy|herring|mackerel|shrimp|prawn|crab|lobster|scallop|clam|mussel|oyster|squid|calamari|octopus|gelatin|lard|tallow|suet|bone marrow|anchovies|anchovy paste)\b", re.IGNORECASE)
embedded_non_veg_markers = re.compile(r"(chicken|turkey|pork|beef|lamb|bacon|ham|sausage|shrimp|salmon|tuna|anchovy|gelatin)", re.IGNORECASE)
dairy_egg_markers = re.compile(r"\b(milk|cream|cheese|butter|yogurt|yoghurt|kefir|egg|eggs|egg white|egg yolk|mayonnaise|mayo|whey|casein|ghee|buttermilk|sour cream|creme fraiche|"
                               r"ricotta|mozzarella|parmesan|cheddar|feta|brie|honey|custard|ice cream|whipped cream|condensed milk|evaporated milk|half and half|half-and-half)\b", re.IGNORECASE)
gluten_markers = re.compile(r"\b(wheat|flour|bread|breadcrumb|breadcrumbs|pasta|noodle|noodles|barley|rye|seitan|couscous|bulgur|farro|spelt|cracker|crackers|tortilla(?! chips)|pita|bagel|croissant|"
                            r"pretzel|muffin|biscuit|crouton|croutons|soy sauce|teriyaki|malt|beer|all[- ]?purpose flour|self[- ]?rising flour|whole wheat)\b", re.IGNORECASE)
plant_markers = re.compile(r"\b(sugar|salt|pepper|spice|herb|oil|vinegar|cocoa|chocolate|vanilla|cinnamon|nutmeg|ginger|garlic|onion|tomato|potato|carrot|celery|lettuce|spinach|broccoli|"
                           r"bean|beans|lentil|lentils|chickpea|rice|corn|pea|peas|apple|banana|orange|lemon|lime|berry|berries|fruit|avocado|mushroom|zucchini|squash|pepper|jalapeno|"
                           r"almond|walnut|pecan|cashew|peanut|pistachio|hazelnut|olive|canola|vegetable oil|sesame oil|coconut oil|maple syrup|agave|molasses|honey substitute|"
                           r"tofu|tempeh|seitan substitute|nutritional yeast|water|broth|stock|juice|wine(?! vinegar))\b", re.IGNORECASE)

allergens = {
    # dairy
    "milk": ["dairy"], "butter": ["dairy"], "unsalted butter": ["dairy"], "salted butter": ["dairy"], 
    "cheese": ["dairy"], "cheddar cheese": ["dairy"], "mozzarella cheese": ["dairy"], "parmesan cheese": ["dairy"], "swiss cheese": ["dairy"], 
    "feta cheese": ["dairy"], "goat cheese": ["dairy"], "blue cheese": ["dairy"], "ricotta cheese": ["dairy"], "cottage cheese": ["dairy"], "cream cheese": ["dairy"], 
    "yogurt": ["dairy"], "greek yogurt": ["dairy"], "plain yogurt": ["dairy"], "frozen yogurt": ["dairy"],
    "sour cream": ["dairy"], "cream": ["dairy"],
    "half and half": ["dairy"],
    
    # eggs
    "egg": ["eggs"], "duck egg": ["eggs"], "quail egg": ["eggs"],
    "mayonnaise": ["eggs"],
    
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
    "peanut": ["peanuts"], "peanut oil": ["peanuts"], "peanut butter": ["peanuts"],
    "almond butter": ["tree nuts"], "cashew butter": ["tree nuts"],
    "hazelnut butter": ["tree nuts"],
    
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