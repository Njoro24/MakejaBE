import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import configuration
from app.config import Config
from app.db import init_db, create_tables



# Import routes (only import what exists)
try:
    from app.routes.auth import auth_bp
except ImportError:
    auth_bp = None
    print("auth.py not found or has import errors")

try:
    from app.routes.user import user_bp
except ImportError:
    user_bp = None
    print("user.py route not found")

try:
    from app.routes.hostel import hostel_bp
except ImportError:
    hostel_bp = None
    print("hostel.py route not found")

try:
    from app.routes.booking import booking_bp
except ImportError:
    booking_bp = None
    print("booking.py route not found")

try:
    from app.routes.payment import payment_bp
except ImportError:
    payment_bp = None
    print("payment.py route not found")

try:
    from app.routes.review import review_bp
except ImportError:
    review_bp = None
    print("review.py route not found")

try:
    from app.routes.admin import admin_bp
except ImportError:
    admin_bp = None
    print("admin.py route not found")

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
   
    
  
    
    # Create Flask app
    app = Flask(__name__)
  
    # Initialize extensions
    init_db(app)
    
    # Setup JWT
    jwt = JWTManager(app)
    
   
    
    # Register blueprints (only register what exists)
    if auth_bp:
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("Auth routes registered")
    
    if user_bp:
        app.register_blueprint(user_bp, url_prefix='/api/users')
        print("User routes registered")
    
    if hostel_bp:
        app.register_blueprint(hostel_bp, url_prefix='/api/hostels')
        print("Hostel routes registered")
    
    if booking_bp:
        app.register_blueprint(booking_bp, url_prefix='/api/bookings')
        print("Booking routes registered")
    
    if payment_bp:
        app.register_blueprint(payment_bp, url_prefix='/api/payments')
        print("Payment routes registered")
    
    if review_bp:
        app.register_blueprint(review_bp, url_prefix='/api/reviews')
        print("Review routes registered")
    
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        print("Admin routes registered")
    
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
            create_tables(app)
            print(f"Database tables created/verified for {config_name} environment")
        except Exception as e:
            print(f"Database initialization skipped: {str(e)}")
    
    return app

def main():
    """Main function to run the application"""
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Create app
    app = create_app(config_name)
    
    print(f"""
 MAKEJA BACKEND
Environment: {config_name.upper()}
Host: {host}
Port: {port}
Debug: {debug}
URL: http://{host}:{port}/
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
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")

if __name__ == '__main__':
    main()