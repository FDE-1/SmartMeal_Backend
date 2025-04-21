from ..connection.loader import db

class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.String, nullable=False)
    recipe_ingredients = db.Column(db.JSON)
    recipe_instructions = db.Column(db.JSON)
    recipe_preparation_time = db.Column(db.Integer)
    recipe_ustensils_required = db.Column(db.JSON)
    recipe_nutritional_value = db.Column(db.JSON)
    rating = db.Column(db.Numeric(2,1))