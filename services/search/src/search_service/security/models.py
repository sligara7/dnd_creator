from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Role(str, Enum):
    """User roles"""
    ADMIN = "admin"
    WRITER = "writer"
    READER = "reader"


class Permission(str, Enum):
    """User permissions"""
    SEARCH_READ = "search:read"
    SEARCH_WRITE = "search:write"
    INDEX_READ = "index:read"
    INDEX_WRITE = "index:write"
    INDEX_DELETE = "index:delete"


class AccessLevel(str, Enum):
    """Document access levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class SecurityConfig(BaseModel):
    """Security configuration"""
    allow_public_access: bool = False
    default_access_level: AccessLevel = AccessLevel.PRIVATE
    encrypted_fields: List[str] = []
    role_permissions: Dict[Role, List[Permission]] = Field(default_factory=dict)
    access_level_roles: Dict[AccessLevel, List[Role]] = Field(default_factory=dict)


class SecurityContext(BaseModel):
    """Security context for requests"""
    user_id: Optional[UUID] = None
    roles: List[Role] = []
    permissions: List[Permission] = []
    access_levels: List[AccessLevel] = []
    token_expires_at: Optional[datetime] = None
