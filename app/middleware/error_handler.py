from flask import jsonify
from jwt import ExpiredSignatureError, InvalidTokenError
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound, UnprocessableEntity, InternalServerError

def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def handle_400(e):
        return jsonify({"status": "error", "message": str(e)}), 400

    @app.errorhandler(Unauthorized)
    def handle_401(e):
        return jsonify({"status": "error", "message": str(e)}), 401

    @app.errorhandler(Forbidden)
    def handle_403(e):
        return jsonify({"status": "error", "message": str(e)}), 403

    @app.errorhandler(NotFound)
    def handle_404(e):
        return jsonify({"status": "error", "message": str(e)}), 404

    @app.errorhandler(UnprocessableEntity)
    def handle_422(e):
        return jsonify({"status": "error", "message": str(e)}), 422

    @app.errorhandler(InternalServerError)
    def handle_500(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    @app.errorhandler(ExpiredSignatureError)
    def handle_jwt_expired(e):
        return jsonify({"status": "error", "message": "Token has expired"}), 401

    @app.errorhandler(InvalidTokenError)
    def handle_jwt_invalid(e):
        return jsonify({"status": "error", "message": "Invalid authentication token"}), 401

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500

from app.utils.exceptions import NotFoundError, UnauthorizedError, BadRequestError

def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def handle_400(e):
        return jsonify({"status": "error", "message": str(e)}), 400

    @app.errorhandler(Unauthorized)
    def handle_401(e):
        return jsonify({"status": "error", "message": str(e)}), 401

    @app.errorhandler(Forbidden)
    def handle_403(e):
        return jsonify({"status": "error", "message": str(e)}), 403

    @app.errorhandler(NotFound)
    def handle_404(e):
        return jsonify({"status": "error", "message": str(e)}), 404

    @app.errorhandler(UnprocessableEntity)
    def handle_422(e):
        return jsonify({"status": "error", "message": str(e)}), 422

    @app.errorhandler(InternalServerError)
    def handle_500(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    @app.errorhandler(ExpiredSignatureError)
    def handle_jwt_expired(e):
        return jsonify({"status": "error", "message": "Token has expired"}), 401

    @app.errorhandler(InvalidTokenError)
    def handle_jwt_invalid(e):
        return jsonify({"status": "error", "message": "Invalid authentication token"}), 401

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500

    @app.errorhandler(NotFoundError)
    def handle_not_found_custom(e):
        return jsonify({"status": "error", "message": str(e)}), 404

    @app.errorhandler(UnauthorizedError)
    def handle_unauth_custom(e):
        return jsonify({"status": "error", "message": str(e)}), 401

    @app.errorhandler(BadRequestError)
    def handle_bad_request_custom(e):
        return jsonify({"status": "error", "message": str(e)}), 400
