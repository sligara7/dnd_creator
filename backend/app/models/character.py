from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class AbilityScores(BaseModel):
    strength: int = Field(..., ge=1, le=30)
    dexterity: int = Field(..., ge=1, le=30)
    constitution: int = Field(..., ge=1, le=30)
    intelligence: int = Field(..., ge=1, le=30)
    wisdom: int = Field(..., ge=1, le=30)
    charisma: int = Field(..., ge=1, le=30)

class CharacterCreate(BaseModel):
    name: str
    user_id: str
    species: str
    character_class: str
    level: int = Field(1, ge=1, le=20)
    alignment: str
    ability_scores: AbilityScores
    skills: List[str] = []
    equipment: List[str] = []
    spells: List[str] = []
    feats: List[str] = []
    personality: Dict[str, str] = {}
    backstory: str = ""
    appearance: str = ""
    
class CharacterResponse(CharacterCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    approved: bool = False
    portrait_url: Optional[str] = None
    journal_entries: List[Dict] = []
    waypoints: List[Dict] = []

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=20)
    ability_scores: Optional[AbilityScores] = None
    skills: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    spells: Optional[List[str]] = None
    feats: Optional[List[str]] = None
    personality: Optional[Dict[str, str]] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None

class JournalEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    title: str
    content: str
    session_number: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class Waypoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    level: int
    title: str
    description: str
    key_achievements: List[str]
    new_abilities: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)