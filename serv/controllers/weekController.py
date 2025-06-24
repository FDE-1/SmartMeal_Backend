from serv.services.weekService import get_all_weeks, create_week_in_db, get_week_by_id, update_week_in_db, delete_week_from_db, get_weeks_by_user, get_user_week
from flask import request
from flask_restx import abort
from firebase_admin import auth

def list_all_weeks():
    """Formats week data for response"""
    weeks = get_all_weeks()
    return [{
        'week_id': w.week_id,
        'user_id': w.user_id,
        'lundi': w.lundi,
        'mardi': w.mardi,
        'mercredi': w.mercredi,
        'jeudi': w.jeudi,
        'vendredi': w.vendredi,
        'samedi': w.samedi,
        'dimanche': w.dimanche
    } for w in weeks]

def handle_week_creation():
    """Validates and processes week creation"""
    data = request.get_json()
    if not data:
        abort(400, 'No input data provided')
    if 'user_id' not in data:
        abort(400, 'user_id is required')
    
    try:
        new_week = create_week_in_db(data)
        return {
            'message': 'Week created successfully',
            'week_id': new_week.week_id
        }
    except Exception as e:
        abort(500, 'Failed to create week')

def get_week_details(week_id):
    """Formats week data for response"""
    week = get_week_by_id(week_id)
    if not week:
        abort(404, 'Week not found')
    
    return {
        'week_id': week.week_id,
        'user_id': week.user_id,
        'lundi': week.lundi,
        'mardi': week.mardi,
        'mercredi': week.mercredi,
        'jeudi': week.jeudi,
        'vendredi': week.vendredi,
        'samedi': week.samedi,
        'dimanche': week.dimanche
    }

def handle_week_update(week_id):
    """Validates and processes week updates"""
    data = request.get_json()
    updated_week = update_week_in_db(week_id, data)
    if not updated_week:
        abort(404, 'Week not found')
    
    return {'message': 'Week updated successfully'}

def handle_week_deletion(week_id):
    """Manages week deletion process"""
    if not delete_week_from_db(week_id):
        abort(404, 'Week not found')
    return {'message': 'Week deleted successfully'}

def get_user_weeks(user_id):
    """Formats weeks data for a specific user"""
    weeks = get_weeks_by_user(user_id)
    return [{
        'week_id': w.week_id,
        'lundi': w.lundi,
        'mardi': w.mardi,
        'mercredi': w.mercredi,
        'jeudi': w.jeudi,
        'vendredi': w.vendredi,
        'samedi': w.samedi,
        'dimanche': w.dimanche
    } for w in weeks]

def get_user_week_data(user_id, week_id):
    """Formats week data for response"""
    week = get_user_week(user_id, week_id)
    if not week:
        abort(404, 'Week not found')
    
    return {
        'lundi': week.lundi,
        'mardi': week.mardi,
        'mercredi': week.mercredi,
        'jeudi': week.jeudi,
        'vendredi': week.vendredi,
        'samedi': week.samedi,
        'dimanche': week.dimanche
    }