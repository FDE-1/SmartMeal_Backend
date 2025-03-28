from flask import jsonify, request
from ..connection.loader import db
from ..models.inventory import Inventory
from flask_restx import Namespace, Resource, fields


api = Namespace('inventory', description='Inventory Management API')

# Define API Model for Swagger Documentation
inventory_model = api.model('Inventory', {
    'user_id': fields.Integer(required=True, description="ID of the user"),
    'ustensils': fields.List(fields.Raw(), description="List of utensils"),
    'grocery': fields.List(fields.Raw(), description="List of grocery items"),
    'fresh_produce': fields.List(fields.Raw(), description="List of fresh produce items"),
})

@api.route('/')
class InventoryListResource(Resource):
    @api.doc('get_all_inventories')
    def get(self):
        """Retrieve all inventory records"""
        inventories = Inventory.query.all()
        return [
            {
                'inventory_id': inv.inventory_id,
                'user_id': inv.user_id,
                'ustensils': inv.ustensils,
                'grocery': inv.grocery,
                'fresh_produce': inv.fresh_produce
            } for inv in inventories
        ], 200

    @api.doc('create_inventory')
    @api.expect(inventory_model)
    def post(self):
        """Create a new inventory entry"""
        data = request.get_json()

        new_inventory = Inventory(
            user_id=data['user_id'],
            ustensils=data.get('ustensils', []),
            grocery=data.get('grocery', []),
            fresh_produce=data.get('fresh_produce', [])
        )

        db.session.add(new_inventory)
        db.session.commit()

        return {'message': 'Inventory added successfully', 'inventory_id': new_inventory.inventory_id}, 201


@api.route('/<int:inventory_id>')
@api.param('inventory_id', 'Inventory ID')
class InventoryResource(Resource):
    @api.doc('get_inventory')
    def get(self, inventory_id):
        """Retrieve inventory by ID"""
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return {'message': 'Inventory not found'}, 404

        return {
            'inventory_id': inventory.inventory_id,
            'user_id': inventory.user_id,
            'ustensils': inventory.ustensils,
            'grocery': inventory.grocery,
            'fresh_produce': inventory.fresh_produce
        }, 200