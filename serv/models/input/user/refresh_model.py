from flask_restx import fields
from loaders.api import api

refresh_token_model = api.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description="Jeton de rafraîchissement")
})