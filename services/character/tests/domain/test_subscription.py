"""Tests for subscription manager."""
import asyncio
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from character_service.core.exceptions import (
    EventApplicationError,
    MessageHubError,
    MessageValidationError,
    StateConflictError,
)
from character_service.domain.messages import (
    CampaignEventMessage,
    CharacterStateMessage,
    ErrorMessage,
    MessageType,
    ProgressEventMessage,
    StateSyncMessage,
)
from character_service.domain.models import (
    CampaignEvent,
    Character,
    EventImpact,
    CharacterProgress,
)
from character_service.domain.subscription import SubscriptionManager


@pytest.fixture
def message_hub():
    """Create mock message hub client."""
    mock = AsyncMock()
    mock.subscribe = Mock()  # Not async
    return mock


@pytest.fixture
def state_publisher():
    """Create mock state publisher."""
    return AsyncMock()


@pytest.fixture
def event_service():
    """Create mock event service."""
    mock = AsyncMock()
    mock._char_repo = AsyncMock()  # For direct state updates
    return mock


@pytest.fixture
def progress_service():
    """Create mock progress service."""
    return AsyncMock()


@pytest.fixture
def subscription_manager(message_hub, state_publisher, event_service, progress_service):
    """Create subscription manager."""
    return SubscriptionManager(
        message_hub,
        state_publisher,
        event_service,
        progress_service,
    )


@pytest.fixture
def test_character():
    """Create test character."""
    return Character.create_new("Test", uuid4(), uuid4())


@pytest.mark.asyncio
async def test_subscription_setup(subscription_manager, message_hub):
    """Test subscription setup."""
    await subscription_manager.start()

    # Verify all necessary subscriptions were set up
    assert message_hub.subscribe.call_count == 9  # Total number of handlers
    subscription_types = [
        call[0][0] for call in message_hub.subscribe.call_args_list
    ]
    assert MessageType.CAMPAIGN_EVENT_CREATED in subscription_types
    assert MessageType.CHARACTER_UPDATED in subscription_types
    assert MessageType.EXPERIENCE_GAINED in subscription_types


@pytest.mark.asyncio
async def test_handle_campaign_event(
    subscription_manager,
    event_service,
    state_publisher,
    test_character,
):
    """Test handling campaign event."""
    # Setup event
    event_id = uuid4()
    message = CampaignEventMessage(
        id=uuid4(),
        type=MessageType.CAMPAIGN_EVENT_CREATED,
        timestamp=datetime.utcnow(),
        event_id=event_id,
        character_id=test_character.id,
        event_type="combat",
        event_data={"damage": 5},
    )

    # Setup mocks
    impact = EventImpact(
        id=uuid4(),
        event_id=event_id,
        character_id=test_character.id,
        impact_type="hit_points",
        impact_data={"amount": -5},
    )
    event_service.apply_event.return_value = [impact]
    event_service._char_repo.get.return_value = test_character

    # Handle event
    await subscription_manager._handle_campaign_event(message)

    # Verify event was processed
    event_service.apply_event.assert_called_once()
    state_publisher.publish_character_update.assert_called_once_with(test_character)


@pytest.mark.asyncio
async def test_handle_duplicate_event(subscription_manager, event_service):
    """Test handling duplicate event."""
    event_id = uuid4()
    message = CampaignEventMessage(
        id=uuid4(),
        type=MessageType.CAMPAIGN_EVENT_CREATED,
        timestamp=datetime.utcnow(),
        event_id=event_id,
        character_id=uuid4(),
        event_type="combat",
        event_data={},
    )

    # Add event to processing set
    subscription_manager._processing_events.add(event_id)

    # Handle event
    await subscription_manager._handle_campaign_event(message)

    # Verify event was not processed
    event_service.apply_event.assert_not_called()


@pytest.mark.asyncio
async def test_handle_character_update(
    subscription_manager,
    event_service,
    test_character,
):
    """Test handling character state update."""
    message = CharacterStateMessage(
        id=uuid4(),
        type=MessageType.CHARACTER_UPDATED,
        timestamp=datetime.utcnow(),
        character_id=test_character.id,
        state_version=1,
        state_data={"level": 2, "hp": 20},
    )

    event_service._char_repo.get.return_value = test_character

    await subscription_manager._handle_character_update(message)

    # Verify character state was updated
    assert test_character.character_data == message.state_data
    assert subscription_manager._character_versions[test_character.id] == 1


@pytest.mark.asyncio
async def test_handle_state_conflict(
    subscription_manager,
    event_service,
    state_publisher,
    test_character,
):
    """Test handling state version conflict."""
    # Set current version higher than incoming
    subscription_manager._character_versions[test_character.id] = 2

    message = CharacterStateMessage(
        id=uuid4(),
        type=MessageType.CHARACTER_UPDATED,
        timestamp=datetime.utcnow(),
        character_id=test_character.id,
        state_version=1,
        state_data={},
    )

    await subscription_manager._handle_character_update(message)

    # Verify sync request was sent
    assert state_publisher.publish_message.call_count == 1
    sync_message = state_publisher.publish_message.call_args[0][0]
    assert isinstance(sync_message, StateSyncMessage)
    assert sync_message.character_id == test_character.id


@pytest.mark.asyncio
async def test_handle_experience_update(
    subscription_manager,
    progress_service,
    test_character,
):
    """Test handling experience update."""
    message = ProgressEventMessage(
        id=uuid4(),
        type=MessageType.EXPERIENCE_GAINED,
        timestamp=datetime.utcnow(),
        character_id=test_character.id,
        progress_type="experience",
        progress_data={
            "amount": 1000,
            "source": "quest",
            "reason": "Completed quest",
        },
    )

    await subscription_manager._handle_experience_update(message)

    # Verify experience was added
    progress_service.add_experience.assert_called_once_with(
        test_character.id,
        1000,
        "quest",
        "Completed quest",
    )


@pytest.mark.asyncio
async def test_handle_error_publishing(
    subscription_manager,
    state_publisher,
):
    """Test error message publishing."""
    source_message = CampaignEventMessage(
        id=uuid4(),
        type=MessageType.CAMPAIGN_EVENT_CREATED,
        timestamp=datetime.utcnow(),
        event_id=uuid4(),
        character_id=uuid4(),
        event_type="combat",
        event_data={},
    )
    error_text = "Test error"

    await subscription_manager._publish_error(source_message, error_text)

    # Verify error message was published
    assert state_publisher.publish_message.call_count == 1
    error_message = state_publisher.publish_message.call_args[0][0]
    assert isinstance(error_message, ErrorMessage)
    assert error_message.error_code == "SUBSCRIPTION_ERROR"
    assert error_message.error_message == error_text
    assert error_message.source_message_id == source_message.id


@pytest.mark.asyncio
async def test_impact_type_calculation(subscription_manager):
    """Test impact type calculation."""
    test_cases = [
        ("combat", {"damage": 5}, "hit_points"),
        ("rest", {"healing": 10}, "hit_points"),
        ("quest", {"experience": 100}, "experience"),
        ("training", {"ability": "strength"}, "ability_score"),
        ("unknown", {}, "other"),
    ]

    for event_type, data, expected in test_cases:
        result = subscription_manager._determine_impact_type(event_type, data)
        assert result == expected


@pytest.mark.asyncio
async def test_impact_magnitude_calculation(subscription_manager):
    """Test impact magnitude calculation."""
    test_cases = [
        ({"damage": 5}, -5),
        ({"healing": 10}, 10),
        ({"experience": 100}, 100),
        ({}, 0),
    ]

    for data, expected in test_cases:
        result = subscription_manager._calculate_impact_magnitude(data)
        assert result == expected
