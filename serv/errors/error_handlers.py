from flask_restx import Api
from errors.exceptions import AppError, ControllerError, ServiceError, LoaderError, ModelError, RouteError, FirebaseError

def register_error_handlers(api: Api):
    @api.errorhandler(AppError)
    @api.errorhandler(ControllerError)
    @api.errorhandler(ServiceError)
    @api.errorhandler(LoaderError)
    @api.errorhandler(ModelError)
    @api.errorhandler(RouteError)
    @api.errorhandler(FirebaseError)
    def handle_app_error(error):
        response = {
            "error_type": error.error_type,
            "message": error.message,
            "error_code": error.status_code
        }
        return response, error.status_code

    @api.errorhandler(Exception)
    def handle_generic_error(error):
        response = {
            "error_type": "InternalServerError",
            "message": f"Erreur inattendue: {str(error)}",
            "error_code": 500
        }
        return response, 500