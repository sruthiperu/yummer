from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import JSONB


# each model needs Base (database), Column (database columns), data types, 
# relationship imports (to connect to other tables)

# recipe table
class Recipe(Base):
    __tablename__ = "recipes"       # which database table this maps to

    id = Column(Integer, primary_key=True)      # recipe id
            
    # columns
    title = Column(String, nullable=False)          # required
    instructions = Column(JSONB, nullable=False)    # required
    description = Column(String, nullable=True)
    servings = Column(Integer, nullable=True)
    total_time = Column(Integer, nullable=True)             # sort: newest --> oldest
    # prep_time = Column(Integer, nullable=True)
    # cook_time = Column(Integer, nullable=True)            # "make this more low-effort" --> AI modifies prep efforts
    nutrition = Column(JSONB, nullable=True)
    recipe_link = Column(String, nullable=True)             # create link from 'Recipe name' + 'Recipe ID'
    image = Column(String, nullable=True)                   # extract from recipe_link source
    date_submitted = Column(DateTime, nullable=True)


# ingredient table
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)       # required
    aliases = Column(ARRAY(String), nullable=True)
    food_type = Column(String, nullable=True)           # dairy, meet, etc.
    allergens = Column(ARRAY(String), nullable=True)    # common allergens
    is_vegan = Column(Boolean, nullable=True)
    is_vegetarian = Column(Boolean, nullable=True)
    is_gluten_free = Column(Boolean, nullable=True)


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
