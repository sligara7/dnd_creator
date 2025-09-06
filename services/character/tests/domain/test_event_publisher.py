"""Tests for event publication manager."""
import asyncio
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

from character_service.core.exceptions import (
    EventApplicationError,
    MessageHubError,
    MessageValidationError,
)
from character_service.domain.event_publisher import (
    EventPublicationManager,
    PublicationConfig,
)
from character_service.domain.messages import (
    CampaignEventMessage,
    CharacterStateMessage,
    ErrorMessage,
    Message,
    MessageType,
    ProgressEventMessage,
)
from character_service.domain.models import (
    CampaignEvent,
    Character,
    CharacterProgress,
)


@pytest.fixture
def state_publisher():
    """Create mock state publisher."""
    mock = AsyncMock()
    mock.create_state_message = AsyncMock()
    mock.publish_message = AsyncMock()
    return mock


@pytest.fixture
def event_service():
    """Create mock event service."""
    return AsyncMock()


@pytest.fixture
def config():
    """Create publication config."""
    return PublicationConfig(
        batch_size=2,  # Small batch size for testing
        batch_timeout=0.1,  # Short timeout for testing
        retry_max_attempts=2,
        retry_initial_delay=0.01,
        retry_max_delay=0.05,
        retry_jitter=0.01,
    )


@pytest.fixture
def publisher(state_publisher, event_service, config):
    """Create event publication manager."""
    return EventPublicationManager(state_publisher, event_service, config)


@pytest.fixture
def test_character():
    """Create test character."""
    return Character.create_new("Test", uuid4(), uuid4())


@pytest.fixture
def test_progress(test_character):
    """Create test progress."""
    return CharacterProgress(
        id=uuid4(),
        character_id=test_character.id,
        experience_points=1000,
        current_level=3,
        previous_level=2,
        level_updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_start_stop_manager(publisher):
    """Test starting and stopping the publication manager."""
    assert publisher._batch_task is None

    await publisher.start()
    assert publisher._batch_task is not None
    assert not publisher._batch_task.done()

    await publisher.stop()
    assert publisher._batch_task is None


@pytest.mark.asyncio
async def test_publish_event(publisher, state_publisher):
    """Test publishing a campaign event."""
    await publisher.start()

    event = CampaignEvent(
        id=uuid4(),
        character_id=uuid4(),
        event_type="combat",
        event_data={"damage": 5},
        impact_type="hit_points",
        impact_magnitude=-5,
        timestamp=datetime.utcnow(),
    )

    await publisher.publish_event(event)
    await asyncio.sleep(0.2)  # Wait for batch processing

    assert state_publisher.publish_message.call_count == 1
    message = state_publisher.publish_message.call_args[0][0]
    assert isinstance(message, CampaignEventMessage)
    assert message.event_id == event.id
    assert message.event_type == event.event_type

    await publisher.stop()


@pytest.mark.asyncio
async def test_publish_character_update(publisher, state_publisher, test_character):
    """Test publishing a character update."""
    await publisher.start()

    state_message = CharacterStateMessage(
        id=uuid4(),
        type=MessageType.CHARACTER_UPDATED,
        timestamp=datetime.utcnow(),
        character_id=test_character.id,
        state_version=1,
        state_data=test_character.character_data,
    )
    state_publisher.create_state_message.return_value = state_message

    await publisher.publish_character_update(test_character)
    await asyncio.sleep(0.2)  # Wait for batch processing

    state_publisher.create_state_message.assert_called_once_with(
        test_character,
        None,
    )
    state_publisher.publish_message.assert_called_once()

    await publisher.stop()


@pytest.mark.asyncio
async def test_publish_progress_update(publisher, state_publisher, test_progress):
    """Test publishing a progress update."""
    await publisher.start()

    await publisher.publish_progress_update(test_progress, "level")
    await asyncio.sleep(0.2)  # Wait for batch processing

    assert state_publisher.publish_message.call_count == 1
    message = state_publisher.publish_message.call_args[0][0]
    assert isinstance(message, ProgressEventMessage)
    assert message.type == MessageType.LEVEL_CHANGED
    assert message.character_id == test_progress.character_id
    assert message.progress_type == "level"
    assert message.progress_data["current_level"] == test_progress.current_level

    await publisher.stop()


@pytest.mark.asyncio
async def test_message_batching(publisher, state_publisher, test_character):
    """Test message batching functionality."""
    await publisher.start()

    # Publish multiple messages quickly
    for _ in range(5):
        await publisher.publish_character_update(test_character)

    await asyncio.sleep(0.3)  # Wait for batch processing

    # With batch_size=2, should see 3 batches (2+2+1)
    assert state_publisher.publish_message.call_count >= 3

    await publisher.stop()


@pytest.mark.asyncio
async def test_retry_logic(publisher, state_publisher, test_character):
    """Test retry logic for failed publications."""
    await publisher.start()

    # Make first attempt fail, then succeed
    state_publisher.publish_message.side_effect = [
        MessageHubError("Connection failed"),
        None,  # Success
    ]

    await publisher.publish_character_update(test_character)
    await asyncio.sleep(0.3)  # Wait for retry

    # Should see 2 attempts
    assert state_publisher.publish_message.call_count == 2

    await publisher.stop()


@pytest.mark.asyncio
async def test_max_retries_exceeded(publisher, state_publisher, test_character):
    """Test handling when max retries are exceeded."""
    await publisher.start()

    # Make all attempts fail
    state_publisher.publish_message.side_effect = MessageHubError("Connection failed")

    await publisher.publish_character_update(test_character)
    await asyncio.sleep(0.5)  # Wait for all retries

    # Should see attempts up to max_retries (2 in test config)
    publish_calls = state_publisher.publish_message.call_args_list
    assert len(publish_calls) >= 2

    # Last call should be an error message
    last_message = publish_calls[-1][0][0]
    assert isinstance(last_message, ErrorMessage)
    assert last_message.error_code == "PUBLICATION_ERROR"
    assert "Max retry attempts exceeded" in last_message.error_message

    await publisher.stop()


@pytest.mark.asyncio
async def test_duplicate_message_prevention(publisher, test_character):
    """Test prevention of duplicate in-flight messages."""
    await publisher.start()

    # Create a message and add it to in_flight
    message_id = uuid4()
    publisher._in_flight.add(message_id)

    # Attempt to publish a message with same ID
    with pytest.raises(MessageValidationError):
        await publisher._enqueue_message(
            CharacterStateMessage(
                id=message_id,
                type=MessageType.CHARACTER_UPDATED,
                timestamp=datetime.utcnow(),
                character_id=test_character.id,
                state_version=1,
                state_data={},
            )
        )

    await publisher.stop()


@pytest.mark.asyncio
async def test_error_handling_during_batch_processing(
    publisher, state_publisher, test_character
):
    """Test error handling during batch processing."""
    await publisher.start()

    # Simulate unexpected error
    state_publisher.publish_message.side_effect = Exception("Unexpected error")

    await publisher.publish_character_update(test_character)
    await asyncio.sleep(0.2)  # Wait for processing

    # Should attempt to publish error message
    error_messages = [
        call[0][0] for call in state_publisher.publish_message.call_args_list
        if isinstance(call[0][0], ErrorMessage)
    ]
    assert len(error_messages) == 1
    assert error_messages[0].error_code == "PUBLICATION_ERROR"
    assert not error_messages[0].should_retry

    await publisher.stop()
