from serv.models.database.user_model import User
from serv.models.database.preference_model import Preferences
from serv.models.database.inventory_model import Inventory
from serv.loaders.postgres import db  
from flask_restx import abort

def get_all_users_service():
    try:
        return User.query.all()
    except Exception as e:
        db.session.rollback()
        abort(500, message=f"Erreur dans le service : {str(e)}", error_type="ServiceError")

def create_user_service(data, firebase_uid):
    try:
        new_user = User(
            user_name=data['user_name'],
            user_surname=data.get('user_surname', ''),
            user_email=data['user_email'],
            user_password=data['user_password'],
            firebase_uid=firebase_uid
        )

        db.session.add(new_user)
        db.session.flush()  # To obtain user_id

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

        return {
            'user_id': new_user.user_id,
            'user_name': new_user.user_name,
            'user_surname': new_user.user_surname,
            'user_email': new_user.user_email,
            'user_password': new_user.user_password
        }
    except Exception as e:
        db.session.rollback()
        abort(500, message=f"Erreur de création de l'utilisateur : {str(e)}", error_type="ServiceError")

def get_user_service(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            abort(404, message="Utilisateur non trouvé", error_type="ServiceError")
        return user
    except Exception as e:
        abort(500, message=f"Erreur lors de la récupération de l'utilisateur : {str(e)}", error_type="ServiceError")

def delete_user_service(user):
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, message=f"Erreur lors de la suppression de l'utilisateur : {str(e)}", error_type="ServiceError")

def get_user_by_uid_service(uid):
    try:
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user:
            abort(404, message="Utilisateur non trouvé", error_type="ServiceError")
        return user
    except Exception as e:
        abort(500, message=f"Erreur lors de la récupération de l'utilisateur : {str(e)}", error_type="ServiceError")

def update_user_info(user_id, update_data, old_password):
    """Handles user info updates"""
    user = User.query.get(user_id)
    if not user:
        abort(404, "Utilisateur non trouvé")
    
    if user.user_password != old_password:
        abort(401, "Mot de passe incorrect")
    
    if 'new_name' in update_data:
        user.user_name = update_data['new_name']
    if 'new_surname' in update_data:
        user.user_surname = update_data['new_surname']
    if 'new_email' in update_data:
        user.user_email = update_data['new_email']
    if 'new_password' in update_data:
        user.user_password = update_data['new_password']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, "Erreur de mise à jour")