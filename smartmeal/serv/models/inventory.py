from ..connection.loader import db
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ustensils = db.Column(JSONB, default=list)
    grocery = db.Column(JSONB, default=list)
    fresh_produce = db.Column(JSONB, default=list)

