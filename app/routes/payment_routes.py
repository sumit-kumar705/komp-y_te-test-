"""
Payment routes with Razorpay integration.
"""

from flask import Blueprint, request

from flask_jwt_extended import jwt_required

from app.services.payment_services import (
    create_razorpay_order,
    verify_razorpay_payment,
    get_payment_by_order,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import get_current_user_id

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/create/<int:order_id>", methods=["POST"])
@jwt_required()
def initiate_payment(order_id):
    """Create Razorpay order for payment."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    try:
        result = create_razorpay_order(order_id)
        return success_response(result, 201)
    except Exception as e:
        return error_response(str(e), 400)


@payment_bp.route("/verify", methods=["POST"])
@jwt_required()
def verify_payment():
    """Verify Razorpay payment after successful payment."""
    data = request.get_json() or {}
    
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")
    
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return error_response("Missing payment verification data", 400)

    try:
        result = verify_razorpay_payment(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 400)


@payment_bp.route("/order/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_payment(order_id):
    """Get payment details for an order."""
    payment = get_payment_by_order(order_id)
    if payment:
        return success_response(payment)
    return error_response("Payment not found", 404)
