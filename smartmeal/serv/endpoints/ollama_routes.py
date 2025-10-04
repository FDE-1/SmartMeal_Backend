import json
import requests
from flask import Flask, jsonify, request
from flask_restx import Namespace, Resource, Api, fields
from ..models.recipe import Recipe
from ..models.preferences import Preferences
from ..models.inventory import Inventory
from ..models.user_recipe import UserRecipe
import requests
import re
import os
from openai import OpenAI
api = Namespace('Ollama', description='Api ia request')
BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv('api_ia_key')
MODEL = "openai/gpt-4o"

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
    'diet': fields.Raw(required=False),
    'goal': fields.String(required=True),
    'new': fields.Integer(required=True),
    'number_of_meals': fields.Integer(required=True),
    'grocery_day': fields.String(required=True),
    'language': fields.String(required=True),
})

@api.route('/single_meal')
class SingleMeal(Resource):
    @api.expect(preferences_model, validate=True)
    @api.doc('generate_single_meal')
    def post(self):
        """Génère un seul repas (recette) basé sur les préférences fournies, en interrogeant Mistral sur Ollama"""
        try:
            if not request.is_json:
                return {'error': 'Le corps de la requête doit être au format JSON'}, 400
            
            preferences = request.get_json()
            if not preferences:
                return {'error': 'Aucune préférence fournie'}, 400

            # Valider les champs minimaux
            required_fields = ["allergy", "goal", "number_of_meals", "grocery_day"]
            for field in required_fields:
                if field not in preferences:
                    return {'error': f'Champ de préférence manquant: {field}'}, 400

            # Construire un prompt pour Mistral
            prompt = self.build_prompt(preferences)

            # Interroger Ollama via Ngrok
            ollama_response = self.query_openrouter(prompt)
            if 'error' in ollama_response:
                return ollama_response, 500

            # Parser la réponse de Mistral en format JSON
            meal_plan = self.parse_response(ollama_response)
            return meal_plan

        except requests.exceptions.HTTPError as e:
            return {'error': f'Erreur lors de l\'appel à Ollama: {str(e)}'}, 500
        except ValueError as e:
            return {'error': f'JSON invalide dans la réponse: {str(e)}'}, 400
        except Exception as e:
            return {'error': f'Erreur interne: {str(e)}'}, 500

    def build_prompt(self, preferences):
        """Construit un prompt pour Mistral basé sur les préférences"""
        allergy_list = [k for k, v in preferences['allergy'].items() if v]
        allergies_str = ", ".join(allergy_list) if allergy_list else "aucune"

        prompt = f"""
        Génère une seule recette de repas qui respecte ces préférences :
        - Régime : {preferences['diet'] if preferences['diet'] else 'aucun'}
        - Objectif : {preferences['goal'] if preferences['goal'] else 'aucun'}
        - Allergies : {allergies_str}
        - Nombre de repas par jour (indicatif) : {preferences['number_of_meals']}
        - Jour des courses (indicatif) : {preferences['grocery_day']}
        - Langue : {preferences['language']}

        La recette doit être saine, simple à préparer, et inclure :
        - Un titre (dans 'items')
        - Calories totales
        - Nutriments (lipide, glucide, proteine, fibre)
        - Liste des ingrédients (NER pour ingrédients normalisés, ingredients pour liste complète avec quantités)
        - Instructions de préparation
        - Type de plat
        - Temps de préparation (en minutes)
        - Portions (servings)

        Retourne UNIQUEMENT un JSON au format suivant (pas de texte supplémentaire) :
        {{
            "Meal": [
                {{
                    "items": ["Titre de la recette"],
                    "calories": 500,
                    "nutriments": {{
                        "lipide": 20.0,
                        "glucide": 50.0,
                        "proteine": 30.0,
                        "fibre": 10.0
                    }},
                    "ingredients": ["1 tasse de quinoa", "1 tomate", "..."],
                    "preparation": "Étapes de préparation...",
                    "NER": ["quinoa", "tomate"],
                    "type": "Déjeuner",
                    "time": 30,
                    "servings": 2
                }}
            ]
        }}
        """
        return prompt

    def query_openrouter(self, prompt):
        """Interroge l'API OpenRouter (compatible ChatGPT) inspiré du code fourni"""
        try:
            client = OpenAI(
                base_url=BASE_URL,
                api_key=API_KEY,
            )

            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            response = completion.choices[0].message.content
            
            return response
        except Exception as e:
            return {'error': f'Erreur lors de l\'appel à OpenRouter: {str(e)}'}
        
    def parse_response(self, response_text):
        """Parse la réponse texte de ChatGPT en JSON structuré"""
        try:
            # Supprimer tout texte avant ou après le JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("Aucun JSON valide trouvé dans la réponse")
            
            meal_plan = json.loads(json_match.group(0))
            
            # Valider le format
            if "Meal" not in meal_plan or not isinstance(meal_plan["Meal"], list) or len(meal_plan["Meal"]) == 0:
                raise ValueError("Format de meal_plan invalide")
            
            return meal_plan
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur de parsing JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing: {str(e)}")