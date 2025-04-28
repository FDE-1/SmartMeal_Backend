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

@api.route('/fake_meal_plan')
class FakeWeeklyMealPlan(Resource):
    @api.doc('fake_meal_plan')
    def get(self):
        """Obtenir un plan de repas hebdomadaire depuis l'API"""
        try:
            #response = requests.get(f'{API_BASE_URL}/meal_plan')
            #response.raise_for_status()  # Vérifie les erreurs HTTP
            response = {
    "Friday": [
        {
            "calories": 576,
            "ingredients": [
                "226 g de gros haricots blancs séchés, comme les haricots corona",
                "3 feuilles de laurier",
                "3 gousses d'ail",
                "farine tout usage",
                "sel casher et poivre noir fraîchement moulu",
                "60 ml d'huile d'olive extra vierge",
                "113 g de pancetta en tranches fines",
                "6 feuilles de sauge fraîches"
            ],
            "items": [
                "Haricots blancs avec pancetta"
            ],
            "servings": 1,
            "time": 29
        }
    ],
    "Monday": [
        {
            "calories": 737,
            "ingredients": [
                "huile de tournesol",
                "567 g de crevettes grandes ou jumbo, pelées et déveinées",
                "sel et poivre noir fraîchement moulu",
                "10 ml de cumin moulu",
                "4 rondelles d'ananas, environ 2,54 cm d'épaisseur",
                "8 tortillas de farine",
                "120 ml de fromage râpé",
                "80 ml de poivrons rouges rôtis, hachés",
                "60 ml d'oignons verts, hachés",
                "120 ml de crème sure légère",
                "10 ml de zeste de citron vert finement râpé",
                "10 ml de poudre d'ail",
                "1 mangue, pelée et coupée",
                "15 ml de jus de citron vert frais",
                "15 ml de coriandre fraîche, hachée"
            ],
            "items": [
                "Quesadillas"
            ],
            "servings": 4,
            "time": 38
        }
    ],
    "Saturday": [
        {
            "calories": 677,
            "ingredients": [
                "2 aubergines",
                "sel",
                "huile d'olive extra vierge, pour badigeonner",
                "5 ml de feuilles de thym frais, finement hachées",
                "poivre noir fraîchement moulu",
                "454 g de pâte à pizza préparée",
                "180 ml de sauce tomate",
                "1 petit tas de feuilles d'origan frais",
                "227 g de mozzarella, tranchée",
                "45 ml de parmesan fraîchement râpé",
                "marjolaine, pour saupoudrer"
            ],
            "items": [
                "Focaccia farcie avec aubergine rôtie et origan"
            ],
            "servings": 1,
            "time": 28
        }
    ],
    "Thursday": [
        {
            "calories": 264,
            "ingredients": [
                "120 ml de feuilles de basilic frais",
                "120 ml de feuilles de coriandre fraîche",
                "180 ml de lait de coco",
                "30 ml de sauce de poisson",
                "30 ml de sauce soja",
                "2,5 ml de coriandre moulue",
                "2,5 ml de cumin moulu",
                "2,5 ml de sucre brut",
                "4 gousses d'ail",
                "1 piment thaï vert",
                "un morceau de 2,54 cm de gingembre frais, pelé",
                "1 tige de citronnelle, couches extérieures dures retirées, tranchée",
                "1 échalote, coupée en deux",
                "poivre noir fraîchement concassé",
                "30 ml d'huile de canola",
                "960 ml de bouillon de poulet biologique ou de légumes",
                "1 poivron jaune, épépiné et coupé en dés",
                "1 aubergine chinoise, en dés",
                "454 g de nouilles udon de sarrasin",
                "sel"
            ],
            "items": [
                "Nouilles udon dodues dans le curry vert thaïlandais avec aubergine"
            ],
            "servings": 4,
            "time": 16
        }
    ],
    "Tuesday": [
        {
            "calories": 339,
            "ingredients": [
                "1 épaule de porc (2722 à 3629 g)",
                "sel",
                "360 ml de vinaigre de cidre",
                "150 ml de ketchup",
                "2,5 ml de poivre de Cayenne",
                "5 ml de poivre noir",
                "15 ml de sucre",
                "120 ml d'eau"
            ],
            "items": [
                "Épaule de porc effilochée"
            ],
            "servings": 3,
            "time": 55
        }
    ],
    "Wednesday": [
        {
            "calories": 709,
            "ingredients": [
                "170 g de saumon en conserve, égoutté et arêtes enlevées",
                "120 ml de poivron rouge en dés",
                "80 ml de céleri en dés",
                "45 ml d'oignon vert tranché à 0,32 cm",
                "45 ml de yaourt grec",
                "30 ml de jus de citron",
                "1,25 ml de sel",
                "454 g de concombres persans"
            ],
            "items": [
                "Salade de saumon de concombre"
            ],
            "servings": 2,
            "time": 24
        }
    ]
} 
            return response.json()
        except requests.RequestException as e:
            return {'error': f'Erreur lors de l\'appel à l\'API: {str(e)}'}, 500