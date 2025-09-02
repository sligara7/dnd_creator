"""Tests for repositories."""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.models import Character, InventoryItem, JournalEntry
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.inventory import InventoryRepository
from character_service.infrastructure.repositories.journal import (
    ExperienceEntryRepository,
    JournalEntryRepository,
    NPCRelationshipRepository,
    QuestRepository,
)


class TestCharacterRepository:
    """Tests for CharacterRepository."""

    @pytest.fixture
    async def test_character(self) -> Character:
        """Test character."""
        return Character.create_new(
            name="Test Character",
            user_id=uuid4(),
            campaign_id=uuid4(),
            theme="traditional",
        )

    async def test_create_character(
        self, db_session: AsyncSession, test_character: Character
    ):
        """Test creating a character."""
        repository = CharacterRepository(db_session)
        db_character = repository.to_db_model(test_character)
        created = await repository.create(db_character)

        assert created is not None
        assert created.name == test_character.name
        assert created.theme == test_character.theme

    async def test_get_character(
        self, db_session: AsyncSession, test_character: Character
    ):
        """Test getting a character."""
        repository = CharacterRepository(db_session)
        db_character = repository.to_db_model(test_character)
        await repository.create(db_character)

        retrieved = await repository.get(test_character.id)
        assert retrieved is not None
        assert retrieved.id == test_character.id
        assert retrieved.name == test_character.name

    async def test_get_by_user_id(
        self, db_session: AsyncSession, test_character: Character
    ):
        """Test getting characters by user ID."""
        repository = CharacterRepository(db_session)
        db_character = repository.to_db_model(test_character)
        await repository.create(db_character)

        retrieved = await repository.get_by_user_id(test_character.user_id)
        assert len(retrieved) == 1
        assert retrieved[0].id == test_character.id


class TestInventoryRepository:
    """Tests for InventoryRepository."""

    @pytest.fixture
    def test_item(self, test_character: Character) -> InventoryItem:
        """Test inventory item."""
        return InventoryItem(
            id=uuid4(),
            root_id=None,
            theme=test_character.theme,
            character_id=test_character.id,
            item_data={
                "name": "Test Item",
                "type": "weapon",
                "weight": 2,
                "cost": {"gold": 1, "silver": 0, "copper": 0},
                "damage": {
                    "type": "slashing",
                    "dice": {"count": 1, "size": 8},
                },
                "properties": ["versatile"],
            },
            quantity=1,
            equipped=False,
            container=None,
            notes="Test notes",
            is_deleted=False,
            deleted_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def test_create_item(
        self, db_session: AsyncSession, test_character: Character, test_item: InventoryItem
    ):
        """Test creating an inventory item."""
        char_repo = CharacterRepository(db_session)
        db_character = char_repo.to_db_model(test_character)
        await char_repo.create(db_character)

        repository = InventoryRepository(db_session)
        db_item = repository.to_db_model(test_item)
        created = await repository.create(db_item)

        assert created is not None
        assert created.character_id == test_character.id
        assert created.item_data == test_item.item_data

    async def test_get_by_character_id(
        self, db_session: AsyncSession, test_character: Character, test_item: InventoryItem
    ):
        """Test getting items by character ID."""
        # Create character
        char_repo = CharacterRepository(db_session)
        db_character = char_repo.to_db_model(test_character)
        await char_repo.create(db_character)

        # Create item
        repository = InventoryRepository(db_session)
        db_item = repository.to_db_model(test_item)
        await repository.create(db_item)

        # Get items
        retrieved = await repository.get_by_character_id(test_character.id)
        assert len(retrieved) == 1
        assert retrieved[0].id == test_item.id


class TestJournalRepository:
    """Tests for JournalRepository."""

    @pytest.fixture
    def test_entry(self, test_character: Character) -> JournalEntry:
        """Test journal entry."""
        return JournalEntry(
            id=uuid4(),
            character_id=test_character.id,
            entry_type="session_log",
            timestamp=datetime.utcnow(),
            title="Test Entry",
            content="Test content",
            data={},
            tags=["test"],
            session_number=1,
            session_date=datetime.utcnow(),
            dm_name="Test DM",
            session_summary="Test summary",
            is_deleted=False,
            deleted_at=None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def test_create_entry(
        self, db_session: AsyncSession, test_character: Character, test_entry: JournalEntry
    ):
        """Test creating a journal entry."""
        # Create character
        char_repo = CharacterRepository(db_session)
        db_character = char_repo.to_db_model(test_character)
        await char_repo.create(db_character)

        # Create entry
        repository = JournalEntryRepository(db_session)
        db_entry = repository.to_db_model(test_entry)
        created = await repository.create(db_entry)

        assert created is not None
        assert created.character_id == test_character.id
        assert created.title == test_entry.title

    async def test_get_by_character_id(
        self, db_session: AsyncSession, test_character: Character, test_entry: JournalEntry
    ):
        """Test getting entries by character ID."""
        # Create character
        char_repo = CharacterRepository(db_session)
        db_character = char_repo.to_db_model(test_character)
        await char_repo.create(db_character)

        # Create entry
        repository = JournalEntryRepository(db_session)
        db_entry = repository.to_db_model(test_entry)
        await repository.create(db_entry)

        # Get entries
        retrieved = await repository.get_by_character_id(test_character.id)
        assert len(retrieved) == 1
        assert retrieved[0].id == test_entry.id
