from app import create_app, db
from flask_migrate import upgrade, init, migrate
import os

def deploy():
    """Run deployment tasks."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if migrations directory exists
            if not os.path.exists('migrations'):
                print("Migrations directory not found. Initializing...")
                init()
                migrate(message='Initial migration')
            
            # Try to run migrations
            print("Running database migration...")
            upgrade()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            print("Creating tables directly...")
            
            try:
                db.create_all()
                print("Tables created successfully!")
                
                # Verify tables were created
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"Created tables: {tables}")
                
            except Exception as create_error:
                print(f"Error creating tables: {create_error}")
                raise

if __name__ == '__main__':
    deploy()