from serv.models.database.inventory_model import Inventory
from serv.models.database.preference_model import Preferences
from serv.models.database.recipe_model import Recipe
import requests

API_BASE_URL = 'http://c58c-2a01-e0a-ee7-db30-f895-736c-3a4c-218c.ngrok-free.app'

def get_user_data(user_id):
    """Retrieves user preferences, inventory and recipes"""
    preferences = Preferences.query.filter_by(user_id=user_id).first()
    inventory = Inventory.query.filter_by(user_id=user_id).first()
    recipes = Recipe.query.filter_by(user_id=user_id).all()
    
    if not preferences or not inventory:
        return None, None, None
    
    return preferences, inventory, recipes

def format_recipes(recipes):
    """Formats user recipes into weekly structure"""
    weekly_recipes = {day: [] for day in [
        "Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday", "Sunday"
    ]}
    
    for recipe in recipes:
        if recipe.day and recipe.day in weekly_recipes:
            weekly_recipes[recipe.day].append({
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "directions": recipe.instructions,
                "link": recipe.link,
                "source": recipe.source,
                "NER": recipe.ner,
                "calories": recipe.calories,
                "type": recipe.type,
                "nutriments": recipe.nutriments or {}
            })
    return weekly_recipes

def call_meal_plan_api(payload):
    """Makes API call to meal planning service"""
    response = requests.post(f'{API_BASE_URL}/optimized_preferences_meal_plan', json=payload)
    response.raise_for_status()
    return response.json()

def get_user_inventory(user_id):
    """Retrieves user inventory from database"""
    inventory = Inventory.query.filter_by(user_id=user_id).first()
    if not inventory:
        return None
    
    inventory_dict = inventory.to_dict() if hasattr(inventory, 'to_dict') else inventory.__dict__
    inventory_dict.pop('_sa_instance_state', None)
    return inventory_dict

def generate_shopping_list_api(payload):
    """Calls external API to generate shopping list"""
    response = requests.post(f'{API_BASE_URL}/shopping_list', json=payload)
    response.raise_for_status()
    return response.json()