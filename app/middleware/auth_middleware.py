"""
Authentication middleware for JWT token validation.
"""
from functools import wraps
from flask import request, jsonify, current_app, g
from utils.security import verify_jwt_token
from services.user_service import UserService
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """JWT Authentication middleware class."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def require_auth(self, f: Callable) -> Callable:
        """
        Decorator that requires valid JWT authentication.
        
        Args:
            f: The function to wrap
            
        Returns:
            Wrapped function that validates JWT token
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._extract_token_from_request()
            
            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'No token provided'
                }), 401
            
            try:
                # Verify token
                payload = verify_jwt_token(token)
                if not payload:
                    return jsonify({
                        'error': 'Invalid token',
                        'message': 'Token verification failed'
                    }), 401
                
                # Get user from database
                user_id = payload.get('user_id')
                if not user_id:
                    return jsonify({
                        'error': 'Invalid token',
                        'message': 'Token missing user_id'
                    }), 401
                
                user = self.user_service.get_user_by_id(user_id)
                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'message': 'Token user does not exist'
                    }), 401
                
                if not user.is_active:
                    return jsonify({
                        'error': 'Account disabled',
                        'message': 'User account is disabled'
                    }), 401
                
                # Store user in request context
                g.current_user = user
                g.token_payload = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Invalid or expired token'
                }), 401
        
        return decorated_function
    
    def optional_auth(self, f: Callable) -> Callable:
        """
        Decorator that optionally validates JWT authentication.
        If token is present, it validates it. If not, continues without auth.
        
        Args:
            f: The function to wrap
            
        Returns:
            Wrapped function that optionally validates JWT token
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._extract_token_from_request()
            
            if token:
                try:
                    # Verify token
                    payload = verify_jwt_token(token)
                    if payload:
                        user_id = payload.get('user_id')
                        if user_id:
                            user = self.user_service.get_user_by_id(user_id)
                            if user and user.is_active:
                                g.current_user = user
                                g.token_payload = payload
                except Exception as e:
                    logger.warning(f"Optional auth warning: {str(e)}")
                    # Continue without auth if token is invalid
                    pass
            
            # Set default values if no valid auth
            if not hasattr(g, 'current_user'):
                g.current_user = None
                g.token_payload = None
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_role(self, required_role: str) -> Callable:
        """
        Decorator that requires a specific user role.
        Must be used after require_auth.
        
        Args:
            required_role: The required user role
            
        Returns:
            Wrapped function that validates user role
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'Must be authenticated to access this resource'
                    }), 401
                
                if g.current_user.role != required_role:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'Role {required_role} required'
                    }), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def require_admin(self, f: Callable) -> Callable:
        """
        Decorator that requires admin role.
        Must be used after require_auth.
        
        Args:
            f: The function to wrap
            
        Returns:
            Wrapped function that validates admin role
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Must be authenticated to access this resource'
                }), 401
            
            if g.current_user.role != 'admin':
                return jsonify({
                    'error': 'Admin access required',
                    'message': 'Only administrators can access this resource'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_owner_or_admin(self, user_id_param: str = 'user_id') -> Callable:
        """
        Decorator that requires user to be resource owner or admin.
        Must be used after require_auth.
        
        Args:
            user_id_param: The parameter name containing the user ID
            
        Returns:
            Wrapped function that validates ownership or admin access
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'Must be authenticated to access this resource'
                    }), 401
                
                # Get user_id from URL parameters or request args
                target_user_id = kwargs.get(user_id_param) or request.args.get(user_id_param)
                
                if not target_user_id:
                    return jsonify({
                        'error': 'Invalid request',
                        'message': f'Missing {user_id_param} parameter'
                    }), 400
                
                # Convert to integer if needed
                try:
                    target_user_id = int(target_user_id)
                except (ValueError, TypeError):
                    return jsonify({
                        'error': 'Invalid request',
                        'message': f'Invalid {user_id_param} format'
                    }), 400
                
                # Check if user is owner or admin
                if g.current_user.id != target_user_id and g.current_user.role != 'admin':
                    return jsonify({
                        'error': 'Access denied',
                        'message': 'Can only access own resources unless admin'
                    }), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def _extract_token_from_request(self) -> Optional[str]:
        """
        Extract JWT token from request headers.
        
        Returns:
            Token string if found, None otherwise
        """
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        
        return None


# Global middleware instance (will be initialized in app factory)
auth_middleware = None

def init_auth_middleware(user_service: UserService):
    """
    Initialize the global auth middleware instance.
    
    Args:
        user_service: UserService instance
    """
    global auth_middleware
    auth_middleware = AuthMiddleware(user_service)

# Convenience decorators for easy import
def require_auth(f: Callable) -> Callable:
    """Global convenience decorator for authentication."""
    if not auth_middleware:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware.require_auth(f)

def optional_auth(f: Callable) -> Callable:
    """Global convenience decorator for optional authentication."""
    if not auth_middleware:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware.optional_auth(f)

def require_role(required_role: str) -> Callable:
    """Global convenience decorator for role-based access."""
    if not auth_middleware:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware.require_role(required_role)

def require_admin(f: Callable) -> Callable:
    """Global convenience decorator for admin access."""
    if not auth_middleware:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware.require_admin(f)

def require_owner_or_admin(user_id_param: str = 'user_id') -> Callable:
    """Global convenience decorator for owner/admin access."""
    if not auth_middleware:
        raise RuntimeError("Auth middleware not initialized")
    return auth_middleware.require_owner_or_admin(user_id_param)

def get_current_user():
    """
    Get the current authenticated user from request context.
    
    Returns:
        User object if authenticated, None otherwise
    """
    return getattr(g, 'current_user', None)

def get_token_payload():
    """
    Get the current JWT token payload from request context.
    
    Returns:
        Token payload dict if authenticated, None otherwise
    """
    return getattr(g, 'token_payload', None)