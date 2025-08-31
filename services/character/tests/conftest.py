"""Test Configuration and Fixtures"""

import asyncio
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from character_service.core.database import get_db, Base
from character_service.main import app as character_app
from character_service.models.models import Character, JournalEntry, InventoryItem

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "DATABASE_TEST_URL",
    "postgresql://postgres:postgres@localhost:5432/character_service_test"
)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def app(test_db) -> FastAPI:
    """Create test FastAPI application."""
    character_app.dependency_overrides[get_db] = lambda: test_db
    return character_app

@pytest.fixture(scope="function")
def client(app) -> TestClient:
    """Create test client."""
    return TestClient(app)

@pytest.fixture(scope="function")
def test_character(test_db) -> Character:
    """Create test character."""
    character = Character(
        name="Test Character",
        user_id="test_user",
        campaign_id="test_campaign",
        character_data={
            "species": "Human",
            "background": "Folk Hero",
            "level": 1,
            "character_classes": {"Fighter": 1},
            "abilities": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        }
    )
    test_db.add(character)
    test_db.commit()
    test_db.refresh(character)
    return character

@pytest.fixture(scope="function")
def test_journal_entry(test_db, test_character) -> JournalEntry:
    """Create test journal entry."""
    entry = JournalEntry(
        character_id=test_character.id,
        title="Test Entry",
        content="Test content for journal entry",
        entry_type="session"
    )
    test_db.add(entry)
    test_db.commit()
    test_db.refresh(entry)
    return entry

@pytest.fixture(scope="function")
def test_inventory_item(test_db, test_character) -> InventoryItem:
    """Create test inventory item."""
    item = InventoryItem(
        character_id=test_character.id,
        item_data={
            "name": "Test Sword",
            "type": "weapon",
            "damage": "1d8",
            "properties": ["versatile"]
        },
        quantity=1
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item
