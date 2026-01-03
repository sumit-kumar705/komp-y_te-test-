"""
Admin routes for dashboard and management.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required

from app.utils.decorators import admin_required
from app.utils.response import success_response, error_response
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.booking import Booking
from app.models.blog import Blog
from app.models.team import TeamMember
from app.models.faq import FAQ
from app.models.newsletter import Newsletter
from app.models.contact import Contact


admin_bp = Blueprint("admin", __name__)


# ============================================
# DASHBOARD
# ============================================

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def get_dashboard_stats():
    """Get admin dashboard statistics."""
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Basic counts
    total_users = User.query.filter(User.role != "admin").count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    
    # Revenue (completed orders)
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED])
    ).scalar() or 0
    
    # This month's orders
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    monthly_orders = Order.query.filter(Order.created_at >= month_start).count()
    monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= month_start,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED])
    ).scalar() or 0
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return success_response({
        "users": total_users,
        "products": total_products,
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "this_month": monthly_orders,
        },
        "revenue": {
            "total": float(total_revenue),
            "this_month": float(monthly_revenue),
        },
        "recent_orders": [o.to_dict() for o in recent_orders],
    })


# ============================================
# ORDERS MANAGEMENT
# ============================================

@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_all_orders():
    """Get all orders with pagination."""
    from app.services.order_services import get_all_orders
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    
    result = get_all_orders(status=status, page=page, per_page=per_page)
    return success_response(result)


@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@admin_required
def get_admin_order(order_id):
    """Get order details (admin)."""
    order = db.session.get(Order, order_id)
    if not order:
        return error_response("Order not found", 404)
    return success_response(order.to_dict(include_items=True, include_user=True))


@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status_admin(order_id):
    """Update order status."""
    from app.services.order_services import update_order_status
    
    data = request.get_json() or {}
    new_status = data.get("status")
    tracking_info = {
        "tracking_number": data.get("tracking_number"),
        "carrier": data.get("carrier"),
    }
    
    if not new_status:
        return error_response("Status is required", 400)
    
    try:
        order = update_order_status(order_id, new_status, tracking_info)
        return success_response(order)
    except Exception as e:
        return error_response(str(e), 400)


# ============================================
# BOOKINGS MANAGEMENT
# ============================================

@admin_bp.route("/bookings", methods=["GET"])
@admin_required
def list_all_bookings():
    """Get all consultation bookings."""
    from app.services.booking_services import get_all_bookings
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    
    result = get_all_bookings(status=status, page=page, per_page=per_page)
    return success_response(result)


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["PUT"])
@admin_required
def update_booking_status_admin(booking_id):
    """Update booking status."""
    from app.services.booking_services import update_booking_status
    
    data = request.get_json() or {}
    new_status = data.get("status")
    admin_notes = data.get("admin_notes")
    
    if not new_status:
        return error_response("Status is required", 400)
    
    try:
        booking = update_booking_status(booking_id, new_status, admin_notes)
        return success_response(booking)
    except Exception as e:
        return error_response(str(e), 400)


# ============================================
# USERS MANAGEMENT
# ============================================

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Get all users."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    pagination = User.query.filter(User.role != "admin").order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return success_response({
        "users": [u.to_dict() for u in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    })


# ============================================
# BLOGS MANAGEMENT
# ============================================

@admin_bp.route("/blogs", methods=["GET"])
@admin_required
def list_blogs_admin():
    """Get all blogs."""
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return success_response([b.to_dict() if hasattr(b, 'to_dict') else {"id": b.id} for b in blogs])


@admin_bp.route("/blogs", methods=["POST"])
@admin_required
def create_blog():
    """Create a blog post."""
    data = request.get_json() or {}
    
    blog = Blog(
        title=data.get("title"),
        content=data.get("content"),
        author=data.get("author"),
        image_url=data.get("image_url"),
    )
    db.session.add(blog)
    
    try:
        db.session.commit()
        return success_response(blog.to_dict() if hasattr(blog, 'to_dict') else {"id": blog.id}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)


@admin_bp.route("/blogs/<int:blog_id>", methods=["PUT"])
@admin_required
def update_blog(blog_id):
    """Update a blog post."""
    blog = db.session.get(Blog, blog_id)
    if not blog:
        return error_response("Blog not found", 404)
    
    data = request.get_json() or {}
    for field in ["title", "content", "author", "image_url"]:
        if field in data:
            setattr(blog, field, data[field])
    
    try:
        db.session.commit()
        return success_response(blog.to_dict() if hasattr(blog, 'to_dict') else {"id": blog.id})
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)


@admin_bp.route("/blogs/<int:blog_id>", methods=["DELETE"])
@admin_required
def delete_blog(blog_id):
    """Delete a blog post."""
    blog = db.session.get(Blog, blog_id)
    if not blog:
        return error_response("Blog not found", 404)
    
    db.session.delete(blog)
    db.session.commit()
    return success_response({"deleted": blog_id})


# ============================================
# TEAM MANAGEMENT
# ============================================

@admin_bp.route("/team", methods=["GET"])
@admin_required
def list_team_admin():
    """Get all team members."""
    members = TeamMember.query.all()
    return success_response([m.to_dict() if hasattr(m, 'to_dict') else {"id": m.id} for m in members])


@admin_bp.route("/team", methods=["POST"])
@admin_required
def create_team_member():
    """Create a team member."""
    data = request.get_json() or {}
    
    member = TeamMember(
        name=data.get("name"),
        role=data.get("role"),
        bio=data.get("bio"),
        image_url=data.get("image_url"),
    )
    db.session.add(member)
    
    try:
        db.session.commit()
        return success_response(member.to_dict() if hasattr(member, 'to_dict') else {"id": member.id}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)


# ============================================
# FAQ MANAGEMENT
# ============================================

@admin_bp.route("/faqs", methods=["GET"])
@admin_required
def list_faqs_admin():
    """Get all FAQs."""
    faqs = FAQ.query.all()
    return success_response([f.to_dict() if hasattr(f, 'to_dict') else {"id": f.id} for f in faqs])


@admin_bp.route("/faqs", methods=["POST"])
@admin_required
def create_faq():
    """Create a FAQ."""
    data = request.get_json() or {}
    
    faq = FAQ(
        question=data.get("question"),
        answer=data.get("answer"),
    )
    db.session.add(faq)
    
    try:
        db.session.commit()
        return success_response(faq.to_dict() if hasattr(faq, 'to_dict') else {"id": faq.id}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)


# ============================================
# NEWSLETTER SUBSCRIBERS
# ============================================

@admin_bp.route("/newsletter", methods=["GET"])
@admin_required
def list_newsletter_subscribers():
    """Get all newsletter subscribers."""
    subscribers = Newsletter.query.all()
    return success_response([s.to_dict() if hasattr(s, 'to_dict') else {"id": s.id, "email": getattr(s, 'email', None)} for s in subscribers])


# ============================================
# CONTACT INQUIRIES
# ============================================

@admin_bp.route("/contacts", methods=["GET"])
@admin_required
def list_contact_inquiries():
    """Get all contact inquiries."""
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return success_response([c.to_dict() if hasattr(c, 'to_dict') else {"id": c.id} for c in contacts])


# ============================================
# SITE SETTINGS
# ============================================

@admin_bp.route("/settings", methods=["GET"])
@admin_required
def get_site_settings():
    """Get current site settings."""
    return success_response({
        "shipping_free_threshold": current_app.config.get("SHIPPING_FREE_THRESHOLD", 2000),
        "shipping_charge": current_app.config.get("SHIPPING_CHARGE", 49),
        "consultation_free_minutes": current_app.config.get("CONSULTATION_FREE_MINUTES", 20),
        "consultation_paid_price": current_app.config.get("CONSULTATION_PAID_PRICE", 250),
        "admin_whatsapp": current_app.config.get("ADMIN_WHATSAPP", "918149550229"),
        "support_email": current_app.config.get("SUPPORT_EMAIL", "support@komplyte.com"),
    })
