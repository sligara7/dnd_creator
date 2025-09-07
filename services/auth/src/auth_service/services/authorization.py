"""Authorization service for access control and permission management."""

from typing import List, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.exceptions import AuthorizationError
from auth_service.models.role import Role
from auth_service.models.user import User
from auth_service.repositories.role import RoleRepository
from auth_service.repositories.user import UserRepository
from auth_service.services.audit import AuditService


class AuthorizationService:
    """Service for authorization and access control."""
    
    def __init__(
        self,
        db: AsyncSession,
        audit_service: Optional[AuditService] = None
    ):
        """
        Initialize authorization service.
        
        Args:
            db: Database session
            audit_service: Audit logging service
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.audit_service = audit_service or AuditService(db)
    
    async def check_permission(
        self,
        user_id: UUID,
        permission: str,
        resource_id: Optional[UUID] = None,
        context: Optional[dict] = None
    ) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User's UUID
            permission: Permission name to check
            resource_id: Optional resource ID for context
            context: Additional context for permission check
            
        Returns:
            True if user has permission, False otherwise
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return False
        
        # Check user permissions
        has_permission = user.has_permission(permission)
        
        # Log permission check
        await self.audit_service.log_permission_check(
            user_id=user_id,
            permission=permission,
            resource_id=resource_id,
            granted=has_permission,
            context=context
        )
        
        return has_permission
    
    async def check_permissions(
        self,
        user_id: UUID,
        permissions: List[str],
        require_all: bool = True
    ) -> bool:
        """
        Check if user has multiple permissions.
        
        Args:
            user_id: User's UUID
            permissions: List of permissions to check
            require_all: If True, user must have all permissions
            
        Returns:
            True if permission check passes
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return False
        
        user_permissions = set(user.get_permissions())
        required_permissions = set(permissions)
        
        if require_all:
            # User must have all permissions
            has_permissions = required_permissions.issubset(user_permissions)
        else:
            # User must have at least one permission
            has_permissions = bool(required_permissions.intersection(user_permissions))
        
        return has_permissions
    
    async def check_role(
        self,
        user_id: UUID,
        role: str
    ) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            user_id: User's UUID
            role: Role name to check
            
        Returns:
            True if user has role
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return False
        
        return user.has_role(role)
    
    async def check_roles(
        self,
        user_id: UUID,
        roles: List[str],
        require_all: bool = False
    ) -> bool:
        """
        Check if user has specific roles.
        
        Args:
            user_id: User's UUID
            roles: List of role names to check
            require_all: If True, user must have all roles
            
        Returns:
            True if role check passes
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return False
        
        user_roles = set(role.name for role in user.roles)
        required_roles = set(roles)
        
        if require_all:
            # User must have all roles
            has_roles = required_roles.issubset(user_roles)
        else:
            # User must have at least one role
            has_roles = bool(required_roles.intersection(user_roles))
        
        return has_roles
    
    async def get_user_permissions(
        self,
        user_id: UUID
    ) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of permission names
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return []
        
        return user.get_permissions()
    
    async def get_user_roles(
        self,
        user_id: UUID
    ) -> List[str]:
        """
        Get all roles for a user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of role names
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            return []
        
        return [role.name for role in user.roles]
    
    async def assign_role(
        self,
        user_id: UUID,
        role_name: str,
        assigned_by: UUID
    ) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User's UUID
            role_name: Name of role to assign
            assigned_by: UUID of user performing assignment
            
        Returns:
            True if role assigned successfully
            
        Raises:
            AuthorizationError: If role doesn't exist
        """
        # Get user and role
        user = await self.user_repo.get(user_id)
        if not user:
            raise AuthorizationError("User not found")
        
        role = await self.role_repo.get_by_name(role_name)
        if not role:
            raise AuthorizationError(f"Role '{role_name}' not found")
        
        # Check if user already has role
        if user.has_role(role_name):
            return True
        
        # Assign role
        user.roles.append(role)
        await self.db.commit()
        
        # Log role assignment
        await self.audit_service.log_role_assignment(
            user_id=user_id,
            role_id=role.id,
            role_name=role_name,
            assigned_by=assigned_by
        )
        
        return True
    
    async def revoke_role(
        self,
        user_id: UUID,
        role_name: str,
        revoked_by: UUID
    ) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: User's UUID
            role_name: Name of role to revoke
            revoked_by: UUID of user performing revocation
            
        Returns:
            True if role revoked successfully
        """
        # Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise AuthorizationError("User not found")
        
        # Find and remove role
        role_to_remove = None
        for role in user.roles:
            if role.name == role_name:
                role_to_remove = role
                break
        
        if not role_to_remove:
            return True  # Role already not assigned
        
        user.roles.remove(role_to_remove)
        await self.db.commit()
        
        # Log role revocation
        await self.audit_service.log_role_revocation(
            user_id=user_id,
            role_id=role_to_remove.id,
            role_name=role_name,
            revoked_by=revoked_by
        )
        
        return True
    
    async def check_resource_access(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        action: str
    ) -> bool:
        """
        Check if user can perform action on resource.
        
        Args:
            user_id: User's UUID
            resource_type: Type of resource (e.g., 'character', 'campaign')
            resource_id: Resource UUID
            action: Action to perform (e.g., 'read', 'write', 'delete')
            
        Returns:
            True if access is allowed
        """
        # Build permission string
        permission = f"{resource_type}:{action}"
        
        # Check general permission first
        if await self.check_permission(user_id, permission):
            return True
        
        # Check ownership-based permission
        ownership_permission = f"{resource_type}:{action}:own"
        if await self.check_permission(user_id, ownership_permission):
            # Check if user owns the resource
            # This would be implemented based on resource type
            is_owner = await self._check_resource_ownership(
                user_id, resource_type, resource_id
            )
            if is_owner:
                return True
        
        # Check specific resource permission
        specific_permission = f"{resource_type}:{resource_id}:{action}"
        if await self.check_permission(user_id, specific_permission):
            return True
        
        return False
    
    async def _check_resource_ownership(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID
    ) -> bool:
        """
        Check if user owns a resource.
        
        Args:
            user_id: User's UUID
            resource_type: Type of resource
            resource_id: Resource UUID
            
        Returns:
            True if user owns resource
        """
        # This would be implemented based on resource type
        # For now, return False as placeholder
        return False
    
    async def enforce_permission(
        self,
        user_id: UUID,
        permission: str,
        resource_id: Optional[UUID] = None
    ) -> None:
        """
        Enforce that user has permission, raise error if not.
        
        Args:
            user_id: User's UUID
            permission: Permission to enforce
            resource_id: Optional resource ID
            
        Raises:
            AuthorizationError: If user lacks permission
        """
        has_permission = await self.check_permission(
            user_id, permission, resource_id
        )
        
        if not has_permission:
            await self.audit_service.log_authorization_failure(
                user_id=user_id,
                permission=permission,
                resource_id=resource_id
            )
            raise AuthorizationError(f"Permission denied: {permission}")
    
    async def enforce_role(
        self,
        user_id: UUID,
        role: str
    ) -> None:
        """
        Enforce that user has role, raise error if not.
        
        Args:
            user_id: User's UUID
            role: Role to enforce
            
        Raises:
            AuthorizationError: If user lacks role
        """
        has_role = await self.check_role(user_id, role)
        
        if not has_role:
            await self.audit_service.log_authorization_failure(
                user_id=user_id,
                required_role=role
            )
            raise AuthorizationError(f"Role required: {role}")
