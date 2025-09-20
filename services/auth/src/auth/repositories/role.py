"""Role repository for auth service."""
from typing import Optional
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError, RoleNotFoundError
from auth.models.api import RoleCreate, RoleResponse, RoleUpdate
from auth.repositories.base import BaseRepository


class RoleRepository(BaseRepository[RoleResponse, RoleCreate, RoleUpdate]):
    """Role repository."""

    def __init__(self, storage_client: StorageClient) -> None:
        """Initialize role repository.

        Args:
            storage_client: Storage service client
        """
        super().__init__(RoleResponse, storage_client)

    async def create(self, role: RoleCreate) -> RoleResponse:
        """Create new role.

        Args:
            role: Role creation model

        Returns:
            Created role

        Raises:
            StorageError: If creation fails
        """
        return await self.storage_client.create_role(role)

    async def get(self, role_id: UUID) -> Optional[RoleResponse]:
        """Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_role(role_id)

    async def update(
        self,
        role_id: UUID,
        role: RoleUpdate
    ) -> Optional[RoleResponse]:
        """Update role.

        Args:
            role_id: Role ID
            role: Role update model

        Returns:
            Updated role

        Raises:
            StorageError: If update fails
            RoleNotFoundError: If role not found
        """
        try:
            return await self.storage_client.update_role(role_id, role)
        except StorageError as e:
            if "not found" in str(e):
                raise RoleNotFoundError(f"Role {role_id} not found")
            raise

    async def delete(self, role_id: UUID) -> bool:
        """Delete role.

        Args:
            role_id: Role ID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            await self.storage_client.delete_role(role_id)
            return True
        except StorageError as e:
            if "not found" in str(e):
                return False
            raise