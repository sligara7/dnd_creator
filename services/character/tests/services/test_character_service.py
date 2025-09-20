"""Tests for character service implementation."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

import pytest
from pytest_mock import MockerFixture

from character_service.clients.storage_port import (
    StoragePort,
    CharacterData,
    InventoryItemData,
    JournalEntryData
)
from character_service.services.character_service_impl import CharacterServiceImpl

class MockStoragePort:
    """Mock storage port for testing."""

    def __init__(self):
        self.characters: Dict[UUID, CharacterData] = {}
        self.inventory_items: Dict[UUID, InventoryItemData] = {}
        self.journal_entries: Dict[UUID, JournalEntryData] = {}

    async def get_character(self, character_id: UUID) -> Optional[CharacterData]:
        """Get a character by ID."""
        return self.characters.get(character_id)

    async def list_characters(self, **kwargs) -> List[CharacterData]:
        """List characters with filters."""
        chars = list(self.characters.values())
        if kwargs.get("active_only", True):
            chars = [c for c in chars if c.is_active]
        if "user_id" in kwargs:
            chars = [c for c in chars if c.user_id == kwargs["user_id"]]
        if "campaign_id" in kwargs:
            chars = [c for c in chars if c.campaign_id == kwargs["campaign_id"]]
        return chars[kwargs.get("offset", 0):kwargs.get("offset", 0) + kwargs.get("limit", 100)]

    async def create_character(self, data: CharacterData) -> CharacterData:
        """Create a new character."""
        self.characters[data.character_id] = data
        return data

    async def update_character(
        self,
        character_id: UUID,
        data: Dict,
        version: Optional[UUID] = None
    ) -> Optional[CharacterData]:
        """Update a character."""
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
        """Soft delete a character."""
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

@pytest.fixture
def storage() -> StoragePort:
    return MockStoragePort()

@pytest.fixture
def service(storage: StoragePort) -> CharacterServiceImpl:
    return CharacterServiceImpl(storage)

@pytest.mark.asyncio
async def test_create_character(service: CharacterServiceImpl):
    # Arrange
    name = "Test Character"
    theme = "traditional"
    user_id = uuid4()
    campaign_id = uuid4()
    character_data = {
        "level": 1,
        "class": "Fighter",
        "race": "Human"
    }

    # Act
    result = await service.create_character(
        name=name,
        theme=theme,
        user_id=user_id,
        campaign_id=campaign_id,
        character_data=character_data
    )

    # Assert
    assert result is not None
    assert result.name == name
    assert result.theme == theme
    assert result.user_id == user_id
    assert result.campaign_id == campaign_id
    assert result.data == character_data
    assert result.is_active is True

@pytest.mark.asyncio
async def test_get_character(service: CharacterServiceImpl, storage: MockStoragePort):
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
            "class": "Fighter",
            "race": "Human"
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    # Act
    result = await service.get_character(char_id)

    # Assert
    assert result is not None
    assert result.character_id == char_id
    assert result.name == char_data.name
    assert result.data == char_data.data

@pytest.mark.asyncio
async def test_get_characters_by_user(service: CharacterServiceImpl, storage: MockStoragePort):
    # Arrange
    user_id = uuid4()
    campaign_id = uuid4()
    
    active_char = CharacterData(
        character_id=uuid4(),
        name="Active Character",
        user_id=user_id,
        campaign_id=campaign_id,
        theme="traditional",
        data={},
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    inactive_char = CharacterData(
        character_id=uuid4(),
        name="Inactive Character",
        user_id=user_id,
        campaign_id=campaign_id,
        theme="traditional",
        data={},
        is_active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    other_user_char = CharacterData(
        character_id=uuid4(),
        name="Other User's Character",
        user_id=uuid4(),  # Different user
        campaign_id=campaign_id,
        theme="traditional",
        data={},
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    storage.characters[active_char.character_id] = active_char
    storage.characters[inactive_char.character_id] = inactive_char
    storage.characters[other_user_char.character_id] = other_user_char

    # Act
    result = await service.get_characters_by_user(user_id)

    # Assert
    assert len(result) == 1
    assert result[0].name == "Active Character"
    assert result[0].user_id == user_id
    assert result[0].is_active is True

@pytest.mark.asyncio
async def test_get_characters_by_campaign(service: CharacterServiceImpl, storage: MockStoragePort):
    # Arrange
    campaign_id = uuid4()
    
    active_char = CharacterData(
        character_id=uuid4(),
        name="Active Character",
        user_id=uuid4(),
        campaign_id=campaign_id,
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
        campaign_id=campaign_id,
        theme="traditional",
        data={},
        is_active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    other_campaign_char = CharacterData(
        character_id=uuid4(),
        name="Other Campaign's Character",
        user_id=uuid4(),
        campaign_id=uuid4(),  # Different campaign
        theme="traditional",
        data={},
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    storage.characters[active_char.character_id] = active_char
    storage.characters[inactive_char.character_id] = inactive_char
    storage.characters[other_campaign_char.character_id] = other_campaign_char

    # Act
    result = await service.get_characters_by_campaign(campaign_id)

    # Assert
    assert len(result) == 1
    assert result[0].name == "Active Character"
    assert result[0].campaign_id == campaign_id
    assert result[0].is_active is True

@pytest.mark.asyncio
async def test_update_character(service: CharacterServiceImpl, storage: MockStoragePort):
    # Arrange
    char_id = uuid4()
    char_data = CharacterData(
        character_id=char_id,
        name="Original Name",
        user_id=uuid4(),
        campaign_id=uuid4(),
        theme="traditional",
        data={
            "level": 1
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    storage.characters[char_id] = char_data

    updated_char = CharacterData(
        **{
            **char_data.model_dump(),
            "name": "Updated Name",
            "data": {
                "level": 2
            }
        }
    )

    # Act
    result = await service.update_character(updated_char)

    # Assert
    assert result is not None
    assert result.name == "Updated Name"
    assert result.data["level"] == 2
    assert result.is_active is True

@pytest.mark.asyncio
async def test_delete_character(service: CharacterServiceImpl, storage: MockStoragePort):
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
    result = await service.delete_character(char_id)

    # Assert
    assert result is True
    assert storage.characters[char_id].is_active is False