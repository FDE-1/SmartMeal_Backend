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
    
    @api.doc('login')
    @api.param('name', 'Name of user')
    @api.param('password', 'Password of the user')
    def login(self, name, password):
        """Log into the database with the given credentials"""
        user = User.query(User).filter(User.user_name == name)
        if not user:
            return {'message': 'No user with the name <"' + name + '"> exist in the database'}, 404
        if user.user_name != password:
            return {'message': 'The password did not match'}, 404
        #should do a cache to keep the user id
        return {'message', 'Successful connection'}, 201