from flask_restx import fields
from serv.loaders.api import api

user_recipe_model = api.model('UserRecipe', {
    'user_id': fields.Integer(required=True),
    'recipe_id': fields.Integer(required=True),
    'personalisation': fields.Raw(required=True)
})