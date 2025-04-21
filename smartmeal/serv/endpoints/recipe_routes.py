from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.recipe import Recipe
from flask_restx import Namespace, Resource, fields

api = Namespace('recipes', description='Recipe operations')

recipe_model = api.model('Recipe', {
    'recipe_name': fields.String(required=True),
    'recipe_ingredients': fields.Raw(required=True),
    'recipe_instructions': fields.Raw(required=True),
    'recipe_preparation_time': fields.Integer(required=True),
    'recipe_ustensils_required': fields.Raw(required=True),
    'recipe_nutritional_value': fields.Raw(required=True),
    'rating': fields.Float(description='Rating from 0 to 5 in 0.5 increments')
})

@api.route('/')
class RecipeList(Resource):
    @api.doc('list_recipes')
    def get(self):
        """List all recipes"""
        recipes = Recipe.query.all()
        return jsonify([{'recipe_id': r.recipe_id, 'name': r.recipe_name, 'rating': r.rating} for r in recipes])

    @api.doc('create_recipe')
    @api.expect(recipe_model)
    def post(self):
        """Create a new recipe"""
        try:
            data = request.json
            if not data:
                return {'message': 'No input data provided'}, 400

            # Validate required fields
            required_fields = [
                'recipe_name',
                'recipe_ingredients',
                'recipe_instructions',
                'recipe_preparation_time',
            ]
            
            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                return {
                    'message': 'Missing required fields',
                    'missing_fields': missing
                }, 400
            
            if 'rating' in data:
                rating = data['rating']
                if not (0 <= rating <= 5) or (rating * 2) % 1 != 0:
                    return {
                        'message': 'Rating must be between 0 and 5 in 0.5 increments'
                    }, 400

            new_recipe = Recipe(
                recipe_name=data['recipe_name'],
                recipe_ingredients=data['recipe_ingredients'],
                recipe_instructions=data['recipe_instructions'],
                recipe_preparation_time=data['recipe_preparation_time'],
                recipe_ustensils_required=data.get('recipe_ustensils_required', []),
                recipe_nutritional_value=data.get('recipe_nutritional_value', {}),
                rating=data.get('rating', None)
            )

            db.session.add(new_recipe)
            db.session.commit()
            
            return {
                'message': 'Recipe created successfully',
                'recipe_id': new_recipe.recipe_id
            }, 201

        except Exception as e:
            db.session.rollback()
            print(str(e))
            return {
                'message': 'Failed to create recipe',
                'error': str(e)
            }, 500

@api.route('/<int:recipe_id>')
class RecipeResource(Resource):
    @api.doc('get_recipe')
    @api.response(404, 'Recipe not found')
    def get(self, recipe_id):
        """Get a specific recipe by ID"""
        recipe = Recipe.query.get_or_404(recipe_id)
        return {
            'recipe_id': recipe.recipe_id,
            'recipe_name': recipe.recipe_name,
            'recipe_ingredients': recipe.recipe_ingredients,
            'recipe_instructions': recipe.recipe_instructions,
            'recipe_preparation_time': recipe.recipe_preparation_time,
            'recipe_ustensils_required': recipe.recipe_ustensils_required,
            'recipe_nutritional_value': recipe.recipe_nutritional_value,
            'rating': float(recipe.rating) if recipe.rating is not None else None
        }

    @api.doc('update_recipe')
    @api.expect(recipe_model)
    @api.response(404, 'Recipe not found')
    def put(self, recipe_id):
        """Update a recipe"""
        try:
            recipe = Recipe.query.get_or_404(recipe_id)
            data = api.payload
            
            recipe.recipe_name = data.get('recipe_name', recipe.recipe_name)
            recipe.recipe_ingredients = data.get('recipe_ingredients', recipe.recipe_ingredients)
            recipe.recipe_instructions = data.get('recipe_instructions', recipe.recipe_instructions)
            recipe.recipe_preparation_time = data.get('recipe_preparation_time', recipe.recipe_preparation_time)
            recipe.recipe_ustensils_required = data.get('recipe_ustensils_required', recipe.recipe_ustensils_required)
            recipe.recipe_nutritional_value = data.get('recipe_nutritional_value', recipe.recipe_nutritional_value)
            if 'rating' in data:
                recipe.rating = data['rating']
            db.session.commit()
            return {'message': 'Recipe updated successfully'}
        
        except Exception as e:
            db.session.rollback()
            return {
                'message': 'Failed to update recipe',
                'error': str(e)
            }, 500

    @api.doc('delete_recipe')
    @api.response(404, 'Recipe not found')
    def delete(self, recipe_id):
        """Delete a recipe"""
        try:
            recipe = Recipe.query.get_or_404(recipe_id)
            db.session.delete(recipe)
            db.session.commit()
            return {'message': 'Recipe deleted successfully'}
        except Exception as e:
            db.session.rollback()
            return {
                'message': 'Failed to delete recipe',
                'error': str(e)
            }, 500
      
@api.route('/testsuite/recipes')
class RecipeTestSuite(Resource):
    @api.doc('run_recipe_test_suite')
    @api.response(200, 'Success')
    @api.response(500, 'Server error')
    def post(self):
        """Execute a complete test suite for recipes"""
        results = []
        recipe_id = None

        def unpack_response(resp):
            """Handle Flask RESTx response tuples"""
            if isinstance(resp, tuple):
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Create recipe without rating ===
            create_payload = {
                "recipe_name": "Pasta Test",
                "recipe_ingredients": {
                    "pasta": "300g",
                    "tomatoes": "2",
                    "garlic": "1 clove"
                },
                "recipe_instructions": [
                    "Boil water",
                    "Cook pasta",
                    "Prepare sauce"
                ],
                "recipe_preparation_time": 20,
                "recipe_ustensils_required": ["pot", "spatula"],
                "recipe_nutritional_value": {
                    "calories": 500,
                    "protein": "15g"
                }
            }

            with current_app.test_request_context(json=create_payload):
                response = RecipeList().post()
                recipe_obj, status_code = unpack_response(response)
                recipe_id = recipe_obj['recipe_id']
                results.append(f"✅ Recipe created with ID: {recipe_id} (no rating)")

            # === Test 2: Get recipe and verify default fields ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Failed to fetch by recipe_id")
                if data['recipe_name'] != "Pasta Test":
                    raise Exception("Incorrect data retrieved")
                print(data['rating'])
                if data['rating'] is not None:
                    raise Exception("Rating should be null for new recipe")
                results.append(f"✅ Recipe retrieved: {data['recipe_name']}")

            # === Test 3: Update with rating ===
            update_payload = {
                "recipe_name": "Updated Pasta",
                "recipe_ingredients": {
                    "pasta": "400g",
                    "tomatoes": "3",
                    "garlic": "2 cloves",
                    "basil": "some leaves"
                },
                "recipe_instructions": [
                    "Boil salted water",
                    "Cook pasta al dente",
                    "Prepare tomato sauce"
                ],
                "recipe_preparation_time": 25,
                "recipe_ustensils_required": ["pot", "spatula", "blender"],
                "recipe_nutritional_value": {
                    "calories": 600,
                    "protein": "18g"
                },
                "rating": 4.5
            }

            with current_app.test_request_context(json=update_payload):
                response = RecipeResource().put(recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Update failed")
                results.append("✅ Update with rating completed")

            # === Test 4: Verify rating update ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                updated, _ = unpack_response(response)
                if updated['rating'] != 4.5:
                    raise Exception("Rating update failed")
                results.append("✅ Rating update verified")

            # === Test 5: Delete ===
            with current_app.test_request_context():
                response = RecipeResource().delete(recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Deletion failed")
                results.append("✅ Recipe deleted successfully")

            # Final verification
            deleted_recipe = Recipe.query.get(recipe_id)
            if deleted_recipe:
                raise Exception("Deletion didn't work")

            results.append("\n🏁 All recipe tests passed successfully!")
            return {'results': results}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            # Cleanup if failed
            if recipe_id:
                recipe = Recipe.query.get(recipe_id)
                if recipe:
                    db.session.delete(recipe)
                    db.session.commit()
            
            results.append(f"\n❌ Error during tests: {str(e)}")
            return {'results': results}, 500