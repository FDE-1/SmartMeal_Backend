from ..connection.loader import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ustensils = db.Column(db.ARRAY(db.JSON))
    grocery = db.Column(db.ARRAY(db.JSON))
    fresh_produce = db.Column(db.ARRAY(db.JSON))

