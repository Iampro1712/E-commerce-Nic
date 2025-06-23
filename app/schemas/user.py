from marshmallow import Schema, fields, validate, validates, ValidationError
from app.utils.auth import validate_email, validate_phone

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=255))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    
    @validates('phone')
    def validate_phone_number(self, value):
        if value and not validate_phone(value):
            raise ValidationError('Invalid phone number format')

class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    """Schema for user profile update"""
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    
    @validates('phone')
    def validate_phone_number(self, value):
        if value and not validate_phone(value):
            raise ValidationError('Invalid phone number format')

class AddressSchema(Schema):
    """Schema for address"""
    type = fields.Str(required=True, validate=validate.OneOf(['shipping', 'billing']))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    company = fields.Str(allow_none=True, validate=validate.Length(max=100))
    address_line_1 = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    address_line_2 = fields.Str(allow_none=True, validate=validate.Length(max=255))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    state = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    country = fields.Str(required=True, validate=validate.Length(min=2, max=2))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    is_default = fields.Bool(missing=False)
    
    @validates('phone')
    def validate_phone_number(self, value):
        if value and not validate_phone(value):
            raise ValidationError('Invalid phone number format')

class PasswordChangeSchema(Schema):
    """Schema for password change"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=255))
