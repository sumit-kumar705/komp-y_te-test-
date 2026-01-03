"""
Booking services for consultation scheduling.
First 20 mins free, ₹250 for additional 20-min sessions.
"""

from datetime import datetime
from flask import current_app

from app.errors import ServiceError, ValidationError
from app.extensions import db
from app.models.booking import Booking, BookingStatus, SessionType
from app.models.user import User


def has_free_consultation(user_id: int) -> bool:
    """Check if user has already used their free consultation."""
    free_booking = Booking.query.filter_by(
        user_id=user_id,
        session_type=SessionType.FREE_INTRO
    ).filter(
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
    ).first()
    
    return free_booking is None


def calculate_session_price(user_id: int) -> dict:
    """Calculate session price for user's next consultation."""
    if has_free_consultation(user_id):
        return {
            "session_type": SessionType.FREE_INTRO.value,
            "price": 0,
            "duration_minutes": current_app.config.get("CONSULTATION_FREE_MINUTES", 20),
            "is_first_session": True,
        }
    else:
        return {
            "session_type": SessionType.PAID.value,
            "price": current_app.config.get("CONSULTATION_PAID_PRICE", 250),
            "duration_minutes": current_app.config.get("CONSULTATION_SESSION_MINUTES", 20),
            "is_first_session": False,
        }


def create_booking(user_id: int, booking_data: dict) -> dict:
    """Create a consultation booking."""
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("User not found")

    # Determine session type and price
    session_info = calculate_session_price(user_id)
    
    # For paid sessions without payment, mark as pending
    is_free = session_info["is_first_session"]
    
    booking = Booking(
        user_id=user_id,
        customer_name=booking_data.get("customer_name") or user.username,
        customer_email=booking_data.get("customer_email") or user.email,
        customer_phone=booking_data.get("customer_phone") or user.phone,
        session_type=SessionType.FREE_INTRO if is_free else SessionType.PAID,
        session_duration_minutes=session_info["duration_minutes"],
        session_price=session_info["price"],
        scheduled_at=booking_data.get("scheduled_at"),
        notes=booking_data.get("notes"),
        status=BookingStatus.CONFIRMED if is_free else BookingStatus.PENDING,
        is_paid=is_free,  # Free sessions count as "paid"
    )
    
    db.session.add(booking)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to create booking: {e}")

    return {
        **booking.to_dict(),
        "requires_payment": not is_free,
    }


def confirm_booking_payment(booking_id: int, razorpay_payment_id: str) -> dict:
    """Confirm booking after payment (for paid sessions)."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        raise ValidationError("Booking not found")

    booking.is_paid = True
    booking.razorpay_payment_id = razorpay_payment_id
    booking.status = BookingStatus.CONFIRMED
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to confirm booking: {e}")

    return booking.to_dict()


def get_user_bookings(user_id: int) -> list:
    """Get all bookings for a user."""
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return [b.to_dict() for b in bookings]


def get_all_bookings(status: str = None, page: int = 1, per_page: int = 20) -> dict:
    """Get all bookings (admin only)."""
    query = Booking.query.order_by(Booking.created_at.desc())
    
    if status:
        try:
            status_enum = BookingStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        "bookings": [b.to_dict(include_user=True) for b in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }


def update_booking_status(booking_id: int, new_status: str, admin_notes: str = None) -> dict:
    """Update booking status (admin only)."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        raise ValidationError("Booking not found")

    try:
        booking.status = BookingStatus(new_status)
    except ValueError:
        raise ValidationError(f"Invalid status: {new_status}")

    if admin_notes:
        booking.admin_notes = admin_notes

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Failed to update booking: {e}")

    return booking.to_dict()
