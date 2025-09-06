"""Tests for event and progress API endpoints."""
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from character_service.api.v2.routers.progress import router
from character_service.core.exceptions import (CharacterNotFoundError,
                                          EventApplicationError,
                                          EventNotFoundError,
                                          ValidationError)
from character_service.domain.event import EventImpactService
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.models import CampaignEvent, EventImpact, CharacterProgress


@pytest.fixture
def app(event_service: AsyncMock, progress_service: AsyncMock) -> FastAPI:
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[EventImpactService] = lambda: event_service
    app.dependency_overrides[ProgressTrackingService] = lambda: progress_service

    return app


@pytest.fixture
def event_service() -> AsyncMock:
    """Mock event service."""
    return AsyncMock()


@pytest.fixture
def progress_service() -> AsyncMock:
    """Mock progress service."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_event(app: FastAPI, event_service: AsyncMock):
    """Test creating a campaign event."""
    character_id = uuid4()
    event_id = uuid4()

    event = CampaignEvent(
        id=event_id,
        character_id=character_id,
        event_type="combat",
        event_data={"enemy": "goblin"},
        impact_type="hit_points",
        impact_magnitude=-5,
        timestamp=datetime.utcnow(),
    )
    event_service.create_event.return_value = event

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/events",
            json={
                "event_type": "combat",
                "event_data": {"enemy": "goblin"},
                "impact_type": "hit_points",
                "impact_magnitude": -5,
            },
        )

    assert response.status_code == 201
    assert response.json()["id"] == str(event_id)
    assert response.json()["character_id"] == str(character_id)
    assert response.json()["event_type"] == "combat"


@pytest.mark.asyncio
async def test_apply_event(app: FastAPI, event_service: AsyncMock):
    """Test applying a campaign event."""
    character_id = uuid4()
    event_id = uuid4()

    impact = EventImpact(
        id=uuid4(),
        event_id=event_id,
        character_id=character_id,
        impact_type="hit_points",
        impact_data={"amount": -5},
    )
    event_service.apply_event.return_value = [impact]

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/events/{event_id}/apply",
        )

    assert response.status_code == 200
    impacts = response.json()
    assert len(impacts) == 1
    assert impacts[0]["event_id"] == str(event_id)
    assert impacts[0]["impact_type"] == "hit_points"


@pytest.mark.asyncio
async def test_revert_event(app: FastAPI, event_service: AsyncMock):
    """Test reverting a campaign event."""
    character_id = uuid4()
    event_id = uuid4()

    impact = EventImpact(
        id=uuid4(),
        event_id=event_id,
        character_id=character_id,
        impact_type="hit_points",
        impact_data={"amount": -5},
        is_reverted=True,
        reverted_at=datetime.utcnow(),
    )
    event_service.revert_event.return_value = [impact]

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/characters/{character_id}/events/{event_id}",
        )

    assert response.status_code == 200
    impacts = response.json()
    assert len(impacts) == 1
    assert impacts[0]["event_id"] == str(event_id)
    assert impacts[0]["is_reverted"] is True


@pytest.mark.asyncio
async def test_add_experience(app: FastAPI, progress_service: AsyncMock):
    """Test adding experience points."""
    character_id = uuid4()
    progress_service.add_experience.return_value = (1000, True, {
        "previous_level": 1,
        "new_level": 3,
        "timestamp": datetime.utcnow().isoformat(),
    })

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/progress/experience",
            json={
                "amount": 1000,
                "source": "quest",
                "reason": "Completed quest",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_experience"] == 1000
    assert data["leveled_up"] is True
    assert data["level_data"]["previous_level"] == 1
    assert data["level_data"]["new_level"] == 3


@pytest.mark.asyncio
async def test_add_milestone(app: FastAPI, progress_service: AsyncMock):
    """Test adding a milestone."""
    character_id = uuid4()
    progress = CharacterProgress(
        id=uuid4(),
        character_id=character_id,
        experience_points=1000,
        current_level=3,
        previous_level=2,
        milestones=[{
            "id": str(uuid4()),
            "title": "First Quest",
            "description": "Completed first quest",
            "type": "quest",
            "achieved_at": datetime.utcnow().isoformat(),
        }],
    )
    progress_service.add_milestone.return_value = progress

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/progress/milestones",
            json={
                "title": "First Quest",
                "description": "Completed first quest",
                "milestone_type": "quest",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["milestones"]) == 1
    assert data["milestones"][0]["title"] == "First Quest"
    assert data["milestones"][0]["type"] == "quest"


@pytest.mark.asyncio
async def test_add_achievement(app: FastAPI, progress_service: AsyncMock):
    """Test adding an achievement."""
    character_id = uuid4()
    progress = CharacterProgress(
        id=uuid4(),
        character_id=character_id,
        experience_points=1000,
        current_level=3,
        previous_level=2,
        achievements=[{
            "id": str(uuid4()),
            "title": "Monster Slayer",
            "description": "Defeated first monster",
            "type": "combat",
            "achieved_at": datetime.utcnow().isoformat(),
        }],
    )
    progress_service.add_achievement.return_value = progress

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/progress/achievements",
            json={
                "title": "Monster Slayer",
                "description": "Defeated first monster",
                "achievement_type": "combat",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["achievements"]) == 1
    assert data["achievements"][0]["title"] == "Monster Slayer"
    assert data["achievements"][0]["type"] == "combat"


@pytest.mark.asyncio
async def test_get_character_progress(app: FastAPI, progress_service: AsyncMock):
    """Test getting character progress."""
    character_id = uuid4()
    progress = CharacterProgress(
        id=uuid4(),
        character_id=character_id,
        experience_points=1000,
        current_level=3,
        previous_level=2,
        milestones=[{
            "id": str(uuid4()),
            "title": "First Quest",
            "description": "Completed first quest",
            "type": "quest",
            "achieved_at": datetime.utcnow().isoformat(),
        }],
        achievements=[{
            "id": str(uuid4()),
            "title": "Monster Slayer",
            "description": "Defeated first monster",
            "type": "combat",
            "achieved_at": datetime.utcnow().isoformat(),
        }],
    )
    progress_service.get_character_progress.return_value = progress

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/characters/{character_id}/progress",
        )

    assert response.status_code == 200
    data = response.json()
    assert data["experience_points"] == 1000
    assert data["current_level"] == 3
    assert len(data["milestones"]) == 1
    assert len(data["achievements"]) == 1


@pytest.mark.asyncio
async def test_error_handling(app: FastAPI, event_service: AsyncMock):
    """Test error handling in endpoints."""
    character_id = uuid4()
    event_id = uuid4()

    # Test character not found
    event_service.create_event.side_effect = CharacterNotFoundError("Character not found")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/events",
            json={
                "event_type": "combat",
                "event_data": {"enemy": "goblin"},
                "impact_type": "hit_points",
                "impact_magnitude": -5,
            },
        )

    assert response.status_code == 404
    assert "Character not found" in response.json()["detail"]

    # Test event not found
    event_service.apply_event.side_effect = EventNotFoundError("Event not found")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/events/{event_id}/apply",
        )

    assert response.status_code == 404
    assert "Event not found" in response.json()["detail"]

    # Test validation error
    event_service.create_event.side_effect = ValidationError("Invalid input")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/characters/{character_id}/events",
            json={
                "event_type": "combat",
                "event_data": {"enemy": "goblin"},
                "impact_type": "hit_points",
                "impact_magnitude": -5,
            },
        )

    assert response.status_code == 422
    assert "Invalid input" in response.json()["detail"]
