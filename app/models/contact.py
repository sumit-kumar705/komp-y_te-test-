"""
Contact/Inquiry model for customer messages.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.extensions import db


class InquiryStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Contact(db.Model):
    __tablename__ = "contacts"
    __table_args__ = (
        db.Index("ix_contacts_email", "email"),
        db.Index("ix_contacts_status", "status"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Contact information
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)

    # Subject and message
    subject: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)

    # Status tracking
    status: Mapped[InquiryStatus] = mapped_column(
        db.Enum(InquiryStatus, name="inquiry_status", native_enum=False),
        nullable=False,
        server_default=InquiryStatus.NEW.value,
    )

    # Admin response
    admin_response: Mapped[str | None] = mapped_column(db.Text, nullable=True)

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

    def __repr__(self) -> str:
        return f"<Contact id={self.id} name={self.name!r} email={self.email!r}>"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contact to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject,
            "message": self.message,
            "status": (
                self.status.value
                if isinstance(self.status, enum.Enum)
                else str(self.status)
            ),
            "admin_response": self.admin_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
