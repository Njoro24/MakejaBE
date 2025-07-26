import os
from flask import Flask
from flask_cors import CORS
from app.db import db, migrate, jwt  

def create_app():
    app = Flask(__name__)

    # Configurations
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../makeja.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Use environment variables in production

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
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
