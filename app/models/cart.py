from app import db
from datetime import datetime
import uuid

class Cart(db.Model):
    """Shopping cart model"""
    __tablename__ = 'carts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.total_price for item in self.items)
    
    @property
    def total_weight(self):
        """Calculate total weight of cart items"""
        total = 0
        for item in self.items:
            if item.product.weight:
                total += float(item.product.weight) * item.quantity
        return total
    
    def add_item(self, product, quantity=1):
        """Add item to cart or update quantity if exists"""
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.updated_at = datetime.utcnow()
        else:
            new_item = CartItem(
                cart_id=self.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(new_item)
        
        self.updated_at = datetime.utcnow()
        return existing_item or new_item
    
    def remove_item(self, product_id):
        """Remove item from cart"""
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if item:
            db.session.delete(item)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_item_quantity(self, product_id, quantity):
        """Update item quantity in cart"""
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if item:
            if quantity <= 0:
                db.session.delete(item)
            else:
                item.quantity = quantity
                item.updated_at = datetime.utcnow()
            
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def clear(self):
        """Clear all items from cart"""
        CartItem.query.filter_by(cart_id=self.id).delete()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert cart to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_items': self.total_items,
            'subtotal': float(self.subtotal),
            'total_weight': self.total_weight,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Cart {self.user.email} - {self.total_items} items>'

class CartItem(db.Model):
    """Cart item model"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String(36), db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of adding to cart
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='cart_items', lazy=True)
    
    # Unique constraint to prevent duplicate items in same cart
    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),)
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.price * self.quantity
    
    @property
    def current_product_price(self):
        """Get current product price (may differ from cart price)"""
        return self.product.price if self.product else self.price
    
    @property
    def price_changed(self):
        """Check if product price has changed since adding to cart"""
        return self.price != self.current_product_price
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'price': float(self.price),
            'current_price': float(self.current_product_price),
            'price_changed': self.price_changed,
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CartItem {self.product.name if self.product else "Unknown"} x{self.quantity}>'
