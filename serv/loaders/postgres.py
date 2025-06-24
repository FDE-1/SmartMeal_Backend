import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize the database connection"""
    app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()