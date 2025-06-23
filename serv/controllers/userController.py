from services.userService import get_all_users_service, create_user_service, get_user_service, delete_user_service, get_user_by_uid_service, update_user_info
from services.firebaseService import delete_firebase_user, create_firebase_user, authenticate_firebase_user, resend_verification_email, refresh_firebase_token, send_password_reset_email
from flask import request
from flask_restx import abort
from firebase_admin import auth

def get_all_users():
    users = get_all_users_service()
    return users, 200

def create_user():
    data = request.get_json()
    if not data:
        abort(400, message="Aucune donnée reçue", error_type="ControllerError")

    required_fields = ['user_name', 'user_email', 'user_password']
    if not all(field in data for field in required_fields):
        abort(400, message="Champs requis manquants", error_type="ControllerError")

    firebase_user = create_firebase_user(data.get('user_email'), data.get('user_password'))
    user = create_user_service(data, firebase_user[0])
    return user, 201

def get_user(user_id):
    if not user_id:
        abort(400, message="Pas de id donné", error_type="ControllerError")
    user = get_user_service(user_id)
    if not user:
        abort(404, message="Utilisateur non trouvé", error_type="ControllerError")
    return user, 200
   

def delete_user(user_id):
    user = get_user_service(user_id)
    if not user:
        abort(404, message="Utilisateur non trouvé", error_type="ControllerError")
    delete_firebase_user(user.firebase_uid)
   
    delete_user_service(user)
    return {'message': f'Utilisateur {user_id} supprimé'}, 200

def login_user():
    data = request.get_json()
    if not all(key in data for key in ['email', 'password']):
        abort(400, "Email et mot de passe requis")

    firebase_uid, _ = authenticate_firebase_user(data['email'], data['password'])
    user = get_user_by_uid_service(firebase_uid)
    if not user:
        abort(404, "Utilisateur non trouvé")

    return {
        'user_id': user.user_id,
        'user_name': user.user_name,
        'user_surname': user.user_surname,
        'user_email': user.user_email
    }

def handle_resend_verification():
    """Controller for verification email flow"""
    data = request.get_json()
    if 'idToken' not in data:
        abort(400, "Jeton ID requis")
    
    try:
        email = resend_verification_email(data['idToken'])
        return {
            "message": f"Email de vérification renvoyé à {email}",
            "email": email
        }
    except auth.InvalidIdTokenError:
        abort(401, "Jeton d'authentification invalide")

def handle_token_refresh():
    """Controller for token refresh flow"""
    data = request.get_json()
    if 'refresh_token' not in data:
        abort(400, "Jeton de rafraîchissement requis")

    try:
        return refresh_firebase_token(data['refresh_token'])
    except auth.RevokedIdTokenError:
        abort(401, "Jeton révoqué")

def handle_password_reset_request():
    """Controller for password reset flow"""
    data = request.get_json()
    if 'email' not in data:
        abort(400, "Email requis")
    
    try:
        email = send_password_reset_email(data['email'])
        return {
            "message": f"Email de réinitialisation envoyé à {email}",
            "email": email
        }
    except Exception as e:
        abort(500, "Erreur lors de l'envoi de l'email")

def handle_user_info_update(user_id):
    """Controller for user info updates"""
    data = request.get_json()

    if 'old_password' not in data:
        abort(400, "Informations manquantes")
    
    update_data = {
        'new_name': data.get('new_name'),
        'new_surname': data.get('new_surname'),
        'new_email': data.get('new_email'),
        'new_password': data.get('new_password')
    }
    
    update_user_info(user_id, update_data, data['old_password'])
    return {'message': 'Informations mises à jour'}