from serv.loaders.postgres import db
from sqlalchemy.dialects.postgresql import JSONB

class ShoppingList(db.Model):
    __tablename__ = 'shopping_list'
    
    shoppinglist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    grocery = db.Column(JSONB, default={})
    fresh_produce = db.Column(JSONB, default={})
    fruit_and_vegetables = db.Column(JSONB, default={})
    
    def __repr__(self):
        return f'<ShoppingList {self.shoppinglist_id} for user {self.user_id}>'