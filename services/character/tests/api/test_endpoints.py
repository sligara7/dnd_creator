"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from character_service.api.v2.models import (
    CharacterCreate,
    CharacterResponse,
    InventoryItemCreate,
    InventoryItemUpdate,
    JournalEntryCreate,
    JournalEntryResponse,
)
from character_service.domain.models import Character, JournalEntry


class TestCharacterEndpoints:
    """Tests for character endpoints."""

    def test_list_characters(self, test_client: TestClient, character_service):
        """Test listing characters."""
        user_id = uuid4()
        response = test_client.get(f"/api/v2/characters?user_id={user_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_create_character(
        self,
        test_client: TestClient,
        character_service,
        test_character_data: CharacterCreate,
    ):
        """Test creating a character."""
        response = test_client.post(
            "/api/v2/characters",
            json=test_character_data.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_character_data.name
        assert data["theme"] == test_character_data.theme
        assert data["user_id"] == str(test_character_data.user_id)

    async def test_get_character(self, test_client: TestClient, character_service):
        """Test getting a character."""
        # Create character first
        user_id = uuid4()
        campaign_id = uuid4()
        character = Character.create_new(
            name="Test Character",
            user_id=user_id,
            campaign_id=campaign_id,
        )
        await character_service.create_character(character)

        # Get character
        response = test_client.get(f"/api/v2/characters/{character.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(character.id)
        assert data["name"] == character.name
        assert data["theme"] == character.theme


class TestInventoryEndpoints:
    """Tests for inventory endpoints."""

    def test_get_character_inventory(
        self, test_client: TestClient, inventory_service, character_service
    ):
        """Test getting character inventory."""
        character_id = uuid4()
        response = test_client.get(f"/api/v2/inventory/{character_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_add_inventory_item(
        self,
        test_client: TestClient,
        inventory_service,
        test_character_data: CharacterCreate,
        test_inventory_item_data: InventoryItemCreate,
    ):
        """Test adding an inventory item."""
        # First create character
        character = await character_service.create_character(**test_character_data.model_dump())

        response = test_client.post(
            f"/api/v2/inventory/{character.id}/items",
            json=test_inventory_item_data.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["character_id"] == str(character.id)
        assert data["item_data"]["name"] == test_inventory_item_data.item_data["name"]

    def test_update_inventory_item(
        self, test_client: TestClient, inventory_service
    ):
        """Test updating an inventory item."""
        item_id = uuid4()
        update_data = InventoryItemUpdate(
            quantity=2,
            equipped=True,
        )
        response = test_client.put(
            f"/api/v2/inventory/items/{item_id}",
            json=update_data.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJournalEndpoints:
    """Tests for journal endpoints."""

    def test_get_character_journal(
        self, test_client: TestClient, journal_service
    ):
        """Test getting character journal."""
        character_id = uuid4()
        response = test_client.get(f"/api/v2/journals/{character_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_create_journal_entry(
        self,
        test_client: TestClient,
        journal_service,
        character_service,
        test_character_data: CharacterCreate,
        test_journal_entry_data: JournalEntryCreate,
    ):
        """Test creating a journal entry."""
        # First create character
        character = await character_service.create_character(**test_character_data.model_dump())

        response = test_client.post(
            f"/api/v2/journals/{character.id}",
            json=test_journal_entry_data.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["character_id"] == str(character.id)
        assert data["title"] == test_journal_entry_data.title
        assert data["entry_type"] == test_journal_entry_data.entry_type

    def test_get_session_entries(
        self, test_client: TestClient, journal_service
    ):
        """Test getting session entries."""
        character_id = uuid4()
        session_number = 1
        response = test_client.get(
            f"/api/v2/journals/{character_id}/session/{session_number}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_journal_entry(
        self, test_client: TestClient, journal_service
    ):
        """Test getting a journal entry."""
        entry_id = uuid4()
        response = test_client.get(f"/api/v2/journals/entries/{entry_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
