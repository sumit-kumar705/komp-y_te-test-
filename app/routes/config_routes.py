"""
Config routes for public site information.
"""

from flask import Blueprint, current_app

from app.utils.response import success_response

config_bp = Blueprint("config", __name__)


@config_bp.route("/shipping", methods=["GET"])
def get_shipping_info():
    """Get shipping charges info (public)."""
    threshold = current_app.config.get("SHIPPING_FREE_THRESHOLD", 2000)
    charge = current_app.config.get("SHIPPING_CHARGE", 49)
    
    return success_response({
        "free_shipping_threshold": threshold,
        "shipping_charge": charge,
        "message": f"Free shipping on orders above ₹{int(threshold)}",
    })


@config_bp.route("/refund", methods=["GET"])
def get_refund_info():
    """Get return/refund info with WhatsApp contact (public)."""
    whatsapp = current_app.config.get("ADMIN_WHATSAPP", "918149550229")
    
    return success_response({
        "whatsapp_number": whatsapp,
        "whatsapp_link": f"https://wa.me/{whatsapp}",
        "return_period_days": 15,
        "policy": "For returns and refunds, please contact us on WhatsApp. Returns accepted within 15 days of delivery.",
        "contact_email": current_app.config.get("SUPPORT_EMAIL", "support@komplyte.com"),
    })


@config_bp.route("/consultation", methods=["GET"])
def get_consultation_info():
    """Get consultation pricing info (public)."""
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
    })


@config_bp.route("/contact", methods=["GET"])
def get_contact_info():
    """Get company contact info (public)."""
    return success_response({
        "company_name": current_app.config.get("COMPANY_NAME", "KOMPLYTE"),
        "whatsapp": current_app.config.get("ADMIN_WHATSAPP", "918149550229"),
        "email": current_app.config.get("SUPPORT_EMAIL", "support@komplyte.com"),
        "address": "Bhoomi Allium Pimple Saudagar, Prassana Colony, Rahatani, Pimpri-Chinchwad, Pune, Maharashtra, India",
    })
