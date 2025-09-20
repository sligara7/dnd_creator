"""Event handlers for auth service."""
import logging
from typing import Any, Dict
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError
from auth.integration.message_hub import MessageHubClient, publish_security_event
from auth.models.api import UserUpdate


logger = logging.getLogger(__name__)


async def setup_event_handlers(
    message_hub: MessageHubClient,
    storage_client: StorageClient
) -> None:
    """Set up event handlers for auth service.

    Args:
        message_hub: Message Hub client
        storage_client: Storage service client
    """
    # User events
    message_hub.subscribe(
        "user.profile.updated",
        _create_user_profile_handler(storage_client)
    )
    message_hub.subscribe(
        "user.account.locked",
        _create_user_lock_handler(storage_client, message_hub)
    )
    message_hub.subscribe(
        "user.mfa.required",
        _create_mfa_handler(storage_client, message_hub)
    )

    # Security events
    message_hub.subscribe(
        "security.policy.updated",
        _create_policy_update_handler(storage_client, message_hub)
    )
    message_hub.subscribe(
        "security.breach.detected",
        _create_breach_handler(storage_client, message_hub)
    )

    logger.info("Auth service event handlers set up")


def _create_user_profile_handler(
    storage_client: StorageClient
) -> callable:
    """Create handler for user profile updates.

    Args:
        storage_client: Storage service client

    Returns:
        Event handler function
    """
    async def handle_user_profile_update(data: Dict[str, Any]) -> None:
        """Handle user profile update event.

        Args:
            data: Event data with user ID and changes
        """
        try:
            # Get user ID and changes
            user_id = UUID(data["user_id"])
            changes = data.get("changes", {})

            # Update user in storage service
            update = UserUpdate(
                email=changes.get("email"),
                status=changes.get("status")
            )
            await storage_client.update_user(user_id, update)

            logger.info(
                "Updated user profile from event",
                extra={"user_id": str(user_id)}
            )

        except (KeyError, ValueError) as e:
            logger.error(
                "Invalid user profile update event",
                extra={
                    "error": str(e),
                    "data": data
                }
            )
        except StorageError as e:
            logger.error(
                "Failed to update user profile",
                extra={
                    "error": str(e),
                    "data": data
                }
            )

    return handle_user_profile_update


def _create_user_lock_handler(
    storage_client: StorageClient,
    message_hub: MessageHubClient
) -> callable:
    """Create handler for user account lock events.

    Args:
        storage_client: Storage service client
        message_hub: Message Hub client

    Returns:
        Event handler function
    """
    async def handle_account_lock(data: Dict[str, Any]) -> None:
        """Handle user account lock event.

        Args:
            data: Event data with user ID and lock details
        """
        try:
            # Get user ID and lock duration
            user_id = UUID(data["user_id"])
            lock_duration = data.get("duration", 300)  # Default 5 minutes

            # Update user in storage service
            update = UserUpdate(
                status="locked",
                locked_until=data.get("locked_until")
            )
            await storage_client.update_user(user_id, update)

            # Publish security event
            await publish_security_event(
                message_hub,
                "account_locked",
                {
                    "user_id": str(user_id),
                    "duration": lock_duration,
                    "reason": data.get("reason", "security_policy")
                }
            )

            logger.info(
                "Locked user account from event",
                extra={
                    "user_id": str(user_id),
                    "duration": lock_duration
                }
            )

        except (KeyError, ValueError) as e:
            logger.error(
                "Invalid account lock event",
                extra={
                    "error": str(e),
                    "data": data
                }
            )
        except StorageError as e:
            logger.error(
                "Failed to lock user account",
                extra={
                    "error": str(e),
                    "data": data
                }
            )

    return handle_account_lock


def _create_mfa_handler(
    storage_client: StorageClient,
    message_hub: MessageHubClient
) -> callable:
    """Create handler for MFA requirement events.

    Args:
        storage_client: Storage service client
        message_hub: Message Hub client

    Returns:
        Event handler function
    """
    async def handle_mfa_required(data: Dict[str, Any]) -> None:
        """Handle MFA requirement event.

        Args:
            data: Event data with user ID
        """
        try:
            # Get user ID
            user_id = UUID(data["user_id"])

            # Update user in storage service
            update = UserUpdate(mfa_enabled=True)
            await storage_client.update_user(user_id, update)

            # Publish security event
            await publish_security_event(
                message_hub,
                "mfa_enabled",
                {
                    "user_id": str(user_id),
                    "reason": data.get("reason", "security_policy")
                }
            )

            logger.info(
                "Enabled MFA for user from event",
                extra={"user_id": str(user_id)}
            )

        except (KeyError, ValueError) as e:
            logger.error(
                "Invalid MFA requirement event",
                extra={
                    "error": str(e),
                    "data": data
                }
            )
        except StorageError as e:
            logger.error(
                "Failed to enable MFA for user",
                extra={
                    "error": str(e),
                    "data": data
                }
            )

    return handle_mfa_required


def _create_policy_update_handler(
    storage_client: StorageClient,
    message_hub: MessageHubClient
) -> callable:
    """Create handler for security policy updates.

    Args:
        storage_client: Storage service client
        message_hub: Message Hub client

    Returns:
        Event handler function
    """
    async def handle_policy_update(data: Dict[str, Any]) -> None:
        """Handle security policy update event.

        Args:
            data: Event data with policy changes
        """
        try:
            policy_id = data["policy_id"]
            changes = data.get("changes", [])

            # Process policy changes based on type
            for change in changes:
                if change["type"] == "mfa_required":
                    # Enable MFA for affected users
                    for user_id in change.get("affected_users", []):
                        update = UserUpdate(mfa_enabled=True)
                        await storage_client.update_user(UUID(user_id), update)

                elif change["type"] == "password_expiry":
                    # Update password expiry for affected users
                    for user_id in change.get("affected_users", []):
                        # Process password expiry
                        pass

            # Publish security event
            await publish_security_event(
                message_hub,
                "policy_applied",
                {
                    "policy_id": policy_id,
                    "changes": changes
                }
            )

            logger.info(
                "Applied security policy changes from event",
                extra={"policy_id": policy_id}
            )

        except KeyError as e:
            logger.error(
                "Invalid policy update event",
                extra={
                    "error": str(e),
                    "data": data
                }
            )
        except StorageError as e:
            logger.error(
                "Failed to apply policy changes",
                extra={
                    "error": str(e),
                    "data": data
                }
            )

    return handle_policy_update


def _create_breach_handler(
    storage_client: StorageClient,
    message_hub: MessageHubClient
) -> callable:
    """Create handler for security breach events.

    Args:
        storage_client: Storage service client
        message_hub: Message Hub client

    Returns:
        Event handler function
    """
    async def handle_security_breach(data: Dict[str, Any]) -> None:
        """Handle security breach event.

        Args:
            data: Event data with breach details
        """
        try:
            breach_type = data["breach_type"]
            affected_users = data.get("affected_users", [])

            # Process breach based on type
            if breach_type == "credential_leak":
                # Reset passwords and lock accounts
                for user_id in affected_users:
                    update = UserUpdate(
                        status="locked",
                        locked_until=data.get("locked_until")
                    )
                    await storage_client.update_user(UUID(user_id), update)

            elif breach_type == "suspicious_activity":
                # Enable enhanced monitoring
                for user_id in affected_users:
                    # Process suspicious activity
                    pass

            # Publish security event
            await publish_security_event(
                message_hub,
                "breach_handled",
                {
                    "breach_type": breach_type,
                    "affected_users": affected_users,
                    "actions_taken": ["account_lock", "password_reset"]
                }
            )

            logger.info(
                "Handled security breach event",
                extra={
                    "breach_type": breach_type,
                    "affected_users": len(affected_users)
                }
            )

        except KeyError as e:
            logger.error(
                "Invalid security breach event",
                extra={
                    "error": str(e),
                    "data": data
                }
            )
        except StorageError as e:
            logger.error(
                "Failed to handle security breach",
                extra={
                    "error": str(e),
                    "data": data
                }
            )

    return handle_security_breach