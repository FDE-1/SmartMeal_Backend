from flask_restx import fields
from serv.loaders.api import api

shopping_list_input = api.model('ShoppingListInput', {
    'user_id': fields.Integer(required=True, description='ID de l’utilisateur'),
    'meal_plan': fields.Raw(required=True, description='Plan de repas généré')
})