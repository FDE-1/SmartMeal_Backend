from serv.services.shopping_listService import get_all_shopping_lists, create_shopping_list_in_db, get_shopping_list, update_shopping_list, delete_shopping_list, get_user_shopping_lists
from flask_restx import abort
from flask import request

def list_all_shopping_lists():
    """Formats shopping lists data for response"""
    lists = get_all_shopping_lists()
    return [{
        'shoppinglist_id': sl.shoppinglist_id,
        'user_id': sl.user_id,
        'grocery': sl.grocery,
        'fresh_produce': sl.fresh_produce,
        'fruit_and_vegetables': sl.fruit_and_vegetables
    } for sl in lists]

def handle_shopping_list_creation():
    """Validates and processes shopping list creation"""
    data = request.get_json()
    if not data:
        abort(400, 'No input data provided')
    if 'user_id' not in data:
        abort(400, 'user_id is required')
    
    try:
        new_list = create_shopping_list_in_db(data)
        return {
            'message': 'Shopping list created successfully',
            'shoppinglist_id': new_list.shoppinglist_id
        }
    except Exception as e:
        abort(500, 'Failed to create shopping list')

def get_shopping_list_details(shoppinglist_id):
    """Formats shopping list data for response"""
    slist = get_shopping_list(shoppinglist_id)
    if not slist:
        abort(404, 'Shopping list not found')
    
    return {
        'shoppinglist_id': slist.shoppinglist_id,
        'user_id': slist.user_id,
        'grocery': slist.grocery,
        'fresh_produce': slist.fresh_produce,
        'fruit_and_vegetables': slist.fruit_and_vegetables
    }

def handle_shopping_list_update(shoppinglist_id):
    """Processes shopping list updates"""
    data = request.get_json()
    updated_list = update_shopping_list(shoppinglist_id, data)
    if not updated_list:
        abort(404, 'Shopping list not found')
    return {'message': 'Shopping list updated successfully'}

def handle_shopping_list_deletion(shoppinglist_id):
    """Handles shopping list deletion"""
    if not delete_shopping_list(shoppinglist_id):
        abort(404, 'Shopping list not found')
    return {'message': 'Shopping list deleted successfully'}

def get_user_shopping_lists_data(user_id):
    """Formats user's shopping lists for response"""
    lists = get_user_shopping_lists(user_id)
    return [{
        'shoppinglist_id': sl.shoppinglist_id,
        'grocery': sl.grocery,
        'fresh_produce': sl.fresh_produce,
        'fruit_and_vegetables': sl.fruit_and_vegetables
    } for sl in lists]