from flask import Flask
from .config import Config
from .middleware.cors_middleware import init_cors
from .middleware.error_handler import register_error_handlers

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    init_cors(app)
    register_error_handlers(app)

    @app.route("/ping")
    def ping():
        return {"message": "pong"}

    @app.route("/unauthorized")
    def test_unauthorized():
        from werkzeug.exceptions import Unauthorized
        raise Unauthorized("You are not authorized")

    @app.route("/unexpected")
    def test_unexpected():
        raise Exception("Crash test")

    return app

