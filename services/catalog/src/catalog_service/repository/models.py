from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from catalog_service.domain.models import ContentSource, ContentType


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Association table for content-theme relationships
content_themes = Table(
    "content_themes",
    Base.metadata,
    Column("content_id", PGUUID, ForeignKey("content.id"), primary_key=True),
    Column("theme_id", PGUUID, ForeignKey("themes.id"), primary_key=True),
)


class Content(Base):
    """Base model for all content items"""
    __tablename__ = "content"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(Enum(ContentType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(Enum(ContentSource), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    properties: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    
    # Metadata
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Theme data
    themes: Mapped[List["Theme"]] = relationship(
        "Theme", secondary=content_themes, back_populates="content"
    )
    theme_adaptations: Mapped[Dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    
    # Validation data
    balance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    consistency_check: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_validated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Theme(Base):
    """Theme definition model"""
    __tablename__ = "themes"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    compatible_types: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    modifiers: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Relationships
    content: Mapped[List["Content"]] = relationship(
        "Content", secondary=content_themes, back_populates="themes"
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
