from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.db import User
from ..utils.validators import validate_email
from ..utils.security import get_password_hash
from datetime import timedelta


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict containing user profile data
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

    def update_user_profile(self, user_id: int, full_name: Optional[str] = None, 
                           email: Optional[str] = None) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: User's ID
            full_name: New full name (optional)
            email: New email address (optional)
            
        Returns:
            Dict containing updated user profile data
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update full name if provided
        if full_name is not None:
            user.full_name = full_name.strip()
        
        # Update email if provided
        if email is not None:
            email = email.lower()
            
            # Validate email format
            if not validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            # Check if email is already taken by another user
            if email != user.email:
                existing_user = self.get_user_by_email(email)
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already taken"
                    )
                user.email = email
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

    def delete_user(self, user_id: int) -> Dict[str, str]:
        """
        Soft delete a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict with success message
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete by deactivating the account
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return {"message": "User account deleted successfully"}

    def get_all_users(self, skip: int = 0, limit: int = 100, 
                     active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Whether to return only active users
            
        Returns:
            List of user dictionaries
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        users = query.offset(skip).limit(limit).all()
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ]

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search users by name or email.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching user dictionaries
        """
        search_term = f"%{query.lower()}%"
        
        users = self.db.query(User).filter(
            and_(
                User.is_active == True,
                or_(
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ]

    def get_user_count(self, active_only: bool = True) -> int:
        """
        Get total number of users.
        
        Args:
            active_only: Whether to count only active users
            
        Returns:
            Total user count
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.count()

    def create_user(self, email: str, password: str, full_name: str, 
                   is_active: bool = True) -> Dict[str, Any]:
        """
        Create a new user (admin function).
        
        Args:
            email: User's email address
            password: User's password (plain text)
            full_name: User's full name
            is_active: Whether user should be active
            
        Returns:
            Dict containing new user data
            
        Raises:
            HTTPException: If validation fails or user already exists
        """
        # Validate email
        if not validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user already exists
        existing_user = self.get_user_by_email(email)
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
            is_active=is_active
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at
        }

    def update_user_status(self, user_id: int, is_active: bool) -> Dict[str, Any]:
        """
        Update user active status (admin function).
        
        Args:
            user_id: User's ID
            is_active: New active status
            
        Returns:
            Dict containing updated user data
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = is_active
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dict containing user statistics
        """
        total_users = self.get_user_count(active_only=False)
        active_users = self.get_user_count(active_only=True)
        inactive_users = total_users - active_users
        
        # Get recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # Get recent logins (last 30 days)
        recent_logins = self.db.query(User).filter(
            and_(
                User.last_login >= thirty_days_ago,
                User.is_active == True
            )
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "recent_registrations": recent_registrations,
            "recent_logins": recent_logins
        }

    def bulk_update_users(self, user_ids: List[int], 
                         updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bulk update multiple users (admin function).
        
        Args:
            user_ids: List of user IDs to update
            updates: Dictionary of fields to update
            
        Returns:
            Dict with update results
            
        Raises:
            HTTPException: If invalid update fields provided
        """
        # Validate update fields
        allowed_fields = {"is_active", "full_name"}
        invalid_fields = set(updates.keys()) - allowed_fields
        
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid update fields: {', '.join(invalid_fields)}"
            )
        
        # Update users
        updated_count = 0
        for user_id in user_ids:
            user = self.get_user_by_id(user_id)
            if user:
                for field, value in updates.items():
                    setattr(user, field, value)
                user.updated_at = datetime.utcnow()
                updated_count += 1
        
        self.db.commit()
        
        return {
            "updated_count": updated_count,
            "total_requested": len(user_ids),
            "message": f"Successfully updated {updated_count} users"
        }


def get_user_service(db: Session) -> UserService:
    """
    Dependency to get UserService instance.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)