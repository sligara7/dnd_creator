"""Models for text generation requests and responses."""
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class TextGenerationType(str, Enum):
    """Types of text content that can be generated."""
    BACKSTORY = "backstory"
    PERSONALITY = "personality"
    COMBAT = "combat"
    EQUIPMENT = "equipment"


class ModelConfig(BaseModel):
    """LLM model configuration."""
    name: str = Field(default="gpt-4-turbo", description="The model to use")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=1000,
        gt=0,
        description="Maximum tokens to generate"
    )


class ThemeConfig(BaseModel):
    """Theme configuration for content generation."""
    genre: str = Field(..., description="Genre of content")
    tone: str = Field(..., description="Tone of content")
    style: str = Field(..., description="Writing style")


class CharacterParameters(BaseModel):
    """Parameters for character content generation."""
    character_class: str = Field(..., description="Character's class")
    character_race: str = Field(..., description="Character's race")
    character_level: int = Field(
        ...,
        gt=0,
        le=20,
        description="Character's level"
    )
    alignment: str = Field(..., description="Character's alignment")
    background: str = Field(..., description="Character's background")


class TextGenerationRequest(BaseModel):
    """Request model for text generation.

    Aligns with ICD specification for /api/v2/text/character endpoint.
    """
    type: TextGenerationType = Field(
        ...,
        description="Type of content to generate"
    )
    parameters: CharacterParameters = Field(
        ...,
        description="Character parameters"
    )
    theme: Optional[ThemeConfig] = Field(
        default=None,
        description="Theme configuration"
    )
    model: Optional[ModelConfig] = Field(
        default=None,
        description="Model configuration"
    )


class TextGenerationResponse(BaseModel):
    """Response model for text generation.

    Aligns with ICD specification for text generation responses.
    """
    request_id: str = Field(..., description="Unique request ID")
    type: TextGenerationType = Field(..., description="Type of content generated")
    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Model used for generation")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )