from enum import Enum
from typing import Dict, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from llm_service.schemas.common import ContentMetadata, JobResult, Theme


class ModelType(str, Enum):
    """Available OpenAI models."""
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"


class TextType(str, Enum):
    """Type of text content to generate."""
    CHARACTER_BACKSTORY = "backstory"
    CHARACTER_PERSONALITY = "personality"
    CHARACTER_COMBAT = "combat"
    CHARACTER_EQUIPMENT = "equipment"
    CAMPAIGN_PLOT = "plot"
    CAMPAIGN_LOCATION = "location"
    CAMPAIGN_QUEST = "quest"
    CAMPAIGN_DIALOGUE = "dialogue"
    CAMPAIGN_EVENT = "event"


class ModelConfig(BaseModel):
    """Configuration for text generation model."""
    name: ModelType = Field(ModelType.GPT_4_TURBO, description="Model to use for generation")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(1000, gt=0, description="Maximum tokens to generate")
    fallback_model: Optional[ModelType] = Field(
        ModelType.GPT_35_TURBO,
        description="Fallback model to use if primary model fails"
    )
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")


class CharacterContext(BaseModel):
    """Context for character-related text generation."""
    character_class: str = Field(description="Character's class")
    character_race: str = Field(description="Character's race")
    character_level: int = Field(ge=1, le=20, description="Character's level")
    alignment: str = Field(description="Character's alignment")
    background: str = Field(description="Character's background")


class CampaignContext(BaseModel):
    """Context for campaign-related text generation."""
    campaign_theme: str = Field(description="Overall theme of the campaign")
    party_level: int = Field(ge=1, le=20, description="Average party level")
    party_size: int = Field(ge=1, description="Number of players in the party")
    duration: str = Field(description="Expected duration (e.g., oneshot, short, long)")


class TextGenerationRequest(BaseModel):
    """Request for text content generation."""
    type: TextType = Field(description="Type of text content to generate")
    theme: Theme = Field(description="Theme configuration for generation")
    model: ModelConfig = Field(default_factory=ModelConfig)
    character_context: Optional[CharacterContext] = Field(None, description="Character-specific context")
    campaign_context: Optional[CampaignContext] = Field(None, description="Campaign-specific context")
    additional_context: Optional[Dict] = Field(default_factory=dict)
    parent_content_id: Optional[UUID] = None

    @model_validator(mode="after")
    def validate_context(self):
        """Validate that appropriate context is provided."""
        if self.type.value.startswith("character_") and not self.character_context:
            raise ValueError("character_context required for character content")
        if self.type.value.startswith("campaign_") and not self.campaign_context:
            raise ValueError("campaign_context required for campaign content")
        return self


class GeneratedText(BaseModel):
    """Generated text content."""
    content: str = Field(description="Generated text content")
    metadata: ContentMetadata = Field(description="Content generation metadata")
    content_id: UUID = Field(description="Unique identifier for the content")
    parent_content_id: Optional[UUID] = None


class TextGenerationResponse(BaseModel):
    """Response containing generated text."""
    result: GeneratedText
    alternative_results: Optional[list[GeneratedText]] = None


class TextJobResult(JobResult[GeneratedText]):
    """Result of a text generation job."""
    pass
