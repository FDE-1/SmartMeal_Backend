from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from ..connection.loader import db
from ..models.recipe import Recipe
import requests
import json
import re

api = Namespace('weekly_meals', description='Weekly meal operations')

# Modèle de réponse attendu pour chaque repas
meal_model = api.model('Meal', {
    'items': fields.List(fields.String, required=True, description='List of food items'),
    'calories': fields.Integer(required=True, description='Total calories'),
    'servings': fields.Integer(required=True, description='Number of servings'),
    'time': fields.Integer(required=True, description='Preparation time in minutes')
})

# Fonction pour appeler Ollama avec le modèle deepseek-r1
def get_meal_plan_from_ollama():
    url = "http://aff9-2a0d-e487-145f-67f3-1c50-b39c-ef51-20a1.ngrok-free.app/api/generate"
    prompt = """
    Génère un plan de repas pour une semaine (Lundi à Samedi) pour une personne. 
    Pour chaque jour, propose 1 à 2 repas avec une liste d'items (plats ou aliments), 
    le total de calories, le nombre de portions et le temps de préparation en minutes. 
    Retourne le résultat EXCLUSIVEMENT au format JSON valide, sans texte supplémentaire, 
    avec les jours et les plats en français (Lundi, Mardi, etc.). Exemple attendu :
    {
        "Lundi": [{"items": ["Steak frites"], "calories": 300, "servings": 3, "time": 50}],
        "Mardi": [{"items": ["Pâtes bolo"], "calories": 350, "servings": 2, "time": 40}]
    }
    """
    data = {
        "model": "deepseek-r1",
        "prompt": prompt,
        "stream": False
    }
    default_plan = {
        "Lundi": [{"items": ["Steak frites"], "calories": 300, "servings": 3, "time": 50}],
        "Mardi": [{"items": ["Pâtes bolo"], "calories": 350, "servings": 2, "time": 40}]
    }

    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()["response"]
        print("Réponse brute d'Ollama :", result)

        # Extraire la partie JSON avec une expression régulière
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)  # Récupère uniquement le contenu entre ```json et ```
            print("JSON extrait :", json_str)
            meal_plan = json.loads(json_str)
        else:
            print("Erreur : Aucun JSON trouvé dans la réponse")
            return default_plan

        return meal_plan

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à Ollama : {e}")
        return default_plan
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON : {e} - Réponse reçue : {result}")
        return default_plan
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return default_plan

@api.route('/')
class WeeklyMealPlan(Resource):
    @api.doc('get_weekly_meal_plan')
    def get(self):
        """Get a weekly meal plan for a person"""
        meal_plan = get_meal_plan_from_ollama()
        return jsonify(meal_plan)

# Exemple d'intégration avec la base de données (optionnel)
@api.route('/from-db')
class WeeklyMealPlanFromDB(Resource):
    @api.doc('get_weekly_meal_plan_from_db')
    def get(self):
        """Get a weekly meal plan based on recipes in the database"""
        recipes = Recipe.query.all()
        if not recipes:
            return {'message': 'No recipes found in the database'}, 404
        
        # Exemple simple : utilise les recettes existantes pour remplir un plan
        sample_plan = {
            "Lundi": [{"items": [recipes[0].recipe_name], "calories": 300, "servings": 1, "time": recipes[0].recipe_preparation_time}],
            "Mardi": [{"items": [recipes[1 % len(recipes)].recipe_name], "calories": 350, "servings": 2, "time": recipes[1 % len(recipes)].recipe_preparation_time}],
            "Mercredi": [{"items": [recipes[2 % len(recipes)].recipe_name], "calories": 400, "servings": 1, "time": recipes[2 % len(recipes)].recipe_preparation_time}],
            "Jeudi": [{"items": [recipes[3 % len(recipes)].recipe_name], "calories": 450, "servings": 2, "time": recipes[3 % len(recipes)].recipe_preparation_time}],
            "Vendredi": [{"items": [recipes[4 % len(recipes)].recipe_name], "calories": 500, "servings": 1, "time": recipes[4 % len(recipes)].recipe_preparation_time}],
            "Samedi": [{"items": [recipes[5 % len(recipes)].recipe_name], "calories": 300, "servings": 3, "time": recipes[5 % len(recipes)].recipe_preparation_time}]
        }
        return jsonify(sample_plan)