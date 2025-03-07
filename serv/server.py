from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/smartmeal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle User
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_surname = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, nullable=False)

# Modèle Inventory
class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ustensils = db.Column(db.ARRAY(db.JSON))
    grocery = db.Column(db.ARRAY(db.JSON))
    fresh_produce = db.Column(db.ARRAY(db.JSON))

# Modèle Recipes
class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String, nullable=False)
    recipe_ingredients = db.Column(db.JSON)
    recipe_instructions = db.Column(db.JSON)
    recipe_preparation_time = db.Column(db.Integer)
    recipe_ustensils_required = db.Column(db.JSON)
    recipe_nutritional_value = db.Column(db.JSON)

# Création des tables (uniquement pour le premier lancement)
# with app.app_context():
#     db.create_all()

# Route pour récupérer tous les utilisateurs
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'user_id': u.user_id, 'name': u.user_name, 'email': u.user_email} for u in users])

# Route pour ajouter un utilisateur
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(
        user_name=data['user_name'],
        user_surname=data['user_surname'],
        user_email=data['user_email'],
        user_password=data['user_password']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully'}), 201

# Route pour récupérer toutes les recettes
@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([{'recipe_id': r.recipe_id, 'name': r.recipe_name} for r in recipes])

# Route pour ajouter une recette
@app.route('/recipes', methods=['POST'])
def add_recipe():
    data = request.json
    new_recipe = Recipe(
        recipe_name=data['recipe_name'],
        recipe_ingredients=data['recipe_ingredients'],
        recipe_instructions=data['recipe_instructions'],
        recipe_preparation_time=data['recipe_preparation_time'],
        recipe_ustensils_required=data['recipe_ustensils_required'],
        recipe_nutritional_value=data['recipe_nutritional_value']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
