from app import db
from datetime import datetime
import uuid
from enum import Enum

class OrderStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class PaymentStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'

class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Order status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Currency
    currency = db.Column(db.String(3), default='USD', nullable=False)
    
    # Shipping information
    shipping_first_name = db.Column(db.String(50), nullable=False)
    shipping_last_name = db.Column(db.String(50), nullable=False)
    shipping_company = db.Column(db.String(100), nullable=True)
    shipping_address_line_1 = db.Column(db.String(255), nullable=False)
    shipping_address_line_2 = db.Column(db.String(255), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(2), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=True)
    
    # Billing information
    billing_first_name = db.Column(db.String(50), nullable=False)
    billing_last_name = db.Column(db.String(50), nullable=False)
    billing_company = db.Column(db.String(100), nullable=True)
    billing_address_line_1 = db.Column(db.String(255), nullable=False)
    billing_address_line_2 = db.Column(db.String(255), nullable=True)
    billing_city = db.Column(db.String(100), nullable=False)
    billing_state = db.Column(db.String(100), nullable=False)
    billing_postal_code = db.Column(db.String(20), nullable=False)
    billing_country = db.Column(db.String(2), nullable=False)
    billing_phone = db.Column(db.String(20), nullable=True)
    
    # Payment information
    payment_method = db.Column(db.String(50), nullable=True)
    payment_reference = db.Column(db.String(255), nullable=True)  # Adyen payment reference
    
    # Notes
    customer_notes = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.order_number = self.generate_order_number()
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        import random
        import string
        
        # Generate order number with format: ORD-YYYYMMDD-XXXX
        date_str = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD-{date_str}-{random_str}"
    
    @property
    def total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items)
    
    @property
    def shipping_address(self):
        """Get formatted shipping address"""
        address_parts = [
            f"{self.shipping_first_name} {self.shipping_last_name}",
            self.shipping_company,
            self.shipping_address_line_1,
            self.shipping_address_line_2,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ]
        return '\n'.join(filter(None, address_parts))
    
    @property
    def billing_address(self):
        """Get formatted billing address"""
        address_parts = [
            f"{self.billing_first_name} {self.billing_last_name}",
            self.billing_company,
            self.billing_address_line_1,
            self.billing_address_line_2,
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ]
        return '\n'.join(filter(None, address_parts))
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    def can_be_refunded(self):
        """Check if order can be refunded"""
        return (self.payment_status == PaymentStatus.PAID and 
                self.status not in [OrderStatus.CANCELLED, OrderStatus.REFUNDED])
    
    def to_dict(self, include_items=True):
        """Convert order to dictionary"""
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'status': self.status.value,
            'payment_status': self.payment_status.value,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'shipping_amount': float(self.shipping_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'total_items': self.total_items,
            'shipping_address': {
                'first_name': self.shipping_first_name,
                'last_name': self.shipping_last_name,
                'company': self.shipping_company,
                'address_line_1': self.shipping_address_line_1,
                'address_line_2': self.shipping_address_line_2,
                'city': self.shipping_city,
                'state': self.shipping_state,
                'postal_code': self.shipping_postal_code,
                'country': self.shipping_country,
                'phone': self.shipping_phone
            },
            'billing_address': {
                'first_name': self.billing_first_name,
                'last_name': self.billing_last_name,
                'company': self.billing_company,
                'address_line_1': self.billing_address_line_1,
                'address_line_2': self.billing_address_line_2,
                'city': self.billing_city,
                'state': self.billing_state,
                'postal_code': self.billing_postal_code,
                'country': self.billing_country,
                'phone': self.billing_phone
            },
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'customer_notes': self.customer_notes,
            'can_be_cancelled': self.can_be_cancelled(),
            'can_be_refunded': self.can_be_refunded(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    
    # Product information at time of order (snapshot)
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items', lazy=True)
    
    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'product_price': float(self.product_price),
            'quantity': self.quantity,
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
