"""Lifecycle policy models for storage service."""

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


class PolicyType(str, Enum):
    """Policy type enumeration."""

    RETENTION = "retention"
    ARCHIVAL = "archival"
    DELETION = "deletion"
    BACKUP = "backup"
    TRANSITION = "transition"


class PolicyStatus(str, Enum):
    """Policy status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"


class LifecyclePolicy(Base):
    """Lifecycle policy for asset management."""

    __tablename__ = "lifecycle_policies"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Policy information
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    type = Column(SQLEnum(PolicyType), nullable=False)
    status = Column(SQLEnum(PolicyStatus), nullable=False, default=PolicyStatus.INACTIVE)
    
    # Policy configuration
    enabled = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0)  # Higher priority policies execute first
    
    # Target criteria (JSON for flexibility)
    target_criteria = Column(JSON, nullable=False, default=dict)
    # Example: {
    #     "asset_types": ["image", "document"],
    #     "services": ["character_service"],
    #     "tags": ["temporary"],
    #     "age_days": 90,
    #     "size_bytes_min": 1000000
    # }
    
    # Action configuration
    action_config = Column(JSON, nullable=False, default=dict)
    # Example: {
    #     "action": "move_to_cold",
    #     "parameters": {"storage_class": "cold"}
    # }
    
    # Execution tracking
    last_executed_at = Column(DateTime, nullable=True)
    next_execution_at = Column(DateTime, nullable=True)
    execution_count = Column(Integer, nullable=False, default=0)
    
    # Schedule (cron expression)
    schedule = Column(String(100), nullable=True)  # e.g., "0 0 * * *" for daily
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rules = relationship("PolicyRule", back_populates="policy", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_policy_status_type", "status", "type"),
        Index("idx_policy_enabled_priority", "enabled", "priority"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<LifecyclePolicy(id={self.id}, name={self.name}, type={self.type})>"


class PolicyRule(Base):
    """Individual rules within a lifecycle policy."""

    __tablename__ = "policy_rules"

    # Primary key
    id = Column(PGUUID, primary_key=True, default=uuid4)
    
    # Foreign key
    policy_id = Column(PGUUID, ForeignKey("lifecycle_policies.id", ondelete="CASCADE"), nullable=False)
    
    # Rule information
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    order = Column(Integer, nullable=False, default=0)  # Execution order within policy
    
    # Condition
    condition_type = Column(String(50), nullable=False)  # e.g., "age", "size", "tag"
    condition_config = Column(JSON, nullable=False, default=dict)
    
    # Action
    action_type = Column(String(50), nullable=False)  # e.g., "archive", "delete", "transition"
    action_config = Column(JSON, nullable=False, default=dict)
    
    # Status
    enabled = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    policy = relationship("LifecyclePolicy", back_populates="rules")

    # Indexes
    __table_args__ = (
        Index("idx_rule_policy_order", "policy_id", "order"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PolicyRule(id={self.id}, name={self.name}, order={self.order})>"
