from serv.models.database.inventory_model import Inventory
from serv.loaders.postgres import db  

def get_all_inventories():
    """Retrieves all inventory records"""
    return Inventory.query.all()

def create_inventory(inventory_data):
    """Creates a new inventory entry"""
    new_inventory = Inventory(
        user_id=inventory_data['user_id'],
        ustensils=inventory_data['ustensils'],
        grocery=inventory_data['grocery'],
        fresh_produce=inventory_data['fresh_produce']
    )
    db.session.add(new_inventory)
    db.session.commit()
    return new_inventory

def get_inventory_by_id(inventory_id):
    """Retrieves inventory by ID"""
    return Inventory.query.get(inventory_id)

def update_inventory(user_id, update_data):
    """Updates inventory for a user"""
    inventory = Inventory.query.filter_by(user_id=user_id).first()
    if not inventory:
        return None
    
    inventory.ustensils = update_data.get('ustensils', inventory.ustensils)
    inventory.grocery = update_data.get('grocery', inventory.grocery)
    inventory.fresh_produce = update_data.get('fresh_produce', inventory.fresh_produce)
    
    db.session.commit()
    return inventory

def delete_inventory(inventory_id):
    """Deletes an inventory"""
    inventory = get_inventory_by_id(inventory_id)
    if inventory:
        db.session.delete(inventory)
        db.session.commit()
    return bool(inventory)

def get_inventory_by_user(user_id):
    """Retrieves inventory for a specific user"""
    return Inventory.query.filter_by(user_id=user_id).first()