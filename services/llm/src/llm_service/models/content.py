from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_service.core.database import Base


class ContentBase(Base):
    """Base class for content models."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class TextContent(ContentBase):
    """Model for generated text content."""

    __tablename__ = "text_content"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("themes.id")
    )
    parent_content_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("text_content.id")
    )
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)

    theme = relationship("Theme", back_populates="text_content")
    parent_content = relationship("TextContent", remote_side=[id])
    child_content = relationship("TextContent", back_populates="parent_content")


class ImageContent(ContentBase):
    """Model for generated image content."""

    __tablename__ = "image_content"

    image_data: Mapped[str] = mapped_column(Text, nullable=False)  # Base64 encoded
    image_type: Mapped[str] = mapped_column(String(50), nullable=False)
    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("themes.id")
    )
    parent_image_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("image_content.id")
    )
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    thumbnail: Mapped[Optional[str]] = mapped_column(Text)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)

    theme = relationship("Theme", back_populates="image_content")
    parent_image = relationship("ImageContent", remote_side=[id])
    child_images = relationship("ImageContent", back_populates="parent_image")


class Theme(ContentBase):
    """Model for theme configuration."""

    __tablename__ = "themes"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    text_parameters: Mapped[dict] = mapped_column(JSONB)
    visual_parameters: Mapped[dict] = mapped_column(JSONB)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    text_content = relationship("TextContent", back_populates="theme")
    image_content = relationship("ImageContent", back_populates="theme")
