from marshmallow import Schema, fields, validate, validates, ValidationError

class AddressOrderSchema(Schema):
    """Schema for order address"""
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

class CreateOrderSchema(Schema):
    """Schema for creating order"""
    shipping_address = fields.Nested(AddressOrderSchema, required=True)
    billing_address = fields.Nested(AddressOrderSchema, required=True)
    payment_method = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    customer_notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    currency = fields.Str(missing='USD', validate=validate.Length(min=3, max=3))

class UpdateOrderStatusSchema(Schema):
    """Schema for updating order status"""
    status = fields.Str(required=True, validate=validate.OneOf([
        'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
    ]))
    admin_notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))

class OrderSearchSchema(Schema):
    """Schema for order search parameters"""
    status = fields.Str(allow_none=True, validate=validate.OneOf([
        'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
    ]))
    payment_status = fields.Str(allow_none=True, validate=validate.OneOf([
        'pending', 'paid', 'failed', 'refunded', 'partially_refunded'
    ]))
    order_number = fields.Str(allow_none=True, validate=validate.Length(max=20))
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    min_amount = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    max_amount = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    sort_by = fields.Str(allow_none=True, validate=validate.OneOf([
        'created_at', 'updated_at', 'total_amount', 'order_number'
    ]))
    sort_order = fields.Str(missing='desc', validate=validate.OneOf(['asc', 'desc']))
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))

class OrderItemSchema(Schema):
    """Schema for order item response"""
    id = fields.Str()
    product_id = fields.Str()
    product_name = fields.Str()
    product_sku = fields.Str()
    product_price = fields.Decimal(places=2)
    quantity = fields.Int()
    total_price = fields.Decimal(places=2)
    created_at = fields.DateTime()

class OrderSchema(Schema):
    """Schema for order response"""
    id = fields.Str()
    order_number = fields.Str()
    user_id = fields.Str()
    status = fields.Str()
    payment_status = fields.Str()
    subtotal = fields.Decimal(places=2)
    tax_amount = fields.Decimal(places=2)
    shipping_amount = fields.Decimal(places=2)
    discount_amount = fields.Decimal(places=2)
    total_amount = fields.Decimal(places=2)
    currency = fields.Str()
    total_items = fields.Int()
    shipping_address = fields.Dict()
    billing_address = fields.Dict()
    payment_method = fields.Str()
    payment_reference = fields.Str()
    customer_notes = fields.Str()
    admin_notes = fields.Str()
    can_be_cancelled = fields.Bool()
    can_be_refunded = fields.Bool()
    items = fields.List(fields.Nested(OrderItemSchema))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    shipped_at = fields.DateTime()
    delivered_at = fields.DateTime()
