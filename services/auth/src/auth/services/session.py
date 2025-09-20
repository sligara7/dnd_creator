"""Session management service for auth service."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from redis.asyncio import Redis

from auth.clients.storage import StorageClient
from auth.core.config import get_settings
from auth.core.exceptions import (
    SessionExpiredError,
    SessionInvalidError,
    StorageError,
)
from auth.integration.message_hub import (
    MessageHubClient,
    publish_security_event,
)
from auth.models.api import SessionCreate, SessionResponse, SessionUpdate


logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions."""

    def __init__(
        self,
        storage_client: StorageClient,
        message_hub: MessageHubClient,
        redis: Redis,
        session_ttl: Optional[int] = None
    ) -> None:
        """Initialize session service.

        Args:
            storage_client: Storage service client
            message_hub: Message Hub client
            redis: Redis client
            session_ttl: Session TTL in seconds (default from settings)
        """
        self.storage = storage_client
        self.message_hub = message_hub
        self.redis = redis
        self.settings = get_settings()
        self.session_ttl = session_ttl or self.settings.token_expiration

    async def create_session(
        self,
        user_id: UUID,
        access_token: str,
        refresh_token: str,
        client_info: Optional[dict] = None
    ) -> SessionResponse:
        """Create a new session.

        Args:
            user_id: User ID
            access_token: JWT access token
            refresh_token: Refresh token
            client_info: Optional client information

        Returns:
            Created session

        Raises:
            StorageError: If session creation fails
        """
        try:
            # Calculate expiration based on token TTL
            expires_at = datetime.utcnow() + timedelta(seconds=self.session_ttl)

            # Create session in storage
            session = await self.storage.create_session(
                SessionCreate(
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="Bearer",
                    expires_at=expires_at,
                    client_info=client_info or {}
                )
            )

            # Store session in Redis
            await self._store_session_in_cache(session)

            # Notify about new session
            await publish_security_event(
                self.message_hub,
                "session_created",
                {
                    "user_id": str(user_id),
                    "session_id": str(session.id),
                    "client_info": client_info or {}
                }
            )

            logger.info(
                "Created session",
                extra={
                    "user_id": str(user_id),
                    "session_id": str(session.id)
                }
            )

            return session

        except StorageError as e:
            logger.error(
                "Failed to create session",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise

    async def get_session(
        self,
        session_id: UUID,
        validate: bool = True
    ) -> Optional[SessionResponse]:
        """Get a session by ID.

        Args:
            session_id: Session ID
            validate: Whether to validate session

        Returns:
            Session if found and valid, None if not found

        Raises:
            SessionExpiredError: If session expired
            SessionInvalidError: If session invalid
            StorageError: If retrieval fails
        """
        try:
            # Try from Redis first
            session = await self._get_session_from_cache(session_id)
            if not session:
                # Not found in cache, try storage
                session = await self.storage.get_session(session_id)
                if session:
                    # Store in cache for next time
                    await self._store_session_in_cache(session)

            if not session:
                return None

            if validate:
                await self._validate_session(session)

            return session

        except (SessionExpiredError, SessionInvalidError):
            # Clear invalid session from cache
            await self._remove_session_from_cache(session_id)
            raise

        except Exception as e:
            logger.error(
                "Error getting session",
                extra={
                    "error": str(e),
                    "session_id": str(session_id)
                }
            )
            raise StorageError(str(e))

    async def update_session(
        self,
        session_id: UUID,
        update: SessionUpdate
    ) -> Optional[SessionResponse]:
        """Update a session.

        Args:
            session_id: Session ID
            update: Session update data

        Returns:
            Updated session if found, None otherwise

        Raises:
            StorageError: If update fails
        """
        try:
            # Update in storage
            session = await self.storage.update_session(session_id, update)
            if not session:
                return None

            # Update cache
            await self._store_session_in_cache(session)

            logger.info(
                "Updated session",
                extra={
                    "session_id": str(session_id),
                    "user_id": str(session.user_id)
                }
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to update session",
                extra={
                    "error": str(e),
                    "session_id": str(session_id)
                }
            )
            raise StorageError(str(e))

    async def revoke_session(self, session_id: UUID) -> bool:
        """Revoke a session.

        Args:
            session_id: Session ID

        Returns:
            True if session revoked, False if not found

        Raises:
            StorageError: If revocation fails
        """
        try:
            # Get session first
            session = await self.storage.get_session(session_id)
            if not session:
                return False

            # Update session status
            now = datetime.utcnow()
            update = SessionUpdate(
                is_active=False,
                revoked_at=now,
                updated_at=now
            )
            updated = await self.storage.update_session(session_id, update)
            if not updated:
                return False

            # Remove from cache
            await self._remove_session_from_cache(session_id)

            # Notify about revoked session
            await publish_security_event(
                self.message_hub,
                "session_revoked",
                {
                    "session_id": str(session_id),
                    "user_id": str(session.user_id)
                }
            )

            logger.info(
                "Revoked session",
                extra={
                    "session_id": str(session_id),
                    "user_id": str(session.user_id)
                }
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to revoke session",
                extra={
                    "error": str(e),
                    "session_id": str(session_id)
                }
            )
            raise StorageError(str(e))

    async def revoke_all_user_sessions(self, user_id: UUID) -> int:
        """Revoke all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions revoked

        Raises:
            StorageError: If revocation fails
        """
        # For now we don't have a bulk operation API in the storage service
        # So we need to query and revoke sessions one by one
        # This can be optimized once storage service supports bulk operations
        revoked = 0
        try:
            # Get user's active sessions
            async for session in self._get_user_sessions(user_id):
                # Revoke each session
                if await self.revoke_session(session.id):
                    revoked += 1

            if revoked > 0:
                # Notify about bulk revocation
                await publish_security_event(
                    self.message_hub,
                    "user_sessions_revoked",
                    {
                        "user_id": str(user_id),
                        "count": revoked
                    }
                )

                logger.info(
                    "Revoked all user sessions",
                    extra={
                        "user_id": str(user_id),
                        "count": revoked
                    }
                )

            return revoked

        except Exception as e:
            logger.error(
                "Failed to revoke user sessions",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def _validate_session(self, session: SessionResponse) -> None:
        """Validate a session.

        Args:
            session: Session to validate

        Raises:
            SessionExpiredError: If session expired
            SessionInvalidError: If session invalid
        """
        now = datetime.utcnow()

        # Check active status
        if not session.is_active:
            raise SessionInvalidError(f"Session {session.id} is inactive")

        # Check expiration
        if session.expires_at < now:
            raise SessionExpiredError(f"Session {session.id} expired")

        # Check revocation
        if session.revoked_at is not None:
            raise SessionInvalidError(f"Session {session.id} was revoked")

    async def _store_session_in_cache(self, session: SessionResponse) -> None:
        """Store session in Redis cache.

        Args:
            session: Session to store
        """
        key = f"session:{session.id}"
        ttl = max(0, int((session.expires_at - datetime.utcnow()).total_seconds()))
        await self.redis.setex(
            key,
            ttl,
            session.model_dump_json()
        )

    async def _get_session_from_cache(
        self,
        session_id: UUID
    ) -> Optional[SessionResponse]:
        """Get session from Redis cache.

        Args:
            session_id: Session ID

        Returns:
            Session if found in cache, None otherwise
        """
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        if data:
            return SessionResponse.model_validate_json(data)
        return None

    async def _remove_session_from_cache(self, session_id: UUID) -> None:
        """Remove session from Redis cache.

        Args:
            session_id: Session ID
        """
        key = f"session:{session_id}"
        await self.redis.delete(key)

    async def _get_user_sessions(self, user_id: UUID):
        """Get all sessions for a user.

        Args:
            user_id: User ID

        Yields:
            User's sessions
        """
        # This should be replaced with proper pagination once storage service
        # adds support for filtering sessions by user_id
        # For now, we just yield all found sessions that match
        session = None
        while True:
            session = await self.storage.get_session(session.id if session else None)
            if not session:
                break
            if session.user_id == user_id:
                yield session