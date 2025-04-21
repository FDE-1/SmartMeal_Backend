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
    'recipe_nutritional_value': fields.Raw(required=True)
})

@api.route('/')
class RecipeList(Resource):
    @api.doc('list_recipes')
    def get(self):
        """List all recipes"""
        recipes = Recipe.query.all()
        return jsonify([{'recipe_id': r.recipe_id, 'name': r.recipe_name} for r in recipes])

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
                'recipe_preparation_time'
            ]
            
            if not all(field in data for field in required_fields):
                missing = [field for field in required_fields if field not in data]
                return {
                    'message': 'Missing required fields',
                    'missing_fields': missing
                }, 400

            new_recipe = Recipe(
                recipe_name=data['recipe_name'],
                recipe_ingredients=data['recipe_ingredients'],
                recipe_instructions=data['recipe_instructions'],
                recipe_preparation_time=data['recipe_preparation_time'],
                recipe_ustensils_required=data.get('recipe_ustensils_required', []),
                recipe_nutritional_value=data.get('recipe_nutritional_value', {})
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
            'recipe_nutritional_value': recipe.recipe_nutritional_value
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
    @api.response(200, 'Succès')
    @api.response(500, 'Erreur du serveur')
    def post(self):
        """Exécute une suite de tests complète pour les recettes"""
        résultats = []
        recipe_id = None
        test_user_id = 4  # ID spécial pour les tests

        def unpack_response(resp):
            """Gère les tuples de Flask RESTx"""
            if isinstance(resp, tuple):
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Création d'une recette ===
            create_payload = {
                "recipe_name": "Pâtes Test",
                "recipe_ingredients": {
                    "pâtes": "300g",
                    "tomates": "2",
                    "ail": "1 gousse"
                },
                "recipe_instructions": [
                    "Faire bouillir l'eau",
                    "Cuire les pâtes",
                    "Préparer la sauce"
                ],
                "recipe_preparation_time": 20,
                "recipe_ustensils_required": ["casserole", "spatule"],
                "recipe_nutritional_value": {
                    "calories": 500,
                    "protéines": "15g"
                }
            }

            with current_app.test_request_context(json=create_payload):
                response = RecipeList().post()
                recipe_obj, status_code = unpack_response(response)
                print(recipe_id)
                print(status_code)
                recipe_id = recipe_obj['recipe_id']
                résultats.append(f"✅ Recette créée avec ID : {recipe_id}")

            # === Test 2: Récupération par recipe_id ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de récupération par recipe_id")
                if data['recipe_name'] != "Pâtes Test":
                    raise Exception("Données incorrectes récupérées")
                résultats.append(f"✅ Recette récupérée : {data['recipe_name']}")

            # === Test 3: Mise à jour complète ===
            update_payload = {
                "recipe_name": "Pâtes Modifiées",
                "recipe_ingredients": {
                    "pâtes": "400g",
                    "tomates": "3",
                    "ail": "2 gousses",
                    "basilic": "quelques feuilles"
                },
                "recipe_instructions": [
                    "Faire bouillir l'eau salée",
                    "Cuire les pâtes al dente",
                    "Préparer la sauce tomate"
                ],
                "recipe_preparation_time": 25,
                "recipe_ustensils_required": ["casserole", "spatule", "mixeur"],
                "recipe_nutritional_value": {
                    "calories": 600,
                    "protéines": "18g"
                }
            }

            with current_app.test_request_context(json=update_payload):
                response = RecipeResource().put(recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de la mise à jour")
                résultats.append("✅ Mise à jour complète effectuée")

            # === Test 4: Vérification des modifications ===
            with current_app.test_request_context():
                response = RecipeResource().get(recipe_id)
                updated, _ = unpack_response(response)
                if updated['recipe_name'] != "Pâtes Modifiées":
                    raise Exception("Échec de mise à jour du nom")
                if updated['recipe_preparation_time'] != 25:
                    raise Exception("Échec de mise à jour du temps")
                if "basilic" not in updated['recipe_ingredients']:
                    raise Exception("Échec d'ajout d'ingrédient")
                résultats.append("✅ Modifications vérifiées")

            # === Test 5: Suppression ===
            with current_app.test_request_context():
                response = RecipeResource().delete(recipe_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de suppression")
                résultats.append("✅ Recette supprimée avec succès")

            # Vérification finale
            deleted_recipe = Recipe.query.get(recipe_id)
            if deleted_recipe:
                raise Exception("La suppression n'a pas fonctionné")

            résultats.append("\n🏁 Tous les tests des recettes sont passés avec succès !")
            return {'résultats': résultats}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            # Nettoyage si échec
            if recipe_id:
                recipe = Recipe.query.get(recipe_id)
                if recipe:
                    db.session.delete(recipe)
                    db.session.commit()
            
            résultats.append(f"\n❌ Erreur pendant les tests : {str(e)}")
            return {'résultats': résultats}, 500