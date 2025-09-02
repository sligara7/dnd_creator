"""Base database model."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base database model."""

    # Common columns for all models
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
