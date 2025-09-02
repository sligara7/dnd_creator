"""Tests for domain models."""
from datetime import datetime
from uuid import uuid4

import pytest

from character_service.domain.models import (
    Character,
    CharacterData,
    ExperienceEntry,
    InventoryItem,
    JournalEntry,
    NPCRelationship,
    Quest,
)


class TestCharacterData:
    """Tests for CharacterData class."""

    def test_create_default(self):
        """Test creating default character data."""
        default_data = CharacterData.create_default()
        assert default_data["level"] == 1
        assert default_data["ability_scores"]["strength"] == 10
        assert "hit_points" in default_data
        assert "spells" in default_data

    def test_ability_scores(self):
        """Test ability scores dictionary."""
        default_data = CharacterData.create_default()
        for ability in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            assert ability in default_data["ability_scores"]
            assert 1 <= default_data["ability_scores"][ability] <= 20

    def test_hit_points(self):
        """Test hit points dictionary."""
        default_data = CharacterData.create_default()
        assert "maximum" in default_data["hit_points"]
        assert "current" in default_data["hit_points"]
        assert "temporary" in default_data["hit_points"]
        assert "hit_dice_total" in default_data["hit_points"]
        assert "hit_dice_current" in default_data["hit_points"]

    def test_features_and_traits(self):
        """Test features and traits dictionaries."""
        default_data = CharacterData.create_default()
        assert "features" in default_data
        assert isinstance(default_data["features"], dict)
        assert "traits" in default_data
        assert isinstance(default_data["traits"], dict)


class TestCharacter:
    """Tests for Character class."""

    def test_create_new(self):
        """Test creating new character."""
        user_id = uuid4()
        campaign_id = uuid4()
        character = Character.create_new(
            name="Test Character",
            user_id=user_id,
            campaign_id=campaign_id,
        )

        assert character.name == "Test Character"
        assert character.theme == "traditional"
        assert character.user_id == user_id
        assert character.campaign_id == campaign_id
        assert character.character_data == CharacterData.create_default()
        assert character.is_active is True


class TestInventoryItem:
    """Tests for InventoryItem class."""

    @pytest.fixture
    def test_item_data(self) -> dict:
        """Test item data."""
        return {
            "name": "Test Sword",
            "type": "weapon",
            "weight": 3,
            "cost": {"gold": 15, "silver": 0, "copper": 0},
            "damage": {
                "type": "slashing",
                "dice": {"count": 1, "size": 8},
            },
            "properties": ["versatile"],
        }

    def test_create_item(self, test_item_data):
        """Test creating inventory item."""
        character_id = uuid4()
        item = InventoryItem(
            id=uuid4(),
            root_id=None,
            theme="traditional",
            character_id=character_id,
            item_data=test_item_data,
            quantity=1,
            equipped=False,
            container=None,
            notes="Test notes",
            is_deleted=False,
            deleted_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert item.item_data == test_item_data
        assert item.quantity == 1
        assert item.equipped is False
        assert item.container is None
        assert item.notes == "Test notes"


class TestJournalEntry:
    """Tests for JournalEntry class."""

    def test_create_entry(self):
        """Test creating journal entry."""
        character_id = uuid4()
        entry = JournalEntry(
            id=uuid4(),
            character_id=character_id,
            entry_type="session_log",
            timestamp=datetime.utcnow(),
            title="Test Entry",
            content="Test content",
            data={},
            tags=["test", "session"],
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

        assert entry.entry_type == "session_log"
        assert entry.title == "Test Entry"
        assert entry.content == "Test content"
        assert entry.tags == ["test", "session"]
        assert entry.session_number == 1
        assert entry.dm_name == "Test DM"
        assert entry.session_summary == "Test summary"


class TestExperienceEntry:
    """Tests for ExperienceEntry class."""

    def test_create_experience_entry(self):
        """Test creating experience entry."""
        journal_entry_id = uuid4()
        session_id = uuid4()
        entry = ExperienceEntry(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            amount=100,
            source="combat",
            reason="Defeated a monster",
            timestamp=datetime.utcnow(),
            session_id=session_id,
            data={"monster_type": "goblin"},
            is_deleted=False,
            deleted_at=None,
        )

        assert entry.amount == 100
        assert entry.source == "combat"
        assert entry.reason == "Defeated a monster"
        assert entry.session_id == session_id
        assert entry.data == {"monster_type": "goblin"}


class TestQuest:
    """Tests for Quest class."""

    def test_create_quest(self):
        """Test creating quest."""
        journal_entry_id = uuid4()
        quest = Quest(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            title="Test Quest",
            description="Test description",
            status="active",
            importance="normal",
            assigned_by="Test NPC",
            rewards={"gold": 100},
            progress=[{"step": 1, "description": "Start quest"}],
            data={"location": "Test Location"},
            is_deleted=False,
            deleted_at=None,
        )

        assert quest.title == "Test Quest"
        assert quest.description == "Test description"
        assert quest.status == "active"
        assert quest.importance == "normal"
        assert quest.assigned_by == "Test NPC"
        assert quest.rewards == {"gold": 100}
        assert quest.progress == [{"step": 1, "description": "Start quest"}]
        assert quest.data == {"location": "Test Location"}


class TestNPCRelationship:
    """Tests for NPCRelationship class."""

    def test_create_npc_relationship(self):
        """Test creating NPC relationship."""
        journal_entry_id = uuid4()
        npc_id = uuid4()
        relationship = NPCRelationship(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            npc_id=npc_id,
            npc_name="Test NPC",
            relationship_type="ally",
            standing=1,
            notes="Test notes",
            last_interaction=datetime.utcnow(),
            data={"faction": "Test Faction"},
            is_deleted=False,
            deleted_at=None,
        )

        assert relationship.npc_id == npc_id
        assert relationship.npc_name == "Test NPC"
        assert relationship.relationship_type == "ally"
        assert relationship.standing == 1
        assert relationship.notes == "Test notes"
        assert relationship.data == {"faction": "Test Faction"}
