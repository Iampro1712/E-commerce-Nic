from marshmallow import Schema, fields, validate, validates, ValidationError

class AddToCartSchema(Schema):
    """Schema for adding item to cart"""
    product_id = fields.Str(required=True, validate=validate.Length(min=36, max=36))
    quantity = fields.Int(required=True, validate=validate.Range(min=1, max=999))

class UpdateCartItemSchema(Schema):
    """Schema for updating cart item quantity"""
    quantity = fields.Int(required=True, validate=validate.Range(min=0, max=999))

class CartItemSchema(Schema):
    """Schema for cart item response"""
    id = fields.Str()
    product_id = fields.Str()
    product = fields.Dict()
    quantity = fields.Int()
    price = fields.Decimal(places=2)
    current_price = fields.Decimal(places=2)
    price_changed = fields.Bool()
    total_price = fields.Decimal(places=2)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class CartSchema(Schema):
    """Schema for cart response"""
    id = fields.Str()
    user_id = fields.Str()
    total_items = fields.Int()
    subtotal = fields.Decimal(places=2)
    total_weight = fields.Float()
    items = fields.List(fields.Nested(CartItemSchema))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
