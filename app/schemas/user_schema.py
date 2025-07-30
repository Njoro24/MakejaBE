from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.user import User
import re

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.Str(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    
    @validates('password')
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')
    
    @validates('phone')
    def validate_phone(self, phone):
        """Validate phone number format"""
        if phone:
            # Remove spaces and common separators
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?[\d]{10,15}$', clean_phone):
                raise ValidationError('Invalid phone number format')
    
    @post_load
    def validate_passwords_match(self, data, **kwargs):
        """Validate that passwords match"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')
        # Remove confirm_password from data
        data.pop('confirm_password', None)
        return data


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    remember_me = fields.Bool(missing=False)


class UserProfileSchema(Schema):
    """Schema for user profile updates"""
    first_name = fields.Str(validate=validate.Length(min=2, max=100))
    last_name = fields.Str(validate=validate.Length(min=2, max=100))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    bio = fields.Str(allow_none=True, validate=validate.Length(max=500))
    profile_picture = fields.Str(allow_none=True, validate=validate.Length(max=500))
    
    @validates('phone')
    def validate_phone(self, phone):
        """Validate phone number format"""
        if phone:
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?[\d]{10,15}$', clean_phone):
                raise ValidationError('Invalid phone number format')


class ChangePasswordSchema(Schema):
    """Schema for password change"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_new_password = fields.Str(required=True)
    
    @validates('new_password')
    def validate_new_password(self, password):
        """Validate new password strength"""
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')
    
    @post_load
    def validate_passwords_match(self, data, **kwargs):
        """Validate that new passwords match"""
        if data.get('new_password') != data.get('confirm_new_password'):
            raise ValidationError('New passwords do not match', field_name='confirm_new_password')
        # Remove confirm_new_password from data
        data.pop('confirm_new_password', None)
        return data


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request"""
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    """Schema for password reset"""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_new_password = fields.Str(required=True)
    
    @validates('new_password')
    def validate_new_password(self, password):
        """Validate new password strength"""
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')
    
    @post_load
    def validate_passwords_match(self, data, **kwargs):
        """Validate that passwords match"""
        if data.get('new_password') != data.get('confirm_new_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_new_password')
        # Remove confirm_new_password from data
        data.pop('confirm_new_password', None)
        return data


class UserResponseSchema(SQLAlchemyAutoSchema):
    """Schema for user response serialization"""
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash', 'reset_token', 'reset_token_expires')
    
    full_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = fields.DateTime(dump_only=True, format='%Y-%m-%d %H:%M:%S')


class UserListResponseSchema(Schema):
    """Schema for paginated user list response"""
    users = fields.List(fields.Nested(UserResponseSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()


class AuthResponseSchema(Schema):
    """Schema for authentication response"""
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    token_type = fields.Str(missing='Bearer')
    expires_in = fields.Int()
    user = fields.Nested(UserResponseSchema)


class RefreshTokenSchema(Schema):
    """Schema for token refresh"""
    refresh_token = fields.Str(required=True)


# Schema instances for reuse
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_profile_schema = UserProfileSchema()
change_password_schema = ChangePasswordSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
user_response_schema = UserResponseSchema()
user_list_response_schema = UserListResponseSchema()
auth_response_schema = AuthResponseSchema()
refresh_token_schema = RefreshTokenSchema()