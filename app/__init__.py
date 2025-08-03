import os
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from app.db import db, migrate, jwt
from app.config import config

mail = Mail()

def create_app(config_name=None):
    app = Flask(__name__)
    
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5173"}}, supports_credentials=True)

    # Import all models so SQLAlchemy registers them
    from app import models

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    from app.routes.room import room_bp  # ✅ Added here, after model import

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')
 

    return app
