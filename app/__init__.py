from flask import Flask
from .config import Config
from .extensions import db, ma, jwt  
from app.routes.booking import booking_bp
from app.routes.room_routes import room_bp  # <- ADD THIS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(booking_bp, url_prefix='/api')
    app.register_blueprint(room_bp, url_prefix='/rooms')  # <- AND THIS

    with app.app_context():
        db.create_all()

    return app
