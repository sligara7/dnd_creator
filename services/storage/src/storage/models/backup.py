"""Backup models for storage service."""

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
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from storage.core.database import Base


class BackupType(str, Enum):
    """Backup type enumeration."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(str, Enum):
    """Backup status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"
    VERIFIED = "verified"


class BackupJob(Base):
    """Backup job tracking."""

    __tablename__ = "backup_jobs"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Backup information
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(SQLEnum(BackupType), nullable=False, default=BackupType.FULL)
    status = Column(SQLEnum(BackupStatus), nullable=False, default=BackupStatus.PENDING)
    
    # Scope
    service_name = Column(String(100), nullable=True)  # Specific service or null for all
    asset_types = Column(JSON, nullable=False, default=list)  # Which asset types to backup
    tags = Column(JSON, nullable=False, default=list)  # Assets with these tags
    
    # Storage location
    backup_location = Column(String(500), nullable=False)
    backup_bucket = Column(String(255), nullable=False)
    
    # Statistics
    total_assets = Column(Integer, nullable=False, default=0)
    processed_assets = Column(Integer, nullable=False, default=0)
    failed_assets = Column(Integer, nullable=False, default=0)
    total_size_bytes = Column(Integer, nullable=False, default=0)
    
    # Error tracking
    error_message = Column(String(1000), nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Retention
    retention_days = Column(Integer, nullable=False, default=30)
    expires_at = Column(DateTime, nullable=True)
    
    # Verification
    is_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)
    verification_checksum = Column(String(64), nullable=True)
    
    # Parent backup (for incremental/differential)
    parent_backup_id = Column(PGUUID, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_backup_status_type", "status", "type"),
        Index("idx_backup_service", "service_name"),
        Index("idx_backup_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<BackupJob(id={self.id}, name={self.name}, status={self.status})>"
