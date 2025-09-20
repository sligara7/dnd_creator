"""Storage port interface for character service storage access.

This module defines the interface for accessing character data through the storage service.
It follows the ports and adapters pattern, allowing us to switch storage implementations
while maintaining a consistent interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# Enums
class EventType(str, Enum):
    """Character event types."""
    LEVEL_UP = "level_up"
    MILESTONE = "milestone"
    QUEST_COMPLETE = "quest_complete"
    ACHIEVEMENT = "achievement"
    STORY_DEVELOPMENT = "story_development"
    CAMPAIGN_EVENT = "campaign_event"
    DEATH = "death"
    RESURRECTION = "resurrection"
    THEME_TRANSITION = "theme_transition"
    PARTY_ROLE = "party_role"
    TRAINING = "training"
    CUSTOM = "custom"

class MilestoneType(str, Enum):
    """Character milestone types."""
    LEVEL = "level"
    QUEST = "quest"
    STORY = "story"
    ACHIEVEMENT = "achievement"
    THEME = "theme"
    CAMPAIGN = "campaign"
    CUSTOM = "custom"

class ProgressType(str, Enum):
    """Character progress types."""
    XP = "xp"
    MILESTONE = "milestone"
    HYBRID = "hybrid"
    CUSTOM = "custom"

class AchievementCategory(str, Enum):
    """Achievement categories."""
    COMBAT = "combat"
    ROLEPLAY = "roleplay"
    EXPLORATION = "exploration"
    STORY = "story"
    THEME = "theme"
    PARTY = "party"
    CUSTOM = "custom"

class Difficulty(str, Enum):
    """Achievement difficulty."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"
    LEGENDARY = "legendary"

class ItemRarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class ItemType(str, Enum):
    """Types of items."""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SCROLL = "scroll"
    RING = "ring"
    ROD = "rod"
    STAFF = "staff"
    WAND = "wand"
    WONDROUS = "wondrous"
    AMMUNITION = "ammunition"
    CONTAINER = "container"
    CURRENCY = "currency"
    OTHER = "other"

class ItemLocation(str, Enum):
    """Where an item is located."""
    EQUIPPED = "equipped"
    CARRIED = "carried"
    STORED = "stored"
    CONTAINER = "container"
    MOUNT = "mount"
    BANK = "bank"
    VAULT = "vault"

class AttunementState(str, Enum):
    """States for magic item attunement."""
    NONE = "none"
    ATTUNED = "attuned"
    ATTUNING = "attuning"
    BROKEN = "broken"

class EffectType(str, Enum):
    """Types of magic item effects."""
    PASSIVE = "passive"
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CHARGED = "charged"
    CURSE = "curse"

class EffectDurationType(str, Enum):
    """Types of effect durations."""
    INSTANT = "instant"
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    UNTIL_DAWN = "until_dawn"
    UNTIL_DUSK = "until_dusk"
    UNTIL_LONG_REST = "until_long_rest"
    UNTIL_SHORT_REST = "until_short_rest"
    CHARGES = "charges"

class ChangeType(str, Enum):
    """Types of character changes."""
    ABILITY_SCORE = "ability_score"
    CLASS_FEATURE = "class_feature"
    EQUIPMENT = "equipment"
    LEVEL = "level"
    PROFICIENCY = "proficiency"
    RESOURCE = "resource"
    SPELL = "spell"
    THEME = "theme"
    OTHER = "other"

class ChangeSource(str, Enum):
    """Sources of character changes."""
    USER = "user"
    STORY = "story"
    THEME = "theme"
    CAMPAIGN = "campaign"
    SYSTEM = "system"

# Message types for storage service communication

class CharacterData(BaseModel):
    """Character data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    character_id: UUID
    parent_id: Optional[UUID] = None
    theme: str
    name: str
    user_id: UUID
    campaign_id: UUID
    data: Dict[str, Any]  # JSONB equivalent
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class InventoryItemData(BaseModel):
    """Inventory item data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    item_id: UUID
    root_id: Optional[UUID] = None
    theme: str
    character_id: UUID
    data: Dict[str, Any]  # JSONB equivalent
    quantity: int = 1
    equipped: bool = False
    container: Optional[str] = None
    notes: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ExperienceEntryData(BaseModel):
    """Experience entry data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    entry_id: UUID
    journal_entry_id: UUID
    amount: int
    source: str
    reason: str
    timestamp: datetime
    session_id: Optional[UUID] = None
    data: Dict[str, Any] = {}  # JSONB equivalent
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class QuestData(BaseModel):
    """Quest data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    quest_id: UUID
    journal_entry_id: UUID
    title: str
    description: str
    status: str = 'active'
    importance: str = 'normal'
    assigned_by: Optional[str] = None
    rewards: Dict[str, Any] = {}  # JSONB equivalent
    progress: List[Dict[str, Any]] = []  # JSONB equivalent
    data: Dict[str, Any] = {}  # JSONB equivalent
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class NPCRelationshipData(BaseModel):
    """NPC relationship data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    relationship_id: UUID
    journal_entry_id: UUID
    npc_id: UUID
    npc_name: str
    relationship_type: str
    standing: int = 0
    notes: Optional[str] = None
    last_interaction: Optional[datetime] = None
    data: Dict[str, Any] = {}  # JSONB equivalent
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class CampaignEventData(BaseModel):
    """Campaign event data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    event_id: UUID
    character_id: UUID
    journal_entry_id: Optional[UUID] = None
    event_type: str
    event_data: Dict[str, Any] = {}  # JSONB equivalent
    impact_type: str
    impact_magnitude: int
    timestamp: datetime
    applied: bool = False
    applied_at: Optional[datetime] = None
    data: Dict[str, Any] = {}  # JSONB equivalent
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class EventImpactData(BaseModel):
    """Event impact data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    impact_id: UUID
    event_id: UUID
    character_id: UUID
    impact_type: str
    impact_data: Dict[str, Any] = {}  # JSONB equivalent
    applied: bool = False
    applied_at: Optional[datetime] = None
    reversion_data: Optional[Dict[str, Any]] = None  # JSONB equivalent
    is_reverted: bool = False
    reverted_at: Optional[datetime] = None
    notes: Optional[str] = None
    data: Dict[str, Any] = {}  # JSONB equivalent
    created_at: datetime
    updated_at: datetime

class CharacterProgressData(BaseModel):
    """Character progress data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    progress_id: UUID
    character_id: UUID
    experience_points: int = 0
    milestones: List[Dict[str, Any]] = []  # JSONB equivalent
    achievements: List[Dict[str, Any]] = []  # JSONB equivalent
    current_level: int = 1
    previous_level: int = 1
    level_updated_at: Optional[datetime] = None
    data: Dict[str, Any] = {}  # JSONB equivalent
    created_at: datetime
    updated_at: datetime

class JournalEntryData(BaseModel):
    """Journal entry data model for storage service messages."""
    model_config = ConfigDict(frozen=True)

    entry_id: UUID
    character_id: UUID
    entry_type: str
    timestamp: datetime
    title: str
    content: str
    data: Dict[str, Any] = {}  # JSONB equivalent
    tags: List[str] = []
    session_number: Optional[int] = None
    session_date: Optional[datetime] = None
    dm_name: Optional[str] = None
    session_summary: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

# Version control enums and models

class VersionNodeType(str, Enum):
    """Types of version nodes."""
    CHARACTER = "character"
    EQUIPMENT = "equipment"
    ABILITY = "ability"
    FEATURE = "feature"

class EdgeType(str, Enum):
    """Types of version edges."""
    PARENT = "parent"  # Previous version
    ROOT = "root"    # Original theme version
    EQUIPPED = "equipped"  # Equipment equipped by character
    CREATED = "created"   # Content created for character

class VersionNode(BaseModel):
    """Version node representing a versioned entity."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    graph_id: UUID
    entity_id: UUID
    node_type: VersionNodeType
    theme: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class VersionEdge(BaseModel):
    """Version edge representing a relationship between nodes."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    graph_id: UUID
    source_id: UUID  # From node
    target_id: UUID  # To node
    edge_type: EdgeType
    metadata: Dict[str, Any] = {}
    created_at: datetime

class VersionGraph(BaseModel):
    """Version graph containing nodes and edges."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    name: str
    description: Optional[str] = None
    nodes: List[VersionNode] = []
    edges: List[VersionEdge] = []
    created_at: datetime
    updated_at: datetime

class CharacterEvent(BaseModel):
    """Character event model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    event_type: EventType
    title: str
    description: Optional[str]
    impact: Dict[str, Any]
    campaign_event_id: Optional[UUID]
    metadata: Dict[str, Any]
    is_processed: bool = False
    processed_at: Optional[datetime]
    created_at: datetime
    milestones: List["CharacterMilestone"] = []

class CharacterMilestone(BaseModel):
    """Character milestone model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    event_id: Optional[UUID]
    milestone_type: MilestoneType
    title: str
    description: Optional[str]
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    campaign_milestone_id: Optional[UUID]
    completed: bool = False
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime

class CharacterProgress(BaseModel):
    """Character progress model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    milestone_id: Optional[UUID]
    progress_type: ProgressType
    current_xp: int = 0
    total_xp: int = 0
    current_level: int = 1
    milestones_completed: int = 0
    level_progression: Dict[str, Any]
    requirements: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ProgressSnapshot(BaseModel):
    """Progress snapshot model for state capture."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    event_id: Optional[UUID]
    snapshot_type: str
    state_before: Dict[str, Any]
    state_after: Optional[Dict[str, Any]]
    diff: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime

class CharacterAchievement(BaseModel):
    """Character achievement model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    title: str
    description: str
    category: AchievementCategory
    difficulty: Difficulty
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    points: int = 0
    campaign_achievement_id: Optional[UUID]
    completed: bool = False
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ItemEffect(BaseModel):
    """Model for magic item effects."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    name: str
    description: str
    effect_type: EffectType
    duration_type: EffectDurationType
    duration_value: Optional[int]
    activation_type: Optional[str]
    activation_cost: Optional[Dict[str, Any]]
    saving_throw: Optional[Dict[str, Any]]
    effect_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    items: List[UUID] = []

class InventoryItem(BaseModel):
    """Base model for inventory items."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    container_id: Optional[UUID]
    name: str
    description: Optional[str]
    item_type: ItemType
    location: ItemLocation
    quantity: int = 1
    weight: float = 0.0
    value: int = 0
    item_metadata: Optional[Dict[str, Any]]
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

class Container(InventoryItem):
    """Model for containers (bags, chests, etc.)."""
    capacity: float = 0.0
    capacity_type: str = "weight"
    is_magical: bool = False
    restrictions: Optional[List[str]] = None

class MagicItem(InventoryItem):
    """Model for magic items."""
    rarity: ItemRarity
    requires_attunement: bool = False
    attunement_requirements: Optional[List[str]] = None
    attunement_state: AttunementState = AttunementState.NONE
    attunement_date: Optional[datetime]
    charges: Optional[int]
    max_charges: Optional[int]
    recharge_type: Optional[str]
    last_recharged: Optional[datetime]
    effects: List[ItemEffect] = []

class CharacterVersion(BaseModel):
    """Character version model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    parent_version_id: Optional[UUID]
    label: Optional[str]
    description: Optional[str]
    state: Dict[str, Any]
    changes: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime
    created_by: str

class CharacterChange(BaseModel):
    """Character change model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    character_id: UUID
    version_id: UUID
    change_type: ChangeType
    source: ChangeSource
    attribute_path: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    created_by: str

class VersionMetadata(BaseModel):
    """Version metadata model."""
    model_config = ConfigDict(frozen=True)

    id: UUID
    version_id: UUID
    character_id: UUID
    level: int
    class_name: str
    active_theme_id: Optional[UUID]
    ability_scores: Dict[str, int]
    campaign_id: Optional[UUID]
    branch_point: Optional[UUID]
    is_milestone: bool = False
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class StoragePort(Protocol):
    """Protocol defining the storage service interface for character data."""

    # Version control methods

    async def create_graph(self, name: str, description: str = None) -> VersionGraph:
        """Create a new version graph."""
        ...

    async def add_node(
        self, 
        graph_id: UUID,
        entity_id: UUID,
        node_type: VersionNodeType,
        theme: str,
        metadata: Dict[str, Any] = None
    ) -> VersionNode:
        """Add a node to a version graph."""
        ...

    async def add_edge(
        self,
        graph_id: UUID,
        source_id: UUID,
        target_id: UUID,
        edge_type: EdgeType,
        metadata: Dict[str, Any] = None
    ) -> VersionEdge:
        """Add an edge to a version graph."""
        ...

    async def get_graph_by_id(self, graph_id: UUID) -> Optional[VersionGraph]:
        """Get a version graph by ID."""
        ...

    async def get_node_by_entity(
        self,
        entity_id: UUID,
        node_type: Optional[VersionNodeType] = None,
        theme: Optional[str] = None
    ) -> Optional[VersionNode]:
        """Get a version node by entity ID, optionally filtered by type and theme."""
        ...

    async def get_node_chain(
        self,
        node_id: UUID,
        edge_type: EdgeType
    ) -> List[VersionNode]:
        """Get a chain of nodes connected by edges of the specified type."""
        ...

    async def get_node_relationships(
        self,
        node_id: UUID,
        edge_type: Optional[EdgeType] = None
    ) -> List[tuple[VersionEdge, VersionNode]]:
        """Get all nodes related to the given node by specified edge type."""
        ...

    async def get_character(self, character_id: UUID) -> Optional[CharacterData]:
        """Get a character by ID."""
        ...

    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[CharacterData]:
        """List characters with optional filters."""
        ...

    async def create_character(self, data: CharacterData) -> CharacterData:
        """Create a new character."""
        ...

    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any],
        version: Optional[UUID] = None
    ) -> CharacterData:
        """Update a character.
        
        Args:
            character_id: The character ID
            data: Fields to update
            version: Optional version ID for optimistic locking
        """
        ...

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        ...

    # Inventory methods

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[InventoryItemData]:
        """Get an inventory item by ID."""
        ...

    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryItemData]:
        """List inventory items for a character."""
        ...

    async def create_inventory_item(
        self,
        data: InventoryItemData
    ) -> InventoryItemData:
        """Create a new inventory item."""
        ...

    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict[str, Any]
    ) -> InventoryItemData:
        """Update an inventory item."""
        ...

    async def delete_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> bool:
        """Soft delete an inventory item."""
        ...

    # Journal methods

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[JournalEntryData]:
        """Get a journal entry by ID."""
        ...

    async def list_journal_entries(
        self,
        character_id: UUID,
        entry_type: Optional[str] = None,
        session_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntryData]:
        """List journal entries for a character."""
        ...

    async def create_journal_entry(
        self,
        data: JournalEntryData
    ) -> JournalEntryData:
        """Create a new journal entry."""
        ...

    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict[str, Any]
    ) -> JournalEntryData:
        """Update a journal entry."""
        ...

    async def delete_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> bool:
        """Soft delete a journal entry."""
        ...

    # Experience entry methods

    async def get_experience_entry(
        self,
        entry_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[ExperienceEntryData]:
        """Get an experience entry by ID."""
        ...

    async def list_experience_entries(
        self,
        journal_entry_id: UUID,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExperienceEntryData]:
        """List experience entries for a journal entry."""
        ...

    async def create_experience_entry(
        self,
        data: ExperienceEntryData
    ) -> ExperienceEntryData:
        """Create a new experience entry."""
        ...

    async def update_experience_entry(
        self,
        entry_id: UUID,
        data: Dict[str, Any]
    ) -> ExperienceEntryData:
        """Update an experience entry."""
        ...

    async def delete_experience_entry(
        self,
        entry_id: UUID
    ) -> bool:
        """Soft delete an experience entry."""
        ...

    # Quest methods

    async def get_quest(
        self,
        quest_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[QuestData]:
        """Get a quest by ID."""
        ...

    async def list_quests(
        self,
        journal_entry_id: UUID,
        status: Optional[str] = None,
        importance: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[QuestData]:
        """List quests for a journal entry."""
        ...

    async def create_quest(
        self,
        data: QuestData
    ) -> QuestData:
        """Create a new quest."""
        ...

    async def update_quest(
        self,
        quest_id: UUID,
        data: Dict[str, Any]
    ) -> QuestData:
        """Update a quest."""
        ...

    async def delete_quest(
        self,
        quest_id: UUID
    ) -> bool:
        """Soft delete a quest."""
        ...

    # NPC relationship methods

    async def get_npc_relationship(
        self,
        relationship_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[NPCRelationshipData]:
        """Get an NPC relationship by ID."""
        ...

    async def list_npc_relationships(
        self,
        journal_entry_id: UUID,
        relationship_type: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[NPCRelationshipData]:
        """List NPC relationships for a journal entry."""
        ...

    async def create_npc_relationship(
        self,
        data: NPCRelationshipData
    ) -> NPCRelationshipData:
        """Create a new NPC relationship."""
        ...

    async def update_npc_relationship(
        self,
        relationship_id: UUID,
        data: Dict[str, Any]
    ) -> NPCRelationshipData:
        """Update an NPC relationship."""
        ...

    async def delete_npc_relationship(
        self,
        relationship_id: UUID
    ) -> bool:
        """Soft delete an NPC relationship."""
        ...

    # Campaign event methods

    async def get_campaign_event(
        self,
        event_id: UUID,
        character_id: Optional[UUID] = None,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[CampaignEventData]:
        """Get a campaign event by ID."""
        ...

    async def list_campaign_events(
        self,
        character_id: UUID,
        event_type: Optional[str] = None,
        impact_type: Optional[str] = None,
        applied_only: bool = False,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[CampaignEventData]:
        """List campaign events for a character."""
        ...

    async def create_campaign_event(
        self,
        data: CampaignEventData
    ) -> CampaignEventData:
        """Create a new campaign event."""
        ...

    async def update_campaign_event(
        self,
        event_id: UUID,
        data: Dict[str, Any]
    ) -> CampaignEventData:
        """Update a campaign event."""
        ...

    async def delete_campaign_event(
        self,
        event_id: UUID
    ) -> bool:
        """Soft delete a campaign event."""
        ...

    # Event impact methods

    async def get_event_impact(
        self,
        impact_id: UUID,
        event_id: Optional[UUID] = None,
        character_id: Optional[UUID] = None
    ) -> Optional[EventImpactData]:
        """Get an event impact by ID."""
        ...

    async def list_event_impacts(
        self,
        event_id: Optional[UUID] = None,
        character_id: Optional[UUID] = None,
        applied_only: bool = False,
        reverted_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[EventImpactData]:
        """List event impacts."""
        ...

    async def create_event_impact(
        self,
        data: EventImpactData
    ) -> EventImpactData:
        """Create a new event impact."""
        ...

    async def update_event_impact(
        self,
        impact_id: UUID,
        data: Dict[str, Any]
    ) -> EventImpactData:
        """Update an event impact."""
        ...

    # Character progress methods

    async def get_character_progress(
        self,
        character_id: UUID
    ) -> Optional[CharacterProgressData]:
        """Get character progress."""
        ...

    async def update_character_progress(
        self,
        character_id: UUID,
        data: Dict[str, Any]
    ) -> CharacterProgressData:
        """Update character progress."""
        ...
