from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, ARRAY, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR


# each model needs Base (database), Column (database columns), data types, 
# relationship imports (to connect to other tables)

# recipe table
class Recipe(Base):
    __tablename__ = "recipes"       # which database table this maps to

    id = Column(Integer, primary_key=True)      # recipe id
            
    # columns
    name = Column(String, nullable=False)          # required
    description = Column(String, nullable=True)
    directions = Column(JSONB, nullable=False)     # required
    servings = Column(Integer, nullable=True)
    total_time = Column(Integer, nullable=True)             # in minutes; sort: newest --> oldest
    # prep_time = Column(Integer, nullable=True)
    # cook_time = Column(Integer, nullable=True)            # "make this more low-effort" --> AI modifies prep efforts
    nutrition = Column(JSONB, nullable=True)
    tags = Column(JSONB, nullable=True)
    date = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)                   # extract from recipe_link source
    link = Column(String, nullable=True)             

    search_vector = Column(TSVECTOR, nullable=True)


# ingredient table
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)       # required
    aliases = Column(ARRAY(String), nullable=True)
    food_type = Column(String, nullable=True)           # dairy, meat, etc
    allergens = Column(ARRAY(String), nullable=True)    # common allergens
    is_vegan = Column(Boolean, nullable=True)
    is_vegetarian = Column(Boolean, nullable=True)
    is_gluten_free = Column(Boolean, nullable=True)


# map recipe to ingredients
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True)

    # link recipes to ingredients
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(String, nullable=True)            # parsed
    unit = Column(String, nullable=True) 
    container_size = Column(String, nullable=True)      # ex. "14 oz" for "1 (14 ounce) can ..."
    raw_ingredient = Column(String, nullable=True)     # original text from recipenlg
    section_title = Column(String, nullable=True)      # null -> unnamed/default section


# user table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, nullable=False, unique=True)  
    google_id = Column(String, nullable=False, unique=True)  
    name = Column(String, nullable=False)
    dietary_restrictions = Column(JSONB, nullable=True)
    allergens = Column(JSONB, nullable=True)
    date_created = Column(DateTime, nullable=True)
