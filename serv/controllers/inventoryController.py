from services.inventoryService import create_inventory, get_all_inventories, update_inventory, delete_inventory, get_inventory_by_id, get_inventory_by_user
from flask_restx import abort
from flask import request

def get_all_inventories():
    return get_all_inventories()

def format_inventories(inventories):
    """Formats inventory data for response"""
    return [{
        'inventory_id': inv.inventory_id,
        'user_id': inv.user_id,
        'ustensils': inv.ustensils,
        'grocery': inv.grocery,
        'fresh_produce': inv.fresh_produce
    } for inv in inventories]

def handle_inventory_creation():
    """Validates and processes inventory creation"""
    data = request.get_json()
    if not data:
        abort(400, 'No input data provided')
    if 'user_id' not in data:
        abort(400, 'user_id is required')
    
    try:
        new_inventory = create_inventory(data)
        return new_inventory
    except Exception as e:
        abort(500, f"Error creating inventory: {str(e)}")

def handle_get_inventory(inventory_id):
    """Handles inventory retrieval"""
    if not inventory_id:
        abort(400, 'Paramètre inventory_id manquant')
    
    inventory = get_inventory_by_id(inventory_id)
    if not inventory:
        abort(404, 'Inventaire pas trouvé')
    
    return {
        'inventory_id': inventory.inventory_id,
        'user_id': inventory.user_id,
        'ustensils': inventory.ustensils,
        'grocery': inventory.grocery,
        'fresh_produce': inventory.fresh_produce
    }

def handle_update_inventory():
    """Handles inventory update"""
    data = request.get_json()

    if 'user_id' not in data:
        abort(400, 'user_id est requis')
    
    updated_inventory = update_inventory(
        data['user_id'],
        data
    )
    if not updated_inventory:
        abort(404, 'Inventaire non trouvé')
    
    return {
        'message': 'Inventaire mis à jour avec succès',
        'inventory': {
            'ustensils': updated_inventory.ustensils,
            'grocery': updated_inventory.grocery,
            'fresh_produce': updated_inventory.fresh_produce
        }
    }

def handle_delete_inventory(inventory_id):
    """Handles inventory deletion"""
    if not delete_inventory(inventory_id):
        abort(404, 'Inventaire non trouvé')
    return {'message': 'Inventaire supprimé'}

def handle_get_inventory_by_user(user_id):
    """Handles inventory retrieval by user ID"""
    inventory = get_inventory_by_user(user_id)
    if not inventory:
        abort(404, 'Inventory not found')
    
    return {
        'inventory_id': inventory.inventory_id,
        'user_id': inventory.user_id,
        'ustensils': inventory.ustensils,
        'grocery': inventory.grocery,
        'fresh_produce': inventory.fresh_produce
    }