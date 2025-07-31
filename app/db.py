from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager  

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()  


def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  

   
    try:
        from app.models.user import User
        print("User model loaded")
    except ImportError:
        print("User model not found")

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

def create_tables(app=None):
    """Create all database tables"""
    if app:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    else:
        db.create_all()
        print("Database tables created successfully")