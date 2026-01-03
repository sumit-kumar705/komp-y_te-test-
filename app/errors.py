"""
Application-specific exceptions and error handlers.
"""

from typing import Any, Dict, Optional
from flask import jsonify


class AppError(Exception):
    """Base application error with structured data for JSON responses."""

    default_message: str = "An application error occurred"
    default_status: int = 500
    default_code: str = "app_error"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message
        self.status_code = int(status_code or self.default_status)
        self.code = code or self.default_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        payload = {"status": "error", "message": self.message, "code": self.code}
        if self.details:
            payload["details"] = self.details
        return payload

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code} status={self.status_code} message={self.message!r}>"


class BadRequestError(AppError):
    default_message = "Bad request"
    default_status = 400
    default_code = "bad_request"


class ValidationError(BadRequestError):
    default_message = "Validation failed"
    default_code = "validation_error"

    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=400, code=self.default_code, details=details)


class UnauthorizedError(AppError):
    default_message = "Unauthorized"
    default_status = 401
    default_code = "unauthorized"


class ForbiddenError(AppError):
    default_message = "Forbidden"
    default_status = 403
    default_code = "forbidden"


class NotFoundError(AppError):
    default_message = "Not found"
    default_status = 404
    default_code = "not_found"


class ConflictError(AppError):
    default_message = "Conflict"
    default_status = 409
    default_code = "conflict"


class ServiceError(AppError):
    default_message = "Service error"
    default_status = 400
    default_code = "service_error"


def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "status": "error",
            "message": "Bad request",
            "code": "bad_request"
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({
            "status": "error",
            "message": "Unauthorized",
            "code": "unauthorized"
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        return jsonify({
            "status": "error",
            "message": "Forbidden",
            "code": "forbidden"
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "status": "error",
            "message": "Not found",
            "code": "not_found"
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "code": "internal_error"
        }), 500
