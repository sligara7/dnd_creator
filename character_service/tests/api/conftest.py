"""API test configuration and fixtures."""
from typing import AsyncGenerator, Dict
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.api.app import create_app
from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository
from character_service.services.character import AbilityScores


@pytest.fixture
async def test_repository(db_manager) -> CharacterRepository:
    """Create a test repository instance.
    
    Args:
        db_manager: Database session manager
        
    Returns:
        Test repository instance
    """
    async with db_manager as session:
        yield CharacterRepository(session)


@pytest.fixture
async def app(test_repository: CharacterRepository):
    """Create test FastAPI application.
    
    Args:
        test_repository: Repository instance for testing
        
    Returns:
        FastAPI application
    """
    app = create_app(repository=test_repository)
    yield app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client.
    
    Args:
        app: FastAPI application
        
    Yields:
        Test HTTP client
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def valid_character_data() -> Dict:
    """Create valid character data for testing.
    
    Returns:
        Character creation data
    """
    return {
        "name": "Test Character",
        "ability_scores": {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        },
        "race": "Human",
        "character_class": "Fighter",
        "background": "Soldier",
        "level": 1
    }


@pytest.fixture
async def test_character(test_repository: CharacterRepository, valid_character_data: Dict) -> Character:
    """Create a test character in the database.
    
    Args:
        test_repository: Repository for database operations
        valid_character_data: Character creation data
        
    Returns:
        Created character instance
    """
    # Create character directly with ability score values
    scores = valid_character_data["ability_scores"]
    
    # Calculate max hit points (10 + CON mod for first level Fighter)
    con_mod = (scores["constitution"] - 10) // 2
    max_hp = 10 + con_mod
    
    return await test_repository.create(
        Character(
            id=uuid4(),
            name=valid_character_data["name"],
            strength=scores["strength"],
            dexterity=scores["dexterity"],
            constitution=scores["constitution"],
            intelligence=scores["intelligence"],
            wisdom=scores["wisdom"],
            charisma=scores["charisma"],
            max_hit_points=max_hp,
            current_hit_points=max_hp,
            temporary_hit_points=0,
            race=valid_character_data["race"],
            character_class=valid_character_data["character_class"],
            background=valid_character_data["background"],
            level=valid_character_data["level"]
        )
    )
