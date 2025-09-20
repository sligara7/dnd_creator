"""API key repository for auth service."""
from typing import Optional
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError, ApiKeyNotFoundError
from auth.models.api import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate
from auth.repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKeyResponse, ApiKeyCreate, ApiKeyUpdate]):
    """API key repository."""

    def __init__(self, storage_client: StorageClient) -> None:
        """Initialize API key repository.

        Args:
            storage_client: Storage service client
        """
        super().__init__(ApiKeyResponse, storage_client)

    async def create(self, api_key: ApiKeyCreate) -> ApiKeyResponse:
        """Create new API key.

        Args:
            api_key: API key creation model

        Returns:
            Created API key

        Raises:
            StorageError: If creation fails
        """
        return await self.storage_client.create_api_key(api_key)

    async def get(self, key_id: UUID) -> Optional[ApiKeyResponse]:
        """Get API key by ID.

        Args:
            key_id: API key ID

        Returns:
            API key if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_api_key(key_id)

    async def update(
        self,
        key_id: UUID,
        api_key: ApiKeyUpdate
    ) -> Optional[ApiKeyResponse]:
        """Update API key.

        Args:
            key_id: API key ID
            api_key: API key update model

        Returns:
            Updated API key

        Raises:
            StorageError: If update fails
            ApiKeyNotFoundError: If API key not found
        """
        try:
            return await self.storage_client.update_api_key(key_id, api_key)
        except StorageError as e:
            if "not found" in str(e):
                raise ApiKeyNotFoundError(f"API key {key_id} not found")
            raise

    async def delete(self, key_id: UUID) -> bool:
        """Delete API key.

        Args:
            key_id: API key ID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            await self.storage_client.delete_api_key(key_id)
            return True
        except StorageError as e:
            if "not found" in str(e):
                return False
            raise