from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.cart_services import add_to_cart, remove_from_cart, get_user_cart
from app.utils.response import success_response, error_response

# ❗️ IMPORTANT: No prefix here
cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/", methods=["GET"])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()
    #user_id = request.args.get("user_id")
    cart_items = get_user_cart(user_id)
    return success_response(cart_items)

@cart_bp.route("/add", methods=["POST"])
@jwt_required()
def add_item():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    item = add_to_cart(data)
    if item:
        return success_response(item, 201)
    return error_response("Failed to add item", 400)

@cart_bp.route("/remove", methods=["DELETE"])
def remove_item():
    data = request.get_json() or {}
    success = remove_from_cart(data)
    if success:
        return success_response({"message": "Item removed"})
    return error_response("Failed to remove item", 400)
