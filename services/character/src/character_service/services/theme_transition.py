"""Theme transition service."""
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from character_service.services.theme_state import ThemeStateManager
from character_service.services.character import CharacterService
from character_service.models.theme import Theme, ThemeFeature, ThemeState, ThemeTransition
from character_service.domain.theme import (
    Theme as ThemeDomain,
    ThemeState as ThemeStateDomain,
    ThemeTransition as ThemeTransitionDomain,
    ThemeTransitionResult,
    ThemeValidationResult,
    ThemeValidationError,
    ThemeTransitionType,
)
from character_service.core.exceptions import (
    ThemeNotFoundError,
    ThemeValidationError as ThemeValidationException,
    CharacterNotFoundError,
)


class ThemeTransitionService:
    """Service for handling theme transitions."""

    def __init__(
        self,
        session: AsyncSession,
        state_manager: ThemeStateManager,
        character_service: CharacterService,
        message_hub: Optional[Any] = None,  # Replace with proper MessageHub type
        llm_service: Optional[Any] = None,  # Replace with proper LLM service type
    ):
        self.session = session
        self.state_manager = state_manager
        self.character_service = character_service
        self.message_hub = message_hub
        self.llm_service = llm_service

    async def validate_transition(
        self,
        character_id: UUID,
        from_theme_id: Optional[UUID],
        to_theme_id: UUID,
        transition_type: ThemeTransitionType,
        campaign_event_id: Optional[UUID] = None,
    ) -> ThemeValidationResult:
        """Validate a theme transition using the theme validation system."""
        try:
            # Get character
            character = await self.character_service.get_character(character_id)
            if not character:
                return ThemeValidationResult(
                    is_valid=False,
                    errors=[
                        ThemeValidationError(
                            error_type="character_not_found",
                            message=f"Character {character_id} not found",
                        )
                    ],
                )
            # Get themes
            themes_query = select(Theme).where(
                Theme.id.in_([tid for tid in [from_theme_id, to_theme_id] if tid])
            )
            themes = (await self.session.execute(themes_query)).scalars().all()
            theme_dict = {theme.id: theme for theme in themes}

            from_theme = theme_dict.get(from_theme_id) if from_theme_id else None
            to_theme = theme_dict.get(to_theme_id)

            if not to_theme:
                return ThemeValidationResult(
                    is_valid=False,
                    errors=[
                        ThemeValidationError(
                            error_type="theme_not_found",
                            message=f"Theme {to_theme_id} not found",
                        )
                    ],
                )

            # Create validation context
            campaign_event = None
            if campaign_event_id:
                # TODO: Fetch campaign event details
                pass

            context = ValidationContext(
                character=character,
                from_theme=from_theme,
                to_theme=to_theme,
                transition_type=transition_type,
                campaign_event=campaign_event,
            )

            # Get appropriate validator based on theme category
            validator = ThemeValidatorFactory.create_validator(to_theme.category)

            # Validate using the validation system
            return await validator.validate(context)

        except Exception as e:
            return ThemeValidationResult(
                is_valid=False,
                errors=[
                    ThemeValidationError(
                        error_type="validation_error",
                        message=str(e),
                    )
                ],
            )

    async def apply_transition(
        self,
        character_id: UUID,
        from_theme_id: Optional[UUID],
        to_theme_id: UUID,
        transition_type: ThemeTransitionType,
        triggered_by: str,
        campaign_event_id: Optional[UUID] = None,
    ) -> ThemeTransitionResult:
        """Apply a theme transition."""
        # First validate the transition
        validation_result = await self.validate_transition(
            character_id,
            from_theme_id,
            to_theme_id,
            transition_type,
            campaign_event_id,
        )

        if not validation_result.is_valid:
            return ThemeTransitionResult(
                success=False,
                validation_result=validation_result,
                error_details={"validation_errors": [e.dict() for e in validation_result.errors]},
            )

        try:
            # Calculate state changes
            changes = await self.state_manager.calculate_state_changes(
                character_id,
                from_theme_id,
                to_theme_id,
            )

            # Start transaction
            async with self.session.begin_nested():
                # Apply ability score changes
                for ability, change in changes["ability_changes"].items():
                    await self.character_service.adjust_ability_score(
                        character_id,
                        ability,
                        change,
                    )

                # Apply equipment changes
                for equipment_change in changes["equipment_changes"]:
                    if equipment_change["operation"] == "add":
                        await self.character_service.add_equipment(
                            character_id,
                            equipment_change["item_id"],
                            equipment_change["quantity"],
                        )
                    elif equipment_change["operation"] == "remove":
                        await self.character_service.remove_equipment(
                            character_id,
                            equipment_change["item_id"],
                            equipment_change["quantity"],
                        )

                # Apply new theme state
                old_state = await self.state_manager.get_active_theme_state(character_id)
                new_state = await self.state_manager.apply_theme_state(
                    character_id,
                    to_theme_id,
                    features=changes["added_features"],
                    modifiers=changes["added_modifiers"],
                )

                # Record transition
                transition = await self.state_manager.record_theme_transition(
                    character_id,
                    from_theme_id,
                    to_theme_id,
                    transition_type,
                    triggered_by,
                    campaign_event_id,
                    changes,
                )

                # Publish transition event
                if self.message_hub:
                    await self.message_hub.publish_event(
                        "theme.transition.completed",
                        {
                            "character_id": str(character_id),
                            "from_theme_id": str(from_theme_id) if from_theme_id else None,
                            "to_theme_id": str(to_theme_id),
                            "transition_type": transition_type,
                            "triggered_by": triggered_by,
                            "campaign_event_id": str(campaign_event_id) if campaign_event_id else None,
                            "changes": changes,
                        }
                    )

            return ThemeTransitionResult(
                success=True,
                transition_id=transition.id,
                old_state=ThemeStateDomain.model_validate(old_state) if old_state else None,
                new_state=new_state,
                applied_changes=changes,
                validation_result=validation_result,
            )

        except Exception as e:
            await self.session.rollback()
            return ThemeTransitionResult(
                success=False,
                validation_result=ThemeValidationResult(
                    is_valid=False,
                    errors=[
                        ThemeValidationError(
                            error_type="transition_error",
                            message=str(e),
                        )
                    ],
                ),
                error_details={"message": str(e)},
            )

    async def get_transition_suggestions(
        self,
        character_id: UUID,
        event_context: Optional[Dict[str, Any]] = None,
    ) -> List[ThemeDomain]:
        """Get theme transition suggestions."""
        # This would typically use LLM service to generate suggestions
        if not self.llm_service:
            return []

        try:
            # Get character details
            character = await self.character_service.get_character(character_id)
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            # Get current theme state
            current_state = await self.state_manager.get_active_theme_state(character_id)

            # Build context for LLM
            context = {
                "character": character.dict(),
                "current_theme": current_state.dict() if current_state else None,
                "event_context": event_context,
            }

            # Get suggestions from LLM service
            # This is a placeholder for the actual LLM integration
            suggestions = await self.llm_service.get_theme_suggestions(context)

            # Convert suggestions to Theme objects
            # This assumes the LLM service returns properly structured theme data
            themes: List[ThemeDomain] = []
            for suggestion in suggestions:
                theme = Theme(**suggestion)
                themes.append(ThemeDomain.model_validate(theme))

            return themes

        except Exception as e:
            # Log error but return empty list
            print(f"Error getting theme suggestions: {e}")
            return []
