"""
Blog model for content management system.

Features:
- Blog posts with title, content, author
- Featured image and SEO fields
- Published/draft status
- Tags for categorization
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Blog(db.Model):
    __tablename__ = "blogs"
    __table_args__ = (
        db.Index("ix_blogs_slug", "slug"),
        db.Index("ix_blogs_published_at", "published_at"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Blog content
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        db.String(255), nullable=False, unique=True, index=True
    )
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    # Media
    featured_image: Mapped[str | None] = mapped_column(db.String(500), nullable=True)

    # Author
    author_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_name: Mapped[str | None] = mapped_column(db.String(120), nullable=True)

    # SEO
    meta_description: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    meta_keywords: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    # Tags (comma-separated or JSON)
    tags: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    # Status
    is_published: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False, server_default="0"
    )

    # View count
    view_count: Mapped[int] = mapped_column(
        db.Integer, nullable=False, default=0, server_default="0"
    )

    # Timestamps
    published_at: Mapped[datetime | None] = mapped_column(
        db.DateTime(timezone=True), nullable=True
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
    author = relationship("User", foreign_keys=[author_id], lazy="select")

    def __repr__(self) -> str:
        return f"<Blog id={self.id} title={self.title!r}>"

    def to_dict(self, include_author: bool = False) -> Dict[str, Any]:
        """Serialize blog post to dictionary."""
        data = {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "excerpt": self.excerpt,
            "featured_image": self.featured_image,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "tags": self.tags.split(",") if self.tags else [],
            "is_published": self.is_published,
            "view_count": self.view_count,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_author and self.author:
            data["author"] = {
                "id": self.author.id,
                "username": self.author.username,
                "email": self.author.email,
            }

        return data
