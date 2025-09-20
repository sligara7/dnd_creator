"""Pydantic schemas for image storage service."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base models
class BaseSchema(BaseModel):
    """Base schema with common fields."""

    class Config:
        """Pydantic config."""

        orm_mode = True


# Image schemas
class ImageBase(BaseSchema):
    """Base image schema."""

    type: str
    subtype: str
    name: str
    description: Optional[str] = None
    url: str
    format: str = "png"
    width: int
    height: int
    size: int
    theme: str
    style_data: Optional[Dict[str, Any]] = None
    generation_params: Optional[Dict[str, Any]] = None
    source_id: Optional[UUID] = None
    source_type: Optional[str] = None


class ImageCreate(ImageBase):
    """Schema for creating an image."""

    pass


class ImageUpdate(BaseSchema):
    """Schema for updating an image."""

    name: Optional[str] = None
    description: Optional[str] = None
    style_data: Optional[Dict[str, Any]] = None
    generation_params: Optional[Dict[str, Any]] = None


class ImageResponse(ImageBase):
    """Schema for image response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Image overlay schemas
class ImageOverlayBase(BaseSchema):
    """Base image overlay schema."""

    image_id: UUID
    type: str
    name: str
    description: Optional[str] = None
    data: Dict[str, Any]
    style: Dict[str, Any]


class ImageOverlayCreate(ImageOverlayBase):
    """Schema for creating an image overlay."""

    pass


class ImageOverlayUpdate(BaseSchema):
    """Schema for updating an image overlay."""

    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None


class ImageOverlayResponse(ImageOverlayBase):
    """Schema for image overlay response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Map grid schemas
class MapGridBase(BaseSchema):
    """Base map grid schema."""

    image_id: UUID
    enabled: bool = True
    size: int = Field(default=50, ge=1)
    color: str = "#000000"
    opacity: float = Field(default=0.5, ge=0.0, le=1.0)


class MapGridCreate(MapGridBase):
    """Schema for creating a map grid."""

    pass


class MapGridUpdate(BaseSchema):
    """Schema for updating a map grid."""

    enabled: Optional[bool] = None
    size: Optional[int] = Field(default=None, ge=1)
    color: Optional[str] = None
    opacity: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MapGridResponse(MapGridBase):
    """Schema for map grid response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Generation task schemas
class GenerationTaskBase(BaseSchema):
    """Base generation task schema."""

    type: str
    status: str
    priority: int
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    attempts: int = 0
    last_error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 5


class GenerationTaskCreate(GenerationTaskBase):
    """Schema for creating a generation task."""

    pass


class GenerationTaskUpdate(BaseSchema):
    """Schema for updating a generation task."""

    status: Optional[str] = None
    priority: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    attempts: Optional[int] = None
    last_error: Optional[str] = None
    retry_count: Optional[int] = None


class GenerationTaskResponse(GenerationTaskBase):
    """Schema for generation task response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_attempt: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Theme schemas
class ThemeBase(BaseSchema):
    """Base theme schema."""

    name: str
    display_name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    variables: Dict[str, Any]
    prompts: Dict[str, Any]
    styles: Dict[str, Any]


class ThemeCreate(ThemeBase):
    """Schema for creating a theme."""

    pass


class ThemeUpdate(BaseSchema):
    """Schema for updating a theme."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    styles: Optional[Dict[str, Any]] = None


class ThemeResponse(ThemeBase):
    """Schema for theme response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Theme variation schemas
class ThemeVariationBase(BaseSchema):
    """Base theme variation schema."""

    name: str
    display_name: str
    description: Optional[str] = None
    config_override: Dict[str, Any]
    variable_override: Dict[str, Any]


class ThemeVariationCreate(ThemeVariationBase):
    """Schema for creating a theme variation."""

    pass


class ThemeVariationUpdate(BaseSchema):
    """Schema for updating a theme variation."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    config_override: Optional[Dict[str, Any]] = None
    variable_override: Optional[Dict[str, Any]] = None


class ThemeVariationResponse(ThemeVariationBase):
    """Schema for theme variation response."""

    id: UUID
    theme_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Style preset schemas
class StylePresetBase(BaseSchema):
    """Base style preset schema."""

    name: str
    display_name: str
    description: Optional[str] = None
    category: str
    config: Dict[str, Any]
    prompts: Dict[str, Any]
    compatibility: List[str]


class StylePresetCreate(StylePresetBase):
    """Schema for creating a style preset."""

    pass


class StylePresetUpdate(BaseSchema):
    """Schema for updating a style preset."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    compatibility: Optional[List[str]] = None


class StylePresetResponse(StylePresetBase):
    """Schema for style preset response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


# Theme element schemas
class ThemeElementBase(BaseSchema):
    """Base theme element schema."""

    category: str
    name: str
    display_name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    prompts: Dict[str, Any]
    compatibility: List[str]


class ThemeElementCreate(ThemeElementBase):
    """Schema for creating a theme element."""

    pass


class ThemeElementUpdate(BaseSchema):
    """Schema for updating a theme element."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    compatibility: Optional[List[str]] = None


class ThemeElementResponse(ThemeElementBase):
    """Schema for theme element response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False