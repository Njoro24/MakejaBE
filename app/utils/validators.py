import re
from flask import request
from functools import wraps
from marshmallow import ValidationError
import phonenumbers
from phonenumbers import NumberParseException
from typing import Dict, List, Any, Optional
import bleach
from urllib.parse import urlparse


class ValidationUtils:
    """Utility class for common validation operations"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def validate_phone(phone: str, country_code: str = None) -> Dict[str, Any]:
        """Validate phone number with detailed response"""
        if not phone:
            return {'valid': False, 'message': 'Phone number is required'}
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone, country_code)
            
            # Check if valid
            if not phonenumbers.is_valid_number(parsed_number):
                return {'valid': False, 'message': 'Invalid phone number'}
            
            # Format phone number
            formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
            return {
                'valid': True,
                'formatted': formatted,
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number
            }
            
        except NumberParseException as e:
            return {'valid': False, 'message': f'Invalid phone number: {str(e)}'}
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Comprehensive password validation"""
        errors = []
        score = 0
        
        if not password:
            return {'valid': False, 'errors': ['Password is required'], 'score': 0}
        
        # Length check
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        elif len(password) >= 12:
            score += 1
        
        # Character type checks
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        else:
            score += 1
        
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        else:
            score += 1
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        else:
            score += 1
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        else:
            score += 1
        
        # Common password check
        if ValidationUtils.is_common_password(password):
            errors.append('Password is too common, please choose a different one')
        
        # Sequential characters check
        if ValidationUtils.has_sequential_chars(password):
            errors.append('Password should not contain sequential characters')
        
        # Strength scoring
        strength_levels = {
            0: 'Very Weak',
            1: 'Weak',
            2: 'Fair',
            3: 'Good',
            4: 'Strong',
            5: 'Very Strong'
        }
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'score': score,
            'strength': strength_levels.get(score, 'Unknown')
        }
    
    @staticmethod
    def is_common_password(password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'pass', 'master', 'hello', 'freedom',
            'whatever', 'qazwsx', 'trustno1', 'jordan23', 'harley',
            'password1', '1234567', 'soccer', 'rock', 'princess',
            'abc123', 'baseball', 'football', 'monkey', 'letmein',
            'shadow', 'master', 'jordan', 'superman', 'harley'
        ]
        return password.lower() in common_passwords
    
    @staticmethod
    def has_sequential_chars(password: str) -> bool:
        """Check for sequential characters in password"""
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        
        password_lower = password.lower()
        
        for sequence in sequences:
            for i in range(len(sequence) - 2):
                if sequence[i:i+3] in password_lower:
                    return True
        
        return False
    
    @staticmethod
    def validate_name(name: str, field_name: str = 'Name') -> Dict[str, Any]:
        """Validate name fields"""
        if not name:
            return {'valid': False, 'message': f'{field_name} is required'}
        
        if len(name.strip()) < 2:
            return {'valid': False, 'message': f'{field_name} must be at least 2 characters long'}
        
        if len(name.strip()) > 100:
            return {'valid': False, 'message': f'{field_name} must be less than 100 characters'}
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
            return {'valid': False, 'message': f'{field_name} can only contain letters, spaces, hyphens, dots, and apostrophes'}
        
        return {'valid': True, 'message': 'Valid name'}
    
    @staticmethod
    def validate_url(url: str) -> Dict[str, Any]:
        """Validate URL format"""
        if not url:
            return {'valid': False, 'message': 'URL is required'}
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return {'valid': False, 'message': 'Invalid URL format'}
            
            if result.scheme not in ['http', 'https']:
                return {'valid': False, 'message': 'URL must use HTTP or HTTPS'}
            
            return {'valid': True, 'message': 'Valid URL'}
            
        except Exception:
            return {'valid': False, 'message': 'Invalid URL format'}
    
    @staticmethod
    def sanitize_input(input_str: str, allowed_tags: List[str] = None) -> str:
        """Sanitize user input to prevent XSS"""
        if not input_str:
            return ''
        
        if allowed_tags is None:
            allowed_tags = []
        
        return bleach.clean(input_str, tags=allowed_tags, strip=True)
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return extension in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 5) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes


class RequestValidator:
    """Request validation utilities"""
    
    @staticmethod
    def validate_json_request():
        """Validate that request contains JSON data"""
        if not request.is_json:
            return False, {'message': 'Request must contain JSON data'}
        
        if not request.get_json():
            return False, {'message': 'Request body cannot be empty'}
        
        return True, None
    
    @staticmethod
    def validate_content_type(allowed_types: List[str]):
        """Validate request content type"""
        content_type = request.content_type
        
        if not content_type:
            return False, {'message': 'Content-Type header is required'}
        
        if not any(allowed_type in content_type for allowed_type in allowed_types):
            return False, {'message': f'Content-Type must be one of: {", ".join(allowed_types)}'}
        
        return True, None
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> Dict[str, Any]:
        """Validate required fields in request data"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }
        
        return {'valid': True}


def validate_request_data(schema_class, partial=False):
    """Decorator to validate request data using Marshmallow schema"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Validate JSON request
            is_valid, error = RequestValidator.validate_json_request()
            if not is_valid:
                return error, 400
            
            # Get request data
            data = request.get_json()
            
            # Validate using schema
            try:
                schema = schema_class()
                if partial:
                    validated_data = schema.load(data, partial=True)
                else:
                    validated_data = schema.load(data)
                
                # Add validated data to request
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as err:
                return {'errors': err.messages}, 400
        
        return decorated
    return decorator


def validate_query_params(allowed_params: List[str], required_params: List[str] = None):
    """Decorator to validate query parameters"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check for unknown parameters
            unknown_params = set(request.args.keys()) - set(allowed_params)
            if unknown_params:
                return {
                    'message': f'Unknown query parameters: {", ".join(unknown_params)}'
                }, 400
            
            # Check for required parameters
            if required_params:
                missing_params = set(required_params) - set(request.args.keys())
                if missing_params:
                    return {
                        'message': f'Missing required query parameters: {", ".join(missing_params)}'
                    }, 400
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


class PaginationValidator:
    """Pagination validation utilities"""
    
    @staticmethod
    def validate_pagination_params(page: int = 1, per_page: int = 10, max_per_page: int = 100) -> Dict[str, Any]:
        """Validate pagination parameters"""
        errors = []
        
        if page < 1:
            errors.append('Page must be greater than 0')
        
        if per_page < 1:
            errors.append('Per page must be greater than 0')
        
        if per_page > max_per_page:
            errors.append(f'Per page cannot exceed {max_per_page}')
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        return {
            'valid': True,
            'page': page,
            'per_page': per_page
        }


class SearchValidator:
    """Search validation utilities"""
    
    @staticmethod
    def validate_search_query(query: str, min_length: int = 3, max_length: int = 100) -> Dict[str, Any]:
        """Validate search query"""
        if not query:
            return {'valid': False, 'message': 'Search query is required'}
        
        query = query.strip()
        
        if len(query) < min_length:
            return {'valid': False, 'message': f'Search query must be at least {min_length} characters long'}
        
        if len(query) > max_length:
            return {'valid': False, 'message': f'Search query cannot exceed {max_length} characters'}
        
        # Sanitize query
        sanitized_query = ValidationUtils.sanitize_input(query)
        
        return {
            'valid': True,
            'query': sanitized_query
        }