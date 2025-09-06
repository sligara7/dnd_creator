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
