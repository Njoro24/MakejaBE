from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize database extensions
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models only if they exist
    try:
        from app.models.user import User
        print("User model loaded")
    except ImportError as e:
        print(f"User model not found: {e}")
    
    try:
        from app.models.hostel import Hostel
        print("Hostel model loaded")
    except ImportError:
        print("Hostel model not found")
    
    try:
        from app.models.booking import Booking
        print("Booking model loaded")
    except ImportError:
        print("Booking model not found")
    
    try:
        from app.models.payment import Payment
        print("Payment model loaded")
    except ImportError:
        print("Payment model not found")
    
    try:
        from app.models.review import Review
        print("Review model loaded")
    except ImportError:
        print("Review model not found")
    
    return db

def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()

def drop_tables(app):
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()

def reset_database(app):
    """Reset database by dropping and recreating all tables"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")