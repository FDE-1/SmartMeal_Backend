from ..connection.loader import db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class Week(db.Model):
    __tablename__ = 'weeks'
    
    id = db.Column(db.Integer, primary_key=True)  

    week_number = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    lundi = db.Column(ARRAY(JSONB), default=[])
    mardi = db.Column(ARRAY(JSONB), default=[])
    mercredi = db.Column(ARRAY(JSONB), default=[])
    jeudi = db.Column(ARRAY(JSONB), default=[])
    vendredi = db.Column(ARRAY(JSONB), default=[])
    samedi = db.Column(ARRAY(JSONB), default=[])
    dimanche = db.Column(ARRAY(JSONB), default=[])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'week_number', name='uq_user_week'),
    )