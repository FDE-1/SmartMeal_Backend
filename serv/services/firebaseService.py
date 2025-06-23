import requests
from firebase_admin import auth
from flask_restx import abort

FIREBASE_API_KEY = "AIzaSyBAeb4LtWX3lHdiqA6glTHEBxyFRYWU_Zo"

def create_firebase_user(email, password):
    if not email or not isinstance(email, str):
        abort(400, message="L'email doit être une chaîne non vide", error_type="FirebaseError")
    if not password or not isinstance(password, str):
        abort(400, message="Le mot de passe doit être une chaîne non vide", error_type="FirebaseError")

    try:
        auth.get_user_by_email(email)
        abort(409, message="Email déjà utilisé", error_type="FirebaseError")
    except auth.UserNotFoundError:
        pass

    try:
        # Create user via REST API
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", "Erreur Firebase inconnue")
            abort(400, message=f"Erreur Firebase : {error_msg}", error_type="FirebaseError")

        uid = data["localId"]
        id_token = data["idToken"]

        # Send verification email
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
        verify_payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        verify_response = requests.post(verify_url, json=verify_payload)
        verify_data = verify_response.json()

        if verify_response.status_code != 200:
            abort(400, message=verify_data.get("error", {}).get("message", "Erreur lors de l'envoi de l'email"), error_type="FirebaseError")

        return uid, id_token
    except Exception as e:
        abort(500, message=f"Erreur Firebase : {str(e)}", error_type="FirebaseError")

def delete_firebase_user(firebase_uid):
    try:
        auth.delete_user(firebase_uid)
    except auth.UserNotFoundError:
        abort(409, message="Utilisateur non trouvé", error_type="FirebaseError")
    except Exception as e:
        abort(500, message=f"Erreur lors de la suppression dans Firebase: {str(e)}", error_type="FirebaseError")

def authenticate_firebase_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if response.status_code != 200:
        error_message = response_data["error"]["message"]
        if error_message == "EMAIL_NOT_FOUND":
            abort(404, "Email non trouvé")
        elif error_message == "INVALID_PASSWORD":
            abort(401, "Mot de passe incorrect")
        abort(400, error_message)
    
    id_token = response_data["idToken"]
    decoded_token = auth.verify_id_token(id_token, check_revoked=True)
    if not decoded_token.get("email_verified", False):
        abort(403, "Email non vérifié")
    
    return decoded_token["uid"], id_token

def resend_verification_email(id_token):
    """Handles Firebase verification email resend"""
    decoded_token = auth.verify_id_token(id_token)
    if decoded_token.get("email_verified", False):
        abort(400, "Email déjà vérifié")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    }
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        abort(400, response.json()["error"]["message"])
    
    return decoded_token.get('email')

def refresh_firebase_token(refresh_token):
    """Handles Firebase token refresh"""
    url = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if response.status_code != 200:
        abort(400, response_data["error"]["message"])

    id_token = response_data["id_token"]
    decoded_token = auth.verify_id_token(id_token, check_revoked=True)
    
    if not decoded_token.get("email_verified", False):
        abort(403, "Email non vérifié")
    
    return {
        "id_token": id_token,
        "refresh_token": response_data["refresh_token"]
    }

def send_password_reset_email(email):
    """Handles Firebase password reset email"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if response.status_code != 200:
        error_message = response_data["error"]["message"]
        if error_message == "EMAIL_NOT_FOUND":
            abort(404, "Email non trouvé")
        abort(400, error_message)
    
    return email