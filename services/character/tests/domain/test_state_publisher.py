"""Tests for state publication service."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

from character_service.core.exceptions import MessageHubError
from character_service.domain.messages import (
    CharacterStateMessage,
    CampaignEventMessage,
    MessageType,
    ProgressEventMessage,
)
from character_service.domain.models import Character, CampaignEvent
from character_service.domain.state_publisher import StatePublisher


@pytest.fixture
def message_hub():
    """Create mock message hub client."""
    mock = AsyncMock()
    mock.subscribe = Mock()  # Not async
    return mock


@pytest.fixture
def event_service():
    """Create mock event service."""
    return AsyncMock()


@pytest.fixture
def state_publisher(message_hub, event_service):
    """Create state publisher instance with mocked dependencies."""
    return StatePublisher(message_hub, event_service)


@pytest.fixture
def test_character():
    """Create test character instance."""
    return Character.create_new("Test", uuid4(), uuid4())


@pytest.mark.asyncio
async def test_publish_character_created(state_publisher, message_hub, test_character):
    """Test publishing character creation event."""
    await state_publisher.publish_character_created(test_character)

    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, CharacterStateMessage)
    assert message.type == MessageType.CHARACTER_CREATED
    assert message.character_id == test_character.id
    assert message.state_data == test_character.character_data
    assert message.state_version == 1


@pytest.mark.asyncio
async def test_publish_character_updated(state_publisher, message_hub, test_character):
    """Test publishing character update event."""
    previous_data = {"level": 1, "experience": 0}
    test_character.character_data = {"level": 2, "experience": 1000}

    await state_publisher.publish_character_updated(
        test_character,
        previous_data=previous_data,
    )

    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, CharacterStateMessage)
    assert message.type == MessageType.CHARACTER_UPDATED
    assert message.character_id == test_character.id
    assert message.state_data == test_character.character_data
    assert message.state_changes == {
        "level": {"old": 1, "new": 2},
        "experience": {"old": 0, "new": 1000},
    }


@pytest.mark.asyncio
async def test_publish_experience_gained(state_publisher, message_hub, test_character):
    """Test publishing experience gain event."""
    await state_publisher.publish_experience_gained(
        test_character,
        amount=1000,
        source="quest",
        reason="Completed quest",
    )

    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, ProgressEventMessage)
    assert message.type == MessageType.EXPERIENCE_GAINED
    assert message.character_id == test_character.id
    assert message.progress_type == "experience"
    assert message.progress_data == {
        "amount": 1000,
        "source": "quest",
        "reason": "Completed quest",
    }


@pytest.mark.asyncio
async def test_publish_level_changed(state_publisher, message_hub, test_character):
    """Test publishing level change event."""
    test_character.character_data["character_class"] = "Fighter"
    await state_publisher.publish_level_changed(
        test_character,
        previous_level=1,
        new_level=2,
    )

    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, ProgressEventMessage)
    assert message.type == MessageType.LEVEL_CHANGED
    assert message.character_id == test_character.id
    assert message.progress_type == "level"
    assert message.progress_data == {
        "previous_level": 1,
        "new_level": 2,
        "class": "Fighter",
    }


@pytest.mark.asyncio
async def test_publish_milestone_achieved(state_publisher, message_hub, test_character):
    """Test publishing milestone achievement event."""
    milestone_id = uuid4()
    await state_publisher.publish_milestone_achieved(
        test_character,
        milestone_id=milestone_id,
        title="First Quest",
        milestone_type="quest",
    )

    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, ProgressEventMessage)
    assert message.type == MessageType.MILESTONE_ACHIEVED
    assert message.character_id == test_character.id
    assert message.progress_type == "milestone"
    assert message.progress_data == {
        "milestone_id": str(milestone_id),
        "title": "First Quest",
        "type": "quest",
    }


@pytest.mark.asyncio
async def test_handle_campaign_event(
    state_publisher,
    event_service,
    message_hub,
    test_character,
):
    """Test handling incoming campaign events."""
    # Setup event
    event_id = uuid4()
    event_message = CampaignEventMessage(
        id=uuid4(),
        type=MessageType.CAMPAIGN_EVENT_CREATED,
        timestamp=datetime.utcnow(),
        event_id=event_id,
        character_id=test_character.id,
        event_type="combat",
        event_data={"damage": 5},
    )

    # Setup mocks
    event_service.apply_event.return_value = [Mock()]  # Return mock impact
    event_service._char_repo.get.return_value = test_character

    # Handle event
    await state_publisher._handle_campaign_event(event_message)

    # Verify event was applied
    event_service.apply_event.assert_called_once_with(event_id)

    # Verify state was published
    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, CharacterStateMessage)
    assert message.type == MessageType.CHARACTER_UPDATED
    assert message.character_id == test_character.id


@pytest.mark.asyncio
async def test_handle_sync_request(
    state_publisher,
    event_service,
    message_hub,
    test_character,
):
    """Test handling sync requests."""
    # Setup request
    sync_message = CharacterStateMessage(
        id=uuid4(),
        type=MessageType.STATE_SYNC_REQUESTED,
        timestamp=datetime.utcnow(),
        character_id=test_character.id,
        state_version=0,
        state_data={},
    )

    # Setup mocks
    event_service._char_repo.get.return_value = test_character

    # Handle request
    await state_publisher._handle_sync_request(sync_message)

    # Verify state was published
    message_hub.publish.assert_called_once()
    message = message_hub.publish.call_args[0][0]
    assert isinstance(message, CharacterStateMessage)
    assert message.type == MessageType.CHARACTER_UPDATED
    assert message.character_id == test_character.id


@pytest.mark.asyncio
async def test_message_hub_error_handling(state_publisher, message_hub, test_character):
    """Test error handling for message hub failures."""
    message_hub.publish.side_effect = MessageHubError("Connection failed")

    with pytest.raises(MessageHubError):
        await state_publisher.publish_character_created(test_character)
