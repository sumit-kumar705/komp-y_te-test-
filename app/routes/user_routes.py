"""
User routes for profile management.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.auth_services import get_user_by_id, update_user_profile
from app.utils.response import success_response, error_response
from app.utils.decorators import get_current_user_id

user_bp = Blueprint("user", __name__)


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user's profile."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    user = get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    
    return success_response(user)


@user_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user's profile."""
    user_id = get_current_user_id()
    if not user_id:
        return error_response("Authentication required", 401)

    data = request.get_json() or {}
    
    try:
        user = update_user_profile(user_id, data)
        if user:
            return success_response(user)
        return error_response("User not found", 404)
    except Exception as e:
        return error_response(str(e), 400)
