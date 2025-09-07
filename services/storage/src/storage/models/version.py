"""Version models for storage service."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    JSON,
    Enum as SQLEnum,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from storage.core.database import Base


class VersionStatus(str, Enum):
    """Version status enumeration."""

    CURRENT = "current"
    PREVIOUS = "previous"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AssetVersion(Base):
    """Version tracking for assets."""

    __tablename__ = "asset_versions"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Foreign key
    asset_id = Column(PGUUID, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    # Version information
    version_number = Column(Integer, nullable=False)
    version_tag = Column(String(100), nullable=True)  # Optional user-defined tag
    status = Column(SQLEnum(VersionStatus), nullable=False, default=VersionStatus.PREVIOUS)
    
    # Storage information
    storage_path = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)
    
    # Change information
    change_type = Column(String(50), nullable=True)  # e.g., "update", "resize", "format_change"
    change_description = Column(String(500), nullable=True)
    created_by = Column(PGUUID, nullable=True)  # User who created this version
    
    # Metadata
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # When this version should be deleted

    # Relationships
    asset = relationship("Asset", back_populates="versions")
    metadata_entries = relationship("VersionMetadata", back_populates="version", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_version_asset_number", "asset_id", "version_number", unique=True),
        Index("idx_version_status", "status"),
        Index("idx_version_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AssetVersion(id={self.id}, asset_id={self.asset_id}, version={self.version_number})>"


class VersionMetadata(Base):
    """Extended metadata for versions."""

    __tablename__ = "version_metadata"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Foreign key
    version_id = Column(PGUUID, ForeignKey("asset_versions.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata
    key = Column(String(255), nullable=False)
    value = Column(String(1000), nullable=False)
    type = Column(String(50), nullable=False, default="string")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    version = relationship("AssetVersion", back_populates="metadata_entries")

    # Indexes
    __table_args__ = (
        Index("idx_version_metadata_key", "version_id", "key", unique=True),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<VersionMetadata(id={self.id}, key={self.key}, value={self.value})>"
