"""State synchronization exceptions."""


class SyncError(Exception):
    """Base class for synchronization errors."""


class SyncConfigurationError(SyncError):
    """Error in synchronization configuration."""


class SyncStateError(SyncError):
    """Error in synchronization state."""


class SyncConflictError(SyncError):
    """Synchronization conflict detected."""


class SyncConnectionError(SyncError):
    """Error connecting to campaign service."""


class SyncTimeoutError(SyncError):
    """Synchronization timeout occurred."""


class SyncVersionError(SyncError):
    """Error with state version management."""


class SyncSubscriptionError(SyncError):
    """Error managing sync subscriptions."""


class SyncMessageError(SyncError):
    """Error processing sync messages."""


class SyncRetryError(SyncError):
    """Maximum retry attempts exceeded."""
