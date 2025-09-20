"""API models for auth service."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    """Base user model."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="User's username"
    )
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """User creation model."""

    password: constr(min_length=12) = Field(
        ...,
        description="User's password"
    )


class UserUpdate(BaseModel):
    """User update model."""

    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=12)] = None
    mfa_enabled: Optional[bool] = None
    mfa_secret: Optional[str] = None
    failed_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None
    status: Optional[str] = None


class UserResponse(UserBase):
    """User response model."""

    id: UUID
    mfa_enabled: bool
    last_login: Optional[datetime]
    failed_attempts: int
    locked_until: Optional[datetime]
    status: str
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RoleBase(BaseModel):
    """Base role model."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Role name"
    )
    description: Optional[str] = Field(
        None,
        max_length=256,
        description="Role description"
    )


class RoleCreate(RoleBase):
    """Role creation model."""

    is_system_role: Optional[bool] = False


class RoleUpdate(BaseModel):
    """Role update model."""

    description: Optional[str] = None


class RoleResponse(RoleBase):
    """Role response model."""

    id: UUID
    is_system_role: bool
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class SessionBase(BaseModel):
    """Base session model."""

    user_id: UUID = Field(..., description="User ID")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = "Bearer"
    expires_at: datetime = Field(..., description="Session expiration")
    client_info: Dict = Field(default_factory=dict)


class SessionCreate(SessionBase):
    """Session creation model."""


class SessionUpdate(BaseModel):
    """Session update model."""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    revoked_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class SessionResponse(SessionBase):
    """Session response model."""

    id: UUID
    is_active: bool
    revoked_at: Optional[datetime]
    last_activity: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ApiKeyBase(BaseModel):
    """Base API key model."""

    user_id: UUID = Field(..., description="User ID")
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="API key name"
    )
    description: Optional[str] = Field(
        None,
        max_length=256,
        description="API key description"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="API key expiration"
    )


class ApiKeyCreate(ApiKeyBase):
    """API key creation model."""

    key_hash: str = Field(..., description="Hashed API key")


class ApiKeyUpdate(BaseModel):
    """API key update model."""

    name: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    last_used: Optional[datetime] = None


class ApiKeyResponse(ApiKeyBase):
    """API key response model."""

    id: UUID
    key_hash: str
    last_used: Optional[datetime]
    is_active: bool
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AuditLogBase(BaseModel):
    """Base audit log model."""

    user_id: Optional[UUID] = Field(None, description="User ID")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[UUID] = Field(None, description="Resource ID")
    old_data: Optional[Dict] = Field(None, description="Previous resource state")
    new_data: Optional[Dict] = Field(None, description="New resource state")
    client_info: Dict = Field(default_factory=dict)
    ip_address: Optional[str] = Field(None, description="IP address")


class AuditLogCreate(AuditLogBase):
    """Audit log creation model."""

    success: bool = Field(..., description="Operation success")
    failure_reason: Optional[str] = Field(None, description="Failure reason")