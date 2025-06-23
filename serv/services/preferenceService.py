from serv.models.database.preference_model import Preferences
from serv.loaders.postgres import db  

def create_preference_in_db(preference_data):
    """Handles preference creation in database"""
    new_preference = Preferences(
        user_id=preference_data['user_id'],
        allergy=preference_data.get('allergy', {}),
        diet=preference_data.get('diet', ''),
        goal=preference_data.get('goal', ''),
        new=preference_data.get('new', 1),
        number_of_meals=preference_data.get('number_of_meals', 3),
        grocery_day=preference_data.get('grocery_day', 'Monday'),
        language=preference_data.get('language', 'fr')
    )
    db.session.add(new_preference)
    db.session.commit()
    return new_preference

def get_preference_by_user(user_id):
    """Retrieves user preferences"""
    return Preferences.query.filter_by(user_id=user_id).first()

def update_preference(user_id, update_data):
    """Updates user preferences"""
    preference = get_preference_by_user(user_id)
    if not preference:
        return None
    
    fields = ['user_id', 'allergy', 'diet', 'goal', 'new', 
             'number_of_meals', 'grocery_day', 'language']
    for field in fields:
        if field in update_data:
            setattr(preference, field, update_data[field])
    
    db.session.commit()
    return preference

def delete_preference(user_id):
    """Deletes user preferences"""
    preference = get_preference_by_user(user_id)
    if preference:
        db.session.delete(preference)
        db.session.commit()
    return bool(preference)