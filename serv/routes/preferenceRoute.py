from flask_restx import Namespace, Resource
from loaders.api import api
from models.input.preference.preference_model import preference_model
from controllers.preferenceController import handle_preference_creation, handle_get_preference, handle_update_preference, handle_delete_preference
from flask import request
from models.input.preference.preference_id_model import preference_id_model
from models.input.preference.update_model import update_model

preference_route = Namespace('preferences', description='User preferences operations')

@preference_route.route('/')
class PreferenceList(Resource):
    @preference_route.expect(preference_model)
    def post(self):
        """Create a new preference"""
        return handle_preference_creation()
    
@preference_route.route('/id')
class PreferenceById(Resource):
    @preference_route.doc('get_preference')
    @preference_route.doc(params={'user_id': 'ID de l\'utilisateur'})
    def get(self):
        """Récupère les préférences d'un utilisateur"""
        user_id = request.args.get('user_id', type=int)
        return handle_get_preference(user_id)

    @preference_route.expect(update_model)
    def put(self):
        """Met à jour la préférence"""
        return handle_update_preference()

    @preference_route.expect(preference_id_model)
    def delete(self):
        """Supprime la preference"""
        data = preference_route.payload
        return handle_delete_preference(data['user_id'])