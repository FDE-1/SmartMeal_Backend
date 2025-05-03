from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from ..connection.loader import db
from ..models.recipe import Recipe
import requests
import json
import re
import threading
from functools import wraps
api = Namespace('tenserflow', description='Test TenserFlow')

API_BASE_URL = 'http://a1f5-2a01-e0a-ee7-db30-64cf-2054-8bd5-4e08.ngrok-free.app'

ingredient_model = api.model('Ingredient', {
    'name': fields.String(required=True, description='Nom de l\'ingrédient'),
    'quantity': fields.String(required=True, description='Quantité'),
    'type_quantity': fields.String(required=False, description='Type de quantité (g, L, etc.)'),
})

inventory_model = api.model('Inventory', {
    'inventory_id': fields.Integer(required=True, description='Identifiant de l\'inventaire'),
    'user_id': fields.Integer(required=True, description='Identifiant utilisateur'),
    'ustensils': fields.List(fields.Nested(ingredient_model), required=False),
    'grocery': fields.List(fields.Nested(ingredient_model), required=False),
    'fresh_produce': fields.List(fields.Nested(ingredient_model), required=False),
})

meal_model = api.model('Meal', {
    'NER': fields.List(fields.String, required=True),
    'calories': fields.Integer(required=True),
    'ingredients': fields.List(fields.String, required=True),
    'items': fields.List(fields.String, required=True),
    'servings': fields.Integer(required=True),
    'time': fields.Integer(required=True),
})

shopping_list_input = api.model('ShoppingListInput', {
    'meal_plan': fields.Raw(required=True, description='Plan de repas, mappé par jour (lundi, mardi, etc.)'),
    'inventory': fields.Nested(inventory_model, required=False),
})

allergy_model = api.model('Allergy', {
    k: fields.Boolean(required=True) for k in [
        "ail", "ogm", "riz", "sel", "blé", "kiwi", "lait", "miel", "porc", "soja", "thé", "bœuf", "cacao", "café",
        "lupin", "maïs", "pomme", "œufs", "alcool", "avocat", "banane", "fraise", "gluten", "oignon", "pêche",
        "tomate", "carotte", "céleri", "lactose", "poisson", "sésame", "fructose", "moutarde", "sulfites", "gélatine",
        "histamine", "crustacés", "mollusques", "cacahuètes", "champignons", "charcuterie", "viande rouge",
        "fruits de mer", "sucre ajouté", "aliments frits", "viande blanche", "aliments acides", "fruits à coque",
        "produits laitiers", "graisses saturées", "huiles végétales", "produits fermentés",
        "aliments transformés", "aliments riches en fodmap", "aliments riches en purines",
        "aliments ultra-transformés"
    ]
})

preferences_model = api.model('Preferences', {
    'preference_id': fields.Integer(required=True),
    'user_id': fields.Integer(required=True),
    'allergy': fields.Nested(allergy_model, required=True),
    'diet': fields.String(required=True),
    'goal': fields.String(required=True),
    'new': fields.Integer(required=True),
    'number_of_meals': fields.Integer(required=True),
    'grocery_day': fields.String(required=True),
    'language': fields.String(required=True),
})

user_data_model = api.model('UserData', {
    'inventory': fields.Nested(inventory_model, required=True),
    'preferences': fields.Nested(preferences_model, required=True),
})

@api.route('/meal_plan')
class WeeklyMealPlan(Resource):
    @api.doc('get_weekly_meal_plan')
    def get(self):
        """Obtenir un plan de repas hebdomadaire depuis l'API"""
        try:
            response = requests.get(f'{API_BASE_URL}/meal_plan')
            response.raise_for_status()  # Vérifie les erreurs HTTP
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        
@api.route('/furniture')
class ShoppingList(Resource):
    @api.expect(shopping_list_input, validate=True)
    @api.doc('get_shopping_list')
    def post(self):
        """Obtenir une liste de courses basée sur le plan de repas et l'inventaire fournis dans le corps de la requête"""
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            data = request.get_json()
            if not data or 'meal_plan' not in data:
                return {'error': 'Aucun plan de repas fourni'}, 400
            
            # Préparer les données à envoyer : meal_plan et inventory (si présent)
            payload = {
                'meal_plan': data['meal_plan'],
                'inventory': data.get('inventory', {})
            }
            
            # Envoyer les données à l'endpoint shopping_list
            response = requests.post(f'{API_BASE_URL}/shopping_list', json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide: {str(e)}'}, 400
                
@api.route('/custom_meal_plan')
class MealPlanPref(Resource):
    @api.doc('get_furniture')
    def post(self):
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            meal_plan = request.get_json()
            if not meal_plan:
                return {'error': 'Aucun plan de repas fourni'}, 400
            
            # Envoyer le plan de repas fourni à l'endpoint shopping_list
            response = requests.post(f'{API_BASE_URL}/custom_meal_plan', json=meal_plan)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide: {str(e)}'}, 400

        
@api.route('/stock_meal_plan')
class OptimizedMealPlan(Resource):
    @api.doc('get_optimized_meal_plan')
    def post(self):
        """Obtenir un plan de repas optimisé basé sur l'inventaire fourni dans le corps de la requête"""
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            inventory_data = request.get_json()
            if not inventory_data:
                return {'error': 'Aucun inventaire fourni'}, 400
            
            # Envoyer les données d'inventaire à l'endpoint optimized_meal_plan
            response = requests.post(f'{API_BASE_URL}/optimized_meal_plan', json=inventory_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide: {str(e)}'}, 400

@api.route('/stock_preferences_meal_plan')
class OptimizedPreferencesMealPlan(Resource):
    @api.expect(user_data_model)
    @api.doc('get_optimized_preferences_meal_plan')
    def post(self):
        """Obtenir un plan de repas optimisé basé sur l'inventaire et les préférences utilisateur fournies dans le corps de la requête"""
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            inventory_data = request.get_json()
            if not inventory_data:
                return {'error': 'Aucun inventaire fourni'}, 400
            
            # Envoyer les données d'inventaire à l'endpoint optimized_preferences_meal_plan
            response = requests.post(f'{API_BASE_URL}/optimized_preferences_meal_plan', json=inventory_data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print("❌ HTTPError status:", e.response.status_code)
            print("❌ HTTPError body:", e.response.text)
            return {'error': f'Erreur HTTP de l\'API: {e.response.text}'}, e.response.status_code
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide: {str(e)}'}, 400