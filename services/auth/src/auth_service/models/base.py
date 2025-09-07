"""Base model for Auth Service database entities."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all entities."""
    
    __abstract__ = True
    
    # UUID Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Soft Delete Fields
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamp Fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def soft_delete(self) -> None:
        """Mark entity as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft-deleted entity."""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
