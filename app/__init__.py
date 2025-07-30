
import os
from app.extensions import db, migrate, jwt, ma
from flask import Flask
from flask_cors import CORS
from .config import Config
from .middleware.cors_middleware import init_cors
from .middleware.error_handler import register_error_handlers
from .middleware.rate_limiting import init_rate_limiter


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_cors(app)
    init_rate_limiter(app)
    register_error_handlers(app)

    return app

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
