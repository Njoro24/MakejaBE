import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, g
from models.user import User, TokenBlacklist
import uuid
import os
import secrets
import string

class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def generate_tokens(user_id):
        """Generate access and refresh tokens for a user"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'exp': now + timedelta(minutes=int(current_app.config.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'exp': now + timedelta(days=int(current_app.config.get('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 30))),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'type': 'refresh'
        }
        
        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        refresh_token = jwt.encode(
            refresh_payload,
            current_app.config['JWT_REFRESH_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(current_app.config.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30)) * 60
        }
    
    @staticmethod
    def decode_token(token, token_type='access'):
        """Decode and validate a JWT token"""
        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
            if token_type == 'refresh':
                secret_key = current_app.config['JWT_REFRESH_SECRET_KEY']
            
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=['HS256']
            )
            
            # Check if token is blacklisted
            if TokenBlacklist.is_blacklisted(payload['jti']):
                return None
            
            # Verify token type
            if payload.get('type') != token_type:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def blacklist_token(token):
        """Add token to blacklist"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256'],
                options={"verify_exp": False}
            )
            
            jti = payload['jti']
            expires_at = datetime.fromtimestamp(payload['exp'])
            
            TokenBlacklist.blacklist_token(jti, expires_at)
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Generate new access token using refresh token"""
        payload = SecurityUtils.decode_token(refresh_token, 'refresh')
        
        if not payload:
            return None
        
        user = User.find_by_id(payload['user_id'])
        if not user or not user.is_active:
            return None
        
        # Generate new access token
        tokens = SecurityUtils.generate_tokens(user.id)
        return tokens['access_token']
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        return getattr(g, 'current_user', None)
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_reset_token():
        """Generate password reset token"""
        return str(uuid.uuid4())


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Decode token
        payload = SecurityUtils.decode_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Get user
        current_user = User.find_by_id(payload['user_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'message': 'User not found or inactive'}), 401
        
        # Store current user in g
        g.current_user = current_user
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = SecurityUtils.get_current_user()
        
        if not current_user:
            return jsonify({'message': 'Authentication required'}), 401
        
        # Check if user has admin role (you can modify this based on your role system)
        if not getattr(current_user, 'is_admin', False):
            return jsonify({'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                pass
        
        if token:
            # Decode token
            payload = SecurityUtils.decode_token(token)
            if payload:
                # Get user
                current_user = User.find_by_id(payload['user_id'])
                if current_user and current_user.is_active:
                    g.current_user = current_user
        
        return f(*args, **kwargs)
    
    return decorated


def rate_limit_by_ip(max_requests=100, window=3600):
    """Decorator for rate limiting by IP address"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Simple in-memory rate limiting (use Redis in production)
            client_ip = request.remote_addr
            
            # You can implement more sophisticated rate limiting here
            # For now, we'll just pass through
            return f(*args, **kwargs)
        
        return decorated
    return decorator


class PasswordValidator:
    """Password validation utilities"""
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            errors.append("Password must contain at least one special character")
        
        return errors
    
    @staticmethod
    def is_common_password(password):
        """Check if password is commonly used (basic check)"""
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        return password.lower() in common_passwords


class SecurityHeaders:
    """Security headers utilities"""
    
    @staticmethod
    def apply_security_headers(response):
        """Apply security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response