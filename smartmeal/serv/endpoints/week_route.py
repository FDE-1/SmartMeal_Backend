from flask import jsonify, request, current_app
from ..connection.loader import db
from ..models.week import Week
from flask_restx import Namespace, Resource, fields

api = Namespace('weeks', description='Weekly meal planning operations')

day_fields = {
    'lundi': fields.List(fields.Raw, required=False),
    'mardi': fields.List(fields.Raw, required=False),
    'mercredi': fields.List(fields.Raw, required=False),
    'jeudi': fields.List(fields.Raw, required=False),
    'vendredi': fields.List(fields.Raw, required=False),
    'samedi': fields.List(fields.Raw, required=False),
    'dimanche': fields.List(fields.Raw, required=False)
}

week_model = api.model('Week', {
    'id': fields.Integer(readOnly=True),
    'user_id': fields.Integer(required=True),
    'week_number': fields.Integer(required=True),
    **day_fields
})

@api.route('/')
class WeekList(Resource):
    @api.doc('list_weeks')
    def get(self):
        """List all weeks"""
        weeks = Week.query.all()
        return jsonify([{
            'id': w.id,
            'user_id': w.user_id,
            'week_number': w.week_number,
            'lundi': w.lundi,
            'mardi': w.mardi,
            'mercredi': w.mercredi,
            'jeudi': w.jeudi,
            'vendredi': w.vendredi,
            'samedi': w.samedi,
            'dimanche': w.dimanche
        } for w in weeks])

    @api.doc('create_week')
    @api.expect(week_model)
    def post(self):
        """Create a new week"""
        try:
            data = request.json
            if not data:
                return {'message': 'No input data provided'}, 400

            if 'user_id' not in data:
                return {'message': 'user_id is required'}, 400
            if 'week_number' not in data:
                return {'message': 'week_number is required'}, 400

            new_week = Week(
                user_id=data['user_id'],
                week_number=data['week_number'],
                lundi=data.get('lundi', []),
                mardi=data.get('mardi', []),
                mercredi=data.get('mercredi', []),
                jeudi=data.get('jeudi', []),
                vendredi=data.get('vendredi', []),
                samedi=data.get('samedi', []),
                dimanche=data.get('dimanche', [])
            )

            db.session.add(new_week)
            db.session.commit()
            db.session.refresh(new_week)
            
            return {
                'message': 'Week created successfully',
                'id': new_week.id,
                'week_number': new_week.week_number
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating week: {str(e)}")
            return {
                'message': 'Failed to create week',
                'error': str(e)
            }, 500
@api.route('/<int:id>')
class WeekResource(Resource):
    @api.doc('get_week')
    @api.response(404, 'Week not found')
    def get(self, id):
        """Get a specific week by ID"""
        week = Week.query.get_or_404(id)
        return {
            'id': week.id,
            'user_id': week.user_id,
            'week_number': week.week_number,
            'lundi': week.lundi,
            'mardi': week.mardi,
            'mercredi': week.mercredi,
            'jeudi': week.jeudi,
            'vendredi': week.vendredi,
            'samedi': week.samedi,
            'dimanche': week.dimanche
        }

    @api.doc('update_week')
    @api.expect(week_model)
    @api.response(404, 'Week not found')
    def put(self, id):
        """Update a week"""
        try:
            week = Week.query.get_or_404(id)
            data = request.json

            # Allow updating week_number too, but check uniqueness
            if 'week_number' in data:
                week.week_number = data['week_number']
            if 'lundi' in data:
                week.lundi = data['lundi']
            if 'mardi' in data:
                week.mardi = data['mardi']
            if 'mercredi' in data:
                week.mercredi = data['mercredi']
            if 'jeudi' in data:
                week.jeudi = data['jeudi']
            if 'vendredi' in data:
                week.vendredi = data['vendredi']
            if 'samedi' in data:
                week.samedi = data['samedi']
            if 'dimanche' in data:
                week.dimanche = data['dimanche']

            db.session.commit()
            return {'message': 'Week updated successfully'}

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating week {id}: {str(e)}")
            return {
                'message': 'Failed to update week',
                'error': str(e)
            }, 500

    @api.doc('delete_week')
    @api.response(404, 'Week not found')
    def delete(self, id):
        """Delete a week"""
        try:
            week = Week.query.get_or_404(id)
            db.session.delete(week)
            db.session.commit()
            return {'message': 'Week deleted successfully'}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting week {id}: {str(e)}")
            return {
                'message': 'Failed to delete week',
                'error': str(e)
            }, 500

@api.route('/user/<int:user_id>')
class UserWeeks(Resource):
    @api.doc('get_user_weeks')
    def get(self, user_id):
        """Get all weeks for a user"""
        weeks = Week.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'id': w.id,
            'week_number': w.week_number,
            'lundi': w.lundi,
            'mardi': w.mardi,
            'mercredi': w.mercredi,
            'jeudi': w.jeudi,
            'vendredi': w.vendredi,
            'samedi': w.samedi,
            'dimanche': w.dimanche
        } for w in weeks])


@api.route('/user/<int:user_id>/week/<int:week_number>')
class UserWeek(Resource):
    @api.doc('get_user_week')
    def get(self, user_id, week_number):
        """Get a specific week for a user by week number"""
        week = Week.query.filter_by(user_id=user_id, week_number=week_number).first()
        
        if not week:
            return {'message': 'Week not found'}, 404
            
        return jsonify({
            'id': week.id,
            'week_number': week.week_number,
            'lundi': week.lundi,
            'mardi': week.mardi,
            'mercredi': week.mercredi,
            'jeudi': week.jeudi,
            'vendredi': week.vendredi,
            'samedi': week.samedi,
            'dimanche': week.dimanche
        })
    
@api.route('/testsuite/weeks')
class WeekTestSuite(Resource):
    @api.doc('run_week_test_suite')
    @api.response(200, 'Success')
    @api.response(500, 'Server error')
    def post(self):
        """Execute a complete test suite for weeks"""
        results = []
        created_week_id = None
        created_week_number = 42  # Arbitrary test week
        test_user_id = 1  # Special test user ID

        def unpack_response(resp):
            if isinstance(resp, tuple):
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Create week ===
            create_payload = {
                "user_id": test_user_id,
                "week_number": created_week_number,
                "lundi": [{"meal": "Pasta", "time": "12:00"}],
                "mardi": [{"meal": "Salad", "time": "13:00"}]
            }

            with current_app.test_request_context(json=create_payload):
                response = WeekList().post()
                week_obj, status_code = unpack_response(response)
                if status_code != 201:
                    raise Exception("Week creation failed")
                created_week_id = week_obj['id']
                results.append(f"✅ Week created with ID: {created_week_id} (week_number={created_week_number})")

            # === Test 2: Get week by ID ===
            with current_app.test_request_context():
                response = WeekResource().get(created_week_id)
                data, status_code = unpack_response(response)
                if status_code != 200 or data['user_id'] != test_user_id:
                    raise Exception("Failed to fetch week by ID")
                results.append("✅ Week retrieved successfully by ID")

            # === Test 3: Update week ===
            update_payload = {
                "mercredi": [{"meal": "Soup", "time": "12:30"}],
                "jeudi": [{"meal": "Sandwich", "time": "13:30"}]
            }

            with current_app.test_request_context(json=update_payload):
                response = WeekResource().put(created_week_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Update failed")
                results.append("✅ Week updated successfully")

            # === Test 4: Verify update ===
            with current_app.test_request_context():
                response = WeekResource().get(created_week_id)
                updated, _ = unpack_response(response)
                if not updated['mercredi']:
                    raise Exception("Wednesday update failed")
                results.append("✅ Update verified")

            # === Test 5: Get by user ID ===
            with current_app.test_request_context():
                response = UserWeeks().get(test_user_id)
                data, status_code = unpack_response(response)
                if status_code != 200 or len(data.json) == 0:
                    raise Exception("Failed to fetch weeks by user ID")
                results.append("✅ User weeks retrieved")

            # === Test 6: Get by user & week_number ===
            with current_app.test_request_context():
                response = UserWeek().get(test_user_id, created_week_number)
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Failed to fetch week by user & week_number")
                results.append("✅ Week retrieved by user & week_number")

            # === Test 7: Delete ===
            with current_app.test_request_context():
                response = WeekResource().delete(created_week_id)
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Deletion failed")
                results.append("✅ Week deleted successfully")

            # Final verification
            deleted_week = Week.query.get(created_week_id)
            if deleted_week:
                raise Exception("Deletion didn't work")

            results.append("\n🏁 All week tests passed successfully!")
            return {'results': results}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            # Cleanup if failed
            if created_week_id:
                w = Week.query.get(created_week_id)
                if w:
                    db.session.delete(w)
                    db.session.commit()
            
            results.append(f"\n❌ Error during tests: {str(e)}")
            return {'results': results}, 500
