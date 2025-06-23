from loaders.postgres import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False)
    user_surname = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, nullable=False)
    firebase_uid = db.Column(db.String, nullable=False)

    preferences = db.relationship(
        'Preferences', 
        back_populates='user',
        cascade='all, delete-orphan',
        lazy=True
    )

    inventory = db.relationship('Inventory', backref='user', cascade='all, delete-orphan')