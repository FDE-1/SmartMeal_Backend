import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from ..connection.loader import db
from ..models.recipe import Recipe
import requests
import json
import re
import threading
from functools import wraps
from datetime import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
import random
api = Namespace('tenserflow', description='Test TenserFlow')

# Charger les données sauvegardées
try:
    df = pd.read_pickle("recipes_df.pkl")
    with open("label_encoder.pkl", "rb") as f:
        encoder = pickle.load(f)
    model = tf.keras.models.load_model("meal_plan_model.keras")
    print("Modèle et données chargés avec succès")
except FileNotFoundError as e:
    print(f"Erreur : Fichier manquant - {e}")
    exit(1)


# Fonction pour générer un plan de repas
def generate_meal_plan():
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    meal_plan = {}
    
    for day in days:
        num_meals = random.randint(1, 2)
        meals = []
        used_titles = set()  # Éviter les doublons dans un même jour
        for _ in range(num_meals):
            type_plat = random.choice(["entrée", "plat principal", "dessert"])
            # Filtrer les recettes par type de plat
            recettes_type = df[df["type_plat"] == type_plat]
            if recettes_type.empty:
                continue
            # Sélectionner une recette aléatoire parmi celles du type
            recette = recettes_type.sample(n=1).iloc[0]
            if recette["title"] in used_titles:
                continue  # Éviter les doublons
            used_titles.add(recette["title"])
            
            meals.append({
                "items": [recette["title"] or "Plat sans titre"],
                "calories": int(recette["calories"]),
                "servings": int(recette["servings"]),
                "time": int(recette["time"])
            })
        meal_plan[day] = meals
    
    return meal_plan

def generate_shopping_list(meal_plan):
    ingredients_set = {}
    
    def parse_quantity(qty_str):
        try:
            qty_str = qty_str.replace("g", "").replace("ml", "").replace("unités", "").strip()
            if "/" in qty_str:
                num, denom = qty_str.split("/")
                return float(num.strip()) / float(denom.strip())
            return float(qty_str)
        except (ValueError, ZeroDivisionError):
            return 100.0
    
    for day, meals in meal_plan.items():
        for meal in meals:
            title = meal["items"][0]
            recette = df[df["title"] == title]
            if not recette.empty:
                ingredients = recette.iloc[0]["ingredients"]
                for ingredient in ingredients:
                    parts = ingredient.split(",")[0].split()
                    quantity = next((p for p in parts if any(c.isdigit() for c in p) or "/" in p), "100")
                    unit = next((p for p in parts if p in ["g", "ml", "unités"]), "g")
                    name = " ".join(p for p in parts if p != quantity and p != unit)
                    key = name.strip()
                    
                    if key in ingredients_set:
                        current_qty = parse_quantity(ingredients_set[key])
                        new_qty = parse_quantity(quantity)
                        ingredients_set[key] = f"{current_qty + new_qty}{unit}"
                    else:
                        ingredients_set[key] = f"{quantity}{unit}"
    
    return ingredients_set

the_meal_plan = generate_meal_plan()

@api.route('/meal_plan')
class WeeklyMealPlan(Resource):
    @api.doc('get_weekly_meal_plan')
    @async_llm_call
    def get(self):
        """Get a weekly meal plan (async)"""
        the_meal_plan = generate_meal_plan()
        return the_meal_plan
@api.route('/furniture')
class ShoppingList(Resource):
    @api.doc('get_furniture')
    @async_llm_call
    def get(self):
        """Get a shopping list based on the weekly meal plan (async)"""
        #meal_plan = get_meal_plan_from_ollama()  # Récupère le plan de repas
        return generate_shopping_list(the_meal_plan)