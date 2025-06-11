from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from enum import Enum

class ProficiencyLevel(Enum):
    """Enumeration for proficiency levels in D&D 5e."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class AbilityScore:
    """Class representing a D&D ability score with its component values."""
    
    def __init__(self, base_score: int = 10):
        self.base_score: int = base_score
        self.bonus: int = 0
        self.set_score: Optional[int] = None
        self.stacking_bonuses: Dict[str, int] = {}
    
    @property
    def total_score(self) -> int:
        if self.set_score is not None:
            return self.set_score
        return max(1, min(30, self.base_score + self.bonus + sum(self.stacking_bonuses.values())))
    
    @property
    def modifier(self) -> int:
        return (self.total_score - 10) // 2

class CharacterCore:
    """
    CORE INDEPENDENT VARIABLES - Set during character creation/leveling.
    
    These variables define the fundamental character build and rarely change
    except through leveling up or major story events.
    """
    
    def __init__(self, name: str = ""):
        # Basic Character Identity
        self.name: str = name
        self.species: str = ""
        self.species_variants: List[str] = []
        self.lineage: Optional[str] = None
        self.character_classes: Dict[str, int] = {}  # {"Fighter": 3, "Wizard": 2}
        self.subclasses: Dict[str, str] = {}  # {"Fighter": "Champion"}
        self.background: str = ""
        self.alignment_ethical: str = ""  # Lawful, Neutral, Chaotic
        self.alignment_moral: str = ""    # Good, Neutral, Evil
        
        # Appearance and Identity
        self.height: str = ""
        self.weight: str = ""
        self.age: int = 0
        self.eyes: str = ""
        self.hair: str = ""
        self.skin: str = ""
        self.gender: str = ""
        self.pronouns: str = ""
        self.size: str = "Medium"
        
        # Base Ability Scores
        self.strength: AbilityScore = AbilityScore(10)
        self.dexterity: AbilityScore = AbilityScore(10)
        self.constitution: AbilityScore = AbilityScore(10)
        self.intelligence: AbilityScore = AbilityScore(10)
        self.wisdom: AbilityScore = AbilityScore(10)
        self.charisma: AbilityScore = AbilityScore(10)
        
        # Core Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.weapon_proficiencies: Set[str] = set()
        self.armor_proficiencies: Set[str] = set()
        self.tool_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.languages: Set[str] = set()
        
        # Core Features and Traits
        self.species_traits: Dict[str, Any] = {}
        self.class_features: Dict[str, Any] = {}
        self.background_feature: str = ""
        self.feats: List[str] = []
        
        # Core Movement and Senses
        self.base_speed: int = 30
        self.base_vision_types: Dict[str, int] = {}  # {"darkvision": 60}
        self.base_movement_types: Dict[str, int] = {}  # {"swim": 30, "fly": 0}
        
        # Core Defenses
        self.base_damage_resistances: Set[str] = set()
        self.base_damage_immunities: Set[str] = set()
        self.base_damage_vulnerabilities: Set[str] = set()
        self.base_condition_immunities: Set[str] = set()
        
        # Core Spellcasting Abilities
        self.spellcasting_ability: Optional[str] = None
        self.spellcasting_classes: Dict[str, Dict[str, Any]] = {}
        self.ritual_casting_classes: Dict[str, bool] = {}
        
        # Character Background & Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory: str = ""
        
        # Hit Dice (base values from class)
        self.hit_dice: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Character Sheet Metadata
        self.creation_date: str = ""
        self.player_name: str = ""
        self.campaign: str = ""
        self.sources_used: Set[str] = set()
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level or first class)."""
        if not self.character_classes:
            return ""
        return max(self.character_classes.items(), key=lambda x: x[1])[0]
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        """Get the AbilityScore object for a specific ability."""
        ability_map = {
            "strength": self.strength, "str": self.strength,
            "dexterity": self.dexterity, "dex": self.dexterity,
            "constitution": self.constitution, "con": self.constitution,
            "intelligence": self.intelligence, "int": self.intelligence,
            "wisdom": self.wisdom, "wis": self.wisdom,
            "charisma": self.charisma, "cha": self.charisma
        }
        return ability_map.get(ability.lower())
    
    def validate(self) -> Dict[str, Any]:
        """Validate core character data."""
        issues = []
        warnings = []
        
        # Basic validation
        if not self.name.strip():
            warnings.append("Character name is empty")
        
        if not self.species:
            issues.append("Species is required")
        
        if not self.character_classes:
            issues.append("At least one character class is required")
        
        # Ability score validation
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability = self.get_ability_score(ability_name)
            if ability and (ability.total_score < 1 or ability.total_score > 30):
                issues.append(f"{ability_name.title()} score ({ability.total_score}) must be between 1 and 30")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "species_variants": self.species_variants,
            "lineage": self.lineage,
            "character_classes": self.character_classes,
            "subclasses": self.subclasses,
            "background": self.background,
            "alignment": [self.alignment_ethical, self.alignment_moral],
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            "proficiencies": {
                "skills": dict(self.skill_proficiencies),
                "saving_throws": dict(self.saving_throw_proficiencies),
                "weapons": list(self.weapon_proficiencies),
                "armor": list(self.armor_proficiencies),
                "tools": dict(self.tool_proficiencies),
                "languages": list(self.languages)
            },
            "features": {
                "species_traits": self.species_traits,
                "class_features": self.class_features,
                "background_feature": self.background_feature,
                "feats": self.feats
            },
            "spellcasting": {
                "ability": self.spellcasting_ability,
                "classes": self.spellcasting_classes
            },
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
                "backstory": self.backstory
            }
        }