from flask import jsonify, request
from ..connection.loader import db
from ..models.user import User
from flask_restx import Namespace, Resource, fields

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'user_name': fields.String(required=True),
    'user_surname': fields.String(required=True),
    'user_email': fields.String(required=True),
    'user_password': fields.String(required=True)
})

@api.route('/')
class UserList(Resource):
    @api.doc('list_users')
    def get(self):
        """List all users"""
        users = User.query.all()
        return jsonify([{'user_id': u.user_id, 'name': u.user_name, 'email': u.user_email} for u in users])

    @api.doc('create_user')
    @api.expect(user_model)
    def post(self):
        """Create a new user"""
        data = request.json
        
        new_user = User(
            user_name=data['user_name'],
            user_surname=data['user_surname'],
            user_email=data['user_email'],
            user_password=data['user_password']
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User added successfully'}, 201

@api.route('/login')
class LoginResource(Resource):
    @api.doc('login')
    @api.param('name', 'Name of user', _in='query')
    @api.param('password', 'Password of the user', _in='query')
    def get(self):
        """Log into the database with the given credentials"""
        name = request.args.get('name')
        password = request.args.get('password')

        if not name or not password:
            return {'message': 'Both name and password are required'}, 400

        user = User.query.filter_by(user_name=name).first()
        if not user:
            return {'message': f'No user with the name "{name}" exists in the database'}, 404
        if user.password != password:
            return {'message': 'The password did not match'}, 401

        return {'message': 'Successful connection'}, 200
