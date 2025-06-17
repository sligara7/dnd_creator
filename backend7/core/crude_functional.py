from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple


class BackstoryElement(Enum):
    """Key elements that make up a character's backstory according to D&D 2024 rules."""
    ORIGIN = auto()       # Where the character comes from
    FAMILY = auto()       # Family details
    EDUCATION = auto()    # Training and learning
    DEFINING_EVENT = auto() # Major event that shaped the character
    MOTIVATION = auto()   # Why they became an adventurer
    CONNECTIONS = auto()  # Relationships with others
    GOALS = auto()        # Future aspirations


class AbstractBackground(ABC):
    """
    Abstract base class defining the contract for character backgrounds in D&D 5e (2024 Edition).
    
    Per D&D 2024 rules, backgrounds provide a character's personal history and include mechanical benefits:
    - Two skill proficiencies
    - Tool proficiencies
    - Languages
    - Equipment
    - Background feature
    - A 1st-level feat
    """
    
    @abstractmethod
    def get_all_backgrounds(self) -> List[str]:
        """
        Get a list of all official backgrounds.
        
        Returns:
            List[str]: List of official background names
        """
        pass
    
    @abstractmethod
    def get_background_details(self, background: str) -> Dict[str, Any]:
        """
        Get complete details for a background.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, Any]: Complete background details
        """
        pass
    
    @abstractmethod
    def get_background_proficiencies(self, background: str) -> Dict[str, List[str]]:
        """
        Get proficiencies granted by a background.
        
        Per D&D 2024 rules, backgrounds typically provide:
        - Two skill proficiencies
        - One or more tool proficiencies
        - One language
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, List[str]]: Dictionary with skill, tool, and language proficiencies
        """
        pass
    
    @abstractmethod
    def get_background_equipment(self, background: str) -> List[str]:
        """
        Get starting equipment granted by a background.
        
        Per D&D 2024 rules, backgrounds provide a set of starting equipment.
        
        Args:
            background: Character background
            
        Returns:
            List[str]: List of starting equipment items
        """
        pass
    
    @abstractmethod
    def get_background_feature(self, background: str) -> Dict[str, Any]:
        """
        Get the special feature associated with a background.
        
        Per D&D 2024 rules, each background provides a special feature
        that grants a unique benefit.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, Any]: Background feature details
        """
        pass
    
    @abstractmethod
    def get_background_feat(self, background: str) -> str:
        """
        Get the 1st-level feat granted by a background.
        
        Per D&D 2024 rules, each background provides a 1st-level feat.
        
        Args:
            background: Character background
            
        Returns:
            str: Name of the feat
        """
        pass
    
    @abstractmethod
    def validate_custom_background(self, background_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom background against D&D 2024 rules.
        
        Per D&D 2024 rules, custom backgrounds should provide:
        - Two skill proficiencies
        - A total of two between tool proficiencies and languages
        - A standard equipment package
        - A background feature
        - A 1st-level feat
        
        Args:
            background_data: Custom background definition
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        pass
    
    @abstractmethod
    def create_custom_background(self, background_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a custom character background.
        
        Per D&D 2024 rules, players can create custom backgrounds that fit their character concept.
        
        Args:
            background_data: Background specification
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def apply_background_benefits(self, character_data: Dict[str, Any], background: str) -> Dict[str, Any]:
        """
        Apply all mechanical benefits of a background to a character.
        
        Args:
            character_data: Character information
            background: Background to apply
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass
    
    @abstractmethod
    def get_character_background(self) -> str:
        """
        Get the character's current background.
        
        Returns:
            str: Background name
        """
        pass
    
    @abstractmethod
    def set_character_background(self, background: str) -> bool:
        """
        Set the character's background.
        
        Args:
            background: Background name
            
        Returns:
            bool: True if successfully set
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class SpellcastingType(Enum):
    """Types of spellcasting in D&D 5e (2024 Edition)"""
    NONE = "none"             # No spellcasting ability
    PREPARED = "prepared"     # Prepare spells from a list (Clerics, Wizards, etc.)
    KNOWN = "known"           # Know a fixed set of spells (Bards, Sorcerers, etc.)
    PACT = "pact"             # Warlock's unique spellcasting
    HYBRID = "hybrid"         # Mixed spellcasting types (certain subclasses)

class ClassResource(Enum):
    """Special resources used by different classes"""
    # Core class resources (extendable for custom classes)
    RAGE = "rage"               # Barbarian
    BARDIC_INSPIRATION = "bardic_inspiration"  # Bard
    CHANNEL_DIVINITY = "channel_divinity"  # Cleric, Paladin
    WILD_SHAPE = "wild_shape"   # Druid
    ACTION_SURGE = "action_surge"  # Fighter
    KI = "ki"                   # Monk
    LAY_ON_HANDS = "lay_on_hands"  # Paladin
    FAVORED_FOE = "favored_foe"  # Ranger
    SNEAK_ATTACK = "sneak_attack"  # Rogue
    SORCERY_POINTS = "sorcery_points"  # Sorcerer
    PACT_SLOTS = "pact_slots"   # Warlock
    ARCANE_RECOVERY = "arcane_recovery"  # Wizard
    # Custom resources can be added as needed

class SubclassType(Enum):
    """Types of subclasses based on when they're chosen"""
    LEVEL_1 = 1   # Chosen at level 1 (Cleric Domains, Sorcerous Origins)
    LEVEL_2 = 2   # Chosen at level 2 (Wizard Schools)
    LEVEL_3 = 3   # Chosen at level 3 (Fighter Martial Archetypes, etc.)
    # Custom subclass levels can be defined as needed

class AbstractCharacterClass(ABC):
    """
    Abstract base class defining the contract for character classes in D&D 5e (2024 Edition).
    
    This interface supports both official D&D classes and custom classes,
    enforcing the core rules while allowing creative freedom.
    """
    
    # XP thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Maximum level in D&D 5e
    MAX_LEVEL = 20
    
    @abstractmethod
    def get_hit_die(self) -> str:
        """
        Get the hit die type for this class (d6, d8, d10, or d12).
        
        Returns:
            str: Hit die (e.g., "d8")
        """
        pass
    
    @abstractmethod
    def get_proficiency_bonus(self, level: int) -> int:
        """
        Get proficiency bonus based on level.
        
        Per 2024 rules:
        - Levels 1-4: +2
        - Levels 5-8: +3
        - Levels 9-12: +4
        - Levels 13-16: +5
        - Levels 17-20: +6
        
        Args:
            level: Character level
            
        Returns:
            int: Proficiency bonus
        """
        pass
    
    @abstractmethod
    def get_saving_throw_proficiencies(self) -> List[str]:
        """
        Get saving throw proficiencies (each class gets 2).
        
        Returns:
            List[str]: List of ability scores with proficient saving throws
        """
        pass
    
    @abstractmethod
    def get_armor_proficiencies(self) -> List[str]:
        """
        Get armor proficiencies for this class.
        
        Returns:
            List[str]: Armor proficiencies
        """
        pass
    
    @abstractmethod
    def get_weapon_proficiencies(self) -> List[str]:
        """
        Get weapon proficiencies for this class.
        
        Returns:
            List[str]: Weapon proficiencies
        """
        pass
    
    @abstractmethod
    def get_tool_proficiencies(self) -> List[str]:
        """
        Get tool proficiencies for this class.
        
        Returns:
            List[str]: Tool proficiencies
        """
        pass
    
    @abstractmethod
    def get_skill_choices(self) -> Tuple[List[str], int]:
        """
        Get available skills and number of choices for this class.
        
        Returns:
            Tuple[List[str], int]: (Available skills, number to choose)
        """
        pass
    
    @abstractmethod
    def get_starting_equipment(self) -> Dict[str, Any]:
        """
        Get starting equipment options.
        
        Returns:
            Dict[str, Any]: Starting equipment choices
        """
        pass
    
    @abstractmethod
    def get_features_by_level(self, level: int) -> Dict[str, Any]:
        """
        Get class features gained at a specific level.
        
        Args:
            level: Class level
            
        Returns:
            Dict[str, Any]: Features gained at that level
        """
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self) -> List[int]:
        """
        Get levels at which Ability Score Improvements are gained.
        
        Per 2024 rules, standard ASI levels are 4, 8, 12, 16, and 19.
        
        Returns:
            List[int]: Levels with ASIs
        """
        pass
    
    @abstractmethod
    def get_spellcasting_ability(self) -> Optional[str]:
        """
        Get the spellcasting ability for this class, if any.
        
        Returns:
            Optional[str]: Ability used for spellcasting or None
        """
        pass
    
    @abstractmethod
    def get_spellcasting_type(self) -> SpellcastingType:
        """
        Get the type of spellcasting this class uses.
        
        Returns:
            SpellcastingType: Spellcasting type
        """
        pass
    
    @abstractmethod
    def get_spell_slots_by_level(self, class_level: int) -> Dict[int, int]:
        """
        Get available spell slots by spell level at a given class level.
        
        Args:
            class_level: Level in this class
            
        Returns:
            Dict[int, int]: {spell_level: num_slots}
        """
        pass
    
    @abstractmethod
    def get_cantrips_known(self, class_level: int) -> int:
        """
        Get number of cantrips known at a given level.
        
        Args:
            class_level: Level in this class
            
        Returns:
            int: Number of cantrips known
        """
        pass
    
    @abstractmethod
    def get_spells_known(self, class_level: int, ability_modifier: int = 0) -> int:
        """
        Get number of spells known or prepared at a given level.
        
        For prepared casters, this often includes ability modifier.
        
        Args:
            class_level: Level in this class
            ability_modifier: Spellcasting ability modifier
            
        Returns:
            int: Number of spells known/prepared
        """
        pass
    
    @abstractmethod
    def get_subclass_type(self) -> SubclassType:
        """
        Get when this class chooses a subclass.
        
        Returns:
            SubclassType: When subclass is chosen
        """
        pass
    
    @abstractmethod
    def get_multiclass_requirements(self) -> Dict[str, int]:
        """
        Get ability score requirements for multiclassing into this class.
        
        Returns:
            Dict[str, int]: Minimum scores needed {ability: min_score}
        """
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies gained when multiclassing into this class.
        
        Returns:
            Dict[str, List[str]]: Proficiencies by category
        """
        pass
    
    @abstractmethod
    def get_class_resources(self, level: int) -> Dict[str, Any]:
        """
        Get class-specific resources at a given level.
        
        Args:
            level: Class level
            
        Returns:
            Dict[str, Any]: Resources and their values/uses
        """
        pass

    @abstractmethod
    def get_multiclass_requirements(self) -> Dict[str, int]:
        """
        Get ability score requirements for multiclassing into this class.
        
        Returns:
            Dict[str, int]: Minimum scores needed {ability: min_score}
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple

class EquipmentCategory(Enum):
    """Official equipment categories in D&D 5e (2024 Edition)."""
    WEAPON = auto()
    ARMOR = auto()
    ADVENTURING_GEAR = auto()
    TOOL = auto()
    MOUNT = auto()
    VEHICLE = auto()
    TRADE_GOOD = auto()
    MAGIC_ITEM = auto()
    # Additional categories can be created for custom equipment

class WeaponType(Enum):
    """Official weapon types in D&D 5e (2024 Edition)."""
    SIMPLE_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_MELEE = auto()
    MARTIAL_RANGED = auto()
    # Additional weapon types can be created for custom equipment

class ArmorType(Enum):
    """Official armor types in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()
    # Additional armor types can be created for custom equipment

class DamageType(Enum):
    """Official damage types in D&D 5e (2024 Edition)."""
    ACID = auto()
    BLUDGEONING = auto()
    COLD = auto()
    FIRE = auto()
    FORCE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    PIERCING = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    SLASHING = auto()
    THUNDER = auto()
    # Additional damage types can be created for custom equipment

class WeaponProperty(Enum):
    """Official weapon properties in D&D 5e (2024 Edition)."""
    AMMUNITION = auto()
    FINESSE = auto()
    HEAVY = auto()
    LIGHT = auto()
    LOADING = auto()
    RANGE = auto()
    REACH = auto()
    SPECIAL = auto()
    THROWN = auto()
    TWO_HANDED = auto()
    VERSATILE = auto()
    # Additional weapon properties can be created for custom equipment

class Currency(Enum):
    """Official currency in D&D 5e (2024 Edition)."""
    CP = auto()  # Copper piece (100 CP = 1 GP)
    SP = auto()  # Silver piece (10 SP = 1 GP)
    EP = auto()  # Electrum piece (2 EP = 1 GP)
    GP = auto()  # Gold piece (base unit)
    PP = auto()  # Platinum piece (1 PP = 10 GP)
    # Additional currencies can be created for custom settings

class AbstractEquipment(ABC):
    """
    Abstract base class defining the contract for equipment in D&D 5e (2024 Edition).
    
    This interface supports both official D&D equipment and custom creations.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the equipment's name.
        
        Returns:
            str: Equipment name
        """
        pass
        
    @abstractmethod
    def get_category(self) -> EquipmentCategory:
        """
        Get the equipment's category.
        
        Returns:
            EquipmentCategory: Equipment category
        """
        pass
        
    @abstractmethod
    def get_cost(self) -> Dict[Currency, int]:
        """
        Get the equipment's cost in different currencies.
        
        Returns:
            Dict[Currency, int]: Cost in various currencies
        """
        pass
        
    @abstractmethod
    def get_weight(self) -> float:
        """
        Get the equipment's weight in pounds.
        
        Returns:
            float: Weight in pounds
        """
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the equipment's description.
        
        Returns:
            str: Equipment description
        """
        pass
        
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the equipment to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the equipment
        """
        pass


class AbstractWeapon(AbstractEquipment):
    """
    Abstract base class defining the contract for weapons in D&D 5e (2024 Edition).
    
    This interface supports both official D&D weapons and custom creations.
    """
    
    @abstractmethod
    def get_weapon_type(self) -> WeaponType:
        """
        Get the weapon's type.
        
        Returns:
            WeaponType: Type of weapon
        """
        pass
        
    @abstractmethod
    def get_damage_dice(self) -> str:
        """
        Get the weapon's damage dice expression.
        
        Returns:
            str: Damage dice (e.g., "1d8")
        """
        pass
        
    @abstractmethod
    def get_damage_type(self) -> DamageType:
        """
        Get the weapon's damage type.
        
        Returns:
            DamageType: Type of damage dealt
        """
        pass
        
    @abstractmethod
    def get_properties(self) -> List[WeaponProperty]:
        """
        Get the weapon's properties.
        
        Returns:
            List[WeaponProperty]: Weapon properties
        """
        pass
        
    @abstractmethod
    def get_range(self) -> Tuple[int, int]:
        """
        Get the weapon's range (for ranged weapons).
        
        Returns:
            Tuple[int, int]: (Normal range, Maximum range)
        """
        pass
        
    @abstractmethod
    def is_melee(self) -> bool:
        """
        Check if the weapon is melee.
        
        Returns:
            bool: True if melee, False if ranged
        """
        pass
        
    @abstractmethod
    def is_martial(self) -> bool:
        """
        Check if the weapon is martial.
        
        Returns:
            bool: True if martial, False if simple
        """
        pass
        
    @abstractmethod
    def calculate_damage(self, ability_modifier: int, is_versatile: bool = False) -> Tuple[str, int]:
        """
        Calculate weapon damage with ability modifier.
        
        Per D&D 2024 rules:
        - Melee weapons typically add Strength modifier to damage
        - Ranged weapons typically add Dexterity modifier to damage
        - Finesse weapons can use either Strength or Dexterity
        - Versatile weapons deal different damage when wielded with two hands
        
        Args:
            ability_modifier: Relevant ability modifier
            is_versatile: If using versatile weapon with two hands
            
        Returns:
            Tuple[str, int]: (Damage dice expression, Fixed damage bonus)
        """
        pass


class AbstractArmor(AbstractEquipment):
    """
    Abstract base class defining the contract for armor in D&D 5e (2024 Edition).
    
    This interface supports both official D&D armor and custom creations.
    """
    
    @abstractmethod
    def get_armor_type(self) -> ArmorType:
        """
        Get the armor's type.
        
        Returns:
            ArmorType: Type of armor
        """
        pass
        
    @abstractmethod
    def get_base_ac(self) -> int:
        """
        Get the armor's base AC.
        
        Returns:
            int: Base armor class
        """
        pass
        
    @abstractmethod
    def get_strength_requirement(self) -> int:
        """
        Get the armor's minimum strength requirement.
        
        Returns:
            int: Minimum strength required (0 if none)
        """
        pass
        
    @abstractmethod
    def has_stealth_disadvantage(self) -> bool:
        """
        Check if the armor imposes disadvantage on stealth checks.
        
        Returns:
            bool: True if disadvantage, False otherwise
        """
        pass
        
    @abstractmethod
    def get_max_dex_bonus(self) -> Optional[int]:
        """
        Get the maximum dexterity bonus allowed by the armor.
        
        Returns:
            Optional[int]: Maximum dexterity bonus (None if unlimited)
        """
        pass
        
    @abstractmethod
    def calculate_ac(self, dexterity_modifier: int) -> int:
        """
        Calculate total AC with dexterity modifier.
        
        Per D&D 2024 rules:
        - Light armor: AC + full Dexterity modifier
        - Medium armor: AC + Dexterity modifier (max +2)
        - Heavy armor: AC (no Dexterity modifier)
        - Shields: +2 AC
        
        Args:
            dexterity_modifier: Character's dexterity modifier
            
        Returns:
            int: Total armor class
        """
        pass


class AbstractEquipmentManager(ABC):
    """
    Abstract base class for managing equipment in D&D 5e (2024 Edition).
    
    This interface supports working with collections of equipment items.
    """
    
    @abstractmethod
    def get_all_weapons(self) -> Dict[str, AbstractWeapon]:
        """
        Get all available weapons.
        
        Returns:
            Dict[str, AbstractWeapon]: Dictionary of weapons by ID
        """
        pass
        
    @abstractmethod
    def get_all_armor(self) -> Dict[str, AbstractArmor]:
        """
        Get all available armor.
        
        Returns:
            Dict[str, AbstractArmor]: Dictionary of armor by ID
        """
        pass
        
    @abstractmethod
    def get_equipment_by_category(self, category: EquipmentCategory) -> Dict[str, AbstractEquipment]:
        """
        Get equipment by category.
        
        Args:
            category: Equipment category
            
        Returns:
            Dict[str, AbstractEquipment]: Dictionary of equipment by ID
        """
        pass
        
    @abstractmethod
    def get_starting_equipment_options(self, character_class: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get starting equipment options for a character class.
        
        Per D&D 2024 rules, each class has specific starting equipment options.
        
        Args:
            character_class: Character class name
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Starting equipment options
        """
        pass
        
    @abstractmethod
    def calculate_carrying_capacity(self, strength_score: int, size_multiplier: float = 1.0) -> Dict[str, float]:
        """
        Calculate carrying capacity based on strength.
        
        Per D&D 2024 rules:
        - Carrying capacity = strength score × 15 (in pounds)
        - Push/drag/lift = strength score × 30 (in pounds)
        - Size modifiers: Tiny ×0.5, Small ×1, Medium ×1, Large ×2, etc.
        
        Args:
            strength_score: Character's strength score
            size_multiplier: Multiplier based on creature size
            
        Returns:
            Dict[str, float]: Carrying capacity values
        """
        pass
        
    @abstractmethod
    def create_custom_equipment(self, equipment_data: Dict[str, Any]) -> AbstractEquipment:
        """
        Create a custom equipment item from data.
        
        Args:
            equipment_data: Equipment specifications
            
        Returns:
            AbstractEquipment: Custom equipment instance
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple

class FeatCategory(Enum):
    """Enumeration of official feat categories in D&D 5e (2024 Edition)."""
    GENERAL = auto()      # General feats available to anyone
    HEROIC = auto()       # Heroic tier feats (1st-level+)
    EPIC = auto()         # Epic tier feats (higher-level only)
    SPECIES = auto()      # Species-specific feats
    CLASS = auto()        # Class-specific feats
    BACKGROUND = auto()   # Background-specific feats
    # Additional categories can be created for custom feats

class AbstractFeat(ABC):
    """
    Abstract base class for feats in D&D 5e (2024 Edition).
    
    Per 2024 rules, feats represent special talents or expertise that give a character
    capabilities beyond what their class normally provides. They can be acquired:
    - At character creation (Background feat)
    - When reaching ability score improvement levels
    - Through certain class or species features
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the feat's name.
        
        Returns:
            str: Feat name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the feat's description.
        
        Returns:
            str: Feat description
        """
        pass
    
    @abstractmethod
    def get_category(self) -> FeatCategory:
        """
        Get the feat's category.
        
        Returns:
            FeatCategory: Feat category
        """
        pass
    
    @abstractmethod
    def get_prerequisites(self) -> Dict[str, Any]:
        """
        Get the feat's prerequisites.
        
        Per 2024 rules, prerequisites can include:
        - Minimum ability scores
        - Specific class/species/background requirements
        - Character level requirements
        - Other feat requirements (feat chains)
        
        Returns:
            Dict[str, Any]: Dictionary of prerequisites
        """
        pass
    
    @abstractmethod
    def get_benefits(self) -> Dict[str, Any]:
        """
        Get the feat's benefits.
        
        Per 2024 rules, benefits may include:
        - Ability score improvements
        - Skill proficiencies
        - New actions or bonus actions
        - Special abilities or resources
        
        Returns:
            Dict[str, Any]: Dictionary of benefits
        """
        pass
    
    @abstractmethod
    def get_min_level(self) -> int:
        """
        Get minimum character level required for the feat.
        
        Returns:
            int: Minimum level required
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert feat to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of feat
        """
        pass


class AbstractFeats(ABC):
    """
    Abstract base class for managing feats in D&D 5e (2024 Edition).
    
    Per 2024 rules:
    - Characters typically receive one feat at 1st level from their background
    - Additional feats can be gained at ASI levels (4th, 8th, 12th, 16th, 19th)
    - Some classes or species provide additional feat options
    - Feats can provide one-time benefits or ongoing abilities
    """
    
    @abstractmethod
    def get_all_feats(self) -> List[AbstractFeat]:
        """
        Return a list of all available feats.
        
        Returns:
            List[AbstractFeat]: List of all feats
        """
        pass
    
    @abstractmethod
    def get_feat_details(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a feat.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with feat details or None if not found
        """
        pass
    
    @abstractmethod
    def get_available_feats(self, character_data: Dict[str, Any]) -> List[AbstractFeat]:
        """
        Get feats available to a specific character based on prerequisites.
        
        Per 2024 rules, availability depends on:
        - Character level
        - Ability scores
        - Class, species, and background
        - Previously selected feats
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractFeat]: List of feats available to the character
        """
        pass
    
    @abstractmethod
    def validate_feat_prerequisites(self, character_data: Dict[str, Any], feat_name: str) -> Tuple[bool, str]:
        """
        Check if character meets feat prerequisites.
        
        Args:
            character_data: Character information
            feat_name: Name of the feat to check
            
        Returns:
            Tuple[bool, str]: (True if prerequisites met, explanation message)
        """
        pass
    
    @abstractmethod
    def apply_feat_benefits(self, character_data: Dict[str, Any], feat_name: str) -> Dict[str, Any]:
        """
        Apply the benefits of a feat to character stats.
        
        Args:
            character_data: Character information to modify
            feat_name: Name of the feat to apply
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass
    
    @abstractmethod
    def get_feats_by_category(self, category: FeatCategory) -> List[AbstractFeat]:
        """
        Get feats by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List[AbstractFeat]: List of feats in the category
        """
        pass
    
    @abstractmethod
    def get_background_feats(self) -> List[AbstractFeat]:
        """
        Get feats available for selection at 1st level via background.
        
        Per 2024 rules, every character receives one feat from their background.
        
        Returns:
            List[AbstractFeat]: List of background-appropriate feats
        """
        pass
    
    @abstractmethod
    def get_asi_replacement_feats(self, character_data: Dict[str, Any]) -> List[AbstractFeat]:
        """
        Get feats that can be taken instead of an Ability Score Improvement.
        
        Per 2024 rules, characters can select a feat instead of an ASI.
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractFeat]: List of feats available as ASI replacements
        """
        pass
    
    @abstractmethod
    def get_feat_usage_rules(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get rules for how a feat can be used (usage limits, recharge conditions).
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Usage rules or None if feat has no special usage limits
        """
        pass
    
    @abstractmethod
    def create_custom_feat(self, feat_data: Dict[str, Any]) -> AbstractFeat:
        """
        Create a custom feat from provided specifications.
        
        Args:
            feat_data: Feat specifications
            
        Returns:
            AbstractFeat: New custom feat
        """
        pass
    
    @abstractmethod
    def validate_custom_feat(self, feat_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom feat against D&D 2024 design principles.
        
        Args:
            feat_data: Custom feat specifications
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def get_suggested_feat_progressions(self, character_concept: Dict[str, Any]) -> List[List[str]]:
        """
        Get suggested feat progressions for a character concept.
        
        Args:
            character_concept: Character concept including class, playstyle, etc.
            
        Returns:
            List[List[str]]: List of feat progression paths
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import math
import random

class AbstractMulticlassAndLevelUp(ABC):
    """
    Abstract base class defining the contract for character level-up and multiclassing 
    in D&D 5e (2024 Edition).
    
    This interface focuses exclusively on the rules governing character advancement
    through level-up and multiclassing.
    """
    
    # Experience point thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Proficiency bonus by level
    PROFICIENCY_BONUS = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    @abstractmethod
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """Level up the character in their current class or a new class."""
        pass
    
    @abstractmethod
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """Check if character meets ability score requirements to multiclass."""
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """Get proficiencies gained when multiclassing into a specific class."""
        pass
    
    @abstractmethod
    def calculate_multiclass_spellcaster_level(self) -> int:
        """Calculate effective spellcaster level for determining spell slots."""
        pass
    
    @abstractmethod
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """Get available spell slots based on multiclass spellcaster level."""
        pass
    
    @abstractmethod
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """Calculate hit points gained when leveling up in a multiclass."""
        pass
    
    @abstractmethod
    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        pass
    
    @abstractmethod
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """Get features gained for a specific class at a specific level."""
        pass
    
    @abstractmethod
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """Apply choices made during level up."""
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """Get levels at which a class grants Ability Score Improvements."""
        pass
    
    @abstractmethod
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """Check if character is eligible for level up based on XP."""
        pass
    
    @abstractmethod
    def get_next_level_xp_threshold(self) -> int:
        """Get XP needed for next level."""
        pass
    
    @abstractmethod
    def calculate_character_level(self) -> int:
        """Calculate total character level from all class levels."""
        pass
    
    @abstractmethod
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """Get all classes and whether character qualifies to multiclass into them."""
        pass


class DNDMulticlassAndLevelUp(AbstractMulticlassAndLevelUp):
    """
    Concrete implementation of D&D 2024 multiclass and level-up rules.
    
    This class implements the actual game mechanics for character advancement.
    """
    
    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize with character data.
        
        Args:
            character_data: Current character information
        """
        self.character_data = character_data
        
        # D&D 2024 class data
        self.class_data = {
            "Barbarian": {
                "hit_die": 12,
                "primary_ability": "strength",
                "multiclass_requirements": {"strength": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": None,
                "multiclass_proficiencies": {
                    "armor": ["shields", "simple weapons", "martial weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Bard": {
                "hit_die": 8,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_any"],
                    "tools": ["choose_1_musical_instrument"]
                }
            },
            "Cleric": {
                "hit_die": 8,
                "primary_ability": "wisdom",
                "multiclass_requirements": {"wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "shields"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Druid": {
                "hit_die": 8,
                "primary_ability": "wisdom",
                "multiclass_requirements": {"wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "armor": ["leather_armor", "studded_leather", "shields"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Fighter": {
                "hit_die": 10,
                "primary_ability": ["strength", "dexterity"],  # Either works
                "multiclass_requirements": {"strength": 13, "dexterity": 13},  # Either 13+ works
                "asi_levels": [4, 6, 8, 12, 14, 16, 19],  # Fighter gets extra ASIs
                "spellcaster_type": None,  # Base class, subclasses may vary
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "heavy_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Monk": {
                "hit_die": 8,
                "primary_ability": ["dexterity", "wisdom"],
                "multiclass_requirements": {"dexterity": 13, "wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": None,
                "multiclass_proficiencies": {
                    "weapons": ["simple_weapons", "shortswords"],
                    "tools": ["choose_1_artisan_or_musical"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Paladin": {
                "hit_die": 10,
                "primary_ability": ["strength", "charisma"],
                "multiclass_requirements": {"strength": 13, "charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "half",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "heavy_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Ranger": {
                "hit_die": 10,
                "primary_ability": ["dexterity", "wisdom"],
                "multiclass_requirements": {"dexterity": 13, "wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "half",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Rogue": {
                "hit_die": 8,
                "primary_ability": "dexterity",
                "multiclass_requirements": {"dexterity": 13},
                "asi_levels": [4, 8, 10, 12, 16, 19],  # Rogue gets extra ASI at 10
                "spellcaster_type": None,  # Base class, Arcane Trickster is 1/3
                "multiclass_proficiencies": {
                    "armor": ["light_armor"],
                    "weapons": ["simple_weapons", "hand_crossbows", "longswords", "rapiers", "shortswords"],
                    "tools": ["thieves_tools"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Sorcerer": {
                "hit_die": 6,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Warlock": {
                "hit_die": 8,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "warlock",  # Special case - pact magic
                "multiclass_proficiencies": {
                    "armor": ["light_armor"],
                    "weapons": ["simple_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Wizard": {
                "hit_die": 6,
                "primary_ability": "intelligence",
                "multiclass_requirements": {"intelligence": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_class_list"]
                }
            }
        }
        
        # Full caster spell slot progression (levels 1-20)
        self.full_caster_slots = {
            1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
            6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        }
    
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """Level up the character in their current class or a new class."""
        current_level = self.calculate_character_level()
        new_level = current_level + 1
        
        if new_level > 20:
            return {"error": "Cannot exceed level 20"}
        
        # Determine class to level up in
        if new_class:
            # Multiclassing
            can_multiclass, reason = self.can_multiclass_into(new_class)
            if not can_multiclass:
                return {"error": f"Cannot multiclass into {new_class}: {reason}"}
            target_class = new_class
            is_first_level_in_class = self.get_level_in_class(new_class) == 0
        else:
            # Level up in existing class (primary class)
            classes = self.character_data.get("classes", {})
            if not classes:
                return {"error": "No classes found"}
            target_class = max(classes.items(), key=lambda x: x[1])[0]
            is_first_level_in_class = False
        
        # Calculate changes
        results = {
            "new_level": new_level,
            "class_leveled": target_class,
            "is_multiclass": new_class is not None,
            "is_first_level_in_class": is_first_level_in_class
        }
        
        # Hit point increase
        hp_increase = self.calculate_multiclass_hit_points(target_class, is_first_level_in_class)
        results["hp_increase"] = hp_increase
        
        # Update class levels
        current_classes = self.character_data.get("classes", {}).copy()
        new_class_level = current_classes.get(target_class, 0) + 1
        current_classes[target_class] = new_class_level
        results["new_class_levels"] = current_classes
        
        # Check for ASI
        asi_levels = self.get_ability_score_improvement_levels(target_class)
        if new_class_level in asi_levels:
            results["asi_available"] = True
            results["asi_options"] = self._get_asi_options()
        else:
            results["asi_available"] = False
        
        # Update proficiency bonus
        results["proficiency_bonus"] = self.PROFICIENCY_BONUS[new_level]
        
        # Get new class features
        features = self.get_features_for_multiclass(target_class, new_class_level)
        results["new_features"] = features
        
        # Handle spellcasting
        if self._is_spellcaster():
            results["spell_slots"] = self.get_multiclass_spell_slots()
            results["new_spells"] = self._calculate_new_spells(target_class, new_class_level)
        
        # Multiclass proficiencies (if applicable)
        if new_class and is_first_level_in_class:
            results["multiclass_proficiencies"] = self.get_multiclass_proficiencies(new_class)
        
        return results
    
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """Check if character meets ability score requirements to multiclass."""
        if new_class not in self.class_data:
            return False, f"Unknown class: {new_class}"
        
        # Check if already at level 20
        if self.calculate_character_level() >= 20:
            return False, "Already at maximum level (20)"
        
        class_info = self.class_data[new_class]
        requirements = class_info["multiclass_requirements"]
        ability_scores = self.character_data.get("ability_scores", {})
        
        # Check current class requirements (must have 13+ in primary ability to multiclass OUT)
        current_classes = self.character_data.get("classes", {})
        for current_class in current_classes:
            if current_class in self.class_data:
                current_requirements = self.class_data[current_class]["multiclass_requirements"]
                for ability, min_score in current_requirements.items():
                    if ability_scores.get(ability, 10) < min_score:
                        return False, f"Need {ability.title()} {min_score}+ to multiclass out of {current_class}"
        
        # Check new class requirements
        for ability, min_score in requirements.items():
            current_score = ability_scores.get(ability, 10)
            if current_score < min_score:
                return False, f"Need {ability.title()} {min_score}+ (currently {current_score})"
        
        return True, "Multiclass requirements met"
    
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """Get proficiencies gained when multiclassing into a specific class."""
        if new_class not in self.class_data:
            return {}
        
        return self.class_data[new_class].get("multiclass_proficiencies", {})
    
    def calculate_multiclass_spellcaster_level(self) -> int:
        """Calculate effective spellcaster level for determining spell slots."""
        classes = self.character_data.get("classes", {})
        total_caster_level = 0
        
        for class_name, class_level in classes.items():
            if class_name not in self.class_data:
                continue
                
            caster_type = self.class_data[class_name]["spellcaster_type"]
            
            if caster_type == "full":
                total_caster_level += class_level
            elif caster_type == "half":
                total_caster_level += class_level // 2
            elif caster_type == "third":
                total_caster_level += class_level // 3
            # Warlock pact magic doesn't contribute to multiclass spell slots
        
        return total_caster_level
    
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """Get available spell slots based on multiclass spellcaster level."""
        caster_level = self.calculate_multiclass_spellcaster_level()
        
        if caster_level == 0:
            return {}
        
        # Cap at 20 for spell slot purposes
        caster_level = min(caster_level, 20)
        
        return self.full_caster_slots.get(caster_level, {})
    
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """Calculate hit points gained when leveling up in a multiclass."""
        if new_class not in self.class_data:
            return 1  # Minimum 1 HP
        
        hit_die = self.class_data[new_class]["hit_die"]
        con_mod = self._get_ability_modifier("constitution")
        
        if is_first_level and self.calculate_character_level() == 0:
            # First character level ever - max hit die
            return hit_die + con_mod
        else:
            # Take average (rounded up) + CON modifier
            average_roll = (hit_die // 2) + 1
            return max(1, average_roll + con_mod)  # Minimum 1 HP per level
    
    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        classes = self.character_data.get("classes", {})
        return classes.get(class_name, 0)
    
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """Get features gained for a specific class at a specific level."""
        # This would be expanded with actual class feature data
        # For now, return basic information
        features = {
            "class": class_name,
            "level": level,
            "features": []
        }
        
        # Add some basic features based on common patterns
        if level == 1:
            features["features"].append(f"{class_name} proficiencies and starting features")
        elif level == 2:
            features["features"].append(f"{class_name} level 2 features")
        elif level == 3:
            features["features"].append(f"Subclass choice for {class_name}")
        
        # Add ASI notification
        asi_levels = self.get_ability_score_improvement_levels(class_name)
        if level in asi_levels:
            features["features"].append("Ability Score Improvement available")
        
        return features
    
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """Apply choices made during level up."""
        try:
            # Apply ability score improvements
            if "asi_choices" in choices:
                asi_choices = choices["asi_choices"]
                current_scores = self.character_data.get("ability_scores", {})
                
                for ability, increase in asi_choices.items():
                    if ability in current_scores:
                        new_score = min(20, current_scores[ability] + increase)
                        current_scores[ability] = new_score
                
                self.character_data["ability_scores"] = current_scores
            
            # Apply class level increases
            if "new_class_levels" in choices:
                self.character_data["classes"] = choices["new_class_levels"]
            
            # Update character level
            if "new_level" in choices:
                self.character_data["level"] = choices["new_level"]
            
            # Apply new spells
            if "spell_choices" in choices:
                current_spells = self.character_data.get("spells_known", {})
                for spell_level, spells in choices["spell_choices"].items():
                    if spell_level not in current_spells:
                        current_spells[spell_level] = []
                    current_spells[spell_level].extend(spells)
                self.character_data["spells_known"] = current_spells
            
            return True
            
        except Exception as e:
            print(f"Error applying level up choices: {e}")
            return False
    
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """Get levels at which a class grants Ability Score Improvements."""
        if class_name not in self.class_data:
            return [4, 8, 12, 16, 19]  # Default ASI levels
        
        return self.class_data[class_name]["asi_levels"]
    
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """Check if character is eligible for level up based on XP."""
        current_xp = self.character_data.get("experience_points", 0)
        current_level = self.calculate_character_level()
        
        if current_level >= 20:
            return False, "Already at maximum level (20)"
        
        next_threshold = self.get_next_level_xp_threshold()
        
        if current_xp >= next_threshold:
            return True, f"Ready to level up! (XP: {current_xp}/{next_threshold})"
        else:
            needed_xp = next_threshold - current_xp
            return False, f"Need {needed_xp} more XP to level up (XP: {current_xp}/{next_threshold})"
    
    def get_next_level_xp_threshold(self) -> int:
        """Get XP needed for next level."""
        current_level = self.calculate_character_level()
        next_level = min(current_level + 1, 20)
        return self.XP_THRESHOLDS[next_level]
    
    def calculate_character_level(self) -> int:
        """Calculate total character level from all class levels."""
        classes = self.character_data.get("classes", {})
        return sum(classes.values())
    
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """Get all classes and whether character qualifies to multiclass into them."""
        result = {}
        
        for class_name in self.class_data.keys():
            # Skip if already have this class
            if self.get_level_in_class(class_name) > 0:
                result[class_name] = False
            else:
                can_multiclass, _ = self.can_multiclass_into(class_name)
                result[class_name] = can_multiclass
        
        return result
    
    # Helper methods
    def _get_ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier from score."""
        score = self.character_data.get("ability_scores", {}).get(ability, 10)
        return (score - 10) // 2
    
    def _is_spellcaster(self) -> bool:
        """Check if character has any spellcasting abilities."""
        classes = self.character_data.get("classes", {})
        
        for class_name in classes.keys():
            if class_name in self.class_data:
                caster_type = self.class_data[class_name]["spellcaster_type"]
                if caster_type in ["full", "half", "third", "warlock"]:
                    return True
        
        return False
    
    def _get_asi_options(self) -> Dict[str, Any]:
        """Get available ASI options."""
        return {
            "ability_scores": {
                "strength": "Increase Strength by 1 or 2",
                "dexterity": "Increase Dexterity by 1 or 2", 
                "constitution": "Increase Constitution by 1 or 2",
                "intelligence": "Increase Intelligence by 1 or 2",
                "wisdom": "Increase Wisdom by 1 or 2",
                "charisma": "Increase Charisma by 1 or 2"
            },
            "feats": "Choose a feat instead of ability score increase",
            "notes": "Total increases cannot exceed +2, and no ability can exceed 20"
        }
    
    def _calculate_new_spells(self, class_name: str, class_level: int) -> Dict[str, List[str]]:
        """Calculate new spells learned at this level."""
        # Simplified spell learning - would need full spell progression tables
        new_spells = {}
        
        caster_type = self.class_data.get(class_name, {}).get("spellcaster_type")
        
        if caster_type == "full":
            # Full casters learn new spells regularly
            if class_level <= 17:  # Can learn up to 9th level spells
                max_spell_level = min((class_level + 1) // 2, 9)
                if class_level % 2 == 1:  # Odd levels often unlock new spell levels
                    new_spells[str(max_spell_level)] = [f"New {max_spell_level} level spell"]
        elif caster_type == "half":
            # Half casters learn spells more slowly
            if class_level >= 2 and class_level <= 17:
                max_spell_level = min((class_level - 1) // 4 + 1, 5)
                if class_level in [3, 5, 9, 13, 17]:  # Key spell learning levels
                    new_spells[str(max_spell_level)] = [f"New {max_spell_level} level spell"]
        
        return new_spells
    
    # Legacy compatibility methods (for existing character creator)
    def calculate_level_up_changes(self, current_character: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """Legacy method for backward compatibility with existing character creator."""
        self.character_data = current_character
        
        # Calculate what class to level up in
        current_level = current_character.get("level", 1)
        classes = current_character.get("classes", {"Fighter": current_level})
        
        # For single class, continue in that class
        if len(classes) == 1:
            target_class = list(classes.keys())[0]
        else:
            # For multiclass, level up primary class
            target_class = max(classes.items(), key=lambda x: x[1])[0]
        
        # Simulate level up
        level_up_result = self.level_up()
        
        # Convert to legacy format
        changes = {
            "proficiency_bonus": self.PROFICIENCY_BONUS[new_level],
            "class_levels": level_up_result.get("new_class_levels", classes),
            "hit_points": level_up_result.get("hp_increase", 1),
            "new_proficiencies": [],
            "suggested_equipment": self._suggest_level_appropriate_equipment(new_level)
        }
        
        if level_up_result.get("asi_available"):
            changes["ability_score_improvements"] = self._suggest_asi_improvements(current_character)
        
        if self._is_spellcaster():
            changes["new_spells"] = level_up_result.get("new_spells", {})
            changes["spell_slots"] = level_up_result.get("spell_slots", {})
        
        return changes
    
    def _suggest_asi_improvements(self, character: Dict[str, Any]) -> Dict[str, int]:
        """Legacy method: Suggest ability score improvements."""
        abilities = character.get("ability_scores", {})
        classes = character.get("classes", {})
        
        # Find primary class
        if classes:
            primary_class = max(classes.items(), key=lambda x: x[1])[0]
            if primary_class in self.class_data:
                primary_ability = self.class_data[primary_class]["primary_ability"]
                if isinstance(primary_ability, list):
                    # Choose the higher of the two abilities
                    primary_ability = max(primary_ability, key=lambda a: abilities.get(a, 10))
            else:
                primary_ability = "strength"
        else:
            primary_ability = "strength"
        
        # Suggest improving primary ability or constitution
        current_primary = abilities.get(primary_ability, 10)
        current_con = abilities.get("constitution", 10)
        
        if current_primary < 20:
            return {primary_ability: 2}
        elif current_con < 16:
            return {"constitution": 2}
        else:
            return {"dexterity": 2}  # Default fallback
    
    def _suggest_level_appropriate_equipment(self, new_level: int) -> List[str]:
        """Legacy method: Suggest equipment appropriate for the character level."""
        suggestions = []
        
        if new_level == 3:
            suggestions.append("Masterwork weapon")
        elif new_level == 5:
            suggestions.append("Magic weapon +1")
        elif new_level == 10:
            suggestions.append("Magic armor +1")
        elif new_level == 15:
            suggestions.append("Rare magical item")
        elif new_level == 20:
            suggestions.append("Legendary magical item")
        
        return suggestions

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ProficiencyLevel(Enum):
    """Enumeration of proficiency levels for skills in D&D 5e (2024 Edition)."""
    NONE = 0        # No proficiency (0x proficiency bonus)
    PROFICIENT = 1  # Proficient (1x proficiency bonus)
    EXPERT = 2      # Expertise (2x proficiency bonus)

class SkillCategory(Enum):
    """Categorization of skills by common usage in D&D 5e."""
    SOCIAL = auto()      # Social interaction skills
    EXPLORATION = auto()  # Exploration and environment skills
    KNOWLEDGE = auto()    # Knowledge and information skills
    PHYSICAL = auto()     # Physical activity skills
    PERCEPTION = auto()   # Awareness and detection skills

class AbstractSkills(ABC):
    """
    Abstract base class for handling character skills in D&D 5e (2024 Edition).
    
    Skills in D&D represent specific areas of training and expertise that characters
    can use to overcome challenges. Each skill is tied to one of the six ability scores
    and can have different levels of proficiency.
    """
    
    # Standard skills in D&D 5e (2024 Edition)
    STANDARD_SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Map skills to their primary abilities
    SKILL_TO_ABILITY = {
        "Acrobatics": "dexterity",
        "Animal Handling": "wisdom",
        "Arcana": "intelligence",
        "Athletics": "strength",
        "Deception": "charisma",
        "History": "intelligence",
        "Insight": "wisdom",
        "Intimidation": "charisma",
        "Investigation": "intelligence",
        "Medicine": "wisdom",
        "Nature": "intelligence",
        "Perception": "wisdom",
        "Performance": "charisma",
        "Persuasion": "charisma",
        "Religion": "intelligence",
        "Sleight of Hand": "dexterity",
        "Stealth": "dexterity",
        "Survival": "wisdom"
    }
    
    # Map skills to categories
    SKILL_TO_CATEGORY = {
        "Acrobatics": SkillCategory.PHYSICAL,
        "Animal Handling": SkillCategory.SOCIAL,
        "Arcana": SkillCategory.KNOWLEDGE,
        "Athletics": SkillCategory.PHYSICAL,
        "Deception": SkillCategory.SOCIAL,
        "History": SkillCategory.KNOWLEDGE,
        "Insight": SkillCategory.SOCIAL,
        "Intimidation": SkillCategory.SOCIAL,
        "Investigation": SkillCategory.KNOWLEDGE,
        "Medicine": SkillCategory.KNOWLEDGE,
        "Nature": SkillCategory.KNOWLEDGE,
        "Perception": SkillCategory.PERCEPTION,
        "Performance": SkillCategory.SOCIAL,
        "Persuasion": SkillCategory.SOCIAL,
        "Religion": SkillCategory.KNOWLEDGE,
        "Sleight of Hand": SkillCategory.PHYSICAL,
        "Stealth": SkillCategory.PHYSICAL,
        "Survival": SkillCategory.EXPLORATION
    }
    
    @abstractmethod
    def get_skill_ability(self, skill_name: str) -> str:
        """
        Get the ability associated with a skill.
        
        Per D&D 2024 rules, each skill is associated with a specific ability.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            str: Associated ability ("strength", "dexterity", etc.)
        """
        pass
    
    @abstractmethod
    def calculate_skill_modifier(self, skill_name: str, ability_scores: Dict[str, int],
                              proficiency_bonus: int) -> int:
        """
        Calculate modifier for a skill check.
        
        Per D&D 2024 rules:
        - Base modifier is the ability score modifier
        - Add proficiency bonus if proficient
        - Add twice proficiency bonus if expert
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            int: Total skill modifier
        """
        pass
    
    @abstractmethod
    def set_skill_proficiency(self, skill_name: str, proficiency_level: ProficiencyLevel) -> bool:
        """
        Set proficiency level for a skill.
        
        Args:
            skill_name: Name of the skill
            proficiency_level: Level of proficiency
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def get_proficiency_level(self, skill_name: str) -> ProficiencyLevel:
        """
        Get proficiency level for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            ProficiencyLevel: Current proficiency level
        """
        pass
    
    @abstractmethod
    def get_skill_dc_by_difficulty(self, difficulty: str) -> int:
        """
        Get recommended DC for a skill check based on difficulty.
        
        Per D&D 2024 rules:
        - Very Easy: DC 5
        - Easy: DC 10
        - Moderate: DC 15
        - Hard: DC 20
        - Very Hard: DC 25
        - Nearly Impossible: DC 30
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            int: Recommended DC
        """
        pass
    
    @abstractmethod
    def get_skills_by_ability(self, ability: str) -> List[str]:
        """
        Get skills associated with a specific ability.
        
        Args:
            ability: Ability name (e.g., "strength", "dexterity")
            
        Returns:
            List[str]: List of skills for that ability
        """
        pass
    
    @abstractmethod
    def get_skills_by_category(self, category: SkillCategory) -> List[str]:
        """
        Get skills by category.
        
        Args:
            category: Skill category to filter by
            
        Returns:
            List[str]: List of skills in the category
        """
        pass
    
    @abstractmethod
    def get_passive_skill_value(self, skill_name: str, ability_scores: Dict[str, int],
                             proficiency_bonus: int) -> int:
        """
        Calculate passive value for a skill.
        
        Per D&D 2024 rules, passive check = 10 + skill modifier.
        Most commonly used for Perception but applicable to any skill.
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            int: Passive skill value
        """
        pass
    
    @abstractmethod
    def perform_skill_check(self, skill_name: str, ability_scores: Dict[str, int],
                         proficiency_bonus: int, difficulty_class: int,
                         advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Perform a skill check.
        
        Per D&D 2024 rules:
        - Roll d20 + ability modifier + applicable proficiency bonus
        - With advantage, roll twice and take the higher roll
        - With disadvantage, roll twice and take the lower roll
        - Success if result equals or exceeds the DC
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            difficulty_class: DC of the check
            advantage: Whether the check has advantage
            disadvantage: Whether the check has disadvantage
            
        Returns:
            Dict[str, Any]: Result of the skill check including:
                - success: Whether the check succeeded
                - roll: The dice roll result
                - total: The total check result
                - modifier: The total modifier applied
        """
        pass
    
    @abstractmethod
    def handle_group_check(self, skill_name: str, character_modifiers: List[int],
                        difficulty_class: int) -> Dict[str, Any]:
        """
        Perform a group check for multiple characters.
        
        Per D&D 2024 rules, group checks succeed if at least half the group succeeds.
        
        Args:
            skill_name: Skill being checked
            character_modifiers: List of each character's modifier for the skill
            difficulty_class: DC of the check
            
        Returns:
            Dict[str, Any]: Result of the group check
        """
        pass
    
    @abstractmethod
    def get_class_skills(self, character_class: str) -> List[str]:
        """
        Get skills typically associated with a class.
        
        Per D&D 2024 rules, each class has a list of skills to choose from
        for starting proficiencies.
        
        Args:
            character_class: Character's class
            
        Returns:
            List[str]: Skills associated with the class
        """
        pass
    
    @abstractmethod
    def get_background_skills(self, background: str) -> List[str]:
        """
        Get skills granted by a background.
        
        Per D&D 2024 rules, backgrounds typically provide two skill proficiencies.
        
        Args:
            background: Character's background
            
        Returns:
            List[str]: Skills granted by the background
        """
        pass
    
    @abstractmethod
    def get_proficient_skills(self) -> List[str]:
        """
        Get list of skills the character is proficient in.
        
        Returns:
            List[str]: Skills with proficiency
        """
        pass
    
    @abstractmethod
    def get_expertise_skills(self) -> List[str]:
        """
        Get list of skills the character has expertise in.
        
        Returns:
            List[str]: Skills with expertise
        """
        pass
    
    @abstractmethod
    def calculate_all_skill_modifiers(self, ability_scores: Dict[str, int],
                                   proficiency_bonus: int) -> Dict[str, int]:
        """
        Calculate modifiers for all skills.
        
        Args:
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            Dict[str, int]: Mapping of skill names to modifiers
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class SpeciesSize(Enum):
    """Official species sizes in D&D 5e (2024 Edition)."""
    TINY = auto()
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    HUGE = auto()
    GARGANTUAN = auto()

class AbstractSpecies(ABC):
    """
    Abstract base class defining the contract for character species in D&D 5e (2024 Edition).
    
    Per D&D 2024 rules, species (formerly known as races) define inherent character traits such as:
    - Size (typically Small or Medium for player characters)
    - Base walking speed (typically 25-35 feet)
    - Vision types (normal vision, darkvision, etc.)
    - Languages known
    - Special traits and abilities
    - Damage resistances or immunities (if any)
    - Tool or skill proficiencies (if any)
    
    This interface supports both official D&D species and custom creations.
    """
    
    # Core species from the 2024 Player's Handbook
    CORE_SPECIES = [
        "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome",
        "Goliath", "Halfling", "Human", "Orc", "Tiefling"
    ]
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the species.
        
        Returns:
            str: Species name
        """
        pass
    
    @abstractmethod
    def get_size(self) -> SpeciesSize:
        """
        Get the size category of the species.
        
        Per D&D 2024 rules, most playable species are Small or Medium.
        
        Returns:
            SpeciesSize: Size category
        """
        pass
    
    @abstractmethod
    def get_base_speed(self) -> int:
        """
        Get the base walking speed in feet.
        
        Per D&D 2024 rules, this is typically 30 feet, with some exceptions:
        - Dwarves and small species often have 25 feet
        - Some species have enhanced speed (35 or 40 feet)
        
        Returns:
            int: Base walking speed in feet
        """
        pass
    
    @abstractmethod
    def get_movement_types(self) -> Dict[str, int]:
        """
        Get all movement types and speeds.
        
        Some species have additional movement types such as:
        - Flying
        - Swimming
        - Climbing
        - Burrowing
        
        Returns:
            Dict[str, int]: Dictionary mapping movement type to speed in feet
        """
        pass
    
    @abstractmethod
    def get_ability_score_increases(self) -> Dict[str, int]:
        """
        Get ability score increases granted by the species.
        
        Per D&D 2024 rules, species may provide ability score increases.
        
        Returns:
            Dict[str, int]: Dictionary mapping ability names to increases
        """
        pass
    
    @abstractmethod
    def get_vision_types(self) -> Dict[str, int]:
        """
        Get special vision types and their ranges.
        
        Per D&D 2024 rules, vision types include:
        - Normal vision (default)
        - Darkvision (common, 60-120 ft range)
        - Blindsight (rare)
        - Tremorsense (rare)
        - Truesight (very rare)
        
        Returns:
            Dict[str, int]: Dictionary mapping vision type to range in feet
        """
        pass
    
    @abstractmethod
    def get_languages(self) -> List[str]:
        """
        Get languages known by the species.
        
        Per D&D 2024 rules, most species know Common plus additional languages.
        
        Returns:
            List[str]: List of languages
        """
        pass
    
    @abstractmethod
    def get_damage_resistances(self) -> List[str]:
        """
        Get damage types the species has resistance to.
        
        Returns:
            List[str]: List of damage types
        """
        pass
    
    @abstractmethod
    def get_damage_immunities(self) -> List[str]:
        """
        Get damage types the species has immunity to.
        
        Returns:
            List[str]: List of damage types
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> List[str]:
        """
        Get conditions the species has immunity to.
        
        Returns:
            List[str]: List of conditions
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> Dict[str, Any]:
        """
        Get the species-specific traits and abilities.
        
        Per D&D 2024 rules, species traits define unique capabilities and may include:
        - Natural weapons
        - Magical abilities
        - Environmental adaptations
        - Cultural benefits
        
        Returns:
            Dict[str, Any]: Dictionary mapping trait names to descriptions and mechanics
        """
        pass
    
    @abstractmethod
    def get_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies granted by the species.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping proficiency types (skills, tools) to lists
        """
        pass
    
    @abstractmethod
    def get_lineages(self) -> List[str]:
        """
        Get available lineages or subraces for the species.
        
        Per D&D 2024 rules, many species have lineage options that provide additional
        or replacement traits.
        
        Returns:
            List[str]: List of available lineages
        """
        pass
    
    @abstractmethod
    def get_lineage_details(self, lineage: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific lineage.
        
        Args:
            lineage: Name of the lineage
            
        Returns:
            Optional[Dict[str, Any]]: Lineage details or None if not found
        """
        pass
    
    @abstractmethod
    def has_feature(self, feature_name: str) -> bool:
        """
        Check if the species has a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            bool: True if the species has the feature
        """
        pass
    
    @abstractmethod
    def get_age_range(self) -> Tuple[int, int]:
        """
        Get the typical age range for the species.
        
        Per D&D 2024 rules, species vary widely in lifespan.
        
        Returns:
            Tuple[int, int]: (Maturity age, Maximum age)
        """
        pass
    
    @abstractmethod
    def get_size_dimensions(self) -> Dict[str, Tuple[float, float]]:
        """
        Get typical height and weight ranges for the species.
        
        Per D&D 2024 rules, each species has typical physical dimensions.
        
        Returns:
            Dict[str, Tuple[float, float]]: Dictionary with height and weight ranges
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert species information to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of species
        """
        pass
    
    @abstractmethod
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the species definition against D&D 2024 rules.
        
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def apply_to_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the species traits and bonuses to a character.
        
        Args:
            character_data: Character information to modify
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass


class AbstractSpeciesRegistry(ABC):
    """
    Abstract base class for a registry of species in D&D 5e (2024 Edition).
    
    This interface supports managing collections of species, including custom creations.
    """
    
    @abstractmethod
    def get_all_species(self) -> List[str]:
        """
        Get a list of all available species names.
        
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_details(self, species_name: str) -> Optional[AbstractSpecies]:
        """
        Get detailed information about a species.
        
        Args:
            species_name: Name of the species
            
        Returns:
            Optional[AbstractSpecies]: Species instance or None if not found
        """
        pass
    
    @abstractmethod
    def get_species_by_size(self, size: SpeciesSize) -> List[str]:
        """
        Get species that are of a specific size.
        
        Args:
            size: Size category to filter by
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_by_ability_bonus(self, ability: str) -> List[str]:
        """
        Get species that provide a bonus to a specific ability.
        
        Args:
            ability: Ability score name
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_by_feature(self, feature: str) -> List[str]:
        """
        Get species that have a specific feature.
        
        Args:
            feature: Feature to search for
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def register_custom_species(self, species_data: Dict[str, Any]) -> AbstractSpecies:
        """
        Create and register a custom species.
        
        Args:
            species_data: Custom species definition
            
        Returns:
            AbstractSpecies: New custom species instance
        """
        pass
    
    @abstractmethod
    def get_core_species(self) -> List[str]:
        """
        Get only the core species from the 2024 Player's Handbook.
        
        Returns:
            List[str]: List of core species names
        """
        pass
    
    @abstractmethod
    def validate_custom_species(self, species_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom species definition against D&D 2024 design principles.
        
        Args:
            species_data: Custom species definition
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from enum import Enum, auto

class SpellLevel(Enum):
    """Enum representing spell levels in D&D"""
    CANTRIP = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    # Custom levels could be added for homebrew high-level magic

class CastingTime(Enum):
    """Enum representing spell casting times in D&D"""
    ACTION = "1 action"
    BONUS_ACTION = "1 bonus action"
    REACTION = "1 reaction"
    MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWELVE_HOURS = "12 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    CUSTOM = "custom"  # For special cases

class SpellRange(Enum):
    """Enum representing common spell ranges in D&D"""
    SELF = "self"
    TOUCH = "touch"
    SIGHT = "sight"
    UNLIMITED = "unlimited"
    CUSTOM = "custom"  # For specific distances like 30 feet, 60 feet, etc.

class SpellDuration(Enum):
    """Enum representing spell durations in D&D"""
    INSTANTANEOUS = "instantaneous"
    ONE_ROUND = "1 round"
    ONE_MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    ONE_HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    SEVEN_DAYS = "7 days"
    THIRTY_DAYS = "30 days"
    UNTIL_DISPELLED = "until dispelled"
    CUSTOM = "custom"  # For special durations

class MagicSchool(Enum):
    """Enum representing the schools of magic in D&D"""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration" 
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"
    # The interface allows for custom schools beyond the standard eight

class DamageType(Enum):
    """Enum representing damage types in D&D"""
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing" 
    THUNDER = "thunder"
    # Custom damage types can be added for unique spells

class AreaOfEffect(Enum):
    """Enum representing area of effect shapes in D&D"""
    CONE = "cone"
    CUBE = "cube"
    CYLINDER = "cylinder"
    LINE = "line"
    SPHERE = "sphere"
    EMANATION = "emanation"  # New in 2024 rules
    CUSTOM = "custom"  # For special shapes

class SpellComponent:
    """Class to store information about spell components"""
    
    def __init__(self, verbal: bool = False, somatic: bool = False, material: Optional[str] = None,
                 material_cost: Optional[int] = None, material_consumed: bool = False):
        """
        Initialize spell components.
        
        Per D&D 2024 rules, spells may require:
        - Verbal (V): Speaking mystic words
        - Somatic (S): Performing specific gestures
        - Material (M): Specific physical substances or objects, sometimes with a cost
        
        Args:
            verbal: Whether the spell requires verbal components
            somatic: Whether the spell requires somatic components
            material: Description of material components required
            material_cost: Cost of material components in gold pieces
            material_consumed: Whether material components are consumed when cast
        """
        self.verbal = verbal
        self.somatic = somatic
        self.material = material
        self.material_cost = material_cost
        self.material_consumed = material_consumed

class AbstractSpell(ABC):
    """
    Abstract base class for all D&D spells, following the 2024 edition rules.
    
    This class defines the common attributes and interface that all spells
    must implement, whether official D&D spells or custom creations.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the spell's name.
        
        Returns:
            str: Spell name
        """
        pass
    
    @abstractmethod
    def get_level(self) -> SpellLevel:
        """
        Get the spell's level.
        
        Per D&D 2024 rules, spells range from cantrips (level 0) to level 9.
        
        Returns:
            SpellLevel: Spell level
        """
        pass
    
    @abstractmethod
    def get_school(self) -> MagicSchool:
        """
        Get the spell's school of magic.
        
        Returns:
            MagicSchool: School of magic
        """
        pass
    
    @abstractmethod
    def get_casting_time(self) -> Union[CastingTime, str]:
        """
        Get the spell's casting time.
        
        Returns:
            Union[CastingTime, str]: Casting time
        """
        pass
    
    @abstractmethod
    def get_range(self) -> Union[SpellRange, int, str]:
        """
        Get the spell's range.
        
        Returns:
            Union[SpellRange, int, str]: Range of the spell
        """
        pass
    
    @abstractmethod
    def get_components(self) -> SpellComponent:
        """
        Get the spell's components.
        
        Returns:
            SpellComponent: Components required
        """
        pass
    
    @abstractmethod
    def get_duration(self) -> Union[SpellDuration, str]:
        """
        Get the spell's duration.
        
        Returns:
            Union[SpellDuration, str]: Duration of effect
        """
        pass
    
    @abstractmethod
    def requires_concentration(self) -> bool:
        """
        Check if this spell requires concentration.
        
        Per D&D 2024 rules, concentration spells end if:
        - The caster casts another concentration spell
        - The caster takes damage and fails a Constitution saving throw
        - The caster is incapacitated or killed
        
        Returns:
            bool: True if concentration is required
        """
        pass
    
    @abstractmethod
    def can_be_cast_as_ritual(self) -> bool:
        """
        Check if this spell can be cast as a ritual.
        
        Per D&D 2024 rules, ritual casting:
        - Takes 10 minutes longer than normal casting time
        - Does not consume a spell slot
        - Requires the caster to have the Ritual Casting feature
        - The spell must be prepared/known and have the ritual tag
        
        Returns:
            bool: True if it's a ritual spell
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the spell's description.
        
        Returns:
            str: Full spell description
        """
        pass
    
    @abstractmethod
    def get_higher_level_effect(self, cast_level: int) -> Optional[str]:
        """
        Get the enhanced effect when cast at a higher level.
        
        Per D&D 2024 rules, many spells have increased effects when
        cast using higher-level spell slots.
        
        Args:
            cast_level: The level at which the spell is being cast
            
        Returns:
            Optional[str]: Description of the enhanced effect, None if no enhancement
        """
        pass
    
    @abstractmethod
    def get_classes(self) -> List[str]:
        """
        Get classes that can learn/prepare this spell.
        
        Returns:
            List[str]: List of class names
        """
        pass
    
    @abstractmethod
    def get_damage(self) -> Optional[Dict[str, Any]]:
        """
        Get damage information if the spell deals damage.
        
        Returns:
            Optional[Dict[str, Any]]: Damage details or None
        """
        pass
    
    @abstractmethod
    def get_healing(self) -> Optional[Dict[str, Any]]:
        """
        Get healing information if the spell heals.
        
        Returns:
            Optional[Dict[str, Any]]: Healing details or None
        """
        pass
    
    @abstractmethod
    def get_saving_throw(self) -> Optional[Dict[str, str]]:
        """
        Get saving throw information if the spell requires one.
        
        Returns:
            Optional[Dict[str, str]]: Saving throw details or None
        """
        pass
    
    @abstractmethod
    def get_conditions(self) -> List[Dict[str, Any]]:
        """
        Get conditions that the spell can apply.
        
        Returns:
            List[Dict[str, Any]]: List of conditions
        """
        pass
    
    @abstractmethod
    def get_area_of_effect(self) -> Optional[Dict[str, Any]]:
        """
        Get area of effect if the spell affects an area.
        
        Returns:
            Optional[Dict[str, Any]]: Area details or None
        """
        pass
    
    @abstractmethod
    def cast(self, caster: Any, target: Any = None, cast_level: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Cast the spell.
        
        Args:
            caster: The entity casting the spell
            target: The target of the spell (if any)
            cast_level: The level at which to cast the spell (defaults to spell's level)
            **kwargs: Additional spell-specific parameters
            
        Returns:
            Dict[str, Any]: The result of the spell casting
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the spell to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the spell
        """
        pass


class AbstractSpells(ABC):
    """
    Abstract base class for managing spells in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the spell system, including:
    - Retrieving information about spells
    - Filtering spells based on various criteria
    - Managing spell lists for characters
    - Handling spell casting and effects
    """
    
    @abstractmethod
    def get_all_spells(self) -> List[AbstractSpell]:
        """
        Return a list of all available spells.
        
        Returns:
            List[AbstractSpell]: List of all spells
        """
        pass
    
    @abstractmethod
    def get_spell_details(self, spell_name: str) -> Optional[AbstractSpell]:
        """
        Get detailed information about a spell.
        
        Args:
            spell_name: Name of the spell
            
        Returns:
            Optional[AbstractSpell]: The spell object or None if not found
        """
        pass
    
    @abstractmethod
    def get_spells_by_level(self, level: Union[int, SpellLevel]) -> List[AbstractSpell]:
        """
        Get spells of a specific level.
        
        Args:
            level: Spell level to filter by
            
        Returns:
            List[AbstractSpell]: List of spells at that level
        """
        pass
    
    @abstractmethod
    def get_spells_by_class(self, character_class: str) -> List[AbstractSpell]:
        """
        Get spells available to a specific class.
        
        Per D&D 2024 rules, each class has access to a specific list of spells.
        
        Args:
            character_class: Character class name
            
        Returns:
            List[AbstractSpell]: List of spells available to the class
        """
        pass
    
    @abstractmethod
    def get_spells_by_school(self, school: Union[str, MagicSchool]) -> List[AbstractSpell]:
        """
        Get spells from a specific school of magic.
        
        Args:
            school: School of magic to filter by
            
        Returns:
            List[AbstractSpell]: List of spells from that school
        """
        pass
    
    @abstractmethod
    def filter_spells(self, filters: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Filter spells based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[AbstractSpell]: List of filtered spells
        """
        pass
    
    @abstractmethod
    def calculate_spell_save_dc(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell save DC for a character.
        
        Per D&D 2024 rules:
        Spell save DC = 8 + proficiency bonus + spellcasting ability modifier
        
        Args:
            character_data: Character information
            
        Returns:
            int: Calculated spell save DC
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell attack bonus for a character.
        
        Per D&D 2024 rules:
        Spell attack bonus = proficiency bonus + spellcasting ability modifier
        
        Args:
            character_data: Character information
            
        Returns:
            int: Calculated spell attack bonus
        """
        pass
    
    @abstractmethod
    def get_prepared_spells(self, character_data: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Get list of spells a character has prepared.
        
        Per D&D 2024 rules:
        - Prepared casters (like Clerics, Druids) can prepare a number of spells
          equal to their spellcasting ability modifier + their class level
        - Other casters have spells known rather than prepared
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractSpell]: List of prepared spells
        """
        pass
    
    @abstractmethod
    def get_spells_known(self, character_data: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Get list of spells a character knows.
        
        Per D&D 2024 rules:
        - Known casters (like Bards, Sorcerers) know a fixed number of spells
          based on their class and level
        - Prepared casters know all spells on their class list but must prepare a subset
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractSpell]: List of known spells
        """
        pass
    
    @abstractmethod
    def get_available_spell_slots(self, character_data: Dict[str, Any]) -> Dict[int, int]:
        """
        Get available spell slots for a character.
        
        Per D&D 2024 rules, spell slots are determined by:
        - Character's class and level
        - Multiclassing uses a combined formula for determining slots
        - Slots are expended when spells are cast and recovered with rests
        
        Args:
            character_data: Character information
            
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to number of slots
        """
        pass
    
    @abstractmethod
    def use_spell_slot(self, character_data: Dict[str, Any], slot_level: int) -> bool:
        """
        Use a spell slot of the specified level.
        
        Per D&D 2024 rules:
        - A spell slot is expended when a spell is cast
        - A higher-level slot can be used to cast a lower-level spell
        - Cantrips don't use spell slots
        
        Args:
            character_data: Character information
            slot_level: Level of slot to use
            
        Returns:
            bool: True if slot was successfully used
        """
        pass
    
    @abstractmethod
    def create_custom_spell(self, spell_data: Dict[str, Any]) -> AbstractSpell:
        """
        Create a custom spell.
        
        This method supports the creation of unique spells beyond standard D&D rules,
        while ensuring they adhere to the basic spell structure.
        
        Args:
            spell_data: Custom spell definition
            
        Returns:
            AbstractSpell: New custom spell instance
        """
        pass
    
    @abstractmethod
    def validate_spell_creation(self, spell_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom spell definition.
        
        Ensures the spell follows the basic structure required by the system,
        while allowing for creative freedom in effects and mechanics.
        
        Args:
            spell_data: Custom spell definition
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def validate_spell_casting(self, character_data: Dict[str, Any], spell: AbstractSpell, 
                            slot_level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate if a character can cast a specific spell.
        
        Per D&D 2024 rules, casting requirements include:
        - The spell must be known/prepared
        - The character must have an appropriate spell slot available
        - The character must be able to provide the necessary components
        - The character must not be prevented from casting (e.g., silenced for verbal)
        
        Args:
            character_data: Character information
            spell: The spell to cast
            slot_level: Level at which to cast the spell
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        pass
    
    @abstractmethod
    def resolve_spell_effect(self, character_data: Dict[str, Any], spell: AbstractSpell,
                          targets: List[Any], slot_level: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Resolve the effect of a spell.
        
        Per D&D 2024 rules, spell resolution may include:
        - Attack rolls (for spell attacks)
        - Saving throws (for spells requiring saves)
        - Damage or healing calculations
        - Condition or status effects
        - Environmental or terrain effects
        
        Args:
            character_data: Character information
            spell: The spell being cast
            targets: Targets of the spell
            slot_level: Level at which the spell is cast
            **kwargs: Additional spell-specific parameters
            
        Returns:
            Dict[str, Any]: Result of the spell effect
        """
        pass

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

import sys
import json
import os
import random
from typing import Dict, Any, List

# Import character sheet components
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
from character_sheet import CharacterSheet, ProficiencyLevel
from llm_service import LLMService, JSONExtractor

class CharacterCreator:
    """A D&D character creator that uses any LLM service."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the character creator.
        
        Args:
            llm_service: An implementation of LLMService
        """
        self.llm_service = llm_service
        self.character = CharacterSheet()
        self.current_character_json = {}  # Store the current character JSON
        self.is_first_creation = True     # Track if this is the first creation
        self.json_extractor = JSONExtractor()
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service."""
        return self.llm_service.test_connection()
    
    def _generate_character_name(self, species: str) -> str:
        """Generate a character name based on species."""
        name_suggestions = {
            "Elf": ["Aeliana", "Thalion", "Silvyr", "Elenion", "Miriel", "Legolas"],
            "Dwarf": ["Thorin", "Dwalin", "Gimli", "Daina", "Borin", "Nala"],
            "Halfling": ["Bilbo", "Rosie", "Pippin", "Merry", "Frodo", "Samwise"],
            "Human": ["Gareth", "Elena", "Marcus", "Lyanna", "Roderick", "Aria"],
            "Dragonborn": ["Balasar", "Akra", "Torinn", "Sora", "Kriv", "Nala"],
            "Tiefling": ["Akmenios", "Nemeia", "Orianna", "Zevran", "Enna", "Damaia"],
            "Gnome": ["Boddynock", "Dimble", "Glim", "Seebo", "Sindri", "Turen"],
            "Half-Elf": ["Aramil", "Berris", "Dayereth", "Enna", "Galinndan", "Hadarai"],
            "Half-Orc": ["Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"]
        }
        
        names = name_suggestions.get(species, name_suggestions["Human"])
        return random.choice(names)
    
    def validate_character_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize character data to ensure correct types."""
        valid_data = {}
        
        # Basic identity - ensure strings with better name handling
        name = data.get("name", "")
        if not name or name.strip() == "":
            species = str(data.get("species", "Human"))
            valid_data["name"] = self._generate_character_name(species)
        else:
            valid_data["name"] = str(name).strip()
        
        valid_data["species"] = str(data.get("species", "Human"))
        valid_data["background"] = str(data.get("background", "Commoner"))
        
        # Level - ensure integer
        valid_data["level"] = int(data.get("level", 1))
        
        # Classes - ensure dict with string keys and int values
        classes = {}
        for cls, lvl in data.get("classes", {}).items():
            try:
                classes[str(cls)] = int(lvl)
            except (ValueError, TypeError):
                classes[str(cls)] = 1
        if not classes:
            classes["Fighter"] = 1
        valid_data["classes"] = classes
        
        # Subclasses - ensure dict with string keys and values
        subclasses = {}
        for cls, subcls in data.get("subclasses", {}).items():
            subclasses[str(cls)] = str(subcls)
        valid_data["subclasses"] = subclasses
        
        # Alignment - ensure list of strings
        alignment = data.get("alignment", ["Neutral", "Neutral"])
        if isinstance(alignment, list) and len(alignment) >= 2:
            valid_data["alignment"] = [str(alignment[0]), str(alignment[1])]
        else:
            valid_data["alignment"] = ["Neutral", "Neutral"]
        
        # Ability scores - ensure dict with int values
        ability_scores = {}
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            try:
                score = data.get("ability_scores", {}).get(ability, 10)
                ability_scores[ability] = int(score)
            except (ValueError, TypeError):
                ability_scores[ability] = 10
        valid_data["ability_scores"] = ability_scores
        
        # Lists of strings - skills, traits, etc.
        for field in ["skill_proficiencies", "saving_throw_proficiencies", 
                      "personality_traits", "ideals", "bonds", "flaws"]:
            valid_data[field] = [str(item) for item in data.get(field, [])]
        
        # Enhanced armor - support both string and object formats
        armor = data.get("armor", "")
        if isinstance(armor, dict):
            valid_data["armor"] = {
                "name": str(armor.get("name", "")),
                "type": str(armor.get("type", "light")),
                "ac_base": int(armor.get("ac_base", 10)),
                "special_properties": [str(p) for p in armor.get("special_properties", [])],
                "description": str(armor.get("description", ""))
            }
        else:
            valid_data["armor"] = str(armor)
        
        # Enhanced weapons - ensure list of detailed dicts
        weapons = []
        for weapon in data.get("weapons", []):
            if isinstance(weapon, dict):
                weapon_data = {
                    "name": str(weapon.get("name", "Dagger")),
                    "type": str(weapon.get("type", "simple")),
                    "damage": str(weapon.get("damage", "1d4")),
                    "damage_type": str(weapon.get("damage_type", "piercing")),
                    "properties": [str(p) for p in weapon.get("properties", [])],
                    "special_abilities": [str(a) for a in weapon.get("special_abilities", [])],
                    "description": str(weapon.get("description", "")),
                    "magical": bool(weapon.get("magical", False)),
                    "rarity": str(weapon.get("rarity", "common"))
                }
                weapons.append(weapon_data)
            elif isinstance(weapon, str):
                weapons.append({
                    "name": weapon,
                    "type": "simple",
                    "damage": "1d4",
                    "damage_type": "piercing",
                    "properties": [],
                    "special_abilities": [],
                    "description": "",
                    "magical": False,
                    "rarity": "common"
                })
        valid_data["weapons"] = weapons
        
        # Magical items
        magical_items = []
        for item in data.get("magical_items", []):
            if isinstance(item, dict):
                magical_items.append({
                    "name": str(item.get("name", "")),
                    "type": str(item.get("type", "wondrous item")),
                    "rarity": str(item.get("rarity", "common")),
                    "attunement": bool(item.get("attunement", False)),
                    "properties": [str(p) for p in item.get("properties", [])],
                    "description": str(item.get("description", ""))
                })
        valid_data["magical_items"] = magical_items
        
        # Equipment - support both string and object formats
        equipment = []
        for item in data.get("equipment", []):
            if isinstance(item, dict):
                equipment.append({
                    "name": str(item.get("name", "")),
                    "quantity": int(item.get("quantity", 1)),
                    "description": str(item.get("description", ""))
                })
            elif isinstance(item, str):
                equipment.append({
                    "name": item,
                    "quantity": 1,
                    "description": ""
                })
        valid_data["equipment"] = equipment
        
        # Special abilities
        special_abilities = []
        for ability in data.get("special_abilities", []):
            if isinstance(ability, dict):
                special_abilities.append({
                    "name": str(ability.get("name", "")),
                    "type": str(ability.get("type", "extraordinary")),
                    "uses": str(ability.get("uses", "at will")),
                    "description": str(ability.get("description", ""))
                })
        valid_data["special_abilities"] = special_abilities
        
        # Spellcasting information
        if "spellcasting_ability" in data:
            valid_data["spellcasting_ability"] = str(data["spellcasting_ability"])
            valid_data["spell_save_dc"] = int(data.get("spell_save_dc", 10))
            valid_data["spell_attack_bonus"] = int(data.get("spell_attack_bonus", 0))
            
            # Validate spells_known
            spells_known = {}
            for level_str, spells in data.get("spells_known", {}).items():
                try:
                    level = int(level_str)
                    spells_known[str(level)] = [str(spell) for spell in spells]
                except (ValueError, TypeError):
                    pass
            valid_data["spells_known"] = spells_known
            
            # Validate spell_slots
            spell_slots = {}
            for level_str, slots in data.get("spell_slots", {}).items():
                try:
                    level = int(level_str)
                    spell_slots[str(level)] = int(slots)
                except (ValueError, TypeError):
                    pass
            valid_data["spell_slots"] = spell_slots
        
        # Enhanced backstory and personality
        valid_data["backstory"] = str(data.get("backstory", ""))
        
        personality_details = data.get("personality_details", {})
        if isinstance(personality_details, dict):
            valid_data["personality_details"] = {
                "mannerisms": [str(m) for m in personality_details.get("mannerisms", [])],
                "interaction_traits": [str(t) for t in personality_details.get("interaction_traits", [])],
                "appearance": str(personality_details.get("appearance", "")),
                "voice_and_speech": str(personality_details.get("voice_and_speech", ""))
            }
        
        return valid_data
    
    def populate_character(self, character_data: Dict[str, Any]) -> None:
        """Populate character sheet with data from the validated JSON."""
        try:
            # Reset character to avoid conflicts
            self.character = CharacterSheet()
            
            # Basic identity
            if "name" in character_data:
                self.character.set_name(character_data["name"])
            
            if "species" in character_data:
                self.character.set_species(character_data["species"])
            
            # Classes and levels
            for class_name, level in character_data.get("classes", {}).items():
                self.character.set_class_level(class_name, level)
                
                # Set subclass if provided
                subclasses = character_data.get("subclasses", {})
                if subclasses and class_name in subclasses:
                    self.character.set_subclass(class_name, subclasses[class_name])
            
            # Background and alignment
            if "background" in character_data:
                self.character.set_background(character_data["background"])
            
            if "alignment" in character_data and len(character_data["alignment"]) == 2:
                self.character.set_alignment(character_data["alignment"][0], character_data["alignment"][1])
            
            # Ability scores
            for ability, score in character_data.get("ability_scores", {}).items():
                self.character.set_base_ability_score(ability, int(score))
            
            # Proficiencies
            for skill in character_data.get("skill_proficiencies", []):
                self.character.set_skill_proficiency(skill, ProficiencyLevel.PROFICIENT)
            
            for ability in character_data.get("saving_throw_proficiencies", []):
                self.character.set_saving_throw_proficiency(ability, ProficiencyLevel.PROFICIENT)
            
            # Equipment
            armor = character_data.get("armor", {})
            if isinstance(armor, dict) and armor.get("name"):
                self.character.equip_armor(armor["name"])
            elif isinstance(armor, str) and armor:
                self.character.equip_armor(armor)
            
            if character_data.get("shield", False):
                self.character.equip_shield()
            
            for weapon in character_data.get("weapons", []):
                self.character.add_weapon(weapon)
            
            for item in character_data.get("equipment", []):
                self.character.add_equipment(item)
            
            # Spellcasting
            if "spellcasting_ability" in character_data:
                self.character.set_spellcasting_ability(character_data["spellcasting_ability"])
                
                for level_str, spells in character_data.get("spells_known", {}).items():
                    level = int(level_str)
                    for spell in spells:
                        self.character.add_spell_known(level, spell)
            
            # Personality
            for trait in character_data.get("personality_traits", []):
                self.character.add_personality_trait(trait)
            
            for ideal in character_data.get("ideals", []):
                self.character.add_ideal(ideal)
            
            for bond in character_data.get("bonds", []):
                self.character.add_bond(bond)
            
            for flaw in character_data.get("flaws", []):
                self.character.add_flaw(flaw)
            
            # Backstory
            if "backstory" in character_data:
                self.character.set_backstory(character_data["backstory"])
                
            # Calculate all derived stats
            self.character.calculate_all_derived_stats()
            
        except Exception as e:
            print(f"Error populating character sheet: {e}")
    
    def create_character(self, description: str, level: int = 1) -> Dict[str, Any]:
        """Create a character based on a description and specified level."""
        prompt = f"""
        Create a level {level} D&D character based on this description: {description}
        
        IMPORTANT REQUIREMENTS:
        - Character level must be {level}
        - Generate an appropriate fantasy name for this character
        - Create specialized equipment that fits the character concept and level
        - If this is a unique concept (like Jedi), create appropriate special abilities and equipment
        - Scale ability scores, equipment, and spells to level {level}
        - Write a detailed, immersive backstory (minimum 3-4 paragraphs)
        - Include specialized weapons, armor, and magical items as appropriate
        - Respond with a complete character in valid JSON format following the schema
        - Make sure to include ALL required fields including "name" and "level"
        
        For level {level} characters:
        - Ability scores should reflect experience and training
        - Equipment should be of appropriate quality and magical enhancement
        - Spellcasters should have access to spells up to their maximum spell level
        - Include class features and abilities appropriate to this level
        """
        
        response = self.llm_service.generate(prompt)
        
        # Extract and validate JSON
        character_data = self.json_extractor.extract_json(response)
        
        # If extraction failed, provide level-appropriate fallback data
        if not character_data:
            print("Could not extract proper JSON. Using fallback character template.")
            character_data = self._get_fallback_character(description, level)
        
        # Ensure level is set correctly
        character_data["level"] = level
        
        # Ensure name is populated
        if not character_data.get("name") or character_data.get("name") == "":
            species = character_data.get("species", "Human")
            character_data["name"] = self._generate_character_name(species)
        
        # Validate data to ensure proper types
        validated_data = self.validate_character_json(character_data)
        
        # Store this as our current character JSON for future iterations
        self.current_character_json = validated_data.copy()
        self.is_first_creation = False
        
        # Populate the character sheet
        self.populate_character(validated_data)
        
        # Get final character summary
        return self.character.get_character_summary()
    
    def refine_character(self, feedback: str) -> Dict[str, Any]:
        """Refine the character based on feedback, using the previous character as base."""
        
        # Use the stored JSON instead of character summary for more accurate iteration
        if self.current_character_json:
            current_char_json = json.dumps(self.current_character_json, indent=2)
        else:
            # Fallback to character summary if JSON not available
            current_char_json = json.dumps(self.character.get_character_summary(), indent=2)
        
        prompt = f"""
        Current character JSON: 
        {current_char_json}
        
        User feedback: {feedback}
        
        IMPORTANT:
        - Modify the existing character based on the feedback
        - Keep all existing fields unless specifically changing them
        - Maintain the character's name unless asked to change it
        - Return the COMPLETE updated character JSON, not just the changes
        - Ensure all required fields are present in your response
        
        Provide the updated character in valid JSON format exactly matching the schema.
        """
        
        # Get LLM response
        response = self.llm_service.generate(prompt)
        
        # Extract and validate JSON
        updated_character = self.json_extractor.extract_json(response)
        
        if not updated_character:
            print("Failed to extract changes. Trying a simplified prompt...")
            
            # Try a simpler prompt that explicitly asks for complete character
            simple_prompt = f"""
            Take this character: {current_char_json}
            
            Apply this change: {feedback}
            
            Return the complete updated character as valid JSON.
            """
            response = self.llm_service.generate(simple_prompt)
            updated_character = self.json_extractor.extract_json(response)
        
        # If still no valid JSON, merge feedback manually with current character
        if not updated_character:
            print("LLM failed to provide valid JSON. Applying minimal changes...")
            updated_character = self.current_character_json.copy()
            
            # Try to parse feedback for simple changes
            if "name" in feedback.lower():
                # Extract potential name from feedback
                words = feedback.split()
                for i, word in enumerate(words):
                    if word.lower() in ["name", "called", "named"] and i + 1 < len(words):
                        updated_character["name"] = words[i + 1].strip(".,!?")
                        break
        
        # Validate data
        validated_changes = self.validate_character_json(updated_character)
        
        # Update our stored character JSON
        self.current_character_json = validated_changes.copy()
        
        # Apply changes to character sheet
        self.populate_character(validated_changes)
        
        return self.character.get_character_summary()
    
    def _get_fallback_character(self, description: str = "", level: int = 1) -> Dict[str, Any]:
        """Generate a level-appropriate fallback character."""
        # Scale ability scores based on level
        base_scores = {
            "strength": 14, "dexterity": 12, "constitution": 13, 
            "intelligence": 10, "wisdom": 11, "charisma": 10
        }
        
        # Add ability score improvements for higher levels
        improvements = (level - 1) // 4 * 2  # ASI every 4 levels
        base_scores["strength"] += improvements
        
        return {
            "name": "Adventurer",
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Soldier",
            "alignment": ["Neutral", "Good"],
            "ability_scores": base_scores,
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "saving_throw_proficiencies": ["Strength", "Constitution"],
            "personality_traits": ["I face problems head-on", "I have a strong sense of duty"],
            "ideals": ["Honor", "Protection of the innocent"],
            "bonds": ["My fellow soldiers are my family"],
            "flaws": ["I have trouble trusting new allies"],
            "armor": {
                "name": "Plate Armor" if level >= 5 else "Chain Mail",
                "type": "heavy" if level >= 5 else "medium",
                "ac_base": 18 if level >= 5 else 16,
                "special_properties": ["Masterwork craftsmanship"] if level >= 10 else [],
                "description": f"Well-crafted armor befitting a level {level} warrior"
            },
            "weapons": [{
                "name": f"{'Magical ' if level >= 5 else ''}Longsword",
                "type": "martial",
                "damage": "1d8 + 1" if level >= 5 else "1d8",
                "damage_type": "slashing",
                "properties": ["versatile"],
                "special_abilities": ["Enhanced Strike"] if level >= 5 else [],
                "description": f"A {('magical ' if level >= 5 else '')}longsword wielded with skill",
                "magical": level >= 5,
                "rarity": "uncommon" if level >= 5 else "common"
            }],
            "equipment": [
                {"name": "Explorer's Pack", "quantity": 1, "description": "Standard adventuring gear"},
                {"name": "Shield", "quantity": 1, "description": "Steel shield"}
            ],
            "backstory": f"A veteran soldier with {level} levels of experience, having served in numerous campaigns and earned recognition for bravery and tactical skill. Through years of combat and training, they have honed their abilities to a fine edge.",
            "personality_details": {
                "mannerisms": ["Stands at attention when addressed", "Checks weapons before battle"],
                "interaction_traits": ["Direct and honest", "Protective of allies"],
                "appearance": f"Battle-scarred warrior in well-maintained gear",
                "voice_and_speech": "Speaks with military precision and authority"
            }
        }

import sys
import json
import os
import random
from typing import Dict, Any, List

# Import character sheet components
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
from character_sheet import CharacterSheet, ProficiencyLevel
from llm_service import LLMService, JSONExtractor
from abstract_multiclass_and_level_up import AbstractMulticlassAndLevelUp


class CharacterCreator:
    """A D&D character creator that uses any LLM service with full level progression."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the character creator.
        
        Args:
            llm_service: An implementation of LLMService
        """
        self.llm_service = llm_service
        self.character = CharacterSheet()
        self.current_character_json = {}
        self.character_progression = {}  # Store full level 1-20 progression
        self.is_first_creation = True
        self.json_extractor = JSONExtractor()
        self.level_up_rules = AbstractMulticlassAndLevelUp()
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service."""
        return self.llm_service.test_connection()
    
    def create_character_progression(self, description: str, target_level: int = 20) -> Dict[str, Dict[str, Any]]:
        """
        Create a complete character progression from level 1 to target_level.
        
        Args:
            description: Character concept description
            target_level: Maximum level to create (default 20)
        
        Returns:
            Dictionary with keys like 'level_1', 'level_2', etc.
        """
        print(f"Creating character progression from level 1 to {target_level}...")
        
        # Step 1: Create the base level 1 character
        level_1_character = self._create_base_character(description)
        self.character_progression = {"level_1": level_1_character}
        
        # Step 2: Create progression for each subsequent level
        for level in range(2, target_level + 1):
            print(f"  Generating level {level}...")
            level_character = self._create_level_up_character(level, description)
            self.character_progression[f"level_{level}"] = level_character
        
        # Step 3: Save progression to file
        self._save_character_progression(description)
        
        print(f"✅ Complete character progression created (levels 1-{target_level})")
        return self.character_progression
    
    def _create_base_character(self, description: str) -> Dict[str, Any]:
        """Create the base level 1 character."""
        prompt = f"""
        Create a level 1 D&D character based on this description: {description}
        
        This is the foundation character that will grow from level 1 to 20. Consider:
        - What class(es) would best represent this concept?
        - What would their early backstory be as a beginning adventurer?
        - What basic equipment would they start with?
        - What are their core personality traits that will evolve over time?
        
        IMPORTANT REQUIREMENTS:
        - Character level must be 1
        - Generate an appropriate fantasy name
        - Create a backstory that shows their humble beginnings
        - Include basic starting equipment appropriate for level 1
        - Consider multiclass potential for future growth
        - Respond with complete character in valid JSON format
        """
        
        response = self.llm_service.generate(prompt)
        character_data = self.json_extractor.extract_json(response)
        
        if not character_data:
            character_data = self._get_fallback_character(description, 1)
        
        character_data["level"] = 1
        validated_data = self.validate_character_json(character_data)
        
        # Store as current character for reference
        self.current_character_json = validated_data.copy()
        
        return validated_data
    
    def _create_level_up_character(self, level: int, original_description: str) -> Dict[str, Any]:
        """Create a character at a specific level based on progression rules."""
        previous_level = level - 1
        previous_character = self.character_progression[f"level_{previous_level}"]
        
        # Apply level-up rules using the abstract class
        level_up_changes = self.level_up_rules.calculate_level_up_changes(
            previous_character, level
        )
        
        # Generate narrative progression
        prompt = f"""
        Level up this D&D character from level {previous_level} to level {level}.
        
        Original concept: {original_description}
        
        Previous character state:
        {json.dumps(previous_character, indent=2)}
        
        Level {level} changes to apply:
        {json.dumps(level_up_changes, indent=2)}
        
        IMPORTANT REQUIREMENTS:
        - Maintain character continuity and core identity
        - Apply the mechanical changes provided
        - Evolve the backstory to reflect growth and new experiences
        - Add new equipment/abilities appropriate for level {level}
        - Show character development and maturation
        - Update personality to reflect experiences gained
        - Consider multiclass progression if appropriate
        
        For level {level} specifically:
        - Update ability scores with any ASI/feat improvements
        - Add new class features and abilities
        - Upgrade equipment quality and magical enhancement
        - Expand spell repertoire if applicable
        - Develop relationships and reputation in the world
        
        Return the COMPLETE level {level} character in valid JSON format.
        """
        
        response = self.llm_service.generate(prompt)
        character_data = self.json_extractor.extract_json(response)
        
        if not character_data:
            print(f"LLM failed for level {level}, applying mechanical changes only...")
            character_data = self._apply_mechanical_level_up(previous_character, level_up_changes, level)
        
        # Ensure level is correct
        character_data["level"] = level
        
        # Apply mechanical changes from the abstract class
        character_data = self._merge_level_up_changes(character_data, level_up_changes)
        
        validated_data = self.validate_character_json(character_data)
        return validated_data
    
    def _apply_mechanical_level_up(self, previous_char: Dict[str, Any], changes: Dict[str, Any], level: int) -> Dict[str, Any]:
        """Apply mechanical level-up changes when LLM fails."""
        character_data = previous_char.copy()
        character_data["level"] = level
        
        # Apply ability score improvements
        if "ability_score_improvements" in changes:
            for ability, improvement in changes["ability_score_improvements"].items():
                current_score = character_data.get("ability_scores", {}).get(ability, 10)
                character_data.setdefault("ability_scores", {})[ability] = current_score + improvement
        
        # Apply new class levels
        if "class_levels" in changes:
            for class_name, new_level in changes["class_levels"].items():
                character_data.setdefault("classes", {})[class_name] = new_level
        
        # Add new proficiencies
        if "new_proficiencies" in changes:
            character_data.setdefault("skill_proficiencies", []).extend(changes["new_proficiencies"])
        
        # Add new spells
        if "new_spells" in changes:
            for spell_level, spells in changes["new_spells"].items():
                character_data.setdefault("spells_known", {}).setdefault(spell_level, []).extend(spells)
        
        # Update backstory with generic progression
        character_data["backstory"] += f"\n\nAt level {level}, the character has gained significant experience and continues to grow in power and wisdom."
        
        return character_data
    
    def _merge_level_up_changes(self, character_data: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Merge mechanical changes with LLM-generated character data."""
        # Ensure core mechanical changes are applied correctly
        if "class_levels" in changes:
            for class_name, new_level in changes["class_levels"].items():
                character_data.setdefault("classes", {})[class_name] = new_level
        
        if "ability_score_improvements" in changes:
            for ability, improvement in changes["ability_score_improvements"].items():
                current_score = character_data.get("ability_scores", {}).get(ability, 10)
                # Only apply if the LLM didn't already account for it
                if current_score < 20:  # Cap at 20
                    character_data.setdefault("ability_scores", {})[ability] = min(20, current_score + improvement)
        
        if "proficiency_bonus" in changes:
            character_data["proficiency_bonus"] = changes["proficiency_bonus"]
        
        if "hit_points" in changes:
            character_data["hit_points"] = changes["hit_points"]
        
        return character_data
    
    def _save_character_progression(self, description: str) -> None:
        """Save the character progression to JSON files."""
        # Create save directory
        save_dir = os.path.join(os.path.dirname(__file__), 'character_progressions')
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename from character name and description
        char_name = self.character_progression["level_1"].get("name", "unnamed_character")
        safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
        
        # Save complete progression
        progression_file = os.path.join(save_dir, f"{safe_name}_progression.json")
        with open(progression_file, 'w') as f:
            json.dump(self.character_progression, f, indent=2)
        
        # Save individual level files
        level_dir = os.path.join(save_dir, safe_name)
        os.makedirs(level_dir, exist_ok=True)
        
        for level_key, character_data in self.character_progression.items():
            level_file = os.path.join(level_dir, f"{level_key}.json")
            with open(level_file, 'w') as f:
                json.dump(character_data, f, indent=2)
        
        print(f"Character progression saved to: {progression_file}")
        print(f"Individual levels saved to: {level_dir}/")
    
    def get_character_at_level(self, level: int) -> Dict[str, Any]:
        """Get character data at a specific level."""
        level_key = f"level_{level}"
        if level_key in self.character_progression:
            return self.character_progression[level_key]
        else:
            raise ValueError(f"Level {level} not found in character progression")
    
    def preview_progression_summary(self) -> str:
        """Generate a summary of the character's progression."""
        if not self.character_progression:
            return "No character progression available."
        
        summary = []
        char_name = self.character_progression["level_1"].get("name", "Unknown")
        summary.append(f"=== {char_name}'s Character Progression ===\n")
        
        for level in range(1, len(self.character_progression) + 1):
            level_key = f"level_{level}"
            if level_key in self.character_progression:
                char_data = self.character_progression[level_key]
                
                # Extract key info
                classes = char_data.get("classes", {})
                class_summary = ", ".join([f"{cls} {lvl}" for cls, lvl in classes.items()])
                
                abilities = char_data.get("ability_scores", {})
                highest_ability = max(abilities.items(), key=lambda x: x[1]) if abilities else ("Unknown", 0)
                
                summary.append(f"Level {level}: {class_summary}")
                summary.append(f"  Highest Ability: {highest_ability[0].title()} ({highest_ability[1]})")
                
                # Show major features at key levels
                if level in [1, 3, 5, 11, 17, 20]:
                    weapons = char_data.get("weapons", [])
                    if weapons:
                        best_weapon = weapons[0].get("name", "None") if isinstance(weapons[0], dict) else weapons[0]
                        summary.append(f"  Primary Weapon: {best_weapon}")
                    
                    magical_items = char_data.get("magical_items", [])
                    if magical_items:
                        item_count = len(magical_items)
                        summary.append(f"  Magical Items: {item_count}")
                
                summary.append("")
        
        return "\n".join(summary)
    
    # Keep existing methods for backward compatibility
    def create_character(self, description: str, level: int = 1) -> Dict[str, Any]:
        """Create a character at a specific level (backward compatibility)."""
        if level == 1:
            # Create just level 1
            character_data = self._create_base_character(description)
            self.populate_character(character_data)
            return self.character.get_character_summary()
        else:
            # Create progression up to target level and return that level
            self.create_character_progression(description, level)
            target_character = self.get_character_at_level(level)
            self.populate_character(target_character)
            return self.character.get_character_summary()
    
    # ... (keep all existing validation and utility methods from previous version) ...
    
    def validate_character_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize character data to ensure correct types."""
        # ... (keep existing validation logic) ...
        valid_data = {}
        
        # Basic identity - ensure strings with better name handling
        name = data.get("name", "")
        if not name or name.strip() == "":
            species = str(data.get("species", "Human"))
            valid_data["name"] = self._generate_character_name(species)
        else:
            valid_data["name"] = str(name).strip()
        
        valid_data["species"] = str(data.get("species", "Human"))
        valid_data["background"] = str(data.get("background", "Commoner"))
        valid_data["level"] = int(data.get("level", 1))
        
        # Classes
        classes = {}
        for cls, lvl in data.get("classes", {}).items():
            try:
                classes[str(cls)] = int(lvl)
            except (ValueError, TypeError):
                classes[str(cls)] = 1
        if not classes:
            classes["Fighter"] = 1
        valid_data["classes"] = classes
        
        # Continue with rest of validation...
        # (Include all the validation logic from the previous version)
        
        return valid_data
    
    def _generate_character_name(self, species: str) -> str:
        """Generate a character name based on species."""
        name_suggestions = {
            "Elf": ["Aeliana", "Thalion", "Silvyr", "Elenion", "Miriel", "Legolas"],
            "Dwarf": ["Thorin", "Dwalin", "Gimli", "Daina", "Borin", "Nala"],
            "Halfling": ["Bilbo", "Rosie", "Pippin", "Merry", "Frodo", "Samwise"],
            "Human": ["Gareth", "Elena", "Marcus", "Lyanna", "Roderick", "Aria"],
            "Dragonborn": ["Balasar", "Akra", "Torinn", "Sora", "Kriv", "Nala"],
            "Tiefling": ["Akmenios", "Nemeia", "Orianna", "Zevran", "Enna", "Damaia"],
            "Gnome": ["Boddynock", "Dimble", "Glim", "Seebo", "Sindri", "Turen"],
            "Half-Elf": ["Aramil", "Berris", "Dayereth", "Enna", "Galinndan", "Hadarai"],
            "Half-Orc": ["Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"]
        }
        
        names = name_suggestions.get(species, name_suggestions["Human"])
        return random.choice(names)
    
    def populate_character(self, character_data: Dict[str, Any]) -> None:
        """Populate character sheet with data from the validated JSON."""
        # ... (keep existing populate logic) ...
        pass
    
    def _get_fallback_character(self, description: str = "", level: int = 1) -> Dict[str, Any]:
        """Generate a level-appropriate fallback character."""
        # ... (keep existing fallback logic) ...
        pass

    # In character_creator.py, modify the finalize_character method:
    def finalize_character(self, character_id: str, additional_details: Dict[str, Any] = None) -> Dict[str, Any]:
        character = self.active_characters.get(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Existing validation using CharacterValidator
        validation_result = self.validator.validate_full_character(character)
        
        # Add comprehensive rules validation using CreateRules
        from backend4.create_rules import CreateRules
        # Convert character dict to CharacterSheet object first, then validate
        # rules_validation = CreateRules.validate_entire_character_sheet(character_sheet)
        
        # Combine validation results
        character["validation_result"] = validation_result
        # character["rules_validation"] = rules_validation
        
        # use /backend4/unified_validator.py for unified validation

from typing import Dict, Any, Optional
import logging

from character_core import CharacterCore
from character_state import CharacterState
from character_stats import CharacterStats

logger = logging.getLogger(__name__)

class CharacterSheet:
    """
    Main character sheet class that orchestrates the three sub-components:
    - CharacterCore: Core character build data
    - CharacterState: Current gameplay state
    - CharacterStats: Calculated/derived statistics
    """
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
        
        # Validation tracking
        self._last_validation_result: Optional[Dict[str, Any]] = None
        self._validation_timestamp: Optional[str] = None
    
    def validate_against_rules(self, use_unified: bool = True) -> Dict[str, Any]:
        """Validate entire character sheet against D&D rules."""
        try:
            if use_unified:
                from unified_validator import create_unified_validator
                validator = create_unified_validator()
                character_data = self.to_dict()
                result = validator.validate_character(character_data, self)
            else:
                # Fallback validation
                core_validation = self.core.validate()
                result = {
                    "overall_valid": core_validation["valid"],
                    "summary": {
                        "total_issues": len(core_validation["issues"]),
                        "total_warnings": len(core_validation["warnings"]),
                        "validators_run": 1,
                        "validators_passed": 1 if core_validation["valid"] else 0
                    },
                    "all_issues": core_validation["issues"],
                    "all_warnings": core_validation["warnings"],
                    "detailed_results": {"core": core_validation}
                }
            
            self._last_validation_result = result
            return result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "overall_valid": False,
                "summary": {"total_issues": 1, "validators_run": 0, "validators_passed": 0},
                "all_issues": [f"Validation error: {str(e)}"],
                "all_warnings": [],
                "detailed_results": {}
            }
    
    def calculate_all_derived_stats(self) -> None:
        """Trigger recalculation of all derived statistics."""
        self.stats.invalidate_cache()
        # Accessing properties will trigger recalculation
        _ = self.stats.proficiency_bonus
        _ = self.stats.armor_class
        _ = self.stats.max_hit_points
        _ = self.stats.initiative
    
    # Convenience properties that delegate to appropriate sub-components
    @property
    def name(self) -> str:
        return self.core.name
    
    @property
    def total_level(self) -> int:
        return self.core.total_level
    
    @property
    def armor_class(self) -> int:
        return self.stats.armor_class
    
    @property
    def current_hit_points(self) -> int:
        return self.state.current_hit_points
    
    @property
    def max_hit_points(self) -> int:
        return self.stats.max_hit_points
    
    # Convenience methods for common operations
    def level_up(self, class_name: str) -> None:
        """Level up in the specified class."""
        current_level = self.core.character_classes.get(class_name, 0)
        self.core.character_classes[class_name] = current_level + 1
        self.calculate_all_derived_stats()
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = self.state.take_damage(damage)
        # Check if character died
        if self.state.current_hit_points == 0:
            # Handle death/unconsciousness
            self.state.add_condition("unconscious")
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character."""
        old_hp = self.state.current_hit_points
        self.state.current_hit_points = min(self.stats.max_hit_points, old_hp + healing)
        healed = self.state.current_hit_points - old_hp
        
        # Remove unconscious condition if healed above 0
        if self.state.current_hit_points > 0 and "unconscious" in self.state.active_conditions:
            self.state.remove_condition("unconscious")
        
        return healed
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Create a comprehensive character summary."""
        return {
            # Core identity
            "name": self.core.name,
            "species": self.core.species,
            "level": self.core.total_level,
            "classes": self.core.character_classes,
            "background": self.core.background,
            
            # Ability scores
            "ability_scores": {
                "strength": self.core.strength.total_score,
                "dexterity": self.core.dexterity.total_score,
                "constitution": self.core.constitution.total_score,
                "intelligence": self.core.intelligence.total_score,
                "wisdom": self.core.wisdom.total_score,
                "charisma": self.core.charisma.total_score
            },
            
            # Combat stats
            "armor_class": self.stats.armor_class,
            "hit_points": {
                "current": self.state.current_hit_points,
                "max": self.stats.max_hit_points,
                "temp": self.state.temporary_hit_points
            },
            "initiative": self.stats.initiative,
            "proficiency_bonus": self.stats.proficiency_bonus,
            
            # Current state
            "conditions": list(self.state.active_conditions.keys()),
            "exhaustion_level": self.state.exhaustion_level,
            
            # Equipment
            "armor": self.state.armor,
            "shield": self.state.shield,
            "weapons": self.state.weapons,
            
            # Validation
            "is_valid": self._last_validation_result.get("overall_valid", False) if self._last_validation_result else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire character sheet to dictionary."""
        return {
            "core": self.core.to_dict(),
            "state": self.state.to_dict(),
            "stats": self.stats.to_dict(),
            "validation": self._last_validation_result
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load character sheet from dictionary."""
        if "core" in data:
            # Load core data
            core_data = data["core"]
            self.core.name = core_data.get("name", "")
            self.core.species = core_data.get("species", "")
            # ... load other core data
        
        if "state" in data:
            # Load state data
            state_data = data["state"]
            self.state.current_hit_points = state_data.get("hit_points", {}).get("current", 0)
            # ... load other state data
        
        # Recalculate stats after loading
        self.calculate_all_derived_stats()

from typing import Dict, List, Optional, Any
from datetime import datetime

class CharacterState:
    """
    IN-GAME INDEPENDENT VARIABLES - Updated during gameplay.
    
    These variables track the character's current state and resources,
    changing frequently during gameplay sessions.
    """
    
    def __init__(self):
        # Experience Points
        self.experience_points: int = 0
        
        # Hit Points - Current Values
        self.current_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_point_maximum_modifier: int = 0
        
        # Hit Dice - Current Values
        self.hit_dice_remaining: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Spell Slots - Current Values
        self.spell_slots_total: Dict[int, int] = {}     # {1: 4, 2: 3, 3: 2}
        self.spell_slots_remaining: Dict[int, int] = {}  # {1: 2, 2: 1, 3: 0}
        self.spells_known: Dict[int, List[str]] = {}    # {0: ["Fire Bolt"], 1: ["Magic Missile"]}
        self.spells_prepared: List[str] = []
        self.ritual_book_spells: List[str] = []
        
        # Equipment - Current Items
        self.armor: Optional[str] = None
        self.shield: bool = False
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.magical_items: List[Dict[str, Any]] = []
        self.attuned_items: List[str] = []
        self.max_attunement_slots: int = 3
        
        # Currency
        self.currency: Dict[str, int] = {
            "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
        }
        
        # Conditions and Effects
        self.active_conditions: Dict[str, Dict[str, Any]] = {}
        self.exhaustion_level: int = 0
        
        # Temporary Defenses
        self.temp_damage_resistances: Set[str] = set()
        self.temp_damage_immunities: Set[str] = set()
        self.temp_damage_vulnerabilities: Set[str] = set()
        self.temp_condition_immunities: Set[str] = set()
        
        # Action Economy - Current State
        self.actions_per_turn: int = 1
        self.bonus_actions_per_turn: int = 1
        self.reactions_per_turn: int = 1
        self.actions_used: int = 0
        self.bonus_actions_used: int = 0
        self.reactions_used: int = 0
        
        # Companion Creatures
        self.beast_companion: Optional[Dict[str, Any]] = None
        
        # Adventure Notes
        self.notes: Dict[str, str] = {
            'organizations': "", 'allies': "", 'enemies': "", 'backstory': "", 'other': ""
        }
        
        # Timestamps
        self.last_updated: str = ""
        self.last_long_rest: Optional[str] = None
        self.last_short_rest: Optional[str] = None
    
    def reset_action_economy(self) -> None:
        """Reset action economy for a new turn."""
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.reactions_used = 0
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = {"temp_hp_damage": 0, "hp_damage": 0, "overkill": 0}
        
        # Apply to temporary HP first
        if self.temporary_hit_points > 0:
            temp_damage = min(damage, self.temporary_hit_points)
            self.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then to regular HP
        if damage > 0:
            self.current_hit_points -= damage
            result["hp_damage"] = damage
            
            if self.current_hit_points < 0:
                result["overkill"] = abs(self.current_hit_points)
                self.current_hit_points = 0
        
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character and return amount healed."""
        # Note: This needs max_hit_points from CharacterStats
        # Will be handled by the main CharacterSheet class
        pass
    
    def use_spell_slot(self, level: int) -> bool:
        """Use a spell slot of the specified level."""
        if level not in self.spell_slots_remaining or self.spell_slots_remaining[level] <= 0:
            return False
        
        self.spell_slots_remaining[level] -= 1
        return True
    
    def add_condition(self, condition: str, duration: Optional[int] = None, 
                     source: Optional[str] = None) -> None:
        """Apply a condition to the character."""
        self.active_conditions[condition] = {
            "duration": duration,
            "source": source,
            "applied_at": datetime.now().isoformat()
        }
    
    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the character."""
        if condition in self.active_conditions:
            del self.active_conditions[condition]
            return True
        return False
    
    def take_short_rest(self, hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Perform a short rest."""
        result = {"hp_recovered": 0, "hit_dice_spent": {}}
        
        if hit_dice_spent:
            # Process hit dice healing
            for die_type, count in hit_dice_spent.items():
                available = self.hit_dice_remaining.get(die_type, 0)
                if available >= count:
                    self.hit_dice_remaining[die_type] = available - count
                    result["hit_dice_spent"][die_type] = count
                    # HP recovery calculation would need CharacterStats
        
        self.last_short_rest = datetime.now().isoformat()
        return result
    
    def take_long_rest(self) -> Dict[str, Any]:
        """Perform a long rest."""
        result = {"hp_recovered": 0, "spell_slots_recovered": {}, "hit_dice_recovered": {}}
        
        # Restore spell slots
        for level, total in self.spell_slots_total.items():
            old_slots = self.spell_slots_remaining.get(level, 0)
            self.spell_slots_remaining[level] = total
            result["spell_slots_recovered"][level] = total - old_slots
        
        # Reduce exhaustion by 1
        if self.exhaustion_level > 0:
            self.exhaustion_level -= 1
        
        self.last_long_rest = datetime.now().isoformat()
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_points": self.experience_points,
            "hit_points": {
                "current": self.current_hit_points,
                "temporary": self.temporary_hit_points,
                "max_modifier": self.hit_point_maximum_modifier
            },
            "spell_slots": {
                "total": self.spell_slots_total,
                "remaining": self.spell_slots_remaining
            },
            "spells": {
                "known": self.spells_known,
                "prepared": self.spells_prepared,
                "ritual_book": self.ritual_book_spells
            },
            "equipment": {
                "armor": self.armor,
                "shield": self.shield,
                "weapons": self.weapons,
                "items": self.equipment,
                "magical_items": self.magical_items,
                "attuned": self.attuned_items
            },
            "currency": self.currency,
            "conditions": {
                "active": self.active_conditions,
                "exhaustion": self.exhaustion_level
            },
            "action_economy": {
                "actions_used": self.actions_used,
                "bonus_actions_used": self.bonus_actions_used,
                "reactions_used": self.reactions_used
            },
            "notes": self.notes,
            "timestamps": {
                "last_updated": self.last_updated,
                "last_long_rest": self.last_long_rest,
                "last_short_rest": self.last_short_rest
            }
        }

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CharacterStats:
    """
    DEPENDENT VARIABLES - Calculated from other variables.
    
    These variables are computed based on core character data and current state.
    They should be recalculated whenever their dependencies change.
    """
    
    def __init__(self, core: 'CharacterCore', state: 'CharacterState'):
        self.core = core
        self.state = state
        
        # Cached calculated values
        self._proficiency_bonus: Optional[int] = None
        self._armor_class: Optional[int] = None
        self._max_hit_points: Optional[int] = None
        self._initiative: Optional[int] = None
        self._spell_save_dc: Optional[int] = None
        self._spell_attack_bonus: Optional[int] = None
        self._passive_perception: Optional[int] = None
        self._passive_investigation: Optional[int] = None
        self._passive_insight: Optional[int] = None
        
        # Available actions (computed based on class features, etc.)
        self._available_actions: Dict[str, Dict[str, Any]] = {}
        self._available_reactions: Dict[str, Dict[str, Any]] = {}
        
        # Dependencies tracking for cache invalidation
        self._last_core_hash: Optional[int] = None
        self._last_state_hash: Optional[int] = None
    
    def invalidate_cache(self) -> None:
        """Invalidate all cached calculations."""
        self._proficiency_bonus = None
        self._armor_class = None
        self._max_hit_points = None
        self._initiative = None
        self._spell_save_dc = None
        self._spell_attack_bonus = None
        self._passive_perception = None
        self._passive_investigation = None
        self._passive_insight = None
        self._available_actions = {}
        self._available_reactions = {}
    
    def _needs_recalculation(self) -> bool:
        """Check if recalculation is needed based on dependencies."""
        # Simple hash-based dependency tracking
        core_hash = hash(str(self.core.to_dict()))
        state_hash = hash(str(self.state.to_dict()))
        
        if (self._last_core_hash != core_hash or 
            self._last_state_hash != state_hash):
            self._last_core_hash = core_hash
            self._last_state_hash = state_hash
            return True
        return False
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        if self._proficiency_bonus is None or self._needs_recalculation():
            level = self.core.total_level
            self._proficiency_bonus = 2 + ((level - 1) // 4)
        return self._proficiency_bonus
    
    @property
    def armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        if self._armor_class is None or self._needs_recalculation():
            self._armor_class = self._calculate_armor_class()
        return self._armor_class
    
    @property
    def max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if self._max_hit_points is None or self._needs_recalculation():
            self._max_hit_points = self._calculate_max_hit_points()
        return self._max_hit_points
    
    @property
    def initiative(self) -> int:
        """Calculate initiative bonus."""
        if self._initiative is None or self._needs_recalculation():
            self._initiative = self._calculate_initiative()
        return self._initiative
    
    @property
    def spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if self._spell_save_dc is None or self._needs_recalculation():
            self._spell_save_dc = self._calculate_spell_save_dc()
        return self._spell_save_dc
    
    @property
    def spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if self._spell_attack_bonus is None or self._needs_recalculation():
            self._spell_attack_bonus = self._calculate_spell_attack_bonus()
        return self._spell_attack_bonus
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive Perception score."""
        if self._passive_perception is None or self._needs_recalculation():
            self._passive_perception = self._calculate_passive_perception()
        return self._passive_perception
    
    def _calculate_armor_class(self) -> int:
        """Internal method to calculate armor class."""
        base_ac = 10
        dex_mod = self.core.dexterity.modifier
        
        # Check for worn armor
        if self.state.armor:
            armor_type = self.state.armor.lower()
            
            # Light armor
            if any(a in armor_type for a in ["padded", "leather"]):
                if "studded" in armor_type:
                    base_ac = 12 + dex_mod
                else:
                    base_ac = 11 + dex_mod
            
            # Medium armor
            elif any(a in armor_type for a in ["chain shirt", "scale", "breastplate", "half plate"]):
                if "chain shirt" in armor_type:
                    base_ac = 13 + min(dex_mod, 2)
                elif "scale" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "breastplate" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "half plate" in armor_type:
                    base_ac = 15 + min(dex_mod, 2)
            
            # Heavy armor
            elif any(a in armor_type for a in ["ring mail", "chain mail", "splint", "plate"]):
                if "ring mail" in armor_type:
                    base_ac = 14
                elif "chain mail" in armor_type:
                    base_ac = 16
                elif "splint" in armor_type:
                    base_ac = 17
                elif "plate" in armor_type:
                    base_ac = 18
        else:
            # Unarmored Defense
            if "Barbarian" in self.core.character_classes:
                con_mod = self.core.constitution.modifier
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
            
            if "Monk" in self.core.character_classes:
                wis_mod = self.core.wisdom.modifier
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self.state.shield:
            base_ac += 2
        
        return base_ac
    
    def _calculate_max_hit_points(self) -> int:
        """Internal method to calculate maximum hit points."""
        if not self.core.character_classes:
            return 1
        
        con_mod = self.core.constitution.modifier
        total = 0
        
        hit_die_sizes = {
            "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
            "Wizard": 6, "Sorcerer": 6
        }
        
        for class_name, level in self.core.character_classes.items():
            if level <= 0:
                continue
                
            hit_die = hit_die_sizes.get(class_name, 8)
            
            # First level is max hit die + CON
            if class_name == self.core.primary_class:
                total += hit_die + con_mod
                remaining_levels = level - 1
            else:
                remaining_levels = level
            
            # Average for remaining levels
            total += remaining_levels * ((hit_die // 2) + 1 + con_mod)
        
        # Add modifiers from state
        total += self.state.hit_point_maximum_modifier
        
        return max(1, total)
    
    def _calculate_initiative(self) -> int:
        """Internal method to calculate initiative."""
        dex_mod = self.core.dexterity.modifier
        bonus = 0
        
        # Check for feats and features
        if "Alert" in self.core.feats:
            bonus += 5
        
        if "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:  # Jack of All Trades
                bonus += self.proficiency_bonus // 2
        
        return dex_mod + bonus
    
    def _calculate_spell_save_dc(self) -> int:
        """Internal method to calculate spell save DC."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return 8 + self.proficiency_bonus + ability_mod
    
    def _calculate_spell_attack_bonus(self) -> int:
        """Internal method to calculate spell attack bonus."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return self.proficiency_bonus + ability_mod
    
    def _calculate_passive_perception(self) -> int:
        """Internal method to calculate passive Perception."""
        wis_mod = self.core.wisdom.modifier
        prof_bonus = 0
        
        perception_prof = self.core.skill_proficiencies.get("Perception", ProficiencyLevel.NONE)
        if perception_prof == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif perception_prof == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        feat_bonus = 5 if "Observant" in self.core.feats else 0
        
        return 10 + wis_mod + prof_bonus + feat_bonus
    
    def calculate_skill_bonus(self, skill_name: str) -> int:
        """Calculate bonus for a specific skill check."""
        skill_abilities = {
            "Athletics": "strength", "Acrobatics": "dexterity",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity",
            "Arcana": "intelligence", "History": "intelligence",
            "Investigation": "intelligence", "Nature": "intelligence", "Religion": "intelligence",
            "Animal Handling": "wisdom", "Insight": "wisdom", "Medicine": "wisdom",
            "Perception": "wisdom", "Survival": "wisdom",
            "Deception": "charisma", "Intimidation": "charisma",
            "Performance": "charisma", "Persuasion": "charisma"
        }
        
        if skill_name not in skill_abilities:
            return 0
        
        ability = skill_abilities[skill_name]
        ability_mod = self.core.get_ability_score(ability).modifier
        
        # Check proficiency
        prof_level = self.core.skill_proficiencies.get(skill_name, ProficiencyLevel.NONE)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Jack of All Trades for non-proficient skills
        if prof_level == ProficiencyLevel.NONE and "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:
                prof_bonus = self.proficiency_bonus // 2
        
        return ability_mod + prof_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calculated stats to dictionary."""
        return {
            "proficiency_bonus": self.proficiency_bonus,
            "armor_class": self.armor_class,
            "max_hit_points": self.max_hit_points,
            "initiative": self.initiative,
            "spell_save_dc": self.spell_save_dc,
            "spell_attack_bonus": self.spell_attack_bonus,
            "passive_perception": self.passive_perception,
            "available_actions": self._available_actions,
            "available_reactions": self._available_reactions
        }

import json
import os
from typing import Dict, Any

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend4/character_utils.py
def format_character_summary(character_data: Dict[str, Any]) -> str:
    """Format character data into readable text with enhanced details."""
    output = []
    
    # Basic identity
    output.append("=== CHARACTER IDENTITY ===")
    output.append(f"Name: {character_data.get('name', 'Unknown')}")
    output.append(f"Species: {character_data.get('species', 'Unknown')}")
    output.append(f"Level: {character_data.get('level', 1)}")
    output.append(f"Classes: {', '.join([f'{cls} ({lvl})' for cls, lvl in character_data.get('classes', {}).items()])}")
    
    # Subclasses
    if character_data.get('subclasses'):
        subclass_str = ', '.join([f"{cls}: {subcls}" for cls, subcls in character_data.get('subclasses', {}).items()])
        output.append(f"Subclasses: {subclass_str}")
    
    output.append(f"Background: {character_data.get('background', 'Unknown')}")
    output.append(f"Alignment: {character_data.get('alignment', 'Unknown')}")
    output.append("")
    
    # Ability scores
    output.append("=== ABILITY SCORES ===")
    abilities = character_data.get('ability_scores', {})
    mods = character_data.get('ability_modifiers', {})
    
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = abilities.get(ability, 10)
        mod = mods.get(ability, 0)
        mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
        output.append(f"{ability.capitalize():12} {score:2} ({mod_str})")
    output.append("")
    
    # Combat stats
    output.append("=== COMBAT ===")
    output.append(f"AC: {character_data.get('ac', 10)}")
    hp = character_data.get('hp', {})
    output.append(f"HP: {hp.get('current', 0)}/{hp.get('max', 0)}")
    output.append(f"Initiative: {character_data.get('initiative', 0)}")
    output.append(f"Proficiency Bonus: +{character_data.get('proficiency_bonus', 2)}")
    output.append("")
    
    # Enhanced Equipment Section
    output.append("=== EQUIPMENT ===")
    
    # Armor
    armor = character_data.get('armor', {})
    if isinstance(armor, dict) and armor.get('name'):
        output.append(f"Armor: {armor['name']} (AC {armor.get('ac_base', 10)})")
        if armor.get('special_properties'):
            output.append(f"  Properties: {', '.join(armor['special_properties'])}")
        if armor.get('description'):
            output.append(f"  Description: {armor['description']}")
    elif isinstance(armor, str) and armor:
        output.append(f"Armor: {armor}")
    
    # Weapons
    output.append("\nWeapons:")
    for weapon in character_data.get('weapons', []):
        if isinstance(weapon, dict):
            magical_indicator = " (Magical)" if weapon.get('magical', False) else ""
            output.append(f"- {weapon.get('name', 'Unknown')}{magical_indicator}")
            output.append(f"  Damage: {weapon.get('damage', '1d4')} {weapon.get('damage_type', 'piercing')}")
            if weapon.get('special_abilities'):
                output.append(f"  Special: {', '.join(weapon['special_abilities'])}")
            if weapon.get('description'):
                output.append(f"  Description: {weapon['description']}")
        elif isinstance(weapon, str):
            output.append(f"- {weapon}")
    
    # Magical Items
    magical_items = character_data.get('magical_items', [])
    if magical_items:
        output.append("\nMagical Items:")
        for item in magical_items:
            if isinstance(item, dict):
                attune_text = " (Requires Attunement)" if item.get('attunement', False) else ""
                output.append(f"- {item.get('name', 'Unknown')} ({item.get('rarity', 'common')}){attune_text}")
                if item.get('properties'):
                    output.append(f"  Properties: {', '.join(item['properties'])}")
                if item.get('description'):
                    output.append(f"  Description: {item['description']}")
    
    # Regular Equipment
    equipment = character_data.get('equipment', [])
    if equipment:
        output.append("\nOther Equipment:")
        for item in equipment:
            if isinstance(item, dict):
                qty_text = f" x{item['quantity']}" if item.get('quantity', 1) > 1 else ""
                output.append(f"- {item.get('name', 'Unknown')}{qty_text}")
            elif isinstance(item, str):
                output.append(f"- {item}")
    
    output.append("")
    
    # Special Abilities
    special_abilities = character_data.get('special_abilities', [])
    if special_abilities:
        output.append("=== SPECIAL ABILITIES ===")
        for ability in special_abilities:
            if isinstance(ability, dict):
                output.append(f"- {ability.get('name', 'Unknown')} ({ability.get('uses', 'at will')})")
                if ability.get('description'):
                    output.append(f"  {ability['description']}")
        output.append("")
    
    # Spellcasting
    if character_data.get('spellcasting_ability'):
        output.append("=== SPELLCASTING ===")
        output.append(f"Spellcasting Ability: {character_data['spellcasting_ability'].capitalize()}")
        output.append(f"Spell Save DC: {character_data.get('spell_save_dc', 10)}")
        output.append(f"Spell Attack Bonus: +{character_data.get('spell_attack_bonus', 0)}")
        
        # Spell slots
        spell_slots = character_data.get('spell_slots', {})
        if spell_slots:
            slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in spell_slots.items()])
            output.append(f"Spell Slots: {slots_text}")
        
        # Spells known
        spells_known = character_data.get('spells_known', {})
        if spells_known:
            output.append("\nSpells Known:")
            for level, spells in sorted(spells_known.items(), key=lambda x: int(x[0])):
                level_name = "Cantrips" if level == "0" else f"Level {level}"
                output.append(f"  {level_name}: {', '.join(spells)}")
        output.append("")
    
    # Skills and features
    output.append("=== PROFICIENT SKILLS ===")
    for skill in character_data.get('proficient_skills', []):
        output.append(f"- {skill}")
    output.append("")
    
    # Character details
    output.append("=== CHARACTER DETAILS ===")
    if character_data.get('personality_traits'):
        output.append("Personality Traits:")
        for trait in character_data.get('personality_traits', []):
            output.append(f"- {trait}")
    
    if character_data.get('ideals'):
        output.append("Ideals:")
        for ideal in character_data.get('ideals', []):
            output.append(f"- {ideal}")
            
    if character_data.get('bonds'):
        output.append("Bonds:")
        for bond in character_data.get('bonds', []):
            output.append(f"- {bond}")
            
    if character_data.get('flaws'):
        output.append("Flaws:")
        for flaw in character_data.get('flaws', []):
            output.append(f"- {flaw}")
    
    # Enhanced personality details
    personality_details = character_data.get('personality_details', {})
    if personality_details:
        output.append("\n=== PERSONALITY DETAILS ===")
        if personality_details.get('appearance'):
            output.append(f"Appearance: {personality_details['appearance']}")
        if personality_details.get('mannerisms'):
            output.append(f"Mannerisms: {', '.join(personality_details['mannerisms'])}")
        if personality_details.get('voice_and_speech'):
            output.append(f"Voice: {personality_details['voice_and_speech']}")
    
    # Enhanced backstory
    if character_data.get('backstory'):
        output.append("\n=== BACKSTORY ===")
        output.append(character_data.get('backstory', ''))
    
    return "\n".join(output)


def save_character(character_data: Dict[str, Any], save_dir: str = None) -> str:
    """Save character data to a JSON file."""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_characters')
    
    # Create characters directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Generate filename from character name
    char_name = character_data.get('name', 'unnamed_character')
    safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
    filename = os.path.join(save_dir, f"{safe_name}.json")
    
    # Save the character data
    with open(filename, 'w') as f:
        json.dump(character_data, f, indent=2)
    
    return filename

from typing import Dict, Any, List, Tuple
import logging

from .content_registry import ContentRegistry
from .constants import RuleConstants

logger = logging.getLogger(__name__)

class CharacterValidationEngine:
    """Specialized engine for comprehensive character validation."""
    
    def __init__(self):
        self.content_registry = ContentRegistry()
        self.constants = RuleConstants()
    
    def validate_character_sheet(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate an entire character sheet against all rules."""
        results = []
        
        try:
            # Basic character information
            results.extend(self._validate_basic_info(character_sheet))
            
            # Character build validation
            results.extend(self._validate_character_build(character_sheet))
            
            # Equipment and resources
            results.extend(self._validate_equipment_and_resources(character_sheet))
            
            # Multiclass validation
            results.extend(self._validate_multiclass_rules(character_sheet))
            
        except Exception as e:
            logger.error(f"Character validation failed: {e}")
            results.append((False, f"Validation error: {str(e)}"))
        
        return results
    
    def validate_creation_data(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character data during creation process."""
        issues = []
        warnings = []
        
        # Validate required fields
        required_fields = ["name", "species", "classes", "ability_scores"]
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate classes
        if "classes" in character_data:
            class_issues = self._validate_classes_data(character_data["classes"])
            issues.extend(class_issues)
        
        # Validate ability scores
        if "ability_scores" in character_data:
            ability_issues = self._validate_ability_scores_data(character_data["ability_scores"])
            issues.extend(ability_issues)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def _validate_basic_info(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate basic character information."""
        results = []
        
        # Name validation
        name = character_sheet.get_name() if hasattr(character_sheet, 'get_name') else ""
        if not name or len(name.strip()) < 2:
            results.append((False, "Character name must be at least 2 characters"))
        else:
            results.append((True, "Valid character name"))
        
        # Species validation
        species = character_sheet.get_species() if hasattr(character_sheet, 'get_species') else ""
        if self.content_registry.is_valid_species(species):
            results.append((True, f"Valid species: {species}"))
        else:
            results.append((False, f"Invalid species: {species}"))
        
        return results
    
    def _validate_character_build(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate character build (classes, levels, abilities)."""
        results = []
        
        # Class validation
        if hasattr(character_sheet, 'get_class_levels'):
            class_levels = character_sheet.get_class_levels()
            
            if not class_levels:
                results.append((False, "Character must have at least one class"))
            else:
                total_level = sum(class_levels.values())
                if total_level > self.constants.MAX_LEVEL:
                    results.append((False, f"Total level ({total_level}) exceeds maximum ({self.constants.MAX_LEVEL})"))
                else:
                    results.append((True, f"Valid total level: {total_level}"))
                
                # Validate each class
                for class_name, level in class_levels.items():
                    if self.content_registry.is_valid_class(class_name):
                        results.append((True, f"Valid class: {class_name} (level {level})"))
                    else:
                        results.append((False, f"Invalid class: {class_name}"))
        
        return results
    
    def _validate_equipment_and_resources(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate equipment and character resources."""
        results = []
        
        # Basic equipment validation
        if hasattr(character_sheet, 'get_weapons'):
            weapons = character_sheet.get_weapons()
            if isinstance(weapons, list):
                results.append((True, f"Character has {len(weapons)} weapons"))
            else:
                results.append((False, "Weapons data is malformed"))
        
        return results
    
    def _validate_multiclass_rules(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate multiclass-specific rules."""
        results = []
        
        if hasattr(character_sheet, 'get_class_levels'):
            class_levels = character_sheet.get_class_levels()
            
            if len(class_levels) > 1:
                # This is a multiclass character
                results.append((True, "Multiclass character detected"))
                
                # Validate multiclass requirements would go here
                # This would require ability scores and detailed validation
            else:
                results.append((True, "Single-class character"))
        
        return results
    
    def _validate_classes_data(self, classes_data: Dict[str, int]) -> List[str]:
        """Validate classes data structure."""
        issues = []
        
        if not isinstance(classes_data, dict):
            issues.append("Classes must be a dictionary mapping class names to levels")
            return issues
        
        for class_name, level in classes_data.items():
            if not self.content_registry.is_valid_class(class_name):
                issues.append(f"Invalid class: {class_name}")
            
            if not isinstance(level, int) or level < 1 or level > 20:
                issues.append(f"Invalid level for {class_name}: {level}")
        
        return issues
    
    def _validate_ability_scores_data(self, ability_scores: Dict[str, int]) -> List[str]:
        """Validate ability scores data structure."""
        issues = []
        
        required_abilities = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        
        for ability in required_abilities:
            if ability not in ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = ability_scores[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score}")
        
        return issues

class RuleConstants:
    """Centralized constants for D&D 2024 rules."""
    
    # Ability Score Rules
    ABILITY_SCORE_MIN = 3
    ABILITY_SCORE_MAX = 30
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    
    # Character Level Rules
    MIN_LEVEL = 1
    MAX_LEVEL = 20
    
    # XP thresholds, proficiency bonuses, etc.
    XP_BY_LEVEL = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Base content sets
    BASE_CLASSES = {
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    }
    
    # Class data
    HIT_DIE_BY_CLASS = {
        "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
        "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
        "Artificer": 8, "Wizard": 6, "Sorcerer": 6
    }
    
    MULTICLASS_REQUIREMENTS = {
        "Artificer": {"intelligence": 13},
        "Barbarian": {"strength": 13},
        "Bard": {"charisma": 13},
        "Cleric": {"wisdom": 13},
        "Druid": {"wisdom": 13},
        "Fighter": {"strength": 13, "dexterity": 13},  # Either
        "Monk": {"dexterity": 13, "wisdom": 13},
        "Paladin": {"strength": 13, "charisma": 13},
        "Ranger": {"dexterity": 13, "wisdom": 13},
        "Rogue": {"dexterity": 13},
        "Sorcerer": {"charisma": 13},
        "Warlock": {"charisma": 13},
        "Wizard": {"intelligence": 13}
    }

    # remember new classes can be created, so the multiclass_requirements need to be flexible to allow for new classes

from typing import Dict, Any, Set, Optional
import logging

from .constants import RuleConstants
from .validators import ContentValidator

logger = logging.getLogger(__name__)

class ContentRegistry:
    """Manages registration and validation of custom game content."""
    
    def __init__(self):
        self.constants = RuleConstants()
        self.validator = ContentValidator()
        
        # Custom content storage
        self.custom_classes: Set[str] = set()
        self.custom_species: Set[str] = set()
        self.custom_feats: Set[str] = set()
        self.custom_spells: Set[str] = set()
        self.custom_backgrounds: Set[str] = set()
        self.custom_weapons: Dict[str, Dict[str, Any]] = {}
        self.custom_armor: Dict[str, Dict[str, Any]] = {}
        
        # Custom class data
        self.custom_hit_dice: Dict[str, int] = {}
        self.custom_multiclass_requirements: Dict[str, Dict[str, int]] = {}
        self.custom_subclass_levels: Dict[str, int] = {}
    
    def register_class(self, class_name: str, hit_die: int, **kwargs) -> bool:
        """Register a custom character class with validation."""
        try:
            # Validate input
            self.validator.validate_class_name(class_name)
            self.validator.validate_hit_die(hit_die)
            
            if class_name in self.constants.BASE_CLASSES or class_name in self.custom_classes:
                raise ValueError(f"Class '{class_name}' already exists")
            
            # Validate optional parameters
            multiclass_requirements = kwargs.get('multiclass_requirements')
            if multiclass_requirements:
                self.validator.validate_multiclass_requirements(multiclass_requirements)
                self.custom_multiclass_requirements[class_name] = multiclass_requirements
            
            # Store class data
            self.custom_classes.add(class_name)
            self.custom_hit_dice[class_name] = hit_die
            self.custom_subclass_levels[class_name] = kwargs.get('subclass_level', 3)
            
            logger.info(f"Registered custom class: {class_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register class '{class_name}': {e}")
            return False
    
    def register_species(self, species_name: str, abilities: Dict[str, Any]) -> bool:
        """Register a custom species with validation."""
        try:
            self.validator.validate_species_name(species_name)
            self.validator.validate_species_abilities(abilities)
            
            if species_name in self.custom_species:
                raise ValueError(f"Species '{species_name}' already exists")
            
            self.custom_species.add(species_name)
            logger.info(f"Registered custom species: {species_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register species '{species_name}': {e}")
            return False
    
    def register_feat(self, feat_name: str, feat_details: Dict[str, Any]) -> bool:
        """Register a custom feat with validation."""
        try:
            self.validator.validate_feat_name(feat_name)
            self.validator.validate_feat_details(feat_details)
            
            if feat_name in self.custom_feats:
                raise ValueError(f"Feat '{feat_name}' already exists")
            
            self.custom_feats.add(feat_name)
            logger.info(f"Registered custom feat: {feat_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register feat '{feat_name}': {e}")
            return False
    
    def register_spell(self, spell_name: str, spell_details: Dict[str, Any]) -> bool:
        """Register a custom spell with validation."""
        try:
            self.validator.validate_spell_name(spell_name)
            self.validator.validate_spell_details(spell_details)
            
            if spell_name in self.custom_spells:
                raise ValueError(f"Spell '{spell_name}' already exists")
            
            self.custom_spells.add(spell_name)
            logger.info(f"Registered custom spell: {spell_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register spell '{spell_name}': {e}")
            return False
    
    def register_background(self, background_name: str, background_details: Dict[str, Any]) -> bool:
        """Register a custom background with validation."""
        try:
            self.validator.validate_background_name(background_name)
            self.validator.validate_background_details(background_details)
            
            if background_name in self.custom_backgrounds:
                raise ValueError(f"Background '{background_name}' already exists")
            
            self.custom_backgrounds.add(background_name)
            logger.info(f"Registered custom background: {background_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register background '{background_name}': {e}")
            return False
    
    def register_weapon(self, weapon_name: str, properties: Dict[str, Any]) -> bool:
        """Register a custom weapon with validation."""
        try:
            self.validator.validate_weapon_name(weapon_name)
            self.validator.validate_weapon_properties(properties)
            
            if weapon_name in self.custom_weapons:
                raise ValueError(f"Weapon '{weapon_name}' already exists")
            
            self.custom_weapons[weapon_name] = properties
            logger.info(f"Registered custom weapon: {weapon_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register weapon '{weapon_name}': {e}")
            return False
    
    def register_armor(self, armor_name: str, properties: Dict[str, Any]) -> bool:
        """Register a custom armor with validation."""
        try:
            self.validator.validate_armor_name(armor_name)
            self.validator.validate_armor_properties(properties)
            
            if armor_name in self.custom_armor:
                raise ValueError(f"Armor '{armor_name}' already exists")
            
            self.custom_armor[armor_name] = properties
            logger.info(f"Registered custom armor: {armor_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register armor '{armor_name}': {e}")
            return False
    
    # Query methods
    def is_valid_class(self, class_name: str) -> bool:
        """Check if a class name is valid."""
        return class_name in self.constants.BASE_CLASSES or class_name in self.custom_classes
    
    def is_valid_species(self, species_name: str) -> bool:
        """Check if a species name is valid."""
        return species_name in self.custom_species
    
    def get_class_info(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a class."""
        if class_name in self.constants.BASE_CLASSES:
            return {
                "hit_die": self.constants.HIT_DIE_BY_CLASS.get(class_name, 8),
                "multiclass_requirements": self.constants.MULTICLASS_REQUIREMENTS.get(class_name, {}),
                "subclass_level": 3,  # Default for most classes
                "custom": False
            }
        elif class_name in self.custom_classes:
            return {
                "hit_die": self.custom_hit_dice.get(class_name, 8),
                "multiclass_requirements": self.custom_multiclass_requirements.get(class_name, {}),
                "subclass_level": self.custom_subclass_levels.get(class_name, 3),
                "custom": True
            }
        return None
    
    def get_multiclass_requirements(self, class_name: str) -> Dict[str, int]:
        """Get multiclass requirements for a class."""
        if class_name in self.constants.BASE_CLASSES:
            return self.constants.MULTICLASS_REQUIREMENTS.get(class_name, {})
        elif class_name in self.custom_classes:
            return self.custom_multiclass_requirements.get(class_name, {})
        return {}

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union, Tuple, Any
import logging

from .rules import (
    RuleConstants,
    ValidationEngine,
    ContentRegistry,
    MulticlassEngine,
    CharacterValidationEngine
)

logger = logging.getLogger(__name__)

class CreateRules(ABC):
    """
    Unified interface for D&D 2024 Edition rule enforcement.
    
    This class provides a clean API for all rule-related operations while
    delegating implementation to specialized sub-engines.
    """
    
    # Initialize specialized engines
    _constants = RuleConstants()
    _validation_engine = ValidationEngine()
    _content_registry = ContentRegistry()
    _multiclass_engine = MulticlassEngine()
    _character_validator = CharacterValidationEngine()
    
    # ===== CONTENT REGISTRATION API =====
    
    @classmethod
    def register_custom_class(cls, class_name: str, hit_die: int, **kwargs) -> bool:
        """Register a custom character class."""
        return cls._content_registry.register_class(class_name, hit_die, **kwargs)
    
    @classmethod
    def register_custom_species(cls, species_name: str, abilities: Dict[str, Any]) -> bool:
        """Register a custom species."""
        return cls._content_registry.register_species(species_name, abilities)
    
    @classmethod
    def register_custom_feat(cls, feat_name: str, feat_details: Dict[str, Any]) -> bool:
        """Register a custom feat."""
        return cls._content_registry.register_feat(feat_name, feat_details)
    
    @classmethod
    def register_custom_spell(cls, spell_name: str, spell_details: Dict[str, Any]) -> bool:
        """Register a custom spell."""
        return cls._content_registry.register_spell(spell_name, spell_details)
    
    @classmethod
    def register_custom_background(cls, background_name: str, background_details: Dict[str, Any]) -> bool:
        """Register a custom background."""
        return cls._content_registry.register_background(background_name, background_details)
    
    @classmethod
    def register_custom_weapon(cls, weapon_name: str, properties: Dict[str, Any]) -> bool:
        """Register a custom weapon."""
        return cls._content_registry.register_weapon(weapon_name, properties)
    
    @classmethod
    def register_custom_armor(cls, armor_name: str, properties: Dict[str, Any]) -> bool:
        """Register a custom armor."""
        return cls._content_registry.register_armor(armor_name, properties)
    
    # ===== MULTICLASS AND LEVEL-UP API =====
    
    @classmethod
    def calculate_level_up_changes(cls, current_character: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """Calculate changes when a character levels up."""
        return cls._multiclass_engine.calculate_level_up_changes(current_character, new_level)
    
    @classmethod
    def validate_multiclass_eligibility(cls, character_data: Dict[str, Any], new_class: str) -> Tuple[bool, str]:
        """Validate if character can multiclass into a new class."""
        return cls._multiclass_engine.validate_multiclass_eligibility(character_data, new_class)
    
    @classmethod
    def calculate_multiclass_spell_slots(cls, character_data: Dict[str, Any]) -> Dict[int, int]:
        """Calculate spell slots for multiclass spellcasters."""
        return cls._multiclass_engine.calculate_spell_slots(character_data)
    
    @classmethod
    def get_level_up_options(cls, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available options when leveling up."""
        return cls._multiclass_engine.get_level_up_options(character_data)
    
    @classmethod
    def apply_level_up(cls, character_data: Dict[str, Any], level_up_choices: Dict[str, Any]) -> Dict[str, Any]:
        """Apply level up choices to character data."""
        return cls._multiclass_engine.apply_level_up(character_data, level_up_choices)
    
    # ===== VALIDATION API =====
    
    @classmethod
    def validate_entire_character_sheet(cls, character_sheet) -> List[Tuple[bool, str]]:
        """Validate an entire character sheet against all rules."""
        return cls._character_validator.validate_character_sheet(character_sheet)
    
    @classmethod
    def validate_character_creation(cls, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character data during creation process."""
        return cls._character_validator.validate_creation_data(character_data)
    
    # ===== UTILITY API =====
    
    @classmethod
    def is_valid_class(cls, class_name: str) -> bool:
        """Check if a class name is valid."""
        return cls._content_registry.is_valid_class(class_name)
    
    @classmethod
    def is_valid_species(cls, species_name: str) -> bool:
        """Check if a species name is valid."""
        return cls._content_registry.is_valid_species(species_name)
    
    @classmethod
    def get_class_info(cls, class_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a class."""
        return cls._content_registry.get_class_info(class_name)
    
    @classmethod
    def get_multiclass_requirements(cls, class_name: str) -> Dict[str, int]:
        """Get multiclass requirements for a class."""
        return cls._content_registry.get_multiclass_requirements(class_name)

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import json5
import re


# # Using Ollama (default)
# llm_service = OllamaLLMService(model="llama3")

# # Using OpenAI
# llm_service = OpenAILLMService(api_key="your-api-key", model="gpt-4")

# # Using Anthropic
# llm_service = AnthropicLLMService(api_key="your-api-key", model="claude-3-sonnet-20240229")

# # Using factory
# llm_service = create_llm_service('ollama', model="llama3")
# llm_service = create_llm_service('openai', api_key="your-key", model="gpt-4")

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the LLM service is available."""
        pass


class OllamaLLMService(LLMService):
    """Ollama implementation of LLM service."""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        import ollama
        
        self.model = model
        self.ollama_client = ollama.Client(host=host)
        self.conversation_history = []
        
        # Enhanced system prompt for specialized equipment and detailed backgrounds
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        Create character data using this exact schema:
        {
          "name": "ALWAYS provide a character name here - generate one if needed",
          "species": "Species",
          "level": X,
          "classes": {"Class Name": Level},
          "subclasses": {"Class Name": "Subclass"},
          "background": "Background",
          "alignment": ["Ethical", "Moral"],
          "ability_scores": {
            "strength": X, "dexterity": X, "constitution": X, 
            "intelligence": X, "wisdom": X, "charisma": X
          },
          "skill_proficiencies": ["Skill1", "Skill2"],
          "saving_throw_proficiencies": ["Ability1", "Ability2"],
          "personality_traits": ["Trait1", "Trait2", "Trait3"],
          "ideals": ["Ideal1", "Ideal2"],
          "bonds": ["Bond1", "Bond2"],
          "flaws": ["Flaw1", "Flaw2"],
          "armor": {
            "name": "Armor Name",
            "type": "light/medium/heavy",
            "ac_base": X,
            "special_properties": ["property1", "property2"],
            "description": "Detailed description of the armor"
          },
          "weapons": [
            {
              "name": "Weapon Name",
              "type": "simple/martial/exotic",
              "damage": "XdY + modifier",
              "damage_type": "slashing/piercing/bludgeoning/force/etc",
              "properties": ["property1", "property2"],
              "special_abilities": ["ability1", "ability2"],
              "description": "Detailed description including special features",
              "magical": true/false,
              "rarity": "common/uncommon/rare/very rare/legendary/artifact"
            }
          ],
          "magical_items": [
            {
              "name": "Item Name",
              "type": "wondrous item/ring/amulet/etc",
              "rarity": "common/uncommon/rare/very rare/legendary/artifact",
              "attunement": true/false,
              "properties": ["property1", "property2"],
              "description": "Detailed description of magical properties"
            }
          ],
          "equipment": [
            {
              "name": "Item Name",
              "quantity": X,
              "description": "Item description"
            }
          ],
          "backstory": "Detailed backstory (minimum 3-4 paragraphs covering origin, motivations, key events, current goals)",
          "personality_details": {
            "mannerisms": ["mannerism1", "mannerism2"],
            "interaction_traits": ["trait1", "trait2"],
            "appearance": "Detailed physical description",
            "voice_and_speech": "How they speak and sound"
          }
        }

        If character is a spellcaster, include:
        {
          "spellcasting_ability": "ability",
          "spell_save_dc": X,
          "spell_attack_bonus": X,
          "spells_known": {
            "0": ["Cantrip1", "Cantrip2"],
            "1": ["1st Level Spell1", "1st Level Spell2"],
            "2": ["2nd Level Spell1"],
            etc.
          },
          "spell_slots": {
            "1": X, "2": X, "3": X, etc.
          }
        }

        For special character concepts (Jedi, etc.), create appropriate abilities:
        {
          "special_abilities": [
            {
              "name": "Ability Name",
              "type": "supernatural/spell-like/extraordinary",
              "uses": "X/day" or "at will" or "constant",
              "description": "Detailed description of the ability"
            }
          ]
        }

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
        
        self._ensure_model_available()
    
    def _ensure_model_available(self) -> None:
        """Verify that the required model is available, attempt to pull if not."""
        try:
            models = self.ollama_client.list()
            model_exists = False
            if 'models' in models:
                model_exists = any(model.get('name', '') == self.model for model in models['models'])
            
            if not model_exists:
                print(f"Model {self.model} not found. Attempting to pull...")
                self.ollama_client.pull(self.model)
                print(f"Successfully pulled {self.model}")
                
        except Exception as e:
            print(f"Warning: Could not verify model availability: {str(e)}")
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from Ollama."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            response = self.ollama_client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    *conversation_history,
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': response['message']['content']})
            
            return response['message']['content']
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the Ollama service."""
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt="Hello, are you working properly?"
            )
            print(f"Connection test successful: {response['response'][:50]}...")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


class OpenAILLMService(LLMService):
    """OpenAI implementation of LLM service."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", max_tokens: int = 4000):
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Same enhanced system prompt as Ollama
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        [Same detailed schema as Ollama service...]

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from OpenAI."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                *conversation_history,
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the OpenAI service."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Hello, are you working properly?'}],
                max_tokens=50
            )
            print(f"OpenAI connection test successful: {response.choices[0].message.content[:50]}...")
            return True
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False


class AnthropicLLMService(LLMService):
    """Anthropic Claude implementation of LLM service."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", max_tokens: int = 4000):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Same enhanced system prompt
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        [Same detailed schema as other services...]

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from Anthropic Claude."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            # Convert conversation history to Claude format
            messages = []
            for msg in conversation_history:
                if msg['role'] != 'system':  # Claude handles system prompts separately
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # Add current prompt
            messages.append({'role': 'user', 'content': prompt})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                messages=messages
            )
            
            content = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
        except Exception as e:
            print(f"Error calling Anthropic: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the Anthropic service."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                system="You are a helpful assistant.",
                messages=[{'role': 'user', 'content': 'Hello, are you working properly?'}]
            )
            print(f"Anthropic connection test successful: {response.content[0].text[:50]}...")
            return True
        except Exception as e:
            print(f"Anthropic connection test failed: {e}")
            return False

class BedrockLLMService(LLMService):
    """AWS Bedrock implementation of LLM service."""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", 
                 region: str = "us-east-1", max_tokens: int = 4000):
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 package not installed. Run: pip install boto3")
        
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
        
        # Same enhanced system prompt as other services
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.
        [Same detailed prompt as other services...]
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from AWS Bedrock."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            # Build conversation for Claude via Bedrock
            messages = []
            for msg in conversation_history:
                if msg['role'] != 'system':
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            messages.append({'role': 'user', 'content': prompt})
            
            # Bedrock request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to AWS Bedrock."""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "system": "You are a helpful assistant.",
                "messages": [{'role': 'user', 'content': 'Hello, are you working properly?'}]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            print(f"Bedrock connection test successful: {content[:50]}...")
            return True
            
        except Exception as e:
            print(f"Bedrock connection test failed: {e}")
            return False


class JSONExtractor:
    """Utility class for extracting JSON from LLM responses."""
    
    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with multi-layered fallback strategies."""
        try:
            print(f"Processing response: {text[:100]}..." if len(text) > 100 else text)
            
            # 1. First, try direct JSON parsing
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed, trying alternatives...")
            
            # 2. Try to find JSON content using regex for code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                json_content = json_match.group(1)
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Code block extraction failed...")
            
            # 3. Try to find the outermost JSON object
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                json_content = json_match.group(1)
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Regex JSON extraction failed...")
            
            # 4. Try manual extraction of start/end braces
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx >= 0 and end_idx >= 0 and end_idx > start_idx:
                json_content = text[start_idx:end_idx+1]
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Manual brace extraction failed...")
            
            # 5. Try with json5 for more lenient parsing
            try:
                return json5.loads(text)
            except Exception:
                print("JSON5 parsing failed...")
                
            # 6. Try cleaning and json5 parsing
            cleaned_text = text.replace('\n', ' ').replace('\r', '')
            try:
                return json5.loads(cleaned_text)
            except Exception:
                print("Clean JSON5 parsing failed...")
            
            # 7. Try fixing common JSON issues
            fixed_text = JSONExtractor._fix_common_json_issues(text)
            if fixed_text:
                try:
                    return json.loads(fixed_text)
                except json.JSONDecodeError:
                    pass
            
            print("All JSON parsing methods failed")
            return {}
            
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            return {}
    
    @staticmethod
    def _fix_common_json_issues(text: str) -> str:
        """Attempt to fix common JSON formatting issues."""
        try:
            # Remove any text before the first {
            start_idx = text.find('{')
            if start_idx > 0:
                text = text[start_idx:]
            
            # Remove any text after the last }
            end_idx = text.rfind('}')
            if end_idx >= 0:
                text = text[:end_idx + 1]
            
            # Fix trailing commas
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            
            # Fix unquoted keys (basic attempt)
            text = re.sub(r'(\w+):', r'"\1":', text)
            
            # Fix single quotes to double quotes
            text = text.replace("'", '"')
            
            return text
        except Exception:
            return ""


# Factory function for easy LLM service creation
def create_llm_service(service_type: str, **kwargs) -> LLMService:
    """
    Factory function to create LLM services.
    
    Args:
        service_type: Type of service ('ollama', 'openai', 'anthropic', 'bedrock')
        **kwargs: Additional arguments for the specific service
    
    Returns:
        LLMService: Configured LLM service instance
    """
    if service_type.lower() == 'ollama':
        return OllamaLLMService(**kwargs)
    elif service_type.lower() == 'openai':
        return OpenAILLMService(**kwargs)
    elif service_type.lower() == 'anthropic':
        return AnthropicLLMService(**kwargs)
    elif service_type.lower() == 'bedrock':
        return BedrockLLMService(**kwargs)
    else:
        raise ValueError(f"Unknown service type: {service_type}")

from typing import Dict, Any, Tuple
import logging

from abstract_multiclass_and_level_up import DNDMulticlassAndLevelUp
from .content_registry import ContentRegistry

logger = logging.getLogger(__name__)

class MulticlassEngine:
    """Handles all multiclass and level-up operations."""
    
    def __init__(self):
        self.content_registry = ContentRegistry()
    
    def calculate_level_up_changes(self, current_character: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """Calculate changes when a character levels up."""
        handler = DNDMulticlassAndLevelUp(current_character)
        return handler.calculate_level_up_changes(current_character, new_level)
    
    def validate_multiclass_eligibility(self, character_data: Dict[str, Any], new_class: str) -> Tuple[bool, str]:
        """Validate if character can multiclass into a new class."""
        handler = DNDMulticlassAndLevelUp(character_data)
        return handler.can_multiclass_into(new_class)
    
    def calculate_spell_slots(self, character_data: Dict[str, Any]) -> Dict[int, int]:
        """Calculate spell slots for multiclass spellcasters."""
        handler = DNDMulticlassAndLevelUp(character_data)
        return handler.get_multiclass_spell_slots()
    
    def get_level_up_options(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available options when leveling up."""
        handler = DNDMulticlassAndLevelUp(character_data)
        current_level = handler.calculate_character_level()
        
        # Check if character can level up
        can_level, message = handler.check_level_up_eligibility()
        if not can_level:
            return {"can_level_up": False, "message": message}
        
        # Get available classes for multiclassing
        available_classes = handler.get_available_classes_for_multiclass()
        current_classes = list(character_data.get("classes", {}).keys())
        
        return {
            "can_level_up": True,
            "current_level": current_level,
            "next_level": current_level + 1,
            "xp_needed": handler.get_next_level_xp_threshold(),
            "current_classes": current_classes,
            "multiclass_options": {
                class_name: eligible for class_name, eligible in available_classes.items()
                if class_name not in current_classes
            },
            "level_up_in_existing": {
                class_name: f"Continue as {class_name}"
                for class_name in current_classes
            }
        }
    
    def apply_level_up(self, character_data: Dict[str, Any], level_up_choices: Dict[str, Any]) -> Dict[str, Any]:
        """Apply level up choices to character data."""
        handler = DNDMulticlassAndLevelUp(character_data)
        
        # Determine which class to level up in
        target_class = level_up_choices.get("class")
        if not target_class:
            # Default to primary class
            classes = character_data.get("classes", {})
            if classes:
                target_class = max(classes.items(), key=lambda x: x[1])[0]
            else:
                return {"error": "No class specified and no existing classes found"}
        
        # Perform the level up
        level_up_result = handler.level_up(target_class if target_class not in character_data.get("classes", {}) else None)
        
        if "error" in level_up_result:
            return level_up_result
        
        # Apply choices
        if level_up_choices:
            success = handler.apply_level_up_choices(level_up_choices)
            if not success:
                return {"error": "Failed to apply level up choices"}
        
        # Return updated character data
        updated_data = character_data.copy()
        updated_data.update({
            "level": level_up_result["new_level"],
            "classes": level_up_result["new_class_levels"],
            "experience_points": character_data.get("experience_points", 0)
        })
        
        return {
            "success": True,
            "updated_character": updated_data,
            "level_up_summary": level_up_result
        }

import sys
import os

# Add the project root to the path
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')

# Import required modules
try:
    from llm_service import OllamaLLMService
    from backend4.character_creator import CharacterCreator
    from character_utils import format_character_summary, save_character
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required files are in place:")
    print("- llm_service.py")
    print("- character_creator_v2.py") 
    print("- character_utils.py")
    print("- character_sheet.py")
    sys.exit(1)


def run_character_creator():
    """Run the character creator with progression options."""
    print("=== D&D Character Creator with Progression ===")
    
    # Initialize services
    llm_service = OllamaLLMService(model="llama3")
    creator = CharacterCreator(llm_service)
    
    if not creator.test_connection():
        print("❌ Failed to connect to LLM. Please make sure your LLM service is running.")
        return
    
    print("✅ Successfully connected to LLM service\n")
    
    # Get creation options
    print("Choose an option:")
    print("1. Create character at specific level")
    print("2. Create full character progression (levels 1-20)")
    print("3. Create progression up to specific level")
    
    choice = input("> ").strip()
    
    # Get character description
    print("\nWhat type of character would you like to create?")
    print("Examples:")
    print("- An elven wizard who specializes in illusion magic")
    print("- A dwarven paladin seeking redemption")
    print("- A half-orc barbarian with a gentle heart")
    description = input("> ")
    
    try:
        if choice == "1":
            # Single level creation
            print("\nWhat level should this character be? (1-20)")
            level = int(input("> "))
            level = max(1, min(20, level))
            
            print(f"\nCreating level {level} character...")
            summary = creator.create_character(description, level)
            print("\n" + format_character_summary(summary))
            
        elif choice == "2":
            # Full progression
            print("\nCreating full character progression (levels 1-20)...")
            progression = creator.create_character_progression(description, 20)
            
            # Show progression summary
            print(creator.preview_progression_summary())
            
            # Ask which level to display in detail
            print("Which level would you like to see in detail? (1-20)")
            display_level = int(input("> "))
            character_data = creator.get_character_at_level(display_level)
            creator.populate_character(character_data)
            summary = creator.character.get_character_summary()
            print(f"\n=== Level {display_level} Character ===")
            print(format_character_summary(summary))
            
        elif choice == "3":
            # Progression up to specific level
            print("\nWhat's the maximum level for progression? (1-20)")
            max_level = int(input("> "))
            max_level = max(1, min(20, max_level))
            
            print(f"\nCreating character progression (levels 1-{max_level})...")
            progression = creator.create_character_progression(description, max_level)
            
            print(creator.preview_progression_summary())
            
            # Show final level by default
            character_data = creator.get_character_at_level(max_level)
            creator.populate_character(character_data)
            summary = creator.character.get_character_summary()
            print(f"\n=== Level {max_level} Character ===")
            print(format_character_summary(summary))
            
        else:
            print("Invalid choice. Please run again.")
            return
        
        # Ask to save
        print("\nWould you like to save this character? (yes/no)")
        if input("> ").lower() in ['yes', 'y']:
            if hasattr(creator, 'character_progression') and creator.character_progression:
                print("Character progression saved!")
            else:
                filename = save_character(summary)
                print(f"Character saved to: {filename}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_character_creator()

import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

# Add project paths for imports
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend')

# Core imports
from character_sheet import CharacterSheet
from create_rules import CreateRules

# Try to import legacy validators with fallbacks
try:
    from backend.core.character.character_validator import CharacterValidator
    LEGACY_VALIDATOR_AVAILABLE = True
except ImportError:
    print("Warning: Legacy CharacterValidator not found, using simplified validation")
    LEGACY_VALIDATOR_AVAILABLE = False

try:
    from backend.services.validation_service import ValidationService
    VALIDATION_SERVICE_AVAILABLE = True
except ImportError:
    print("Warning: ValidationService not found")
    VALIDATION_SERVICE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ValidationResult:
    """Structured validation result container."""
    
    def __init__(self, valid: bool = True, issues: List[str] = None, 
                 warnings: List[str] = None, validator_name: str = "unknown"):
        self.valid = valid
        self.issues = issues or []
        self.warnings = warnings or []
        self.validator_name = validator_name
        self.total_checks = len(self.issues) + len(self.warnings) if self.issues or self.warnings else 1
        self.passed_checks = 1 if valid else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "validator": self.validator_name,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks
        }


class SimplifiedCharacterValidator:
    """Fallback validator when legacy systems aren't available."""
    
    def validate_full_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic character validation."""
        issues = []
        warnings = []
        
        # Basic required fields
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate ability scores
        if "ability_scores" in character_data:
            for ability, score in character_data["ability_scores"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score} (must be 1-30)")
        
        # Validate level
        if "level" in character_data:
            level = character_data["level"]
            if not isinstance(level, int) or level < 1 or level > 20:
                issues.append(f"Invalid character level: {level} (must be 1-20)")
        
        # Validate classes
        if "classes" in character_data:
            classes = character_data["classes"]
            if isinstance(classes, dict):
                total_levels = sum(classes.values())
                if total_levels != character_data.get("level", 1):
                    warnings.append(f"Class levels ({total_levels}) don't match character level ({character_data.get('level', 1)})")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_checks": len(issues) + len(warnings) + 1,
            "passed_checks": len(issues) == 0
        }


class UnifiedCharacterValidator:
    """
    Unified character validator that combines multiple validation approaches.
    
    This validator attempts to use:
    1. Legacy CharacterValidator (if available)
    2. ValidationService (if available) 
    3. CreateRules comprehensive validation
    4. Simplified fallback validation
    """
    
    def __init__(self):
        # Initialize available validators
        self.legacy_validator = None
        self.validation_service = None
        self.create_rules = CreateRules()
        self.simplified_validator = SimplifiedCharacterValidator()
        
        # Try to initialize legacy systems
        if LEGACY_VALIDATOR_AVAILABLE:
            try:
                self.legacy_validator = CharacterValidator()
                logger.info("Legacy CharacterValidator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize legacy validator: {e}")
        
        if VALIDATION_SERVICE_AVAILABLE:
            try:
                self.validation_service = ValidationService()
                logger.info("ValidationService initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize validation service: {e}")
    
    def validate_character(self, character_data: Dict[str, Any], 
                          character_sheet: Optional[CharacterSheet] = None) -> Dict[str, Any]:
        """
        Comprehensive character validation using all available validators.
        
        Args:
            character_data: Character data dictionary
            character_sheet: Optional CharacterSheet object for advanced validation
            
        Returns:
            Comprehensive validation results
        """
        results = {}
        all_issues = []
        all_warnings = []
        overall_valid = True
        
        # 1. Legacy validator
        if self.legacy_validator:
            try:
                legacy_result = self.legacy_validator.validate_full_character(character_data)
                results["legacy_validation"] = ValidationResult(
                    valid=legacy_result.get("valid", False),
                    issues=legacy_result.get("issues", []),
                    warnings=legacy_result.get("warnings", []),
                    validator_name="legacy"
                ).to_dict()
                
                all_issues.extend(legacy_result.get("issues", []))
                all_warnings.extend(legacy_result.get("warnings", []))
                overall_valid = overall_valid and legacy_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"Legacy validation failed: {e}")
                results["legacy_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Legacy validation error: {str(e)}"],
                    validator_name="legacy"
                ).to_dict()
                overall_valid = False
        
        # 2. Simplified validation (always run as baseline)
        try:
            simple_result = self.simplified_validator.validate_full_character(character_data)
            results["simplified_validation"] = ValidationResult(
                valid=simple_result.get("valid", False),
                issues=simple_result.get("issues", []),
                warnings=simple_result.get("warnings", []),
                validator_name="simplified"
            ).to_dict()
            
            # Only add issues if not already caught by legacy validator
            new_issues = [issue for issue in simple_result.get("issues", []) if issue not in all_issues]
            new_warnings = [warning for warning in simple_result.get("warnings", []) if warning not in all_warnings]
            
            all_issues.extend(new_issues)
            all_warnings.extend(new_warnings)
            overall_valid = overall_valid and simple_result.get("valid", False)
            
        except Exception as e:
            logger.error(f"Simplified validation failed: {e}")
            results["simplified_validation"] = ValidationResult(
                valid=False,
                issues=[f"Simplified validation error: {str(e)}"],
                validator_name="simplified"
            ).to_dict()
            overall_valid = False
        
        # 3. CreateRules validation (if character sheet available)
        if character_sheet:
            try:
                rules_validation = self.create_rules.validate_entire_character_sheet(character_sheet)
                
                rules_issues = [msg for valid, msg in rules_validation if not valid]
                rules_warnings = []  # CreateRules might not distinguish warnings
                
                results["rules_validation"] = ValidationResult(
                    valid=all(valid for valid, _ in rules_validation),
                    issues=rules_issues,
                    warnings=rules_warnings,
                    validator_name="create_rules"
                ).to_dict()
                
                # Add unique issues
                new_rules_issues = [issue for issue in rules_issues if issue not in all_issues]
                all_issues.extend(new_rules_issues)
                overall_valid = overall_valid and all(valid for valid, _ in rules_validation)
                
            except Exception as e:
                logger.error(f"CreateRules validation failed: {e}")
                results["rules_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Rules validation error: {str(e)}"],
                    validator_name="create_rules"
                ).to_dict()
                overall_valid = False
        else:
            logger.info("Character sheet not provided, skipping CreateRules validation")
        
        # 4. ValidationService (if available and character sheet provided)
        if self.validation_service and character_sheet:
            try:
                # Assuming ValidationService has a similar interface
                service_result = self.validation_service.validate_character(character_data)
                results["service_validation"] = ValidationResult(
                    valid=service_result.get("valid", False),
                    issues=service_result.get("issues", []),
                    warnings=service_result.get("warnings", []),
                    validator_name="validation_service"
                ).to_dict()
                
                # Add unique issues
                new_service_issues = [issue for issue in service_result.get("issues", []) if issue not in all_issues]
                new_service_warnings = [warning for warning in service_result.get("warnings", []) if warning not in all_warnings]
                
                all_issues.extend(new_service_issues)
                all_warnings.extend(new_service_warnings)
                overall_valid = overall_valid and service_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"ValidationService failed: {e}")
                results["service_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Service validation error: {str(e)}"],
                    validator_name="validation_service"
                ).to_dict()
                overall_valid = False
        
        # Compile final results
        total_validators = len([v for v in results.values() if v])
        passed_validators = len([v for v in results.values() if v and v.get("valid", False)])
        
        return {
            "overall_valid": overall_valid,
            "summary": {
                "total_issues": len(all_issues),
                "total_warnings": len(all_warnings),
                "validators_run": total_validators,
                "validators_passed": passed_validators,
                "validation_coverage": f"{passed_validators}/{total_validators}" if total_validators > 0 else "0/0"
            },
            "all_issues": all_issues,
            "all_warnings": all_warnings,
            "detailed_results": results,
            "recommendations": self._generate_recommendations(all_issues, all_warnings)
        }
    
    def validate_character_creation_step(self, step_name: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific step in character creation."""
        if step_name == "ability_scores":
            return self._validate_ability_scores(character_data.get("ability_scores", {}))
        elif step_name == "class_selection":
            return self._validate_class_selection(character_data.get("classes", {}))
        elif step_name == "equipment":
            return self._validate_equipment(character_data)
        else:
            # Default to full validation
            return self.validate_character(character_data)
    
    def _validate_ability_scores(self, ability_scores: Dict[str, int]) -> Dict[str, Any]:
        """Validate ability scores specifically."""
        issues = []
        warnings = []
        
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = ability_scores[ability]
                if score < 8:
                    warnings.append(f"{ability.title()} score ({score}) is very low")
                elif score > 18:
                    warnings.append(f"{ability.title()} score ({score}) is exceptionally high for starting character")
        
        total_score = sum(ability_scores.values())
        if total_score < 60:
            warnings.append(f"Total ability scores ({total_score}) are quite low")
        elif total_score > 90:
            warnings.append(f"Total ability scores ({total_score}) are very high")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "ability_scores"
        }
    
    def _validate_class_selection(self, classes: Dict[str, int]) -> Dict[str, Any]:
        """Validate class selection and levels."""
        issues = []
        warnings = []
        
        if not classes:
            issues.append("No classes selected")
        else:
            total_levels = sum(classes.values())
            if len(classes) > 1 and min(classes.values()) < 3:
                warnings.append("Multiclassing before level 3 may limit class features")
            
            for class_name, level in classes.items():
                if level < 1:
                    issues.append(f"Invalid level for {class_name}: {level}")
                elif level > 20:
                    issues.append(f"Class level too high for {class_name}: {level}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "class_selection"
        }
    
    def _validate_equipment(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate equipment selection."""
        issues = []
        warnings = []
        
        # Basic equipment validation
        weapons = character_data.get("weapons", [])
        armor = character_data.get("armor", {})
        
        if not weapons:
            warnings.append("No weapons equipped")
        
        if isinstance(armor, dict) and not armor.get("name"):
            warnings.append("No armor equipped")
        elif isinstance(armor, str) and not armor:
            warnings.append("No armor equipped")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "equipment"
        }
    
    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate helpful recommendations based on validation results."""
        recommendations = []
        
        if issues:
            recommendations.append("Fix all validation errors before finalizing character")
        
        if warnings:
            recommendations.append("Review warnings to ensure character meets your expectations")
        
        if not issues and not warnings:
            recommendations.append("Character validation passed! Ready for gameplay")
        
        # Specific recommendations based on common issues
        ability_issues = [issue for issue in issues if "ability" in issue.lower()]
        if ability_issues:
            recommendations.append("Consider using point buy or standard array for balanced ability scores")
        
        class_issues = [issue for issue in issues if "class" in issue.lower()]
        if class_issues:
            recommendations.append("Verify class selection meets multiclassing prerequisites")
        
        return recommendations
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate a human-readable validation summary."""
        if validation_result["overall_valid"]:
            return f"✅ Character validation passed ({validation_result['summary']['validation_coverage']} validators)"
        else:
            issues = len(validation_result["all_issues"])
            warnings = len(validation_result["all_warnings"])
            return f"❌ Character validation failed: {issues} issues, {warnings} warnings"


# Factory function for easy instantiation
def create_unified_validator() -> UnifiedCharacterValidator:
    """Create a unified validator with proper error handling."""
    try:
        return UnifiedCharacterValidator()
    except Exception as e:
        logger.error(f"Failed to create unified validator: {e}")
        # Return a minimal validator as fallback
        return UnifiedCharacterValidator()


# Convenience function for quick validation
def validate_character_quick(character_data: Dict[str, Any], 
                           character_sheet: Optional[CharacterSheet] = None) -> bool:
    """Quick validation that returns just True/False."""
    validator = create_unified_validator()
    result = validator.validate_character(character_data, character_sheet)
    return result["overall_valid"]