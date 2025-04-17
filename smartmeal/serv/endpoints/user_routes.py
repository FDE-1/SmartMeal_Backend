from flask import jsonify, request
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
        """Exécute une suite de tests complète en utilisant les endpoints existants"""
        from .user_routes import UserResource, UserDetail, UserChangeInfo 
        résultats = []
        test_data = {
            'name': 'test_user',
            'surname': 'test_surname',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        update_data = {
            'name': 'test_user',
            'new_surname': 'updated_surname',
            'new_email': 'updated@example.com',
            'old_password': 'testpassword123',
            'new_password': 'newpassword123'
        }

        try:
            # 1. Test get_list()
            résultats.append("=== Test 1: Récupération liste utilisateurs ===")
            users = self.get_list()[0].json
            résultats.append(f"Nombre d'utilisateurs initiaux: {len(users)}")

            # 2. Test create_user()
            résultats.append("\n=== Test 2: Création utilisateur ===")
            with api.test_request_context():
                api.payload = test_data
                response = self.create_user()
                if response[1] != 201:
                    raise Exception(f"Échec création: {response[0].json}")
                
                user_id = response[0].json['user_id']
                résultats.append(f"✅ Utilisateur créé (ID: {user_id})")

            # 3. Test get_info()
            résultats.append("\n=== Test 3: Récupération infos utilisateur ===")
            with api.test_request_context():
                api.payload = {'id': user_id}
                response = self.get_info()
                if response[1] != 200:
                    raise Exception(f"Échec récupération: {response[0].json}")
                résultats.append(f"✅ Infos utilisateur: {response[0].json}")

            # 4. Test change_info()
            résultats.append("\n=== Test 4: Mise à jour infos ===")
            with api.test_request_context():
                api.payload = update_data
                response = self.change_info()
                if response[1] != 200:
                    raise Exception(f"Échec mise à jour: {response[0].json}")
                résultats.append("✅ Mise à jour réussie")

            # 5. Vérification des modifications
            résultats.append("\n=== Test 5: Vérification modifications ===")
            with api.test_request_context():
                api.payload = {'id': user_id}
                updated_user = self.get_info()[0].json
                if updated_user['surname'] != update_data['new_surname']:
                    raise Exception("Surnom non mis à jour")
                résultats.append("✅ Modifications vérifiées")

            # 6. Test delete_user()
            résultats.append("\n=== Test 6: Suppression utilisateur ===")
            with api.test_request_context():
                api.payload = {
                    'name': 'test_user',
                    'password': update_data['new_password']
                }
                response = self.delete_user()
                if response[1] != 200:
                    raise Exception(f"Échec suppression: {response[0].json}")
                résultats.append("✅ Utilisateur supprimé")

            # 7. Vérification finale
            résultats.append("\n=== Test 7: Vérification finale ===")
            final_users = self.get_list()[0].json
            if any(u['user_id'] == user_id for u in final_users):
                raise Exception("Utilisateur toujours présent")
            résultats.append(f"✅ Vérification finale OK - Nombre utilisateurs: {len(final_users)}")

            résultats.append("\n🏁 Tous les tests ont réussi !")
            return {'résultats': résultats}, 200

        except Exception as e:
            db.session.rollback()
            résultats.append(f"\n❌ Échec du test: {str(e)}")
            return {'résultats': résultats}, 500