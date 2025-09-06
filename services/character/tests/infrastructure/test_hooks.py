"""Tests for event publication hooks."""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from character_service.domain.models import (
    CampaignEvent,
    Character,
    CharacterProgress,
    EventImpact,
)
from character_service.infrastructure.hooks import (
    publish_event_impact,
    publish_character_update,
    publish_progress_update,
)


@pytest.fixture
def event_service():
    """Create mock event service."""
    return AsyncMock()


@pytest.fixture
def progress_service():
    """Create mock progress service."""
    return AsyncMock()


@pytest.fixture
def event_publisher():
    """Create mock event publisher."""
    publisher = AsyncMock()
    publisher.publish_event = AsyncMock()
    publisher.publish_character_update = AsyncMock()
    publisher.publish_progress_update = AsyncMock()
    return publisher


@pytest.fixture
def test_character():
    """Create test character."""
    return Character.create_new("Test", uuid4(), uuid4())


@pytest.fixture
def test_event(test_character):
    """Create test event."""
    return CampaignEvent(
        id=uuid4(),
        character_id=test_character.id,
        event_type="combat",
        event_data={"damage": 5},
        impact_type="hit_points",
        impact_magnitude=-5,
    )


@pytest.fixture
def test_impact(test_event, test_character):
    """Create test impact."""
    return EventImpact(
        id=uuid4(),
        event_id=test_event.id,
        character_id=test_character.id,
        impact_type=test_event.impact_type,
        impact_data={"amount": test_event.impact_magnitude},
    )


@pytest.fixture
def test_progress(test_character):
    """Create test progress."""
    return CharacterProgress(
        id=uuid4(),
        character_id=test_character.id,
        experience_points=1000,
        current_level=3,
        previous_level=2,
    )


@pytest.mark.asyncio
async def test_publish_event_impact_hook(
    event_service,
    event_publisher,
    test_event,
    test_impact,
):
    """Test event impact publication hook."""
    # Call hook with event and impacts
    await publish_event_impact(
        event_service=event_service,
        event_publisher=event_publisher,
        event=test_event,
        impacts=[test_impact],
    )

    # Verify event was published
    event_publisher.publish_event.assert_called_once_with(test_event)


@pytest.mark.asyncio
async def test_publish_event_impact_hook_no_event(
    event_service,
    event_publisher,
):
    """Test hook behavior when no event is provided."""
    # Call hook without event
    await publish_event_impact(
        event_service=event_service,
        event_publisher=event_publisher,
    )

    # Verify no publication occurred
    event_publisher.publish_event.assert_not_called()


@pytest.mark.asyncio
async def test_publish_character_update_hook(
    event_publisher,
    test_character,
):
    """Test character update publication hook."""
    previous_data = {"level": 1}

    # Call hook with character and previous data
    await publish_character_update(
        event_publisher=event_publisher,
        character=test_character,
        previous_data=previous_data,
    )

    # Verify update was published
    event_publisher.publish_character_update.assert_called_once_with(
        test_character,
        previous_data=previous_data,
    )


@pytest.mark.asyncio
async def test_publish_character_update_hook_no_previous_data(
    event_publisher,
    test_character,
):
    """Test character update hook without previous data."""
    # Call hook without previous data
    await publish_character_update(
        event_publisher=event_publisher,
        character=test_character,
    )

    # Verify update was published
    event_publisher.publish_character_update.assert_called_once_with(
        test_character,
        previous_data=None,
    )


@pytest.mark.asyncio
async def test_publish_progress_update_hook(
    progress_service,
    event_publisher,
    test_progress,
):
    """Test progress update publication hook."""
    # Call hook with progress
    await publish_progress_update(
        progress_service=progress_service,
        event_publisher=event_publisher,
        progress=test_progress,
        update_type="level",
    )

    # Verify progress was published
    event_publisher.publish_progress_update.assert_called_once_with(
        test_progress,
        "level",
    )


@pytest.mark.asyncio
async def test_publish_progress_update_hook_no_progress(
    progress_service,
    event_publisher,
):
    """Test hook behavior when no progress is provided."""
    # Call hook without progress
    await publish_progress_update(
        progress_service=progress_service,
        event_publisher=event_publisher,
    )

    # Verify no publication occurred
    event_publisher.publish_progress_update.assert_not_called()


@pytest.mark.asyncio
async def test_publish_progress_update_hook_default_type(
    progress_service,
    event_publisher,
    test_progress,
):
    """Test progress update hook with default update type."""
    # Call hook without update_type
    await publish_progress_update(
        progress_service=progress_service,
        event_publisher=event_publisher,
        progress=test_progress,
    )

    # Verify progress was published with default type
    event_publisher.publish_progress_update.assert_called_once_with(
        test_progress,
        "other",
    )
