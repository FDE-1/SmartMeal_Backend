from flask_restx import fields
from serv.loaders.api import api

seach_model = api.model('Search', {
    'inventory_id':  fields.Integer(readOnly=True, required=True, description='Identifiant unique')
})