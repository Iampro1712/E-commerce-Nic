from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import or_, and_
from app import db
from app.models.product import Product, Category, ProductImage
from app.schemas.product import (
    ProductSchema, ProductUpdateSchema, CategorySchema, 
    ProductSearchSchema, ProductImageSchema
)
from app.utils.auth import token_required, admin_required, get_current_user, sanitize_input

products_bp = Blueprint('products', __name__)

# Schema instances
product_schema = ProductSchema()
product_update_schema = ProductUpdateSchema()
category_schema = CategorySchema()
product_search_schema = ProductSearchSchema()
product_image_schema = ProductImageSchema()

# Category endpoints
@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order, Category.name).all()
        return jsonify({
            'categories': [cat.to_dict() for cat in categories]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get categories'}), 500

@products_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """Create new category (admin only)"""
    try:
        data = sanitize_input(request.get_json())
        validated_data = category_schema.load(data)
        
        # Check if slug already exists
        if Category.query.filter_by(slug=validated_data['slug']).first():
            return jsonify({'error': 'Category slug already exists'}), 400
        
        # Check if name already exists
        if Category.query.filter_by(name=validated_data['name']).first():
            return jsonify({'error': 'Category name already exists'}), 400
        
        # Validate parent category if provided
        if validated_data.get('parent_id'):
            parent = Category.query.get(validated_data['parent_id'])
            if not parent:
                return jsonify({'error': 'Parent category not found'}), 404
        
        category = Category(**validated_data)
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create category'}), 500

@products_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({
            'category': category.to_dict(include_products=True)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get category'}), 500

@products_bp.route('/categories/<category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update category (admin only)"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        data = sanitize_input(request.get_json())
        validated_data = category_schema.load(data, partial=True)
        
        # Check if slug already exists (excluding current category)
        if 'slug' in validated_data:
            existing = Category.query.filter(
                Category.slug == validated_data['slug'],
                Category.id != category_id
            ).first()
            if existing:
                return jsonify({'error': 'Category slug already exists'}), 400
        
        # Check if name already exists (excluding current category)
        if 'name' in validated_data:
            existing = Category.query.filter(
                Category.name == validated_data['name'],
                Category.id != category_id
            ).first()
            if existing:
                return jsonify({'error': 'Category name already exists'}), 400
        
        # Update category fields
        for field, value in validated_data.items():
            setattr(category, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update category'}), 500

@products_bp.route('/categories/<category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete category (admin only)"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Check if category has products
        if category.products:
            return jsonify({'error': 'Cannot delete category with products'}), 400
        
        # Check if category has subcategories
        if category.children:
            return jsonify({'error': 'Cannot delete category with subcategories'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete category'}), 500

# Product endpoints
@products_bp.route('', methods=['GET'])
def get_products():
    """Get products with search and filtering"""
    try:
        # Parse query parameters
        args = request.args.to_dict()
        validated_params = product_search_schema.load(args)
        
        # Build query
        query = Product.query
        
        # Apply filters
        if validated_params.get('is_active') is not None:
            query = query.filter(Product.is_active == validated_params['is_active'])
        
        if validated_params.get('category_id'):
            query = query.filter(Product.category_id == validated_params['category_id'])
        
        if validated_params.get('is_featured') is not None:
            query = query.filter(Product.is_featured == validated_params['is_featured'])
        
        if validated_params.get('min_price') is not None:
            query = query.filter(Product.price >= validated_params['min_price'])
        
        if validated_params.get('max_price') is not None:
            query = query.filter(Product.price <= validated_params['max_price'])
        
        if validated_params.get('in_stock'):
            query = query.filter(
                or_(
                    Product.track_inventory == False,
                    Product.inventory_quantity > 0
                )
            )
        
        # Apply search
        if validated_params.get('q'):
            search_term = f"%{validated_params['q']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.short_description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        
        # Apply sorting
        sort_by = validated_params.get('sort_by', 'created_at')
        sort_order = validated_params.get('sort_order', 'desc')
        
        if sort_by == 'name':
            order_field = Product.name
        elif sort_by == 'price':
            order_field = Product.price
        elif sort_by == 'updated_at':
            order_field = Product.updated_at
        else:  # created_at or popularity
            order_field = Product.created_at
        
        if sort_order == 'desc':
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())
        
        # Apply pagination
        page = validated_params.get('page', 1)
        per_page = validated_params.get('per_page', 20)
        
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get products'}), 500

@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Create new product (admin only)"""
    try:
        data = sanitize_input(request.get_json())
        validated_data = product_schema.load(data)
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=validated_data['sku']).first():
            return jsonify({'error': 'Product SKU already exists'}), 400
        
        # Check if slug already exists
        if Product.query.filter_by(slug=validated_data['slug']).first():
            return jsonify({'error': 'Product slug already exists'}), 400
        
        # Validate category exists
        category = Category.query.get(validated_data['category_id'])
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Extract images data
        images_data = validated_data.pop('images', [])
        
        # Create product
        product = Product(**validated_data)
        db.session.add(product)
        db.session.flush()  # Get product ID
        
        # Add images
        for img_data in images_data:
            image = ProductImage(product_id=product.id, **img_data)
            db.session.add(image)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create product'}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'product': product.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get product'}), 500

@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update product (admin only)"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = sanitize_input(request.get_json())
        validated_data = product_update_schema.load(data)
        
        # Check if SKU already exists (excluding current product)
        if 'sku' in validated_data:
            existing = Product.query.filter(
                Product.sku == validated_data['sku'],
                Product.id != product_id
            ).first()
            if existing:
                return jsonify({'error': 'Product SKU already exists'}), 400
        
        # Check if slug already exists (excluding current product)
        if 'slug' in validated_data:
            existing = Product.query.filter(
                Product.slug == validated_data['slug'],
                Product.id != product_id
            ).first()
            if existing:
                return jsonify({'error': 'Product slug already exists'}), 400
        
        # Validate category exists
        if 'category_id' in validated_data:
            category = Category.query.get(validated_data['category_id'])
            if not category:
                return jsonify({'error': 'Category not found'}), 404
        
        # Update product fields
        for field, value in validated_data.items():
            if field != 'images':  # Handle images separately
                setattr(product, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update product'}), 500

@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product (admin only)"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        db.session.delete(product)
        db.session.commit()

        return jsonify({
            'message': 'Product deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete product'}), 500

# Product image endpoints
@products_bp.route('/<product_id>/images', methods=['POST'])
@admin_required
def add_product_image(product_id):
    """Add image to product (admin only)"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        data = sanitize_input(request.get_json())
        validated_data = product_image_schema.load(data)

        # If this is set as primary, unset other primary images
        if validated_data.get('is_primary', False):
            ProductImage.query.filter_by(product_id=product_id).update({'is_primary': False})

        image = ProductImage(product_id=product_id, **validated_data)
        db.session.add(image)
        db.session.commit()

        return jsonify({
            'message': 'Image added successfully',
            'image': image.to_dict()
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add image'}), 500

@products_bp.route('/<product_id>/images/<image_id>', methods=['PUT'])
@admin_required
def update_product_image(product_id, image_id):
    """Update product image (admin only)"""
    try:
        image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
        if not image:
            return jsonify({'error': 'Image not found'}), 404

        data = sanitize_input(request.get_json())
        validated_data = product_image_schema.load(data, partial=True)

        # If this is set as primary, unset other primary images
        if validated_data.get('is_primary', False):
            ProductImage.query.filter_by(product_id=product_id).filter(
                ProductImage.id != image_id
            ).update({'is_primary': False})

        # Update image fields
        for field, value in validated_data.items():
            setattr(image, field, value)

        db.session.commit()

        return jsonify({
            'message': 'Image updated successfully',
            'image': image.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update image'}), 500

@products_bp.route('/<product_id>/images/<image_id>', methods=['DELETE'])
@admin_required
def delete_product_image(product_id, image_id):
    """Delete product image (admin only)"""
    try:
        image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
        if not image:
            return jsonify({'error': 'Image not found'}), 404

        db.session.delete(image)
        db.session.commit()

        return jsonify({
            'message': 'Image deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete image'}), 500
