"""Service layer for character content generation.

This module provides services for generating character content, including
personality traits, background narratives, and character arcs.
"""
from typing import Any, Dict, List, Optional

from ..core.config import Settings
from ..core.exceptions import ContentGenerationError
from ..models.character_content import (
    BackgroundNarrative,
    CharacterArc,
    CharacterContentType,
    PersonalityTraits,
)
from ..providers.openai import OpenAIProvider
from ..services.theme import ThemeService


class CharacterContentService:
    """Service for generating character content."""

    def __init__(
        self,
        settings: Settings,
        openai_provider: OpenAIProvider,
        theme_service: Optional[ThemeService] = None
    ):
        self.settings = settings
        self.openai_provider = openai_provider
        self.theme_service = theme_service or ThemeService(settings)

    async def generate_personality_traits(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> PersonalityTraits:
        """Generate personality traits for a character."""
        try:
            # Generate prompt for personality traits
            prompt = self._build_personality_prompt(
                character_data,
                theme_context,
                campaign_context
            )

            # Generate content using OpenAI
            content = await self.openai_provider.generate_text(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
            )

            # Parse and validate response
            personality_traits = self._parse_personality_traits(content)
            
            return personality_traits
            
        except Exception as e:
            raise ContentGenerationError(
                f"Failed to generate personality traits: {str(e)}"
            )

    async def generate_background_narrative(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> BackgroundNarrative:
        """Generate background narrative for a character."""
        try:
            # Generate prompt for background narrative
            prompt = self._build_background_prompt(
                character_data,
                theme_context,
                campaign_context
            )

            # Generate content using OpenAI
            content = await self.openai_provider.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.8,
            )

            # Parse and validate response
            background_narrative = self._parse_background_narrative(content)
            
            return background_narrative
            
        except Exception as e:
            raise ContentGenerationError(
                f"Failed to generate background narrative: {str(e)}"
            )

    async def generate_character_arc(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> CharacterArc:
        """Generate a character development arc."""
        try:
            # Generate prompt for character arc
            prompt = self._build_arc_prompt(
                character_data,
                theme_context,
                campaign_context
            )

            # Generate content using OpenAI
            content = await self.openai_provider.generate_text(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,
            )

            # Parse and validate response
            character_arc = self._parse_character_arc(content)
            
            return character_arc
            
        except Exception as e:
            raise ContentGenerationError(
                f"Failed to generate character arc: {str(e)}"
            )

    def _build_personality_prompt(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for personality trait generation."""
        # Extract relevant character data
        race = character_data.get("race", "")
        class_name = character_data.get("class", "")
        background = character_data.get("background", "")

        # Build base prompt
        prompt = f"""Generate personality traits for a D&D character with the following details:
Race: {race}
Class: {class_name}
Background: {background}

Consider the character's background story and provide:
1. Alignment-related traits and tendencies
2. Distinctive personality characteristics
3. Strong bonds with people, places, or ideals
4. Core ideals and beliefs
5. Notable flaws or weaknesses
6. Unique quirks or mannerisms

Format the response as a JSON object with the following structure:
{{
    "alignment_traits": {{ "description of alignment tendencies" }},
    "personality_characteristics": ["trait 1", "trait 2", ...],
    "bonds": ["bond 1", "bond 2", ...],
    "ideals": ["ideal 1", "ideal 2", ...],
    "flaws": ["flaw 1", "flaw 2", ...],
    "quirks": ["quirk 1", "quirk 2", ...]
}}"""

        # Add theme context if provided
        if theme_context:
            prompt += f"\n\nConsider the following theme context:\n{theme_context}"

        # Add campaign context if provided
        if campaign_context:
            prompt += f"\n\nConsider the following campaign context:\n{campaign_context}"

        return prompt

    def _build_background_prompt(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for background narrative generation."""
        # Extract relevant character data
        race = character_data.get("race", "")
        class_name = character_data.get("class", "")
        background = character_data.get("background", "")

        # Build base prompt
        prompt = f"""Generate a background narrative for a D&D character with the following details:
Race: {race}
Class: {class_name}
Background: {background}

Provide a comprehensive background story including:
1. Early life experiences and upbringing
2. Defining events that shaped the character
3. Key relationships and their impact
4. Core motivations and driving forces
5. Any significant secrets or hidden aspects

Format the response as a JSON object with the following structure:
{{
    "early_life": "detailed description",
    "defining_events": ["event 1", "event 2", ...],
    "relationships": {{"person/group": "relationship description"}},
    "motivations": ["motivation 1", "motivation 2", ...],
    "secrets": ["secret 1", "secret 2", ...]
}}"""

        # Add theme context if provided
        if theme_context:
            prompt += f"\n\nConsider the following theme context:\n{theme_context}"

        # Add campaign context if provided
        if campaign_context:
            prompt += f"\n\nConsider the following campaign context:\n{campaign_context}"

        return prompt

    def _build_arc_prompt(
        self,
        character_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]] = None,
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for character arc generation."""
        # Extract relevant character data
        race = character_data.get("race", "")
        class_name = character_data.get("class", "")
        background = character_data.get("background", "")

        # Build base prompt
        prompt = f"""Generate a character development arc for a D&D character with the following details:
Race: {race}
Class: {class_name}
Background: {background}

Outline potential character development including:
1. Current character state
2. Potential development paths
3. Growth opportunities
4. Personal challenges
5. Major themes in their development

Format the response as a JSON object with the following structure:
{{
    "current_state": "description",
    "potential_developments": ["path 1", "path 2", ...],
    "growth_opportunities": ["opportunity 1", "opportunity 2", ...],
    "challenges": ["challenge 1", "challenge 2", ...],
    "arc_themes": ["theme 1", "theme 2", ...]
}}"""

        # Add theme context if provided
        if theme_context:
            prompt += f"\n\nConsider the following theme context:\n{theme_context}"

        # Add campaign context if provided
        if campaign_context:
            prompt += f"\n\nConsider the following campaign context:\n{campaign_context}"

        return prompt

    def _parse_personality_traits(self, content: str) -> PersonalityTraits:
        """Parse and validate personality traits from generated content."""
        import json
        
        try:
            data = json.loads(content)
            return PersonalityTraits(**data)
        except Exception as e:
            raise ContentGenerationError(f"Failed to parse personality traits: {str(e)}")

    def _parse_background_narrative(self, content: str) -> BackgroundNarrative:
        """Parse and validate background narrative from generated content."""
        import json
        
        try:
            data = json.loads(content)
            return BackgroundNarrative(**data)
        except Exception as e:
            raise ContentGenerationError(f"Failed to parse background narrative: {str(e)}")

    def _parse_character_arc(self, content: str) -> CharacterArc:
        """Parse and validate character arc from generated content."""
        import json
        
        try:
            data = json.loads(content)
            return CharacterArc(**data)
        except Exception as e:
            raise ContentGenerationError(f"Failed to parse character arc: {str(e)}")