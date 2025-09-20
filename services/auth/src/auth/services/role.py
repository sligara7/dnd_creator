"""Role management service for auth service."""
import logging
from typing import List, Optional, Set
from uuid import UUID

from redis.asyncio import Redis

from auth.clients.storage import StorageClient
from auth.core.exceptions import (
    RoleNotFoundError,
    StorageError,
)
from auth.integration.message_hub import (
    MessageHubClient,
    publish_role_change,
    publish_security_event,
)
from auth.models.api import RoleCreate, RoleResponse, RoleUpdate


logger = logging.getLogger(__name__)


class RoleService:
    """Service for managing roles."""

    def __init__(
        self,
        storage_client: StorageClient,
        message_hub: MessageHubClient,
        redis: Redis
    ) -> None:
        """Initialize role service.

        Args:
            storage_client: Storage service client
            message_hub: Message Hub client
            redis: Redis client
        """
        self.storage = storage_client
        self.message_hub = message_hub
        self.redis = redis

    async def create_role(self, role: RoleCreate) -> RoleResponse:
        """Create a new role.

        Args:
            role: Role creation data

        Returns:
            Created role

        Raises:
            StorageError: If role creation fails
        """
        try:
            # Create role in storage
            created = await self.storage.create_role(role)

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "role_created",
                {
                    "role_id": str(created.id),
                    "name": created.name,
                    "is_system_role": created.is_system_role
                }
            )

            logger.info(
                "Created role",
                extra={
                    "role_id": str(created.id),
                    "name": created.name
                }
            )

            return created

        except Exception as e:
            logger.error(
                "Failed to create role",
                extra={
                    "error": str(e),
                    "name": role.name
                }
            )
            raise StorageError(str(e))

    async def get_role(self, role_id: UUID) -> Optional[RoleResponse]:
        """Get a role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            return await self.storage.get_role(role_id)

        except Exception as e:
            logger.error(
                "Failed to get role",
                extra={
                    "error": str(e),
                    "role_id": str(role_id)
                }
            )
            raise StorageError(str(e))

    async def update_role(
        self,
        role_id: UUID,
        update: RoleUpdate
    ) -> Optional[RoleResponse]:
        """Update a role.

        Args:
            role_id: Role ID
            update: Role update data

        Returns:
            Updated role if found, None otherwise

        Raises:
            StorageError: If update fails
            RoleNotFoundError: If role not found
        """
        try:
            # Get current role for change tracking
            current_role = await self.storage.get_role(role_id)
            if not current_role:
                raise RoleNotFoundError(f"Role {role_id} not found")

            # Update role
            updated = await self.storage.update_role(role_id, update)
            if not updated:
                return None

            # Track changes
            changes = {
                field: getattr(updated, field)
                for field in update.__fields_set__
                if getattr(updated, field) != getattr(current_role, field)
            }

            if changes:
                # Publish security event for role change
                await publish_security_event(
                    self.message_hub,
                    "role_updated",
                    {
                        "role_id": str(role_id),
                        "changes": changes
                    }
                )

                logger.info(
                    "Updated role",
                    extra={
                        "role_id": str(role_id),
                        "changes": list(changes.keys())
                    }
                )

            return updated

        except RoleNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to update role",
                extra={
                    "error": str(e),
                    "role_id": str(role_id)
                }
            )
            raise StorageError(str(e))

    async def delete_role(self, role_id: UUID) -> bool:
        """Delete a role.

        Args:
            role_id: Role ID

        Returns:
            True if role deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            # Get role first for system role check
            role = await self.storage.get_role(role_id)
            if not role:
                return False

            # Prevent deletion of system roles
            if role.is_system_role:
                logger.warning(
                    "Attempted to delete system role",
                    extra={"role_id": str(role_id)}
                )
                return False

            # Delete role
            success = await self.storage.delete_role(role_id)
            if success:
                # Publish security event
                await publish_security_event(
                    self.message_hub,
                    "role_deleted",
                    {"role_id": str(role_id)}
                )

                logger.info(
                    "Deleted role",
                    extra={"role_id": str(role_id)}
                )

            return success

        except Exception as e:
            logger.error(
                "Failed to delete role",
                extra={
                    "error": str(e),
                    "role_id": str(role_id)
                }
            )
            raise StorageError(str(e))

    async def assign_role_to_user(
        self,
        role_id: UUID,
        user_id: UUID
    ) -> None:
        """Assign a role to a user.

        Args:
            role_id: Role ID
            user_id: User ID

        Raises:
            RoleNotFoundError: If role not found
            UserNotFoundError: If user not found
            StorageError: If assignment fails
        """
        try:
            # Get role first
            role = await self.storage.get_role(role_id)
            if not role:
                raise RoleNotFoundError(f"Role {role_id} not found")

            # Assign role
            await self.storage.assign_user_role(user_id, role_id)

            # Publish event
            await publish_role_change(
                self.message_hub,
                user_id,
                role_id,
                assigned=True
            )

            logger.info(
                "Assigned role to user",
                extra={
                    "role_id": str(role_id),
                    "user_id": str(user_id)
                }
            )

        except RoleNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to assign role to user",
                extra={
                    "error": str(e),
                    "role_id": str(role_id),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def revoke_role_from_user(
        self,
        role_id: UUID,
        user_id: UUID
    ) -> None:
        """Revoke a role from a user.

        Args:
            role_id: Role ID
            user_id: User ID

        Raises:
            StorageError: If revocation fails
        """
        try:
            # Revoke role
            await self.storage.revoke_user_role(user_id, role_id)

            # Publish event
            await publish_role_change(
                self.message_hub,
                user_id,
                role_id,
                assigned=False
            )

            logger.info(
                "Revoked role from user",
                extra={
                    "role_id": str(role_id),
                    "user_id": str(user_id)
                }
            )

        except Exception as e:
            logger.error(
                "Failed to revoke role from user",
                extra={
                    "error": str(e),
                    "role_id": str(role_id),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def get_user_roles(
        self,
        user_id: UUID,
        use_cache: bool = True
    ) -> List[RoleResponse]:
        """Get all roles assigned to a user.

        Args:
            user_id: User ID
            use_cache: Whether to use Redis cache

        Returns:
            List of user's roles

        Raises:
            StorageError: If retrieval fails
        """
        try:
            # Try cache first if enabled
            if use_cache:
                roles = await self._get_roles_from_cache(user_id)
                if roles is not None:
                    return roles

            # Get from storage
            roles = await self.storage.get_user_roles(user_id)

            # Update cache
            if use_cache:
                await self._store_roles_in_cache(user_id, roles)

            return roles

        except Exception as e:
            logger.error(
                "Failed to get user roles",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def has_role(
        self,
        user_id: UUID,
        role_name: str
    ) -> bool:
        """Check if a user has a specific role.

        Args:
            user_id: User ID
            role_name: Role name to check

        Returns:
            True if user has role, False otherwise

        Raises:
            StorageError: If check fails
        """
        try:
            # Get user's roles
            roles = await self.get_user_roles(user_id)
            return any(r.name == role_name for r in roles)

        except Exception as e:
            logger.error(
                "Failed to check user role",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "role_name": role_name
                }
            )
            raise StorageError(str(e))

    async def has_any_role(
        self,
        user_id: UUID,
        role_names: List[str]
    ) -> bool:
        """Check if a user has any of the specified roles.

        Args:
            user_id: User ID
            role_names: Role names to check

        Returns:
            True if user has any role, False otherwise

        Raises:
            StorageError: If check fails
        """
        try:
            # Get user's roles
            roles = await self.get_user_roles(user_id)
            role_set = {r.name for r in roles}
            return bool(role_set & set(role_names))

        except Exception as e:
            logger.error(
                "Failed to check user roles",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "role_names": role_names
                }
            )
            raise StorageError(str(e))

    async def get_roles_by_scope(
        self,
        scope: str
    ) -> List[RoleResponse]:
        """Get all roles in a scope.

        Args:
            scope: Role scope (e.g., "character", "campaign")

        Returns:
            List of roles in scope

        Raises:
            StorageError: If retrieval fails
        """
        try:
            # Get all roles and filter by scope
            # Note: This should be replaced with a proper API in the storage
            # service once filtering/pagination is added
            roles = []
            async for role in self._list_roles():
                if role.name.startswith(f"{scope}:"):
                    roles.append(role)
            return roles

        except Exception as e:
            logger.error(
                "Failed to get roles by scope",
                extra={
                    "error": str(e),
                    "scope": scope
                }
            )
            raise StorageError(str(e))

    async def _list_roles(self):
        """List all roles.

        Yields:
            Roles from storage
        """
        # Note: This should be replaced with proper pagination once
        # storage service adds support for it
        role = None
        while True:
            role = await self.storage.get_role(role.id if role else None)
            if not role:
                break
            yield role

    async def _store_roles_in_cache(
        self,
        user_id: UUID,
        roles: List[RoleResponse]
    ) -> None:
        """Store user roles in Redis cache.

        Args:
            user_id: User ID
            roles: Roles to cache
        """
        key = f"user_roles:{user_id}"
        await self.redis.setex(
            key,
            3600,  # 1 hour TTL
            json.dumps([r.model_dump() for r in roles])
        )

    async def _get_roles_from_cache(
        self,
        user_id: UUID
    ) -> Optional[List[RoleResponse]]:
        """Get user roles from Redis cache.

        Args:
            user_id: User ID

        Returns:
            List of roles if found in cache, None otherwise
        """
        key = f"user_roles:{user_id}"
        data = await self.redis.get(key)
        if data:
            return [
                RoleResponse.model_validate(r)
                for r in json.loads(data)
            ]
        return None