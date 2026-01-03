"""
Order model with shipping charges and payment tracking.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import enum

from sqlalchemy import func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    INITIATED = "initiated"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (db.Index("ix_orders_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Order amounts
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    shipping_charges: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Order status
    status: Mapped[OrderStatus] = mapped_column(
        db.Enum(OrderStatus, name="order_status", native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )

    # Payment tracking
    payment_status: Mapped[PaymentStatus] = mapped_column(
        db.Enum(PaymentStatus, name="payment_status", native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )
    razorpay_order_id: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # Shipping information
    shipping_address_line1: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    shipping_address_line2: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    shipping_state: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(db.String(20), nullable=True)
    shipping_country: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # Contact information
    customer_name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)

    # Tracking information
    tracking_number: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    carrier: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # Order notes
    notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)

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
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="select")
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="select",
        cascade="all, delete-orphan",
    )
    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} user_id={self.user_id} total={self.total_amount} status={self.status}>"

    def update_status(self, new_status: OrderStatus) -> None:
        if isinstance(new_status, str):
            new_status = OrderStatus(new_status)
        self.status = new_status

    def to_dict(
        self, include_items: bool = False, include_user: bool = False
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "user_id": self.user_id,
            "subtotal": float(self.subtotal) if self.subtotal is not None else 0,
            "shipping_charges": float(self.shipping_charges) if self.shipping_charges is not None else 0,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0,
            "status": self.status.value if isinstance(self.status, enum.Enum) else str(self.status),
            "payment_status": self.payment_status.value if isinstance(self.payment_status, enum.Enum) else str(self.payment_status),
            "razorpay_order_id": self.razorpay_order_id,
            "razorpay_payment_id": self.razorpay_payment_id,
            "shipping_address_line1": self.shipping_address_line1,
            "shipping_address_line2": self.shipping_address_line2,
            "shipping_city": self.shipping_city,
            "shipping_state": self.shipping_state,
            "shipping_postal_code": self.shipping_postal_code,
            "shipping_country": self.shipping_country,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "tracking_number": self.tracking_number,
            "carrier": self.carrier,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }

        if include_items:
            items = getattr(self, "order_items", []) or []
            data["order_items"] = [
                item.to_dict(include_product=True) if hasattr(item, "to_dict") else {"id": getattr(item, "id", None)}
                for item in items
            ]

        if include_user and hasattr(self, "user") and self.user is not None:
            data["user"] = {
                "id": self.user.id,
                "username": getattr(self.user, "username", None),
                "email": getattr(self.user, "email", None),
            }

        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.Index("ix_order_items_order_id", "order_id"),
        db.Index("ix_order_items_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product_name: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    quantity: Mapped[int] = mapped_column(db.Integer, default=1, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product")

    def to_dict(self, include_product: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": float(self.price) if self.price is not None else 0.0,
            "line_total": float(self.price * self.quantity) if self.price else 0.0,
        }

        if include_product and self.product:
            data["product"] = self.product.to_dict()

        return data
