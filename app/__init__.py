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
    app.config.from_object(Config)

    # Configure CORS - single source of truth
    CORS(
        app,
        origins=[
            "https://makeja-csu3.vercel.app",    # old URL
            "https://makeja-kappa.vercel.app"    # new URL
        ],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )

    # Initialize extensions
    try:
        init_db(app)
        jwt = JWTManager(app)
        print("Extensions initialized successfully")
    except Exception as e:
        print(f"Extensions error: {e}")
    
    # Initialize middleware
    try:
        init_rate_limiter(app)
        register_error_handlers(app)
        print("Middleware initialized successfully")
    except Exception as e:
        print(f"Middleware error: {e}")
    
    # Register blueprints
    try:
        from .routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("Auth blueprint registered successfully")
    except Exception as e:
        print(f"Auth blueprint error: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    # Root endpoint
    @app.route('/')
    def home():
        return {'message': 'Flask app is running'}, 200
    
    return app