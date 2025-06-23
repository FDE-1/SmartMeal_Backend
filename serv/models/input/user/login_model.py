from flask_restx import fields
from serv.loaders.api import api

login_model = api.model('Login', {
    'email': fields.String(required=True, description="email"),
    'password': fields.String(required=True, description="Mot de passe")
})