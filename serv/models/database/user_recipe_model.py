from loaders.postgres import db
from sqlalchemy.dialects.postgresql import JSONB

class UserRecipe(db.Model):
    __tablename__ = 'user_recipes'
    
    user_recipes_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    personalisation = db.Column(JSONB, default={})