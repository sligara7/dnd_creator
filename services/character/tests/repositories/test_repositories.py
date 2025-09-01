"""Repository Tests"""

import uuid
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from character_service.repositories.character_repository import CharacterRepository
from character_service.repositories.journal_repository import JournalRepository
from character_service.repositories.inventory_repository import InventoryRepository
from character_service.models.models import Character
from character_service.schemas.schemas import (
    CharacterCreate,
    CharacterUpdate,
    JournalEntryCreate,
    JournalEntryUpdate,
    InventoryItemCreate,
    InventoryItemUpdate
)

async def create_test_character(repo: CharacterRepository) -> Character:
    """Helper to create a test character via repository."""
    character_data = {
        "name": "Test Character",
        "user_id": "test_user",
        "campaign_id": "test_campaign",
        "character_data": {
            "species": "Human",
            "background": "Folk Hero",
            "level": 1,
            "class_": "Fighter",
            "alignment": "Lawful Good",
            "abilities": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            },
            "skills": ["Athletics", "Intimidation"],
            "equipment": {"weapons": ["Longsword", "Shield"]}
        }
    }
    return await repo.create(CharacterCreate(**character_data))
@pytest.mark.asyncio
async def test_character_repository(db_session: AsyncSession):
    """Test character repository operations."""
    repo = CharacterRepository(db_session)

    # Test create
    character = await create_test_character(repo)
    assert character.name == "Test Character"
    assert character.user_id == "test_user"

    # Test get
    retrieved = await repo.get(character.id)
    assert retrieved.id == character.id
    assert retrieved.name == character.name

    # Test get all
    characters = await repo.get_all(limit=10, offset=0)
    assert len(characters) > 0
    assert any(c.id == character.id for c in characters)

    # Test update
    update_data = CharacterUpdate(**{**character_data, "name": "Updated Character"})
    updated = await repo.update(character.id, update_data)
    assert updated.name == "Updated Character"

    # Test delete
    assert await repo.delete(character.id) is True
    assert await repo.get(character.id) is None

@pytest.mark.asyncio
async def test_journal_repository(db_session: AsyncSession):
    """Test journal repository operations."""
    char_repo = CharacterRepository(db_session)
    character = await create_test_character(char_repo)

    repo = JournalRepository(db_session)

    # Test create
    entry_data = JournalEntryCreate(
        character_id=character.id,
        timestamp=datetime.utcnow(),
        title="Test Entry",
        content="Test content",
        entry_type="session"
    )
    entry = await repo.create(entry_data)
    assert entry.title == "Test Entry"
    assert entry.character_id == character.id

    # Test get
    retrieved = await repo.get(entry.id)
    assert retrieved.id == entry.id
    assert retrieved.title == entry.title

    # Test get by character
    entries = await repo.get_all_by_character(character.id)
    assert len(entries) > 0
    assert entries[0].character_id == character.id

    # Test update
    update_data = JournalEntryUpdate(title="Updated Entry")
    updated = await repo.update(entry.id, update_data)
    assert updated.title == "Updated Entry"

    # Test delete
    assert await repo.delete(entry.id) is True
    assert await repo.get(entry.id) is None

@pytest.mark.asyncio
async def test_inventory_repository(db_session: AsyncSession):
    """Test inventory repository operations."""
    char_repo = CharacterRepository(db_session)
    character = await create_test_character(char_repo)

    repo = InventoryRepository(db_session)

    # Test create
    item_data = InventoryItemCreate(
        character_id=character.id,
        item_data={
            "name": "Test Sword",
            "type": "weapon",
            "damage": "1d8"
        },
        quantity=1
    )
    item = await repo.create(item_data)
    assert item.item_data["name"] == "Test Sword"
    assert item.character_id == character.id

    # Test get
    retrieved = await repo.get(item.id)
    assert retrieved.id == item.id
    assert retrieved.item_data["name"] == "Test Sword"

    # Test get by character
    items = await repo.get_all_by_character(character.id)
    assert len(items) > 0
    assert items[0].character_id == character.id

    # Test update
    update_data = InventoryItemUpdate(
        item_data={
            "name": "Updated Sword",
            "type": "weapon",
            "damage": "1d8"
        },
        quantity=2
    )
    updated = await repo.update(item.id, update_data)
    assert updated.item_data["name"] == "Updated Sword"
    assert updated.quantity == 2

    # Test delete
    assert await repo.delete(item.id) is True
    assert await repo.get(item.id) is None

@pytest.mark.asyncio
async def test_repository_error_handling(db_session: AsyncSession):
    """Test repository error handling."""
    char_repo = CharacterRepository(db_session)
    journal_repo = JournalRepository(db_session)
    inventory_repo = InventoryRepository(db_session)

    # Test get non-existent items
    assert await char_repo.get(999999) is None
    assert await journal_repo.get(999999) is None
    assert await inventory_repo.get(999999) is None

    # Test update non-existent items
    assert await char_repo.update(999999, CharacterUpdate(name="Test")) is None
    assert await journal_repo.update(999999, JournalEntryUpdate(title="Test")) is None
    assert await inventory_repo.update(999999, InventoryItemUpdate(quantity=1)) is None

    # Test delete non-existent items
    assert await char_repo.delete(999999) is False
    assert await journal_repo.delete(999999) is False
    assert await inventory_repo.delete(999999) is False
