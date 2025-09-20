"""User management service for auth service."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Set
from uuid import UUID

import argon2
from redis.asyncio import Redis

from auth.clients.storage import StorageClient
from auth.core.config import get_settings
from auth.core.exceptions import (
    InvalidCredentialsError,
    StorageError,
    UserLockedError,
    UserNotFoundError,
)
from auth.integration.message_hub import (
    MessageHubClient,
    publish_security_event,
    publish_user_created,
)
from auth.models.api import UserCreate, UserResponse, UserUpdate


logger = logging.getLogger(__name__)
pwd_hasher = argon2.PasswordHasher()


class UserService:
    """Service for managing users."""

    def __init__(
        self,
        storage_client: StorageClient,
        message_hub: MessageHubClient,
        redis: Redis
    ) -> None:
        """Initialize user service.

        Args:
            storage_client: Storage service client
            message_hub: Message Hub client
            redis: Redis client
        """
        self.storage = storage_client
        self.message_hub = message_hub
        self.redis = redis
        self.settings = get_settings()

    async def create_user(
        self,
        user_data: UserCreate,
        publish_event: bool = True
    ) -> UserResponse:
        """Create a new user.

        Args:
            user_data: User creation data
            publish_event: Whether to publish creation event

        Returns:
            Created user

        Raises:
            StorageError: If user creation fails
        """
        try:
            # Hash password
            hashed_password = pwd_hasher.hash(user_data.password)

            # Create user with hashed password
            user = await self.storage.create_user(
                UserCreate(
                    username=user_data.username,
                    email=user_data.email,
                    password=hashed_password
                )
            )

            # Publish creation event if requested
            if publish_event:
                await publish_user_created(
                    self.message_hub,
                    user.id,
                    user.username
                )

            logger.info(
                "Created user",
                extra={
                    "user_id": str(user.id),
                    "username": user.username
                }
            )

            return user

        except Exception as e:
            logger.error(
                "Failed to create user",
                extra={
                    "error": str(e),
                    "username": user_data.username
                }
            )
            raise StorageError(str(e))

    async def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            return await self.storage.get_user(user_id)

        except Exception as e:
            logger.error(
                "Failed to get user",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def get_user_by_username(
        self,
        username: str
    ) -> Optional[UserResponse]:
        """Get a user by username.

        Args:
            username: Username to look up

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            return await self.storage.get_user_by_username(username)

        except Exception as e:
            logger.error(
                "Failed to get user by username",
                extra={
                    "error": str(e),
                    "username": username
                }
            )
            raise StorageError(str(e))

    async def get_user_by_email(
        self,
        email: str
    ) -> Optional[UserResponse]:
        """Get a user by email.

        Args:
            email: Email to look up

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            return await self.storage.get_user_by_email(email)

        except Exception as e:
            logger.error(
                "Failed to get user by email",
                extra={
                    "error": str(e),
                    "email": email
                }
            )
            raise StorageError(str(e))

    async def update_user(
        self,
        user_id: UUID,
        update: UserUpdate
    ) -> Optional[UserResponse]:
        """Update a user.

        Args:
            user_id: User ID
            update: User update data

        Returns:
            Updated user if found, None otherwise

        Raises:
            StorageError: If update fails
            UserNotFoundError: If user not found
        """
        try:
            # Get current user for change tracking
            current_user = await self.storage.get_user(user_id)
            if not current_user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Hash new password if provided
            if update.password:
                update.password = pwd_hasher.hash(update.password)

            # Apply update
            updated = await self.storage.update_user(user_id, update)
            if not updated:
                return None

            # Track changes
            changes = {
                field: getattr(updated, field)
                for field in update.__fields_set__
                if getattr(updated, field) != getattr(current_user, field)
            }

            if changes:
                # Publish security event for significant changes
                significant_fields = {
                    "email", "status", "mfa_enabled",
                    "failed_attempts", "locked_until"
                }
                if significant_fields & set(changes.keys()):
                    await publish_security_event(
                        self.message_hub,
                        "user_updated",
                        {
                            "user_id": str(user_id),
                            "changes": changes
                        }
                    )

                logger.info(
                    "Updated user",
                    extra={
                        "user_id": str(user_id),
                        "changes": list(changes.keys())
                    }
                )

            return updated

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to update user",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user.

        Args:
            user_id: User ID

        Returns:
            True if user deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        try:
            # Get user first
            user = await self.storage.get_user(user_id)
            if not user:
                return False

            # Delete user
            success = await self.storage.delete_user(user_id)
            if success:
                # Publish security event
                await publish_security_event(
                    self.message_hub,
                    "user_deleted",
                    {"user_id": str(user_id)}
                )

                logger.info(
                    "Deleted user",
                    extra={"user_id": str(user_id)}
                )

            return success

        except Exception as e:
            logger.error(
                "Failed to delete user",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def verify_password(
        self,
        user_id: UUID,
        password: str,
        update_metrics: bool = True,
        client_info: Optional[dict] = None
    ) -> None:
        """Verify a user's password.

        Args:
            user_id: User ID
            password: Password to verify
            update_metrics: Whether to update login metrics
            client_info: Optional client information

        Raises:
            UserNotFoundError: If user not found
            UserLockedError: If account is locked
            InvalidCredentialsError: If password is invalid
            StorageError: If verification fails
        """
        try:
            # Get user
            user = await self.storage.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Check account status
            if user.status == "locked":
                if (
                    user.locked_until and
                    user.locked_until > datetime.utcnow()
                ):
                    raise UserLockedError("Account is locked")

            # Verify password
            try:
                pwd_hasher.verify(user.password_hash, password)

                if update_metrics:
                    # Reset failed attempts on success
                    if user.failed_attempts > 0:
                        await self.update_user(
                            user_id,
                            UserUpdate(
                                failed_attempts=0,
                                locked_until=None
                            )
                        )

                    # Publish successful login event
                    await publish_security_event(
                        self.message_hub,
                        "login_success",
                        {
                            "user_id": str(user_id),
                            "client_info": client_info or {}
                        }
                    )

            except argon2.exceptions.VerifyMismatchError:
                if update_metrics:
                    # Increment failed attempts
                    failed_attempts = user.failed_attempts + 1
                    update = UserUpdate(failed_attempts=failed_attempts)

                    # Lock account if max attempts exceeded
                    if failed_attempts >= self.settings.max_login_attempts:
                        locked_until = datetime.utcnow() + timedelta(
                            seconds=self.settings.lockout_duration
                        )
                        update.locked_until = locked_until
                        update.status = "locked"

                    await self.update_user(user_id, update)

                    # Publish failed login event
                    await publish_security_event(
                        self.message_hub,
                        "login_failed",
                        {
                            "user_id": str(user_id),
                            "failed_attempts": failed_attempts,
                            "client_info": client_info or {}
                        }
                    )

                raise InvalidCredentialsError("Invalid password")

        except (UserNotFoundError, UserLockedError, InvalidCredentialsError):
            raise

        except Exception as e:
            logger.error(
                "Failed to verify password",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> None:
        """Change a user's password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Raises:
            UserNotFoundError: If user not found
            InvalidCredentialsError: If current password is invalid
            StorageError: If password change fails
        """
        try:
            # First verify current password
            await self.verify_password(
                user_id,
                current_password,
                update_metrics=False
            )

            # Hash and set new password
            new_hash = pwd_hasher.hash(new_password)
            await self.update_user(
                user_id,
                UserUpdate(password=new_hash)
            )

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "password_changed",
                {"user_id": str(user_id)}
            )

            logger.info(
                "Changed user password",
                extra={"user_id": str(user_id)}
            )

        except (UserNotFoundError, InvalidCredentialsError):
            raise

        except Exception as e:
            logger.error(
                "Failed to change password",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def reset_password(
        self,
        user_id: UUID,
        new_password: str,
        reset_failed_attempts: bool = True
    ) -> None:
        """Reset a user's password.

        Args:
            user_id: User ID
            new_password: New password
            reset_failed_attempts: Whether to reset failed login attempts

        Raises:
            UserNotFoundError: If user not found
            StorageError: If password reset fails
        """
        try:
            # Get user
            user = await self.storage.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Hash new password
            new_hash = pwd_hasher.hash(new_password)

            # Update user
            update = UserUpdate(password=new_hash)
            if reset_failed_attempts:
                update.failed_attempts = 0
                update.locked_until = None
                update.status = "active"

            await self.update_user(user_id, update)

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "password_reset",
                {"user_id": str(user_id)}
            )

            logger.info(
                "Reset user password",
                extra={"user_id": str(user_id)}
            )

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to reset password",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def enable_mfa(
        self,
        user_id: UUID,
        mfa_secret: str
    ) -> None:
        """Enable MFA for a user.

        Args:
            user_id: User ID
            mfa_secret: MFA secret key

        Raises:
            UserNotFoundError: If user not found
            StorageError: If MFA setup fails
        """
        try:
            # Get user first
            user = await self.storage.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Update user with MFA settings
            await self.update_user(
                user_id,
                UserUpdate(
                    mfa_enabled=True,
                    mfa_secret=mfa_secret
                )
            )

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "mfa_enabled",
                {"user_id": str(user_id)}
            )

            logger.info(
                "Enabled MFA for user",
                extra={"user_id": str(user_id)}
            )

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to enable MFA",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def disable_mfa(self, user_id: UUID) -> None:
        """Disable MFA for a user.

        Args:
            user_id: User ID

        Raises:
            UserNotFoundError: If user not found
            StorageError: If MFA disable fails
        """
        try:
            # Get user first
            user = await self.storage.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Update user
            await self.update_user(
                user_id,
                UserUpdate(
                    mfa_enabled=False,
                    mfa_secret=None
                )
            )

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "mfa_disabled",
                {"user_id": str(user_id)}
            )

            logger.info(
                "Disabled MFA for user",
                extra={"user_id": str(user_id)}
            )

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to disable MFA",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))

    async def lock_account(
        self,
        user_id: UUID,
        duration: Optional[int] = None,
        reason: Optional[str] = None
    ) -> None:
        """Lock a user account.

        Args:
            user_id: User ID
            duration: Optional lock duration in seconds
            reason: Optional reason for lock

        Raises:
            UserNotFoundError: If user not found
            StorageError: If account lock fails
        """
        try:
            # Get user first
            user = await self.storage.get_user(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            # Calculate lock expiry
            locked_until = None
            if duration:
                locked_until = datetime.utcnow() + timedelta(seconds=duration)

            # Update user
            await self.update_user(
                user_id,
                UserUpdate(
                    status="locked",
                    locked_until=locked_until
                )
            )

            # Publish security event
            await publish_security_event(
                self.message_hub,
                "account_locked",
                {
                    "user_id": str(user_id),
                    "duration": duration,
                    "reason": reason or "manual_lock"
                }
            )

            logger.info(
                "Locked user account",
                extra={
                    "user_id": str(user_id),
                    "duration": duration,
                    "reason": reason
                }
            )

        except UserNotFoundError:
            raise

        except Exception as e:
            logger.error(
                "Failed to lock account",
                extra={
                    "error": str(e),
                    "user_id": str(user_id)
                }
            )
            raise StorageError(str(e))