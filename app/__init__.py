from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, jwt, ma
import os

  # Load environment variables from a .env file if present

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/yourdb')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # CORS setup (specific to frontend origin)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

    # Import and register Blueprints here
    # from app.routes.hostel import hostel_bp
    # app.register_blueprint(hostel_bp, url_prefix="/api/hostels")

    return app
