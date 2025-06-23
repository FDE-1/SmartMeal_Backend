from flask import Flask
from flask_cors import CORS
from loaders.postgres import init_db, db
from routes.userRoute import user_route
from routes.weekRoute import week_route
from routes.user_recipeRoute import user_reciperoute
from routes.shopping_listRoute import shopping_list_route
from routes.mealRoute import meal_route
from routes.recipe_route import recipe_route
from routes.inventoryRoute import inventory_route
from routes.preferenceRoute import preference_route
from loaders.api import api
from loaders.firebase import firebase_app
from errors.error_handlers import register_error_handlers
app = Flask(__name__)
CORS(app)
init_db(app)

with app.app_context():
    db.create_all()

api.init_app(app)
api.add_namespace(user_route)
api.add_namespace(week_route)
api.add_namespace(user_reciperoute)
api.add_namespace(meal_route)
api.add_namespace(shopping_list_route)
api.add_namespace(recipe_route)
api.add_namespace(inventory_route)
api.add_namespace(preference_route)

register_error_handlers(api)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')