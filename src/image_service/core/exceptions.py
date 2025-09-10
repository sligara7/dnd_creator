"""
Core exceptions for the Image Service.
"""

class ImageServiceError(Exception):
    """Base exception for Image Service errors."""
    pass

class ImageGenerationError(ImageServiceError):
    """Raised when image generation fails."""
    pass

class ImageStorageError(ImageServiceError):
    """Raised when image storage operations fail."""
    pass

class ImageNotFoundError(ImageServiceError):
    """Raised when requested image is not found."""
    pass
