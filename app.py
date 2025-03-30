from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from pathlib import Path
import sys

# Temporary path fix - remove after package installation
sys.path.append(str(Path(__file__).parent))

# Import from your package structure
from smartmeal.serv.connection.loader import init_db, db
from smartmeal.serv.endpoints.user_routes import api as user_ns
from smartmeal.serv.endpoints.recipe_routes import api as recipe_ns
from smartmeal.serv.endpoints.preferences_routes import api as preferences_ns
from smartmeal.serv.endpoints.inventory_routes import api as inventory_ns
from smartmeal.serv.endpoints.ia_routes import api as ia

app = Flask(__name__)

# Enable CORS for all origins
CORS(app)  # Allows any fetch request from any origin

# Initialize database
init_db(app)

# Create tables - using the correct db instance from your package
with app.app_context():
    db.create_all()

# Swagger setup
api = Api(
    app,
    title='SmartMeal API',
    version='1.0',
    description='API for SmartMeal application',
    doc='/swagger'
)

# Add namespaces
api.add_namespace(user_ns)
api.add_namespace(recipe_ns)
api.add_namespace(preferences_ns)
api.add_namespace(inventory_ns)
api.add_namespace(ia)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Allow external access