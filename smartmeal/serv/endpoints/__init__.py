# Can be empty or used to collect all API routes
from .user_routes import api as user_api
from .recipe_routes import api as recipe_api
from .preferences_routes import api as preferences_api

__all__ = ['user_api', 'recipe_api', 'preferences_api']