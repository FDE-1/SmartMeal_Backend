from flask_restx import Namespace, Resource
from loaders.api import api
from controllers.user_recipeController import list_all_user_recipes, handle_user_recipe_creation, get_user_recipes_data, get_user_recipe_details, handle_user_recipe_update, handle_user_recipe_deletion
from models.input.user_recipe.user_recipe_model import user_recipe_model

user_reciperoute = Namespace('user_recipes', description='User recipe personalization operations')


@user_reciperoute.route('/')
class UserRecipeList(Resource):
    @user_reciperoute.doc('list_user_recipes')
    def get(self):
        """List all user recipes"""
        return list_all_user_recipes()
    
    @user_reciperoute.doc('create_user_recipe')
    @user_reciperoute.expect(user_recipe_model)
    def post(self):
        """Create a new user recipe"""
        return handle_user_recipe_creation()

@user_reciperoute.route('/user/<int:user_id>')
class UserRecipeByUser(Resource):
    @user_reciperoute.doc('get_user_recipes_by_user')
    def get(self, user_id):
        """Get all recipes for a specific user"""
        return get_user_recipes_data(user_id)

@user_reciperoute.route('/<int:user_recipes_id>')
class UserRecipeResource(Resource):
    @user_reciperoute.doc('get_user_recipe')
    @user_reciperoute.response(404, 'User recipe not found')
    def get(self, user_recipes_id):
        """Get a specific user recipe by ID"""
        return get_user_recipe_details(user_recipes_id)

    @user_reciperoute.doc('update_user_recipe')
    @user_reciperoute.expect(user_recipe_model)
    @user_reciperoute.response(404, 'User recipe not found')
    def put(self, user_recipes_id):
        """Update a user recipe"""
        return handle_user_recipe_update(user_recipes_id)
    
    @user_reciperoute.doc('delete_user_recipe')
    @user_reciperoute.response(404, 'User recipe not found')
    def delete(self, user_recipes_id):
        """Delete a user recipe"""
        return handle_user_recipe_deletion(user_recipes_id)