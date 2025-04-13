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

API_BASE_URL = 'http://6e8c-2a0d-e487-34f-4e34-d78-d7c-6814-8b8b.ngrok-free.app'

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
        """Obtenir une liste de courses basée sur un plan de repas"""
        try:
            # Récupérer d'abord un plan de repas
            meal_plan_response = requests.get(f'{API_BASE_URL}/meal_plan')
            meal_plan_response.raise_for_status()
            meal_plan = meal_plan_response.json()
            
            # Envoyer le plan de repas à l'endpoint shopping_list
            response = requests.post(f'{API_BASE_URL}/shopping_list', json=meal_plan)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500