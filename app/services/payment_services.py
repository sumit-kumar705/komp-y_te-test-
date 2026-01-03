"""
Payment services with Razorpay integration.
"""

import hmac
import hashlib
from datetime import datetime

from flask import current_app
import razorpay

from app.errors import ServiceError, ValidationError
from app.extensions import db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentStatus as PaymentStatusEnum
from app.services.email_service import send_payment_success_email
from app.services.order_services import confirm_order_payment


def get_razorpay_client():
    """Get Razorpay client instance."""
    key_id = current_app.config.get("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        raise ServiceError("Razorpay not configured")
    
    return razorpay.Client(auth=(key_id, key_secret))


def create_razorpay_order(order_id: int) -> dict:
    """
    Create a Razorpay order for payment.
    Returns the Razorpay order details needed by frontend.
    """
    order = db.session.get(Order, order_id)
    if not order:
        raise ValidationError("Order not found")

    if order.payment_status == PaymentStatus.PAID:
        raise ValidationError("Order already paid")

    try:
        client = get_razorpay_client()
        
        # Amount in paise (₹1 = 100 paise)
        amount_paise = int(float(order.total_amount) * 100)
        
        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "notes": {
                "order_id": str(order.id),
                "customer_email": order.customer_email or "",
            }
        })
        
        # Update order with Razorpay order ID
        order.razorpay_order_id = razorpay_order["id"]
        order.payment_status = PaymentStatus.INITIATED
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=float(order.total_amount),
            currency="INR",
            razorpay_order_id=razorpay_order["id"],
            status=PaymentStatusEnum.INITIATED,
        )
        db.session.add(payment)
        
        db.session.commit()
        
        return {
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": current_app.config.get("RAZORPAY_KEY_ID"),
            "amount": amount_paise,
            "currency": "INR",
            "order_id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
        }
        
    except razorpay.errors.BadRequestError as e:
        raise ServiceError(f"Razorpay error: {e}")
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to create payment: {e}")


def verify_razorpay_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> dict:
    """
    Verify Razorpay payment signature and confirm order.
    This is called after successful payment on frontend.
    """
    # Find the payment record
    payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        raise ValidationError("Payment not found")

    order = db.session.get(Order, payment.order_id)
    if not order:
        raise ValidationError("Order not found")

    # Verify signature
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET")
    if not key_secret:
        raise ServiceError("Razorpay not configured")

    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected_signature != razorpay_signature:
        # Payment verification failed
        payment.status = PaymentStatusEnum.FAILED
        payment.error_description = "Signature verification failed"
        order.payment_status = PaymentStatus.FAILED
        db.session.commit()
        raise ValidationError("Payment verification failed")

    # Payment verified successfully
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = PaymentStatusEnum.SUCCESS
    payment.paid_at = datetime.utcnow()
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to update payment: {e}")

    # Confirm the order (deduct stock, clear cart, send email)
    result = confirm_order_payment(order.id, razorpay_payment_id)
    
    # Send payment success email
    try:
        send_payment_success_email(order, payment)
    except Exception as e:
        current_app.logger.error(f"Failed to send payment email: {e}")

    return {
        "success": True,
        "order": result,
        "payment": payment.to_dict(),
    }


def get_payment_by_order(order_id: int) -> dict:
    """Get payment details for an order."""
    payment = Payment.query.filter_by(order_id=order_id).first()
    if payment:
        return payment.to_dict()
    return None
