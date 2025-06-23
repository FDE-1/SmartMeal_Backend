from flask_restx import fields
from loaders.api import api

user_model = api.model('user_model', {
    'user_id': fields.Integer(readOnly=True, description='Identifiant unique'),
    'user_name': fields.String(required=True, description='Prénom'),
    'user_surname': fields.String(required=True, description='Nom'),
    'user_email': fields.String(required=True, description='Email'),
    'user_password': fields.String(required=True, description='Mot de passe'),
})