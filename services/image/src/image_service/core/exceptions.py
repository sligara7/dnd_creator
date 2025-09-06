"""Core exceptions for the image service."""

from typing import Any, Optional


class ImageServiceError(Exception):
    """Base exception for the image service."""
    
    def __init__(self, message: str, code: str = "IMAGE_SERVICE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(ImageServiceError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class GenerationError(ImageServiceError):
    """Exception raised when image generation fails."""
    
    def __init__(self, message: str, generation_params: Optional[dict[str, Any]] = None):
        super().__init__(message, code="GENERATION_ERROR")
        self.generation_params = generation_params


class StorageError(ImageServiceError):
    """Exception raised for storage-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, code="STORAGE_ERROR")
        self.operation = operation


class CacheError(ImageServiceError):
    """Exception raised for cache-related errors."""
    
    def __init__(self, message: str, key: Optional[str] = None):
        super().__init__(message, code="CACHE_ERROR")
        self.key = key


class QueueError(ImageServiceError):
    """Exception raised for queue-related errors."""
    
    def __init__(self, message: str, queue_name: Optional[str] = None):
        super().__init__(message, code="QUEUE_ERROR")
        self.queue_name = queue_name


class ThemeError(ImageServiceError):
    """Exception raised for theme-related errors."""
    
    def __init__(self, message: str, theme: Optional[str] = None):
        super().__init__(message, code="THEME_ERROR")
        self.theme = theme


class OverlayError(ImageServiceError):
    """Exception raised for overlay-related errors."""
    
    def __init__(self, message: str, overlay_id: Optional[str] = None):
        super().__init__(message, code="OVERLAY_ERROR")
        self.overlay_id = overlay_id


class ImageNotFoundError(ImageServiceError):
    """Exception raised when an image is not found."""
    
    def __init__(self, message: str, image_id: str):
        super().__init__(message, code="IMAGE_NOT_FOUND")
        self.image_id = image_id


class MessageHubError(ImageServiceError):
    """Exception raised for Message Hub-related errors."""
    
    def __init__(self, message: str, event_type: Optional[str] = None):
        super().__init__(message, code="MESSAGE_HUB_ERROR")
        self.event_type = event_type
