"""
Team Member model for 'Meet The Team' section.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class TeamMember(db.Model):
    __tablename__ = "team_members"
    __table_args__ = (db.Index("ix_team_members_display_order", "display_order"),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Member information
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    position: Mapped[str] = mapped_column(db.String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    # Contact and social media
    email: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(db.String(20), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    # Profile photo
    photo_url: Mapped[str | None] = mapped_column(db.String(500), nullable=True)

    # Display order
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
        return (
            f"<TeamMember id={self.id} name={self.name!r} position={self.position!r}>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize team member to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "bio": self.bio,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": self.linkedin_url,
            "twitter_url": self.twitter_url,
            "photo_url": self.photo_url,
            "display_order": self.display_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
