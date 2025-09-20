"""Test storage port integration."""

from datetime import datetime
import pytest
from uuid import UUID, uuid4

from character_service.clients.storage_port import (
    StoragePort,
    CharacterData,
    InventoryItemData,
    JournalEntryData,
    ExperienceEntryData,
    QuestData,
    NPCRelationshipData,
    CampaignEventData,
    EventImpactData,
    CharacterProgressData
)

from tests.mocks.storage_mock import MockStorageService

@pytest.fixture
def storage() -> StoragePort:
    return MockStorageService()

@pytest.mark.asyncio
async def test_character_lifecycle(storage: StoragePort):
    """Test basic character CRUD operations."""
    # Create
    char_data = {
        "name": "Test Character",
        "user_id": str(uuid4()),
        "campaign_id": str(uuid4()),
        "theme": "traditional",
        "is_active": True,
        "data": {
            "level": 1,
            "race": "Human",
            "class": "Fighter"
        }
    }
    created = await storage.create_character(char_data)
    assert created is not None
    assert created["name"] == char_data["name"]
    assert created["theme"] == char_data["theme"]
    assert created["data"]["level"] == 1

    # Get
    retrieved = await storage.get_character(UUID(created["id"]))
    assert retrieved is not None
    assert retrieved["id"] == created["id"]
    assert retrieved["name"] == char_data["name"]

    # Update
    update_data = {
        "name": "Updated Character",
        "data": {
            "level": 2,
            "race": "Human",
            "class": "Fighter"
        }
    }
    updated = await storage.update_character(UUID(created["id"]), update_data)
    assert updated is not None
    assert updated["name"] == "Updated Character"
    assert updated["data"]["level"] == 2

    # List
    chars = await storage.list_characters(
        user_id=UUID(created["user_id"]),
        campaign_id=UUID(created["campaign_id"]),
        theme=created["theme"]
    )
    assert len(chars) > 0
    assert any(c["id"] == created["id"] for c in chars)

    # Delete
    deleted = await storage.delete_character(UUID(created["id"]))
    assert deleted is True

    # Verify deletion
    deleted_char = await storage.get_character(UUID(created["id"]))
    assert deleted_char is not None
    assert not deleted_char["is_active"]

@pytest.mark.asyncio
async def test_inventory_operations(storage: StoragePort):
    """Test inventory item operations."""
    # Create character first
    char_data = {
        "name": "Test Character",
        "user_id": str(uuid4()),
        "campaign_id": str(uuid4()),
        "theme": "traditional",
        "is_active": True,
        "data": {}
    }
    char = await storage.create_character(char_data)
    char_id = UUID(char["id"])

    # Create item
    item_data = {
        "character_id": str(char_id),
        "name": "Test Item",
        "equipped": False,
        "container": "backpack",
        "is_deleted": False,
        "data": {
            "type": "weapon",
            "damage": "1d6",
            "weight": 2
        }
    }
    item = await storage.create_inventory_item(item_data)
    assert item is not None
    assert item["name"] == item_data["name"]
    assert not item["equipped"]

    # Get item
    retrieved = await storage.get_inventory_item(UUID(item["id"]), char_id)
    assert retrieved is not None
    assert retrieved["id"] == item["id"]
    assert retrieved["name"] == item_data["name"]

    # Update item
    update_data = {
        "name": "Updated Item",
        "equipped": True
    }
    updated = await storage.update_inventory_item(UUID(item["id"]), update_data)
    assert updated is not None
    assert updated["name"] == "Updated Item"
    assert updated["equipped"]

    # List items
    items = await storage.list_inventory_items(char_id)
    assert len(items) > 0
    assert any(i["id"] == item["id"] for i in items)

    # Filter by equipped
    equipped = await storage.list_inventory_items(char_id, equipped_only=True)
    assert len(equipped) > 0
    assert all(i["equipped"] for i in equipped)

    # Delete item
    deleted = await storage.delete_inventory_item(UUID(item["id"]))
    assert deleted is True

    # Verify deletion
    items = await storage.list_inventory_items(char_id, include_deleted=False)
    assert not any(i["id"] == item["id"] for i in items)

@pytest.mark.asyncio
async def test_journal_operations(storage: StoragePort):
    """Test journal entry operations."""
    # Create character first
    char_data = {
        "name": "Test Character",
        "user_id": str(uuid4()),
        "campaign_id": str(uuid4()),
        "theme": "traditional",
        "is_active": True,
        "data": {}
    }
    char = await storage.create_character(char_data)
    char_id = UUID(char["id"])

    # Create entry
    entry_data = {
        "character_id": str(char_id),
        "title": "Test Entry",
        "content": "Test content",
        "entry_type": "session",
        "is_deleted": False,
        "data": {
            "session_number": 1,
            "xp_gained": 100
        }
    }
    entry = await storage.create_journal_entry(entry_data)
    assert entry is not None
    assert entry["title"] == entry_data["title"]

    # Get entry
    retrieved = await storage.get_journal_entry(UUID(entry["id"]), char_id)
    assert retrieved is not None
    assert retrieved["id"] == entry["id"]
    assert retrieved["title"] == entry_data["title"]

    # Update entry
    update_data = {
        "title": "Updated Entry",
        "content": "Updated content"
    }
    updated = await storage.update_journal_entry(UUID(entry["id"]), update_data)
    assert updated is not None
    assert updated["title"] == "Updated Entry"
    assert updated["content"] == "Updated content"

    # List entries
    entries = await storage.list_journal_entries(char_id)
    assert len(entries) > 0
    assert any(e["id"] == entry["id"] for e in entries)

    # Delete entry
    deleted = await storage.delete_journal_entry(UUID(entry["id"]))
    assert deleted is True

    # Verify deletion
    entries = await storage.list_journal_entries(char_id, include_deleted=False)
    assert not any(e["id"] == entry["id"] for e in entries)