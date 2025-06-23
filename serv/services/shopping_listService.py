from models.database.shoppinglist_model import ShoppingList
from loaders.postgres import db  
from flask_restx import abort

def get_all_shopping_lists():
    """Retrieves all shopping lists from database"""
    return ShoppingList.query.all()

def create_shopping_list_in_db(list_data):
    """Creates a new shopping list in database"""
    new_list = ShoppingList(
        user_id=list_data['user_id'],
        grocery=list_data.get('grocery', {}),
        fresh_produce=list_data.get('fresh_produce', {}),
        fruit_and_vegetables=list_data.get('fruit_and_vegetables', {})
    )
    db.session.add(new_list)
    db.session.commit()
    return new_list

def get_shopping_list(shoppinglist_id):
    """Retrieves a single shopping list"""
    return ShoppingList.query.get(shoppinglist_id)

def update_shopping_list(shoppinglist_id, update_data):
    """Updates shopping list data"""
    slist = get_shopping_list(shoppinglist_id)
    if not slist:
        return None
    
    fields = ['grocery', 'fresh_produce', 'fruit_and_vegetables']
    for field in fields:
        if field in update_data:
            setattr(slist, field, update_data[field])
    
    db.session.commit()
    return slist

def delete_shopping_list(shoppinglist_id):
    """Deletes a shopping list"""
    slist = get_shopping_list(shoppinglist_id)
    if slist:
        db.session.delete(slist)
        db.session.commit()
    return bool(slist)

def get_user_shopping_lists(user_id):
    """Retrieves all shopping lists for a specific user"""
    return ShoppingList.query.filter_by(user_id=user_id).all()