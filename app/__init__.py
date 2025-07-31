from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .db import init_db
from .middleware.error_handler import register_error_handlers
from .middleware.rate_limiting import init_rate_limiter

def create_app(config_name=None):
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    try:
        app.config.from_object(Config)
    except Exception as e:
        print(f"Config error: {e}")
    
    # Configure CORS
    CORS(
        app,
        origins=["https://makeja-csu3.vercel.app"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )

    try:
        init_db(app)
        jwt = JWTManager(app)
    except Exception as e:
        print(f"Extensions error: {e}")
    
    try:
        init_rate_limiter(app)
        register_error_handlers(app)
    except Exception as e:
        print(f"Middleware error: {e}")
    
    try:
        from .routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("Auth blueprint registered successfully")
    except Exception as e:
        print(f"Blueprint error: {e}")
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/')
    def home():
        return {'message': 'Flask app is running'}, 200
    
    return app