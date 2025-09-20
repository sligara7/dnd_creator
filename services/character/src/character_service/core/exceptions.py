"""Core exceptions."""


class ValidationError(Exception):
    """Validation error."""

    pass


class InventoryError(Exception):
    """Inventory error."""

    pass


class EvolutionError(Exception):
    """Evolution error."""

    pass


class ResourceExhaustedError(Exception):
    """Resource exhausted error."""

    pass


class StateError(Exception):
    """State error."""

    pass


class CharacterNotFoundError(Exception):
    """Raised when a character is not found."""

    pass


class StorageOperationError(Exception):
    """Raised when a storage service operation fails."""

    pass


class EventNotFoundError(Exception):
    """Raised when an event is not found."""

    pass


class EventApplicationError(Exception):
    """Raised when an event fails to apply."""

    pass


class MessageHubError(Exception):
    """Raised when there's an error communicating with Message Hub."""

    pass


class MessageValidationError(Exception):
    """Raised when a message fails validation."""

    pass


class StateConflictError(Exception):
    """Raised when there's a conflict during state synchronization."""

    pass
