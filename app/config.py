""" Simple Flask Configuration for Makeja Hostel App """
import os

class Config:
    """Basic configuration for the hostel booking app"""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    
    # Database - PostgreSQL for production, SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://makeja_user:makeja_pass@localhost/makeja_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Frontend URL for email verification
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    
    # M-Pesa payment settings (Sandbox - for testing only)
    MPESA_CONSUMER_KEY = 'Bl0yLyomUFlqQJv36ou12oxNLDVpRE38iPUYZ5dXZbGruDel'
    MPESA_CONSUMER_SECRET = 'o3G6DSjlMnlWDbxKGe7EEAwRTwabldnpuaApcI4bPjcllbOUV3PMAhkEyCyAQrtm'
    MPESA_SHORTCODE = '174379'
    MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://your-app.com/api/payments/callback')
    
    # App settings
    CURRENCY = 'KES'
    TIMEZONE = 'Africa/Nairobi'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://makeja_user:makeja_pass@localhost/makeja_db'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}