from flask_cors import CORS

def init_cors(app):
    CORS(
        app,
        origins=app.config.get("ALLOWED_ORIGINS"),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS"),
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"]
    )
