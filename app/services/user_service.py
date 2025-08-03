from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from flask import abort

from app.db import User
from ..utils.validators import validate_email
from ..utils.security import get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        user = self.get_user_by_id(user_id)
        if not user:
            abort(404, description="User not found")

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
        user = self.get_user_by_id(user_id)
        if not user:
            abort(404, description="User not found")

        if full_name is not None:
            user.full_name = full_name.strip()

        if email is not None:
            email = email.lower()
            if not validate_email(email):
                abort(400, description="Invalid email format")

            if email != user.email:
                existing_user = self.get_user_by_email(email)
                if existing_user:
                    abort(400, description="Email already taken")
                user.email = email

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
        user = self.get_user_by_id(user_id)
        if not user:
            abort(404, description="User not found")

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return {"message": "User account deleted successfully"}

    def get_all_users(self, skip: int = 0, limit: int = 100,
                      active_only: bool = True) -> List[Dict[str, Any]]:
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
        query = self.db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        return query.count()

    def create_user(self, email: str, password: str, full_name: str,
                    is_active: bool = True) -> Dict[str, Any]:
        if not validate_email(email):
            abort(400, description="Invalid email format")

        existing_user = self.get_user_by_email(email)
        if existing_user:
            abort(400, description="User with this email already exists")

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
        user = self.get_user_by_id(user_id)
        if not user:
            abort(404, description="User not found")

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
        total_users = self.get_user_count(active_only=False)
        active_users = self.get_user_count(active_only=True)
        inactive_users = total_users - active_users

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()

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
        allowed_fields = {"is_active", "full_name"}
        invalid_fields = set(updates.keys()) - allowed_fields

        if invalid_fields:
            abort(400, description=f"Invalid update fields: {', '.join(invalid_fields)}")

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
    return UserService(db)
