import paypalrestsdk
from flask import current_app
import hmac
import hashlib
import base64
import json
from datetime import datetime

class PayPalClient:
    """PayPal payment client wrapper"""
    
    def __init__(self):
        paypalrestsdk.configure({
            "mode": current_app.config['PAYPAL_MODE'],
            "client_id": current_app.config['PAYPAL_CLIENT_ID'],
            "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
        })
        self.webhook_id = current_app.config.get('PAYPAL_WEBHOOK_ID')
    
    def create_payment(self, amount, currency, return_url, cancel_url, description="Payment", items=None):
        """Create a PayPal payment"""
        try:
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": description
                }]
            }
            
            # Add items if provided
            if items:
                payment_data["transactions"][0]["item_list"] = {"items": items}
            
            payment = paypalrestsdk.Payment(payment_data)
            
            if payment.create():
                current_app.logger.info(f"PayPal payment created: {payment.id}")
                return payment
            else:
                current_app.logger.error(f"PayPal payment creation failed: {payment.error}")
                raise Exception(f"Payment creation failed: {payment.error}")
                
        except Exception as e:
            current_app.logger.error(f"PayPal payment creation failed: {str(e)}")
            raise e
    
    def execute_payment(self, payment_id, payer_id):
        """Execute a PayPal payment after user approval"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                current_app.logger.info(f"PayPal payment executed: {payment_id}")
                return payment
            else:
                current_app.logger.error(f"PayPal payment execution failed: {payment.error}")
                raise Exception(f"Payment execution failed: {payment.error}")
                
        except Exception as e:
            current_app.logger.error(f"PayPal payment execution failed: {str(e)}")
            raise e
    
    def get_payment(self, payment_id):
        """Get payment details"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return payment
        except Exception as e:
            current_app.logger.error(f"PayPal get payment failed: {str(e)}")
            raise e
    
    def refund_payment(self, sale_id, amount=None, currency="USD"):
        """Refund a payment"""
        try:
            sale = paypalrestsdk.Sale.find(sale_id)
            
            refund_data = {}
            if amount:
                refund_data = {
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    }
                }
            
            refund = sale.refund(refund_data)
            
            if refund:
                current_app.logger.info(f"PayPal refund created: {refund.id}")
                return refund
            else:
                current_app.logger.error(f"PayPal refund failed: {sale.error}")
                raise Exception(f"Refund failed: {sale.error}")
                
        except Exception as e:
            current_app.logger.error(f"PayPal refund failed: {str(e)}")
            raise e
    
    def get_refund(self, refund_id):
        """Get refund details"""
        try:
            refund = paypalrestsdk.Refund.find(refund_id)
            return refund
        except Exception as e:
            current_app.logger.error(f"PayPal get refund failed: {str(e)}")
            raise e
    
    def create_webhook_event_verification(self, headers, body):
        """Verify webhook event signature"""
        try:
            if not self.webhook_id:
                current_app.logger.warning("PayPal webhook ID not configured")
                return False
            
            # PayPal webhook verification
            webhook_event = paypalrestsdk.WebhookEvent({
                "id": headers.get('PAYPAL-TRANSMISSION-ID'),
                "create_time": headers.get('PAYPAL-TRANSMISSION-TIME'),
                "resource_type": headers.get('PAYPAL-TRANSMISSION-SIG'),
                "event_type": headers.get('PAYPAL-TRANSMISSION-SIG'),
                "summary": "Webhook event verification",
                "resource": json.loads(body)
            })
            
            verification_data = {
                "transmission_id": headers.get('PAYPAL-TRANSMISSION-ID'),
                "cert_id": headers.get('PAYPAL-CERT-ID'),
                "auth_algo": headers.get('PAYPAL-AUTH-ALGO'),
                "transmission_sig": headers.get('PAYPAL-TRANSMISSION-SIG'),
                "transmission_time": headers.get('PAYPAL-TRANSMISSION-TIME'),
                "webhook_id": self.webhook_id,
                "webhook_event": webhook_event
            }
            
            result = paypalrestsdk.WebhookEvent.verify(verification_data)
            return result
            
        except Exception as e:
            current_app.logger.error(f"PayPal webhook verification failed: {str(e)}")
            return False
    
    def create_direct_payment(self, amount, currency, credit_card_data, description="Payment"):
        """Create a direct credit card payment"""
        try:
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "credit_card",
                    "funding_instruments": [{
                        "credit_card": credit_card_data
                    }]
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": description
                }]
            }
            
            payment = paypalrestsdk.Payment(payment_data)
            
            if payment.create():
                current_app.logger.info(f"PayPal direct payment created: {payment.id}")
                return payment
            else:
                current_app.logger.error(f"PayPal direct payment creation failed: {payment.error}")
                raise Exception(f"Direct payment creation failed: {payment.error}")
                
        except Exception as e:
            current_app.logger.error(f"PayPal direct payment creation failed: {str(e)}")
            raise e
    
    def get_payment_approval_url(self, payment):
        """Get the approval URL from a payment"""
        try:
            for link in payment.links:
                if link.rel == "approval_url":
                    return link.href
            return None
        except Exception as e:
            current_app.logger.error(f"Failed to get approval URL: {str(e)}")
            return None
    
    def create_billing_agreement(self, plan_id, name, description, start_date):
        """Create a billing agreement for subscriptions"""
        try:
            billing_agreement = paypalrestsdk.BillingAgreement({
                "name": name,
                "description": description,
                "start_date": start_date,
                "plan": {
                    "id": plan_id
                },
                "payer": {
                    "payment_method": "paypal"
                }
            })
            
            if billing_agreement.create():
                current_app.logger.info(f"PayPal billing agreement created: {billing_agreement.token}")
                return billing_agreement
            else:
                current_app.logger.error(f"PayPal billing agreement creation failed: {billing_agreement.error}")
                raise Exception(f"Billing agreement creation failed: {billing_agreement.error}")
                
        except Exception as e:
            current_app.logger.error(f"PayPal billing agreement creation failed: {str(e)}")
            raise e

def get_paypal_client():
    """Get PayPal client instance"""
    return PayPalClient()
