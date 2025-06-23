from flask_restx import Api

api = Api(
    title='SmartMeal API',
    version='2.0',
    description="API pour l'application smartmeal",
    doc='/swagger'
)