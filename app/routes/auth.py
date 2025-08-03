from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService
from app.models.user import TokenBlacklist
from datetime import datetime
from flask_cors import cross_origin


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email verification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract input data
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone_number = data.get('phone_number', '').strip() if data.get('phone_number') else None
        
        # Validate required fields
        if not all([email, password, first_name, last_name]):
            return jsonify({'error': 'Email, password, first name, and last name are required'}), 400
        
        # Use AuthService to register user
        result = AuthService.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed due to server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"Login attempt - Email: {email}")
        
        # Check if user exists and their status
        from app.models.user import User
        user = User.find_by_email(email.lower())
        if user:
            print(f"User found - Email verified: {user.is_email_verified}, Active: {user.is_active}")  # DEBUG
            print(f"Password check: {user.check_password(password)}")  # DEBUG
        else:
            print("User not found") 
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Use AuthService to authenticate user
        result = AuthService.authenticate_user(email=email, password=password)
        
        return jsonify(result), 200
        
    except ValueError as e:
        print(f"Auth error: {str(e)}")
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Token verification failed'}), 401

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    """Verify user's email address"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Verification token is required'}), 400
        
        # Use AuthService to verify email
        result = AuthService.verify_email(token=token)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Email verification failed due to server error'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Use AuthService to resend verification
        result = AuthService.resend_verification_email(email=email)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification email'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        return jsonify({
            'user': user.serialize()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user's password"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Use AuthService to change password
        result = AuthService.change_password(
            user_id=current_user_id,
            current_password=current_password,
            new_password=new_password
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Use AuthService to request password reset
        result = AuthService.request_password_reset(email=email)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Failed to process password reset request'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # Use AuthService to reset password
        result = AuthService.reset_password(token=token, new_password=new_password)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': 'Failed to reset password'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by blacklisting token"""
    try:
        jti = get_jwt()['jti']
        
        # Check if token is already blacklisted
        if TokenBlacklist.is_blacklisted(jti):
            return jsonify({'error': 'Token already invalidated'}), 400
        
        # Get the raw token from request headers
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Use AuthService to logout
            result = AuthService.logout_user(token=token)
            
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Invalid authorization header'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Failed to logout'}), 500

@auth_bp.route('/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_account():
    """Deactivate current user's account"""
    try:
        current_user_id = get_jwt_identity()
        
        # Use AuthService to deactivate user
        result = AuthService.deactivate_user(user_id=current_user_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Deactivate account error: {str(e)}")
        return jsonify({'error': 'Failed to deactivate account'}), 500

@auth_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Auth routes working!',
        'service': 'AuthService integration active',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@auth_bp.route('/verify', methods=['GET', 'OPTIONS'])
@cross_origin(origins="http://127.0.0.1:5173", supports_credentials=True)
@jwt_required()
def verify_token():
    """Verify if token is valid and return user info"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'message': 'Token is valid',
            'user': user.serialize()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Token verification failed'}), 401