"""Theme-aware generation pipeline models."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ThemeType(str, Enum):
    """Type of theme for content generation."""
    TRADITIONAL = "traditional"
    ANTITHETICON = "antitheticon"


class ThemeGenre(str, Enum):
    """Genre classification for themes."""
    FANTASY = "fantasy"
    DARK_FANTASY = "dark_fantasy"
    HIGH_FANTASY = "high_fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"
    POLITICAL = "political"


class ThemeTone(str, Enum):
    """Tone classification for themes."""
    SERIOUS = "serious"
    LIGHT = "light"
    DRAMATIC = "dramatic"
    COMEDIC = "comedic"
    GRITTY = "gritty"
    EPIC = "epic"


class ThemeElements(BaseModel):
    """Core elements that define a theme's characteristics."""
    key_words: List[str] = Field(
        description="Key words that characterize the theme"
    )
    excluded_words: List[str] = Field(
        default_list=[],
        description="Words to explicitly avoid in generation"
    )
    style_guide: Dict[str, str] = Field(
        description="Style guidelines for content generation"
    )
    character_traits: List[str] = Field(
        description="Common character traits for this theme"
    )
    world_elements: List[str] = Field(
        description="Defining world/setting elements"
    )


class ThemeContext(BaseModel):
    """Context information for theme-aware generation."""
    theme_id: UUID = Field(description="Unique identifier for the theme")
    name: str = Field(description="Theme name")
    type: ThemeType = Field(description="Theme type classification")
    genre: ThemeGenre = Field(description="Primary genre")
    sub_genres: List[ThemeGenre] = Field(
        default_list=[],
        description="Additional genre influences"
    )
    tone: ThemeTone = Field(description="Primary tone")
    elements: ThemeElements = Field(description="Theme elements and characteristics")
    parent_theme_id: Optional[UUID] = Field(
        default=None,
        description="Parent theme ID for derived themes"
    )


class ContentType(str, Enum):
    """Types of content that can be generated."""
    CHARACTER_BACKSTORY = "character_backstory"
    NPC_DIALOGUE = "npc_dialogue"
    LOCATION_DESCRIPTION = "location_description"
    ITEM_DESCRIPTION = "item_description"
    COMBAT_NARRATIVE = "combat_narrative"
    QUEST_DESCRIPTION = "quest_description"
    PLOT_DEVELOPMENT = "plot_development"


class GenerationConfig(BaseModel):
    """Configuration for content generation."""
    model: str = Field(
        default="gpt-5-nano",
        description="Model to use for generation"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Randomness in generation"
    )
    max_tokens: int = Field(
        default=1000,
        gt=0,
        description="Maximum tokens to generate"
    )
    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Penalty for token presence"
    )
    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Penalty for token frequency"
    )
    stop_sequences: List[str] = Field(
        default_list=[],
        description="Sequences that stop generation"
    )
    stream_tokens: bool = Field(
        default=True,
        description="Whether to stream tokens"
    )


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    prompt_tokens: int = Field(description="Number of tokens in prompt")
    completion_tokens: int = Field(description="Number of generated tokens")
    total_tokens: int = Field(description="Total tokens used")
    generation_time_ms: int = Field(description="Time taken for generation")
    model_name: str = Field(description="Model used for generation")
    cached: bool = Field(description="Whether result was from cache")


class GenerationResult(BaseModel):
    """Result of content generation."""
    content: str = Field(description="Generated content")
    metadata: GenerationMetadata = Field(description="Generation metadata")
    theme_context: ThemeContext = Field(description="Theme context used")
    content_type: ContentType = Field(description="Type of content generated")
