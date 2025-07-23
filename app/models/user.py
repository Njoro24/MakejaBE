from app.db import db
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import uuid

bcrypt = Bcrypt()

class User(db.Model): 
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password using Flask-Bcrypt"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def clear_reset_token(self):
        """Clear password reset token"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def is_reset_token_valid(self):
        """Check if reset token is still valid"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        return datetime.utcnow() < self.reset_token_expires
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def serialize(self):
        """Serialize user data (excluding sensitive information)"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'full_name': self.full_name
        }
    
    def serialize_with_token(self, access_token, refresh_token=None):
        """Serialize user data with authentication tokens"""
        user_data = self.serialize()
        user_data['access_token'] = access_token
        if refresh_token:
            user_data['refresh_token'] = refresh_token
        return user_data
    
    def save(self):
        """Save user to database"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete user from database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Update user attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        return cls.query.get(user_id)
    
    @classmethod
    def find_by_reset_token(cls, token):
        """Find user by reset token"""
        return cls.query.filter_by(reset_token=token).first()
    
    def __repr__(self):
        return f"<User {self.email}>"


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"
    
    id = db.Column(db.Integer, primary_key=True)
    token_jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def save(self):
        """Save token to blacklist"""
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_blacklisted(cls, jti):
        """Check if token is blacklisted"""
        token = cls.query.filter_by(token_jti=jti).first()
        return token is not None
    
    @classmethod
    def blacklist_token(cls, jti, expires_at):
        """Add token to blacklist"""
        blacklisted_token = cls(token_jti=jti, expires_at=expires_at)
        blacklisted_token.save()
    
    def __repr__(self):
        return f"<TokenBlacklist {self.token_jti}>"