class AppError(Exception):
    def __init__(self, error_type: str, message: str, status_code: int = 500):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self):
        return {
            "error_type": self.error_type,
            "message": self.message,
            "status_code": self.status_code
        }


class ControllerError(AppError):
    def __init__(self, message="Erreur dans le contrôleur", status_code=400):
        super().__init__("Controller", message, status_code)


class ServiceError(AppError):
    def __init__(self, message="Erreur dans le service", status_code=500):
        super().__init__("Service", message, status_code)


class LoaderError(AppError):
    def __init__(self, message="Erreur de chargement", status_code=503):
        super().__init__("Loader", message, status_code)


class ModelError(AppError):
    def __init__(self, message="Erreur de modèle", status_code=422):
        super().__init__("Model", message, status_code)


class RouteError(AppError):
    def __init__(self, message="Route non trouvée", status_code=404):
        super().__init__("Route", message, status_code)
        
class FirebaseError(AppError):
    def __init__(self, message="Firebase erreur", status_code=504):
        super().__init__("Firebase", message, status_code)