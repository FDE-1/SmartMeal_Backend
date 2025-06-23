from models.database.recipe_model import Recipe
from models.database.user_model import User
from loaders.postgres import db  
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text

def get_all_recipes():
    """Retrieves all recipes from database"""
    return Recipe.query.all()

def create_recipe_in_db(recipe_data):
    """Creates a new recipe in database"""
    new_recipe = Recipe(
        title=recipe_data['title'],
        ingredients=recipe_data['ingredients'],
        instructions=recipe_data['instructions'],
        ner=recipe_data.get('ner', []),
        type=recipe_data.get('type', ''),
        calories=recipe_data.get('calories', 0),
        nutriments=recipe_data.get('nutriments', {}),
        day=recipe_data.get('day', ''),
        link=recipe_data.get('link', ''),
        source=recipe_data.get('source', ''),
        user_id=recipe_data['user_id']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return new_recipe

def get_recipe_by_id(recipe_id):
    """Retrieves a single recipe by ID"""
    return Recipe.query.get(recipe_id)

def update_recipe_in_db(recipe_id, update_data):
    """Updates recipe data in database"""
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return None
    
    # Update required fields
    for field in ['title', 'ingredients', 'instructions']:
        if field in update_data:
            setattr(recipe, field, update_data[field])
    
    # Update optional fields
    optional_fields = ['ner', 'type', 'calories', 'nutriments', 'day', 'link', 'source']
    for field in optional_fields:
        if field in update_data:
            setattr(recipe, field, update_data[field])
    
    db.session.commit()
    return recipe

def delete_recipe_from_db(recipe_id):
    """Deletes a recipe from database"""
    recipe = get_recipe_by_id(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
    return bool(recipe)

def get_user_recipes(user_id):
    """Retrieves all recipes for a specific user"""
    if not User.query.get(user_id):
        return None
    return Recipe.query.filter_by(user_id=user_id).all()

def validate_recipe_data(recipe_data):
    """Validates recipe data for bulk like operation"""
    required_fields = ['title', 'ingredients', 'instructions', 'ner', 'user_id']
    if not all(field in recipe_data for field in required_fields):
        missing = [field for field in required_fields if field not in recipe_data]
        return False, f'Missing required fields: {missing}'
    
    if 'day' in recipe_data and recipe_data['day'] and recipe_data['day'] not in [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]:
        return False, 'Invalid day value'
    return True, None

def like_or_create_recipe(recipe_data, user_id):
    """Handles recipe like or creation"""
    recipe = Recipe.query.filter_by(title=recipe_data['title']).first()
    
    if recipe:
        if recipe.list_like_id is None:
            recipe.list_like_id = [user_id]
        elif user_id not in recipe.list_like_id:
            current_list = recipe.list_like_id or []
            current_list.append(user_id)
            recipe.list_like_id = current_list
            flag_modified(recipe, 'list_like_id')
        db.session.commit()
        return {
            'status': 'updated',
            'recipe': recipe
        }
    else:
        new_recipe = Recipe(
            title=recipe_data['title'],
            ingredients=recipe_data['ingredients'],
            instructions=recipe_data['instructions'],
            ner=recipe_data.get('ner', []),
            type=recipe_data.get('type', ''),
            calories=recipe_data.get('calories', 0),
            nutriments=recipe_data.get('nutriments', {}),
            day=recipe_data.get('day'),
            link=recipe_data.get('link', ''),
            source=recipe_data.get('source', ''),
            user_id=recipe_data['user_id'],
            list_like_id=[user_id]
        )
        db.session.add(new_recipe)
        db.session.commit()
        return {
            'status': 'created',
            'recipe': new_recipe
        }
    
def get_liked_recipes(user_id):
    """Retrieves liked recipes for a user using raw SQL"""
    return db.session.execute(
        text("SELECT * FROM recipes WHERE list_like_id @> ARRAY[:user_id]::bigint[]"),
        {"user_id": user_id}
    ).fetchall()    