from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.user import User
from flask_restx import Namespace, Resource, fields

api = Namespace('users', description='Opérations utilisateur')

# Modèles Swagger
user_model = api.model('User', {
    'user_id': fields.Integer(readOnly=True, description='Identifiant unique'),
    'user_name': fields.String(required=True, description='Prénom'),
    'user_surname': fields.String(required=True, description='Nom'),
    'user_email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Mot de passe')
})

login_model = api.model('Login', {
    'name': fields.String(required=True, description="Nom d'utilisateur"),
    'password': fields.String(required=True, description="Mot de passe")
})

change_info_model = api.model('ChangeInfo', {
    'name': fields.String(required=True, description="Nom d'utilisateur"),
    'new_surname': fields.String(description="Nouveau nom"),
    'new_email': fields.String(description="Nouvel email"),
    'old_password': fields.String(required=True, description="Ancien mot de passe"),
    'new_password': fields.String(description="Nouveau mot de passe")
})

test_suite_model = api.model('TestSuite', {
    'test_name': fields.String(description="Nom du test")
})

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
        try:
            data = api.payload
            
            if not data:
                api.abort(400, "Aucune donnée reçue")
            
            required_fields = ['user_name', 'user_surname', 'user_email', 'password']
            if not all(field in data for field in required_fields):
                api.abort(400, "Champs requis manquants")
            
            if User.query.filter_by(user_email=data['user_email']).first():
                api.abort(409, "Email déjà utilisé")
            
            new_user = User(
                user_name=data['user_name'],
                user_surname=data['user_surname'],
                user_email=data['user_email'],
                user_password=data['password']
            )
            
            db.session.add(new_user)
            db.session.commit()
            return new_user, 201
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur de création", error=str(e))

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

@api.route('/login')
class UserLogin(Resource):
    @api.doc('login')
    @api.expect(login_model)
    def post(self):
        """Authentification utilisateur"""
        try:
            data = api.payload
            if not all(key in data for key in ['name', 'password']):
                api.abort(400, "Nom et mot de passe requis")
            
            user = User.query.filter_by(user_name=data['name']).first()
            if not user:
                api.abort(404, "Utilisateur non trouvé")
            
            if not user.user_password!= data['password']:
                api.abort(401, "Mot de passe incorrect")
            
            return {'message': 'Authentification réussie'}, 200
            
        except Exception as e:
            api.abort(500, "Erreur d'authentification", error=str(e))

@api.route('/change-info')
class UserChangeInfo(Resource):
    @api.doc('change_info')
    @api.expect(change_info_model)
    def put(self):
        """Modifie les informations utilisateur"""
        try:
            data = api.payload
            if not all(key in data for key in ['name', 'old_password']):
                api.abort(400, "Informations manquantes")
            
            user = User.query.filter_by(user_name=data['name']).first()
            if not user:
                api.abort(404, "Utilisateur non trouvé")
            
            if user.user_password!= data['old_password']:
                api.abort(401, "Mot de passe incorrect")
            
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
                'name': test_user['user_name'],
                'new_surname': 'updated_surname',
                'new_email': 'updated@example.com',
                'old_password': test_user['password'],
                'new_password': 'newpassword123'
            }

            # === Test 1: Création utilisateur ===
            with current_app.test_request_context(json=test_user):
                response, code = UserResource().post()
                user_id = response.user_id
                résultats.append(f"✅ Utilisateur créé avec ID : {user_id}")

            # === Test 2: Authentification ===
            with current_app.test_request_context(json=login_payload):
                login_response = UserLogin().post()
                résultats.append("✅ Authentification réussie")

            # === Test 3: Récupération utilisateur par ID ===
            with current_app.test_request_context():
                user_data = UserDetail().get(user_id)
                résultats.append(f"✅ Données récupérées : {user_data.user_name} {user_data.user_surname}")

            # === Test 4: Mise à jour des informations ===
            with current_app.test_request_context(json=update_payload):
                change_response = UserChangeInfo().put()
                résultats.append("✅ Mise à jour réussie")

            # === Test 5: Vérification de la mise à jour ===
            with current_app.test_request_context():
                updated_user = UserDetail().get(user_id)
                if updated_user.user_surname != update_payload['new_surname']:
                    raise Exception("Nom non mis à jour")
                if updated_user.user_email != update_payload['new_email']:
                    raise Exception("Email non mis à jour")
                résultats.append("✅ Informations vérifiées après mise à jour")

            # === Nettoyage : suppression directe (pas de route DELETE définie) ===
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                résultats.append("✅ Utilisateur supprimé manuellement")

            résultats.append("\n🏁 Tous les tests ont réussi !")
            return {'résultats': résultats}, 200

        except Exception as e:
            db.session.rollback()
            résultats.append(f"\n❌ Erreur pendant les tests : {str(e)}")
            return {'résultats': résultats}, 500
