"""API key management service for auth service."""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from redis.asyncio import Redis

from auth.clients.storage import StorageClient
from auth.core.config import get_settings
from auth.core.exceptions import (
    ApiKeyNotFoundError,
    StorageError,
)
from auth.integration.message_hub import (
    MessageHubClient,
    publish_security_event,
)
from auth.models.api import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate
from auth.services.user import UserService


logger = logging.getLogger(__name__)


class ApiKeyService:
    """Service for managing API keys."""

    def __init__(
        self,
        storage_client: StorageClient,
        message_hub: MessageHubClient,
        redis: Redis,
        user_service: UserService
    ) -> None:
        """Initialize API key service.

        Args:
            storage_client: Storage service client
            message_hub: Message Hub client
            redis: Redis client
            user_service: User service for user lookups
        """
        self.storage = storage_client
        self.message_hub = message_hub
        self.redis = redis
        self.user_service = user_service
        self.settings = get_settings()

    async def create_api_key(
        self,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        expires_in: Optional[int] = None
    ) -> Tuple[ApiKeyResponse, str]:
        """Create a new API key.

        Args:
            user_id: User ID
            name: Key name
            description: Optional key description
            expires_in: Optional expiration in seconds

        Returns:
            Tuple of (API key response, raw API key)

        Raises:
            UserNotFoundError: If user not found
            StorageError: If key creation fails
        """
        try:
            # Get user to ensure they exist
            user = await self.user_service.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Generate key and compute hash
            raw_key = self._generate_api_key()
            key_hash = self._hash_api_key(raw_key)

            # Calculate expiration
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            # Create API key
            key = await self.storage.create_api_key(
                ApiKeyCreate(
                    user_id=user_id,
                    key_hash=key_hash,
                    name=name,
                    description=description,
                    expires_at=expires_at
                )
            )

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "api_key_created",
                {
                    "key_id": str(key.id),
                    "user_id": str(user_id),
                    "name": name,
                    "expires_at": expires_at.isoformat() if expires_at else None
                }
            )

            logger.info(
                "Created API key",
                extra={
                    "key_id": str(key.id),
                    "user_id": str(user_id),
                    "name": name
                }
            )

            return key, raw_key

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to create API key",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "name": name
                }
            )
            raise StorageError(str(e))

    async def get_api_key(
        self,
        key_id: UUID
    ) -> Optional[ApiKeyResponse]:
        """Get an API key by ID.

        Args:
            key_id: API key ID

        Returns:
            API key if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            return await self.storage.get_api_key(key_id)

        except Exception as e:
            logger.error(
                "Failed to get API key",
                extra={
                    "error": str(e),
                    "key_id": str(key_id)
                }
            )
            raise StorageError(str(e))

    async def verify_api_key(
        self,
        raw_key: str,
        update_metrics: bool = True
    ) -> ApiKeyResponse:
        """Verify an API key.

        Args:
            raw_key: Raw API key to verify
            update_metrics: Whether to update metrics

        Returns:
            API key if valid

        Raises:
            InvalidCredentialsError: If key is invalid or expired
            StorageError: If verification fails
        """
        try:
            # Hash key for lookup
            key_hash = self._hash_api_key(raw_key)

            # Try Redis cache first
            key = None
            if update_metrics:
                key = await self._get_key_from_cache(key_hash)

            # Check storage if not in cache
            if not key:
                key = await self._get_key_by_hash(key_hash)
                if not key:
                    raise InvalidCredentialsError("Invalid API key")

            # Validate key
            self._validate_api_key(key)

            # Update metrics if requested
            if update_metrics:
                # Store key in cache
                await self._store_key_in_cache(key_hash, key)

                # Update last used timestamp
                update = ApiKeyUpdate(last_used=datetime.utcnow())
                await self.storage.update_api_key(key.id, update)

                # Publish security event
                await publish_security_event(
                    self.message_hub,
                    "api_key_used",
                    {
                        "key_id": str(key.id),
                        "user_id": str(key.user_id)
                    }
                )

            return key

        except InvalidCredentialsError:
            raise

        except Exception as e:
            logger.error(
                "Failed to verify API key",
                extra={"error": str(e)}
            )
            raise StorageError(str(e))

    async def revoke_api_key(self, key_id: UUID) -> None:
        """Revoke an API key.

        Args:
            key_id: API key ID

        Raises:
            ApiKeyNotFoundError: If key not found
            StorageError: If revocation fails
        """
        try:
            # Get key first
            key = await self.storage.get_api_key(key_id)
            if not key:
                raise ApiKeyNotFoundError(f"API key {key_id} not found")

            # Update key status
            update = ApiKeyUpdate(
                is_active=False,
                deleted_at=datetime.utcnow()
            )
            updated = await self.storage.update_api_key(key_id, update)
            if updated:
                # Remove from cache
                await self._remove_key_from_cache(updated.key_hash)

                # Publish security event
                await publish_security_event(
                    self.message_hub,
                    "api_key_revoked",
                    {
                        "key_id": str(key_id),
                        "user_id": str(key.user_id)
                    }
                )

                logger.info(
                    "Revoked API key",
                    extra={
                        "key_id": str(key_id),
                        "user_id": str(key.user_id)
                    }
                )

        except ApiKeyNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to revoke API key",
                extra={
                    "error": str(e),
                    "key_id": str(key_id)
                }
            )
            raise StorageError(str(e))

    async def get_user_api_keys(
        self,
        user_id: UUID
    ) -> List[ApiKeyResponse]:
        """Get all API keys for a user.

        Args:
            user_id: User ID

        Returns:
            List of user's API keys

        Raises:
            StorageError: If retrieval fails
        """
        try:
            # Get user's keys with filtering
            # Note: This should be replaced with a proper API when storage
            # service adds support for filtering/pagination
            keys = []
            async for key in self._list_api_keys():
                if key.user_id == user_id:
                    keys.append(key)
            return keys

        except Exception as e:
            logger.error(
                "Failed to get user API keys",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def revoke_user_api_keys(self, user_id: UUID) -> int:
        """Revoke all API keys for a user.

        Args:
            user_id: User ID

        Returns:
            Number of keys revoked

        Raises:
            StorageError: If revocation fails
        """
        try:
            # Get user's active keys
            revoked = 0
            async for key in self._list_api_keys():
                if key.user_id == user_id and key.is_active:
                    try:
                        await self.revoke_api_key(key.id)
                        revoked += 1
                    except Exception:
                        logger.warning(
                            "Failed to revoke API key",
                            extra={
                                "key_id": str(key.id),
                                "user_id": str(user_id)
                            }
                        )

            if revoked > 0:
                # Publish security event
                await publish_security_event(
                    self.message_hub,
                    "user_api_keys_revoked",
                    {
                        "user_id": str(user_id),
                        "count": revoked
                    }
                )

                logger.info(
                    "Revoked all user API keys",
                    extra={
                        "user_id": str(user_id),
                        "count": revoked
                    }
                )

            return revoked

        except Exception as e:
            logger.error(
                "Failed to revoke user API keys",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    def _generate_api_key(self) -> str:
        """Generate a new API key.

        Returns:
            Generated API key
        """
        # Generate 32 bytes of random data
        key_bytes = secrets.token_bytes(32)
        # Encode in base32 for URL-safe string
        return secrets.token_urlsafe(32)

    def _hash_api_key(self, raw_key: str) -> str:
        """Hash an API key.

        Args:
            raw_key: Raw API key to hash

        Returns:
            Hashed API key
        """
        # Use SHA-256 for key hashing
        hasher = hashlib.sha256()
        hasher.update(raw_key.encode())
        return hasher.hexdigest()

    def _validate_api_key(self, key: ApiKeyResponse) -> None:
        """Validate an API key.

        Args:
            key: API key to validate

        Raises:
            InvalidCredentialsError: If key is invalid or expired
        """
        now = datetime.utcnow()

        # Check status
        if not key.is_active:
            raise InvalidCredentialsError("API key is inactive")

        # Check expiration
        if key.expires_at and key.expires_at < now:
            raise InvalidCredentialsError("API key has expired")

    async def _get_key_by_hash(
        self,
        key_hash: str
    ) -> Optional[ApiKeyResponse]:
        """Get API key by hash.

        Args:
            key_hash: Hashed API key

        Returns:
            API key if found, None otherwise

        Raises:
            StorageError: If lookup fails
        """
        try:
            # Note: This should be replaced with a proper API when storage
            # service adds support for querying by key_hash
            async for key in self._list_api_keys():
                if key.key_hash == key_hash:
                    return key
            return None

        except Exception as e:
            logger.error(
                "Failed to get API key by hash",
                extra={"error": str(e)}
            )
            raise StorageError(str(e))

    async def _list_api_keys(self):
        """List all API keys.

        Yields:
            API keys from storage
        """
        # Note: This should be replaced with proper pagination once
        # storage service adds support for it
        key = None
        while True:
            key = await self.storage.get_api_key(key.id if key else None)
            if not key:
                break
            yield key

    async def _store_key_in_cache(
        self,
        key_hash: str,
        key: ApiKeyResponse
    ) -> None:
        """Store API key in Redis cache.

        Args:
            key_hash: Key hash for lookup
            key: API key to store
        """
        redis_key = f"api_key:{key_hash}"
        ttl = 300  # 5 minutes
        if key.expires_at:
            # If key expires, use remaining time as TTL
            remaining = (key.expires_at - datetime.utcnow()).total_seconds()
            ttl = min(ttl, max(0, int(remaining)))
        await self.redis.setex(
            redis_key,
            ttl,
            key.model_dump_json()
        )

    async def _get_key_from_cache(
        self,
        key_hash: str
    ) -> Optional[ApiKeyResponse]:
        """Get API key from Redis cache.

        Args:
            key_hash: Key hash to lookup

        Returns:
            API key if found in cache, None otherwise
        """
        redis_key = f"api_key:{key_hash}"
        data = await self.redis.get(redis_key)
        if data:
            return ApiKeyResponse.model_validate_json(data)
        return None

    async def _remove_key_from_cache(
        self,
        key_hash: str
    ) -> None:
        """Remove API key from Redis cache.

        Args:
            key_hash: Key hash to remove
        """
        redis_key = f"api_key:{key_hash}"
        await self.redis.delete(redis_key)