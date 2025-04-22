from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.user_recipe import UserRecipe
from flask_restx import Namespace, Resource, fields

api = Namespace('user_recipes', description='User recipe personalization operations')

user_recipe_model = api.model('UserRecipe', {
    'user_id': fields.Integer(required=True),
    'recipe_id': fields.Integer(required=True),
    'personalisation': fields.Raw(required=True)
})

@api.route('/')
class UserRecipeList(Resource):
    @api.doc('list_user_recipes')
    def get(self):
        """List all user recipes"""
        user_recipes = UserRecipe.query.all()
        return jsonify([{
            'user_recipes_id': ur.user_recipes_id,
            'user_id': ur.user_id,
            'recipe_id': ur.recipe_id,
            'personalisation': ur.personalisation
        } for ur in user_recipes])

    @api.doc('create_user_recipe')
    @api.expect(user_recipe_model)
    def post(self):
        """Create a new user recipe"""
        try:
            data = request.json
            if not data:
                return {'message': 'No input data provided'}, 400

            required_fields = ['user_id', 'recipe_id']
            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                return {
                    'message': 'Missing required fields',
                    'missing_fields': missing
                }, 400

            new_user_recipe = UserRecipe(
                user_id=data['user_id'],
                recipe_id=data['recipe_id'],
                personalisation=data.get('personalisation', {})
            )

            db.session.add(new_user_recipe)
            db.session.commit()
            
            return {
                'message': 'User recipe created successfully',
                'user_recipes_id': new_user_recipe.user_recipes_id
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user recipe: {str(e)}")
            return {
                'message': 'Failed to create user recipe',
                'error': str(e)
            }, 500

@api.route('/user/<int:user_id>')
class UserRecipeByUser(Resource):
    @api.doc('get_user_recipes_by_user')
    def get(self, user_id):
        """Get all recipes for a specific user"""
        user_recipes = UserRecipe.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'user_recipes_id': ur.user_recipes_id,
            'recipe_id': ur.recipe_id,
            'personalisation': ur.personalisation
        } for ur in user_recipes])

@api.route('/<int:user_recipes_id>')
class UserRecipeResource(Resource):
    @api.doc('get_user_recipe')
    @api.response(404, 'User recipe not found')
    def get(self, user_recipes_id):
        """Get a specific user recipe by ID"""
        user_recipe = UserRecipe.query.get_or_404(user_recipes_id)
        return {
            'user_recipes_id': user_recipe.user_recipes_id,
            'user_id': user_recipe.user_id,
            'recipe_id': user_recipe.recipe_id,
            'personalisation': user_recipe.personalisation
        }

    @api.doc('update_user_recipe')
    @api.expect(user_recipe_model)
    @api.response(404, 'User recipe not found')
    def put(self, user_recipes_id):
        """Update a user recipe"""
        try:
            user_recipe = UserRecipe.query.get_or_404(user_recipes_id)
            data = api.payload
            
            if 'user_id' in data:
                user_recipe.user_id = data['user_id']
            if 'recipe_id' in data:
                user_recipe.recipe_id = data['recipe_id']
            if 'personalisation' in data:
                user_recipe.personalisation = data['personalisation']
            
            db.session.commit()
            return {'message': 'User recipe updated successfully'}
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user recipe {user_recipes_id}: {str(e)}")
            return {
                'message': 'Failed to update user recipe',
                'error': str(e)
            }, 500

    @api.doc('delete_user_recipe')
    @api.response(404, 'User recipe not found')
    def delete(self, user_recipes_id):
        """Delete a user recipe"""
        try:
            user_recipe = UserRecipe.query.get_or_404(user_recipes_id)
            db.session.delete(user_recipe)
            db.session.commit()
            return {'message': 'User recipe deleted successfully'}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user recipe {user_recipes_id}: {str(e)}")
            return {
                'message': 'Failed to delete user recipe',
                'error': str(e)
            }, 500

@api.route('/testsuite/user_recipes')
class UserRecipeTestSuite(Resource):
    @api.doc('run_user_recipe_test_suite')
    @api.response(200, 'Success')
    @api.response(500, 'Server error')
    def post(self):
        """Execute a complete test suite for user recipes"""
        results = []
        user_recipe_id = None
        test_user_id = 1  # Special test user ID
        test_recipe_id = 1  # Special test recipe ID

        def unpack_response(resp):
            if isinstance(resp, tuple):
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Create user recipe ===
            create_payload = {
                "user_id": test_user_id,
                "recipe_id": test_recipe_id,
                "personalisation": {
                    "spiciness": "medium",
                    "notes": "Test recipe"
                }
            }

            with current_app.test_request_context(json=create_payload):
                response = UserRecipeList().post()
                recipe_obj, status_code = unpack_response(response)
                print(recipe_obj)
                print(status_code)
                user_recipe_id = recipe_obj['user_recipes_id']
                results.append(f"✅ User recipe created with ID: {user_recipe_id}")

            # === Test 2: Get user recipe ===
            with current_app.test_request_context():
                response = UserRecipeResource().get(user_recipe_id)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Failed to fetch user recipe")
                if data['user_id'] != test_user_id:
                    raise Exception("Incorrect user ID")
                results.append("✅ User recipe retrieved successfully")

            # === Test 3: Update user recipe ===
            update_payload = {
                "personalisation": {
                    "spiciness": "hot",
                    "notes": "Updated test recipe",
                    "extra": "cheese"
                }
            }

            with current_app.test_request_context(json=update_payload):
                response = UserRecipeResource().put(user_recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Update failed")
                results.append("✅ User recipe updated successfully")

            # === Test 4: Get by user ID ===
            with current_app.test_request_context():
                response = UserRecipeByUser().get(test_user_id)
                data, status_code = unpack_response(response)
                if status_code != 200 or len(data.json) == 0:
                    raise Exception("Failed to fetch by user ID")
                results.append("✅ User recipes by user retrieved")

            # === Test 5: Delete ===
            with current_app.test_request_context():
                response = UserRecipeResource().delete(user_recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Deletion failed")
                results.append("✅ User recipe deleted successfully")

            results.append("\n🏁 All user recipe tests passed successfully!")
            return {'results': results}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            if user_recipe_id:
                ur = UserRecipe.query.get(user_recipe_id)
                if ur:
                    db.session.delete(ur)
                    db.session.commit()
            
            results.append(f"\n❌ Error during tests: {str(e)}")
            return {'results': results}, 500