"""Session repository for auth service."""
from typing import Optional
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError, SessionInvalidError
from auth.models.api import SessionCreate, SessionResponse, SessionUpdate
from auth.repositories.base import BaseRepository


class SessionRepository(BaseRepository[SessionResponse, SessionCreate, SessionUpdate]):
    """Session repository."""

    def __init__(self, storage_client: StorageClient) -> None:
        """Initialize session repository.

        Args:
            storage_client: Storage service client
        """
        super().__init__(SessionResponse, storage_client)

    async def create(self, session: SessionCreate) -> SessionResponse:
        """Create new session.

        Args:
            session: Session creation model

        Returns:
            Created session

        Raises:
            StorageError: If creation fails
        """
        return await self.storage_client.create_session(session)

    async def get(self, session_id: UUID) -> Optional[SessionResponse]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        return await self.storage_client.get_session(session_id)

    async def update(
        self,
        session_id: UUID,
        session: SessionUpdate
    ) -> Optional[SessionResponse]:
        """Update session.

        Args:
            session_id: Session ID
            session: Session update model

        Returns:
            Updated session

        Raises:
            StorageError: If update fails
            SessionInvalidError: If session not found
        """
        try:
            return await self.storage_client.update_session(session_id, session)
        except StorageError as e:
            if "not found" in str(e):
                raise SessionInvalidError(f"Session {session_id} not found")
            raise

    async def delete(self, session_id: UUID) -> bool:
        """Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            await self.storage_client.delete_session(session_id)
            return True
        except StorageError as e:
            if "not found" in str(e):
                return False
            raise