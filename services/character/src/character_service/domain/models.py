"""Core domain models for the Character Service."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


@dataclass
class CharacterData:
    """Character data stored in JSONB."""
    level: int
    race: str
    character_class: str
    ability_scores: Dict[str, int]
    hit_points: Dict[str, int]
    armor_class: int
    initiative: int
    speed: int
    proficiency_bonus: int
    features: Dict[str, Any]
    traits: Dict[str, str]
    resources: Dict[str, Any]
    equipment: Dict[str, Any]
    spells: Dict[str, Any]
    background: Dict[str, Any]
    notes: Dict[str, str]

    @staticmethod
    def create_default() -> Dict[str, Any]:
        """Create default character data."""
        return {
            "level": 1,
            "race": "",
            "character_class": "",
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            },
            "hit_points": {
                "maximum": 0,
                "current": 0,
                "temporary": 0,
                "hit_dice_total": 1,
                "hit_dice_current": 1,
            },
            "armor_class": 10,
            "initiative": 0,
            "speed": 30,
            "proficiency_bonus": 2,
            "features": {},
            "traits": {
                "personality": "",
                "ideals": "",
                "bonds": "",
                "flaws": "",
            },
            "resources": {
                "spell_slots": {},
                "class_resources": {},
            },
            "equipment": {
                "armor": None,
                "weapons": [],
                "other": [],
            },
            "spells": {
                "cantrips": [],
                "prepared": [],
                "known": [],
            },
            "background": {
                "name": "",
                "feature": "",
                "description": "",
            },
            "notes": {},
        }


@dataclass
class Character:
    """Core character domain model with JSONB data storage."""
    id: UUID
    parent_id: Optional[UUID]
    theme: str
    name: str
    user_id: UUID
    campaign_id: UUID
    character_data: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create_new(cls, name: str, user_id: UUID, campaign_id: UUID,
                theme: str = "traditional") -> "Character":
        """Create a new character with default data."""
        return cls(
            id=uuid4(),
            parent_id=None,
            theme=theme,
            name=name,
            user_id=user_id,
            campaign_id=campaign_id,
            character_data=CharacterData.create_default(),
        )


@dataclass
class InventoryItem:
    """Individual inventory item model."""
    id: UUID
    root_id: Optional[UUID]
    theme: str
    character_id: UUID
    item_data: Dict[str, Any]
    quantity: int = 1
    equipped: bool = False
    container: Optional[str] = None
    notes: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class JournalEntry:
    """Enhanced journal entry model."""
    id: UUID
    character_id: UUID
    entry_type: str
    timestamp: datetime
    title: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    session_number: Optional[int] = None
    session_date: Optional[datetime] = None
    dm_name: Optional[str] = None
    session_summary: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExperienceEntry:
    """Experience tracking model."""
    id: UUID
    journal_entry_id: UUID
    amount: int
    source: str
    reason: str
    timestamp: datetime
    session_id: Optional[UUID] = None
    data: Dict[str, Any] = field(default_factory=dict)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


@dataclass
class Quest:
    """Quest tracking model."""
    id: UUID
    journal_entry_id: UUID
    title: str
    description: str
    status: str = "active"
    importance: str = "normal"
    assigned_by: Optional[str] = None
    rewards: Dict[str, Any] = field(default_factory=dict)
    progress: List[Dict[str, Any]] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


@dataclass
class NPCRelationship:
    """NPC relationship tracking model."""
    id: UUID
    journal_entry_id: UUID
    npc_id: UUID
    npc_name: str
    relationship_type: str
    standing: int = 0
    notes: Optional[str] = None
    last_interaction: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
