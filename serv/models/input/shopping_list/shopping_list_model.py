from flask_restx import fields
from serv.loaders.api import api

shopping_list_model = api.model('ShoppingList', {
    'shoppinglist_id': fields.Integer(readOnly=True),
    'user_id': fields.Integer(required=True),
    'grocery': fields.Raw(required=False),
    'fresh_produce': fields.Raw(required=False),
    'fruit_and_vegetables': fields.Raw(required=False)
})
