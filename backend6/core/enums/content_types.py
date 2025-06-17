"""
Content Type Enumerations for Creative Content Generation.

Defines the types of D&D content that can be generated, their properties,
and categorizations for the creative content framework.
"""

from enum import Enum
from typing import Set


class ContentType(Enum):
    """Primary types of D&D content that can be generated."""
    SPECIES = "species"
    CHARACTER_CLASS = "character_class"
    SUBCLASS = "subclass"
    BACKGROUND = "background"
    FEAT = "feat"
    SPELL = "spell"
    WEAPON = "weapon"
    ARMOR = "armor"
    EQUIPMENT = "equipment"
    MAGIC_ITEM = "magic_item"
    
    @property
    def is_character_option(self) -> bool:
        """Check if this content type is a character option."""
        return self in {
            self.SPECIES, self.CHARACTER_CLASS, self.SUBCLASS, 
            self.BACKGROUND, self.FEAT
        }
    
    @property
    def is_equipment(self) -> bool:
        """Check if this content type is equipment."""
        return self in {self.WEAPON, self.ARMOR, self.EQUIPMENT, self.MAGIC_ITEM}
    
    @property
    def requires_mechanics(self) -> bool:
        """Check if this content type requires mechanical rules."""
        return self in {
            self.SPECIES, self.CHARACTER_CLASS, self.SUBCLASS,
            self.FEAT, self.SPELL, self.WEAPON, self.ARMOR, self.MAGIC_ITEM
        }


class GenerationType(Enum):
    """Types of content generation approaches."""
    CONCEPT_DRIVEN = "concept_driven"     # Start with thematic concept
    TEMPLATE_BASED = "template_based"     # Use existing templates
    SIGNATURE_EQUIPMENT = "signature_equipment"  # Character-specific items
    CUSTOM_SPECIES = "custom_species"     # New species for character concept
    CUSTOM_CLASS = "custom_class"         # New class for character concept


class ContentRarity(Enum):
    """Rarity levels for generated content following D&D 5e standards."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    
    @property
    def requires_dm_approval(self) -> bool:
        """Check if this rarity typically requires DM approval."""
        return self in {self.LEGENDARY, self.ARTIFACT}


class ThemeCategory(Enum):
    """Thematic categories for content organization."""
    # Core fantasy themes
    ARCANE = "arcane"                   # Magic and wizardry
    DIVINE = "divine"                   # Gods and religion
    NATURE = "nature"                   # Natural world and primal forces
    MARTIAL = "martial"                 # Combat and warfare
    
    # Elemental themes
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHTNING = "lightning"
    ICE = "ice"
    
    # Specific themes
    SHADOW = "shadow"                   # Darkness and stealth
    CELESTIAL = "celestial"             # Heavenly and angelic
    INFERNAL = "infernal"               # Hellish and demonic
    UNDEAD = "undead"                   # Death and undeath
    ABERRANT = "aberrant"               # Alien and otherworldly
    
    # Cultural themes
    NORDIC = "nordic"                   # Norse/Viking themes
    ORIENTAL = "oriental"               # Eastern themes
    EGYPTIAN = "egyptian"               # Ancient Egyptian themes
    GRECIAN = "grecian"                 # Greek mythology themes
    
    # Modern/unique themes
    TECHNOLOGICAL = "technological"     # Magitech, artificer themes
    COSMIC = "cosmic"                   # Space, stars, cosmic horror
    TEMPORAL = "temporal"               # Time manipulation
    
    @property
    def is_elemental(self) -> bool:
        """Check if this theme is elemental."""
        return self in {self.FIRE, self.WATER, self.EARTH, self.AIR, self.LIGHTNING, self.ICE}
    
    @property
    def is_planar(self) -> bool:
        """Check if this theme relates to other planes."""
        return self in {self.CELESTIAL, self.INFERNAL, self.SHADOW, self.ABERRANT}


# Content type groupings for management
CHARACTER_OPTIONS = {
    ContentType.SPECIES,
    ContentType.CHARACTER_CLASS,
    ContentType.SUBCLASS,
    ContentType.BACKGROUND,
    ContentType.FEAT
}

EQUIPMENT_TYPES = {
    ContentType.WEAPON,
    ContentType.ARMOR,
    ContentType.EQUIPMENT,
    ContentType.MAGIC_ITEM
}

SIGNATURE_CONTENT = {
    ContentType.WEAPON,
    ContentType.ARMOR,
    ContentType.MAGIC_ITEM,
    ContentType.SPELL,
    ContentType.FEAT
}


def get_content_types_by_category(category: str) -> Set[ContentType]:
    """Get content types by category name."""
    categories = {
        'character_options': CHARACTER_OPTIONS,
        'equipment': EQUIPMENT_TYPES,
        'signature': SIGNATURE_CONTENT
    }
    return categories.get(category, set())

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Union, Tuple, Any

class ProficiencyLevel(Enum):
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class AbilityScore:
    """
    Class representing a D&D ability score with its component values.
    
    This breakdown allows for precise tracking of different bonuses and their sources,
    which is essential for proper stacking rules and temporary effects.
    """
    
    def __init__(self, base_score: int = 10):
        # Core Independent Variable
        self.base_score: int = base_score  # Starting value from character creation
        
        # In-Game Independent Variables
        self.bonus: int = 0  # Temporary or permanent flat bonuses
        self.set_score: Optional[int] = None  # Direct override (e.g., from Belt of Giant Strength)
        self.stacking_bonuses: Dict[str, int] = {}  # Named bonuses that can stack (source -> value)
    
    @property
    def total_score(self) -> int:
        """Calculate the final ability score value applying all bonuses and overrides."""
        # Dependent Variable (calculated)
        if self.set_score is not None:
            return self.set_score
        
        return self.base_score + self.bonus + sum(self.stacking_bonuses.values())
    
    @property
    def modifier(self) -> int:
        """Calculate the ability modifier using D&D 5e formula."""
        # Dependent Variable (calculated)
        return (self.total_score - 10) // 2
    
    def add_stacking_bonus(self, source: str, value: int) -> None:
        """Add a stacking bonus from a specific source."""
        self.stacking_bonuses[source] = value
    
    def remove_stacking_bonus(self, source: str) -> None:
        """Remove a stacking bonus from a specific source."""
        if source in self.stacking_bonuses:
            del self.stacking_bonuses[source]
            
    def reset_bonuses(self) -> None:
        """Reset all bonuses to default values."""
        self.bonus = 0
        self.set_score = None
        self.stacking_bonuses.clear()
        
    def __int__(self) -> int:
        """Allow casting the ability score to an integer."""
        return self.total_score