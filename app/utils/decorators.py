"""
Authentication and authorization decorators.
"""

from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.extensions import db
from app.models.user import User


def admin_required(fn):
    """
    Decorator that requires the user to be an admin.
    Must be used after @jwt_required() or will verify JWT itself.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Authentication required",
                "code": "unauthorized"
            }), 401
        
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Invalid token",
                "code": "unauthorized"
            }), 401
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found",
                "code": "not_found"
            }), 404
        
        if not user.is_admin:
            return jsonify({
                "status": "error",
                "message": "Admin access required",
                "code": "forbidden"
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def login_required(fn):
    """
    Decorator that requires the user to be logged in.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Authentication required",
                "code": "unauthorized"
            }), 401
        
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Invalid token",
                "code": "unauthorized"
            }), 401
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found",
                "code": "not_found"
            }), 404
        
        if not user.is_active:
            return jsonify({
                "status": "error",
                "message": "Account is deactivated",
                "code": "forbidden"
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Get the current logged-in user from JWT token."""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        pass
    return None


def get_current_user_id():
    """Get the current user ID from JWT token."""
    try:
        user_id = get_jwt_identity()
        return int(user_id) if user_id else None
    except (ValueError, TypeError):
        return None
