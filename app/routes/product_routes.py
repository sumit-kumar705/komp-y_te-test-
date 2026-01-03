"""
Product routes - GET is public (guest browsing), POST/PUT/DELETE require admin.
"""

from flask import Blueprint, request

from app.services.product_services import (
    get_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    get_featured_products,
    search_products,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

product_bp = Blueprint("product", __name__)


# ============================================
# PUBLIC ROUTES (Guest can access)
# ============================================

@product_bp.route("/", methods=["GET"])
def list_products():
    """Get all products (public - guest can browse)."""
    # Optional filters
    category_id = request.args.get("category_id", type=int)
    featured_only = request.args.get("featured", "").lower() == "true"
    search_query = request.args.get("search")
    
    if search_query:
        products = search_products(search_query)
    elif featured_only:
        products = get_featured_products()
    else:
        products = get_products(category_id=category_id)
    
    return success_response(products)


@product_bp.route("/featured", methods=["GET"])
def list_featured_products():
    """Get featured products (public)."""
    products = get_featured_products()
    return success_response(products)


@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Get product by ID (public)."""
    product = get_product_by_id(product_id)
    if product:
        return success_response(product)
    return error_response("Product not found", 404)


# ============================================
# ADMIN ROUTES (Require authentication)
# ============================================

@product_bp.route("/", methods=["POST"])
@admin_required
def add_product():
    """Create a product (admin only)."""
    data = request.get_json() or {}
    
    # Validate required fields
    if not data.get("name") or not data.get("price"):
        return error_response("Name and price are required", 400)
    
    try:
        product = create_product(data)
        if product:
            return success_response(product, 201)
        return error_response("Failed to create product", 400)
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def edit_product(product_id):
    """Update a product (admin only)."""
    data = request.get_json() or {}
    
    try:
        updated = update_product(product_id, data)
        if updated:
            return success_response(updated)
        return error_response("Product not found", 404)
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def remove_product(product_id):
    """Delete a product (admin only)."""
    try:
        deleted = delete_product(product_id)
        if deleted:
            return success_response({"deleted": product_id})
        return error_response("Product not found", 404)
    except Exception as e:
        return error_response(str(e), 400)
