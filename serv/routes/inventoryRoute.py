from flask_restx import Namespace, Resource
from serv.loaders.api import api
from serv.controllers.inventoryController import get_all_inventories, format_inventories, handle_inventory_creation, handle_get_inventory, handle_update_inventory, handle_delete_inventory, handle_get_inventory_by_user
from serv.models.input.inventory.inventory_model import inventory_model
from serv.models.input.inventory.search_model import seach_model
from serv.models.input.inventory.search_user_model import search_user_model
from flask import abort
from flask import request

inventory_route = Namespace('inventory', description='Inventory Management inventory_route')

@inventory_route.route('/')
class InventoryListResource(Resource):
    @inventory_route.doc('get_all_inventories')
    def get(self):
        """Retrieve all inventory records"""
        try:
            inventories = get_all_inventories()
            return format_inventories(inventories), 200
        except Exception as e:
            abort(500, f"Error retrieving inventories: {str(e)}")

    @inventory_route.doc('create_inventory')
    @inventory_route.expect(inventory_model)
    def post(self):
        """Create a new inventory entry"""
        data = inventory_route.payload
        result = handle_inventory_creation(data)
        return result, 201
    
@inventory_route.route('/inventories')
class InventoryResource(Resource):
    @inventory_route.doc('get_inventory')
    @inventory_route.doc(params={'inventory_id': 'Identifiant unique de l\'inventaire'})
    def get(self):
        """Récupère un inventaire par son ID"""
        try:
            inventory_id = request.args.get('inventory_id', type=int)
            return handle_get_inventory(inventory_id), 200
        except Exception as e:
            abort(500, f"Erreur lors de la récupération: {str(e)}")

    @inventory_route.doc('update_inventory')
    @inventory_route.expect(inventory_model)
    def put(self):
        """Met à jour complètement un inventaire"""
        return handle_update_inventory()

    @inventory_route.doc('delete_inventory')
    @inventory_route.expect(seach_model)
    def delete(self):
        """Supprime un inventaire"""
        try:
            data = inventory_route.payload
            return handle_delete_inventory(data['inventory_id'])
        except Exception as e:
            abort(500, f"Erreur lors de la suppression: {str(e)}")

@inventory_route.route('/by_user/<int:user_id>')
class InventoryResourceUser(Resource):
    @inventory_route.doc('get_inventory_by_user')
    def get(self, user_id):
        """Retrieve inventory by user ID"""
        return handle_get_inventory_by_user(user_id)