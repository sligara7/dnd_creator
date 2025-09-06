"""Utility functions for the image service."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def generate_uuid() -> UUID:
    """Generate a new UUID."""
    return uuid4()


def build_cache_key(*parts: Any) -> str:
    """Build a cache key from parts."""
    return ":".join(str(part) for part in parts if part is not None)


def parse_size_string(size: str) -> tuple[int, int]:
    """Parse a size string (e.g., '1024x768') into a tuple of integers."""
    try:
        width, height = map(int, size.split("x"))
        return width, height
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid size string: {size}. Expected format: WIDTHxHEIGHT") from e


def format_duration_ms(ms: int) -> str:
    """Format milliseconds into a human-readable string."""
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    seconds = seconds % 60
    return f"{int(minutes)}m {int(seconds)}s"


def check_image_dimensions(width: int, height: int) -> None:
    """Validate image dimensions."""
    if not (32 <= width <= 4096 and 32 <= height <= 4096):
        raise ValueError(
            "Image dimensions must be between 32 and 4096 pixels"
        )
    
    # Check aspect ratio (max 2:1 in either direction)
    aspect_ratio = width / height
    if not (0.5 <= aspect_ratio <= 2.0):
        raise ValueError(
            "Image aspect ratio must be between 1:2 and 2:1"
        )


class LocationBase(BaseModel):
    """Base model for locations."""
    x: int
    y: int


class SizeBase(BaseModel):
    """Base model for sizes."""
    width: int
    height: int
    
    def __init__(self, **data):
        super().__init__(**data)
        check_image_dimensions(self.width, self.height)


class ColorBase(BaseModel):
    """Base model for colors."""
    hex: str
    opacity: Optional[float] = 1.0


def parse_color(color: str) -> ColorBase:
    """Parse a color string into a ColorBase model."""
    if color.startswith("#"):
        hex_value = color
        opacity = 1.0
    elif color.startswith("rgba"):
        try:
            r, g, b, a = map(float, color[5:-1].split(","))
            hex_value = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            opacity = a
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid rgba color format: {color}") from e
    else:
        raise ValueError(f"Unsupported color format: {color}")
    
    return ColorBase(hex=hex_value, opacity=opacity)


class GridConfig(BaseModel):
    """Configuration for map grids."""
    size: int
    color: ColorBase
    enabled: bool = True


class ThemeProperties(BaseModel):
    """Theme properties for image generation."""
    color_scheme: str
    lighting: str
    atmosphere: str


class StyleConfig(BaseModel):
    """Configuration for image styles."""
    pose: Optional[str] = None
    background: Optional[str] = None
    lighting: Optional[str] = None
    angle: Optional[str] = None
    detail_level: Optional[str] = None
    

def parse_style_preset(preset: str) -> StyleConfig:
    """Parse a style preset string into a StyleConfig."""
    # TODO: Implement style preset parsing
    raise NotImplementedError("Style preset parsing not implemented")


def get_mimetype_from_url(url: str) -> str:
    """Get mimetype from a URL."""
    ext = url.rsplit(".", 1)[-1].lower()
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
    }.get(ext, "application/octet-stream")
