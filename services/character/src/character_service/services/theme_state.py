"""Theme state management service."""
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from character_service.models.theme import (
    Theme,
    ThemeFeature,
    ThemeState,
    ThemeTransition,
)
from character_service.domain.theme import (
    Theme as ThemeDomain,
    ThemeState as ThemeStateDomain,
    ThemeTransition as ThemeTransitionDomain,
    ThemeTransitionResult,
    ThemeValidationResult,
    ThemeValidationError,
)
from character_service.core.exceptions import (
    ThemeNotFoundError,
    ThemeValidationError as ThemeValidationException,
)


class ThemeStateManager:
    """Service for managing theme states."""

    def __init__(
        self,
        session: AsyncSession,
        message_hub: Optional[Any] = None,  # Replace with proper MessageHub type
    ):
        self.session = session
        self.message_hub = message_hub

    async def get_active_theme_state(
        self,
        character_id: UUID,
    ) -> Optional[ThemeStateDomain]:
        """Get a character's active theme state."""
        query = select(ThemeState).where(
            and_(
                ThemeState.character_id == character_id,
                ThemeState.is_active == True,  # noqa: E712
            )
        )
        result = await self.session.execute(query)
        theme_state = result.scalar_one_or_none()
        
        if not theme_state:
            return None
        
        return ThemeStateDomain.model_validate(theme_state)

    async def get_theme_history(
        self,
        character_id: UUID,
    ) -> List[ThemeTransitionDomain]:
        """Get a character's theme transition history."""
        query = select(ThemeTransition).where(
            ThemeTransition.character_id == character_id
        ).order_by(ThemeTransition.created_at.desc())
        
        result = await self.session.execute(query)
        transitions = result.scalars().all()
        
        return [
            ThemeTransitionDomain.model_validate(transition)
            for transition in transitions
        ]

    async def apply_theme_state(
        self,
        character_id: UUID,
        theme_id: UUID,
        features: Optional[List[str]] = None,
        modifiers: Optional[Dict[str, Any]] = None,
    ) -> ThemeStateDomain:
        """Apply a new theme state to a character."""
        # Get the theme
        theme_query = select(Theme).where(Theme.id == theme_id)
        theme = (await self.session.execute(theme_query)).scalar_one_or_none()
        if not theme:
            raise ThemeNotFoundError(f"Theme {theme_id} not found")

        # Deactivate current theme state if it exists
        current_state = await self.get_active_theme_state(character_id)
        if current_state:
            current_state_model = await self.session.get(ThemeState, current_state.id)
            current_state_model.is_active = False
            current_state_model.deactivated_at = datetime.utcnow()
            self.session.add(current_state_model)

        # Create new theme state
        new_state = ThemeState(
            character_id=character_id,
            theme_id=theme_id,
            is_active=True,
            applied_at=datetime.utcnow(),
            applied_features=features or [],
            applied_modifiers=modifiers or {},
            progress_state={},
        )
        self.session.add(new_state)
        await self.session.commit()

        # Publish event
        if self.message_hub:
            await self.message_hub.publish_event(
                "theme.state.applied",
                {
                    "character_id": str(character_id),
                    "theme_id": str(theme_id),
                    "features": features,
                    "modifiers": modifiers,
                }
            )

        return ThemeStateDomain.model_validate(new_state)

    async def validate_theme_state(
        self,
        character_id: UUID,
        theme_id: UUID,
    ) -> ThemeValidationResult:
        """Validate a theme state for a character."""
        errors: List[ThemeValidationError] = []
        warnings: List[ThemeValidationError] = []

        # Get the theme
        theme_query = select(Theme).where(Theme.id == theme_id)
        theme = (await self.session.execute(theme_query)).scalar_one_or_none()
        if not theme:
            return ThemeValidationResult(
                is_valid=False,
                errors=[
                    ThemeValidationError(
                        error_type="theme_not_found",
                        message=f"Theme {theme_id} not found",
                    )
                ],
            )

        # Validate theme requirements and restrictions
        # This would typically call into a more comprehensive validation system
        if theme.level_requirement > 1:
            # TODO: Check character level
            warnings.append(
                ThemeValidationError(
                    error_type="level_requirement",
                    message=f"Theme requires level {theme.level_requirement}",
                    context={"required_level": theme.level_requirement},
                )
            )

        if theme.class_restrictions:
            # TODO: Check character class
            warnings.append(
                ThemeValidationError(
                    error_type="class_restriction",
                    message="Theme has class restrictions",
                    context={"allowed_classes": theme.class_restrictions},
                )
            )

        if theme.race_restrictions:
            # TODO: Check character race
            warnings.append(
                ThemeValidationError(
                    error_type="race_restriction",
                    message="Theme has race restrictions",
                    context={"allowed_races": theme.race_restrictions},
                )
            )

        return ThemeValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    async def calculate_state_changes(
        self,
        character_id: UUID,
        from_theme_id: Optional[UUID],
        to_theme_id: UUID,
    ) -> Dict[str, Any]:
        """Calculate changes when transitioning between theme states."""
        changes: Dict[str, Any] = {
            "removed_features": [],
            "added_features": [],
            "removed_modifiers": {},
            "added_modifiers": {},
            "ability_changes": {},
            "equipment_changes": [],
        }

        # Get the themes
        themes_query = select(Theme).where(
            Theme.id.in_([tid for tid in [from_theme_id, to_theme_id] if tid])
        )
        themes = (await self.session.execute(themes_query)).scalars().all()
        theme_dict = {theme.id: theme for theme in themes}

        from_theme = theme_dict.get(from_theme_id) if from_theme_id else None
        to_theme = theme_dict.get(to_theme_id)

        if not to_theme:
            raise ThemeNotFoundError(f"Theme {to_theme_id} not found")

        # Calculate feature changes
        if from_theme:
            changes["removed_features"] = [
                feat.name for feat in from_theme.features
            ]
            changes["removed_modifiers"] = from_theme.base_modifiers

        changes["added_features"] = [
            feat.name for feat in to_theme.features
        ]
        changes["added_modifiers"] = to_theme.base_modifiers

        # Calculate ability score changes
        if from_theme:
            for ability, adj in from_theme.ability_adjustments.items():
                changes["ability_changes"][ability] = -adj

        for ability, adj in to_theme.ability_adjustments.items():
            if ability in changes["ability_changes"]:
                changes["ability_changes"][ability] += adj
            else:
                changes["ability_changes"][ability] = adj

        # Calculate equipment changes
        if from_theme:
            changes["equipment_changes"].extend([
                {
                    "operation": "remove",
                    "item_id": str(equip.item_id),
                    "quantity": equip.quantity,
                }
                for equip in from_theme.equipment_changes
                if equip.operation == "add"
            ])

        changes["equipment_changes"].extend([
            {
                "operation": equip.operation,
                "item_id": str(equip.item_id),
                "quantity": equip.quantity,
            }
            for equip in to_theme.equipment_changes
        ])

        return changes

    async def record_theme_transition(
        self,
        character_id: UUID,
        from_theme_id: Optional[UUID],
        to_theme_id: UUID,
        transition_type: str,
        triggered_by: str,
        campaign_event_id: Optional[UUID] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> ThemeTransitionDomain:
        """Record a theme transition."""
        transition = ThemeTransition(
            character_id=character_id,
            from_theme_id=from_theme_id,
            to_theme_id=to_theme_id,
            transition_type=transition_type,
            triggered_by=triggered_by,
            campaign_event_id=campaign_event_id,
            changes=changes or {},
        )
        self.session.add(transition)
        await self.session.commit()

        # Publish event
        if self.message_hub:
            await self.message_hub.publish_event(
                "theme.transition.recorded",
                {
                    "character_id": str(character_id),
                    "from_theme_id": str(from_theme_id) if from_theme_id else None,
                    "to_theme_id": str(to_theme_id),
                    "transition_type": transition_type,
                    "triggered_by": triggered_by,
                    "campaign_event_id": str(campaign_event_id) if campaign_event_id else None,
                }
            )

        return ThemeTransitionDomain.model_validate(transition)

    async def rollback_theme_transition(
        self,
        transition_id: UUID,
        reason: str,
    ) -> ThemeTransitionResult:
        """Rollback a theme transition."""
        # Get the transition
        transition = await self.session.get(ThemeTransition, transition_id)
        if not transition:
            raise ValueError(f"Transition {transition_id} not found")

        if transition.rolled_back:
            return ThemeTransitionResult(
                success=False,
                error_details={"message": "Transition already rolled back"},
                validation_result=ThemeValidationResult(is_valid=False),
            )

        # Get the current state
        current_state = await self.get_active_theme_state(transition.character_id)
        if not current_state or current_state.theme_id != transition.to_theme_id:
            return ThemeTransitionResult(
                success=False,
                error_details={"message": "Character's current theme state doesn't match transition"},
                validation_result=ThemeValidationResult(is_valid=False),
            )

        # Calculate reverse changes
        reverse_changes = await self.calculate_state_changes(
            transition.character_id,
            transition.to_theme_id,
            transition.from_theme_id,
        )

        # Apply the rollback
        try:
            old_state = current_state
            new_state = await self.apply_theme_state(
                transition.character_id,
                transition.from_theme_id,
                modifiers=reverse_changes.get("added_modifiers"),
            )

            # Mark the transition as rolled back
            transition.rolled_back = True
            transition.rollback_reason = reason
            self.session.add(transition)

            # Record the rollback transition
            rollback_transition = await self.record_theme_transition(
                transition.character_id,
                transition.to_theme_id,
                transition.from_theme_id,
                "rollback",
                "system",
                changes=reverse_changes,
            )

            await self.session.commit()

            return ThemeTransitionResult(
                success=True,
                transition_id=rollback_transition.id,
                old_state=ThemeStateDomain.model_validate(old_state),
                new_state=new_state,
                applied_changes=reverse_changes,
                validation_result=ThemeValidationResult(is_valid=True),
            )

        except Exception as e:
            await self.session.rollback()
            return ThemeTransitionResult(
                success=False,
                error_details={"message": str(e)},
                validation_result=ThemeValidationResult(
                    is_valid=False,
                    errors=[
                        ThemeValidationError(
                            error_type="rollback_error",
                            message=str(e),
                        )
                    ],
                ),
            )
