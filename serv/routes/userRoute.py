from flask_restx import Namespace, Resource
from models.input.user.user_model import user_model 
from models.input.user.login_model import login_model
from models.input.user.resend_email_model import resend_email_model
from models.input.user.refresh_model import refresh_token_model
from models.input.user.forgot_password_model import forgot_password_model
from models.input.user.change_model import change_info_model
from controllers.userController import get_all_users, create_user, get_user, delete_user, login_user, handle_resend_verification, handle_token_refresh, handle_password_reset_request, handle_user_info_update
from loaders.api import api

user_route = Namespace('users', description='Opérations liées aux utilisateurs')

@user_route.route('/')
class UserResource(Resource):
    @user_route.doc('list_users')
    @user_route.marshal_list_with(user_model)
    @user_route.response(200, 'Succès')
    @user_route.response(500, 'Erreur serveur')
    def get(self):
        """Liste tous les utilisateurs"""
        return get_all_users()

    @user_route.doc('create_user')
    @user_route.expect(user_model)
    @user_route.marshal_with(user_model, code=201)
    @user_route.response(201, 'Utilisateur créé')
    @user_route.response(400, 'Erreur de validation ou Firebase')
    @user_route.response(409, 'Email déjà utilisé')
    @user_route.response(500, 'Erreur serveur')
    def post(self):
        """Crée un nouvel utilisateur"""
        return create_user()

@user_route.route('/<int:user_id>')
@user_route.param('user_id', 'ID utilisateur')
class UserDetail(Resource):
    @user_route.doc('get_user')
    @user_route.marshal_with(user_model)
    @user_route.response(200, 'Succès')
    @user_route.response(400, 'ID invalide')
    @user_route.response(404, 'Utilisateur non trouvé')
    @user_route.response(500, 'Erreur serveur')
    def get(self, user_id):
        """Récupère un utilisateur par son ID"""
        return get_user(user_id)

    @user_route.doc('delete_user')
    @user_route.response(200, 'Utilisateur supprimé')
    @user_route.response(404, 'Utilisateur non trouvé')
    @user_route.response(500, 'Erreur serveur')
    def delete(self, user_id):
        """Supprime un utilisateur par son ID"""
        return delete_user(user_id)
    
@user_route.route('/login')
class UserLogin(Resource):
    @user_route.doc('login')
    @user_route.expect(login_model)
    def post(self):
        """Authentification utilisateur"""
        return login_user()
    
@user_route.route('/resend-verification')
class ResendVerification(Resource):
    @user_route.doc('resend_verification')
    @user_route.expect(resend_email_model)
    def post(self):
        """Renvoyer l'email de vérification"""
        return handle_resend_verification()

@user_route.route('/refresh-token')
class RefreshToken(Resource):
    @user_route.doc('refresh_token')
    @user_route.expect(refresh_token_model)
    def post(self):
        """Rafraîchir le jeton Firebase"""
        return  handle_token_refresh()
    
@user_route.route('/forgot-password')
class ForgotPassword(Resource):
    @user_route.doc('forgot_password')
    @user_route.expect(forgot_password_model)
    def post(self):
        """Envoyer un email de réinitialisation de mot de passe"""
        return handle_password_reset_request()
    
@user_route.route('/change-info/<int:user_id>')
class UserChangeInfo(Resource):
    @user_route.doc('change_info')
    @user_route.expect(change_info_model)
    def put(self, user_id):
        """Modifie les informations utilisateur"""
        return handle_user_info_update(user_id)
