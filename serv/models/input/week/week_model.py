from flask_restx import fields
from serv.loaders.api import api

day_fields = {
    'lundi': fields.List(fields.Raw, required=False),
    'mardi': fields.List(fields.Raw, required=False),
    'mercredi': fields.List(fields.Raw, required=False),
    'jeudi': fields.List(fields.Raw, required=False),
    'vendredi': fields.List(fields.Raw, required=False),
    'samedi': fields.List(fields.Raw, required=False),
    'dimanche': fields.List(fields.Raw, required=False)
}

week_model= api.model('Week', {
    'week_id': fields.Integer(readOnly=True),
    'user_id': fields.Integer(required=True),
    **day_fields
})