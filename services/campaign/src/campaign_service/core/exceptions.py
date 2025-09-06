"""Core exceptions for the campaign service."""


class CampaignServiceError(Exception):
    """Base exception for campaign service errors."""

    pass


class ThemeNotFoundError(CampaignServiceError):
    """Raised when a requested theme cannot be found."""

    pass


class ThemeValidationError(CampaignServiceError):
    """Raised when theme validation fails."""

    pass


class ChapterNotFoundError(CampaignServiceError):
    """Raised when a requested chapter cannot be found."""

    pass


class CampaignNotFoundError(CampaignServiceError):
    """Raised when a requested campaign cannot be found."""

    pass


class ValidationError(CampaignServiceError):
    """Raised when validation fails."""

    pass


class GenerationError(CampaignServiceError):
    """Raised when content generation fails."""

    pass


class IntegrationError(CampaignServiceError):
    """Raised when service integration fails."""

    pass


class StateError(CampaignServiceError):
    """Raised when an operation is invalid for the current state."""

    pass


class VersionControlError(CampaignServiceError):
    """Raised when version control operation fails."""

    pass


class StoryManagementError(CampaignServiceError):
    """Raised when story management operation fails."""

    pass


class MergeConflictError(VersionControlError):
    """Raised when branch merge conflicts occur."""

    pass
