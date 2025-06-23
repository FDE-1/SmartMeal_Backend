from sqlalchemy import BIGINT
from loaders.postgres import db
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)  # Changed from recipe_name
    ingredients = db.Column(JSONB)  # Changed from recipe_ingredients
    instructions = db.Column(JSONB)  # Changed from recipe_instructions
    ner = db.Column(JSONB)
    type = db.Column(db.String(50))
    nutriments = db.Column(JSONB)  # Replaces recipe_nutritional_value
    day = db.Column(db.String(10), 
                  db.CheckConstraint("day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')"))
    link = db.Column(db.Text)
    source = db.Column(db.String(50))
    calories = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    list_like_id = db.Column(ARRAY(BIGINT))
