from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.shopping_list import ShoppingList
from flask_restx import Namespace, Resource, fields

api = Namespace('shopping_lists', description='Shopping list operations')

shopping_list_model = api.model('ShoppingList', {
    'shoppinglist_id': fields.Integer(readOnly=True),
    'user_id': fields.Integer(required=True),
    'grocery': fields.Raw(required=False),
    'fresh_produce': fields.Raw(required=False),
    'fruit_and_vegetables': fields.Raw(required=False)
})

@api.route('/')
class ShoppingListResource(Resource):
    @api.doc('list_shopping_lists')
    def get(self):
        """List all shopping lists"""
        lists = ShoppingList.query.all()
        return jsonify([{
            'shoppinglist_id': sl.shoppinglist_id,
            'user_id': sl.user_id,
            'grocery': sl.grocery,
            'fresh_produce': sl.fresh_produce,
            'fruit_and_vegetables': sl.fruit_and_vegetables
        } for sl in lists])

    @api.doc('create_shopping_list')
    @api.expect(shopping_list_model)
    def post(self):
        """Create a new shopping list"""
        try:
            data = request.json
            if not data:
                return {'message': 'No input data provided'}, 400

            if 'user_id' not in data:
                return {'message': 'user_id is required'}, 400

            new_list = ShoppingList(
                user_id=data['user_id'],
                grocery=data.get('grocery', {}),
                fresh_produce=data.get('fresh_produce', {}),
                fruit_and_vegetables=data.get('fruit_and_vegetables', {})
            )

            db.session.add(new_list)
            db.session.commit()
            
            return {
                'message': 'Shopping list created successfully',
                'shoppinglist_id': new_list.shoppinglist_id
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating shopping list: {str(e)}")
            return {
                'message': 'Failed to create shopping list',
                'error': str(e)
            }, 500

@api.route('/<int:shoppinglist_id>')
class ShoppingListDetail(Resource):
    @api.doc('get_shopping_list')
    @api.response(404, 'Shopping list not found')
    def get(self, shoppinglist_id):
        """Get a specific shopping list"""
        slist = ShoppingList.query.get_or_404(shoppinglist_id)
        return {
            'shoppinglist_id': slist.shoppinglist_id,
            'user_id': slist.user_id,
            'grocery': slist.grocery,
            'fresh_produce': slist.fresh_produce,
            'fruit_and_vegetables': slist.fruit_and_vegetables
        }

    @api.doc('update_shopping_list')
    @api.expect(shopping_list_model)
    @api.response(404, 'Shopping list not found')
    def put(self, shoppinglist_id):
        """Update a shopping list"""
        try:
            slist = ShoppingList.query.get_or_404(shoppinglist_id)
            data = request.json
            
            if 'grocery' in data:
                slist.grocery = data['grocery']
            if 'fresh_produce' in data:
                slist.fresh_produce = data['fresh_produce']
            if 'fruit_and_vegetables' in data:
                slist.fruit_and_vegetables = data['fruit_and_vegetables']
            
            db.session.commit()
            return {'message': 'Shopping list updated successfully'}
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating shopping list {shoppinglist_id}: {str(e)}")
            return {
                'message': 'Failed to update shopping list',
                'error': str(e)
            }, 500

    @api.doc('delete_shopping_list')
    @api.response(404, 'Shopping list not found')
    def delete(self, shoppinglist_id):
        """Delete a shopping list"""
        try:
            slist = ShoppingList.query.get_or_404(shoppinglist_id)
            db.session.delete(slist)
            db.session.commit()
            return {'message': 'Shopping list deleted successfully'}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting shopping list {shoppinglist_id}: {str(e)}")
            return {
                'message': 'Failed to delete shopping list',
                'error': str(e)
            }, 500

@api.route('/user/<int:user_id>')
class UserShoppingLists(Resource):
    @api.doc('get_user_shopping_lists')
    def get(self, user_id):
        """Get all shopping lists for a user"""
        top_list = ShoppingList.query.filter_by(user_id=user_id).order_by(ShoppingList.shoppinglist_id.desc()).first()        
        return jsonify({
            'shoppinglist_id': top_list.shoppinglist_id,
            'grocery': top_list.grocery,
            'fresh_produce': top_list.fresh_produce,
            'fruit_and_vegetables': top_list.fruit_and_vegetables
        })
    
@api.route('/testsuite/shopping_lists')
class ShoppingListTestSuite(Resource):
    @api.doc('run_shopping_list_test_suite')
    @api.response(200, 'Success')
    @api.response(500, 'Server error')
    def post(self):
        """Execute a complete test suite for shopping lists"""
        results = []
        shoppinglist_id = None
        test_user_id = 1  # Special test user ID

        def unpack_response(resp):
            if isinstance(resp, tuple):
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Create shopping list ===
            create_payload = {
                "user_id": test_user_id,
                "grocery": {"rice": 2, "pasta": 3},
                "fresh_produce": {"milk": 1},
                "fruit_and_vegetables": {"apple": 5}
            }

            with current_app.test_request_context(json=create_payload):
                response = ShoppingListResource().post()
                list_obj, status_code = unpack_response(response)
                print(list_obj)
                print(status_code)
                shoppinglist_id = list_obj['shoppinglist_id']
                results.append(f"✅ Shopping list created with ID: {shoppinglist_id}")

            # === Test 2: Get shopping list ===
            with current_app.test_request_context():
                response = ShoppingListDetail().get(shoppinglist_id)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Failed to fetch shopping list")
                if data['user_id'] != test_user_id:
                    raise Exception("Incorrect user ID")
                results.append("✅ Shopping list retrieved successfully")

            # === Test 3: Update shopping list ===
            update_payload = {
                "grocery": {"rice": 3, "pasta": 2, "oil": 1},
                "fruit_and_vegetables": {"apple": 4, "banana": 2}
            }

            with current_app.test_request_context(json=update_payload):
                response = ShoppingListDetail().put(shoppinglist_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Update failed")
                results.append("✅ Shopping list updated successfully")

            # === Test 4: Verify update ===
            with current_app.test_request_context():
                response = ShoppingListDetail().get(shoppinglist_id)
                updated, _ = unpack_response(response)
                if updated['grocery'].get('oil') != 1:
                    raise Exception("Grocery update failed")
                results.append("✅ Update verified")

            # === Test 5: Get by user ID ===
            with current_app.test_request_context():
                response = UserShoppingLists().get(test_user_id)
                data, status_code = unpack_response(response)
                if status_code != 200 or len(data.json) == 0:
                    raise Exception("Failed to fetch by user ID")
                results.append("✅ User shopping lists retrieved")

            # === Test 6: Delete ===
            with current_app.test_request_context():
                response = ShoppingListDetail().delete(shoppinglist_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Deletion failed")
                results.append("✅ Shopping list deleted successfully")

            # Final verification
            deleted_list = ShoppingList.query.get(shoppinglist_id)
            if deleted_list:
                raise Exception("Deletion didn't work")

            results.append("\n🏁 All shopping list tests passed successfully!")
            return {'results': results}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            # Cleanup if failed
            if shoppinglist_id:
                sl = ShoppingList.query.get(shoppinglist_id)
                if sl:
                    db.session.delete(sl)
                    db.session.commit()
            
            results.append(f"\n❌ Error during tests: {str(e)}")
            return {'results': results}, 500