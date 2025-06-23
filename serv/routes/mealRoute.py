from flask_restx import Namespace, Resource
from loaders.api import api
from controllers.mealController import generate_meal_plan, handle_shopping_list_request
from models.input.meal.user_id_model import user_id_model
from models.input.meal.shopping_list import shopping_list_input
from flask import request
from flask import abort

meal_route = Namespace('tenserflow', description='Test TenserFlow')

@meal_route.route('/meal_plan_user_id')
class OptimizedPreferencesMealPlan(Resource):
    @meal_route.doc('meal_plan_user_id')
    @meal_route.expect(user_id_model)
    def post(self):
        """Generate optimized meal plan"""
        data = request.get_json()
        user_id = data.get('user_id')
        return generate_meal_plan(user_id)
    
@meal_route.route('/shopping')
class ShoppingListUserId(Resource):
    @meal_route.expect(shopping_list_input, validate=True)
    @meal_route.doc('shopping_list_user_id')
    def post(self):
        """Generate shopping list from meal plan"""
        return handle_shopping_list_request()