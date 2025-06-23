from flask_restx import abort
from flask import request
from models.database.user_model import User
from services.recipeService import get_all_recipes, create_recipe_in_db, update_recipe_in_db, get_recipe_by_id, delete_recipe_from_db, get_user_recipes, like_or_create_recipe, get_liked_recipes
def list_all_recipes():
    """Formats recipes data for response"""
    recipes = get_all_recipes()
    return [{
        'recipe_id': r.recipe_id,
        'title': r.title,
        'ingredients': r.ingredients,
        'instructions': r.instructions,
        'ner': r.ner,
        'type': r.type,
        'calories': r.calories,
        'nutriments': r.nutriments,
        'day': r.day,
        'link': r.link,
        'source': r.source,
        'user_id': r.user_id
    } for r in recipes]

def validate_recipe_data():
    """Validates recipe creation data"""
    data = request.get_json()
    if not data:
        abort(400, 'No input data provided')
    
    required_fields = ['title', 'ingredients', 'instructions', 'ner', 'user_id']
    missing = [field for field in required_fields if field not in data]
    if missing:
        abort(400, {
            'message': 'Missing required fields',
            'missing_fields': missing
        })
    
    if 'day' in data and data['day'] not in [
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]:
        abort(400, 'Invalid day value')

def handle_recipe_creation():
    """Processes recipe creation"""
    data = request.get_json()
    validate_recipe_data(data)
    try:
        new_recipe = create_recipe_in_db(data)
        return {
            'message': 'Recipe created successfully',
            'recipe_id': new_recipe.recipe_id,
            'title': new_recipe.title
        }
    except Exception as e:
        abort(500, 'Failed to create recipe')

def validate_day(day):
    """Validates day value"""
    if day and day not in ['Monday', 'Tuesday', 'Wednesday', 
                         'Thursday', 'Friday', 'Saturday', 'Sunday']:
        abort(400, 'Invalid day value')

def get_recipe_details(recipe_id):
    """Formats recipe data for response"""
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        abort(404, 'Recipe not found')
    
    return {
        'recipe_id': recipe.recipe_id,
        'title': recipe.title,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'ner': recipe.ner,
        'type': recipe.type,
        'calories': recipe.calories,
        'nutriments': recipe.nutriments or {},
        'day': recipe.day,
        'link': recipe.link,
        'source': recipe.source,
        'user_id': recipe.user_id
    }

def handle_recipe_update(recipe_id):
    """Processes recipe updates"""
    data = request.get_json()
    if 'day' in data:
        validate_day(data['day'])
    
    updated_recipe = update_recipe_in_db(recipe_id, data)
    if not updated_recipe:
        abort(404, 'Recipe not found')
    
    return {
        'message': 'Recipe updated successfully',
        'recipe_id': updated_recipe.recipe_id
    }

def handle_recipe_deletion(recipe_id):
    """Handles recipe deletion"""
    if not delete_recipe_from_db(recipe_id):
        abort(404, 'Recipe not found')
    return {'message': 'Recipe deleted successfully'}

def get_user_recipes_data(user_id):
    """Formats user recipes data for response"""
    recipes = get_user_recipes(user_id)
    if recipes is None:
        abort(404, 'User not found')
    
    return [{
        'recipe_id': r.recipe_id,
        'title': r.title,
        'ingredients': r.ingredients,
        'instructions': r.instructions,
        'ner': r.ner,
        'type': r.type,
        'calories': r.calories,
        'nutriments': r.nutriments or {},
        'day': r.day,
        'link': r.link,
        'source': r.source,
        'user_id': r.user_id
    } for r in recipes]

def process_bulk_like():
    """Processes bulk like operation"""
    data = request.get_json()
    if not data or 'user_id' not in data or 'recipes' not in data:
        abort(400, 'Invalid input data')
    
    user_id = data['user_id']
    if not User.query.get(user_id):
        abort(404, 'User not found')
    
    results = []
    for recipe_data in data['recipes']:
        is_valid, error = validate_recipe_data(recipe_data)
        if not is_valid:
            results.append({
                'title': recipe_data.get('title', 'Unknown'),
                'status': 'failed',
                'message': error
            })
            continue
        
        try:
            result = like_or_create_recipe(recipe_data, user_id)
            results.append({
                'title': result['recipe'].title,
                'recipe_id': result['recipe'].recipe_id,
                'status': result['status'],
                'message': f'Recipe {result["status"]} and user ID added to list_like_id'
            })
        except Exception as e:
            results.append({
                'title': recipe_data.get('title', 'Unknown'),
                'status': 'failed',
                'message': str(e)
            })
    
    return {
        'message': 'Bulk like operation completed',
        'results': results
    }

def format_liked_recipes(liked_recipes):
    """Formats liked recipes data for response"""
    return [{
        'recipe_id': recipe[0],
        'title': recipe[1],
        'user_id': recipe[2],
        'list_like_id': recipe[3],
        'ingredients': recipe[4],
        'instructions': recipe[5],
        'ner': recipe[6],
        'type': recipe[7],
        'calories': recipe[8],
        'nutriments': recipe[9]
    } for recipe in liked_recipes]

def handle_liked_recipes_request(user_id):
    """Validates and processes liked recipes request"""
    if not user_id or not str(user_id).isdigit():
        abort(400, 'Invalid user_id')
    
    user = User.query.get(user_id)
    if not user:
        abort(404, 'User not found')
    
    liked_recipes = get_liked_recipes(user_id)
    if not liked_recipes:
        return {'message': 'No liked recipes found'}, 200
    
    return {
        'message': 'Liked recipes retrieved',
        'recipes': format_liked_recipes(liked_recipes)
    }