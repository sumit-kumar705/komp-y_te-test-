"""
Cart routes with authentication.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.cart_services import (
    get_user_cart,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import get_current_user_id

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/", methods=["GET"])
@jwt_required()
def get_cart():
    """Get current user's cart."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    cart = get_user_cart(user_id)
    return success_response(cart)


@cart_bp.route("/", methods=["POST"])
@jwt_required()
def add_item_to_cart():
    """Add item to cart."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return error_response("Product ID is required", 400)

    try:
        result = add_to_cart(user_id, product_id, quantity)
        return success_response(result, 201)
    except Exception as e:
        return error_response(str(e), 400)


@cart_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_cart(product_id):
    """Update cart item quantity."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    data = request.get_json() or {}
    quantity = data.get("quantity")

    if quantity is None:
        return error_response("Quantity is required", 400)

    try:
        result = update_cart_item(user_id, product_id, quantity)
        if result:
            return success_response(result)
        return error_response("Item not found in cart", 404)
    except Exception as e:
        return error_response(str(e), 400)


@cart_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_item_from_cart(product_id):
    """Remove item from cart."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    removed = remove_from_cart(user_id, product_id)
    if removed:
        return success_response({"removed": product_id})
    return error_response("Item not found in cart", 404)


@cart_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def empty_cart():
    """Clear all items from cart."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    clear_cart(user_id)
    return success_response({"message": "Cart cleared"})
