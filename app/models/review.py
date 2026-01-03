"""
Product Review/Testimonial model.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        db.Index("ix_reviews_product_id", "product_id"),
        db.Index("ix_reviews_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Product being reviewed
    product_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=True
    )

    # Reviewer information
    user_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Guest reviewer info (if not logged in)
    guest_name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    # Review content
    rating: Mapped[int] = mapped_column(db.Integer, nullable=False)  # 1-5 stars
    title: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    comment: Mapped[str] = mapped_column(db.Text, nullable=False)

    # Verification and moderation
    is_verified_purchase: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )
    is_approved: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )

    # Helpfulness tracking
    helpful_count: Mapped[int] = mapped_column(
        db.Integer, nullable=False, default=0, server_default="0"
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
    product = relationship("Product", foreign_keys=[product_id], lazy="select")
    user = relationship("User", foreign_keys=[user_id], lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Review id={self.id} product_id={self.product_id} rating={self.rating}>"
        )

    def to_dict(
        self, include_product: bool = False, include_user: bool = False
    ) -> Dict[str, Any]:
        """Serialize review to dictionary."""
        data = {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "guest_name": self.guest_name,
            "guest_email": self.guest_email,
            "rating": self.rating,
            "title": self.title,
            "comment": self.comment,
            "is_verified_purchase": self.is_verified_purchase,
            "is_approved": self.is_approved,
            "helpful_count": self.helpful_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_product and self.product:
            data["product"] = {"id": self.product.id, "name": self.product.name}

        if include_user and self.user:
            data["user"] = {"id": self.user.id, "username": self.user.username}

        return data
