from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.user import User, Address
from app.models.cart import Cart
from app.schemas.user import (
    UserRegistrationSchema, UserLoginSchema, UserUpdateSchema, 
    AddressSchema, PasswordChangeSchema
)
from app.utils.auth import token_required, get_current_user, validate_password, sanitize_input

auth_bp = Blueprint('auth', __name__)

# Schema instances
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_update_schema = UserUpdateSchema()
address_schema = AddressSchema()
password_change_schema = PasswordChangeSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = user_registration_schema.load(data)
        
        # Check if user already exists
        if User.query.filter_by(email=validated_data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(validated_data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Create new user
        user = User(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone')
        )
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create cart for user
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = user_login_schema.load(data)
        
        # Find user
        user = User.query.filter_by(email=validated_data['email'].lower()).first()
        
        if not user or not user.check_password(validated_data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = user_update_schema.load(data)
        
        # Update user fields
        for field, value in validated_data.items():
            setattr(user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = password_change_schema.load(data)
        
        # Check current password
        if not user.check_password(validated_data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password strength
        is_valid, message = validate_password(validated_data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        user.set_password(validated_data['new_password'])
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500

@auth_bp.route('/addresses', methods=['GET'])
@token_required
def get_addresses():
    """Get user addresses"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        addresses = [addr.to_dict() for addr in user.addresses]
        
        return jsonify({
            'addresses': addresses
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get addresses'}), 500

@auth_bp.route('/addresses', methods=['POST'])
@token_required
def add_address():
    """Add new address"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = address_schema.load(data)
        
        # If this is set as default, unset other defaults of same type
        if validated_data.get('is_default', False):
            Address.query.filter_by(
                user_id=user.id,
                type=validated_data['type']
            ).update({'is_default': False})
        
        # Create new address
        address = Address(user_id=user.id, **validated_data)
        db.session.add(address)
        db.session.commit()
        
        return jsonify({
            'message': 'Address added successfully',
            'address': address.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add address'}), 500

@auth_bp.route('/addresses/<address_id>', methods=['PUT'])
@token_required
def update_address(address_id):
    """Update address"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        address = Address.query.filter_by(id=address_id, user_id=user.id).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = address_schema.load(data, partial=True)
        
        # If this is set as default, unset other defaults of same type
        if validated_data.get('is_default', False):
            Address.query.filter_by(
                user_id=user.id,
                type=validated_data.get('type', address.type)
            ).filter(Address.id != address_id).update({'is_default': False})
        
        # Update address fields
        for field, value in validated_data.items():
            setattr(address, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Address updated successfully',
            'address': address.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update address'}), 500

@auth_bp.route('/addresses/<address_id>', methods=['DELETE'])
@token_required
def delete_address(address_id):
    """Delete address"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        address = Address.query.filter_by(id=address_id, user_id=user.id).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({
            'message': 'Address deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete address'}), 500
