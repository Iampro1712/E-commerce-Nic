import pytest
import json
from app.models.user import User

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+505 8888-8888'
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'access_token' in response_data
        assert 'user' in response_data
        assert response_data['user']['email'] == data['email']
    
    def test_register_duplicate_email(self, client, user):
        """Test registration with duplicate email"""
        data = {
            'email': user.email,
            'password': 'NewPassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Email already registered' in response_data['error']
    
    def test_register_invalid_password(self, client):
        """Test registration with weak password"""
        data = {
            'email': 'newuser@example.com',
            'password': '123',  # Too weak
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_login_success(self, client, user):
        """Test successful login"""
        data = {
            'email': user.email,
            'password': 'TestPassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'access_token' in response_data
        assert 'user' in response_data
    
    def test_login_invalid_credentials(self, client, user):
        """Test login with invalid credentials"""
        data = {
            'email': user.email,
            'password': 'WrongPassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'Invalid email or password' in response_data['error']
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'user' in response_data
        assert response_data['user']['email'] == 'test@example.com'
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication"""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+505 9999-9999'
        }
        
        response = client.put('/api/auth/profile',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['user']['first_name'] == 'Updated'
        assert response_data['user']['last_name'] == 'Name'
    
    def test_change_password(self, client, auth_headers):
        """Test changing password"""
        data = {
            'current_password': 'TestPassword123',
            'new_password': 'NewTestPassword123'
        }
        
        response = client.post('/api/auth/change-password',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password"""
        data = {
            'current_password': 'WrongPassword',
            'new_password': 'NewTestPassword123'
        }
        
        response = client.post('/api/auth/change-password',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Current password is incorrect' in response_data['error']
    
    def test_add_address(self, client, auth_headers):
        """Test adding user address"""
        data = {
            'type': 'shipping',
            'first_name': 'Test',
            'last_name': 'User',
            'address_line_1': 'Calle Principal 123',
            'city': 'Managua',
            'state': 'Managua',
            'postal_code': '12345',
            'country': 'NI',
            'is_default': True
        }
        
        response = client.post('/api/auth/addresses',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'address' in response_data
        assert response_data['address']['type'] == 'shipping'
    
    def test_get_addresses(self, client, auth_headers):
        """Test getting user addresses"""
        response = client.get('/api/auth/addresses', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'addresses' in response_data
        assert isinstance(response_data['addresses'], list)
