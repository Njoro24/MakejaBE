from flask import Flask
from .config import Config
from .middleware.cors_middleware import init_cors
from .middleware.error_handler import register_error_handlers
from .middleware.rate_limiting import init_rate_limiter
from .db import init_db
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=["https://makeja-csu3.vercel.app"])


    init_cors(app)
    init_rate_limiter(app)
    register_error_handlers(app)
    
    # Add these missing parts:
    init_db(app)
    jwt = JWTManager(app)
    
    # Register your blueprints here
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    

    return app