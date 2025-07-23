"""
Tests for user management routes and services.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime
from werkzeug.security import generate_password_hash

from routes.user import create_user_routes
from services.user_service import UserService
from models.user import User
from utils.response import ServiceResponse


class TestUserRoutes:
    """Test cases for user management routes."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def mock_user_service(self):
        """Mock UserService for testing."""
        return Mock(spec=UserService)
    
    @pytest.fixture
    def test_user(self):
        """Create test user object."""
        return User(
            id=1,
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            first_name='Test',
            last_name='User',
            role='user',
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def test_admin(self):
        """Create test admin user object."""
        return User(
            id=2,
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpass123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def client(self, app, mock_user_service):
        """Create test client with mocked services."""
        user_bp = create_user_routes(mock_user_service)
        app.register_blueprint(user_bp)
        return app.test_client()
    
    @patch('routes.user.require_admin')
    def test_get_users_success(self, mock_require_admin, client, mock_user_service, test_user, test_admin):
        """Test successful user listing."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_users_paginated.return_value = ServiceResponse(
            success=True,
            data={
                'users': [test_user, test_admin],
                'total': 2,
                'pages': 1
            }
        )
        
        response = client.get('/api/users?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'pagination' in data
        assert len(data['users']) == 2
        assert data['pagination']['total'] == 2
    
    @patch('routes.user.require_admin')
    def test_get_users_with_filters(self, mock_require_admin, client, mock_user_service):
        """Test user listing with filters."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_users_paginated.return_value = ServiceResponse(
            success=True,
            data={
                'users': [],
                'total': 0,
                'pages': 0
            }
        )
        
        response = client.get('/api/users?search=test&role=admin&is_active=true&sort_by=username')
        
        assert response.status_code == 200
        
        # Verify service was called with correct parameters
        mock_user_service.get_users_paginated.assert_called_once_with(
            page=1,
            per_page=10,
            search='test',
            role='admin',
            is_active=True,
            sort_by='username',
            sort_order='desc'
        )
    
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_get_user_success(self, mock_require_auth, mock_require_owner_or_admin, client, mock_user_service, test_user):
        """Test successful user retrieval."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_user_by_id.return_value = test_user
        
        response = client.get('/api/users/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_get_user_not_found(self, mock_require_auth, mock_require_owner_or_admin, client, mock_user_service):
        """Test user retrieval with non-existent user."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_user_by_id.return_value = None
        
        response = client.get('/api/users/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_update_user_success(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test successful user update."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        updated_user = User(**test_user.__dict__)
        updated_user.first_name = 'Updated'
        mock_user_service.update_user.return_value = ServiceResponse(
            success=True,
            data=updated_user
        )
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        
        response = client.put('/api/users/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User updated successfully'
        assert 'user' in data
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_update_user_not_found(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test user update with non-existent user."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service response
        mock_user_service.get_user_by_id.return_value = None
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        
        response = client.put('/api/users/999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_update_user_validation_error(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test user update with validation errors."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        mock_user_service.update_user.return_value = ServiceResponse(
            success=False,
            error='Email already exists'
        )
        
        update_data = {
            'email': 'duplicate@example.com'
        }
        
        response = client.put('/api/users/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Email already exists'
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_update_user_invalid_json(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test user update with invalid JSON."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service response
        mock_user_service.get_user_by_id.return_value = test_user
        
        response = client.put('/api/users/1',
                            data='invalid json',
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid JSON'
    
    @patch('routes.user.require_admin')
    def test_delete_user_success(self, mock_require_admin, client, mock_user_service, test_user):
        """Test successful user deletion."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        mock_user_service.delete_user.return_value = ServiceResponse(
            success=True,
            data=None
        )
        
        response = client.delete('/api/users/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User deleted successfully'
    
    @patch('routes.user.require_admin')
    def test_delete_user_not_found(self, mock_require_admin, client, mock_user_service):
        """Test user deletion with non-existent user."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_user_by_id.return_value = None
        
        response = client.delete('/api/users/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'
    
    @patch('routes.user.require_admin')
    def test_delete_user_service_error(self, mock_require_admin, client, mock_user_service, test_user):
        """Test user deletion with service error."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        mock_user_service.delete_user.return_value = ServiceResponse(
            success=False,
            error='Cannot delete user with active sessions'
        )
        
        response = client.delete('/api/users/1')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Cannot delete user with active sessions'
    
    @patch('routes.user.require_admin')
    def test_create_user_success(self, mock_require_admin, client, mock_user_service, test_user):
        """Test successful user creation."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.create_user.return_value = ServiceResponse(
            success=True,
            data=test_user
        )
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'user'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user' in data
    
    @patch('routes.user.require_admin')
    def test_create_user_validation_error(self, mock_require_admin, client, mock_user_service):
        """Test user creation with validation errors."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.create_user.return_value = ServiceResponse(
            success=False,
            error='Username already exists'
        )
        
        user_data = {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'password123',
            'first_name': 'Existing',
            'last_name': 'User',
            'role': 'user'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Username already exists'
    
    @patch('routes.user.require_admin')
    def test_create_user_missing_fields(self, mock_require_admin, client, mock_user_service):
        """Test user creation with missing required fields."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
            # Missing password and other required fields
        }
        
        response = client.post('/api/users',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    @patch('routes.user.require_admin')
    def test_activate_user_success(self, mock_require_admin, client, mock_user_service, test_user):
        """Test successful user activation."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service responses
        test_user.is_active = False
        mock_user_service.get_user_by_id.return_value = test_user
        
        activated_user = User(**test_user.__dict__)
        activated_user.is_active = True
        mock_user_service.activate_user.return_value = ServiceResponse(
            success=True,
            data=activated_user
        )
        
        response = client.post('/api/users/1/activate')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User activated successfully'
        assert 'user' in data
    
    @patch('routes.user.require_admin')
    def test_deactivate_user_success(self, mock_require_admin, client, mock_user_service, test_user):
        """Test successful user deactivation."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        
        deactivated_user = User(**test_user.__dict__)
        deactivated_user.is_active = False
        mock_user_service.deactivate_user.return_value = ServiceResponse(
            success=True,
            data=deactivated_user
        )
        
        response = client.post('/api/users/1/deactivate')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User deactivated successfully'
        assert 'user' in data
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_change_password_success(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test successful password change."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        mock_user_service.change_password.return_value = ServiceResponse(
            success=True,
            data=None
        )
        
        password_data = {
            'current_password': 'password123',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/users/1/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password changed successfully'
    
    @patch('routes.user.get_current_user')
    @patch('routes.user.require_owner_or_admin')
    @patch('routes.user.require_auth')
    def test_change_password_invalid_current(self, mock_require_auth, mock_require_owner_or_admin, mock_get_current_user, client, mock_user_service, test_user):
        """Test password change with invalid current password."""
        # Mock authentication
        mock_require_auth.return_value = lambda f: f
        mock_require_owner_or_admin.return_value = lambda f: f
        mock_get_current_user.return_value = test_user
        
        # Mock service responses
        mock_user_service.get_user_by_id.return_value = test_user
        mock_user_service.change_password.return_value = ServiceResponse(
            success=False,
            error='Current password is incorrect'
        )
        
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/users/1/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Current password is incorrect'
    
    def test_unauthorized_access(self, client):
        """Test that routes require proper authentication."""
        # Test routes that should require admin access
        admin_routes = [
            '/api/users',
            '/api/users/1/activate',
            '/api/users/1/deactivate'
        ]
        
        for route in admin_routes:
            response = client.get(route)
            assert response.status_code == 401
        
        # Test routes that should require authentication
        auth_routes = [
            '/api/users/1',
            '/api/users/1/change-password'
        ]
        
        for route in auth_routes:
            response = client.get(route)
            assert response.status_code == 401
    
    @patch('routes.user.require_admin')
    def test_service_error_handling(self, mock_require_admin, client, mock_user_service):
        """Test handling of service errors."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service to raise exception
        mock_user_service.get_users_paginated.side_effect = Exception('Database connection failed')
        
        response = client.get('/api/users')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'internal server error' in data['error'].lower()
    
    @patch('routes.user.require_admin')
    def test_pagination_parameters(self, mock_require_admin, client, mock_user_service):
        """Test pagination parameter handling."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Mock service response
        mock_user_service.get_users_paginated.return_value = ServiceResponse(
            success=True,
            data={
                'users': [],
                'total': 0,
                'pages': 0
            }
        )
        
        # Test with custom pagination parameters
        response = client.get('/api/users?page=2&per_page=25')
        
        assert response.status_code == 200
        
        # Verify service was called with correct parameters
        mock_user_service.get_users_paginated.assert_called_once_with(
            page=2,
            per_page=25,
            search=None,
            role=None,
            is_active=None,
            sort_by='created_at',
            sort_order='desc'
        )
    
    @patch('routes.user.require_admin')
    def test_invalid_pagination_parameters(self, mock_require_admin, client, mock_user_service):
        """Test handling of invalid pagination parameters."""
        # Mock authentication
        mock_require_admin.return_value = lambda f: f
        
        # Test with invalid page parameter
        response = client.get('/api/users?page=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'invalid' in data['error'].lower()