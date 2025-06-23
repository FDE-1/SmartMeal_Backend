from flask_restx import Namespace, Resource
from serv.loaders.api import api
from serv.controllers.recipeController import list_all_recipes, handle_recipe_creation, get_recipe_details, handle_recipe_update, handle_recipe_deletion, get_user_recipes_data, process_bulk_like, handle_liked_recipes_request
from serv.models.input.recipe.recipe_model import recipe_model
from serv.models.input.recipe.bulk_like_model import bulk_like_model
from serv.models.input.recipe.like_recipe_model import liked_recipe_model
from flask import request
from flask import abort

recipe_route = Namespace('recipes', description='Recipe operations')

@recipe_route.route('/')
class RecipeList(Resource):
    @recipe_route.doc('list_recipes')
    def get(self):
        """List all recipes"""
        return list_all_recipes()

    @recipe_route.doc('create_recipe')
    @recipe_route.expect(recipe_model)
    def post(self):
        """Create a new recipe"""
        return handle_recipe_creation()

@recipe_route.route('/<int:recipe_id>')
class RecipeResource(Resource):
    @recipe_route.doc('get_recipe')
    @recipe_route.response(404, 'Recipe not found')
    def get(self, recipe_id):
        """Get a specific recipe by ID"""
        return get_recipe_details(recipe_id)

    @recipe_route.doc('update_recipe')
    @recipe_route.expect(recipe_model)
    @recipe_route.response(404, 'Recipe not found')
    def put(self, recipe_id):
        """Update a recipe"""
        return handle_recipe_update(recipe_id)

    @recipe_route.doc('delete_recipe')
    @recipe_route.response(404, 'Recipe not found')
    def delete(self, recipe_id):
        """Delete a recipe"""
        return handle_recipe_deletion(recipe_id)
    
@recipe_route.route('/user/<int:user_id>')
class UserRecipesResource(Resource):
    @recipe_route.doc('get_user_recipes')
    @recipe_route.response(404, 'User not found')
    def get(self, user_id):
        """Get all recipes for a specific user"""
        return get_user_recipes_data(user_id)
    
@recipe_route.route('/bulk-like')
class RecipeBulkLike(Resource):
    @recipe_route.doc('bulk_like_recipes')
    @recipe_route.expect(bulk_like_model)
    @recipe_route.response(400, 'Invalid input data')
    @recipe_route.response(404, 'User not found')
    @recipe_route.response(500, 'Server error')
    def post(self):
        """Like multiple recipes or create and like if they don't exist"""
        return process_bulk_like()
    
@recipe_route.route('/liked')
class RecipeLikedList(Resource):
    @recipe_route.doc('get_liked_recipes')
    @recipe_route.response(200, 'Success', [liked_recipe_model])
    @recipe_route.response(400, 'Invalid user_id')
    @recipe_route.response(404, 'User not found')
    @recipe_route.param('user_id', 'The ID of the user', type=int, required=True)
    def get(self):
        """Get all recipes liked by a user"""
        user_id = request.args.get('user_id')
        return handle_liked_recipes_request(user_id)