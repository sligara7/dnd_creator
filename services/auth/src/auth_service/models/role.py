"""Role and Permission models for authorization."""

from typing import List
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from auth_service.models.base import BaseModel, Base


# Association table for role-permission many-to-many relationship
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", PGUUID(as_uuid=True), ForeignKey("roles.id")),
    Column("permission_id", PGUUID(as_uuid=True), ForeignKey("permissions.id")),
)


class Permission(BaseModel):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permissions"
    
    # Permission Details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False, index=True)  # e.g., "character", "campaign"
    action = Column(String(50), nullable=False, index=True)  # e.g., "read", "write", "delete"
    scope = Column(String(50), nullable=True)  # e.g., "own", "all", "team"
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    # Indexes
    __table_args__ = (
        Index("idx_permission_resource_action", "resource", "action"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Permission(name={self.name}, resource={self.resource}, action={self.action})>"


class Role(BaseModel):
    """Role model for role-based access control."""
    
    __tablename__ = "roles"
    
    # Role Details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles can't be deleted
    priority = Column(Integer, default=0, nullable=False)  # Higher priority overrides lower
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission."""
        return any(perm.name == permission_name for perm in self.permissions)
    
    def get_permission_names(self) -> List[str]:
        """Get all permission names for this role."""
        return [perm.name for perm in self.permissions]
    
    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from this role."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Role(name={self.name}, is_system={self.is_system})>"


# Common system roles and permissions (for initial setup)
SYSTEM_ROLES = [
    {
        "name": "admin",
        "description": "System administrator with full access",
        "is_system": True,
        "priority": 100,
    },
    {
        "name": "user",
        "description": "Regular user with basic access",
        "is_system": True,
        "priority": 10,
    },
    {
        "name": "dm",
        "description": "Dungeon Master with campaign management access",
        "is_system": True,
        "priority": 50,
    },
    {
        "name": "player",
        "description": "Player with character management access",
        "is_system": True,
        "priority": 20,
    },
]

SYSTEM_PERMISSIONS = [
    # Character permissions
    {"name": "character.create", "resource": "character", "action": "create", "scope": "own"},
    {"name": "character.read", "resource": "character", "action": "read", "scope": "own"},
    {"name": "character.update", "resource": "character", "action": "update", "scope": "own"},
    {"name": "character.delete", "resource": "character", "action": "delete", "scope": "own"},
    {"name": "character.share", "resource": "character", "action": "share", "scope": "own"},
    
    # Campaign permissions
    {"name": "campaign.create", "resource": "campaign", "action": "create", "scope": "own"},
    {"name": "campaign.read", "resource": "campaign", "action": "read", "scope": "all"},
    {"name": "campaign.update", "resource": "campaign", "action": "update", "scope": "own"},
    {"name": "campaign.delete", "resource": "campaign", "action": "delete", "scope": "own"},
    {"name": "campaign.manage", "resource": "campaign", "action": "manage", "scope": "own"},
    
    # Image permissions
    {"name": "image.create", "resource": "image", "action": "create", "scope": "own"},
    {"name": "image.read", "resource": "image", "action": "read", "scope": "all"},
    {"name": "image.update", "resource": "image", "action": "update", "scope": "own"},
    {"name": "image.delete", "resource": "image", "action": "delete", "scope": "own"},
    
    # User management permissions
    {"name": "user.create", "resource": "user", "action": "create", "scope": "all"},
    {"name": "user.read", "resource": "user", "action": "read", "scope": "all"},
    {"name": "user.update", "resource": "user", "action": "update", "scope": "all"},
    {"name": "user.delete", "resource": "user", "action": "delete", "scope": "all"},
    
    # System permissions
    {"name": "system.admin", "resource": "system", "action": "admin", "scope": "all"},
]
