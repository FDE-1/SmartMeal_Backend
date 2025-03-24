from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from ..connection.loader import db
from ..models.preferences import Preferences
from ..models.user import User
from psycopg2 import IntegrityError

api = Namespace('preferences', description='User preferences operations')

preference_model = api.model('Preferences', {
    'preference_id': fields.Integer(readonly=True),
    'user_id': fields.Integer,
    'allergy': fields.Raw(example={'nuts': True, 'dairy': False}),
    'diet': fields.String(example='vegetarian'),
    'goal': fields.String(example='weight loss'),
    'new': fields.Integer(min=1, max=5, example=3),
    'number_of_meals': fields.Integer(example=3),
    'grocery_day': fields.String(example='Monday'),
    'language': fields.String(example='en')
})

@api.route('/')
class PreferenceList(Resource):
    @api.doc('list_preferences')
    @api.response(200, 'Success')
    def get(self):
        """List all preferences"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                return {'message': 'User not found'}, 404
                
            return {[p.serialize() for p in user.preferences]
            } 
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Database error: {str(e)}'}, 500

    @api.doc('create_preference')
    @api.expect(preference_model)
    @api.response(201, 'Preference created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new preference"""
        try:
            data = request.get_json()
            
            # Validate 'new' field
            if 'new' in data and (data['new'] < 1 or data['new'] > 5):
                return {'message': 'New must be between 1 and 5'}, 400
            
            preference = Preferences(
                user_id=data.get('user_id'),
                allergy=data.get('allergy'),
                diet=data.get('diet'),
                goal=data.get('goal'),
                new=data.get('new'),
                number_of_meals=data.get('number_of_meals'),
                grocery_day=data.get('grocery_day'),
                language=data.get('language')
            )
            
            db.session.add(preference)
            db.session.commit()
            return preference.to_dict(), 201
            
        except IntegrityError as e:
            db.session.rollback()
            return {'message': 'Database integrity error'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

@api.route('/<int:preference_id>')
@api.param('preference_id', 'The preference identifier')
@api.response(404, 'Preference not found')
class PreferenceResource(Resource):
    @api.doc('get_preference')
    @api.marshal_with(preference_model)
    def get(self, preference_id):
        """Get a specific preference"""
        try:
            user = db.session.get(User, preference_id)
            if not user:
                api.abort(404, "user not found")
            return user.preferences
        except Exception as e:
            return {'message': str(e)}, 500

    @api.doc('update_preference')
    @api.expect(preference_model)
    @api.response(200, 'Preference updated')
    @api.response(400, 'Validation error')
    def put(self, preference_id):
        """Update a preference"""
        try:
            preference = db.session.get(Preferences, preference_id)
            if not preference:
                api.abort(404, "Preference not found")
            
            data = request.get_json()
            
            # Validate 'new' field
            if 'new' in data and (data['new'] < 1 or data['new'] > 5):
                return {'message': 'New must be between 1 and 5'}, 400
            
            if 'user_id' in data:
                preference.user_id = data['user_id']
            if 'allergy' in data:
                preference.allergy = data['allergy']
            if 'diet' in data:
                preference.diet = data['diet']
            if 'goal' in data:
                preference.goal = data['goal']
            if 'new' in data:
                preference.new = data['new']
            if 'number_of_meals' in data:
                preference.number_of_meals = data['number_of_meals']
            if 'grocery_day' in data:
                preference.grocery_day = data['grocery_day']
            if 'language' in data:
                preference.language = data['language']
            
            db.session.commit()
            return preference.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            return {'message': 'Database integrity error'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    @api.doc('delete_preference')
    @api.response(204, 'Preference deleted')
    def delete(self, preference_id):
        """Delete a preference"""
        try:
            preference = db.session.get(Preferences, preference_id)
            if not preference:
                api.abort(404, "Preference not found")
            
            db.session.delete(preference)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
        
@api.route('/test-relationship/<int:user_id>')
class TestRelationship(Resource):
    def get(self, user_id):
        """Test user-preference relationship"""
        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'User not found'}, 404
            
        return {
            'user_id': user.user_id,
            'preferences': [p.serialize() for p in user.preferences]
        } 