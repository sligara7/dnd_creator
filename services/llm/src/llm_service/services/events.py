"""Event handlers for service integration."""
from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from fastapi import BackgroundTasks

from ..core.exceptions import EventHandlingError
from ..models.theme import ContentType, ThemeContext
from .character import CharacterEventType, CharacterService
from .generation import GenerationPipeline


class EventHandler:
    """Handler for service events."""

    def __init__(
        self,
        character_service: CharacterService,
        generation_pipeline: GenerationPipeline,
        background_tasks: BackgroundTasks,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize event handler."""
        self.character_service = character_service
        self.generation_pipeline = generation_pipeline
        self.background_tasks = background_tasks
        self.logger = logger or structlog.get_logger()

    async def handle_character_event(
        self,
        event_type: CharacterEventType,
        character_id: UUID,
        data: Dict[str, Any],
        theme_context: Optional[ThemeContext] = None
    ) -> None:
        """Handle events from Character service."""
        try:
            if event_type == CharacterEventType.THEME_TRANSITIONED:
                await self._handle_theme_transition(
                    character_id,
                    theme_context
                )
            elif event_type == CharacterEventType.NARRATIVE_ADDED:
                await self._handle_narrative_update(
                    character_id,
                    data,
                    theme_context
                )
            else:
                self.logger.warning(
                    "unhandled_event_type",
                    event_type=event_type.value,
                    character_id=str(character_id)
                )

        except Exception as e:
            self.logger.error(
                "event_handling_failed",
                event_type=event_type.value,
                character_id=str(character_id),
                error=str(e)
            )
            raise EventHandlingError(f"Failed to handle event: {str(e)}")

    async def _handle_theme_transition(
        self,
        character_id: UUID,
        theme_context: ThemeContext
    ) -> None:
        """Handle theme transition events."""
        try:
            # Validate theme compatibility
            is_valid = await self.character_service.validate_theme(
                character_id,
                theme_context
            )
            if not is_valid:
                raise EventHandlingError("Theme validation failed")

            # Generate updated content for the new theme
            content_types = [
                ContentType.CHARACTER_BACKSTORY,
                ContentType.CHARACTER_PERSONALITY,
                ContentType.CHARACTER_COMBAT
            ]
            
            for content_type in content_types:
                # Add to background tasks to handle asynchronously
                self.background_tasks.add_task(
                    self._generate_themed_content,
                    character_id,
                    content_type,
                    theme_context
                )

            self.logger.info(
                "theme_transition_queued",
                character_id=str(character_id),
                theme=theme_context.name,
                content_types=[ct.value for ct in content_types]
            )

        except Exception as e:
            self.logger.error(
                "theme_transition_failed",
                character_id=str(character_id),
                theme=theme_context.name,
                error=str(e)
            )
            raise EventHandlingError(f"Theme transition failed: {str(e)}")

    async def _handle_narrative_update(
        self,
        character_id: UUID,
        data: Dict[str, Any],
        theme_context: Optional[ThemeContext]
    ) -> None:
        """Handle narrative update events."""
        try:
            content_type = ContentType(data["content_type"])
            existing_content = data.get("content", "")

            # Generate complementary content
            result = await self.generation_pipeline.generate_content(
                content_type=content_type,
                theme_context=theme_context,
                existing_content=existing_content
            )

            # Update character content
            await self.character_service.update_character_content(
                character_id=character_id,
                content_type=content_type,
                content=result.content
            )

            self.logger.info(
                "narrative_update_complete",
                character_id=str(character_id),
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None
            )

        except Exception as e:
            self.logger.error(
                "narrative_update_failed",
                character_id=str(character_id),
                error=str(e)
            )
            raise EventHandlingError(f"Narrative update failed: {str(e)}")

    async def _generate_themed_content(
        self,
        character_id: UUID,
        content_type: ContentType,
        theme_context: ThemeContext
    ) -> None:
        """Generate themed content for character."""
        try:
            # Get existing character content
            character_content = await self.character_service.get_character_content(
                character_id,
                content_type
            )

            # Generate new content
            result = await self.generation_pipeline.generate_content(
                content_type=content_type,
                theme_context=theme_context,
                existing_content=character_content.existing_content
            )

            # Update character content
            await self.character_service.update_character_content(
                character_id=character_id,
                content_type=content_type,
                content=result.content
            )

            # Notify about content generation
            await self.character_service.notify_content_generation(
                character_id=character_id,
                content_type=content_type,
                theme_context=theme_context
            )

            self.logger.info(
                "themed_content_generated",
                character_id=str(character_id),
                content_type=content_type.value,
                theme=theme_context.name
            )

        except Exception as e:
            self.logger.error(
                "themed_content_generation_failed",
                character_id=str(character_id),
                content_type=content_type.value,
                theme=theme_context.name,
                error=str(e)
            )
            # Log error but don't raise to allow other content types to proceed
