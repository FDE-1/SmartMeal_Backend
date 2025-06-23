from loaders.postgres import db  
from flask_restx import abort
from models.database.user_recipe_model import UserRecipe

def get_all_user_recipes():
    """Retrieves all user recipes from database"""
    return UserRecipe.query.all()

def create_user_recipe_in_db(recipe_data):
    """Handles user recipe creation in database"""
    new_recipe = UserRecipe(
        user_id=recipe_data['user_id'],
        recipe_id=recipe_data['recipe_id'],
        personalisation=recipe_data.get('personalisation', {})
    )
    db.session.add(new_recipe)
    db.session.commit()
    return new_recipe

def get_user_recipes_by_user_id(user_id):
    """Retrieves all recipes for a specific user from database"""
    return UserRecipe.query.filter_by(user_id=user_id).all()

def get_user_recipe_by_id(user_recipes_id):
    """Retrieves a single user recipe from database"""
    return UserRecipe.query.get(user_recipes_id)

def update_user_recipe_in_db(user_recipes_id, update_data):
    """Updates user recipe in database"""
    user_recipe = UserRecipe.query.get(user_recipes_id)
    if not user_recipe:
        return None
    
    updatable_fields = ['user_id', 'recipe_id', 'personalisation']
    for field in updatable_fields:
        if field in update_data:
            setattr(user_recipe, field, update_data[field])
    
    db.session.commit()
    return user_recipe

def delete_user_recipe_from_db(user_recipes_id):
    """Handles user recipe deletion in database"""
    user_recipe = UserRecipe.query.get(user_recipes_id)
    if user_recipe:
        db.session.delete(user_recipe)
        db.session.commit()
    return bool(user_recipe)