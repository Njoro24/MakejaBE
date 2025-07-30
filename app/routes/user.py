"""
User management routes for profile operations and admin functions.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.db import db
import logging
import re

logger = logging.getLogger(__name__)

# Create the blueprint
user_bp = Blueprint('users', __name__)

def validate_email(email):
    """Enhanced email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@user_bp.route('', methods=['GET'])
@jwt_required()  # Protect user listing
def get_users():
    """
    Get list of users with pagination and search.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    - search: Search term for email/name
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        search = request.args.get('search', '').strip()
        
        # Ensure positive values
        page = max(1, page)
        per_page = max(1, per_page)
        
        # Basic query - only active users
        query = User.query.filter(User.is_active == True)
        
        # Add search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.email.ilike(search_filter),  # Case-insensitive search
                    User.first_name.ilike(search_filter),
                    User.last_name.ilike(search_filter),
                    db.func.concat(User.first_name, ' ', User.last_name).ilike(search_filter)
                )
            )
        
        # Order by created_at for consistent pagination
        query = query.order_by(User.created_at.desc())
        
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
                'pages': users_pagination.pages,
                'has_prev': users_pagination.has_prev,
                'has_next': users_pagination.has_next
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
@jwt_required()
def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.find_by_id(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Authentication failed'}), 401
        
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404
        
        # Users can only view their own profile unless they're admin
        if current_user_id != user_id:
            # Add admin check here if you have admin roles
            # For now, anyone can view other users (adjust as needed)
            pass
        
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
@jwt_required()
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
        current_user_id = get_jwt_identity()
        
        # Users can only update their own profile
        if current_user_id != user_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You can only update your own profile'
            }), 403
        
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
        
        # Filter only allowed fields and non-empty values
        filtered_data = {}
        for k, v in update_data.items():
            if k in allowed_fields and v is not None:
                if isinstance(v, str):
                    v = v.strip()
                    if v:  # Only add non-empty strings
                        filtered_data[k] = v
                else:
                    filtered_data[k] = v
        
        if not filtered_data:
            return jsonify({
                'error': 'No valid fields to update',
                'message': f'Allowed fields: {", ".join(allowed_fields)}'
            }), 400
        
        # Validate email if being updated
        if 'email' in filtered_data:
            new_email = filtered_data['email'].lower()
            if not validate_email(new_email):
                return jsonify({
                    'error': 'Invalid email format',
                    'message': 'Please provide a valid email address'
                }), 400
            
            # Check if email is being changed and if it's unique
            if new_email != user.email.lower():
                existing_user = User.find_by_email(new_email)
                if existing_user:
                    return jsonify({
                        'error': 'Email already exists',
                        'message': 'This email is already registered'
                    }), 400
                filtered_data['email'] = new_email
        
        # Update user
        user.update(**filtered_data)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update user error: {str(e)}")
        return jsonify({
            'error': 'Update failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete/deactivate user account.
    
    Args:
        user_id: User ID
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only delete their own profile
        if current_user_id != user_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You can only delete your own account'
            }), 403
        
        # Check if user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404
        
        # Instead of hard delete, deactivate the user (soft delete)
        user.update(is_active=False)
        
        return jsonify({
            'message': 'Account deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({
            'error': 'Delete failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('', methods=['POST'])
@jwt_required()  # Protect user creation
def create_user():
    """
    Create new user (Admin function).
    
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
        missing_fields = []
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'message': f'Required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email
        email = data['email'].strip().lower()
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email format',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Validate password
        if len(data['password']) < 6:
            return jsonify({
                'error': 'Password too short',
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        # Check if email already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({
                'error': 'Email already exists',
                'message': 'This email is already registered'
            }), 400
        
        # Create new user
        user = User(
            email=email,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone_number=data.get('phone_number', '').strip() or None
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
        db.session.rollback()
        logger.error(f"Create user error: {str(e)}")
        return jsonify({
            'error': 'User creation failed',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/search', methods=['GET'])
@jwt_required()
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
        
        # Search users (only active ones)
        search_filter = f"%{query}%"
        users = User.query.filter(
            User.is_active == True
        ).filter(
            db.or_(
                User.email.ilike(search_filter),
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
                db.func.concat(User.first_name, ' ', User.last_name).ilike(search_filter)
            )
        ).limit(limit).all()
        
        # Serialize users
        users_data = [user.serialize() for user in users]
        
        return jsonify({
            'users': users_data,
            'count': len(users),
            'query': query
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

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user's profile.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve profile',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for user service.
    """
    try:
        # Test database connection
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'service': 'users',
            'version': '1.0.0',
            'database': 'connected',
            'total_users': user_count
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'users',
            'version': '1.0.0',
            'database': 'disconnected',
            'error': str(e)
        }), 500