from flask_restx import fields
from loaders.api import api
from models.input.recipe.recipe_model import recipe_model

bulk_like_model = api.model('BulkLikeRequest', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'recipes': fields.List(fields.Nested(recipe_model), required=True, description='List of recipes to like')
})