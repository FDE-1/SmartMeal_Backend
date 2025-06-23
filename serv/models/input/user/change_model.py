from flask_restx import fields
from loaders.api import api

change_info_model = api.model('ChangeInfo', {
    'new_name': fields.String(description="Nom d'utilisateur"),
    'new_surname': fields.String(description="Nouveau nom"),
    'new_email': fields.String(description="Nouvel email"),
    'old_password': fields.String(required=True, description="Ancien mot de passe"),
    'new_password': fields.String(description="Nouveau mot de passe")
})