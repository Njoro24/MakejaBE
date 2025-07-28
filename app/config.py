"""
Flask Application Configuration
Basic configuration with M-Pesa integration
"""

import os
import secrets
from datetime import timedelta


class Config:
    """Basic configuration class with essential settings."""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Application settings
    APP_NAME = os.environ.get('APP_NAME', 'Hostel Booking System')
    VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hostel_booking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # Password security
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    MAIL_SUPPRESS_SEND = False
    
    # M-Pesa configuration (for Kenya)
    MPESA_CONSUMER_KEY = os.environ.get('Bl0yLyomUFlqQJv36ou12oxNLDVpRE38iPUYZ5dXZbGruDel')
    MPESA_CONSUMER_SECRET = os.environ.get('o3G6DSjlMnlWDbxKGe7EEAwRTwabldnpuaApcI4bPjcllbOUV3PMAhkEyCyAQrtm')
    MPESA_SHORTCODE = os.environ.get('174379')
    MPESA_PASSKEY = os.environ.get('bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919') #sandbox
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL')
    
    # Payment settings
    CURRENCY = os.environ.get('CURRENCY', 'KES')
    PAYMENT_TIMEOUT = 300  # 5 minutes
    REFUND_WINDOW_HOURS = 24
    
    # Booking configuration
    BOOKING_ADVANCE_DAYS = 365
    BOOKING_MIN_DURATION = 1
    BOOKING_MAX_DURATION = 30
    BOOKING_CUTOFF_TIME = "14:00"
    AUTO_CANCEL_UNPAID_MINUTES = 30
    
    # Review configuration
    REVIEW_MIN_LENGTH = 10
    REVIEW_MAX_LENGTH = 1000
    REVIEW_RATING_MIN = 1
    REVIEW_RATING_MAX = 5
    REVIEWS_PER_PAGE = 10
    
    # Hostel configuration
    HOSTEL_IMAGES_MAX = 10
    ROOM_TYPES = ['single', 'double', 'dormitory', 'suite', 'family']
    
    # Pagination settings
    PAGINATION_PAGE_SIZE = 20
    PAGINATION_MAX_PAGE_SIZE = 100
    
    # Timezone settings
    TIMEZONE = os.environ.get('TIMEZONE', 'Africa/Nairobi')
    
    # Feature flags
    FEATURE_REVIEWS_ENABLED = True
    FEATURE_PAYMENTS_ENABLED = True
    FEATURE_NOTIFICATIONS_ENABLED = True
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass


# Single configuration instance
config = Config


def get_config():
    """
    Get the configuration class.
    
    Returns:
        Config: Configuration class
    """
    return Config