from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from app import db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import AddToCartSchema, UpdateCartItemSchema
from app.utils.auth import token_required, get_current_user, sanitize_input

cart_bp = Blueprint('cart', __name__)

# Schema instances
add_to_cart_schema = AddToCartSchema()
update_cart_item_schema = UpdateCartItemSchema()

def get_or_create_cart(user):
    """Get or create cart for user"""
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
    return cart

@cart_bp.route('', methods=['GET'])
@token_required
def get_cart():
    """Get user's cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cart = get_or_create_cart(user)
        
        return jsonify({
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get cart'}), 500

@cart_bp.route('/add', methods=['POST'])
@token_required
def add_to_cart():
    """Add item to cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = add_to_cart_schema.load(data)
        
        # Check if product exists and is active
        product = Product.query.get(validated_data['product_id'])
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if not product.is_active:
            return jsonify({'error': 'Product is not available'}), 400
        
        # Check inventory if tracking is enabled
        if product.track_inventory:
            if product.inventory_quantity < validated_data['quantity']:
                return jsonify({
                    'error': 'Insufficient inventory',
                    'available_quantity': product.inventory_quantity
                }), 400
        
        # Get or create cart
        cart = get_or_create_cart(user)
        
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=product.id
        ).first()
        
        if existing_item:
            # Check total quantity after adding
            new_quantity = existing_item.quantity + validated_data['quantity']
            
            if product.track_inventory and new_quantity > product.inventory_quantity:
                return jsonify({
                    'error': 'Insufficient inventory',
                    'available_quantity': product.inventory_quantity,
                    'current_in_cart': existing_item.quantity
                }), 400
            
            existing_item.quantity = new_quantity
            existing_item.updated_at = datetime.utcnow()
            item = existing_item
        else:
            # Create new cart item
            item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=validated_data['quantity'],
                price=product.price
            )
            db.session.add(item)

        cart.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Item added to cart successfully',
            'cart': cart.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add item to cart'}), 500

@cart_bp.route('/update/<item_id>', methods=['PUT'])
@token_required
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = update_cart_item_schema.load(data)
        
        # Get cart
        cart = get_or_create_cart(user)
        
        # Find cart item
        item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
        if not item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        # If quantity is 0, remove item
        if validated_data['quantity'] == 0:
            db.session.delete(item)
        else:
            # Check inventory if tracking is enabled
            if item.product.track_inventory:
                if item.product.inventory_quantity < validated_data['quantity']:
                    return jsonify({
                        'error': 'Insufficient inventory',
                        'available_quantity': item.product.inventory_quantity
                    }), 400
            
            item.quantity = validated_data['quantity']
            item.updated_at = datetime.utcnow()

        cart.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Cart item updated successfully',
            'cart': cart.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update cart item'}), 500

@cart_bp.route('/remove/<item_id>', methods=['DELETE'])
@token_required
def remove_cart_item(item_id):
    """Remove item from cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get cart
        cart = get_or_create_cart(user)
        
        # Find cart item
        item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
        if not item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(item)
        cart.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Item removed from cart successfully',
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove cart item'}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@token_required
def clear_cart():
    """Clear all items from cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get cart
        cart = get_or_create_cart(user)
        
        # Delete all cart items
        CartItem.query.filter_by(cart_id=cart.id).delete()
        cart.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Cart cleared successfully',
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to clear cart'}), 500

@cart_bp.route('/count', methods=['GET'])
@token_required
def get_cart_count():
    """Get cart item count"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cart = get_or_create_cart(user)
        
        return jsonify({
            'count': cart.total_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get cart count'}), 500

@cart_bp.route('/validate', methods=['POST'])
@token_required
def validate_cart():
    """Validate cart items (check availability, prices, etc.)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cart = get_or_create_cart(user)
        
        issues = []
        updated_items = []
        
        for item in cart.items:
            item_issues = []
            
            # Check if product still exists and is active
            if not item.product or not item.product.is_active:
                item_issues.append('Product is no longer available')
            else:
                # Check inventory
                if item.product.track_inventory:
                    if item.product.inventory_quantity < item.quantity:
                        item_issues.append(f'Only {item.product.inventory_quantity} items available')
                        # Auto-adjust quantity
                        if item.product.inventory_quantity > 0:
                            item.quantity = item.product.inventory_quantity
                            updated_items.append(item.id)
                        else:
                            item_issues.append('Product is out of stock')
                
                # Check price changes
                if item.price != item.product.price:
                    item_issues.append(f'Price changed from ${item.price} to ${item.product.price}')
                    # Auto-update price
                    item.price = item.product.price
                    updated_items.append(item.id)
            
            if item_issues:
                issues.append({
                    'item_id': item.id,
                    'product_name': item.product.name if item.product else 'Unknown Product',
                    'issues': item_issues
                })
        
        # Save any updates
        if updated_items:
            cart.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues,
            'updated_items': updated_items,
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to validate cart'}), 500
