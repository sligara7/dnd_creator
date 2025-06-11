from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from enum import Enum, auto

class CreatureType(Enum):
    """Official creature types in D&D 2024 rules"""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"
    # Allow for custom types beyond official rules
    CUSTOM = "custom"

class CreatureSize(Enum):
    """Official size categories for creatures in D&D 2024 rules"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"
    # Allow for custom sizes beyond official rules
    CUSTOM = "custom"

class CreatureTag(Enum):
    """Common creature tags in D&D 2024 rules"""
    AMPHIBIOUS = auto()
    AQUATIC = auto()
    AIRBORNE = auto()
    PACK_TACTICS = auto()
    SHAPECHANGER = auto()
    SWARM = auto()
    MAGICAL = auto()
    VENOMOUS = auto()
    LEGENDARY = auto()
    MYTHIC = auto()
    SPELLCASTER = auto()
    # Custom tags can be added as strings

class AbstractCreature(ABC):
    """
    Abstract base class for D&D creatures following the 2024 rules.
    
    Key characteristics required for any creature in D&D:
    1. Creature Type: The fundamental nature (beast, humanoid, etc.)
    2. Ability Scores: STR, DEX, CON, INT, WIS, CHA (3-30)
    3. Armor Class (AC): Defense rating
    4. Hit Points (HP): Durability before defeat
    5. Speed: Movement capabilities
    6. Challenge Rating (CR): Difficulty/threat level
    7. Actions: Combat abilities and attacks
    """
    
    # Common creature skills as defined in the rules
    SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", 
        "History", "Insight", "Intimidation", "Investigation", "Medicine", 
        "Nature", "Perception", "Performance", "Persuasion", "Religion", 
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Saving throws correspond to ability scores
    SAVING_THROWS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    # Ability score ranges
    MIN_ABILITY_SCORE = 1  # Absolute minimum
    MAX_ABILITY_SCORE = 30  # Absolute maximum
    
    # Challenge ratings
    CHALLENGE_RATINGS = [
        0, 0.125, 0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
        24, 25, 26, 27, 28, 29, 30
    ]
    
    @abstractmethod
    def get_ability_scores(self) -> Dict[str, int]:
        """
        Get the creature's six ability scores.
        
        Returns:
            Dict[str, int]: Dictionary of ability scores
        """
        pass
    
    @abstractmethod
    def get_ability_modifiers(self) -> Dict[str, int]:
        """
        Get modifiers for all ability scores.
        
        Returns:
            Dict[str, int]: Dictionary of ability modifiers
        """
        pass
    
    @abstractmethod
    def get_armor_class(self) -> int:
        """
        Get the creature's armor class.
        
        Returns:
            int: Armor class value
        """
        pass
    
    @abstractmethod
    def get_hit_points(self) -> int:
        """
        Get the creature's current hit points.
        
        Returns:
            int: Current HP
        """
        pass
    
    @abstractmethod
    def get_max_hit_points(self) -> int:
        """
        Get the creature's maximum hit points.
        
        Returns:
            int: Maximum HP
        """
        pass
    
    @abstractmethod
    def get_hit_dice(self) -> str:
        """
        Get the creature's hit dice formula.
        
        Returns:
            str: Hit dice (e.g., "3d8+6")
        """
        pass
    
    @abstractmethod
    def get_speeds(self) -> Dict[str, int]:
        """
        Get all movement speeds.
        
        Returns:
            Dict[str, int]: Dictionary of movement types and speeds
        """
        pass
    
    @abstractmethod
    def get_challenge_rating(self) -> float:
        """
        Get the creature's challenge rating.
        
        Returns:
            float: Challenge rating
        """
        pass
    
    @abstractmethod
    def get_xp_value(self) -> int:
        """
        Get the XP value based on challenge rating.
        
        Returns:
            int: XP value
        """
        pass
    
    @abstractmethod
    def get_proficiency_bonus(self) -> int:
        """
        Get the creature's proficiency bonus based on CR.
        
        Returns:
            int: Proficiency bonus
        """
        pass
    
    @abstractmethod
    def get_saving_throw_modifiers(self) -> Dict[str, int]:
        """
        Get modifiers for saving throws.
        
        Returns:
            Dict[str, int]: Dictionary of saving throw modifiers
        """
        pass
    
    @abstractmethod
    def get_skill_modifiers(self) -> Dict[str, int]:
        """
        Get modifiers for skills.
        
        Returns:
            Dict[str, int]: Dictionary of skill modifiers
        """
        pass
    
    @abstractmethod
    def get_senses(self) -> Dict[str, Any]:
        """
        Get the creature's special senses.
        
        Returns:
            Dict[str, Any]: Dictionary of senses and their values
        """
        pass
    
    @abstractmethod
    def get_damage_vulnerabilities(self) -> List[str]:
        """
        Get damage types the creature is vulnerable to.
        
        Returns:
            List[str]: Damage vulnerabilities
        """
        pass
    
    @abstractmethod
    def get_damage_resistances(self) -> List[str]:
        """
        Get damage types the creature is resistant to.
        
        Returns:
            List[str]: Damage resistances
        """
        pass
    
    @abstractmethod
    def get_damage_immunities(self) -> List[str]:
        """
        Get damage types the creature is immune to.
        
        Returns:
            List[str]: Damage immunities
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> List[str]:
        """
        Get conditions the creature is immune to.
        
        Returns:
            List[str]: Condition immunities
        """
        pass
    
    @abstractmethod
    def get_languages(self) -> List[str]:
        """
        Get languages the creature can understand or speak.
        
        Returns:
            List[str]: Languages
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> Dict[str, Any]:
        """
        Get special traits/features of the creature.
        
        Returns:
            Dict[str, Any]: Dictionary of traits
        """
        pass
    
    @abstractmethod
    def get_actions(self) -> Dict[str, Any]:
        """
        Get actions the creature can take.
        
        Returns:
            Dict[str, Any]: Dictionary of actions
        """
        pass
    
    @abstractmethod
    def get_reactions(self) -> Dict[str, Any]:
        """
        Get reactions the creature can take.
        
        Returns:
            Dict[str, Any]: Dictionary of reactions
        """
        pass
    
    @abstractmethod
    def get_legendary_actions(self) -> Optional[Dict[str, Any]]:
        """
        Get legendary actions if the creature has any.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary of legendary actions or None
        """
        pass
    
    @abstractmethod
    def get_lair_actions(self) -> Optional[Dict[str, Any]]:
        """
        Get lair actions if the creature has any.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary of lair actions or None
        """
        pass
    
    @abstractmethod
    def get_spellcasting_details(self) -> Optional[Dict[str, Any]]:
        """
        Get spellcasting details if the creature can cast spells.
        
        Returns:
            Optional[Dict[str, Any]]: Spellcasting information or None
        """
        pass
    
    @abstractmethod
    def to_stat_block(self) -> Dict[str, Any]:
        """
        Convert the creature to standard D&D stat block format.
        
        Returns:
            Dict[str, Any]: Stat block representation
        """
        pass
    
    @abstractmethod
    def take_damage(self, amount: int, damage_type: str) -> int:
        """
        Apply damage to the creature.
        
        Args:
            amount: Damage amount
            damage_type: Type of damage
            
        Returns:
            int: Remaining hit points
        """
        pass
    
    @abstractmethod
    def heal(self, amount: int) -> int:
        """
        Heal the creature.
        
        Args:
            amount: Healing amount
            
        Returns:
            int: New hit points total
        """
        pass


class AbstractCreatures(ABC):
    """
    Abstract base class for managing creatures in D&D 5e (2024 Edition).
    
    This interface supports both official D&D creatures and custom creations.
    """
    
    @abstractmethod
    def get_all_creatures(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available creatures.
        
        Returns:
            List[Dict[str, Any]]: List of creature summary information
        """
        pass
    
    @abstractmethod
    def get_creature_details(self, creature_id: str) -> Optional[AbstractCreature]:
        """
        Get detailed information about a creature.
        
        Args:
            creature_id: Unique identifier for the creature
            
        Returns:
            Optional[AbstractCreature]: The creature object or None if not found
        """
        pass
    
    @abstractmethod
    def filter_creatures(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter creatures based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[Dict[str, Any]]: List of filtered creature summaries
        """
        pass
    
    @abstractmethod
    def create_creature(self, creature_data: Dict[str, Any]) -> AbstractCreature:
        """
        Create a new creature.
        
        Args:
            creature_data: Creature definition data
            
        Returns:
            AbstractCreature: New creature instance
        """
        pass
    
    @abstractmethod
    def get_creatures_by_type(self, creature_type: Union[str, CreatureType]) -> List[Dict[str, Any]]:
        """
        Get creatures by their type.
        
        Args:
            creature_type: Type to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching creature summaries
        """
        pass
    
    @abstractmethod
    def get_creatures_by_cr_range(self, min_cr: float, max_cr: float) -> List[Dict[str, Any]]:
        """
        Get creatures within a challenge rating range.
        
        Args:
            min_cr: Minimum challenge rating
            max_cr: Maximum challenge rating
            
        Returns:
            List[Dict[str, Any]]: List of matching creature summaries
        """
        pass
    
    @abstractmethod
    def get_creature_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available creature templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping template names to their definitions
        """
        pass
    
    @abstractmethod
    def create_creature_from_template(self, template_id: str, 
                                   customizations: Dict[str, Any] = None) -> AbstractCreature:
        """
        Create a creature from a template with optional customizations.
        
        Args:
            template_id: Template identifier
            customizations: Custom overrides for the template
            
        Returns:
            AbstractCreature: New creature instance based on template
        """
        pass
    
    @abstractmethod
    def generate_random_encounter(self, party_level: int, difficulty: str = "medium", 
                               environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate a random encounter appropriate for a party.
        
        Args:
            party_level: Average party level
            difficulty: Encounter difficulty (easy, medium, hard, deadly)
            environment: Optional environment to filter creatures
            
        Returns:
            List[Dict[str, Any]]: List of creatures for the encounter
        """
        pass
    
    @abstractmethod
    def calculate_encounter_difficulty(self, creatures: List[Union[str, AbstractCreature]], 
                                   party_size: int, party_level: int) -> Dict[str, Any]:
        """
        Calculate encounter difficulty according to D&D rules.
        
        Args:
            creatures: List of creatures or creature IDs
            party_size: Number of players
            party_level: Average party level
            
        Returns:
            Dict[str, Any]: Encounter assessment including difficulty and XP
        """
        pass