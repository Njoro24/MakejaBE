from flask import Flask
from .config import Config
from .middleware.cors_middleware import init_cors
from .middleware.error_handler import register_error_handlers
from .middleware.rate_limiting import init_rate_limiter


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_cors(app)
    init_rate_limiter(app)
    register_error_handlers(app)

    return app
