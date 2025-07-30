from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('is_admin') is True:
            return fn(*args, **kwargs)
        else:
            return jsonify({'error': 'Admins only!'}), 403
    return wrapper
