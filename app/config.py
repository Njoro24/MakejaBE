import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # General Config
    SECRET_KEY = 'dev'  # Change in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # Change in production
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
