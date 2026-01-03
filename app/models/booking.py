"""
Booking/Consultation model.

For Komplyte's consultation feature.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.extensions import db


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        db.Index("ix_bookings_user_id", "user_id"),
        db.Index("ix_bookings_appointment_date", "appointment_date"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # User information (can be guest or registered user)
    user_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Guest booking information
    guest_name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)

    # Appointment details
    appointment_date: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(
        db.Integer, nullable=False, default=30
    )

    # Consultation type
    consultation_type: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # Notes and requirements
    notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    # Status
    status: Mapped[BookingStatus] = mapped_column(
        db.Enum(BookingStatus, name="booking_status", native_enum=False),
        nullable=False,
        server_default=BookingStatus.PENDING.value,
    )

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

    # Relationships
    user = relationship("User", foreign_keys=[user_id], lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} date={self.appointment_date} status={self.status}>"
        )

    def to_dict(self, include_user: bool = False) -> Dict[str, Any]:
        """Serialize booking to dictionary."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "guest_name": self.guest_name,
            "guest_email": self.guest_email,
            "guest_phone": self.guest_phone,
            "appointment_date": (
                self.appointment_date.isoformat() if self.appointment_date else None
            ),
            "duration_minutes": self.duration_minutes,
            "consultation_type": self.consultation_type,
            "notes": self.notes,
            "admin_notes": self.admin_notes,
            "status": (
                self.status.value
                if isinstance(self.status, enum.Enum)
                else str(self.status)
            ),
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
