"""Integration package for auth service."""
from auth.integration.event_handlers import setup_event_handlers
from auth.integration.message_hub import (
    MessageHubClient,
    publish_user_created,
    publish_login_event,
    publish_role_change,
    publish_security_event,
)

__all__ = [
    "MessageHubClient",
    "setup_event_handlers",
    "publish_user_created",
    "publish_login_event",
    "publish_role_change",
    "publish_security_event",
]