from flask_restx import fields
from loaders.api import api

user_id_model = api.model('UserIdModel', {
    'user_id': fields.Integer(required=True, description='ID de l’utilisateur')
})     