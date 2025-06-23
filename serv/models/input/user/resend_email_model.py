from flask_restx import fields
from loaders.api import api

resend_email_model = api.model('ResendVerification', {
    'idToken': fields.String(required=True, description="Jeton ID Firebase")
})