from marshmallow import Schema, fields, validate, validates, ValidationError

class CategorySchema(Schema):
    """Schema for category"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    slug = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    image_url = fields.Url(allow_none=True, validate=validate.Length(max=255))
    is_active = fields.Bool(missing=True)
    sort_order = fields.Int(missing=0)
    parent_id = fields.Str(allow_none=True, validate=validate.Length(min=36, max=36))

class ProductImageSchema(Schema):
    """Schema for product image"""
    image_url = fields.Url(required=True, validate=validate.Length(max=255))
    alt_text = fields.Str(allow_none=True, validate=validate.Length(max=200))
    sort_order = fields.Int(missing=0)
    is_primary = fields.Bool(missing=False)

class ProductSchema(Schema):
    """Schema for product"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    short_description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.Str(required=True, validate=validate.Length(min=1, max=220))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    compare_price = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    cost_price = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    
    # Inventory
    track_inventory = fields.Bool(missing=True)
    inventory_quantity = fields.Int(missing=0, validate=validate.Range(min=0))
    low_stock_threshold = fields.Int(missing=5, validate=validate.Range(min=0))
    
    # Product attributes
    weight = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    dimensions = fields.Str(allow_none=True, validate=validate.Length(max=100))
    
    # SEO
    meta_title = fields.Str(allow_none=True, validate=validate.Length(max=200))
    meta_description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    
    # Status
    is_active = fields.Bool(missing=True)
    is_featured = fields.Bool(missing=False)
    is_digital = fields.Bool(missing=False)
    
    # Relationships
    category_id = fields.Str(required=True, validate=validate.Length(min=36, max=36))
    images = fields.List(fields.Nested(ProductImageSchema), missing=[])
    
    @validates('compare_price')
    def validate_compare_price(self, value):
        if value is not None and 'price' in self.context:
            if value <= self.context['price']:
                raise ValidationError('Compare price must be greater than regular price')

class ProductUpdateSchema(ProductSchema):
    """Schema for product update (all fields optional)"""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    sku = fields.Str(validate=validate.Length(min=1, max=100))
    slug = fields.Str(validate=validate.Length(min=1, max=220))
    price = fields.Decimal(places=2, validate=validate.Range(min=0))
    category_id = fields.Str(validate=validate.Length(min=36, max=36))

class ProductSearchSchema(Schema):
    """Schema for product search parameters"""
    q = fields.Str(allow_none=True, validate=validate.Length(max=200))  # Search query
    category_id = fields.Str(allow_none=True, validate=validate.Length(min=36, max=36))
    min_price = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    max_price = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))
    is_featured = fields.Bool(allow_none=True)
    is_active = fields.Bool(missing=True)
    in_stock = fields.Bool(allow_none=True)
    sort_by = fields.Str(allow_none=True, validate=validate.OneOf([
        'name', 'price', 'created_at', 'updated_at', 'popularity'
    ]))
    sort_order = fields.Str(missing='asc', validate=validate.OneOf(['asc', 'desc']))
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    
    @validates('max_price')
    def validate_price_range(self, value):
        if value is not None and 'min_price' in self.context:
            min_price = self.context.get('min_price')
            if min_price is not None and value < min_price:
                raise ValidationError('Max price must be greater than min price')
