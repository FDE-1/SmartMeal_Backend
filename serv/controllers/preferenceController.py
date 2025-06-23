from flask_restx import abort
from flask import request
from serv.services.preferenceService import create_preference_in_db, update_preference, get_preference_by_user, delete_preference

def handle_preference_creation():
    """Validates and processes preference creation"""
    data = request.get_json()
    if not data:
        abort(400, 'Pas de donnée reçu')
    if 'user_id' not in data:
        abort(400, 'user_id non reçu')
    
    try:
        new_preference = create_preference_in_db(data)
        return {
            'message': 'Préférence créée',
            'preference_id': new_preference.preference_id
        }
    except Exception as e:
        abort(500, f"Erreur serveur: {str(e)}")

def handle_get_preference(user_id):
    """Handles preference retrieval"""
    if not user_id:
        abort(400, 'Paramètre user_id manquant')
    
    preference = get_preference_by_user(user_id)
    if not preference:
        abort(404, 'Préférence non trouvée')
    
    return {
        'preference_id': preference.preference_id,
        'user_id': preference.user_id,
        'allergy': preference.allergy,
        'diet': preference.diet,
        'goal': preference.goal,
        'new': preference.new,
        'number_of_meals': preference.number_of_meals,
        'grocery_day': preference.grocery_day,
        'language': preference.language
    }

def handle_update_preference():
    """Handles preference update"""    
    data = request.get_json()

    if not data:
        abort(400, 'Aucune donnée reçue')
    if 'user_id' not in data:
        abort(400, 'user_id est requis')
    
    updated_preference = update_preference(
        data['user_id'],
        data
    )
    if not updated_preference:
        abort(404, 'Préférence non trouvée')
    
    return {
        'message': 'Préférence mise à jour',
        'preference_id': updated_preference.preference_id,
        'user_id': updated_preference.user_id,
        'allergy': updated_preference.allergy,
        'updated_fields': list(data.keys())
    }

def handle_delete_preference(user_id):
    """Handles preference deletion"""
    if not delete_preference(user_id):
        abort(404, 'Préférence non trouvée')
    return {'message': 'Preference deleted'}