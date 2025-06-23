from serv.models.database.week_model import Week
from serv.loaders.postgres import db  
from flask_restx import abort

def get_all_weeks():
    """Retrieves all weeks from database"""
    return Week.query.all()

def create_week_in_db(week_data):
    """Handles week creation in database"""
    new_week = Week(
        week_id=week_data['week_id'],
        user_id=week_data['user_id'],
        lundi=week_data.get('lundi', []),
        mardi=week_data.get('mardi', []),
        mercredi=week_data.get('mercredi', []),
        jeudi=week_data.get('jeudi', []),
        vendredi=week_data.get('vendredi', []),
        samedi=week_data.get('samedi', []),
        dimanche=week_data.get('dimanche', [])
    )
    db.session.add(new_week)
    db.session.commit()
    db.session.refresh(new_week)
    return new_week

def get_week_by_id(week_id):
    """Retrieves a single week from database"""
    return Week.query.get(week_id)

def update_week_in_db(week_id, update_data):
    """Handles week updates in database"""
    week = Week.query.get(week_id)
    if not week:
        return None
    
    fields = ['lundi', 'mardi', 'mercredi', 'jeudi', 
             'vendredi', 'samedi', 'dimanche']
    
    for field in fields:
        if field in update_data:
            setattr(week, field, update_data[field])
    
    db.session.commit()
    return week

def delete_week_from_db(week_id):
    """Handles week deletion in database"""
    week = Week.query.get(week_id)
    if week:
        db.session.delete(week)
        db.session.commit()
    return week is not None

def get_weeks_by_user(user_id):
    """Retrieves all weeks for a specific user"""
    return Week.query.filter_by(user_id=user_id).all()

def get_user_week(user_id, week_id):
    """Retrieves a specific week for a user"""
    return Week.query.filter_by(user_id=user_id, week_id=week_id).first()