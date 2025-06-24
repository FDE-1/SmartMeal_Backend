from flask_restx import fields
from serv.loaders.api import api

forgot_password_model = api.model('ForgotPassword', {
    'email': fields.String(required=True, description="Email")
})