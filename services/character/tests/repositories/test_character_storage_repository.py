"""Tests for the character storage repository."""

import pytest
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

from character_service.clients.storage_port import (
    StoragePort,
    CharacterData,
    InventoryItemData,
    JournalEntryData
)
from character_service.repositories.character_storage_repository import CharacterStorageRepository
from character_service.schemas.schemas import CharacterCreate, CharacterUpdate

class MockStoragePort:
    """Mock storage port for testing."""

    def __init__(self):
        self.characters: Dict[UUID, CharacterData] = {}
        self.inventory_items: Dict[UUID, InventoryItemData] = {}
        self.journal_entries: Dict[UUID, JournalEntryData] = {}

    async def get_character(self, character_id: UUID) -> CharacterData:
        return self.characters.get(character_id)

    async def list_characters(self, **kwargs) -> list[CharacterData]:
        chars = list(self.characters.values())
        if kwargs.get("active_only", True):
            chars = [c for c in chars if c.is_active]
        return chars[kwargs.get("offset", 0):kwargs.get("offset", 0) + kwargs.get("limit", 100)]

    async def create_character(self, data: CharacterData) -> CharacterData:
        self.characters[data.character_id] = data
        return data

    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any],
        version: UUID = None
    ) -> CharacterData:
        char = self.characters.get(character_id)
        if not char:
            return None
        
        updated = CharacterData(
            **{
                **char.model_dump(),
                **data,
                "updated_at": datetime.utcnow()
            }
        )
        self.characters[character_id] = updated
        return updated

    async def delete_character(self, character_id: UUID) -> bool:
        if character_id not in self.characters:
            return False
        char = self.characters[character_id]
        self.characters[character_id] = CharacterData(
            **{
                **char.model_dump(),
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        )
        return True

    # Inventory operations (implement as needed)
    async def get_inventory_item(self, item_id: UUID, character_id: UUID = None) -> InventoryItemData:
        return self.inventory_items.get(item_id)

    async def list_inventory_items(self, character_id: UUID, **kwargs) -> list[InventoryItemData]:
        items = [i for i in self.inventory_items.values() if i.character_id == character_id]
        if kwargs.get("equipped_only"):
            items = [i for i in items if i.equipped]
        if not kwargs.get("include_deleted"):
            items = [i for i in items if not i.is_deleted]
        return items[kwargs.get("offset", 0):kwargs.get("offset", 0) + kwargs.get("limit", 100)]

    # Journal operations (implement as needed)
    async def get_journal_entry(self, entry_id: UUID, character_id: UUID = None) -> JournalEntryData:
        return self.journal_entries.get(entry_id)

    async def list_journal_entries(self, character_id: UUID, **kwargs) -> list[JournalEntryData]:
        entries = [e for e in self.journal_entries.values() if e.character_id == character_id]
        if not kwargs.get("include_deleted"):
            entries = [e for e in entries if not e.is_deleted]
        return entries[kwargs.get("offset", 0):kwargs.get("offset", 0) + kwargs.get("limit", 100)]

@pytest.fixture
def storage() -> StoragePort:
    return MockStoragePort()

@pytest.fixture
def repository(storage: StoragePort) -> CharacterStorageRepository:
    return CharacterStorageRepository(storage)

@pytest.mark.asyncio
async def test_create_character(repository: CharacterStorageRepository):
    # Arrange
    char_data = CharacterCreate(
        name="Test Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        character_data={
            "level": 1,
            "race": "Human",
            "class": "Fighter"
        }
    )

    # Act
    result = await repository.create(char_data)

    # Assert
    assert result is not None
    assert result.name == char_data.name
    assert result.theme == char_data.theme
    assert result.data["level"] == 1
    assert result.data["race"] == "Human"
    assert result.is_active is True

@pytest.mark.asyncio
async def test_get_character(repository: CharacterStorageRepository, storage: MockStoragePort):
    # Arrange
    char_id = uuid4()
    char_data = CharacterData(
        character_id=char_id,
        name="Test Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={
            "level": 1,
            "race": "Human",
            "class": "Fighter"
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    # Act
    result = await repository.get(char_id)

    # Assert
    assert result is not None
    assert result.character_id == char_id
    assert result.name == char_data.name
    assert result.data == char_data.data

@pytest.mark.asyncio
async def test_update_character(repository: CharacterStorageRepository, storage: MockStoragePort):
    # Arrange
    char_id = uuid4()
    char_data = CharacterData(
        character_id=char_id,
        name="Test Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={
            "level": 1,
            "race": "Human",
            "class": "Fighter"
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    update_data = CharacterUpdate(
        name="Updated Character",
        character_data={
            "level": 2
        }
    )

    # Act
    result = await repository.update(char_id, update_data)

    # Assert
    assert result is not None
    assert result.name == "Updated Character"
    assert result.data["level"] == 2
    assert result.data["race"] == "Human"  # Original data preserved

@pytest.mark.asyncio
async def test_delete_character(repository: CharacterStorageRepository, storage: MockStoragePort):
    # Arrange
    char_id = uuid4()
    char_data = CharacterData(
        character_id=char_id,
        name="Test Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={},
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    # Act
    result = await repository.delete(char_id)

    # Assert
    assert result is True
    stored_char = storage.characters[char_id]
    assert stored_char.is_active is False

@pytest.mark.asyncio
async def test_list_active_characters(repository: CharacterStorageRepository, storage: MockStoragePort):
    # Arrange
    active_char = CharacterData(
        character_id=uuid4(),
        name="Active Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={},
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    inactive_char = CharacterData(
        character_id=uuid4(),
        name="Inactive Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={},
        is_active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[active_char.character_id] = active_char
    storage.characters[inactive_char.character_id] = inactive_char

    # Act
    result = await repository.get_all(limit=10, offset=0)

    # Assert
    assert len(result) == 1
    assert result[0].name == "Active Character"
    assert result[0].is_active is True

@pytest.mark.asyncio
async def test_update_evolution(repository: CharacterStorageRepository, storage: MockStoragePort):
    # Arrange
    char_id = uuid4()
    char_data = CharacterData(
        character_id=char_id,
        name="Test Character",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={
            "level": 1,
            "experience": 0
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    evolution_data = {
        "level": 2,
        "experience": 300
    }

    # Act
    result = await repository.update_evolution(char_id, evolution_data)

    # Assert
    assert result is not None
    assert result.data["level"] == 2
    assert result.data["experience"] == 300