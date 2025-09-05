"""Base test case for theme system tests."""
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, AsyncMock

from character_service.domain.theme import (
    Theme,
    ThemeCategory,
    ThemeTransitionType,
    ThemeState,
    ThemeValidationError,
    ThemeValidationResult,
)
from character_service.services.theme_transition import ThemeTransitionService
from character_service.services.theme_state import ThemeStateManager
from character_service.validation.theme_validator import ValidationContext, ThemeValidator
from character_service.clients.theme_integration import (
    ThemeIntegrationManager,
    CampaignServiceClient,
    LLMServiceClient,
    MessageHubClient,
    ThemeCacheClient,
)


class MockCharacter:
    """Mock character for testing."""

    def __init__(
        self,
        id: UUID = None,
        level: int = 1,
        class_name: str = "Fighter",
        race: str = "Human",
        ability_scores: Optional[Dict[str, int]] = None,
    ):
        self.id = id or uuid4()
        self.level = level
        self.class_name = class_name
        self.race = race
        
        # Set ability scores
        scores = ability_scores or {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }
        for ability, score in scores.items():
            setattr(self, f"{ability}_score", score)


class MockTheme:
    """Mock theme for testing."""

    def __init__(
        self,
        id: UUID = None,
        name: str = "Test Theme",
        category: ThemeCategory = ThemeCategory.BACKGROUND,
        level_requirement: int = 1,
        class_restrictions: List[str] = None,
        race_restrictions: List[str] = None,
        ability_adjustments: Dict[str, int] = None,
    ):
        self.id = id or uuid4()
        self.name = name
        self.category = category
        self.level_requirement = level_requirement
        self.class_restrictions = class_restrictions or []
        self.race_restrictions = race_restrictions or []
        self.ability_adjustments = ability_adjustments or {}


class MockThemeState:
    """Mock theme state for testing."""

    def __init__(
        self,
        id: UUID = None,
        character_id: UUID = None,
        theme_id: UUID = None,
        active: bool = True,
        transition_type: ThemeTransitionType = ThemeTransitionType.STORY,
        transition_time: datetime = None,
    ):
        self.id = id or uuid4()
        self.character_id = character_id
        self.theme_id = theme_id
        self.active = active
        self.transition_type = transition_type
        self.transition_time = transition_time or datetime.utcnow()

    def dict(self) -> Dict[str, Any]:
        """Convert state to dict."""
        return {
            "id": str(self.id),
            "character_id": str(self.character_id),
            "theme_id": str(self.theme_id),
            "active": self.active,
            "transition_type": self.transition_type.value,
            "transition_time": self.transition_time.isoformat(),
        }


@pytest.fixture
def character() -> MockCharacter:
    """Create a mock character."""
    return MockCharacter(
        level=5,
        class_name="Fighter",
        race="Human",
        ability_scores={
            "strength": 15,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 13,
        },
    )


@pytest.fixture
def from_theme() -> MockTheme:
    """Create a mock source theme."""
    return MockTheme(
        name="Previous Theme",
        category=ThemeCategory.BACKGROUND,
        ability_adjustments={"strength": 2},
    )


@pytest.fixture
def to_theme() -> MockTheme:
    """Create a mock destination theme."""
    return MockTheme(
        name="New Theme",
        category=ThemeCategory.CLASS,
        level_requirement=5,
        class_restrictions=["Fighter", "Paladin"],
        ability_adjustments={"strength": 1, "constitution": 1},
    )


@pytest.fixture
def theme_state(character: MockCharacter, from_theme: MockTheme) -> MockThemeState:
    """Create a mock theme state."""
    return MockThemeState(
        character_id=character.id,
        theme_id=from_theme.id,
        transition_type=ThemeTransitionType.STORY,
    )


@pytest_asyncio.fixture
async def mock_character_service(character: MockCharacter) -> AsyncMock:
    """Create a mock character service."""
    service = AsyncMock()
    service.get_character.return_value = character
    return service


@pytest_asyncio.fixture
async def mock_state_manager(theme_state: MockThemeState) -> AsyncMock:
    """Create a mock state manager."""
    manager = AsyncMock()
    manager.get_active_theme_state.return_value = theme_state
    manager.calculate_state_changes.return_value = {
        "ability_changes": {
            "strength": -1,  # Net change from removing +2 and adding +1
            "constitution": 1,
        }
    }
    manager.transition_theme_state.return_value = theme_state
    return manager


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Create a mock database session."""
    session = AsyncMock()
    return session


@pytest_asyncio.fixture
async def mock_integration_manager() -> AsyncMock:
    """Create a mock integration manager."""
    manager = AsyncMock()
    manager.campaign = AsyncMock(spec=CampaignServiceClient)
    manager.llm = AsyncMock(spec=LLMServiceClient)
    manager.message_hub = AsyncMock(spec=MessageHubClient)
    manager.cache = AsyncMock(spec=ThemeCacheClient)
    return manager


@pytest_asyncio.fixture
async def theme_service(
    mock_character_service: AsyncMock,
    mock_state_manager: AsyncMock,
    mock_session: AsyncMock,
    mock_integration_manager: AsyncMock,
) -> ThemeTransitionService:
    """Create a theme transition service for testing."""
    return ThemeTransitionService(
        character_service=mock_character_service,
        state_manager=mock_state_manager,
        session=mock_session,
        integration_manager=mock_integration_manager,
    )
