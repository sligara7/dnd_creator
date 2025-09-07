"""Session model for user session management."""

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


class SessionType(str, Enum):
    """Session type enumeration."""
    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    SERVICE = "service"


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    IDLE = "idle"


class Session(BaseModel):
    """Session model for tracking user sessions."""
    
    __tablename__ = "sessions"
    
    # Session Identification
    token = Column(String(512), unique=True, nullable=False, index=True)
    refresh_token = Column(String(512), unique=True, nullable=True, index=True)
    
    # Session Type and Status
    session_type = Column(
        SQLEnum(SessionType),
        default=SessionType.WEB,
        nullable=False
    )
    status = Column(
        SQLEnum(SessionStatus),
        default=SessionStatus.ACTIVE,
        nullable=False,
        index=True
    )
    
    # User Association
    user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Session Timing
    expires_at = Column(DateTime, nullable=False)
    refresh_expires_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    idle_timeout = Column(Integer, default=1800)  # 30 minutes in seconds
    
    # Client Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_id = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    
    # Session Data
    data = Column(JSON, nullable=True)  # Additional session data
    
    # Security
    is_suspicious = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_user_status", "user_id", "status"),
        Index("idx_session_expires", "expires_at"),
        Index("idx_session_last_activity", "last_activity"),
    )
    
    def is_valid(self) -> bool:
        """Check if session is valid."""
        now = datetime.utcnow()
        return (
            self.status == SessionStatus.ACTIVE
            and self.expires_at > now
            and not self.is_deleted
            and not self.is_suspicious
        )
    
    def is_idle(self) -> bool:
        """Check if session is idle."""
        if self.idle_timeout is None:
            return False
        now = datetime.utcnow()
        idle_threshold = self.last_activity + timedelta(seconds=self.idle_timeout)
        return now > idle_threshold
    
    def can_refresh(self) -> bool:
        """Check if session can be refreshed."""
        if not self.refresh_token or not self.refresh_expires_at:
            return False
        now = datetime.utcnow()
        return (
            self.status == SessionStatus.ACTIVE
            and self.refresh_expires_at > now
            and not self.is_deleted
        )
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """Revoke the session."""
        self.status = SessionStatus.REVOKED
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason
        self.updated_at = datetime.utcnow()
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        if self.status == SessionStatus.IDLE:
            self.status = SessionStatus.ACTIVE
    
    def mark_idle(self) -> None:
        """Mark session as idle."""
        self.status = SessionStatus.IDLE
    
    def extend(self, duration_seconds: int = 3600) -> None:
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
        self.update_activity()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Session(id={self.id}, user_id={self.user_id}, type={self.session_type}, status={self.status})>"
