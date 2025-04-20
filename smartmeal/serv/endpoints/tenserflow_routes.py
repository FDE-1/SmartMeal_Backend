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

API_BASE_URL = 'http://1db8-2a01-cb0d-60e-a700-8457-9272-1c01-7bae.ngrok-free.app'

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
    @api.doc('get_furniture')
    def post(self):
        """Obtenir une liste de courses basée sur le plan de repas fourni dans le corps de la requête"""
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            meal_plan = request.get_json()
            if not meal_plan:
                return {'error': 'Aucun plan de repas fourni'}, 400
            
            # Envoyer le plan de repas fourni à l'endpoint shopping_list
            response = requests.post(f'{API_BASE_URL}/shopping_list', json=meal_plan)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide: {str(e)}'}, 400