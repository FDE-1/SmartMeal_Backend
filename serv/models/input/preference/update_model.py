from flask_restx import fields
from loaders.api import api

update_model = api.model('update', {
    "user_id": fields.Integer(),
    "allergy": fields.Raw(required=True, description="ID of the user"),
    "goal": fields.String(required=True, description="ID of the user"),
    "number_of_meals": fields.Integer(required=True, description="ID of the user"),
})