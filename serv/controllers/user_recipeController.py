from services.user_recipeService import get_all_user_recipes, create_user_recipe_in_db, get_user_recipes_by_user_id, get_user_recipe_by_id, update_user_recipe_in_db, delete_user_recipe_from_db
from flask_restx import abort
from flask import request

def list_all_user_recipes():
    """Formats user recipe data for response"""
    recipes = get_all_user_recipes()
    return [{
        'user_recipes_id': ur.user_recipes_id,
        'user_id': ur.user_id,
        'recipe_id': ur.recipe_id,
        'personalisation': ur.personalisation
    } for ur in recipes]

def handle_user_recipe_creation():
    """Validates and processes user recipe creation"""
    
    data = request.get_json()
    if not data:
        abort(400, 'No input data provided')
    
    required_fields = ['user_id', 'recipe_id']
    missing = [field for field in required_fields if field not in data]
    if missing:
        abort(400, {'message': 'Missing required fields', 'missing_fields': missing})
    
    try:
        new_recipe = create_user_recipe_in_db(data)
        return {
            'message': 'User recipe created successfully',
            'user_recipes_id': new_recipe.user_recipes_id
        }
    except Exception as e:
        abort(500, 'Failed to create user recipe')

def get_user_recipes_data(user_id):
    """Formats user recipes data for response"""
    recipes = get_user_recipes_by_user_id(user_id)
    return [{
        'user_recipes_id': ur.user_recipes_id,
        'recipe_id': ur.recipe_id,
        'personalisation': ur.personalisation
    } for ur in recipes]

def get_user_recipe_details(user_recipes_id):
    """Formats user recipe data for response"""
    user_recipe = get_user_recipe_by_id(user_recipes_id)
    if not user_recipe:
        abort(404, 'User recipe not found')
    
    return {
        'user_recipes_id': user_recipe.user_recipes_id,
        'user_id': user_recipe.user_id,
        'recipe_id': user_recipe.recipe_id,
        'personalisation': user_recipe.personalisation
    }

def handle_user_recipe_update(user_recipes_id):
    """Validates and processes user recipe updates"""
    data = request.get_json()
    updated_recipe = update_user_recipe_in_db(user_recipes_id, data)
    if not updated_recipe:
        abort(404, 'User recipe not found')
    
    return {'message': 'User recipe updated successfully'}

def handle_user_recipe_deletion(user_recipes_id):
    """Manages user recipe deletion process"""
    if not delete_user_recipe_from_db(user_recipes_id):
        abort(404, 'User recipe not found')
    return {'message': 'User recipe deleted successfully'}