from flask_restx import fields
from loaders.api import api

liked_recipe_model = api.model('LikedRecipe', {
    'recipe_id': fields.Integer(required=True, description='The recipe ID'),
    'title': fields.String(required=True, description='The recipe title'),
    'user_id': fields.Integer(required=True, description='The user ID who created the recipe'),
    'list_like_id': fields.List(fields.Integer, description='List of user IDs who liked the recipe'),
    'ingredients': fields.List(fields.String, description='List of ingredients'),
    'instructions': fields.List(fields.String, description='List of instructions'),
    'ner': fields.List(fields.String, description='Named entity recognition tags'),
    'type': fields.String(description='Recipe type'),
    'calories': fields.Integer(description='Calorie count'),
    'nutriments': fields.Raw(description='Nutritional information')
})