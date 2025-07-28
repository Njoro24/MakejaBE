from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
from flask_jwt_extended import create_access_token, decode_token
from jwt.exceptions import InvalidTokenError
import re

from app.models.user import User, TokenBlacklist
from app.db import db
from app.services.email_service import EmailService


class AuthService:
    """Service class for handling authentication operations."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email is valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        return True, ""
        
    @staticmethod
    def register_user(email: str, password: str, first_name: str, last_name: str, 
                     phone_number: str = None) -> Dict[str, Any]:
        """
        Register a new user with email verification.
        
        Args:
            email: User's email address
            password: User's password (plain text)
            first_name: User's first name
            last_name: User's last name
            phone_number: User's phone number (optional)
            
        Returns:
            Dict containing user info and verification status
            
        Raises:
            ValueError: If validation fails or user already exists
        """
        # Validate input
        email = email.strip().lower()
        if not AuthService.validate_email(email):
            raise ValueError("Invalid email format")
        
        is_valid_password, password_error = AuthService.validate_password(password)
        if not is_valid_password:
            raise ValueError(password_error)
        
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First name and last name are required")
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        try:
            # Create new user
            user = User(
                email=email,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone_number=phone_number.strip() if phone_number else None
            )
            
            # Set password using the model's method
            user.set_password(password)
            
            # Generate verification token
            verification_token = user.generate_verification_token()
            
            # Save user to database
            user.save()
            
            # Send verification email
            email_sent = EmailService.send_verification_email(
                user_email=email,
                user_name=user.full_name,
                token=verification_token
            )
            
            return {
                "success": True,
                "message": "Registration successful! Please check your email to verify your account.",
                "user": user.serialize(),
                "email_sent": email_sent,
                "verification_required": True
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            raise ValueError("Registration failed due to server error")
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password (plain text)
            
        Returns:
            Dict containing user info and access token
            
        Raises:
            ValueError: If authentication fails
        """
        email = email.strip().lower()
        
        # Validate email format
        if not AuthService.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Find user by email
        user = User.find_by_email(email)
        
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Check if email is verified
        if not user.is_email_verified:
            raise ValueError("Please verify your email before logging in")
        
        try:
            # Update user's updated_at timestamp (last activity)
            user.update(updated_at=datetime.utcnow())
            
            # Generate access token
            access_token = create_access_token(identity=user.id)
            
            return {
                "success": True,
                "message": "Login successful",
                "user": user.serialize(),
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            raise ValueError("Authentication failed due to server error")
    
    @staticmethod
    def verify_email(token: str) -> Dict[str, Any]:
        """
        Verify user's email address using verification token.
        
        Args:
            token: Email verification token
            
        Returns:
            Dict containing verification result
            
        Raises:
            ValueError: If token is invalid or expired
        """
        if not token:
            raise ValueError("Verification token is required")
        
        # Find user with this token
        user = User.find_by_verification_token(token)
        
        if not user:
            raise ValueError("Invalid verification token")
        
        # Check if token is valid and not expired
        if not user.is_verification_token_valid(token):
            raise ValueError("Verification token has expired")
        
        # Check if already verified
        if user.is_email_verified:
            return {
                "success": True,
                "message": "Email already verified",
                "user": user.serialize()
            }
        
        try:
            # Verify the user
            user.verify_email()
            db.session.commit()
            
            return {
                "success": True,
                "message": "Email verified successfully! You can now log in.",
                "user": user.serialize()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Email verification error: {str(e)}")
            raise ValueError("Email verification failed due to server error")
    
    @staticmethod
    def resend_verification_email(email: str) -> Dict[str, Any]:
        """
        Resend email verification token.
        
        Args:
            email: User's email address
            
        Returns:
            Dict containing operation result
            
        Raises:
            ValueError: If user not found or already verified
        """
        email = email.strip().lower()
        
        if not AuthService.validate_email(email):
            raise ValueError("Invalid email format")
        
        user = User.find_by_email(email)
        if not user:
            raise ValueError("User not found")
        
        if user.is_email_verified:
            raise ValueError("Email already verified")
        
        try:
            # Generate new verification token
            verification_token = user.generate_verification_token()
            db.session.commit()
            
            # Send verification email
            email_sent = EmailService.send_verification_email(
                user_email=email,
                user_name=user.full_name,
                token=verification_token
            )
            
            if email_sent:
                return {
                    "success": True,
                    "message": "Verification email sent successfully!"
                }
            else:
                raise ValueError("Failed to send verification email")
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Resend verification error: {str(e)}")
            raise ValueError("Failed to resend verification email")
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            Dict with success message
            
        Raises:
            ValueError: If current password is wrong or new password is invalid
        """
        # Get user
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not user.check_password(current_password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        is_valid_password, password_error = AuthService.validate_password(new_password)
        if not is_valid_password:
            raise ValueError(password_error)
        
        try:
            # Update password
            user.set_password(new_password)
            user.update(updated_at=datetime.utcnow())
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Change password error: {str(e)}")
            raise ValueError("Failed to change password")
    
    @staticmethod
    def request_password_reset(email: str) -> Dict[str, Any]:
        """
        Generate password reset token for user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with operation result
        """
        email = email.strip().lower()
        
        if not AuthService.validate_email(email):
            raise ValueError("Invalid email format")
        
        user = User.find_by_email(email)
        if not user:
            # Don't reveal if email exists for security
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent"
            }
        
        try:
            # Generate password reset token
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # Send password reset email
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
            email_sent = EmailService.send_password_reset_email(
                user_email=email,
                user_name=user.full_name,
                reset_url=reset_url
            )
            
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent",
                "email_sent": email_sent
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset request error: {str(e)}")
            raise ValueError("Failed to process password reset request")
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user's password using reset token.
        
        Args:
            token: Password reset token
            new_password: New password (plain text)
            
        Returns:
            Dict with success message
            
        Raises:
            ValueError: If token is invalid or password is weak
        """
        if not token:
            raise ValueError("Reset token is required")
        
        # Find user with this token
        user = User.find_by_reset_token(token)
        
        if not user:
            raise ValueError("Invalid reset token")
        
        # Check if token is still valid
        if not user.is_reset_token_valid():
            raise ValueError("Reset token has expired")
        
        # Validate new password
        is_valid_password, password_error = AuthService.validate_password(new_password)
        if not is_valid_password:
            raise ValueError(password_error)
        
        try:
            # Update password and clear reset token
            user.set_password(new_password)
            user.clear_reset_token()
            user.update(updated_at=datetime.utcnow())
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset error: {str(e)}")
            raise ValueError("Failed to reset password")
    
    @staticmethod
    def logout_user(token: str) -> Dict[str, Any]:
        """
        Logout user by blacklisting their token.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict with success message
        """
        try:
            # Decode token to get expiration time
            decoded_token = decode_token(token)
            jti = decoded_token['jti']
            expires_at = datetime.fromtimestamp(decoded_token['exp'])
            
            # Add token to blacklist
            TokenBlacklist.blacklist_token(jti, expires_at)
            
            return {
                "success": True,
                "message": "Logged out successfully"
            }
            
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            raise ValueError("Failed to logout")
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object or None if not found
        """
        return User.find_by_id(user_id)
    
    @staticmethod
    def deactivate_user(user_id: int) -> Dict[str, Any]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict with success message
            
        Raises:
            ValueError: If user not found
        """
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            user.update(is_active=False, updated_at=datetime.utcnow())
            
            return {
                "success": True,
                "message": "User account deactivated successfully"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deactivate user error: {str(e)}")
            raise ValueError("Failed to deactivate user")
    
    @staticmethod
    def activate_user(user_id: int) -> Dict[str, Any]:
        """
        Activate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict with success message
            
        Raises:
            ValueError: If user not found
        """
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            user.update(is_active=True, updated_at=datetime.utcnow())
            
            return {
                "success": True,
                "message": "User account activated successfully"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Activate user error: {str(e)}")
            raise ValueError("Failed to activate user")