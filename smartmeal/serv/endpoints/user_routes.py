from flask import jsonify, request
from ..connection.loader import db
from ..models.user import User
from flask_restx import Namespace, Resource, fields

api = Namespace('users', description='User operations')

@api.route('/')
class UserList(Resource):

    @api.doc('list_users', method=['GET'])
    def get_list(self):
        """Renvoie une liste de tous les utilsateurs"""
        try:
            users = User.query.all()
            return jsonify([{'user_id': u.user_id, 'name': u.user_name, 'email': u.user_email} for u in users])
        except Exception as e:
            db.session.rollback()
            return {
                'message': "Erreur lors de la récupération de tous les utilisateur",
                'error': str(e)
            }, 500

    info_model = api.model('User', {
        'id': fields.String(required=True, description="Id de l'utilisateur")
    })
    @api.doc('get_info', method=['Get'])
    def get_info(self):
        try:
            data = api.payload

            id = data['id']
            if not id:
                return {'message': "Manque d'information"}, 400
            
            user = User.query.filter_by(user_id=id).first()
            if not user:
                return {'message': f"Aucun utilisateur avec l'id {id} existe"}, 404
            
            if user.user_id != id:
                return {'message': "Mot de passe incorrect"}, 401
            
            return  {user}, 200
        except Exception as e:
                    db.session.rollback()
                    return {
                        'message': "Erreur lors de la récupération des informations de d'utilisateur",
                        'error': str(e)
                    }, 500

    user_model = api.model('User', {
        'name': fields.String(required=True, description="Nom de l'utilisateur"),
        'surname': fields.String(required=True, description = "Surnom"),
        'email': fields.String(required=True, description= "email"),
        'password': fields.String(required=True, description="Mot de passe")
    })
    @api.doc('create_user', method=['POST'])
    @api.expect(user_model)
    def create_user(self):
        """Crée un nouvel utilisateur"""
        try:
            data = api.payload
            
            if not data:
                return {'message': 'Aucune information reçue'}, 400

            required_fields = ['name', 'surname', 'email', 'password']
            if not all(field in data for field in required_fields):
                return {'message': 'Manque des informations'}, 400

            if User.query.filter_by(user_email=data['email']).first():
                return {'message': 'Email est déjà utilisé par un autre utilisateur'}, 409

            new_user = User(
                user_name=data['name'],
                user_surname=data['surname'],
                user_email=data['email'],
                user_password=data['password']
            )

            db.session.add(new_user)
            db.session.commit()
            
            return {
                'message': 'Utilisateur crée',
                'user_id': new_user.user_id
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                'message': "Erreur lors de la création d'utilisateur",
                'error': str(e)
            }, 500
        
    
    login_model = api.model('login', {
        'name': fields.String(required=True, description="Nom de l'utilisateur"),
        'password': fields.String(required=True, description="Mot de passe"),
    })
    @api.doc('login', method=['POST'])
    @api.expect(login_model)
    def login(self):
        """Identifie l'utilisateur avec son nom et le mot de passe"""
        try:
            data = api.payload
            name = data['name']
            password = data['password']

            if not name or not password:
                return {'message': "Manque d'information"}, 400
            
            user = User.query.filter_by(user_name=name).first()
            if not user:
                return {'message': f"Aucun utilisateur avec le nom {name} existe"}, 404
            
            if user.password != password:
                return {'message': "Mot de passe incorrect"}, 401
            
            return  {'message': 'Successful connection'}, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': "Erreur lors de l'indentification de l'utilisateur",
                'error': str(e)
            }, 500
        
    change_model = api.model('change_password', {
        'name': fields.String(required=True, description="Nom de l'utilisateur"),
        'new_surname': fields.String(required=False, description= "Nouveau Surnom"),
        'new_email' : fields.String(required=False, description="Nouveau email"),
        'old_password' : fields.String(required=True, description="Ancien mot de passe"),
        'new_password' : fields.String(required=False, description="Nouveau mot de passe")
    })
    @api.doc('change_info', method=['PUT'])
    @api.expect(change_model)
    def change_info(self):
        """Change les informations l'utilisateur"""
        try:
            data = api.payload
            name = data['name']
            new_surname = data['new_surname']
            new_email = data['new_email']
            old_password = data['old_password']
            new_password = data['new_password']

            if not name or not old_password:
                return {'message': "Manque d'information"}, 400
            
            user = User.query.filter_by(user_name=name).first()
            if not user:
                return {'message': f"Aucun utilisateur avec le nom {name} existe"}, 404
            
            if user.password != old_password:
                return {'message': "Mot de passe incorrect"}, 401
            
            if new_password:
                user.password = new_password
            if new_surname:
                user.surname =  new_surname
            if new_email:
                user.email = new_email
            db.session.commit()

            return  {'message': 'Information changé avec succès'}, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': "Erreur lors du changement d'information de l'utilisateur",
                'error': str(e)
            }, 500
    
    delete_model = api.model('delete', {
        'name' : fields.String(required=True, description="Nom de l'utilisateur"),
        'password': fields.String(required=True, description="Mot de passe")
    })
    @api.doc("delete", method=['DELETE'])
    def delete_user(self):
        """Supprime l'utilisateur"""
        try:
            data = api.payload
            name = data['name']
            password = data['password']

            if not name or not password:
                return {'message': "Manque d'information"}, 400
            
            user = User.query.filter_by(user_name=name).first()
            if not user:
                return {'message': f"Aucun utilisateur avec le nom {name} existe"}, 404
            
            if user.password != password:
                return {'message': "Mot de passe incorrect"}, 401
            
            db.session.delete(user)
            db.session.commit()

            return  {'message': 'Suppréssion fait avec succès'}, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': "Erreur lors de la supprésion de l'utilisateur",
                'error': str(e)
            }, 500
        

@api.route('/testsuite')
class TestSuite(Resource):
    @api.doc('run_test_suite')
    def post(self):
        """Exécute une suite de tests complète en utilisant les endpoints existants"""
        résultats_tests = []
        données_test = {
            'name': 'utilisateur_test',
            'surname': 'nom_test',
            'email': 'test@exemple.com',
            'password': 'motdepasse123'
        }
        données_maj = {
            'name': 'utilisateur_test',
            'new_surname': 'nom_maj',
            'new_email': 'maj@exemple.com',
            'old_password': 'motdepasse123',
            'new_password': 'nouveaumdp123'
        }

        try:
            # 1. Obtenir la liste initiale des utilisateurs
            résultats_tests.append("1. Récupération de la liste initiale des utilisateurs...")
            réponse_liste = self.get_list()
            utilisateurs_initiaux = réponse_liste[0].json
            résultats_tests.append(f"Utilisateurs initiaux: {[u['user_id'] for u in utilisateurs_initiaux]}")
            if not any(u['user_id'] == id_utilisateur for u in utilisateurs_finaux):
                résultats_tests.append("✅ Utilisateur nom dans le système")
            else:
                raise Exception("L'utilisateur existe au début")

            # 2. Créer un nouvel utilisateur test
            résultats_tests.append("\n2. Création de l'utilisateur test...")
            with api.test_request_context():
                api.payload = données_test
                réponse_création = self.post()
                if réponse_création[1] == 201:
                    id_utilisateur = réponse_création[0].json['user_id']
                    résultats_tests.append(f"✅ Utilisateur créé avec succès (ID: {id_utilisateur})")
                else:
                    raise Exception(f"Échec de la création: {réponse_création[0].json}")

            # 3. Obtenir les infos de l'utilisateur
            résultats_tests.append("\n3. Récupération des informations utilisateur...")
            with api.test_request_context():
                api.payload = {'id': id_utilisateur}
                réponse_infos = self.get_info()
                if réponse_infos[1] == 200:
                    résultats_tests.append(f"✅ Informations utilisateur récupérées: {réponse_infos[0].json}")
                else:
                    raise Exception(f"Échec de la récupération: {réponse_infos[0].json}")

            # 4. Mettre à jour les infos utilisateur
            résultats_tests.append("\n4. Mise à jour des informations utilisateur...")
            with api.test_request_context():
                api.payload = données_maj
                réponse_maj = self.change_info()
                if réponse_maj[1] == 200:
                    résultats_tests.append("✅ Mise à jour réussie")
                else:
                    raise Exception(f"Échec de la mise à jour: {réponse_maj[0].json}")

            # 5. Vérifier les mises à jour
            résultats_tests.append("\n5. Vérification des mises à jour...")
            with api.test_request_context():
                api.payload = {'id': id_utilisateur}
                infos_maj = self.get_info()
                if infos_maj[1] == 200:
                    données_utilisateur = infos_maj[0].json
                    if (données_utilisateur['surname'] == données_maj['new_surname'] and 
                        données_utilisateur['email'] == données_maj['new_email']):
                        résultats_tests.append("✅ Mises à jour vérifiées avec succès")
                    else:
                        raise Exception("Les mises à jour n'ont pas été appliquées correctement")
                else:
                    raise Exception("Échec de la vérification")

            # 6. Supprimer l'utilisateur
            résultats_tests.append("\n6. Suppression de l'utilisateur test...")
            with api.test_request_context():
                api.payload = {
                    'name': 'utilisateur_test',
                    'password': données_maj['new_password']
                }
                réponse_suppression = self.delete_user()
                if réponse_suppression[1] == 200:
                    résultats_tests.append("✅ Utilisateur supprimé avec succès")
                else:
                    raise Exception(f"Échec de la suppression: {réponse_suppression[0].json}")

            # 7. Vérifier la suppression
            résultats_tests.append("\n7. Vérification de la suppression...")
            réponse_liste_finale = self.get_list()
            utilisateurs_finaux = réponse_liste_finale[0].json
            if not any(u['user_id'] == id_utilisateur for u in utilisateurs_finaux):
                résultats_tests.append("✅ Utilisateur correctement supprimé du système")
            else:
                raise Exception("L'utilisateur existe toujours après suppression")

            résultats_tests.append("\n🏁 TOUS LES TESTS ONT RÉUSSI AVEC SUCCÈS")
            return {'résultats': résultats_tests}, 200

        except Exception as e:
            résultats_tests.append(f"\n❌ ÉCHEC DU TEST: {str(e)}")
            return {'résultats': résultats_tests}, 500