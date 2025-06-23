from app import db
from datetime import datetime
import uuid

class Category(db.Model):
    """Product category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Self-referential relationship for subcategories
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self, include_products=False):
        """Convert category to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_products:
            data['products'] = [product.to_dict() for product in self.products if product.is_active]
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Product model"""
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    short_description = db.Column(db.String(500), nullable=True)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_price = db.Column(db.Numeric(10, 2), nullable=True)  # Original price for discounts
    cost_price = db.Column(db.Numeric(10, 2), nullable=True)  # Cost for profit calculation
    
    # Inventory
    track_inventory = db.Column(db.Boolean, default=True, nullable=False)
    inventory_quantity = db.Column(db.Integer, default=0, nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=5, nullable=False)
    
    # Product attributes
    weight = db.Column(db.Numeric(8, 2), nullable=True)  # in kg
    dimensions = db.Column(db.String(100), nullable=True)  # LxWxH in cm
    
    # SEO and metadata
    meta_title = db.Column(db.String(200), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_digital = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.compare_price and self.compare_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.inventory_quantity <= self.low_stock_threshold
    
    def to_dict(self, include_images=True):
        """Convert product to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'sku': self.sku,
            'slug': self.slug,
            'price': float(self.price),
            'compare_price': float(self.compare_price) if self.compare_price else None,
            'is_on_sale': self.is_on_sale,
            'discount_percentage': self.discount_percentage,
            'track_inventory': self.track_inventory,
            'inventory_quantity': self.inventory_quantity,
            'is_in_stock': self.is_in_stock,
            'is_low_stock': self.is_low_stock,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'is_digital': self.is_digital,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_images:
            data['images'] = [img.to_dict() for img in self.images]
        
        return data
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    """Product image model"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert product image to dictionary"""
        return {
            'id': self.id,
            'image_url': self.image_url,
            'alt_text': self.alt_text,
            'sort_order': self.sort_order,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ProductImage {self.product.name} - {self.sort_order}>'
