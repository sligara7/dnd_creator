"""Character service integration layer."""
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
import structlog
from pydantic import BaseModel, Field

from ..core.config import Settings
from ..core.exceptions import IntegrationError
from ..models.theme import ContentType, ThemeContext


class CharacterEventType(str, Enum):
    """Types of character events."""
    BACKSTORY_GENERATED = "backstory_generated"
    TRAITS_UPDATED = "traits_updated"
    NARRATIVE_ADDED = "narrative_added"
    THEME_VALIDATED = "theme_validated"
    THEME_TRANSITIONED = "theme_transitioned"


class CharacterContent(BaseModel):
    """Character content for generation."""
    character_id: UUID = Field(description="Character ID")
    content_type: ContentType = Field(description="Type of content")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for generation"
    )
    existing_content: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Existing character content"
    )
    requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Generation requirements"
    )


class CharacterEvent(BaseModel):
    """Event from Character service."""
    event_type: CharacterEventType = Field(description="Type of event")
    character_id: UUID = Field(description="Character ID")
    data: Dict[str, Any] = Field(description="Event data")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context if relevant"
    )


class CharacterService:
    """Service for interacting with Character service."""
    
    def __init__(
        self,
        settings: Settings,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize the service."""
        self.settings = settings
        self.logger = logger or structlog.get_logger()
        self.base_url = settings.CHARACTER_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.CHARACTER_SERVICE_TIMEOUT
        )
        self.openai = OpenAIService(settings)

    async def generate_character_content(
        self,
        character_id: UUID,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None
    ) -> str:
        """Generate content for a character."""
        try:
            # Get character details and content requirements
            content = await self.get_character_content(
                character_id,
                content_type
            )

            # Prepare generation context
            generation_context = {
                'class_name': content.requirements.get('class_name'),
                'race_name': content.requirements.get('race_name'),
                'background_name': content.requirements.get('background_name'),
                'alignment': content.requirements.get('alignment'),
                'level': content.requirements.get('level'),
                'combat_role': content.requirements.get('combat_role'),
                'equipment_type': content.requirements.get('equipment_type'),
                'theme_details': theme_context.details if theme_context else '',
                'theme_tone': theme_context.tone if theme_context else '',
                'additional_context': content.existing_content or ''
            }

            # Format prompt from template
            from .prompts.character import format_template
            prompt = format_template(
                content_type.value,
                generation_context
            )

            # Generate content using OpenAI
            completion = await self.openai.generate_text(
                prompt=prompt,
                max_tokens=self.settings.OPENAI_MAX_TOKENS,
                temperature=self.settings.OPENAI_TEMPERATURE
            )

            return completion.choices[0].text.strip()

        except Exception as e:
            self.logger.error(
                'character_content_generation_failed',
                character_id=str(character_id),
                content_type=content_type.value,
                error=str(e)
            )
            raise IntegrationError(f'Failed to generate character content: {str(e)}')

    async def validate_content(
        self,
        character_id: UUID,
        content_type: ContentType,
        content: str,
        theme_context: Optional[ThemeContext] = None
    ) -> bool:
        """Validate generated content."""
        try:
            from .validation import validate_character_content
            is_valid = await validate_character_content(
                content=content,
                content_type=content_type,
                theme_context=theme_context,
                settings=self.settings
            )

            self.logger.info(
                'content_validation_complete',
                character_id=str(character_id),
                content_type=content_type.value,
                is_valid=is_valid
            )

            return is_valid

        except Exception as e:
            self.logger.error(
                'content_validation_failed',
                character_id=str(character_id),
                content_type=content_type.value,
                error=str(e)
            )
            # Non-critical error, log but don't fail generation
            return True

    def __init__(
        self,
        settings: Settings,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize the service."""
        self.settings = settings
        self.logger = logger or structlog.get_logger()
        self.base_url = settings.CHARACTER_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.CHARACTER_SERVICE_TIMEOUT
        )

    async def get_character_content(
        self,
        character_id: UUID,
        content_type: ContentType
    ) -> CharacterContent:
        """Get character content for generation."""
        try:
            response = await self.client.get(
                f"/api/v2/characters/{character_id}/content",
                params={"content_type": content_type.value}
            )
            response.raise_for_status()
            
            data = response.json()
            return CharacterContent(
                character_id=character_id,
                content_type=content_type,
                theme_context=ThemeContext(**data["theme_context"])
                if data.get("theme_context") else None,
                existing_content=data.get("existing_content"),
                requirements=data.get("requirements")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "character_content_fetch_failed",
                character_id=str(character_id),
                content_type=content_type.value,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to fetch character content: {str(e)}"
            )

    async def update_character_content(
        self,
        character_id: UUID,
        content_type: ContentType,
        content: str
    ) -> None:
        """Update character content after generation."""
        try:
            response = await self.client.put(
                f"/api/v2/characters/{character_id}/content",
                json={
                    "content_type": content_type.value,
                    "content": content
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "character_content_updated",
                character_id=str(character_id),
                content_type=content_type.value
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "character_content_update_failed",
                character_id=str(character_id),
                content_type=content_type.value,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to update character content: {str(e)}"
            )

    async def validate_theme(
        self,
        character_id: UUID,
        theme_context: ThemeContext
    ) -> bool:
        """Validate theme compatibility for character."""
        try:
            response = await self.client.post(
                f"/api/v2/characters/{character_id}/theme/validate",
                json=theme_context.dict()
            )
            response.raise_for_status()
            
            data = response.json()
            is_valid = data["is_valid"]
            
            self.logger.info(
                "theme_validation_complete",
                character_id=str(character_id),
                theme=theme_context.name,
                is_valid=is_valid
            )
            
            return is_valid
            
        except httpx.HTTPError as e:
            self.logger.error(
                "theme_validation_failed",
                character_id=str(character_id),
                theme=theme_context.name,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to validate theme: {str(e)}"
            )

    async def notify_content_generation(
        self,
        character_id: UUID,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None
    ) -> None:
        """Notify Character service about content generation."""
        try:
            response = await self.client.post(
                f"/api/v2/characters/{character_id}/events",
                json={
                    "event_type": CharacterEventType.NARRATIVE_ADDED.value,
                    "content_type": content_type.value,
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "content_generation_notified",
                character_id=str(character_id),
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "content_generation_notification_failed",
                character_id=str(character_id),
                content_type=content_type.value,
                error=str(e)
            )
            # Non-critical error, log but don't raise
            self.logger.warning(
                "Failed to notify content generation",
                exc_info=e
            )
