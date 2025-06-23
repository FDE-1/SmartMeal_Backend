from flask_restx import Namespace, Resource
from serv.loaders.api import api
from serv.controllers.weekController import list_all_weeks, handle_week_creation, get_week_details, handle_week_update, handle_week_deletion, get_user_weeks, get_user_week_data
from serv.models.input.week.week_model import week_model

week_route = Namespace('weeks', description='Weekly meal planning operations')

@week_route.route('/')
class WeekList(Resource):
    @week_route.doc('list_weeks')
    def get(self):
        """List all weeks"""
        return list_all_weeks()

@week_route.route('/')
class WeekList(Resource):
    @week_route.doc('create_week')
    @week_route.expect(week_model)
    def post(self):
        """Create a new week"""
        return handle_week_creation()

@week_route.route('/<int:week_id>')
class WeekResource(Resource):
    @week_route.doc('get_week')
    @week_route.response(404, 'Week not found')
    def get(self, week_id):
        """Get a specific week by ID"""
        week_data = get_week_details(week_id)
        return week_data
    
    @week_route.doc('update_week')
    @week_route.expect(week_model)
    @week_route.response(404, 'Week not found')
    def put(self, week_id):
        """Update a week"""
        return handle_week_update(week_id)
    
    @week_route.doc('delete_week')
    @week_route.response(404, 'Week not found')
    def delete(self, week_id):
        """Delete a week"""
        return handle_week_deletion(week_id)
    
@week_route.route('/user/<int:user_id>')
class UserWeeks(Resource):
    @week_route.doc('get_user_weeks')
    def get(self, user_id):
        """Get all weeks for a user"""
        return get_user_weeks(user_id)
    
@week_route.route('/user/<int:user_id>/week/<int:week_id>')
class UserWeek(Resource):
    @week_route.doc('get_user_week')
    def get(self, user_id, week_id):
        """Get a specific week for a user"""
        return get_user_week_data(user_id, week_id)
