# smartmeal/connection/loader.py
import os
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database connection"""
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)  
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()