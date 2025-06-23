from flask_restx import fields
from serv.loaders.api import api

inventory_model = api.model('Inventory', {
    'user_id': fields.Integer(required=True, description="ID of the user"),
    'ustensils': fields.List(fields.Raw(), required=True, description="List of utensils"),
    'grocery': fields.List(fields.Raw(), required=True, description="List of grocery items"),
    'fresh_produce': fields.List(fields.Raw(), required=True, description="List of fresh produce items"),
})