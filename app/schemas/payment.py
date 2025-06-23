from marshmallow import Schema, fields, validate, validates, ValidationError

class PayPalPaymentSchema(Schema):
    """Schema for creating PayPal payment"""
    amount = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01))
    currency = fields.Str(required=True, validate=validate.Length(min=3, max=3))
    return_url = fields.Url(required=True)
    cancel_url = fields.Url(required=True)
    description = fields.Str(missing="Payment", validate=validate.Length(max=127))
    items = fields.List(fields.Dict(), missing=[])

class PayPalExecutePaymentSchema(Schema):
    """Schema for executing PayPal payment"""
    payment_id = fields.Str(required=True)
    payer_id = fields.Str(required=True)

class PayPalDirectPaymentSchema(Schema):
    """Schema for direct credit card payment"""
    amount = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01))
    currency = fields.Str(required=True, validate=validate.Length(min=3, max=3))
    credit_card = fields.Dict(required=True)
    description = fields.Str(missing="Payment", validate=validate.Length(max=127))

class PayPalRefundSchema(Schema):
    """Schema for PayPal refund"""
    sale_id = fields.Str(required=True)
    amount = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0.01))
    currency = fields.Str(missing='USD', validate=validate.Length(min=3, max=3))

class PayPalWebhookSchema(Schema):
    """Schema for PayPal webhook validation"""
    id = fields.Str(required=True)
    event_type = fields.Str(required=True)
    create_time = fields.Str(required=True)
    resource_type = fields.Str(required=True)
    resource = fields.Dict(required=True)
    summary = fields.Str(allow_none=True)

class CreditCardSchema(Schema):
    """Schema for credit card data"""
    type = fields.Str(required=True, validate=validate.OneOf(['visa', 'mastercard', 'amex', 'discover']))
    number = fields.Str(required=True, validate=validate.Length(min=13, max=19))
    expire_month = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    expire_year = fields.Int(required=True, validate=validate.Range(min=2024, max=2050))
    cvv2 = fields.Str(required=True, validate=validate.Length(min=3, max=4))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
