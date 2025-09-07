"""API Key model for API authentication."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from auth_service.models.base import BaseModel


class ApiKeyStatus(str, Enum):
    """API Key status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class ApiKey(BaseModel):
    """API Key model for programmatic access."""
    
    __tablename__ = "api_keys"
    
    # Key Information
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(10), nullable=False)  # For display purposes
    
    # Status and Validity
    status = Column(
        SQLEnum(ApiKeyStatus),
        default=ApiKeyStatus.ACTIVE,
        nullable=False,
        index=True
    )
    expires_at = Column(DateTime, nullable=True)
    
    # User Association
    user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Usage Tracking
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(String(45), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Rate Limiting
    rate_limit = Column(Integer, nullable=True)  # Requests per minute
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset_at = Column(DateTime, nullable=True)
    
    # Permissions and Scopes
    scopes = Column(JSON, nullable=True)  # List of allowed scopes
    allowed_ips = Column(JSON, nullable=True)  # IP whitelist
    allowed_origins = Column(JSON, nullable=True)  # Origin whitelist
    
    # Security
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(Text, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index("idx_api_key_user_status", "user_id", "status"),
        Index("idx_api_key_expires", "expires_at"),
    )
    
    def is_valid(self) -> bool:
        """Check if API key is valid."""
        now = datetime.utcnow()
        if self.expires_at and self.expires_at <= now:
            return False
        return (
            self.status == ApiKeyStatus.ACTIVE
            and not self.is_deleted
        )
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit allows request."""
        if not self.rate_limit:
            return True
        
        now = datetime.utcnow()
        if not self.rate_limit_reset_at or self.rate_limit_reset_at <= now:
            # Reset rate limit window
            self.rate_limit_remaining = self.rate_limit
            self.rate_limit_reset_at = now + timedelta(minutes=1)
        
        return self.rate_limit_remaining > 0
    
    def decrement_rate_limit(self) -> None:
        """Decrement rate limit counter."""
        if self.rate_limit and self.rate_limit_remaining:
            self.rate_limit_remaining -= 1
    
    def check_ip(self, ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if not self.allowed_ips:
            return True
        return ip_address in self.allowed_ips
    
    def check_origin(self, origin: str) -> bool:
        """Check if origin is allowed."""
        if not self.allowed_origins:
            return True
        return origin in self.allowed_origins
    
    def has_scope(self, scope: str) -> bool:
        """Check if API key has a specific scope."""
        if not self.scopes:
            return True  # No scopes means all access
        return scope in self.scopes
    
    def record_usage(self, ip_address: Optional[str] = None) -> None:
        """Record API key usage."""
        self.last_used_at = datetime.utcnow()
        self.last_used_ip = ip_address
        self.usage_count += 1
        if self.rate_limit:
            self.decrement_rate_limit()
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """Revoke the API key."""
        self.status = ApiKeyStatus.REVOKED
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason
        self.updated_at = datetime.utcnow()
    
    def suspend(self) -> None:
        """Suspend the API key temporarily."""
        self.status = ApiKeyStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
    
    def reactivate(self) -> None:
        """Reactivate a suspended API key."""
        if self.status == ApiKeyStatus.SUSPENDED:
            self.status = ApiKeyStatus.ACTIVE
            self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ApiKey(id={self.id}, name={self.name}, user_id={self.user_id}, status={self.status})>"
