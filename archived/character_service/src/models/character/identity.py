"""Models for character identity and personal information."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

from ..base import BaseModelWithAudit

class AlignmentComponent(str, Enum):
    """Components of D&D 5e alignment."""
    # Ethical axis
    LAWFUL = "lawful"
    NEUTRAL = "neutral"
    CHAOTIC = "chaotic"
    
    # Moral axis
    GOOD = "good"
    EVIL = "evil"

class CreatureSize(str, Enum):
    """Available creature sizes in D&D 5e."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class Background(BaseModel):
    """Character background information."""
    name: str = Field(..., description="Name of the background")
    feature: str = Field(..., description="Special feature granted by background")
    description: str = Field(..., description="Description of the background")
    personality_traits: List[str] = Field(default_factory=list)
    ideals: List[str] = Field(default_factory=list)
    bonds: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)
    tool_proficiencies: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    starting_equipment: List[str] = Field(default_factory=list)

class Origin(BaseModel):
    """Character origin information including species and background."""
    species: str = Field(..., description="Character's species/race")
    subrace: Optional[str] = Field(None, description="Subrace or variant if applicable")
    background: Background = Field(..., description="Character's background")
    size: CreatureSize = Field(CreatureSize.MEDIUM, description="Character's size category")
    languages: List[str] = Field(default_factory=list, description="Known languages")
    speed: Dict[str, int] = Field(
        default_factory=lambda: {"walk": 30},
        description="Base movement speeds"
    )
    age: Optional[int] = Field(None, description="Character's age")
    max_age: Optional[int] = Field(None, description="Maximum natural lifespan")
    height: Optional[str] = Field(None, description="Character's height")
    weight: Optional[str] = Field(None, description="Character's weight")

class Alignment(BaseModel):
    """Character's ethical and moral alignment."""
    ethical: AlignmentComponent = Field(
        AlignmentComponent.NEUTRAL,
        description="Lawful-Chaotic axis"
    )
    moral: AlignmentComponent = Field(
        AlignmentComponent.NEUTRAL,
        description="Good-Evil axis"
    )
    
    @property
    def full_alignment(self) -> str:
        """Get the full alignment string."""
        if self.ethical == AlignmentComponent.NEUTRAL and self.moral == AlignmentComponent.NEUTRAL:
            return "True Neutral"
        return f"{self.ethical.capitalize()} {self.moral.capitalize()}"

class Personality(BaseModel):
    """Character personality traits and roleplaying elements."""
    personality_traits: List[str] = Field(
        default_factory=list,
        description="Distinctive personality traits"
    )
    ideals: List[str] = Field(
        default_factory=list,
        description="Ideals and beliefs"
    )
    bonds: List[str] = Field(
        default_factory=list,
        description="Connections to people, places, or things"
    )
    flaws: List[str] = Field(
        default_factory=list,
        description="Character flaws and vulnerabilities"
    )
    notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional personality notes by category"
    )

class Appearance(BaseModel):
    """Character's physical appearance."""
    height: Optional[str] = Field(None, description="Character's height")
    weight: Optional[str] = Field(None, description="Character's weight")
    size: CreatureSize = Field(CreatureSize.MEDIUM, description="Size category")
    age: Optional[int] = Field(None, description="Character's age")
    gender: Optional[str] = Field(None, description="Character's gender")
    eyes: Optional[str] = Field(None, description="Eye color/description")
    skin: Optional[str] = Field(None, description="Skin color/description")
    hair: Optional[str] = Field(None, description="Hair color/style")
    distinguishing_marks: List[str] = Field(
        default_factory=list,
        description="Scars, tattoos, or other marks"
    )
    general_appearance: Optional[str] = Field(
        None,
        description="General appearance description"
    )

class PersonalHistory(BaseModel):
    """Character's background story and history."""
    backstory: str = Field("", description="Character's life story")
    significant_events: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Major life events"
    )
    connections: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "family": [],
            "friends": [],
            "organizations": [],
            "enemies": []
        },
        description="Character's connections"
    )
    notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional history notes by category"
    )

class Identity(BaseModelWithAudit):
    """Complete character identity information."""
    
    # Basic identification
    name: str = Field(..., description="Character's name")
    player_name: str = Field(..., description="Player's name")
    
    # Core identity elements
    origin: Origin = Field(..., description="Species and background")
    alignment: Alignment = Field(..., description="Ethical and moral alignment")
    personality: Personality = Field(
        default_factory=Personality,
        description="Personality traits"
    )
    appearance: Appearance = Field(
        default_factory=Appearance,
        description="Physical appearance"
    )
    history: PersonalHistory = Field(
        default_factory=PersonalHistory,
        description="Background and history"
    )
    
    # Campaign information
    campaign: Optional[str] = Field(None, description="Current campaign")
    faction: Optional[str] = Field(None, description="Associated faction/organization")
    status: str = Field("active", description="Character status (active, retired, deceased)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_played: Optional[datetime] = Field(None)
    version: str = Field("1.0", description="Schema version")
    
    def update_appearance(self, updates: Dict[str, any]) -> None:
        """Update appearance details."""
        for key, value in updates.items():
            if hasattr(self.appearance, key):
                setattr(self.appearance, key, value)
    
    def add_connection(self, category: str, name: str, details: Optional[str] = None) -> bool:
        """Add a new connection to the character's history."""
        if category in self.history.connections:
            connection = name
            if details:
                connection = f"{name} ({details})"
            self.history.connections[category].append(connection)
            return True
        return False
    
    def add_significant_event(self, title: str, description: str, 
                            date: Optional[str] = None) -> None:
        """Add a significant event to character's history."""
        event = {
            "title": title,
            "description": description,
            "date": date or "Unknown"
        }
        self.history.significant_events.append(event)
    
    def get_summary(self) -> Dict[str, any]:
        """Get a summary of the character's identity."""
        return {
            "name": self.name,
            "player": self.player_name,
            "species": self.origin.species,
            "background": self.origin.background.name,
            "alignment": self.alignment.full_alignment,
            "appearance": {
                "size": self.appearance.size,
                "age": self.appearance.age,
                "height": self.appearance.height,
                "weight": self.appearance.weight
            },
            "campaign": self.campaign,
            "status": self.status,
            "last_played": self.last_played.isoformat() if self.last_played else None
        }
