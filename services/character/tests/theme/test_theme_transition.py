"""Tests for theme transition service."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from character_service.domain.theme import (
    ThemeTransitionType,
    ThemeValidationError,
    ThemeValidationResult,
)
from character_service.core.exceptions import ValidationError, ThemeTransitionError

from .test_base import (
    MockCharacter,
    MockTheme,
    MockThemeState,
)


pytestmark = pytest.mark.asyncio


async def test_successful_transition(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_character_service,
    mock_state_manager,
    mock_session,
    mock_integration_manager,
):
    """Test successful theme transition."""
    # Setup mock return values
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Perform transition
    result = await theme_service.apply_transition(
        character_id=character.id,
        from_theme_id=from_theme.id,
        to_theme_id=to_theme.id,
        transition_type=ThemeTransitionType.STORY,
    )

    # Verify success
    assert result is True

    # Verify character service calls
    mock_character_service.get_character.assert_called_once_with(character.id)

    # Verify state manager calls
    mock_state_manager.calculate_state_changes.assert_called_once_with(
        character.id,
        from_theme.id,
        to_theme.id,
    )
    mock_state_manager.transition_theme_state.assert_called_once()

    # Verify ability score changes were applied
    assert character.strength_score == 14  # 15 - 2 (remove old) + 1 (add new)
    assert character.constitution_score == 15  # 14 + 1 (add new)

    # Verify integration calls
    mock_integration_manager.handle_theme_transition.assert_called_once()


async def test_validation_failure(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
):
    """Test theme transition with validation failure."""
    # Set up an invalid theme transition
    to_theme.level_requirement = 10  # Above character's level

    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Attempt transition
    with pytest.raises(ValidationError) as exc:
        await theme_service.apply_transition(
            character_id=character.id,
            from_theme_id=from_theme.id,
            to_theme_id=to_theme.id,
            transition_type=ThemeTransitionType.STORY,
        )

    assert "Theme transition validation failed" in str(exc.value)
    assert len(exc.value.errors) == 1
    assert exc.value.errors[0].error_type == "level_requirement"


async def test_class_restriction_validation(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
):
    """Test theme transition with class restriction validation."""
    # Set up class restrictions that exclude character's class
    to_theme.class_restrictions = ["Wizard", "Sorcerer"]

    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Attempt transition
    with pytest.raises(ValidationError) as exc:
        await theme_service.apply_transition(
            character_id=character.id,
            from_theme_id=from_theme.id,
            to_theme_id=to_theme.id,
            transition_type=ThemeTransitionType.STORY,
        )

    assert "Theme transition validation failed" in str(exc.value)
    assert len(exc.value.errors) == 1
    assert exc.value.errors[0].error_type == "class_restriction"


async def test_antitheticon_transition(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
    mock_integration_manager,
):
    """Test Antitheticon theme transition."""
    # Set up Antitheticon transition
    to_theme.category = ThemeCategory.ANTITHETICON

    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Perform transition
    result = await theme_service.apply_transition(
        character_id=character.id,
        from_theme_id=from_theme.id,
        to_theme_id=to_theme.id,
        transition_type=ThemeTransitionType.ANTITHETICON,
    )

    assert result is True

    # Verify integration handling
    mock_integration_manager.handle_theme_transition.assert_called_once()
    call_args = mock_integration_manager.handle_theme_transition.call_args[0]
    assert call_args[0] == character.id
    assert call_args[3]["transition_type"] == ThemeTransitionType.ANTITHETICON


async def test_campaign_context_integration(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
    mock_integration_manager,
):
    """Test theme transition with campaign context."""
    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Set up campaign context
    campaign_event_id = uuid4()
    mock_integration_manager.campaign.get_campaign_context.return_value = {
        "event_type": "quest_completion",
        "quest_name": "The Ancient Trial",
    }

    # Perform transition with campaign context
    result = await theme_service.apply_transition(
        character_id=character.id,
        from_theme_id=from_theme.id,
        to_theme_id=to_theme.id,
        transition_type=ThemeTransitionType.STORY,
        campaign_event_id=campaign_event_id,
    )

    assert result is True

    # Verify campaign context handling
    mock_integration_manager.campaign.get_campaign_context.assert_called_once_with(
        character.campaign_id,
        campaign_event_id,
    )


async def test_theme_content_generation(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
    mock_integration_manager,
):
    """Test theme transition with content generation."""
    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Set up content generation response
    mock_integration_manager.llm.generate_theme_content.return_value = {
        "narrative": "As the ancient trial concluded...",
        "mechanical_changes": ["Gained proficiency in Athletics"],
    }

    # Perform transition with content generation
    result = await theme_service.apply_transition(
        character_id=character.id,
        from_theme_id=from_theme.id,
        to_theme_id=to_theme.id,
        transition_type=ThemeTransitionType.STORY,
        options={"generate_content": True},
    )

    assert result is True

    # Verify content generation
    mock_integration_manager.llm.generate_theme_content.assert_called_once()
    assert mock_integration_manager.llm.generate_theme_content.call_args[1]["theme_category"] == to_theme.category


async def test_theme_caching(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
    mock_integration_manager,
):
    """Test theme transition cache handling."""
    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Perform transition
    result = await theme_service.apply_transition(
        character_id=character.id,
        from_theme_id=from_theme.id,
        to_theme_id=to_theme.id,
        transition_type=ThemeTransitionType.STORY,
    )

    assert result is True

    # Verify cache invalidation
    mock_integration_manager.cache.invalidate_theme.assert_any_call(character.id)
    mock_integration_manager.cache.invalidate_theme.assert_any_call(from_theme.id)
    mock_integration_manager.cache.invalidate_theme.assert_any_call(to_theme.id)


async def test_integration_error_handling(
    theme_service,
    character,
    from_theme,
    to_theme,
    theme_state,
    mock_session,
    mock_integration_manager,
):
    """Test theme transition with integration error."""
    # Mock theme retrieval
    mock_session.execute.return_value.scalars.return_value.all.return_value = [from_theme, to_theme]

    # Simulate integration error
    mock_integration_manager.handle_theme_transition.side_effect = Exception("Integration failed")

    # Attempt transition
    with pytest.raises(ThemeTransitionError) as exc:
        await theme_service.apply_transition(
            character_id=character.id,
            from_theme_id=from_theme.id,
            to_theme_id=to_theme.id,
            transition_type=ThemeTransitionType.STORY,
        )

    assert "Theme transition failed" in str(exc.value)
    assert "Integration failed" in str(exc.value)
