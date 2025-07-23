"""
User management routes for profile operations and admin functions.
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from app.models.user import User  # Import your User model
import logging

logger = logging.getLogger(__name__)

# Create the blueprint directly (simplified approach)
user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
def get_users():
    """
    Get list of users.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    - search: Search term for email/name
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        search = request.args.get('search', '').strip()
        
        # Basic query
        query = User.query
        
        # Add search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                User.email.like(search_filter) | 
                User.first_name.like(search_filter) | 
                User.last_name.like(search_filter)
            )
        
        # Paginate results
        users_pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Serialize users
        users_data = [user.serialize() for user in users_pagination.items]
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users_pagination.total,
                'pages': users_pagination.pages
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid query parameters',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve users',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
    """
    try:
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404
        
        return jsonify({
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve user',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user profile.
    
    Args:
        user_id: User ID
        
    Expected JSON:
    {
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "string"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Invalid content type',
                'message': 'Content-Type must be application/json'
            }), 400
        
        # Check if user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404
        
        # Get update data
        update_data = request.json
        allowed_fields = ['email', 'first_name', 'last_name', 'phone_number']
        
        # Filter only allowed fields
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return jsonify({
                'error': 'No valid fields to update',
                'message': f'Allowed fields: {", ".join(allowed_fields)}'
            }), 400
        
        # Check if email is being changed and if it's unique
        if 'email' in filtered_data and filtered_data['email'] != user.email:
            existing_user = User.find_by_email(filtered_data['email'])
            if existing_user:
                return jsonify({
                    'error': 'Email already exists',
                    'message': 'This email is already registered'
                }), 400
        
        # Update user
        user.update(**filtered_data)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({
            'error': 'Update failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete user account.
    
    Args:
        user_id: User ID
    """
    try:
        # Check if user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404
        
        # Delete user
        user.delete()
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({
            'error': 'Delete failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('', methods=['POST'])
def create_user():
    """
    Create new user.
    
    Expected JSON:
    {
        "email": "string",
        "password": "string",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "string" (optional)
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Invalid content type',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.json
        required_fields = ['email', 'password', 'first_name', 'last_name']
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'message': f'Required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Check if email already exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({
                'error': 'Email already exists',
                'message': 'This email is already registered'
            }), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number')
        )
        
        # Set password
        user.set_password(data['password'])
        
        # Save user
        user.save()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.serialize()
        }), 201
        
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        return jsonify({
            'error': 'User creation failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/search', methods=['GET'])
def search_users():
    """
    Search users by email or name.
    
    Query parameters:
    - q: Search query
    - limit: Maximum results (default: 10, max: 50)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not query:
            return jsonify({
                'error': 'Missing search query',
                'message': 'Search query (q) is required'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'error': 'Search query too short',
                'message': 'Search query must be at least 2 characters'
            }), 400
        
        # Search users
        search_filter = f"%{query}%"
        users = User.query.filter(
            User.email.like(search_filter) | 
            User.first_name.like(search_filter) | 
            User.last_name.like(search_filter)
        ).limit(limit).all()
        
        # Serialize users
        users_data = [user.serialize() for user in users]
        
        return jsonify({
            'users': users_data,
            'count': len(users)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid query parameters',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Search users error: {str(e)}")
        return jsonify({
            'error': 'Search failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for user service.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'users',
        'version': '1.0.0'
    }), 200