"""User repository for auth service."""
from typing import Optional
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError, UserNotFoundError
from auth.models.api import UserCreate, UserResponse, UserUpdate
from auth.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserResponse, UserCreate, UserUpdate]):
    """User repository."""

    def __init__(self, storage_client: StorageClient) -> None:
        """Initialize user repository.

        Args:
            storage_client: Storage service client
        """
        super().__init__(UserResponse, storage_client)

    async def create(self, user: UserCreate) -> UserResponse:
        """Create new user.

        Args:
            user: User creation model

        Returns:
            Created user

        Raises:
            StorageError: If creation fails
        """
        return await self.storage_client.create_user(user)

    async def get(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_user(user_id)

    async def get_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_user_by_username(username)

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email.

        Args:
            email: Email address

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_user_by_email(email)

    async def update(
        self,
        user_id: UUID,
        user: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user.

        Args:
            user_id: User ID
            user: User update model

        Returns:
            Updated user

        Raises:
            StorageError: If update fails
            UserNotFoundError: If user not found
        """
        try:
            return await self.storage_client.update_user(user_id, user)
        except StorageError as e:
            if "not found" in str(e):
                raise UserNotFoundError(f"User {user_id} not found")
            raise

    async def delete(self, user_id: UUID) -> bool:
        """Delete user.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            await self.storage_client.delete_user(user_id)
            return True
        except StorageError as e:
            if "not found" in str(e):
                return False
            raise