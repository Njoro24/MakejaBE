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
    profile_picture = db.Column(db.Text, nullable=True)  # Changed to Text for longer URLs
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_expires = db.Column(db.DateTime, nullable=True)

    # PostgreSQL specific indexes for better performance
    __table_args__ = (
        db.Index('idx_user_email_active', 'email', 'is_active'),
        db.Index('idx_user_verification_token', 'email_verification_token'),
        db.Index('idx_user_reset_token', 'reset_token'),
    )

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
    
    def generate_verification_token(self):
        """Generate email verification token"""
        self.email_verification_token = str(uuid.uuid4())
        self.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return self.email_verification_token
    
    def is_verification_token_valid(self, token):
        """Check if email verification token is valid"""
        if not self.email_verification_token or not self.email_verification_expires:
            return False
        if self.email_verification_token != token:
            return False
        return datetime.utcnow() < self.email_verification_expires
    
    def verify_email(self):
        """Mark email as verified and clear verification token"""
        self.is_email_verified = True
        self.email_verification_token = None
        self.email_verification_expires = None
        self.updated_at = datetime.utcnow()
    
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
            'is_email_verified': self.is_email_verified,
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
    
    @classmethod
    def find_by_verification_token(cls, token):
        """Find user by email verification token"""
        return cls.query.filter_by(email_verification_token=token).first()
    
    def __repr__(self):
        return f"<User {self.email}>"


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"
    
    id = db.Column(db.Integer, primary_key=True)
    token_jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # PostgreSQL specific indexes
    __table_args__ = (
        db.Index('idx_token_blacklist_jti', 'token_jti'),
        db.Index('idx_token_blacklist_expires', 'expires_at'),
    )
    
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
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """Remove expired tokens from blacklist (for maintenance)"""
        expired_tokens = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for token in expired_tokens:
            db.session.delete(token)
        db.session.commit()
        return len(expired_tokens)
    
    def __repr__(self):
        return f"<TokenBlacklist {self.token_jti}>"