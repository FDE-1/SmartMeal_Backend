from flask_restx import fields
from serv.loaders.api import api

search_user_model = api.model('Search_user', {
    'user_id': fields.Integer(required=True, description="ID of the user")
})