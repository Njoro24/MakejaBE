from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

from ..database.models import User
from ..database.session import get_db
from ..utils.security import create_access_token, verify_token, get_password_hash, verify_password
from ..utils.validators import validate_email, validate_password
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """
        Register a new user with email and password.
        
        Args:
            email: User's email address
            password: User's password (plain text)
            full_name: User's full name
            
        Returns:
            Dict containing user info and access token
            
        Raises:
            HTTPException: If validation fails or user already exists
        """
        # Validate input
        if not validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        if not validate_password(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number"
            )
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            is_active=True
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id}
        )
        
        return {
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "is_active": new_user.is_active,
                "created_at": new_user.created_at
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password (plain text)
            
        Returns:
            Dict containing user info and access token
            
        Raises:
            HTTPException: If authentication fails
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "created_at": user.created_at
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            payload = verify_token(token)
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Find user in database
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is still active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        return user

    def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh an access token.
        
        Args:
            token: Current JWT access token
            
        Returns:
            Dict containing new access token
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = verify_token(token, verify_expiration=False)  # Don't verify expiration for refresh
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Verify user still exists and is active
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        new_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, str]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            Dict with success message
            
        Raises:
            HTTPException: If current password is wrong or new password is invalid
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return {"message": "Password changed successfully"}

    def deactivate_user(self, user_id: int) -> Dict[str, str]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict with success message
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return {"message": "User account deactivated successfully"}

    def activate_user(self, user_id: int) -> Dict[str, str]:
        """
        Activate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict with success message
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return {"message": "User account activated successfully"}

    def reset_password_request(self, email: str) -> Dict[str, str]:
        """
        Generate password reset token for user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with reset token (in production, this would be sent via email)
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user:
            # Don't reveal if email exists for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate password reset token (expires in 1 hour)
        reset_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # In production, you would send this token via email
        # For now, we'll return it in the response
        return {
            "message": "Password reset token generated",
            "reset_token": reset_token  # Remove this in production
        }

    def reset_password(self, token: str, new_password: str) -> Dict[str, str]:
        """
        Reset user's password using reset token.
        
        Args:
            token: Password reset token
            new_password: New password (plain text)
            
        Returns:
            Dict with success message
            
        Raises:
            HTTPException: If token is invalid or password is weak
        """
        try:
            payload = verify_token(token)
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            token_type: str = payload.get("type")
            
            if email is None or user_id is None or token_type != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
                
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Find user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate new password
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return {"message": "Password reset successfully"}


def get_auth_service(db: Session = None) -> AuthService:
    """
    Dependency to get AuthService instance.
    
    Args:
        db: Database session
        
    Returns:
        AuthService instance
    """
    if db is None:
        db = next(get_db())
    return AuthService(db)