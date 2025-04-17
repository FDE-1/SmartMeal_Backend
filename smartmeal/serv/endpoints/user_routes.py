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

@api.route('/test-suite')
class UserTestSuite(Resource):
    @api.doc('run_test_suite')
    @api.expect(test_suite_model)
    def post(self):
        """Exécute une suite de tests complète"""
        test_results = []
        test_data = {
            'user_name': 'test_user',
            'user_surname': 'test_surname',
            'user_email': 'test@example.com',
            'password': 'test123'
        }
        
        try:
            # 1. Get initial list
            test_results.append("1. Liste initiale des utilisateurs")
            initial_users = User.query.all()
            test_results.append(f"Count: {len(initial_users)}")
            
            # 2. Create test user
            test_results.append("2. Création utilisateur test")
            hashed_pw = test_data['password']
            test_user = User(**{**test_data, 'user_password': hashed_pw})
            db.session.add(test_user)
            db.session.commit()
            test_results.append(f"ID: {test_user.user_id}")
            
            # 3. Verify creation
            test_results.append("3. Vérification création")
            created_user = User.query.get(test_user.user_id)
            if not created_user:
                raise Exception("Échec création utilisateur")
            
            # 4. Cleanup
            test_results.append("4. Nettoyage")
            db.session.delete(created_user)
            db.session.commit()
            
            test_results.append("✅ Tous les tests ont réussi")
            return {'results': test_results}, 200
            
        except Exception as e:
            db.session.rollback()
            test_results.append(f"❌ Échec: {str(e)}")
            return {'results': test_results}, 500