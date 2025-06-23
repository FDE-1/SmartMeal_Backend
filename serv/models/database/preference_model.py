from serv.loaders.postgres import db
from sqlalchemy.dialects.postgresql import JSONB

class Preferences(db.Model):
    preference_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    allergy = db.Column(JSONB)    
    diet = db.Column(db.Text)
    goal = db.Column(db.Text)
    new = db.Column(db.Integer)
    number_of_meals = db.Column(db.Integer)
    grocery_day = db.Column(db.Text)
    language = db.Column(db.Text)

    user = db.relationship(
        'User', 
        back_populates='preferences',
        lazy=True
    )