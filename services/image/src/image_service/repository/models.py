from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from image_service.domain.models import ImageType, ImageSubtype, OverlayType


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


class Image(Base):
    """Database model for images"""
    __tablename__ = "images"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(Enum(ImageType))
    subtype: Mapped[str] = mapped_column(Enum(ImageSubtype))
    
    # Content information
    content: Mapped[dict] = mapped_column(JSONB)
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB)
    references: Mapped[List[dict]] = mapped_column(JSONB, default=list)
    
    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    overlays: Mapped[List["Overlay"]] = relationship(
        "Overlay",
        back_populates="image",
        cascade="all, delete",
    )


class Overlay(Base):
    """Database model for image overlays"""
    __tablename__ = "overlays"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    image_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(Enum(OverlayType))
    elements: Mapped[List[dict]] = mapped_column(JSONB)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    image: Mapped[Image] = relationship("Image", back_populates="overlays")
