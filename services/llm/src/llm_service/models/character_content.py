"""Models for character content generation.

This module defines the Pydantic models for character content generation,
including personality traits, background narratives, and character arcs.
"""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CharacterContentType(str, Enum):
    """Types of character content that can be generated."""
    PERSONALITY_TRAITS = "personality_traits"
    BACKGROUND_NARRATIVE = "background_narrative"
    CHARACTER_ARC = "character_arc"


class PersonalityTraits(BaseModel):
    """Model for character personality traits."""
    alignment_traits: Dict[str, str] = Field(
        ...,
        description="Traits related to alignment (lawful/chaotic, good/evil)"
    )
    personality_characteristics: List[str] = Field(
        ...,
        description="List of defining personality characteristics"
    )
    bonds: List[str] = Field(
        ...,
        description="Character's bonds with people, places, or ideals"
    )
    ideals: List[str] = Field(
        ...,
        description="Character's core ideals and beliefs"
    )
    flaws: List[str] = Field(
        ...,
        description="Character's flaws and weaknesses"
    )
    quirks: List[str] = Field(
        ...,
        description="Unique quirks and mannerisms"
    )


class BackgroundNarrative(BaseModel):
    """Model for character background narrative."""
    early_life: str = Field(
        ...,
        description="Character's early life experiences"
    )
    defining_events: List[str] = Field(
        ...,
        description="Major events that shaped the character"
    )
    relationships: Dict[str, str] = Field(
        ...,
        description="Key relationships and their impact"
    )
    motivations: List[str] = Field(
        ...,
        description="Character's primary motivations"
    )
    secrets: Optional[List[str]] = Field(
        default=None,
        description="Character's secrets (if any)"
    )


class CharacterArc(BaseModel):
    """Model for character development arcs."""
    current_state: str = Field(
        ...,
        description="Character's current developmental state"
    )
    potential_developments: List[str] = Field(
        ...,
        description="Potential character development paths"
    )
    growth_opportunities: List[str] = Field(
        ...,
        description="Opportunities for character growth"
    )
    challenges: List[str] = Field(
        ...,
        description="Personal challenges to overcome"
    )
    arc_themes: List[str] = Field(
        ...,
        description="Major themes in the character's development"
    )


class CharacterContentRequest(BaseModel):
    """Request model for character content generation."""
    content_type: CharacterContentType
    character_data: Dict[str, any] = Field(
        ...,
        description="Character data for content generation"
    )
    theme_context: Optional[Dict[str, any]] = Field(
        default=None,
        description="Theme context for content generation"
    )
    campaign_context: Optional[Dict[str, any]] = Field(
        default=None,
        description="Campaign context for content generation"
    )


class CharacterContentResponse(BaseModel):
    """Response model for character content generation."""
    content_type: CharacterContentType
    content: Dict[str, any] = Field(
        ...,
        description="Generated character content"
    )
    metadata: Dict[str, any] = Field(
        default_factory=dict,
        description="Additional generation metadata"
    )