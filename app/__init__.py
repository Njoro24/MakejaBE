from flask import Flask
from .config import Config
from .middleware.cors_middleware import init_cors

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    init_cors(app)
    return app


    @app.route("/ping")
    def ping():
        return {"message": "pong"}
