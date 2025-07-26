from flask import Flask
from .config import Config
from .extensions import db, ma, jwt
from flask_migrate import Migrate  

# Blueprint imports
from app.routes.booking import booking_bp
from app.routes.room_routes import room_bp
from app.routes.auth_routes import auth_bp

migrate = Migrate()  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  

    
    app.register_blueprint(booking_bp, url_prefix='/api')
    app.register_blueprint(room_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app
