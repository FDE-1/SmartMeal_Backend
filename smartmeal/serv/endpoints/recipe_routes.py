from flask import jsonify, request
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
        data = request.json
        new_recipe = Recipe(
            recipe_name=data['recipe_name'],
            recipe_ingredients=data['recipe_ingredients'],
            recipe_instructions=data['recipe_instructions'],
            recipe_preparation_time=data['recipe_preparation_time'],
            recipe_ustensils_required=data['recipe_ustensils_required'],
            recipe_nutritional_value=data['recipe_nutritional_value']
        )
        db.session.add(new_recipe)
        db.session.commit()
        return {'message': 'Recipe added successfully'}, 201