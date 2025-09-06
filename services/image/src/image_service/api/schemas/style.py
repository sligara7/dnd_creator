"""Style and theme schemas for the API."""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from image_service.core.utils import ColorBase, SizeBase, ThemeProperties


class StyleElement(BaseModel):
    """Style element configuration."""
    category: str = Field(description="Element category (e.g., architecture, clothing)")
    name: str = Field(description="Element identifier")
    display_name: str = Field(description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Element description")
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Element importance weight (0.0-2.0)",
    )
    modifiers: Dict[str, float] = Field(
        default_factory=dict,
        description="Style modifiers",
    )


class StylePreset(BaseModel):
    """Style preset configuration."""
    name: str = Field(description="Preset identifier")
    display_name: str = Field(description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Preset description")
    category: str = Field(description="Preset category")
    elements: List[StyleElement] = Field(description="Style elements")
    compatibility: List[str] = Field(description="Compatible themes")


class Theme(BaseModel):
    """Theme configuration."""
    name: str = Field(description="Theme identifier")
    display_name: str = Field(description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Theme description")
    base_theme: Optional[str] = Field(
        default=None,
        description="Parent theme for inheritance",
    )
    properties: ThemeProperties = Field(description="Theme visual properties")
    elements: List[StyleElement] = Field(description="Theme style elements")


class ThemeVariation(BaseModel):
    """Theme variation configuration."""
    theme_id: UUID = Field(description="Parent theme ID")
    name: str = Field(description="Variation identifier")
    display_name: str = Field(description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Variation description")
    property_overrides: Dict[str, str] = Field(
        default_factory=dict,
        description="Theme property overrides",
    )
    element_overrides: List[StyleElement] = Field(
        default_factory=list,
        description="Style element overrides",
    )


class StyleRequest(BaseModel):
    """Style application request."""
    theme: str = Field(description="Theme to apply")
    style_preset: Optional[str] = Field(
        default=None,
        description="Style preset to use",
    )
    elements: List[str] = Field(
        default_factory=list,
        description="Style elements to include",
    )
    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Style application strength (0.0-2.0)",
    )
    properties: Optional[ThemeProperties] = Field(
        default=None,
        description="Theme property overrides",
    )


class ModifyRequest(BaseModel):
    """Image modification request."""
    image_id: UUID = Field(description="Image to modify")
    style: StyleRequest = Field(description="Style to apply")
    size: Optional[SizeBase] = Field(
        default=None,
        description="Target size (if resizing)",
    )
    preserve_content: bool = Field(
        default=True,
        description="Preserve original content",
    )


class StyleResponse(BaseModel):
    """Style application response."""
    image_id: UUID = Field(description="Modified image ID")
    original_id: UUID = Field(description="Original image ID")
    style: StyleRequest = Field(description="Applied style")
    url: str = Field(description="Modified image URL")
    metadata: Dict[str, Any] = Field(description="Style metadata")


class ThemeList(BaseModel):
    """Available themes response."""
    visual_themes: List[str] = Field(description="Available visual themes")
    style_elements: Dict[str, List[str]] = Field(
        description="Available style elements by category",
    )
    compatibility: Dict[str, List[str]] = Field(
        description="Theme compatibility matrix",
    )
