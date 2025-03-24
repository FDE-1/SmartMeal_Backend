from ..connection.loader import db

class Preferences(db.Model):
    __tablename__ = 'preferences'
    __table_args__ = (
        db.CheckConstraint('new >= 1 AND new <= 5', name='preferences_new_check'),
    )
    
    preference_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    allergy = db.Column(db.JSON) 
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
    def serialize(self):
        return {
            'preference_id': self.preference_id,
            'user_id': self.user_id,
            'allergy': self.allergy if self.allergy else {},
            'diet': self.diet or '',
            'goal': self.goal or '',
            'new': self.new or 0,
            'number_of_meals': self.number_of_meals or 0,
            'grocery_day': self.grocery_day or '',
            'language': self.language or ''
        }
    
    