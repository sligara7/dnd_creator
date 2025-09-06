"""Base model for database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from image_service.core.utils import now_utc


class Base(DeclarativeBase):
    """Base class for all database models."""


class TimestampMixin:
    """Mixin to add timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
        onupdate=now_utc
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BaseModel(Base, TimestampMixin):
    """Base model with ID and timestamps."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name."""
        return cls.__name__.lower()
