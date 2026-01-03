"""
Booking model for consultation sessions.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
import enum

from sqlalchemy import func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class SessionType(str, enum.Enum):
    FREE_INTRO = "free_intro"  # First 20 mins free
    PAID = "paid"  # ₹250 for 20 mins


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        db.Index("ix_bookings_user_id", "user_id"),
        db.Index("ix_bookings_scheduled_at", "scheduled_at"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    
    user_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Customer info (for non-logged in or reference)
    customer_name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)
    
    # Session details
    session_type: Mapped[SessionType] = mapped_column(
        db.Enum(SessionType, name="session_type", native_enum=False),
        nullable=False,
        default=SessionType.FREE_INTRO,
    )
    
    session_duration_minutes: Mapped[int] = mapped_column(
        db.Integer, nullable=False, default=20
    )
    
    session_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    
    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )
    
    # Status
    status: Mapped[BookingStatus] = mapped_column(
        db.Enum(BookingStatus, name="booking_status", native_enum=False),
        nullable=False,
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value,
    )
    
    # Payment tracking (for paid sessions)
    is_paid: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    razorpay_payment_id: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    
    # Notes
    notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="bookings", lazy="select")

    def __repr__(self) -> str:
        return f"<Booking id={self.id} user_id={self.user_id} type={self.session_type} status={self.status}>"

    def to_dict(self, include_user: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "session_type": self.session_type.value if isinstance(self.session_type, enum.Enum) else str(self.session_type),
            "session_duration_minutes": self.session_duration_minutes,
            "session_price": float(self.session_price) if self.session_price else 0,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "status": self.status.value if isinstance(self.status, enum.Enum) else str(self.status),
            "is_paid": self.is_paid,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user and self.user:
            data["user"] = {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
            }
        
        return data
