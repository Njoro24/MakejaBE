from app import create_app, db
from flask_migrate import upgrade
import os

def deploy():
    """Run deployment tasks."""
    app = create_app()
    with app.app_context():
        try:
            # Create database tables
            print("Running database migration...")
            upgrade()
            print("Database migration completed successfully!")
        except Exception as e:
            print(f"Migration error: {e}")
            # If migrations don't exist, create tables directly
            print("Creating tables directly...")
            db.create_all()
            print("Tables created successfully!")

if __name__ == '__main__':
    deploy()