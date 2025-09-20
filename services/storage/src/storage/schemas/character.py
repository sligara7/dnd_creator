from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    level: int = Field(default=1, ge=1, le=20)
    race: str = Field(..., min_length=1, max_length=255)
    character_class: str = Field(..., min_length=1, max_length=255)
    background: str = Field(..., min_length=1, max_length=255)
    alignment: Optional[str] = Field(None, max_length=50)
    experience_points: int = Field(default=0, ge=0)
    
    # Ability Scores
    strength: int = Field(..., ge=1, le=30)
    dexterity: int = Field(..., ge=1, le=30)
    constitution: int = Field(..., ge=1, le=30)
    intelligence: int = Field(..., ge=1, le=30)
    wisdom: int = Field(..., ge=1, le=30)
    charisma: int = Field(..., ge=1, le=30)

    # Character Stats
    max_hit_points: int = Field(..., ge=1)
    current_hit_points: int = Field(..., ge=0)
    temporary_hit_points: int = Field(default=0, ge=0)
    armor_class: int = Field(..., ge=0)
    initiative: int = Field(...)
    speed: int = Field(..., ge=0)
    inspiration: bool = Field(default=False)
    proficiency_bonus: int = Field(..., ge=0)

    # Character Details
    personality_traits: Optional[str] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None

    # Extended Data
    spells: List[Dict] = Field(default_factory=list)
    inventory: List[Dict] = Field(default_factory=list)
    features: List[Dict] = Field(default_factory=list)
    proficiencies: List[Dict] = Field(default_factory=list)
    campaign_notes: List[Dict] = Field(default_factory=list)
    journal_entries: List[Dict] = Field(default_factory=list)
    relationships: List[Dict] = Field(default_factory=list)

    # Theme and Campaign Data
    campaign_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    theme_data: Dict = Field(default_factory=dict)

class CharacterCreate(CharacterBase):
    creator_id: UUID
    owner_id: UUID

class CharacterUpdate(CharacterBase):
    pass

class CharacterInDB(CharacterBase):
    id: UUID
    creator_id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CharacterVersionBase(BaseModel):
    character_id: UUID
    version_number: int = Field(..., ge=1)
    change_type: str = Field(..., min_length=1, max_length=50)
    changes: Dict
    metadata: Dict = Field(default_factory=dict)

class CharacterVersionCreate(CharacterVersionBase):
    created_by: UUID

class CharacterVersionInDB(CharacterVersionBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CharacterProgressBase(BaseModel):
    character_id: UUID
    progress_type: str = Field(..., min_length=1, max_length=50)
    milestone: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., min_length=1, max_length=50)
    details: Dict = Field(default_factory=dict)

class CharacterProgressCreate(CharacterProgressBase):
    pass

class CharacterProgressUpdate(BaseModel):
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    details: Optional[Dict] = None
    completed_at: Optional[datetime] = None

class CharacterProgressInDB(CharacterProgressBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

"""Character database request/response schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Base models
class CharacterBase(BaseModel):
    """Base character data."""
    name: str
    player_name: Optional[str] = None
    class_name: str
    level: int
    background: str
    race: str
    alignment: str
    experience_points: int = 0
    
    # Character Details
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    eye_color: Optional[str] = None
    skin_color: Optional[str] = None
    hair_color: Optional[str] = None
    
    # Ability Scores
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Health & Resources
    max_hit_points: int
    current_hit_points: int
    temporary_hit_points: int = 0
    hit_dice_total: str
    hit_dice_current: int
    death_save_successes: int = 0
    death_save_failures: int = 0
    exhaustion_level: int = 0
    inspiration: bool = False
    
    # Proficiencies
    languages: List[str] = Field(default_factory=list)
    weapon_proficiencies: List[str] = Field(default_factory=list)
    armor_proficiencies: List[str] = Field(default_factory=list)
    tool_proficiencies: List[str] = Field(default_factory=list)
    saving_throw_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)
    
    # Character Personality
    personality_traits: List[str] = Field(default_factory=list)
    ideals: List[str] = Field(default_factory=list)
    bonds: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    
    # Rich Text Fields
    backstory: str = ""
    notes: str = ""
    
    # Foreign Keys
    theme_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    owner_id: UUID
    
    # Metadata
    metadata: Dict = Field(default_factory=dict)

class CharacterCreate(CharacterBase):
    """Character creation data."""
    pass

class CharacterUpdate(CharacterBase):
    """Character update data."""
    class Config:
        extra = "allow"

class CharacterResponse(CharacterBase):
    """Character response data."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    version: int = 1

    class Config:
        from_attributes = True

# Theme models
class ThemeBase(BaseModel):
    """Base theme data."""
    name: str
    description: str
    parent_id: Optional[UUID] = None
    metadata: Dict = Field(default_factory=dict)

class ThemeCreate(ThemeBase):
    """Theme creation data."""
    pass

class ThemeResponse(ThemeBase):
    """Theme response data."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Inventory models
class InventoryBase(BaseModel):
    """Base inventory data."""
    copper: int = 0
    silver: int = 0
    electrum: int = 0
    gold: int = 0
    platinum: int = 0
    armor_slot: Optional[UUID] = None
    shield_slot: Optional[UUID] = None
    weapon_slots: List[UUID] = Field(default_factory=list)
    attuned_items: List[UUID] = Field(default_factory=list)

class InventoryCreate(InventoryBase):
    """Inventory creation data."""
    pass

class InventoryResponse(InventoryBase):
    """Inventory response data."""
    id: UUID
    character_id: UUID

    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    """Base inventory item data."""
    name: str
    description: Optional[str] = None
    quantity: int = 1
    weight: float = 0.0
    value_cp: int = 0
    properties: Dict = Field(default_factory=dict)
    is_equipped: bool = False
    requires_attunement: bool = False
    is_attuned: bool = False

class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation data."""
    pass

class InventoryItemResponse(InventoryItemBase):
    """Inventory item response data."""
    id: UUID
    inventory_id: UUID

    class Config:
        from_attributes = True

# Spellcasting models
class SpellcastingBase(BaseModel):
    """Base spellcasting data."""
    spellcasting_ability: str
    spell_class: str
    slots_total: Dict[int, int] = Field(default_factory=dict)
    slots_expended: Dict[int, int] = Field(default_factory=dict)
    spells_known: List[UUID] = Field(default_factory=list)
    spells_prepared: List[UUID] = Field(default_factory=list)
    concentrating: bool = False
    concentration_spell_id: Optional[UUID] = None

class SpellcastingCreate(SpellcastingBase):
    """Spellcasting creation data."""
    pass

class SpellcastingResponse(SpellcastingBase):
    """Spellcasting response data."""
    id: UUID
    character_id: UUID

    class Config:
        from_attributes = True

# Journal entry models
class JournalEntryBase(BaseModel):
    """Base journal entry data."""
    session_date: datetime
    content: str
    xp_gained: int = 0
    milestones: List[str] = Field(default_factory=list)
    dm_notes: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    """Journal entry creation data."""
    pass

class JournalEntryResponse(JournalEntryBase):
    """Journal entry response data."""
    id: UUID
    character_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Condition models
class ConditionBase(BaseModel):
    """Base condition data."""
    condition_name: str
    source: Optional[str] = None
    duration: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class ConditionCreate(ConditionBase):
    """Condition creation data."""
    pass

class ConditionResponse(ConditionBase):
    """Condition response data."""
    id: UUID
    character_id: UUID

    class Config:
        from_attributes = True

# Class resource models
class ClassResourceBase(BaseModel):
    """Base class resource data."""
    name: str
    maximum: int
    current: int
    recharge: str = "long_rest"  # short_rest, long_rest, dawn

class ClassResourceCreate(ClassResourceBase):
    """Class resource creation data."""
    pass

class ClassResourceResponse(ClassResourceBase):
    """Class resource response data."""
    id: UUID
    character_id: UUID

    class Config:
        from_attributes = True

# Version graph models
class VersionGraphBase(BaseModel):
    """Base version graph data."""
    name: str
    description: Optional[str] = None

class VersionGraphCreate(VersionGraphBase):
    """Version graph creation data."""
    pass

class VersionGraphResponse(VersionGraphBase):
    """Version graph response data."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class VersionNodeBase(BaseModel):
    """Base version node data."""
    entity_id: UUID
    type: str
    theme: str
    node_metadata: Dict = Field(default_factory=dict)

class VersionNodeCreate(VersionNodeBase):
    """Version node creation data."""
    pass

class VersionNodeResponse(VersionNodeBase):
    """Version node response data."""
    id: UUID
    graph_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VersionEdgeBase(BaseModel):
    """Base version edge data."""
    source_id: UUID
    target_id: UUID
    type: str
    edge_metadata: Dict = Field(default_factory=dict)

class VersionEdgeCreate(VersionEdgeBase):
    """Version edge creation data."""
    pass

class VersionEdgeResponse(VersionEdgeBase):
    """Version edge response data."""
    id: UUID
    graph_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True