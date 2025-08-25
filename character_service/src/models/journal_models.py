"""
Journal Entry Models

This module contains the models for character journal entries, including:
- Session logs
- Experience tracking
- Character development
- Relationships and quests
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

from src.core.logging_config import get_logger

logger = get_logger(__name__)

class Achievement(BaseModel):
    """A milestone or achievement reached by the character."""
    title: str = Field(..., description="Title of the achievement")
    description: str = Field(..., description="Description of what was achieved")
    reward_type: str = Field(..., description="Type of reward (XP, item, etc.)")
    reward_value: Any = Field(..., description="Value of the reward")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NPCRelationship(BaseModel):
    """Tracks a character's relationship with an NPC."""
    npc_id: str = Field(..., description="ID of the NPC")
    npc_name: str = Field(..., description="Name of the NPC")
    relationship_type: str = Field(..., description="Type of relationship (ally, enemy, etc.)")
    standing: int = Field(0, description="Numerical representation of relationship (-100 to 100)")
    notes: str = Field("", description="Additional notes about the relationship")
    last_interaction: Optional[datetime] = Field(None)

    @validator('standing')
    def validate_standing(cls, v):
        """Ensure standing is between -100 and 100."""
        if not -100 <= v <= 100:
            raise ValueError("Standing must be between -100 and 100")
        return v

class Quest(BaseModel):
    """A quest or mission the character is involved in."""
    title: str = Field(..., description="Title of the quest")
    description: str = Field(..., description="Quest description")
    status: str = Field("active", description="Quest status (active, completed, failed)")
    importance: str = Field("normal", description="Quest importance (minor, normal, major)")
    assigned_by: Optional[str] = Field(None, description="NPC or entity that assigned the quest")
    rewards: Optional[Dict[str, Any]] = Field(None, description="Quest rewards")
    progress: List[Dict[str, Any]] = Field(default_factory=list, description="Quest progress markers")

class ExperienceEntry(BaseModel):
    """Records experience gained by the character."""
    amount: int = Field(..., description="Amount of XP gained")
    source: str = Field(..., description="Source of the XP")
    reason: str = Field(..., description="Reason for gaining XP")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(None, description="ID of the session if gained during play")

    @validator('amount')
    def validate_amount(cls, v):
        """Ensure XP amount is positive."""
        if v <= 0:
            raise ValueError("XP amount must be positive")
        return v

class SessionEntry(BaseModel):
    """Record of a gaming session."""
    session_number: int = Field(..., description="Sequential session number")
    session_date: datetime = Field(..., description="Date and time of the session")
    dm_name: str = Field(..., description="Name of the DM for this session")
    summary: str = Field(..., description="Brief summary of the session")
    locations_visited: List[str] = Field(default_factory=list)
    npcs_met: List[str] = Field(default_factory=list)
    important_events: List[Dict[str, Any]] = Field(default_factory=list)
    combat_encounters: List[Dict[str, Any]] = Field(default_factory=list)
    loot_gained: List[Dict[str, Any]] = Field(default_factory=list)
    experience_gained: int = Field(0, description="Total XP gained in session")

class CharacterDevelopment(BaseModel):
    """Tracks character development and story elements."""
    personality_changes: List[Dict[str, Any]] = Field(default_factory=list)
    goal_progress: List[Dict[str, Any]] = Field(default_factory=list)
    background_additions: List[Dict[str, Any]] = Field(default_factory=list)
    significant_events: List[Dict[str, Any]] = Field(default_factory=list)
    relationships_developed: List[Dict[str, Any]] = Field(default_factory=list)

class JournalEntry(BaseModel):
    """A complete journal entry that may include multiple components."""
    id: UUID = Field(..., description="Unique identifier for this entry")
    character_id: str = Field(..., description="ID of the character this entry belongs to")
    entry_type: str = Field(..., description="Type of journal entry")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(..., description="Title of the journal entry")
    content: str = Field(..., description="Main content of the entry")
    session: Optional[SessionEntry] = Field(None)
    achievements: List[Achievement] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    quests: List[Quest] = Field(default_factory=list)
    relationships: List[NPCRelationship] = Field(default_factory=list)
    development: Optional[CharacterDevelopment] = Field(None)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "character_id": "character-123",
                "entry_type": "session_log",
                "title": "The Battle at Ravencroft",
                "content": "Our party arrived at the village of Ravencroft...",
                "session": {
                    "session_number": 5,
                    "session_date": "2025-08-24T20:00:00Z",
                    "dm_name": "Sarah",
                    "summary": "Defended Ravencroft from bandits",
                    "locations_visited": ["Ravencroft", "Old Mill"],
                    "npcs_met": ["Mayor Blackwood", "Guard Captain Reynolds"],
                    "important_events": [
                        {
                            "type": "combat",
                            "description": "Defeated bandit leader"
                        }
                    ],
                    "experience_gained": 1000
                },
                "achievements": [
                    {
                        "title": "Savior of Ravencroft",
                        "description": "Successfully defended the village",
                        "reward_type": "reputation",
                        "reward_value": "respected"
                    }
                ],
                "tags": ["combat", "quest_complete", "milestone"]
            }
        }
