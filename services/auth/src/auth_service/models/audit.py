"""Audit log model for security event tracking."""

from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
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


class AuditEventType(str, Enum):
    """Audit event type enumeration."""
    # Authentication Events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGED = "password_changed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_FAILED = "mfa_failed"
    
    # Authorization Events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Session Events
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    SESSION_REVOKED = "session_revoked"
    SESSION_REFRESH = "session_refresh"
    
    # API Key Events
    API_KEY_CREATED = "api_key_created"
    API_KEY_USED = "api_key_used"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_EXPIRED = "api_key_expired"
    
    # User Management Events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOCKED = "user_locked"
    USER_UNLOCKED = "user_unlocked"
    USER_VERIFIED = "user_verified"
    
    # Security Events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_DETECTED = "brute_force_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    SECURITY_VIOLATION = "security_violation"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(BaseModel):
    """Audit log for security event tracking."""
    
    __tablename__ = "audit_logs"
    
    # Event Information
    event_type = Column(
        SQLEnum(AuditEventType),
        nullable=False,
        index=True
    )
    severity = Column(
        SQLEnum(AuditSeverity),
        default=AuditSeverity.INFO,
        nullable=False,
        index=True
    )
    
    # User Association (nullable for anonymous events)
    user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    
    # Target Information (if event affects another user or resource)
    target_user_id = Column(PGUUID(as_uuid=True), nullable=True)
    target_resource = Column(String(255), nullable=True)
    target_resource_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Event Details
    action = Column(String(255), nullable=False)
    result = Column(String(50), nullable=True)  # success, failure, etc.
    reason = Column(Text, nullable=True)
    
    # Client Information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(PGUUID(as_uuid=True), nullable=True)
    api_key_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Request Information
    request_id = Column(String(255), nullable=True, index=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(Text, nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)  # Sanitized
    
    # Response Information
    response_status = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Additional Context
    metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Service Information
    service_name = Column(String(100), nullable=True)
    service_version = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_audit_event_type_created", "event_type", "created_at"),
        Index("idx_audit_user_created", "user_id", "created_at"),
        Index("idx_audit_severity_created", "severity", "created_at"),
        Index("idx_audit_ip_created", "ip_address", "created_at"),
    )
    
    @classmethod
    def log_auth_event(
        cls,
        event_type: AuditEventType,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        reason: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Create an authentication event log entry."""
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING
        return cls(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            action=event_type.value,
            result="success" if success else "failure",
            reason=reason,
            ip_address=ip_address,
            metadata=metadata,
        )
    
    @classmethod
    def log_security_event(
        cls,
        event_type: AuditEventType,
        severity: AuditSeverity,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        reason: str = None,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Create a security event log entry."""
        return cls(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            action=event_type.value,
            reason=reason,
            ip_address=ip_address,
            metadata=metadata,
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<AuditLog(id={self.id}, event={self.event_type}, user_id={self.user_id}, severity={self.severity})>"
