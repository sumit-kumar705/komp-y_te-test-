"""
Booking routes for consultation scheduling.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required

from app.services.booking_services import (
    calculate_session_price,
    create_booking,
    confirm_booking_payment,
    get_user_bookings,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import get_current_user_id

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/pricing", methods=["GET"])
@jwt_required()
def get_consultation_pricing():
    """Get consultation pricing for current user."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    pricing = calculate_session_price(user_id)
    return success_response({
        **pricing,
        "description": "First 20 minutes free! Subsequent sessions are ₹250 for 20 minutes."
    })


@booking_bp.route("/", methods=["POST"])
@jwt_required()
def create_consultation_booking():
    """Create a consultation booking."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    data = request.get_json() or {}
    
    try:
        booking = create_booking(user_id, data)
        return success_response(booking, 201)
    except Exception as e:
        return error_response(str(e), 400)


@booking_bp.route("/", methods=["GET"])
@jwt_required()
def list_my_bookings():
    """Get current user's bookings."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    bookings = get_user_bookings(user_id)
    return success_response(bookings)


@booking_bp.route("/confirm-payment", methods=["POST"])
@jwt_required()
def confirm_paid_booking():
    """Confirm payment for a paid consultation booking."""
    data = request.get_json() or {}
    
    booking_id = data.get("booking_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    
    if not booking_id or not razorpay_payment_id:
        return error_response("Missing booking_id or payment_id", 400)

    try:
        booking = confirm_booking_payment(booking_id, razorpay_payment_id)
        return success_response(booking)
    except Exception as e:
        return error_response(str(e), 400)


@booking_bp.route("/info", methods=["GET"])
def get_consultation_info():
    """Get consultation info (public)."""
    return success_response({
        "free_session": {
            "duration_minutes": current_app.config.get("CONSULTATION_FREE_MINUTES", 20),
            "price": 0,
            "description": "First consultation is FREE for new users"
        },
        "paid_session": {
            "duration_minutes": current_app.config.get("CONSULTATION_SESSION_MINUTES", 20),
            "price": current_app.config.get("CONSULTATION_PAID_PRICE", 250),
            "description": "₹250 for each 20-minute consultation session"
        },
        "contact_whatsapp": current_app.config.get("ADMIN_WHATSAPP", "918149550229"),
    })
