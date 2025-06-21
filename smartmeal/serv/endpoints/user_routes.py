from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.user import User
from ..models.preferences import Preferences
from ..models.inventory import Inventory
from flask_restx import Namespace, Resource, fields
from sqlalchemy import text
import time
import requests
import os
import logging
from firebase_admin import credentials, auth, initialize_app
from dotenv import load_dotenv
import json
api = Namespace('users', description='Opérations utilisateur')
#print(os.getenv("private_key"))
load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyBAeb4LtWX3lHdiqA6glTHEBxyFRYWU_Zo")

current_dir = os.path.dirname(os.path.abspath(__file__))
firebase_key_path = os.path.join(current_dir, "smartmeal-62b08-firebase-adminsdk-fbsvc-1e493fd71f.json")
with open(firebase_key_path, 'r') as file:
    firebase = json.load(file)

firebase['private_key_id'] = os.getenv('private_key_id')
private_key = os.getenv('private_key')

# Replace literal '\n' with actual newlines
if private_key:
    firebase['private_key'] = private_key.replace('\\n', '\n')
#with open(firebase_key_path, 'w') as file:
    #json.dump(firebase,file)
#print(firebase)

cred = credentials.Certificate(firebase)
initialize_app(cred)

# Modèles Swagger
user_model = api.model('User', {
    'user_id': fields.Integer(readOnly=True, description='Identifiant unique'),
    'user_name': fields.String(required=True, description='Prénom'),
    'user_surname': fields.String(required=True, description='Nom'),
    'user_email': fields.String(required=True, description='Email'),
    'user_password': fields.String(required=True, description='Mot de passe'),
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description="email"),
    'password': fields.String(required=True, description="Mot de passe")
})

signup_model = api.model('Signup', {
    'user_name': fields.String(required=True, description='Prénom'),
    'user_surname': fields.String(required=True, description='Nom'),
    'email': fields.String(required=True, description="Email"),
    'password': fields.String(required=True, description="Mot de passe")
})

resend_verification_model = api.model('ResendVerification', {
    'idToken': fields.String(required=True, description="Jeton ID Firebase")
})

refresh_token_model = api.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description="Jeton de rafraîchissement")
})

forgot_password_model = api.model('ForgotPassword', {
    'email': fields.String(required=True, description="Email")
})

change_info_model = api.model('ChangeInfo', {
    'new_name': fields.String(description="Nom d'utilisateur"),
    'new_surname': fields.String(description="Nouveau nom"),
    'new_email': fields.String(description="Nouvel email"),
    'old_password': fields.String(required=True, description="Ancien mot de passe"),
    'new_password': fields.String(description="Nouveau mot de passe")
})

test_suite_model = api.model('TestSuite', {
    'test_name': fields.String(description="Nom du test")
})

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        if not decoded_token.get("email_verified", False):
            api.abort(403, "Email not verified. Please verify your email.")
        return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}
    except auth.InvalidIdTokenError:
        api.abort(401, "Invalid authentication token")
    except auth.RevokedIdTokenError:
        api.abort(401, "Token has been revoked")
    except Exception as e:
        api.abort(401, str(e))

@api.route('/')
class UserResource(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    def get(self):
        """Liste tous les utilisateurs"""
        try:
            users = User.query.all()
            return users, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la récupération des utilisateurs", error=str(e))

    @api.doc('create_user')
    @api.expect(user_model)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Crée un nouvel utilisateur"""
        data = api.payload

        if not data:
            api.abort(400, "Aucune donnée reçue")

        required_fields = ['user_name', 'user_email', 'user_password']
        if not all(field in data for field in required_fields):
            api.abort(400, "Champs requis manquants")

        # Vérifier si l'email existe déjà dans Firebase
        try:
            auth.get_user_by_email(data['user_email'])
            api.abort(409, "Email déjà utilisé")
        except auth.UserNotFoundError:
            pass

        try:
            # Créer l'utilisateur dans Firebase
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
            payload = {
                "email": data['user_email'],
                "password": data['user_password'],
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response_data = response.json()
            print(response_data)
            if response.status_code != 200:
                api.abort(400, response_data["error"]["message"])

            id_token = response_data["idToken"]
            uid = response_data["localId"]

            # Envoyer un email de vérification
            verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
            verify_payload = {
                "requestType": "VERIFY_EMAIL",
                "idToken": id_token
            }
            verify_response = requests.post(verify_url, json=verify_payload)
            verify_response_data = verify_response.json()

            if verify_response.status_code != 200:
                api.abort(400, verify_response_data["error"]["message"])

            # Créer l'utilisateur dans SQLAlchemy
            new_user = User(
                user_name=data['user_name'],
                user_surname=data['user_surname'],
                user_email=data['user_email'],
                user_password=data['user_password'],
                firebase_uid=uid 
            )

            db.session.add(new_user)
            db.session.flush()  # Obtenir user_id avant commit

            # Créer les préférences par défaut
            new_preference = Preferences(
                user_id=new_user.user_id,
                allergy={},
                diet='',
                goal='',
                new=1,
                number_of_meals=3,
                grocery_day='Monday',
                language='fr'
            )
            db.session.add(new_preference)

            new_inventory = Inventory(
                user_id=new_user.user_id,
                ustensils=[],
                grocery=[],
                fresh_produce=[]
            )
            db.session.add(new_inventory)

            db.session.commit()
            created_user = User.query.filter_by(firebase_uid=uid).first()
            result = {
            'user_id': created_user.user_id,
            'user_name': created_user.user_name,
            'user_surname': created_user.user_surname,
            'user_email': created_user.user_email,
            'user_password': created_user.user_password
            # Add other fields as per your User model
            }
            return result, 201
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur de création (interne)", error=str(e))


@api.route('/<int:user_id>')
@api.param('user_id', 'ID utilisateur')
class UserDetail(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """Récupère un utilisateur par son ID"""
        user = User.query.get(user_id)
        if not user:
            api.abort(404, "Utilisateur non trouvé")
        return user
    
    @api.doc('delete_user')
    @api.response(200, 'Utilisateur supprimé')
    @api.response(404, 'Utilisateur non trouvé')
    def delete(self, user_id):
        """Supprime un utilisateur par son ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                api.abort(404, "Utilisateur non trouvé")
            
            try:
                auth.delete_user(user.firebase_uid)
            except auth.UserNotFoundError:
                print("user not found in firabase")
            except Exception as e:
                api.abort(500, f"Erreur lors de la suppression dans Firebase: {str(e)}")

            db.session.delete(user)        
            db.session.commit()
            return {'message': f'Utilisateur {user_id} supprimé'}, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la suppression", error=str(e))

@api.route('/login')
class UserLogin(Resource):
    @api.doc('login')
    @api.expect(login_model)
    def post(self):
        """Authentification utilisateur"""
        try:
            data = api.payload
            if not all(key in data for key in ['email', 'password']):
                api.abort(400, "Email et mot de passe requis")

            # Authentifier via Firebase
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {
                "email": data['email'],
                "password": data['password'],
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                error_message = response_data["error"]["message"]
                if error_message == "EMAIL_NOT_FOUND":
                    api.abort(404, "Email non trouvé")
                elif error_message == "INVALID_PASSWORD":
                    api.abort(401, "Mot de passe incorrect")
                api.abort(400, error_message)
            
            id_token = response_data["idToken"]
            decoded_token = auth.verify_id_token(id_token, check_revoked=True)
            if not decoded_token.get("email_verified", False):
                api.abort(403, "Email non vérifié. Veuillez vérifier votre email.")
            firebase_uid = decoded_token["uid"]

            user = User.query.filter_by(firebase_uid=firebase_uid).first()
            if not user:
                api.abort(404, "Utilisateur non trouvé dans la base de données")

            result = {
            'user_id': user.user_id,
            'user_name': user.user_name,
            'user_surname': user.user_surname,
            'user_email': user.user_email,
            'user_password': user.user_password
            # Add other fields as per your User model
            }
            return result, 200
        except Exception as e:
            api.abort(500, "Erreur d'authentification", error=str(e))

@api.route('/resend-verification')
class ResendVerification(Resource):
    @api.doc('resend_verification')
    @api.expect(resend_verification_model)
    def post(self):
        """Renvoyer l'email de vérification"""
        try:
            data = api.payload
            if 'idToken' not in data:
                api.abort(400, "Jeton ID requis")

            decoded_token = auth.verify_id_token(data['idToken'])
            if decoded_token.get("email_verified", False):
                api.abort(400, "Email déjà vérifié")

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
            payload = {
                "requestType": "VERIFY_EMAIL",
                "idToken": data['idToken']
            }
            response = requests.post(url, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                api.abort(400, response_data["error"]["message"])

            return {"message": f"Email de vérification renvoyé à {decoded_token.get('email')}"}, 200
        except auth.InvalidIdTokenError:
            api.abort(401, "Jeton d'authentification invalide")
        except Exception as e:
            api.abort(500, "Erreur lors de l'envoi de l'email", error=str(e))

@api.route('/refresh-token')
class RefreshToken(Resource):
    @api.doc('refresh_token')
    @api.expect(refresh_token_model)
    def post(self):
        """Rafraîchir le jeton Firebase"""
        try:
            data = api.payload
            if 'refresh_token' not in data:
                api.abort(400, "Jeton de rafraîchissement requis")

            url = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}"
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": data['refresh_token']
            }
            response = requests.post(url, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                api.abort(400, response_data["error"]["message"])

            id_token = response_data["id_token"]
            decoded_token = auth.verify_id_token(id_token, check_revoked=True)
            if not decoded_token.get("email_verified", False):
                api.abort(403, "Email non vérifié. Veuillez vérifier votre email.")

            return {
                "idToken": id_token,
                "refreshToken": response_data["refresh_token"]
            }, 200
        except auth.RevokedIdTokenError:
            api.abort(401, "Jeton révoqué")
        except Exception as e:
            api.abort(500, "Erreur lors du rafraîchissement du jeton", error=str(e))


@api.route('/forgot-password')
class ForgotPassword(Resource):
    @api.doc('forgot_password')
    @api.expect(forgot_password_model)
    def post(self):
        """Envoyer un email de réinitialisation de mot de passe"""
        try:
            data = api.payload
            if 'email' not in data:
                api.abort(400, "Email requis")

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
            payload = {
                "requestType": "PASSWORD_RESET",
                "email": data['email']
            }
            response = requests.post(url, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                error_message = response_data["error"]["message"]
                if error_message == "EMAIL_NOT_FOUND":
                    api.abort(404, "Email non trouvé")
                api.abort(400, error_message)

            return {"message": f"Email de réinitialisation envoyé à {data['email']}"}, 200
        except Exception as e:
            api.abort(500, "Erreur lors de l'envoi de l'email", error=str(e))

@api.route('/change-info/<int:user_id>')
class UserChangeInfo(Resource):
    @api.doc('change_info')
    @api.expect(change_info_model)
    def put(self, user_id):
        """Modifie les informations utilisateur"""
        try:
            data = api.payload
            if not all(key in data for key in ['old_password']):
                api.abort(400, "Informations manquantes")
            
            user = User.query.get(user_id)
            if not user:
                api.abort(404, "Utilisateur non trouvé")
            
            if user.user_password!= data['old_password']:
                api.abort(401, "Mot de passe incorrect")
            if 'new_name' in data:
                user.user_name = data['new_name']
            if 'new_surname' in data:
                user.user_surname = data['new_surname']
            if 'new_email' in data:
                user.user_email = data['new_email']
            if 'new_password' in data:
                user.user_password = data['new_password']
            
            db.session.commit()
            return {'message': 'Informations mises à jour'}, 200
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur de mise à jour", error=str(e))


@api.route('/testsuite')
class UserTestSuite(Resource):
    
    @api.doc('run_test_suite')
    @api.response(200, 'Succès')
    @api.response(500, 'Erreur du serveur')
    def post(self):
        """Exécute une suite de tests complète en appelant les autres ressources"""
        résultats = []
        user_id = None

        def unpack_response(resp):
            """Permet de gérer les retours tuple ou simple objet"""
            if isinstance(resp, tuple):
                time.sleep(0.2)
                return resp[0], resp[1]
            return resp, 200
        try:
            # === Données de test ===
            test_user = {
                'user_name': 'test_user',
                'user_surname': 'test_surname',
                'user_email': 'test@example.com',
                'password': 'testpassword123'
            }

            login_payload = {
                'name': test_user['user_name'],
                'password': test_user['password']
            }

            update_payload = {
                'new_name': test_user['user_name'],
                'new_surname': 'updated_surname',
                'new_email': 'updated@example.com',
                'old_password': test_user['password'],
                'new_password': 'newpassword123'
            }

            # === Test 1: Création utilisateur (ou récupération si déjà existant) ===
            with current_app.test_request_context(json=test_user):
                try:
                    response = UserResource().post()
                    user_obj, _ = unpack_response(response)
                    user_id = (
                        user_obj.user_id if hasattr(user_obj, 'user_id')
                        else user_obj['user_id']
                    )
                    résultats.append(f"✅ Utilisateur créé avec ID : {user_id}")
                except Exception as e:
                    user = User.query.filter_by(user_email=test_user['user_email']).first()
                    user_id = user.user_id
                    résultats.append(f"⚠️ Utilisateur existant détecté, ID récupéré : {user_id} + Exception: {e}")

            # === Test 2: Authentification ===
            with current_app.test_request_context(json=login_payload):
                _, status_code = unpack_response(UserLogin().post())
                if status_code != 200:
                    raise Exception("Échec de l'authentification")
                résultats.append("✅ Authentification réussie")

            # === Test 3: Récupération utilisateur ===
            with current_app.test_request_context():
                user_obj, _ = unpack_response(UserDetail().get(user_id))
                résultats.append(f"✅ Données récupérées : {user_obj}")

            # === Test 4: Mise à jour ===
            with current_app.test_request_context(json=update_payload):
                _, status_code = unpack_response(UserChangeInfo().put(user_id))
                if status_code != 200:
                    raise Exception("Échec de la mise à jour")
                résultats.append("✅ Mise à jour réussie")

            # === Test 5: Vérification de la mise à jour ===
            with current_app.test_request_context():
                updated_user, _ = unpack_response(UserDetail().get(user_id))

                surname = (
                    updated_user.user_surname if hasattr(updated_user, 'user_surname')
                    else updated_user['user_surname']
                )
                email = (
                    updated_user.user_email if hasattr(updated_user, 'user_email')
                    else updated_user['user_email']
                )

                if surname != update_payload['new_surname']:
                    raise Exception("Nom non mis à jour")
                if email != update_payload['new_email']:
                    raise Exception("Email non mis à jour")

                résultats.append("✅ Informations vérifiées après mise à jour")

            # === Test 6: Suppression via API ===
            with current_app.test_request_context():
                _, status_code = unpack_response(UserDetail().delete(user_id))
                if status_code != 200:
                    raise Exception("Échec de la suppression")
                résultats.append("✅ Utilisateur supprimé via l'API")
                
            résultats.append("\n🏁 Tous les tests ont réussi !")
            return {'résultats': résultats}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            résultats.append(f"\n❌ Erreur pendant les tests : {str(e)}")
            return {'résultats': résultats}, 500
