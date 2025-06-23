from serv.services.mealService import get_user_data, format_recipes, call_meal_plan_api, get_user_inventory, generate_shopping_list_api
from flask_restx import abort
from flask import request

def generate_meal_plan(user_id):
    """Generates optimized meal plan for user"""
    preferences, inventory, recipes = get_user_data(user_id)
    if not preferences or not inventory:
        abort(404, 'Inventaire ou préférences non trouvés')
    
    inventory_dict = {k: v for k, v in inventory.__dict__.items() 
                    if not k.startswith('_')}
    preferences_dict = {k: v for k, v in preferences.__dict__.items() 
                      if not k.startswith('_')}
    
    payload = {
        "inventory": inventory_dict,
        "preferences": preferences_dict,
        "recette": format_recipes(recipes)
    }
    
    return call_meal_plan_api(payload)

def handle_shopping_list_request():
    """Validates and processes shopping list generation"""
    
    data = request.get_json()
    if not data.get('meal_plan') or not data.get('user_id'):
        abort(400, 'Champ manquant: meal_plan et user_id sont requis')
    
    inventory = get_user_inventory(data['user_id'])
    if not inventory:
        abort(404, 'Aucun inventaire trouvé pour cet utilisateur')
    
    payload = {
        'meal_plan': data['meal_plan'],
        'inventory': inventory
    }
    
    return generate_shopping_list_api(payload)