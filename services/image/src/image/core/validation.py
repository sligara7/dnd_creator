"""Validation utilities for image service."""
import logging
from typing import List, Optional, Set, Tuple
from uuid import UUID

from fastapi import HTTPException, status

from image.core.errors import (
    InvalidThemeError,
    OverlayError,
    PermissionError,
    ThemeError
)

logger = logging.getLogger(__name__)


def validate_image_dimensions(
    width: int,
    height: int,
    max_width: int = 4096,
    max_height: int = 4096,
    min_width: int = 32,
    min_height: int = 32
) -> None:
    """Validate image dimensions.

    Args:
        width: Image width
        height: Image height
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        min_width: Minimum allowed width
        min_height: Minimum allowed height

    Raises:
        HTTPException: If dimensions are invalid
    """
    if width < min_width or height < min_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Image dimensions must be at least "
                f"{min_width}x{min_height} pixels"
            )
        )

    if width > max_width or height > max_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Image dimensions cannot exceed "
                f"{max_width}x{max_height} pixels"
            )
        )

    # Validate aspect ratio
    ratio = width / height
    if ratio < 0.25 or ratio > 4.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image aspect ratio must be between 1:4 and 4:1"
        )


def validate_theme_name(theme: str, available_themes: Set[str]) -> None:
    """Validate theme name.

    Args:
        theme: Theme name
        available_themes: Set of valid theme names

    Raises:
        InvalidThemeError: If theme is invalid
    """
    if theme not in available_themes:
        raise InvalidThemeError(theme)


def validate_theme_elements(
    elements: List[str],
    available_elements: Set[str]
) -> None:
    """Validate theme elements.

    Args:
        elements: List of theme elements
        available_elements: Set of valid element names

    Raises:
        ThemeError: If elements are invalid
    """
    invalid = [e for e in elements if e not in available_elements]
    if invalid:
        raise ThemeError(
            message=f"Invalid theme elements: {', '.join(invalid)}",
            field="elements"
        )


def validate_grid_config(
    size: int,
    min_size: int = 16,
    max_size: int = 128
) -> None:
    """Validate grid configuration.

    Args:
        size: Grid cell size
        min_size: Minimum cell size
        max_size: Maximum cell size

    Raises:
        HTTPException: If grid config is invalid
    """
    if size < min_size or size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Grid cell size must be between "
                f"{min_size} and {max_size} pixels"
            )
        )

    if size % 8 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grid cell size must be a multiple of 8 pixels"
        )


def validate_overlay_coordinates(
    coordinates: List[Tuple[int, int]],
    image_width: int,
    image_height: int
) -> None:
    """Validate overlay coordinates.

    Args:
        coordinates: List of (x, y) coordinates
        image_width: Width of target image
        image_height: Height of target image

    Raises:
        OverlayError: If coordinates are invalid
    """
    for x, y in coordinates:
        if x < 0 or x >= image_width or y < 0 or y >= image_height:
            raise OverlayError(
                message=(
                    f"Coordinates ({x}, {y}) out of bounds "
                    f"for {image_width}x{image_height} image"
                ),
                field="coordinates"
            )


def validate_api_key(
    api_key: Optional[str],
    required_scope: str
) -> None:
    """Validate API key and scope.

    Args:
        api_key: API key from request
        required_scope: Required API scope

    Raises:
        PermissionError: If key is invalid or lacks scope
    """
    if not api_key:
        raise PermissionError("Missing API key")

    # Placeholder for actual key validation
    # In production, validate key with auth service
    if not api_key.startswith("valid_"):
        raise PermissionError("Invalid API key")

    # Placeholder for scope validation
    scopes = ["read", "write"]  # Get from auth service
    if required_scope not in scopes:
        raise PermissionError(
            f"API key lacks required scope: {required_scope}"
        )


def validate_content_type(
    content_type: str,
    allowed_types: Set[str]
) -> None:
    """Validate content type.

    Args:
        content_type: Content type header
        allowed_types: Set of allowed MIME types

    Raises:
        HTTPException: If content type is not allowed
    """
    if not content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Content-Type header"
        )

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported content type. "
                f"Allowed types: {', '.join(allowed_types)}"
            )
        )
