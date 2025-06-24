from serv.loaders.postgres import db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class Week(db.Model):
    __tablename__ = 'weeks'
    
    week_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    lundi = db.Column(ARRAY(JSONB), default=[])
    mardi = db.Column(ARRAY(JSONB), default=[])
    mercredi = db.Column(ARRAY(JSONB), default=[])
    jeudi = db.Column(ARRAY(JSONB), default=[])
    vendredi = db.Column(ARRAY(JSONB), default=[])
    samedi = db.Column(ARRAY(JSONB), default=[])
    dimanche = db.Column(ARRAY(JSONB), default=[])
