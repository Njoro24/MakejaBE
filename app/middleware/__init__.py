from flask import Flask
from .cors_middleware import init_cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_cors(app)
    return app
