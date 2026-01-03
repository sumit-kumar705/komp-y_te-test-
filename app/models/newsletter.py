"""
Newsletter subscription model.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Newsletter(db.Model):
    __tablename__ = "newsletters"
    __table_args__ = (db.Index("ix_newsletters_email", "email"),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Subscriber information
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)

    # Subscription status
    is_subscribed: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=True, server_default="1"
    )

    # Verification
    is_verified: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )
    verification_token: Mapped[str | None] = mapped_column(
        db.String(255), nullable=True
    )

    # Timestamps
    subscribed_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    unsubscribed_at: Mapped[datetime | None] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Newsletter id={self.id} email={self.email!r}>"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize newsletter subscription to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_subscribed": self.is_subscribed,
            "is_verified": self.is_verified,
            "subscribed_at": (
                self.subscribed_at.isoformat() if self.subscribed_at else None
            ),
            "unsubscribed_at": (
                self.unsubscribed_at.isoformat() if self.unsubscribed_at else None
            ),
        }
