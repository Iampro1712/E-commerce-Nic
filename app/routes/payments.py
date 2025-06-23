from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from app import db
from app.models.order import Order, PaymentStatus
from app.utils.paypal_client import get_paypal_client
from app.schemas.payment import (
    PayPalPaymentSchema, PayPalExecutePaymentSchema, PayPalDirectPaymentSchema,
    PayPalRefundSchema, PayPalWebhookSchema, CreditCardSchema
)
from app.utils.auth import token_required, admin_required, get_current_user, sanitize_input
import json

payments_bp = Blueprint('payments', __name__)

# Schema instances
paypal_payment_schema = PayPalPaymentSchema()
paypal_execute_schema = PayPalExecutePaymentSchema()
paypal_direct_schema = PayPalDirectPaymentSchema()
paypal_refund_schema = PayPalRefundSchema()
paypal_webhook_schema = PayPalWebhookSchema()
credit_card_schema = CreditCardSchema()

@payments_bp.route('/create', methods=['POST'])
@token_required
def create_payment():
    """Create PayPal payment"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = paypal_payment_schema.load(data)

        # Get PayPal client
        paypal_client = get_paypal_client()

        # Create payment
        payment = paypal_client.create_payment(
            amount=validated_data['amount'],
            currency=validated_data['currency'],
            return_url=validated_data['return_url'],
            cancel_url=validated_data['cancel_url'],
            description=validated_data.get('description', 'Payment'),
            items=validated_data.get('items', [])
        )

        # Get approval URL
        approval_url = paypal_client.get_payment_approval_url(payment)

        return jsonify({
            'payment_id': payment.id,
            'approval_url': approval_url,
            'status': payment.state
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Create payment failed: {str(e)}")
        return jsonify({'error': 'Failed to create payment'}), 500

@payments_bp.route('/execute', methods=['POST'])
@token_required
def execute_payment():
    """Execute PayPal payment after user approval"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = paypal_execute_schema.load(data)

        # Get PayPal client
        paypal_client = get_paypal_client()

        # Execute payment
        payment = paypal_client.execute_payment(
            payment_id=validated_data['payment_id'],
            payer_id=validated_data['payer_id']
        )

        # Update order payment status if order exists
        order = Order.query.filter_by(payment_reference=payment.id).first()
        if order:
            if payment.state == 'approved':
                order.payment_status = PaymentStatus.PAID
            else:
                order.payment_status = PaymentStatus.FAILED
            db.session.commit()

        return jsonify({
            'payment_id': payment.id,
            'status': payment.state,
            'payer_email': payment.payer.payer_info.email if payment.payer.payer_info else None
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Execute payment failed: {str(e)}")
        return jsonify({'error': 'Failed to execute payment'}), 500

@payments_bp.route('/refund', methods=['POST'])
@admin_required
def refund_payment():
    """Refund PayPal payment (admin only)"""
    try:
        # Validate input data
        data = sanitize_input(request.get_json())
        validated_data = paypal_refund_schema.load(data)

        # Get PayPal client
        paypal_client = get_paypal_client()

        # Create refund
        refund = paypal_client.refund_payment(
            sale_id=validated_data['sale_id'],
            amount=validated_data.get('amount'),
            currency=validated_data.get('currency', 'USD')
        )

        # Update order payment status if order exists
        order = Order.query.filter_by(payment_reference=validated_data['sale_id']).first()
        if order:
            if validated_data.get('amount') and validated_data['amount'] >= order.total_amount:
                order.payment_status = PaymentStatus.REFUNDED
            else:
                order.payment_status = PaymentStatus.PARTIALLY_REFUNDED
            db.session.commit()

        return jsonify({
            'refund_id': refund.id,
            'status': refund.state,
            'amount': refund.amount.total if refund.amount else None,
            'currency': refund.amount.currency if refund.amount else None
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Refund payment failed: {str(e)}")
        return jsonify({'error': 'Failed to refund payment'}), 500

@payments_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle PayPal webhook notifications"""
    try:
        # Get raw payload and headers
        payload = request.get_data(as_text=True)
        headers = dict(request.headers)

        # Get PayPal client and verify webhook
        paypal_client = get_paypal_client()
        is_valid = paypal_client.create_webhook_event_verification(headers, payload)

        if not is_valid:
            current_app.logger.warning("PayPal webhook verification failed")
            return jsonify({'error': 'Invalid webhook'}), 401

        # Parse webhook data
        webhook_data = json.loads(payload)
        validated_data = paypal_webhook_schema.load(webhook_data)

        event_type = validated_data['event_type']
        resource = validated_data['resource']

        current_app.logger.info(f"PayPal webhook received: {event_type}")

        # Process different event types
        if event_type == 'PAYMENT.SALE.COMPLETED':
            # Payment completed
            payment_id = resource.get('parent_payment')
            if payment_id:
                order = Order.query.filter_by(payment_reference=payment_id).first()
                if order:
                    order.payment_status = PaymentStatus.PAID
                    db.session.commit()

        elif event_type == 'PAYMENT.SALE.DENIED':
            # Payment denied
            payment_id = resource.get('parent_payment')
            if payment_id:
                order = Order.query.filter_by(payment_reference=payment_id).first()
                if order:
                    order.payment_status = PaymentStatus.FAILED
                    db.session.commit()

        elif event_type == 'PAYMENT.SALE.REFUNDED':
            # Payment refunded
            payment_id = resource.get('parent_payment')
            if payment_id:
                order = Order.query.filter_by(payment_reference=payment_id).first()
                if order:
                    order.payment_status = PaymentStatus.REFUNDED
                    db.session.commit()

        return jsonify({'status': 'success'}), 200

    except ValidationError as e:
        current_app.logger.error(f"PayPal webhook validation failed: {e.messages}")
        return jsonify({'error': 'Invalid webhook data'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"PayPal webhook processing failed: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500