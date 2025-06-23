from flask_restx import fields
from loaders.api import api

recipe_model = api.model('Recipe', {
    'title': fields.String(required=True, description='Titre de la recette'),
    'ingredients': fields.List(fields.String,required=True,description='List des ingrédients (e.g., "100g Farine")'),
    'instructions': fields.List(fields.String,required=True,description='Instructions'),
    'ner': fields.List(fields.String,required=True,description='Ingredients'),
    'type': fields.String(required=False,description='Catégories["Entree","Plat","Dessert"]'),
    'calories': fields.Integer(required=False, description="Nombre de calories"),
    'nutriments': fields.Nested(api.model('Nutriments', {
        'lipide': fields.Float(description='g lipide'),
        'glucide': fields.Float(description='g glucide'),
        'proteine': fields.Float(description='g proteine'),
        'fibre': fields.Float(description='g fibre')
    }), description='Info Nutritionel'),
    'day': fields.String(required=False,description="Jour ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']",enum=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
    'link': fields.String(required=False,description='Origine default = null'),
    'source': fields.String(required=False,description='Source default = null'),
    'recipe_id': fields.Integer(required=False,description='recipe ID'),
    'user_id': fields.Integer(required=True,description='User ID')
    })