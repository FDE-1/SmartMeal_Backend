# smartmeal/connection/loader.py

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database connection"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/smartmeal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()