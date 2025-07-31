from flask import Flask
from .cors_middleware import init_cors
from app.config import Config  # Make sure this import matches your config location

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_cors(app)
    return app
