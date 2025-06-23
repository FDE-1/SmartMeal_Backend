from flask_restx import fields
from loaders.api import api

preference_model = api.model('Preference', {
    'user_id': fields.Integer(required=True, description="ID of the user"),
    'allergy': fields.Raw(required=True, description="ID of the user"),
    'diet': fields.String(required=True, description="ID of the user"),
    'goal': fields.String(required=True, description="ID of the user"),
    'new': fields.Integer(required=True, description="ID of the user"),
    'number_of_meals': fields.Integer(required=True, description="ID of the user"),
    'grocery_day': fields.String(required=True, description="ID of the user"),
    'language': fields.String(required=True, description="ID of the user"),
})