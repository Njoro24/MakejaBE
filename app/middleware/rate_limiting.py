from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify


def init_rate_limiter(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config.get("RATE_LIMIT_DEFAULT")],
        storage_uri="memory://"
    )

    @limiter.request_filter
    def exempt_health_checks():
        return False

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"status": "error", "message": "Rate limit exceeded"}), 429

    return limiter
