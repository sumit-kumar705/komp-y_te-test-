"""
Payment model (SQLAlchemy 2.0 style).
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
import enum

from sqlalchemy import func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class PaymentMethod(str, enum.Enum):
    RAZORPAY = "razorpay"
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(db.Model):
    __tablename__ = "payments"
    __table_args__ = (
        db.Index("ix_payments_order_id", "order_id"),
        db.Index("ix_payments_razorpay_order_id", "razorpay_order_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    
    order_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(db.String(10), nullable=False, default="INR")
    
    # Razorpay fields
    razorpay_order_id: Mapped[str | None] = mapped_column(db.String(100), nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    razorpay_signature: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    
    # Payment details
    method: Mapped[PaymentMethod] = mapped_column(
        db.Enum(PaymentMethod, name="payment_method", native_enum=False),
        nullable=False,
        default=PaymentMethod.RAZORPAY,
    )
    
    status: Mapped[PaymentStatus] = mapped_column(
        db.Enum(PaymentStatus, name="payment_status_enum", native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )
    
    # Error tracking
    error_code: Mapped[str | None] = mapped_column(db.String(50), nullable=True)
    error_description: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    
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
    paid_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True), nullable=True)

    # Relationship
    order: Mapped["Order"] = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} order_id={self.order_id} amount={self.amount} status={self.status}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": float(self.amount) if self.amount else 0,
            "currency": self.currency,
            "razorpay_order_id": self.razorpay_order_id,
            "razorpay_payment_id": self.razorpay_payment_id,
            "method": self.method.value if isinstance(self.method, enum.Enum) else str(self.method),
            "status": self.status.value if isinstance(self.status, enum.Enum) else str(self.status),
            "error_code": self.error_code,
            "error_description": self.error_description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }
