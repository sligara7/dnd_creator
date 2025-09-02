"""Tests for service layer."""
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from character_service.domain.models import Character, CharacterData, JournalEntry
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.journal import JournalEntryRepository
from character_service.services.character import CharacterServiceImpl
from character_service.services.inventory import InventoryServiceImpl
from character_service.services.journal import JournalServiceImpl


class TestCharacterService:
    """Tests for CharacterService."""

    @pytest.fixture
    def character_repository(self) -> MagicMock:
        """Mock character repository."""
        return MagicMock(spec=CharacterRepository)

    @pytest.fixture
    def character_service(self, character_repository: MagicMock) -> CharacterServiceImpl:
        """Create character service with mocked repository."""
        return CharacterServiceImpl(character_repository)

    async def test_create_character(
        self, character_service: CharacterServiceImpl, character_repository: MagicMock
    ):
        """Test creating a character."""
        # Setup
        user_id = uuid4()
        campaign_id = uuid4()
        name = "Test Character"
        theme = "traditional"
        character_data = CharacterData.create_default()

        # Configure mock
        mock_character = Character.create_new(
            name=name,
            user_id=user_id,
            campaign_id=campaign_id,
            theme=theme,
            character_data=character_data,
        )
        character_repository.create = AsyncMock(return_value=mock_character)
        character_repository.to_domain = MagicMock(return_value=mock_character)

        # Execute
        result = await character_service.create_character(
            name=name,
            theme=theme,
            user_id=user_id,
            campaign_id=campaign_id,
            character_data=character_data,
        )

        # Assert
        assert result is not None
        assert result.name == name
        assert result.theme == theme
        assert result.user_id == user_id
        assert result.campaign_id == campaign_id
        assert result.character_data == character_data
        assert result.is_active is True

    async def test_get_characters_by_user(
        self, character_service: CharacterServiceImpl, character_repository: MagicMock
    ):
        """Test getting characters by user ID."""
        # Setup
        user_id = uuid4()
        mock_characters = [
            Character.create_new(
                name=f"Test Character {i}",
                user_id=user_id,
                campaign_id=uuid4(),
            )
            for i in range(2)
        ]
        character_repository.get_by_user_id = AsyncMock(return_value=mock_characters)
        character_repository.to_domain = MagicMock(side_effect=lambda x: x)

        # Execute
        result = await character_service.get_characters_by_user(user_id)

        # Assert
        assert result is not None
        assert len(result) == 2
        assert all(c.user_id == user_id for c in result)


class TestJournalService:
    """Tests for JournalService."""

    @pytest.fixture
    def journal_repository(self) -> MagicMock:
        """Mock journal repository."""
        return MagicMock(spec=JournalEntryRepository)

    @pytest.fixture
    def character_repository(self) -> MagicMock:
        """Mock character repository."""
        return MagicMock(spec=CharacterRepository)

    @pytest.fixture
    def experience_repository(self) -> MagicMock:
        """Mock experience repository."""
        return MagicMock()

    @pytest.fixture
    def quest_repository(self) -> MagicMock:
        """Mock quest repository."""
        return MagicMock()

    @pytest.fixture
    def npc_relationship_repository(self) -> MagicMock:
        """Mock NPC relationship repository."""
        return MagicMock()

    @pytest.fixture
    def journal_service(
        self,
        journal_repository: MagicMock,
        character_repository: MagicMock,
        experience_repository: MagicMock,
        quest_repository: MagicMock,
        npc_relationship_repository: MagicMock,
    ) -> JournalServiceImpl:
        """Create journal service with mocked repositories."""
        return JournalServiceImpl(
            journal_repository,
            character_repository,
            experience_repository,
            quest_repository,
            npc_relationship_repository,
        )

    async def test_create_entry(
        self, journal_service: JournalServiceImpl, journal_repository: MagicMock
    ):
        """Test creating a journal entry."""
        # Setup
        character_id = uuid4()
        mock_entry = JournalEntry(
            id=uuid4(),
            character_id=character_id,
            entry_type="session_log",
            timestamp=datetime.utcnow(),
            title="Test Entry",
            content="Test content",
        )
        journal_repository.create = AsyncMock(return_value=mock_entry)
        journal_repository.to_domain = MagicMock(return_value=mock_entry)

        # Execute
        result = await journal_service.create_entry(
            character_id=character_id,
            entry_type="session_log",
            title="Test Entry",
            content="Test content",
        )

        # Assert
        assert result is not None
        assert result.character_id == character_id
        assert result.title == "Test Entry"
        assert result.entry_type == "session_log"

    async def test_get_character_entries(
        self, journal_service: JournalServiceImpl, journal_repository: MagicMock
    ):
        """Test getting journal entries for a character."""
        # Setup
        character_id = uuid4()
        mock_entries = [
            JournalEntry(
                id=uuid4(),
                character_id=character_id,
                entry_type="session_log",
                timestamp=datetime.utcnow(),
                title=f"Test Entry {i}",
                content=f"Test content {i}",
            )
            for i in range(2)
        ]
        journal_repository.get_by_character_id = AsyncMock(return_value=mock_entries)
        journal_repository.to_domain = MagicMock(side_effect=lambda x: x)

        # Execute
        result = await journal_service.get_character_entries(character_id)

        # Assert
        assert result is not None
        assert len(result) == 2
        assert all(e.character_id == character_id for e in result)
