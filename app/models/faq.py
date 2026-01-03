"""
FAQ (Frequently Asked Questions) model.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class FAQ(db.Model):
    __tablename__ = "faqs"
    __table_args__ = (db.Index("ix_faqs_category", "category"),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Question and Answer
    question: Mapped[str] = mapped_column(db.String(500), nullable=False)
    answer: Mapped[str] = mapped_column(db.Text, nullable=False)

    # Category for grouping FAQs
    category: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    # Order/priority for display
    display_order: Mapped[int] = mapped_column(
        db.Integer, nullable=False, default=0, server_default="0"
    )

    # Active status
    is_active: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=True, server_default="1"
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

    def __repr__(self) -> str:
        return f"<FAQ id={self.id} question={self.question[:50]}...>"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize FAQ to dictionary."""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "display_order": self.display_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
