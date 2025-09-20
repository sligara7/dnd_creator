"""Campaign service exceptions."""

class CampaignError(Exception):
    """Base exception class for campaign service errors."""
    pass

class PermissionDeniedError(CampaignError):
    """Raised when a user lacks permission for an operation."""
    pass

class ValidationError(CampaignError):
    """Raised when campaign validation fails."""
    pass

class StateTransitionError(CampaignError):
    """Raised when a campaign state transition is invalid."""
    pass

class IntegrationError(CampaignError):
    """Raised when service integration fails."""
    pass

class ThemeError(CampaignError):
    """Raised when theme operations fail."""
    pass