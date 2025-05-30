from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.recipe import Recipe
from ..models.user import User
from flask_restx import Namespace, Resource, fields

api = Namespace('recipes', description='Recipe operations')

recipe_model = api.model('Recipe', {
    'title': fields.String(required=True, description='Titre de la recette'),
    'ingredients': fields.List(fields.String,required=True,description='List des ingrédients (e.g., "100g Farine")'),
    'instructions': fields.List(fields.String,required=True,description='Instructions'),
    'ner': fields.List(fields.String,required=True,description='Ingredients'),
    'type': fields.String(required=False,description='Catégories["Entree","Plat","Dessert"]'),
    'calories': fields.Integer(required=False, description="Nombre de calories"),
    'nutriments': fields.Nested(api.model('Nutriments', {
        'lipide': fields.Float(description='g lipide'),
        'glucide': fields.Float(description='g glucide'),
        'proteine': fields.Float(description='g proteine'),
        'fibre': fields.Float(description='g fibre')
    }), description='Info Nutritionel'),
    'day': fields.String(required=False,description="Jour ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']",enum=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
    'link': fields.String(required=False,description='Origine default = null'),
    'source': fields.String(required=False,description='Source default = null'),
    'recipe_id': fields.Integer(required=False,description='recipe ID'),
    'user_id': fields.Integer(required=True,description='User ID')
})

@api.route('/')
class RecipeList(Resource):
    @api.doc('list_recipes')
    def get(self):
        """List all recipes"""
        recipes = Recipe.query.all()
        return jsonify([{'recipe_id': r.recipe_id, 'title': r.title, 'ingredients': r.ingredients, 'instructions': r.instructions,
                         'ner': r.ner, "type": r.type, 'calories': r.calories, "nutriments": r.nutriments, "day": r.day,
                         "link": r.link, "source": r.source, "user_id": r.user_id} for r in recipes])

    @api.doc('create_recipe')
    @api.expect(recipe_model)
    def post(self):
        """Create a new recipe"""
        try:
            data = request.json
            if not data:
                return {'message': 'No input data provided'}, 400

            # Validate required fields
            required_fields = ['title', 'ingredients', 'instructions', "ner", "user_id"]
            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                return {
                    'message': 'Missing required fields',
                    'missing_fields': missing
                }, 400

            # Validate day if provided
            if 'day' in data and data['day'] not in [
                'Monday', 'Tuesday', 'Wednesday', 
                'Thursday', 'Friday', 'Saturday', 'Sunday'
            ]:
                return {
                    'message': 'Invalid day value'
                }, 400

            new_recipe = Recipe(
                title=data['title'],
                ingredients=data['ingredients'],
                instructions=data['instructions'],
                ner=data.get('ner', []),
                type=data.get('type', ''),  
                calories=data.get('calories', 0),
                nutriments=data.get('nutriments', {}),
                day=data.get('day', ''),
                link=data.get('link', ''),
                source=data.get('source', ''),
                user_id = data['user_id']
            )

            db.session.add(new_recipe)
            db.session.commit()
            
            return {
                'message': 'Recipe created successfully',
                'recipe_id': new_recipe.recipe_id,
                'title': new_recipe.title
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
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'ner': recipe.ner,
            'type': recipe.type,
            'calories': recipe.calories,
            'nutriments': recipe.nutriments or {},
            'day': recipe.day,
            'link': recipe.link,
            'source': recipe.source,
            'user_id': recipe.user_id
        }

    @api.doc('update_recipe')
    @api.expect(recipe_model)
    @api.response(404, 'Recipe not found')
    def put(self, recipe_id):
        """Update a recipe"""
        try:
            recipe = Recipe.query.get_or_404(recipe_id)
            data = api.payload
            
            # Update required fields if provided
            if 'title' in data:
                recipe.title = data['title']
            if 'ingredients' in data:
                recipe.ingredients = data['ingredients']
            if 'instructions' in data:
                recipe.instructions = data['instructions']
            
            # Update optional fields
            recipe.ner = data.get('ner', recipe.ner)
            recipe.type = data.get('type', recipe.type)
            recipe.calories = data.get('calories', recipe.calories)
            recipe.nutriments = data.get('nutriments', recipe.nutriments)
            recipe.day = data.get('day', recipe.day)
            recipe.link = data.get('link', recipe.link)
            recipe.source = data.get('source', recipe.source)
            
            # Validate day if provided
            if 'day' in data and data['day'] not in [None, '']:
                if data['day'] not in ['Monday', 'Tuesday', 'Wednesday', 
                                    'Thursday', 'Friday', 'Saturday', 'Sunday']:
                    return {'message': 'Invalid day value'}, 400
            
            db.session.commit()
            return {
                'message': 'Recipe updated successfully',
                'recipe_id': recipe.recipe_id
            }
        
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
        
@api.route('/user/<int:user_id>')
class UserRecipesResource(Resource):
    @api.doc('get_user_recipes')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get all recipes for a specific user"""
        # Verify user exists
        user = User.query.get_or_404(user_id)
        
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        
        return [{
            'recipe_id': recipe.recipe_id,
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'ner': recipe.ner,
            'type': recipe.type,
            'calories': recipe.calories,
            'nutriments': recipe.nutriments or {},
            'day': recipe.day,
            'link': recipe.link,
            'source': recipe.source,
            'user_id': recipe.user_id,
            'created_at': recipe.created_at.isoformat() if recipe.created_at else None
        } for recipe in recipes]
      
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
            # === Test 1: Create basic recipe ===
            create_payload = {
                "title": "Pasta Test",
                "ingredients": ["300g pasta", "2 tomatoes", "1 clove garlic"],
                "instructions": [
                    "Boil water",
                    "Cook pasta",
                    "Prepare sauce"
                ],
                "type": "Main Course",
                "calories": 500,
                "nutriments": {
                    "lipide": 10,
                    "glucide": 80,
                    "proteine": 15,
                    "fibre": 5
                },
                "day": "Monday",
                "ner": ["pasta", "tomatoes", "garlic"],
                "user_id": 1
            }

            with current_app.test_request_context(json=create_payload):
                response = RecipeList().post()
                recipe_obj, status_code = unpack_response(response)
                print(recipe_obj)
                recipe_id = recipe_obj['recipe_id']
                results.append(f"✅ Recipe created with ID: {recipe_id}")

            # === Test 2: Get recipe and verify fields ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Failed to fetch by recipe_id")
                if data['title'] != "Pasta Test":
                    raise Exception("Incorrect data retrieved")
                if data['type'] != "Main Course":
                    raise Exception("Type not saved correctly")
                results.append(f"✅ Recipe retrieved: {data['title']}")

            # === Test 3: Update recipe ===
            update_payload = {
                "title": "Updated Pasta",
                "ingredients": ["400g pasta", "3 tomatoes", "2 cloves garlic", "some basil"],
                "instructions": [
                    "Boil salted water",
                    "Cook pasta al dente",
                    "Prepare tomato sauce"
                ],
                "type": "Italian",
                "calories": 600,
                "nutriments": {
                    "lipide": 12,
                    "glucide": 90,
                    "proteine": 18,
                    "fibre": 6
                },
                "day": "Tuesday",
                "source": "Family Recipe"
            }

            with current_app.test_request_context(json=update_payload):
                response = RecipeResource().put(recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Update failed")
                results.append("✅ Recipe updated successfully")

            # === Test 4: Verify update ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                updated, _ = unpack_response(response)
                if updated['day'] != "Tuesday":
                    raise Exception("Day update failed")
                if updated['source'] != "Family Recipe":
                    raise Exception("Source update failed")
                results.append("✅ Update verified")

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