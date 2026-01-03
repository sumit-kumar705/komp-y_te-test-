"""
Category routes - GET is public, POST/PUT/DELETE require admin.
"""

from flask import Blueprint, request

from app.services.category_services import (
    get_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

category_bp = Blueprint("category", __name__)


# ============================================
# PUBLIC ROUTES (Guest can access)
# ============================================

@category_bp.route("/", methods=["GET"])
def list_categories():
    """Get all categories (public)."""
    categories = get_categories()
    return success_response(categories)


@category_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """Get category by ID (public)."""
    category = get_category_by_id(category_id)
    if category:
        return success_response(category)
    return error_response("Category not found", 404)


# ============================================
# ADMIN ROUTES
# ============================================

@category_bp.route("/", methods=["POST"])
@admin_required
def add_category():
    """Create a category (admin only)."""
    data = request.get_json() or {}
    
    if not data.get("name"):
        return error_response("Name is required", 400)
    
    try:
        category = create_category(data)
        if category:
            return success_response(category, 201)
        return error_response("Failed to create category", 400)
    except Exception as e:
        return error_response(str(e), 400)


@category_bp.route("/<int:category_id>", methods=["PUT"])
@admin_required
def edit_category(category_id):
    """Update a category (admin only)."""
    data = request.get_json() or {}
    
    try:
        updated = update_category(category_id, data)
        if updated:
            return success_response(updated)
        return error_response("Category not found", 404)
    except Exception as e:
        return error_response(str(e), 400)


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@admin_required
def remove_category(category_id):
    """Delete a category (admin only)."""
    deleted = delete_category(category_id)
    if deleted:
        return success_response({"deleted": category_id})
    return error_response("Category not found", 404)
