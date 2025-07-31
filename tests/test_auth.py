# """
# Tests for authentication routes and services.
# """
# import pytest
# import json
# from unittest.mock import Mock, patch, MagicMock
# from flask import Flask
# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash

# from routes.auth import create_auth_routes
# from services.auth_service import AuthService
# from services.user_service import UserService
# from models.user import User
# from utils.security import generate_jwt_token, verify_jwt_token
# from utils.response import ServiceResponse


# class TestAuthRoutes:
#     """Test cases for authentication routes."""
    
#     @pytest.fixture
#     def app(self):
#         """Create test Flask app."""
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'test-secret-key'
#         app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
#         return app
    
#     @pytest.fixture
#     def mock_auth_service(self):
#         """Mock AuthService for testing."""
#         return Mock(spec=AuthService)
    
#     @pytest.fixture
#     def mock_user_service(self):
#         """Mock UserService for testing."""
#         return Mock(spec=UserService)
    
#     @pytest.fixture
#     def test_user(self):
#         """Create test user object."""
#         return User(
#             id=1,
#             username='testuser',
#             email='test@example.com',
#             password_hash=generate_password_hash('password123'),
#             first_name='Test',
#             last_name='User',
#             role='user',
#             is_active=True,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
    
#     @pytest.fixture
#     def client(self, app, mock_auth_service, mock_user_service):
#         """Create test client with mocked services."""
#         auth_bp = create_auth_routes(mock_auth_service, mock_user_service)
#         app.register_blueprint(auth_bp)
        
#         # Mock middleware initialization
#         with patch('routes.auth.init_auth_middleware'):
#             return app.test_client()
    
#     def test_register_success(self, client, mock_auth_service, test_user):
#         """Test successful user registration."""
#         # Mock service response
#         mock_auth_service.register_user.return_value = ServiceResponse(
#             success=True,
#             data=test_user,
#             message='User registered successfully'
#         )
        
#         # Test data
#         registration_data = {
#             'username': 'testuser',
#             'email': 'test@example.com',
#             'password': 'password123',
#             'confirm_password': 'password123'
#         }
        
#         # Make request
#         response = client.post('/api/auth/register', 
#                              data=json.dumps(registration_data),
#                              content_type='application/json')
        
#         # Assertions
#         assert response.status_code == 201
#         data = json.loads(response.data)
#         assert data['message'] == 'User registered successfully'
#         assert 'user' in data
#         assert 'access_token' in data
#         assert 'refresh_token' in data
#         assert data['user']['username'] == 'testuser'
        
#         # Verify service was called
#         mock_auth_service.register_user.assert_called_once_with(
#             username='testuser',
#             email='test@example.com',
#             password='password123'
#         )
    
#     def test_register_validation_error(self, client, mock_auth_service):
#         """Test registration with validation errors."""
#         # Invalid data - missing confirm_password
#         registration_data = {
#             'username': 'testuser',
#             'email': 'invalid-email',
#             'password': 'weak'
#         }
        
#         response = client.post('/api/auth/register',
#                              data=json.dumps(registration_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Validation error'
#         assert 'details' in data
    
#     def test_register_service_error(self, client, mock_auth_service):
#         """Test registration with service error."""
#         # Mock service error
#         mock_auth_service.register_user.return_value = ServiceResponse(
#             success=False,
#             message='Username already exists'
#         )
        
#         registration_data = {
#             'username': 'testuser',
#             'email': 'test@example.com',
#             'password': 'password123',
#             'confirm_password': 'password123'
#         }
        
#         response = client.post('/api/auth/register',
#                              data=json.dumps(registration_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Registration failed'
#         assert data['message'] == 'Username already exists'
    
#     def test_login_success(self, client, mock_auth_service, mock_user_service, test_user):
#         """Test successful login."""
#         # Mock service response
#         mock_auth_service.authenticate_user.return_value = ServiceResponse(
#             success=True,
#             data=test_user,
#             message='Login successful'
#         )
        
#         login_data = {
#             'username': 'testuser',
#             'password': 'password123'
#         }
        
#         response = client.post('/api/auth/login',
#                              data=json.dumps(login_data),
#                              content_type='application/json')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['message'] == 'Login successful'
#         assert 'user' in data
#         assert 'access_token' in data
#         assert 'refresh_token' in data
        
#         # Verify services were called
#         mock_auth_service.authenticate_user.assert_called_once_with(
#             username='testuser',
#             password='password123'
#         )
#         mock_user_service.update_last_login.assert_called_once_with(test_user.id)
    
#     def test_login_invalid_credentials(self, client, mock_auth_service):
#         """Test login with invalid credentials."""
#         mock_auth_service.authenticate_user.return_value = ServiceResponse(
#             success=False,
#             message='Invalid credentials'
#         )
        
#         login_data = {
#             'username': 'testuser',
#             'password': 'wrongpassword'
#         }
        
#         response = client.post('/api/auth/login',
#                              data=json.dumps(login_data),
#                              content_type='application/json')
        
#         assert response.status_code == 401
#         data = json.loads(response.data)
#         assert data['error'] == 'Login failed'
#         assert data['message'] == 'Invalid credentials'
    
#     def test_login_validation_error(self, client):
#         """Test login with validation errors."""
#         login_data = {
#             'username': '',  # Empty username
#             'password': 'password123'
#         }
        
#         response = client.post('/api/auth/login',
#                              data=json.dumps(login_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Validation error'
    
#     def test_refresh_token_success(self, client, mock_auth_service):
#         """Test successful token refresh."""
#         mock_auth_service.refresh_token.return_value = ServiceResponse(
#             success=True,
#             data={
#                 'access_token': 'new_access_token',
#                 'refresh_token': 'new_refresh_token'
#             },
#             message='Token refreshed successfully'
#         )
        
#         refresh_data = {
#             'refresh_token': 'valid_refresh_token'
#         }
        
#         response = client.post('/api/auth/refresh',
#                              data=json.dumps(refresh_data),
#                              content_type='application/json')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['message'] == 'Token refreshed successfully'
#         assert data['access_token'] == 'new_access_token'
#         assert data['refresh_token'] == 'new_refresh_token'
    
#     def test_refresh_token_invalid(self, client, mock_auth_service):
#         """Test token refresh with invalid token."""
#         mock_auth_service.refresh_token.return_value = ServiceResponse(
#             success=False,
#             message='Invalid refresh token'
#         )
        
#         refresh_data = {
#             'refresh_token': 'invalid_token'
#         }
        
#         response = client.post('/api/auth/refresh',
#                              data=json.dumps(refresh_data),
#                              content_type='application/json')
        
#         assert response.status_code == 401
#         data = json.loads(response.data)
#         assert data['error'] == 'Token refresh failed'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.require_auth')
#     def test_logout_success(self, mock_require_auth, mock_get_current_user, client, test_user):
#         """Test successful logout."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
        
#         response = client.post('/api/auth/logout')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['message'] == 'Logged out successfully'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.require_auth')
#     def test_get_current_user_profile(self, mock_require_auth, mock_get_current_user, client, test_user):
#         """Test getting current user profile."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
        
#         response = client.get('/api/auth/me')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert 'user' in data
#         assert data['user']['username'] == 'testuser'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.get_token_payload')
#     @patch('routes.auth.require_auth')
#     def test_verify_token(self, mock_require_auth, mock_get_token_payload, mock_get_current_user, client, test_user):
#         """Test token verification."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
#         mock_get_token_payload.return_value = {'exp': 1234567890}
        
#         response = client.post('/api/auth/verify-token')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['valid'] is True
#         assert data['user_id'] == test_user.id
#         assert data['username'] == test_user.username
    
#     def test_password_reset_request(self, client, mock_auth_service):
#         """Test password reset request."""
#         mock_auth_service.request_password_reset.return_value = ServiceResponse(
#             success=True,
#             message='Password reset email sent'
#         )
        
#         reset_data = {
#             'email': 'test@example.com'
#         }
        
#         response = client.post('/api/auth/password-reset-request',
#                              data=json.dumps(reset_data),
#                              content_type='application/json')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert 'password reset link has been sent' in data['message']
    
#     def test_password_reset(self, client, mock_auth_service):
#         """Test password reset with token."""
#         mock_auth_service.reset_password.return_value = ServiceResponse(
#             success=True,
#             message='Password reset successful'
#         )
        
#         reset_data = {
#             'token': 'valid_reset_token',
#             'new_password': 'newpassword123',
#             'confirm_password': 'newpassword123'
#         }
        
#         response = client.post('/api/auth/password-reset',
#                              data=json.dumps(reset_data),
#                              content_type='application/json')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['message'] == 'Password reset successfully'
    
#     def test_password_reset_invalid_token(self, client, mock_auth_service):
#         """Test password reset with invalid token."""
#         mock_auth_service.reset_password.return_value = ServiceResponse(
#             success=False,
#             message='Invalid or expired reset token'
#         )
        
#         reset_data = {
#             'token': 'invalid_token',
#             'new_password': 'newpassword123',
#             'confirm_password': 'newpassword123'
#         }
        
#         response = client.post('/api/auth/password-reset',
#                              data=json.dumps(reset_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Password reset failed'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.require_auth')
#     def test_change_password_success(self, mock_require_auth, mock_get_current_user, client, mock_auth_service, test_user):
#         """Test successful password change."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
        
#         mock_auth_service.change_password.return_value = ServiceResponse(
#             success=True,
#             message='Password changed successfully'
#         )
        
#         change_data = {
#             'current_password': 'oldpassword123',
#             'new_password': 'newpassword123',
#             'confirm_password': 'newpassword123'
#         }
        
#         response = client.post('/api/auth/change-password',
#                              data=json.dumps(change_data),
#                              content_type='application/json')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['message'] == 'Password changed successfully'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.require_auth')
#     def test_change_password_mismatch(self, mock_require_auth, mock_get_current_user, client, test_user):
#         """Test password change with mismatched passwords."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
        
#         change_data = {
#             'current_password': 'oldpassword123',
#             'new_password': 'newpassword123',
#             'confirm_password': 'differentpassword123'
#         }
        
#         response = client.post('/api/auth/change-password',
#                              data=json.dumps(change_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Password mismatch'
    
#     @patch('routes.auth.get_current_user')
#     @patch('routes.auth.require_auth')
#     def test_change_password_wrong_current(self, mock_require_auth, mock_get_current_user, client, mock_auth_service, test_user):
#         """Test password change with wrong current password."""
#         # Mock authentication
#         mock_require_auth.return_value = lambda f: f
#         mock_get_current_user.return_value = test_user
        
#         mock_auth_service.change_password.return_value = ServiceResponse(
#             success=False,
#             message='Current password is incorrect'
#         )
        
#         change_data = {
#             'current_password': 'wrongpassword',
#             'new_password': 'newpassword123',
#             'confirm_password': 'newpassword123'
#         }
        
#         response = client.post('/api/auth/change-password',
#                              data=json.dumps(change_data),
#                              content_type='application/json')
        
#         assert response.status_code == 400
#         data = json.loads(response.data)
#         assert data['error'] == 'Password change failed'
    
#     def test_health_check(self, client):
#         """Test health check endpoint."""
#         response = client.get('/api/auth/health')
        
#         assert response.status_code == 200
#         data = json.loads(response.data)
#         assert data['status'] == 'healthy'
#         assert data['service'] == 'auth'


# class TestAuthService:
#     """Test cases for AuthService."""
    
#     @pytest.fixture
#     def mock_user_service(self):
#         """Mock UserService for testing."""
#         return Mock(spec=UserService)
    
#     @pytest.fixture
#     def auth_service(self, mock_user_service):
#         """Create AuthService instance with mocked dependencies."""
#         return AuthService(mock_user_service)
    
#     @pytest.fixture
#     def test_user(self):
#         """Create test user object."""
#         return User(
#             id=1,
#             username='testuser',
#             email='test@example.com',
#             password_hash=generate_password_hash('password123'),
#             first_name='Test',
#             last_name='User',
#             role='user',
#             is_active=True,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
    
#     def test_register_user_success(self, auth_service, mock_user_service, test_user):
#         """Test successful user registration."""
#         mock_user_service.get_user_by_username.return_value = None
#         mock_user_service.get_user_by_email.return_value = None
#         mock_user_service.create_user.return_value = ServiceResponse(
#             success=True,
#             data=test_user
#         )
        
#         result = auth_service.register_user('testuser', 'test@example.com', 'password123')
        
#         assert result.success is True
#         assert result.data == test_user
#         assert 'registered successfully' in result.message
    
#     def test_register_user_username_exists(self, auth_service, mock_user_service, test_user):
#         """Test registration with existing username."""
#         mock_user_service.get_user_by_username.return_value = test_user
        
#         result = auth_service.register_user('testuser', 'test@example.com', 'password123')
        
#         assert result.success is False
#         assert 'Username already exists' in result.message
    
#     def test_register_user_email_exists(self, auth_service, mock_user_service, test_user):
#         """Test registration with existing email."""
#         mock_user_service.get_user_by_username.return_value = None
#         mock_user_service.get_user_by_email.return_value = test_user
        
#         result = auth_service.register_user('testuser', 'test@example.com', 'password123')
        
#         assert result.success is False
#         assert 'Email already exists' in result.message
    
#     def test_authenticate_user_success(self, auth_service, mock_user_service, test_user):
#         """Test successful user authentication."""
#         mock_user_service.get_user_by_username.return_value = test_user
        
#         with patch('services.auth_service.check_password_hash', return_value=True):
#             result = auth_service.authenticate_user('testuser', 'password123')
        
#         assert result.success is True
#         assert result.data == test_user
    
#     def test_authenticate_user_not_found(self, auth_service, mock_user_service):
#         """Test authentication with non-existent user."""
#         mock_user_service.get_user_by_username.return_value = None
        
#         result = auth_service.authenticate_user('nonexistent', 'password123')
        
#         assert result.success is False
#         assert 'Invalid credentials' in result.message
    
#     def test_authenticate_user_wrong_password(self, auth_service, mock_user_service, test_user):
#         """Test authentication with wrong password."""
#         mock_user_service.get_user_by_username.return_value = test_user
        
#         with patch('services.auth_service.check_password_hash', return_value=False):
#             result = auth_service.authenticate_user('testuser', 'wrongpassword')
        
#         assert result.success is False
#         assert 'Invalid credentials' in result.message
    
#     def test_authenticate_user_inactive(self, auth_service, mock_user_service, test_user):
#         """Test authentication with inactive user."""
#         test_user.is_active = False
#         mock_user_service.get_user_by_username.return_value = test_user
        
#         with patch('services.auth_service.check_password_hash', return_value=True):
#             result = auth_service.authenticate_user('testuser', 'password123')
        
#         assert result.success is False
#         assert 'Account is disabled' in result.message
    
#     @patch('services.auth_service.verify_jwt_token')
#     def test_refresh_token_success(self, mock_verify_jwt, auth_service, mock_user_service, test_user):
#         """Test successful token refresh."""
#         mock_verify_jwt.return_value = {
#             'user_id': test_user.id,
#             'username': test_user.username,
#             'role': test_user.role,
#             'type': 'refresh'
#         }
#         mock_user_service.get_user_by_id.return_value = test_user
        
#         result = auth_service.refresh_token('valid_refresh_token')
        
#         assert result.success is True
#         assert 'access_token' in result.data
#         assert 'refresh_token' in result.data
    
#     @patch('services.auth_service.verify_jwt_token')
#     def test_refresh_token_invalid(self, mock_verify_jwt, auth_service):
#         """Test token refresh with invalid token."""
#         mock_verify_jwt.return_value = None
        
#         result = auth_service.refresh_token('invalid_token')
        
#         assert result.success is False
#         assert 'Invalid refresh token' in result.message


# if __name__ == '__main__':
#     pytest.main([__file__])