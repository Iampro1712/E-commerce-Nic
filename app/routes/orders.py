from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import and_, or_
from datetime import datetime
from app import db
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.order import (
    CreateOrderSchema, UpdateOrderStatusSchema, OrderSearchSchema
)
from app.utils.auth import token_required, admin_required, get_current_user, sanitize_input

orders_bp = Blueprint('orders', __name__)

# Schema instances
create_order_schema = CreateOrderSchema()
update_order_status_schema = UpdateOrderStatusSchema()
order_search_schema = OrderSearchSchema()

def calculate_order_totals(cart_items, shipping_amount=0, tax_rate=0.15):
    """Calculate order totals"""
    subtotal = sum(item.total_price for item in cart_items)
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount + shipping_amount
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount
    }

@orders_bp.route('', methods=['POST'])
@token_required
def create_order():
    """Create new order from cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = create_order_schema.load(data)
        
        # Get user's cart
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart or not cart.items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Validate cart items
        for item in cart.items:
            if not item.product or not item.product.is_active:
                return jsonify({'error': f'Product {item.product.name if item.product else "Unknown"} is no longer available'}), 400
            
            if item.product.track_inventory and item.product.inventory_quantity < item.quantity:
                return jsonify({
                    'error': f'Insufficient inventory for {item.product.name}',
                    'available_quantity': item.product.inventory_quantity
                }), 400
        
        # Calculate totals
        shipping_amount = 10.00  # Fixed shipping for now
        totals = calculate_order_totals(cart.items, shipping_amount)
        
        # Create order
        order_data = {
            'user_id': user.id,
            'subtotal': totals['subtotal'],
            'tax_amount': totals['tax_amount'],
            'shipping_amount': totals['shipping_amount'],
            'total_amount': totals['total_amount'],
            'currency': validated_data.get('currency', 'USD'),
            'payment_method': validated_data['payment_method'],
            'customer_notes': validated_data.get('customer_notes'),
            
            # Shipping address
            'shipping_first_name': validated_data['shipping_address']['first_name'],
            'shipping_last_name': validated_data['shipping_address']['last_name'],
            'shipping_company': validated_data['shipping_address'].get('company'),
            'shipping_address_line_1': validated_data['shipping_address']['address_line_1'],
            'shipping_address_line_2': validated_data['shipping_address'].get('address_line_2'),
            'shipping_city': validated_data['shipping_address']['city'],
            'shipping_state': validated_data['shipping_address']['state'],
            'shipping_postal_code': validated_data['shipping_address']['postal_code'],
            'shipping_country': validated_data['shipping_address']['country'],
            'shipping_phone': validated_data['shipping_address'].get('phone'),
            
            # Billing address
            'billing_first_name': validated_data['billing_address']['first_name'],
            'billing_last_name': validated_data['billing_address']['last_name'],
            'billing_company': validated_data['billing_address'].get('company'),
            'billing_address_line_1': validated_data['billing_address']['address_line_1'],
            'billing_address_line_2': validated_data['billing_address'].get('address_line_2'),
            'billing_city': validated_data['billing_address']['city'],
            'billing_state': validated_data['billing_address']['state'],
            'billing_postal_code': validated_data['billing_address']['postal_code'],
            'billing_country': validated_data['billing_address']['country'],
            'billing_phone': validated_data['billing_address'].get('phone')
        }
        
        order = Order(**order_data)
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update inventory
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                product_price=cart_item.price,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price
            )
            db.session.add(order_item)
            
            # Update product inventory
            if cart_item.product.track_inventory:
                cart_item.product.inventory_quantity -= cart_item.quantity
        
        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create order'}), 500

@orders_bp.route('', methods=['GET'])
@token_required
def get_orders():
    """Get user's orders with search and filtering"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Parse query parameters
        args = request.args.to_dict()
        validated_params = order_search_schema.load(args)
        
        # Build query
        query = Order.query.filter_by(user_id=user.id)
        
        # Apply filters
        if validated_params.get('status'):
            query = query.filter(Order.status == OrderStatus(validated_params['status']))
        
        if validated_params.get('payment_status'):
            query = query.filter(Order.payment_status == PaymentStatus(validated_params['payment_status']))
        
        if validated_params.get('order_number'):
            query = query.filter(Order.order_number.ilike(f"%{validated_params['order_number']}%"))
        
        if validated_params.get('start_date'):
            query = query.filter(Order.created_at >= validated_params['start_date'])
        
        if validated_params.get('end_date'):
            query = query.filter(Order.created_at <= validated_params['end_date'])
        
        if validated_params.get('min_amount'):
            query = query.filter(Order.total_amount >= validated_params['min_amount'])
        
        if validated_params.get('max_amount'):
            query = query.filter(Order.total_amount <= validated_params['max_amount'])
        
        # Apply sorting
        sort_by = validated_params.get('sort_by', 'created_at')
        sort_order = validated_params.get('sort_order', 'desc')
        
        if sort_by == 'order_number':
            order_field = Order.order_number
        elif sort_by == 'total_amount':
            order_field = Order.total_amount
        elif sort_by == 'updated_at':
            order_field = Order.updated_at
        else:  # created_at
            order_field = Order.created_at
        
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
            'orders': [order.to_dict() for order in paginated.items],
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
        return jsonify({'error': 'Failed to get orders'}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get specific order"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get order (user can only see their own orders unless admin)
        if user.is_admin:
            order = Order.query.get(order_id)
        else:
            order = Order.query.filter_by(id=order_id, user_id=user.id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get order'}), 500

@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """Cancel order"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get order (user can only cancel their own orders)
        order = Order.query.filter_by(id=order_id, user_id=user.id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if order can be cancelled
        if not order.can_be_cancelled():
            return jsonify({'error': 'Order cannot be cancelled'}), 400
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        
        # Restore inventory
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product and product.track_inventory:
                product.inventory_quantity += item.quantity
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel order'}), 500

# Admin endpoints
@orders_bp.route('/admin/all', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders (admin only)"""
    try:
        # Parse query parameters
        args = request.args.to_dict()
        validated_params = order_search_schema.load(args)
        
        # Build query
        query = Order.query
        
        # Apply filters (same as user orders but without user_id filter)
        if validated_params.get('status'):
            query = query.filter(Order.status == OrderStatus(validated_params['status']))
        
        if validated_params.get('payment_status'):
            query = query.filter(Order.payment_status == PaymentStatus(validated_params['payment_status']))
        
        if validated_params.get('order_number'):
            query = query.filter(Order.order_number.ilike(f"%{validated_params['order_number']}%"))
        
        if validated_params.get('start_date'):
            query = query.filter(Order.created_at >= validated_params['start_date'])
        
        if validated_params.get('end_date'):
            query = query.filter(Order.created_at <= validated_params['end_date'])
        
        if validated_params.get('min_amount'):
            query = query.filter(Order.total_amount >= validated_params['min_amount'])
        
        if validated_params.get('max_amount'):
            query = query.filter(Order.total_amount <= validated_params['max_amount'])
        
        # Apply sorting
        sort_by = validated_params.get('sort_by', 'created_at')
        sort_order = validated_params.get('sort_order', 'desc')
        
        if sort_by == 'order_number':
            order_field = Order.order_number
        elif sort_by == 'total_amount':
            order_field = Order.total_amount
        elif sort_by == 'updated_at':
            order_field = Order.updated_at
        else:  # created_at
            order_field = Order.created_at
        
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
            'orders': [order.to_dict() for order in paginated.items],
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
        return jsonify({'error': 'Failed to get orders'}), 500

@orders_bp.route('/admin/<order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Update order status (admin only)"""
    try:
        # Get order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = update_order_status_schema.load(data)

        # Update order status
        old_status = order.status
        order.status = OrderStatus(validated_data['status'])
        order.updated_at = datetime.utcnow()

        # Update admin notes if provided
        if validated_data.get('admin_notes'):
            order.admin_notes = validated_data['admin_notes']

        # Handle status-specific logic
        if order.status == OrderStatus.SHIPPED and old_status != OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif order.status == OrderStatus.DELIVERED and old_status != OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        elif order.status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
            # Restore inventory
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product and product.track_inventory:
                    product.inventory_quantity += item.quantity

        db.session.commit()

        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order status'}), 500

@orders_bp.route('/stats', methods=['GET'])
@admin_required
def get_order_stats():
    """Get order statistics (admin only)"""
    try:
        from sqlalchemy import func

        # Total orders
        total_orders = Order.query.count()

        # Orders by status
        status_stats = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()

        # Orders by payment status
        payment_status_stats = db.session.query(
            Order.payment_status,
            func.count(Order.id).label('count')
        ).group_by(Order.payment_status).all()

        # Revenue stats
        total_revenue = db.session.query(
            func.sum(Order.total_amount)
        ).filter(Order.payment_status == PaymentStatus.PAID).scalar() or 0

        # Recent orders (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders = Order.query.filter(Order.created_at >= thirty_days_ago).count()

        # Average order value
        avg_order_value = db.session.query(
            func.avg(Order.total_amount)
        ).filter(Order.payment_status == PaymentStatus.PAID).scalar() or 0

        return jsonify({
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'total_revenue': float(total_revenue),
            'average_order_value': float(avg_order_value),
            'status_breakdown': {
                status.value: count for status, count in status_stats
            },
            'payment_status_breakdown': {
                status.value: count for status, count in payment_status_stats
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get order statistics'}), 500
