from flask_restx import Namespace, Resource
from loaders.api import api
from controllers.shopping_listController import list_all_shopping_lists, handle_shopping_list_creation, get_shopping_list_details, handle_shopping_list_update, handle_shopping_list_deletion, get_user_shopping_lists_data
from models.input.shopping_list.shopping_list_model import shopping_list_model

shopping_list_route = Namespace('shopping_lists', description='Shopping list operations')

@shopping_list_route.route('/')
class ShoppingListResource(Resource):
    @shopping_list_route.doc('list_shopping_lists')
    def get(self):
        """List all shopping lists"""
        return list_all_shopping_lists()

    @shopping_list_route.doc('create_shopping_list')
    @shopping_list_route.expect(shopping_list_model)
    def post(self):
        """Create a new shopping list"""
        return handle_shopping_list_creation()
    
@shopping_list_route.route('/<int:shoppinglist_id>')
class ShoppingListDetail(Resource):
    @shopping_list_route.doc('get_shopping_list')
    @shopping_list_route.response(404, 'Shopping list not found')
    def get(self, shoppinglist_id):
        """Get a specific shopping list"""
        return get_shopping_list_details(shoppinglist_id)

    @shopping_list_route.doc('update_shopping_list')
    @shopping_list_route.expect(shopping_list_model)
    @shopping_list_route.response(404, 'Shopping list not found')
    def put(self, shoppinglist_id):
        """Update a shopping list"""
        return handle_shopping_list_update(shoppinglist_id)

    @shopping_list_route.doc('delete_shopping_list')
    @shopping_list_route.response(404, 'Shopping list not found')
    def delete(self, shoppinglist_id):
        """Delete a shopping list"""
        return handle_shopping_list_deletion(shoppinglist_id)
    
@shopping_list_route.route('/user/<int:user_id>')
class UserShoppingLists(Resource):
    @shopping_list_route.doc('get_user_shopping_lists')
    def get(self, user_id):
        """Get all shopping lists for a user"""
        return get_user_shopping_lists_data(user_id)
