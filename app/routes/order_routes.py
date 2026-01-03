"""
Order routes with authentication.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.order_services import (
    create_order_from_cart,
    get_order_by_id,
    get_orders_by_user,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import get_current_user_id

order_bp = Blueprint("order", __name__)


@order_bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    """Create an order from cart (requires login)."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    data = request.get_json() or {}
    
    # Required shipping data
    shipping_data = {
        "customer_name": data.get("customer_name"),
        "customer_email": data.get("customer_email"),
        "customer_phone": data.get("customer_phone"),
        "address_line1": data.get("address_line1"),
        "address_line2": data.get("address_line2"),
        "city": data.get("city"),
        "state": data.get("state"),
        "postal_code": data.get("postal_code"),
        "country": data.get("country", "India"),
        "notes": data.get("notes"),
    }

    # Validate required fields
    required = ["customer_name", "customer_email", "address_line1", "city", "state", "postal_code"]
    missing = [f for f in required if not shipping_data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        order = create_order_from_cart(user_id, shipping_data)
        return success_response(order, 201)
    except Exception as e:
        return error_response(str(e), 400)


@order_bp.route("/", methods=["GET"])
@jwt_required()
def list_my_orders():
    """Get current user's orders."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    orders = get_orders_by_user(user_id)
    return success_response(orders)


@order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """Get order details."""
    user_id = get_current_user_id()
    
    order = get_order_by_id(order_id, user_id)
    if not order:
        return error_response("Order not found", 404)
    
    return success_response(order)


@order_bp.route("/shipping-info", methods=["GET"])
def get_shipping_info():
    """Get shipping charges info (public)."""
    from flask import current_app
    
    threshold = current_app.config.get("SHIPPING_FREE_THRESHOLD", 2000)
    charge = current_app.config.get("SHIPPING_CHARGE", 49)
    
    return success_response({
        "free_shipping_threshold": threshold,
        "shipping_charge": charge,
        "message": f"Free shipping on orders above ₹{int(threshold)}. Shipping charge: ₹{int(charge)} for orders below ₹{int(threshold)}."
    })
