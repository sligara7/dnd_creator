"""Asset models for storage service."""

from datetime import datetime
from typing import Optional, Dict, Any, List
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


class AssetType(str, Enum):
    """Asset type enumeration."""

    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"
    ARCHIVE = "archive"


class AssetStatus(str, Enum):
    """Asset status enumeration."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    ERROR = "error"


class StorageClass(str, Enum):
    """Storage class enumeration."""

    HOT = "hot"  # Frequently accessed
    WARM = "warm"  # Infrequently accessed
    COLD = "cold"  # Archive storage


class Asset(Base):
    """Asset model for binary storage."""

    __tablename__ = "assets"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)

    # Asset information
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(AssetType), nullable=False, default=AssetType.BINARY)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)  # Size in bytes
    checksum = Column(String(64), nullable=False)  # SHA256 hash

    # Storage information
    storage_path = Column(String(500), nullable=False)
    storage_class = Column(SQLEnum(StorageClass), nullable=False, default=StorageClass.HOT)
    bucket_name = Column(String(255), nullable=False)
    
    # Status and lifecycle
    status = Column(SQLEnum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE)
    retention_until = Column(DateTime, nullable=True)
    archive_after = Column(DateTime, nullable=True)
    
    # Ownership and access
    service_name = Column(String(100), nullable=False)  # Which service owns this asset
    owner_id = Column(PGUUID, nullable=True)  # User or entity that owns the asset
    
    # Metadata
    metadata = Column(JSON, nullable=False, default=dict)
    tags = Column(JSON, nullable=False, default=list)
    
    # Versioning
    version_count = Column(Integer, nullable=False, default=1)
    current_version_id = Column(PGUUID, nullable=True)
    
    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = Column(DateTime, nullable=True)

    # Relationships
    versions = relationship("AssetVersion", back_populates="asset", cascade="all, delete-orphan")
    metadata_entries = relationship("AssetMetadata", back_populates="asset", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_asset_service_owner", "service_name", "owner_id"),
        Index("idx_asset_status_class", "status", "storage_class"),
        Index("idx_asset_type_status", "type", "status"),
        Index("idx_asset_checksum", "checksum"),
        Index("idx_asset_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Asset(id={self.id}, name={self.name}, type={self.type}, size={self.size})>"


class AssetMetadata(Base):
    """Extended metadata for assets."""

    __tablename__ = "asset_metadata"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Foreign key
    asset_id = Column(PGUUID, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata
    key = Column(String(255), nullable=False)
    value = Column(String(1000), nullable=False)
    type = Column(String(50), nullable=False, default="string")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="metadata_entries")

    # Indexes
    __table_args__ = (
        Index("idx_metadata_asset_key", "asset_id", "key", unique=True),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AssetMetadata(id={self.id}, key={self.key}, value={self.value})>"
