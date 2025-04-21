from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.inventory import Inventory
from flask_restx import Namespace, Resource, fields
import time

api = Namespace('inventory', description='Inventory Management API')

inventory_model = api.model('Inventory', {
    'user_id': fields.Integer(required=True, description="ID of the user"),
    'ustensils': fields.List(fields.Raw(), required=True, description="List of utensils"),
    'grocery': fields.List(fields.Raw(), required=True, description="List of grocery items"),
    'fresh_produce': fields.List(fields.Raw(), required=True, description="List of fresh produce items"),
})

seach_model = api.model('Search', {
    'inventory_id':  fields.Integer(readOnly=True, required=True, description='Identifiant unique')
})

update_model = api.model('Update', {
    'inventory_id': fields.Integer(required=True, readOnly=True, description='Identifiant unique'),
    'ustensils': fields.List(fields.Raw(), description="List of utensils"),
    'grocery': fields.List(fields.Raw(), description="List of grocery items"),
    'fresh_produce': fields.List(fields.Raw(), description="List of fresh produce items"),
})

search_user_model = api.model('Search_user', {
    'user_id': fields.Integer(required=True, description="ID of the user")
})

@api.route('/')
class InventoryListResource(Resource):
    @api.doc('get_all_inventories')
    def get(self):
        """Retrieve all inventory records"""
        try:
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
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la récupération des inventaires", error=str(e))


    @api.doc('create_inventory')
    @api.expect(inventory_model)
    def post(self):
        """Create a new inventory entry"""
        try:
            data = api.payload
            print(data)
            if not data:
                return {'error': 'No input data provided'}, 400
            if 'user_id' not in data:
                return {'error': 'user_id is required'}, 400

            new_inventory = Inventory(
                user_id=data['user_id'],
                ustensils=data['ustensils'],
                grocery=data['grocery'],
                fresh_produce=data['fresh_produce']
            )

            db.session.add(new_inventory)
            db.session.commit()

            return new_inventory, 201
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la création d'un inventaire", error=str(e))


@api.route('/inventories')
class InventoryResource(Resource):
    @api.doc('get_inventory')
    @api.doc(params={'inventory_id': 'Identifiant unique de l\'inventaire'})
    def get(self):
        """Récupère un inventaire par son ID (via query parameter)"""
        try:
            inventory_id = request.args.get('inventory_id', type=int) 
            if not inventory_id:
                return {'message': 'Paramètre inventory_id manquant'}, 400

            inventory = Inventory.query.get(inventory_id)
            if not inventory:
                return {'message': 'Inventaire pas trouvé'}, 404

            return {
                'inventory_id': inventory.inventory_id,
                'user_id': inventory.user_id,
                'ustensils': inventory.ustensils,
                'grocery': inventory.grocery,
                'fresh_produce': inventory.fresh_produce
            }, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la récupération de l'inventaire", error=str(e))

    @api.doc('update_inventory')
    @api.expect(update_model)
    def put(self):
        """Met à jour complètement un inventaire avec vérification du commit"""
        try:
            data = api.payload
            inventory = Inventory.query.get(data['inventory_id'])
            
            if not inventory:
                api.abort(404, "Inventaire non trouvé")

            def update_items(existing, new_items):
                if not new_items:
                    return existing or []
                
                existing = existing or []
                item_map = {item['name']: item for item in existing}
                
                for item in new_items:
                    name = item['name']
                    if name in item_map:
                        item_map[name]['quantity'] = item_map[name].get('quantity', 0) + item.get('quantity', 1)
                    else:
                        item_map[name] = item
                return list(item_map.values())

            inventory.ustensils = update_items(inventory.ustensils, data.get('ustensils'))
            inventory.grocery = update_items(inventory.grocery, data.get('grocery'))
            inventory.fresh_produce = update_items(inventory.fresh_produce, data.get('fresh_produce'))

            db.session.flush()  
            db.session.commit()
            
            return {
                'message': 'Inventaire mis à jour avec succès',
                'inventory': {
                    'ustensils': inventory.ustensils,
                    'grocery': inventory.grocery,
                    'fresh_produce': inventory.fresh_produce
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur update_inventory: {str(e)}\nTraceback: {traceback.format_exc()}")
            api.abort(500, "Échec de la mise à jour", error={
                'message': str(e),
                'type': type(e).__name__
            })
    @api.doc('delete_inventory')
    @api.expect(seach_model)
    def delete(self):
        """Supprime un inventaire"""
        try:
            data = api.payload
            inventory_id = data['inventory_id']
            inventory = Inventory.query.get(inventory_id)
            db.session.delete(inventory)
            db.session.commit()
            return {'message': 'Inventaire supprimé'}
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la supprésion", error=str(e))

    
@api.route('/by_user/<int:user_id>')
class InventoryResourceUser(Resource):
    @api.doc('get_inventory_by_user')
    def get(self, user_id):
        """Retrieve inventory by user ID"""
        try:
            inventory = Inventory.query.filter_by(user_id=user_id).first()
            if not inventory:
                return {'message': 'Inventory not found'}, 404
            return {
            'inventory_id': inventory.inventory_id,
            'user_id': inventory.user_id,
            'ustensils': inventory.ustensils,
            'grocery': inventory.grocery,
            'fresh_produce': inventory.fresh_produce
             }, 200
        except Exception as e:
            return {'message': str(e)}, 500

@api.route('/testsuite')
class InventoryTestSuite(Resource):

    @api.doc('run_inventory_test_suite')
    @api.response(200, 'Succès')
    @api.response(500, 'Erreur du serveur')
    def post(self):
        """Exécute une suite de tests complète pour l'inventaire"""
        résultats = []
        inventory_id = None
        user_id = 4

        def unpack_response(resp):
            """Gère les tuples de Flask RESTx"""
            if isinstance(resp, tuple):
                time.sleep(0.2)
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Création inventaire ===
            create_payload = {
                "user_id": user_id,
                "ustensils": [{"name": "spoon", "quantity": 2}],
                "grocery": [{"name": "rice", "quantity": 5}],
                "fresh_produce": [{"name": "apple", "quantity": 3}]
            }

            with current_app.test_request_context(json=create_payload):
                response = InventoryListResource().post()
                inv_obj, status_code = unpack_response(response)
                inventory_id = getattr(inv_obj, 'inventory_id', None)
                résultats.append(f"✅ Inventaire créé avec ID : {inventory_id}")

            # === Test 2: Récupération par ID ===
            with current_app.test_request_context(path=f'/by_user/{user_id}'):  # Match the route path
                response = InventoryResourceUser().get(user_id)  # Pass user_id as argument
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de récupération par ID")
                résultats.append(f"✅ Inventaire récupéré : {data}")

            # === Test 3: Mise à jour partielle avec nouveaux items ===
            update_payload = {
                "inventory_id": inventory_id,
                "grocery": [{"name": "rice", "quantity": 3}, {"name": "beans", "quantity": 2}],
                "fresh_produce": [{"name": "banana", "quantity": 5}]
            }

            with current_app.test_request_context(json=update_payload):
                response = InventoryResource().put()
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de la mise à jour")
                résultats.append("✅ Mise à jour effectuée avec succès")

            # === Test 4: Vérification update ===
            with current_app.test_request_context(query_string={"inventory_id": inventory_id}):  # Changed from json to query_string
                response = InventoryResource().get()
                updated, _ = unpack_response(response)
                grocery = updated['grocery']               
                banana_exists = any(item['name'] == 'banana' and item['quantity'] == 5 for item in updated['fresh_produce'])
                rice_updated = any(item['name'] == 'rice' and item['quantity'] == 8 for item in grocery)
                if not (banana_exists and rice_updated):
                    raise Exception("Échec de la fusion ou update des quantités")
                résultats.append("✅ Quantités et nouveaux éléments vérifiés avec succès")

            # === Test 5: Suppression ===
            with current_app.test_request_context(json={"inventory_id": inventory_id}):
                response = InventoryResource().delete()
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de suppression")
                résultats.append("✅ Inventaire supprimé avec succès")

            résultats.append("\n🏁 Tous les tests de l'inventaire sont passés avec succès !")
            return {'résultats': résultats}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            résultats.append(f"\n❌ Erreur pendant les tests : {str(e)}")
            return {'résultats': résultats}, 500
