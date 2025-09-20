"""Image database models."""

from uuid import UUID
from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func

from ...db.base import Base


class Image(Base):
    """Image model.

    Represents a stored image along with its metadata, content, and overlays.
    """
    __tablename__ = "images"
    __table_args__ = {"schema": "image_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    type = Column(String(50), nullable=False)
    subtype = Column(String(50), nullable=False)
    content = Column(JSONB, nullable=False)
    metadata = Column(JSONB, nullable=False)
    overlays = Column(JSONB, nullable=False, server_default='[]')
    references = Column(JSONB, nullable=False, server_default='[]')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))


class Overlay(Base):
    """Overlay model.

    Represents an overlay that can be applied to an image, including its type
    and element configuration.
    """
    __tablename__ = "overlays"
    __table_args__ = {"schema": "image_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    image_id = Column(PGUUID(as_uuid=True), ForeignKey('image_db.images.id'))
    type = Column(String(50), nullable=False)
    elements = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))