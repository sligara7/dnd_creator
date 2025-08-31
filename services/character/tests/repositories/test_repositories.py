"""Repository Tests"""

import pytest
from sqlalchemy.orm import Session

from character_service.repositories.character_repository import CharacterRepository
from character_service.repositories.journal_repository import JournalRepository
from character_service.repositories.inventory_repository import InventoryRepository
from character_service.models.models import Character, JournalEntry, InventoryItem

@pytest.mark.asyncio
async def test_character_repository(test_db: Session):
    """Test character repository operations."""
    repo = CharacterRepository(test_db)

    # Test create
    character_data = {
        "name": "Test Character",
        "user_id": "test_user",
        "campaign_id": "test_campaign",
        "character_data": {
            "species": "Human",
            "background": "Folk Hero",
            "level": 1
        }
    }
    character = await repo.create(character_data)
    assert character.name == "Test Character"
    assert character.user_id == "test_user"

    # Test get
    retrieved = await repo.get(character.id)
    assert retrieved.id == character.id
    assert retrieved.name == character.name

    # Test update
    update_data = {**character_data, "name": "Updated Character"}
    updated = await repo.update(character.id, update_data)
    assert updated.name == "Updated Character"

    # Test delete
    assert await repo.delete(character.id) is True
    assert await repo.get(character.id) is None

@pytest.mark.asyncio
async def test_journal_repository(test_db: Session, test_character: Character):
    """Test journal repository operations."""
    repo = JournalRepository(test_db)

    # Test create
    entry_data = {
        "character_id": test_character.id,
        "title": "Test Entry",
        "content": "Test content",
        "entry_type": "session"
    }
    entry = await repo.create(entry_data)
    assert entry.title == "Test Entry"
    assert entry.character_id == test_character.id

    # Test get
    retrieved = await repo.get(entry.id)
    assert retrieved.id == entry.id
    assert retrieved.title == entry.title

    # Test get by character
    entries = await repo.get_all_by_character(test_character.id)
    assert len(entries) > 0
    assert entries[0].character_id == test_character.id

    # Test update
    update_data = {**entry_data, "title": "Updated Entry"}
    updated = await repo.update(entry.id, update_data)
    assert updated.title == "Updated Entry"

@pytest.mark.asyncio
async def test_inventory_repository(test_db: Session, test_character: Character):
    """Test inventory repository operations."""
    repo = InventoryRepository(test_db)

    # Test create
    item_data = {
        "character_id": test_character.id,
        "item_data": {
            "name": "Test Sword",
            "type": "weapon",
            "damage": "1d8"
        },
        "quantity": 1
    }
    item = await repo.create(item_data)
    assert item.item_data["name"] == "Test Sword"
    assert item.character_id == test_character.id

    # Test get
    retrieved = await repo.get(item.id)
    assert retrieved.id == item.id
    assert retrieved.item_data["name"] == "Test Sword"

    # Test get by character
    items = await repo.get_all_by_character(test_character.id)
    assert len(items) > 0
    assert items[0].character_id == test_character.id

    # Test update
    update_data = {
        **item_data,
        "item_data": {
            **item_data["item_data"],
            "name": "Updated Sword"
        }
    }
    updated = await repo.update(item.id, update_data)
    assert updated.item_data["name"] == "Updated Sword"

    # Test delete
    assert await repo.delete(item.id) is True
    assert await repo.get(item.id) is None

@pytest.mark.asyncio
async def test_repository_error_handling(test_db: Session):
    """Test repository error handling."""
    char_repo = CharacterRepository(test_db)
    journal_repo = JournalRepository(test_db)
    inventory_repo = InventoryRepository(test_db)

    # Test get non-existent items
    assert await char_repo.get(999999) is None
    assert await journal_repo.get(999999) is None
    assert await inventory_repo.get(999999) is None

    # Test update non-existent items
    assert await char_repo.update(999999, {"name": "Test"}) is None
    assert await journal_repo.update(999999, {"title": "Test"}) is None
    assert await inventory_repo.update(999999, {"quantity": 1}) is None

    # Test delete non-existent items
    assert await char_repo.delete(999999) is False
    assert await journal_repo.delete(999999) is False
    assert await inventory_repo.delete(999999) is False
