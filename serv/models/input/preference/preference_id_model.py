from flask_restx import fields
from serv.loaders.api import api

preference_id_model=api.model('user_id',{
    'user_id': fields.Integer()
})