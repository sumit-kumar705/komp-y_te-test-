"""
User model (SQLAlchemy 2.0 style).
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_email", "email"),
        db.Index("ix_users_username", "username"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(
        db.String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    # Contact information
    phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)

    # Address fields
    address_line1: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(db.String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # User role (customer, admin)
    role: Mapped[str] = mapped_column(
        db.String(50), nullable=False, default="customer", server_default="customer"
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=True, server_default="1"
    )

    # Email verification
    is_email_verified: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )

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
    cart_items: Mapped[List["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"

    # Admin property
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"

    # Password helpers
    @property
    def password(self) -> None:
        raise AttributeError("Password is write-only. Use set_password() to set it.")

    @password.setter
    def password(self, raw_password: str) -> None:
        if not raw_password:
            raise ValueError("Password must not be empty.")
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def set_password(self, raw_password: str) -> None:
        self.password = raw_password

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(
        self, include_relationships: bool = False, exclude: Optional[set] = None
    ) -> Dict[str, Any]:
        exclude = set(exclude or set())
        exclude.add("password_hash")

        data: Dict[str, Any] = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "role": self.role,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "is_email_verified": self.is_email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relationships:
            if hasattr(self, "cart_items"):
                data["cart_items"] = [
                    ci.to_dict(include_relations=False)
                    for ci in getattr(self, "cart_items", [])
                ]

        return data
