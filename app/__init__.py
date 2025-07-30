import os
from flask import Flask
from flask_cors import CORS
from app.db import db, migrate, jwt
from flask_mail import Mail
from app.config import config

# Initialize mail at module level so it can be imported
mail = Mail()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Get config name from environment or use default
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    with app.app_context():
        from app.models import user, hostel, review
    
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    return app