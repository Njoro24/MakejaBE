import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import app.models

# Import configuration and database
from app.config import config
from app.db import init_db, db

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, origins=['https://makeja-csu3.vercel.app'], supports_credentials=True )
  
    # Initialize extensions
    init_db(app)
    
    # Initialize mail
    mail = Mail()
    mail.init_app(app)
    
    # Setup JWT
    jwt = JWTManager(app)

    # Import and register blueprints - Remove try-except to see actual errors
    print("Importing auth blueprint...")
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("Auth routes registered at /api/auth")

    # Import other routes with error handling
    try:
        from app.routes.user import user_bp
        app.register_blueprint(user_bp, url_prefix='/api/users')
        print("User routes registered")
    except ImportError as e:
        print(f"User routes not found: {e}")

    try:
        from app.routes.hostel import hostel_bp
        app.register_blueprint(hostel_bp, url_prefix='/api/hostels')
        print("Hostel routes registered")
    except ImportError as e:
        print(f"Hostel routes not found: {e}")

    try:
        from app.routes.booking import booking_bp
        app.register_blueprint(booking_bp, url_prefix='/api/bookings')
        print("Booking routes registered")
    except ImportError as e:
        print(f"Booking routes not found: {e}")

    try:
        from app.routes.payment import payment_bp
        app.register_blueprint(payment_bp, url_prefix='/api/payments')
        print("Payment routes registered")
    except ImportError as e:
        print(f"Payment routes not found: {e}")

    try:
        from app.routes.review import review_bp
        app.register_blueprint(review_bp, url_prefix='/api/reviews')
        print("Review routes registered")
    except ImportError as e:
        print(f"Review routes not found: {e}")

    try:
        from app.routes.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        print("Admin routes registered")
    except ImportError as e:
        print(f"Admin routes not found: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'environment': config_name}, 200
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to Makeja Backend API',
            'version': '1.0.0',
            'environment': config_name,
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'hostels': '/api/hostels',
                'bookings': '/api/bookings',
                'payments': '/api/payments',
                'reviews': '/api/reviews',
                'admin': '/api/admin',
                'health': '/api/health'
            }
        }, 200
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all() 
            print(f"Database tables created/verified for {config_name} environment")
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
    
    return app

def main():
    """Main function to run the application"""
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    app = create_app(config_name)
    
    print(f"""
MAKEJA BACKEND STARTING
Environment: {config_name.upper()}
Host: {host}
Port: {port}
Debug: {debug}
URL: http://{host}:{port}/
Auth API: http://{host}:{port}/api/auth/register
    """)
    
    # Run the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {str(e)}")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=10000)