from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class AbilityScores(ABC):
    """
    Abstract base class defining the interface for handling character ability scores in D&D 5e (2024 Edition).
    
    This class establishes the contract for ability score operations according to the official rules.
    """
    
    # Core ability score names
    ABILITY_SCORES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    # Official ability score limits
    MIN_SCORE = 3  # Absolute minimum (per rules)
    MAX_SCORE = 20  # Maximum without magical enhancement
    MAX_SCORE_HARD_CAP = 30  # Absolute maximum with magical enhancement
    
    # Official point buy system parameters
    POINT_BUY_TOTAL = 27  # Standard point-buy budget
    POINT_BUY_MIN = 8     # Minimum score in point-buy
    POINT_BUY_MAX = 15    # Maximum score in point-buy
    
    @abstractmethod
    def calculate_modifier(self, score: int) -> int:
        """
        Calculate ability modifier based on score.
        
        Per D&D 2024 rules, modifier = floor((score - 10) / 2)
        
        Args:
            score: Ability score value
            
        Returns:
            int: Ability modifier
        """
        pass

    @abstractmethod
    def get_point_buy_cost(self, score: int) -> int:
        """
        Get the point-buy cost for a specific score.
        
        Per D&D 2024 rules:
        Score 8: 0 points
        Score 9: 1 point
        Score 10: 2 points
        Score 11: 3 points
        Score 12: 4 points
        Score 13: 5 points
        Score 14: 7 points
        Score 15: 9 points
        
        Args:
            score: The ability score to calculate cost for
            
        Returns:
            int: Point-buy cost
        """
        pass

    @abstractmethod
    def validate_ability_scores(self, scores_dict: Dict[str, int]) -> bool:
        """
        Validate ability scores against official rules.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def generate_standard_array(self) -> List[int]:
        """
        Return the standard ability score array.
        
        Per D&D 2024 rules, the standard array is [15, 14, 13, 12, 10, 8]
        
        Returns:
            List[int]: Standard array of ability scores
        """
        pass

    @abstractmethod
    def generate_random_scores(self) -> List[int]:
        """
        Generate random ability scores using 4d6 drop lowest method.
        
        Per D&D 2024 rules: Roll 4d6, drop the lowest die, sum the remaining three.
        Repeat six times to generate the six ability scores.
        
        Returns:
            List[int]: Randomly generated ability scores
        """
        pass

    @abstractmethod
    def apply_species_bonuses(self, scores_dict: Dict[str, int], species_bonuses: Dict[str, int]) -> Dict[str, int]:
        """
        Apply species bonuses to ability scores.
        
        Per D&D 2024 rules, species may provide specific ability score increases.
        
        Args:
            scores_dict: Current ability scores
            species_bonuses: Bonuses to apply
            
        Returns:
            Dict[str, int]: Updated ability scores with bonuses applied
        """
        pass
        
    @abstractmethod
    def calculate_total_point_buy_cost(self, scores_dict: Dict[str, int]) -> int:
        """
        Calculate the total point-buy cost for a set of ability scores.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            int: Total point-buy cost
        """
        pass
        
    @abstractmethod
    def apply_ability_score_improvement(self, scores_dict: Dict[str, int], improvements: Dict[str, int]) -> Dict[str, int]:
        """
        Apply Ability Score Improvements (ASI).
        
        Per D&D 2024 rules, ASIs typically allow +2 to one score and +1 to another,
        or +1 to three different scores, subject to the MAX_SCORE cap.
        
        Args:
            scores_dict: Current ability scores
            improvements: Improvements to apply (e.g., {"strength": 2, "constitution": 1})
            
        Returns:
            Dict[str, int]: Updated ability scores with improvements applied
        """
        pass
        
    @abstractmethod
    def get_all_modifiers(self, scores_dict: Dict[str, int]) -> Dict[str, int]:
        """
        Get all ability modifiers from scores.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            Dict[str, int]: Dictionary of ability modifiers
        """
        pass
        
    @abstractmethod
    def suggest_ability_score_distribution(self, character_class: str) -> Dict[str, int]:
        """
        Suggest an optimal ability score distribution for a specific class.
        
        Args:
            character_class: The character class to optimize for
            
        Returns:
            Dict[str, int]: Suggested ability score distribution
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

class AbstractAlignment(ABC):
    """
    Abstract base class defining the interface for character alignments in D&D 5e (2024 Edition).
    
    Alignments in D&D describe a character's moral and ethical outlook:
    - Law vs. Chaos (ethical axis): Attitude toward order, tradition, and rules
    - Good vs. Evil (moral axis): Attitude toward others' well-being and dignity
    
    The nine classic alignments are combinations of:
    - Lawful Good (LG): Organized compassion, honor-bound to help others
    - Neutral Good (NG): Pure altruism without preference for order or freedom
    - Chaotic Good (CG): Kindness through independence and freedom
    - Lawful Neutral (LN): Order and organization without moral judgment
    - True Neutral (N): Balance or ambivalence to moral/ethical extremes
    - Chaotic Neutral (CN): Freedom from both society's restrictions and moral expectations
    - Lawful Evil (LE): Structured and methodical in harming others or society
    - Neutral Evil (NE): Selfishness without particular attachment to freedom or laws
    - Chaotic Evil (CE): Destruction of both order and others' well-being
    
    Note: 2024 rules emphasize alignment as a guideline rather than a restriction,
    with no mechanical penalties for alignment choices or changes.
    """
    
    # Ethical axis options (Law vs. Chaos)
    ETHICAL_AXIS = ["lawful", "neutral", "chaotic"]
    
    # Moral axis options (Good vs. Evil)
    MORAL_AXIS = ["good", "neutral", "evil"]
    
    # Special case: True Neutral is represented as just "neutral"
    NEUTRAL_NEUTRAL = "neutral"
    
    @abstractmethod
    def get_all_alignments(self) -> List[Tuple[str, str]]:
        """
        Return a list of all available alignments according to the rules.
        
        Returns:
            List[Tuple[str, str]]: List of tuples (ethical, moral) representing all valid alignments
        """
        pass
        
    @abstractmethod
    def get_alignment_description(self, ethical: str, moral: str) -> str:
        """
        Get the official description of what an alignment represents.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            str: Official description of the alignment
        """
        pass
        
    @abstractmethod
    def validate_alignment(self, ethical: str, moral: str) -> bool:
        """
        Check if an alignment is valid according to the rules.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def is_compatible_with_deity(self, ethical: str, moral: str, deity_alignment: Tuple[str, str]) -> bool:
        """
        Check if an alignment is compatible with a deity's alignment.
        
        Per 2024 rules, certain deities may have alignment preferences or requirements.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            deity_alignment: Tuple (ethical, moral) representing deity's alignment
            
        Returns:
            bool: True if compatible, False otherwise
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ACCalculationMethod(Enum):
    """Enumeration of AC calculation methods in D&D 5e (2024 Edition)."""
    ARMOR_BASED = auto()       # AC from worn armor (+ DEX mod, limited by armor)
    UNARMORED = auto()         # Base 10 + DEX mod when wearing no armor
    UNARMORED_DEFENSE = auto() # Class features like Monk, Barbarian unarmored defense
    NATURAL_ARMOR = auto()     # Natural armor from species traits
    MAGE_ARMOR = auto()        # Magical effects like Mage Armor spell (13 + DEX mod)
    CUSTOM = auto()            # Custom or homebrew AC calculations

class ArmorCategory(Enum):
    """Armor categories in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto() 
    HEAVY = auto()
    SHIELD = auto()
    NATURAL = auto()
    MAGICAL = auto()

class AbstractArmorClass(ABC):
    """
    Abstract base class defining the contract for armor class (AC) calculation
    in D&D 5e (2024 Edition).
    
    Per D&D 2024 rules, armor class represents how difficult it is to land an
    effective blow on a character, with higher values being better. AC calculation
    can vary based on:
    - Armor worn
    - Shield use
    - Ability modifiers
    - Class features
    - Species traits
    - Magical effects
    """
    
    # Base AC values per D&D 2024 rules
    BASE_UNARMORED_AC = 10
    
    # Standard armor AC values (can be adjusted in implementation for specific items)
    STANDARD_ARMOR_VALUES = {
        # Light Armor
        "Padded": 11,
        "Leather": 11,
        "Studded Leather": 12,
        
        # Medium Armor
        "Hide": 12,
        "Chain Shirt": 13, 
        "Scale Mail": 14,
        "Breastplate": 14,
        "Half Plate": 15,
        
        # Heavy Armor
        "Ring Mail": 14,
        "Chain Mail": 16,
        "Splint": 17,
        "Plate": 18,
        
        # Shield
        "Shield": 2,  # Bonus added to base AC
    }
    
    # DEX modifier caps by armor type
    DEX_MODIFIER_CAPS = {
        ArmorCategory.LIGHT: None,    # No cap
        ArmorCategory.MEDIUM: 2,      # Maximum +2
        ArmorCategory.HEAVY: 0,       # No DEX bonus
        ArmorCategory.SHIELD: None,   # N/A for shields
    }
    
    @abstractmethod
    def calculate_ac(self) -> int:
        """
        Calculate the character's final armor class.
        
        Per D&D 2024 rules, this takes into account:
        - Base AC from armor or other sources
        - Applicable ability modifiers
        - Shield bonus (if any)
        - Magic item bonuses
        - Temporary effects
        - Cover bonuses (if in combat)
        
        Returns:
            int: Final armor class value
        """
        pass
    
    @abstractmethod
    def get_base_ac(self) -> int:
        """
        Get the character's base AC before modifiers.
        
        This varies based on the calculation method:
        - Armor: AC value of the armor
        - Unarmored: 10
        - Unarmored Defense (Monk): 10
        - Unarmored Defense (Barbarian): 10
        - Natural Armor: Species-specific value
        - Mage Armor: 13
        
        Returns:
            int: Base AC value
        """
        pass
    
    @abstractmethod
    def get_armor_ac(self, armor_name: str) -> int:
        """
        Get the base AC provided by a specific armor.
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            int: Base AC value of the armor
        """
        pass
    
    @abstractmethod
    def get_dex_modifier_cap(self, armor_category: ArmorCategory) -> Optional[int]:
        """
        Get the maximum DEX modifier allowed by an armor category.
        
        Per D&D 2024 rules:
        - Light armor: No cap
        - Medium armor: Max +2
        - Heavy armor: No DEX bonus (effectively +0 cap)
        
        Args:
            armor_category: Category of armor
            
        Returns:
            Optional[int]: Maximum allowed DEX modifier (None if no cap)
        """
        pass
    
    @abstractmethod
    def calculate_unarmored_ac(self, ability_scores: Dict[str, int]) -> int:
        """
        Calculate AC when wearing no armor.
        
        Per D&D 2024 rules:
        - Base 10 + DEX modifier
        
        Args:
            ability_scores: Character's ability scores
            
        Returns:
            int: Unarmored AC
        """
        pass
    
    @abstractmethod
    def calculate_armored_ac(self, armor_name: str, ability_scores: Dict[str, int]) -> int:
        """
        Calculate AC when wearing armor.
        
        Per D&D 2024 rules:
        - Light armor: Armor AC + DEX modifier
        - Medium armor: Armor AC + DEX modifier (max +2)
        - Heavy armor: Armor AC (no DEX modifier)
        
        Args:
            armor_name: Name of the armor worn
            ability_scores: Character's ability scores
            
        Returns:
            int: Armored AC
        """
        pass
    
    @abstractmethod
    def calculate_unarmored_defense_ac(self, class_name: str, ability_scores: Dict[str, int]) -> int:
        """
        Calculate AC using a class's Unarmored Defense feature.
        
        Per D&D 2024 rules:
        - Barbarian: 10 + DEX modifier + CON modifier
        - Monk: 10 + DEX modifier + WIS modifier
        
        Args:
            class_name: Name of the class providing Unarmored Defense
            ability_scores: Character's ability scores
            
        Returns:
            int: Unarmored Defense AC
        """
        pass
    
    @abstractmethod
    def calculate_mage_armor_ac(self, ability_scores: Dict[str, int]) -> int:
        """
        Calculate AC with the Mage Armor spell effect.
        
        Per D&D 2024 rules:
        - Mage Armor: 13 + DEX modifier
        
        Args:
            ability_scores: Character's ability scores
            
        Returns:
            int: Mage Armor AC
        """
        pass
    
    @abstractmethod
    def calculate_natural_armor_ac(self, natural_armor: int, ability_scores: Dict[str, int]) -> int:
        """
        Calculate AC using natural armor.
        
        Per D&D 2024 rules:
        - Natural Armor typically provides a base AC that may include DEX
        
        Args:
            natural_armor: Base natural armor value
            ability_scores: Character's ability scores
            
        Returns:
            int: Natural Armor AC
        """
        pass
    
    @abstractmethod
    def get_shield_bonus(self, shield_name: Optional[str] = None) -> int:
        """
        Get the AC bonus from a shield.
        
        Per D&D 2024 rules:
        - Standard shield: +2 AC
        - Magical shields may provide higher bonuses
        
        Args:
            shield_name: Name of the shield (None if using standard shield)
            
        Returns:
            int: Shield AC bonus
        """
        pass
    
    @abstractmethod
    def get_magic_item_ac_bonuses(self) -> Dict[str, int]:
        """
        Get AC bonuses from magic items.
        
        Examples in D&D 2024:
        - Ring of Protection: +1 AC
        - Cloak of Protection: +1 AC
        - Bracers of Defense: +2 AC (when not wearing armor or shield)
        - Magic armor: +1 to +3 to base armor AC
        
        Returns:
            Dict[str, int]: Magic item AC bonuses by item
        """
        pass
    
    @abstractmethod
    def get_cover_bonus(self, cover_type: str) -> int:
        """
        Get AC bonus from cover.
        
        Per D&D 2024 rules:
        - Half cover: +2 AC
        - Three-quarters cover: +5 AC
        - Total cover: Can't be targeted
        
        Args:
            cover_type: Type of cover
            
        Returns:
            int: Cover AC bonus
        """
        pass
    
    @abstractmethod
    def get_temporary_ac_modifiers(self) -> Dict[str, Tuple[int, int]]:
        """
        Get temporary AC modifiers from spells, features, etc.
        
        Examples in D&D 2024:
        - Shield spell: +5 AC until next turn
        - Haste spell: +2 AC for duration
        - Defensive Duelist feat: + proficiency bonus until next turn
        
        Returns:
            Dict[str, Tuple[int, int]]: Modifiers with (bonus, remaining rounds)
        """
        pass
    
    @abstractmethod
    def add_temporary_ac_modifier(self, name: str, bonus: int, duration: int) -> bool:
        """
        Add a temporary AC modifier.
        
        Args:
            name: Name of the effect
            bonus: AC bonus
            duration: Duration in rounds
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def remove_temporary_ac_modifier(self, name: str) -> bool:
        """
        Remove a temporary AC modifier.
        
        Args:
            name: Name of the effect
            
        Returns:
            bool: True if successfully removed
        """
        pass
    
    @abstractmethod
    def update_temporary_modifiers(self) -> Dict[str, int]:
        """
        Update durations of temporary modifiers (typically called at end of round).
        
        Returns:
            Dict[str, int]: Expired modifiers
        """
        pass
    
    @abstractmethod
    def get_best_ac_calculation_method(self, ability_scores: Dict[str, int]) -> ACCalculationMethod:
        """
        Determine the best AC calculation method for the character.
        
        Per D&D 2024 rules, when multiple methods are available:
        - Character uses whichever gives the highest AC
        - Some methods don't stack (e.g., can't combine Unarmored Defense with armor)
        
        Args:
            ability_scores: Character's ability scores
            
        Returns:
            ACCalculationMethod: Best calculation method
        """
        pass
    
    @abstractmethod
    def is_proficient_with_armor(self, armor_name: str) -> bool:
        """
        Check if character is proficient with a specific armor.
        
        Per D&D 2024 rules:
        - Non-proficient armor use imposes disadvantage on:
          * Ability checks, attack rolls, and saving throws using STR or DEX
          * Character can't cast spells
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            bool: True if proficient
        """
        pass
    
    @abstractmethod
    def get_armor_stealth_disadvantage(self, armor_name: str) -> bool:
        """
        Check if armor imposes disadvantage on Stealth checks.
        
        Per D&D 2024 rules:
        - Some medium and all heavy armor impose disadvantage on Stealth checks
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            bool: True if armor imposes disadvantage on Stealth
        """
        pass
    
    @abstractmethod
    def get_armor_strength_requirement(self, armor_name: str) -> Optional[int]:
        """
        Get minimum Strength score required for armor.
        
        Per D&D 2024 rules:
        - Some heavy armor requires minimum Strength to avoid speed reduction
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            Optional[int]: Minimum STR required (None if no requirement)
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AC data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of AC data
        """
        pass
    
    @abstractmethod
    def get_ac_breakdown(self) -> Dict[str, int]:
        """
        Get a breakdown of AC calculation components.
        
        Returns:
            Dict[str, int]: Each component's contribution to total AC
        """
        pass
    
    @abstractmethod
    def calculate_touch_ac(self) -> int:
        """
        Calculate touch AC (ignores armor).
        
        Some optional/legacy mechanics may use touch AC.
        
        Returns:
            int: Touch AC value
        """
        pass
    
    @abstractmethod
    def calculate_flat_footed_ac(self) -> int:
        """
        Calculate flat-footed AC (without DEX bonus).
        
        Some optional/legacy mechanics may use flat-footed AC.
        
        Returns:
            int: Flat-footed AC value
        """
        pass

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
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class AttackType(Enum):
    """Types of attacks in D&D 5e (2024 Edition)."""
    MELEE_WEAPON = auto()    # Melee weapon attacks
    RANGED_WEAPON = auto()   # Ranged weapon attacks
    MELEE_SPELL = auto()     # Melee spell attacks
    RANGED_SPELL = auto()    # Ranged spell attacks
    UNARMED = auto()         # Unarmed strikes
    IMPROVISED = auto()      # Improvised weapon attacks
    SPECIAL = auto()         # Special attack types (monster abilities, etc.)

class DamageType(Enum):
    """Damage types in D&D 5e (2024 Edition)."""
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

class DamageModifierType(Enum):
    """How damage is modified in D&D 5e (2024 Edition)."""
    NORMAL = auto()          # Normal damage
    RESISTANCE = auto()      # Half damage (rounded down)
    VULNERABILITY = auto()   # Double damage
    IMMUNITY = auto()        # No damage
    SPECIAL = auto()         # Special damage modification (e.g., Rage, Heavy Weapon Master)

class AbstractCombatStats(ABC):
    """
    Abstract base class for managing combat statistics in D&D 5e (2024 Edition).
    
    This class handles all combat-related calculations including:
    - Initiative
    - Attack rolls and modifiers
    - Damage calculations
    - Critical hits
    - Saving throws
    """
    
    # Standard combat constants
    STANDARD_CRITICAL_HIT_THRESHOLD = 20
    STANDARD_CRITICAL_MISS_THRESHOLD = 1
    STANDARD_ADVANTAGE_BONUS = 3.5  # Average statistical bonus from advantage
    
    @abstractmethod
    def calculate_initiative(self) -> int:
        """
        Calculate initiative bonus.
        
        Per D&D 2024 rules:
        - Base initiative is the Dexterity modifier
        - Some features add bonuses (Alert feat, etc.)
        - Some features allow using different abilities
        
        Returns:
            int: Initiative modifier
        """
        pass
    
    @abstractmethod
    def roll_initiative(self) -> int:
        """
        Roll initiative for combat.
        
        Per D&D 2024 rules:
        - d20 + initiative bonus
        
        Returns:
            int: Initiative roll result
        """
        pass
    
    @abstractmethod
    def get_attack_bonus(self, attack_type: AttackType, weapon_name: Optional[str] = None,
                      spell_name: Optional[str] = None) -> int:
        """
        Calculate attack bonus for a specific attack.
        
        Per D&D 2024 rules:
        - Weapon attacks: Ability modifier + proficiency (if proficient)
        - Spell attacks: Spellcasting ability + proficiency
        - Unarmed strikes: STR modifier + proficiency
        - Improvised: Ability modifier (typically no proficiency)
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            spell_name: Name of spell (for spell attacks)
            
        Returns:
            int: Total attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self) -> int:
        """
        Calculate spell attack bonus.
        
        Per D&D 2024 rules:
        - Spellcasting ability modifier + proficiency bonus
        
        Returns:
            int: Spell attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_spell_save_dc(self) -> int:
        """
        Calculate spell save DC.
        
        Per D&D 2024 rules:
        - 8 + spellcasting ability modifier + proficiency bonus
        
        Returns:
            int: Spell save DC
        """
        pass
    
    @abstractmethod
    def calculate_damage(self, attack_type: AttackType, weapon_name: Optional[str] = None,
                      spell_name: Optional[str] = None, spell_level: Optional[int] = None,
                      is_critical: bool = False) -> Dict[str, Any]:
        """
        Calculate damage for an attack.
        
        Per D&D 2024 rules:
        - Weapon damage die + ability modifier
        - Critical hits: Extra dice (typically double dice)
        - Spell damage based on spell and spell level
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            spell_name: Name of spell (for spell attacks)
            spell_level: Level spell is cast at (for spells)
            is_critical: Whether the attack is a critical hit
            
        Returns:
            Dict[str, Any]: Dictionary with damage details
        """
        pass
    
    @abstractmethod
    def determine_critical_threshold(self, attack_type: AttackType, 
                                  weapon_name: Optional[str] = None) -> int:
        """
        Determine critical hit threshold for an attack.
        
        Per D&D 2024 rules:
        - Standard: Natural 20
        - Some features modify this (Champion Fighter, Hexblade, etc.)
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            int: Minimum roll for a critical hit
        """
        pass
    
    @abstractmethod
    def calculate_critical_hit_damage(self, base_damage: Dict[DamageType, int], 
                                    attack_type: AttackType) -> Dict[DamageType, int]:
        """
        Calculate critical hit damage.
        
        Per D&D 2024 rules:
        - Roll all damage dice twice and add them together
        - Modifiers are not doubled
        - Some features add extra dice on crits
        
        Args:
            base_damage: Base damage by damage type
            attack_type: Type of attack
            
        Returns:
            Dict[DamageType, int]: Critical hit damage by damage type
        """
        pass
    
    @abstractmethod
    def calculate_saving_throw_bonus(self, ability: str) -> int:
        """
        Calculate bonus for a saving throw.
        
        Per D&D 2024 rules:
        - Base: Ability modifier
        - Add proficiency bonus if proficient
        - Some features add bonuses to specific saves
        
        Args:
            ability: Ability score (STR, DEX, CON, INT, WIS, CHA)
            
        Returns:
            int: Total saving throw bonus
        """
        pass
    
    @abstractmethod
    def has_advantage_on_attack(self, attack_type: AttackType, 
                             target_condition: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Check if character has advantage on an attack roll.
        
        Per D&D 2024 rules, advantage sources include:
        - Attacking a prone target (melee only)
        - Attacking an invisible target
        - Attacking with combat advantage (flanking, optional rule)
        - Attacking from hiding
        
        Args:
            attack_type: Type of attack
            target_condition: Conditions affecting the target
            
        Returns:
            Tuple[bool, str]: (Has advantage, reason)
        """
        pass
    
    @abstractmethod
    def has_disadvantage_on_attack(self, attack_type: AttackType, 
                                target_condition: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Check if character has disadvantage on an attack roll.
        
        Per D&D 2024 rules, disadvantage sources include:
        - Attacking while prone
        - Attacking an invisible target
        - Attacking at long range
        - Attacking while poisoned
        
        Args:
            attack_type: Type of attack
            target_condition: Conditions affecting the target
            
        Returns:
            Tuple[bool, str]: (Has disadvantage, reason)
        """
        pass
    
    @abstractmethod
    def get_damage_modifiers(self, damage_type: DamageType) -> DamageModifierType:
        """
        Get character's damage modifiers for a damage type.
        
        Per D&D 2024 rules:
        - Resistance: Half damage
        - Vulnerability: Double damage
        - Immunity: No damage
        
        Args:
            damage_type: Type of damage
            
        Returns:
            DamageModifierType: How damage is modified
        """
        pass
    
    @abstractmethod
    def apply_damage_modifiers(self, damage: Dict[DamageType, int]) -> Dict[DamageType, int]:
        """
        Apply resistances, vulnerabilities, etc. to damage.
        
        Args:
            damage: Raw damage by damage type
            
        Returns:
            Dict[DamageType, int]: Modified damage by damage type
        """
        pass
    
    @abstractmethod
    def get_weapon_properties(self, weapon_name: str) -> Dict[str, Any]:
        """
        Get properties of a weapon that affect combat.
        
        Per D&D 2024 rules, relevant properties include:
        - Damage die
        - Damage type
        - Range
        - Properties (finesse, heavy, light, two-handed, etc.)
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            Dict[str, Any]: Weapon properties
        """
        pass
    
    @abstractmethod
    def modify_attack_roll(self, base_roll: int, attack_type: AttackType, 
                        has_advantage: bool = False, 
                        has_disadvantage: bool = False) -> Dict[str, Any]:
        """
        Apply all modifiers to an attack roll.
        
        Args:
            base_roll: Base d20 roll
            attack_type: Type of attack
            has_advantage: Whether attack has advantage
            has_disadvantage: Whether attack has disadvantage
            
        Returns:
            Dict[str, Any]: Modified attack roll details
        """
        pass
    
    @abstractmethod
    def get_weapon_damage_die(self, weapon_name: str) -> str:
        """
        Get the damage die for a weapon.
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            str: Damage die (e.g., "1d8", "2d6")
        """
        pass
    
    @abstractmethod
    def get_ability_for_attack(self, attack_type: AttackType, 
                            weapon_name: Optional[str] = None) -> str:
        """
        Determine which ability modifier to use for an attack.
        
        Per D&D 2024 rules:
        - Melee weapons: STR by default, or DEX for finesse
        - Ranged weapons: DEX by default
        - Thrown weapons: STR for melee weapons, DEX for ranged
        - Spell attacks: Spellcasting ability
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            str: Ability to use (STR, DEX, etc.)
        """
        pass
    
    @abstractmethod
    def calculate_attack_damage_modifier(self, attack_type: AttackType, 
                                      weapon_name: Optional[str] = None) -> int:
        """
        Calculate ability modifier for damage.
        
        Per D&D 2024 rules:
        - Melee weapons: STR modifier
        - Ranged weapons: DEX modifier
        - Finesse weapons: STR or DEX (whichever used for attack)
        - Thrown weapons: Same as attack
        - Special cases: Great Weapon Fighting, Dueling style, etc.
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            int: Damage modifier
        """
        pass
    
    @abstractmethod
    def can_make_opportunity_attack(self) -> bool:
        """
        Check if character can make an opportunity attack.
        
        Per D&D 2024 rules:
        - Must have reaction available
        - Must not be incapacitated
        
        Returns:
            bool: True if can make opportunity attack
        """
        pass
    
    @abstractmethod
    def calculate_grapple_modifier(self) -> int:
        """
        Calculate modifier for grapple attempts.
        
        Per D&D 2024 rules:
        - Athletics (STR) check
        - Target contests with Athletics (STR) or Acrobatics (DEX)
        
        Returns:
            int: Grapple check modifier
        """
        pass
    
    @abstractmethod
    def calculate_shove_modifier(self) -> int:
        """
        Calculate modifier for shove attempts.
        
        Per D&D 2024 rules:
        - Athletics (STR) check
        - Target contests with Athletics (STR) or Acrobatics (DEX)
        
        Returns:
            int: Shove check modifier
        """
        pass
    
    @abstractmethod
    def get_special_attacks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get special attacks available to the character.
        
        Examples in D&D 2024:
        - Sneak Attack (Rogue)
        - Divine Smite (Paladin)
        - Flurry of Blows (Monk)
        - Extra Attack (Fighter, etc.)
        
        Returns:
            Dict[str, Dict[str, Any]]: Special attacks with details
        """
        pass
    
    @abstractmethod
    def get_weapon_attack_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all weapon attack options available to character.
        
        Returns:
            Dict[str, Dict[str, Any]]: Weapon attacks with details
        """
        pass
    
    @abstractmethod
    def get_spell_attack_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all spell attack options available to character.
        
        Returns:
            Dict[str, Dict[str, Any]]: Spell attacks with details
        """
        pass
    
    @abstractmethod
    def calculate_two_weapon_fighting_damage(self, main_hand_weapon: str, 
                                          off_hand_weapon: str) -> Dict[str, Any]:
        """
        Calculate damage for two-weapon fighting.
        
        Per D&D 2024 rules:
        - Off-hand weapon must have light property
        - No ability modifier to damage unless Two-Weapon Fighting style
        
        Args:
            main_hand_weapon: Main hand weapon name
            off_hand_weapon: Off-hand weapon name
            
        Returns:
            Dict[str, Any]: Two-weapon fighting damage details
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert combat stats to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of combat stats
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class Condition(Enum):
    """Standard conditions in D&D 5e (2024 Edition)."""
    BLINDED = auto()       # Can't see, auto-fail checks that need sight, attack rolls have disadvantage, attacks against have advantage
    CHARMED = auto()       # Can't attack charmer, charmer has advantage on social checks against creature
    DEAFENED = auto()      # Can't hear, auto-fail checks that need hearing
    FRIGHTENED = auto()    # Disadvantage on ability checks/attacks while source of fear in sight, can't willingly move closer to source
    GRAPPLED = auto()      # Speed is 0, ends if grappler incapacitated or separated from target
    INCAPACITATED = auto() # Can't take actions or reactions
    INVISIBLE = auto()     # Unseen (unless perceived by special means), attack rolls have advantage, attacks against have disadvantage
    PARALYZED = auto()     # Incapacitated, auto-fail STR/DEX saves, attacks have advantage, auto-crit if attacker within 5 feet
    PETRIFIED = auto()     # Transformed to stone, incapacitated, unaware of surroundings, 10× weight, doesn't age, resistance to all damage
    POISONED = auto()      # Disadvantage on attack rolls and ability checks
    PRONE = auto()         # Can only crawl, disadvantage on attack rolls, melee attacks against have advantage, ranged attacks against have disadvantage
    RESTRAINED = auto()    # Speed is 0, attack rolls have disadvantage, attacks against have advantage, disadvantage on DEX saves
    STUNNED = auto()       # Incapacitated, can't move, auto-fail STR/DEX saves, attack rolls against have advantage
    UNCONSCIOUS = auto()   # Incapacitated, can't move/speak, unaware of surroundings, drop everything, fall prone, auto-fail STR/DEX saves, attacks have advantage, auto-crit if attacker within 5 feet

class DeathSaveResult(Enum):
    """Possible results of a death saving throw."""
    SUCCESS = auto()       # Standard success (3 needed to stabilize)
    FAILURE = auto()       # Standard failure (3 causes death)
    CRITICAL_SUCCESS = auto()  # Natural 20: regain 1 HP immediately
    CRITICAL_FAILURE = auto()  # Natural 1: counts as two failures

class ConcentrationBreakResult(Enum):
    """Results of a concentration check when taking damage."""
    MAINTAINED = auto()    # Successfully maintained concentration
    BROKEN = auto()        # Lost concentration on the spell
    SPECIAL_MAINTENANCE = auto()  # Maintained through special ability (e.g., War Caster feat)

class AbstractConditions(ABC):
    """
    Abstract base class for managing conditions, death saves, exhaustion,
    and concentration in D&D 5e (2024 Edition).
    
    Conditions are temporary afflictions that alter a creature's capabilities.
    """
    
    # DC for concentration checks is 10 or half the damage taken, whichever is higher
    BASE_CONCENTRATION_DC = 10
    
    # Exhaustion now provides a -1 penalty to d20 tests per level in 2024 rules (maximum 10)
    MAX_EXHAUSTION_LEVEL = 10
    
    # Death saving throw DC
    DEATH_SAVE_DC = 10
    
    @abstractmethod
    def apply_condition(self, condition: Condition, duration: Optional[int] = None, 
                       source: Optional[str] = None) -> bool:
        """
        Apply a condition to the character.
        
        Per D&D 2024 rules, most conditions:
        - Have specific mechanical effects 
        - May have a duration (in rounds, minutes, etc.)
        - May be caused by specific sources (spells, monster abilities, etc.)
        
        Args:
            condition: Condition to apply
            duration: Duration in rounds (None for indefinite)
            source: Source of the condition
            
        Returns:
            bool: True if condition was successfully applied
        """
        pass
    
    @abstractmethod
    def remove_condition(self, condition: Condition) -> bool:
        """
        Remove a condition from the character.
        
        Per D&D 2024 rules, conditions can be removed by:
        - Spells like Lesser Restoration, Greater Restoration
        - Abilities that specifically remove conditions
        - Ending effects that caused the condition
        - Duration expiration
        
        Args:
            condition: Condition to remove
            
        Returns:
            bool: True if condition was successfully removed
        """
        pass
    
    @abstractmethod
    def has_condition(self, condition: Condition) -> bool:
        """
        Check if character has a specific condition.
        
        Args:
            condition: Condition to check
            
        Returns:
            bool: True if character has the condition
        """
        pass
    
    @abstractmethod
    def get_all_conditions(self) -> Dict[Condition, Dict[str, Any]]:
        """
        Get all conditions affecting the character.
        
        Returns:
            Dict[Condition, Dict[str, Any]]: All active conditions with their details
                including duration, source, etc.
        """
        pass
    
    @abstractmethod
    def is_immune_to_condition(self, condition: Condition) -> bool:
        """
        Check if character is immune to a specific condition.
        
        Per D&D 2024 rules:
        - Some species are immune to specific conditions
        - Some class features grant condition immunities
        - Some spells/items grant temporary condition immunities
        
        Args:
            condition: Condition to check
            
        Returns:
            bool: True if character is immune to the condition
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> Set[Condition]:
        """
        Get all conditions the character is immune to.
        
        Returns:
            Set[Condition]: All condition immunities
        """
        pass
    
    @abstractmethod
    def update_condition_durations(self) -> Dict[Condition, bool]:
        """
        Update durations for all timed conditions (typically at end of turn).
        
        Returns:
            Dict[Condition, bool]: Conditions that expired during this update
        """
        pass
    
    @abstractmethod
    def add_exhaustion_level(self, levels: int = 1) -> int:
        """
        Add levels of exhaustion to the character.
        
        Per D&D 2024 rules:
        - Each level of exhaustion gives -1 penalty to d20 tests
        - At level 10, the character dies
        - Causes: Forced march, extreme environments, some spells, etc.
        
        Args:
            levels: Number of exhaustion levels to add
            
        Returns:
            int: New exhaustion level
        """
        pass
    
    @abstractmethod
    def remove_exhaustion_level(self, levels: int = 1) -> int:
        """
        Remove levels of exhaustion from the character.
        
        Per D&D 2024 rules:
        - A long rest reduces exhaustion level by 1
        - Spells like Greater Restoration remove one level
        - The Periapt of Health prevents exhaustion
        
        Args:
            levels: Number of exhaustion levels to remove
            
        Returns:
            int: New exhaustion level
        """
        pass
    
    @abstractmethod
    def get_exhaustion_level(self) -> int:
        """
        Get the character's current exhaustion level.
        
        Returns:
            int: Current exhaustion level (0-10)
        """
        pass
    
    @abstractmethod
    def get_exhaustion_penalty(self) -> int:
        """
        Get the penalty applied to d20 tests due to exhaustion.
        
        Per D&D 2024 rules:
        - Each level of exhaustion gives a -1 penalty to d20 tests
        - This includes attack rolls, saving throws, and ability checks
        
        Returns:
            int: Penalty to d20 tests (negative number)
        """
        pass
    
    @abstractmethod
    def roll_death_saving_throw(self) -> DeathSaveResult:
        """
        Roll a death saving throw.
        
        Per D&D 2024 rules:
        - Roll d20, no modifiers (unless from features like Blessing of the Dawn)
        - 10 or higher: success
        - 9 or lower: failure
        - Natural 20: regain 1 hit point
        - Natural 1: two failures
        - Three successes: become stable
        - Three failures: die
        
        Returns:
            DeathSaveResult: Result of the death save
        """
        pass
    
    @abstractmethod
    def get_death_save_count(self) -> Dict[str, int]:
        """
        Get current death saving throw success/failure counts.
        
        Returns:
            Dict[str, int]: Dictionary with:
                - "successes": Number of successes
                - "failures": Number of failures
        """
        pass
    
    @abstractmethod
    def reset_death_saves(self) -> None:
        """
        Reset death saving throw counts.
        
        This happens when:
        - Character regains any hit points
        - Character stabilizes
        - Character dies
        """
        pass
    
    @abstractmethod
    def is_stable(self) -> bool:
        """
        Check if an unconscious character is stable.
        
        Per D&D 2024 rules:
        - Stable characters don't need to make death saves
        - They remain unconscious for 1d4 hours
        - Or until they regain hit points
        
        Returns:
            bool: True if stable
        """
        pass
    
    @abstractmethod
    def stabilize(self) -> bool:
        """
        Stabilize a dying character.
        
        Per D&D 2024 rules, stabilization can occur from:
        - Three death save successes
        - Medicine check (DC 10)
        - Spare the Dying cantrip
        - Healer's kit
        
        Returns:
            bool: True if successfully stabilized
        """
        pass
    
    @abstractmethod
    def make_concentration_check(self, damage_taken: int) -> ConcentrationBreakResult:
        """
        Make a concentration check after taking damage.
        
        Per D&D 2024 rules:
        - DC equals 10 or half the damage taken, whichever is higher
        - It's a Constitution saving throw
        - War Caster feat gives advantage
        
        Args:
            damage_taken: Amount of damage that triggered the check
            
        Returns:
            ConcentrationBreakResult: Result of the concentration check
        """
        pass
    
    @abstractmethod
    def break_concentration(self) -> Dict[str, Any]:
        """
        Force break concentration on any concentration spells.
        
        Per D&D 2024 rules, concentration breaks when:
        - Character casts another concentration spell
        - Character takes damage and fails the save
        - Character is incapacitated or killed
        - Character is subject to an effect that breaks concentration
        
        Returns:
            Dict[str, Any]: Details of the broken concentration effect
        """
        pass
    
    @abstractmethod
    def is_concentrating(self) -> bool:
        """
        Check if character is currently concentrating on a spell.
        
        Returns:
            bool: True if concentrating
        """
        pass
    
    @abstractmethod
    def get_concentration_details(self) -> Dict[str, Any]:
        """
        Get details about what the character is concentrating on.
        
        Returns:
            Dict[str, Any]: Details of the concentration spell/effect
        """
        pass
    
    @abstractmethod
    def start_concentrating(self, spell_name: str, spell_level: int, duration: int) -> bool:
        """
        Start concentrating on a new spell.
        
        Per D&D 2024 rules:
        - This automatically breaks concentration on any previous spell
        
        Args:
            spell_name: Name of the spell
            spell_level: Level the spell is cast at
            duration: Duration in rounds
            
        Returns:
            bool: True if successfully started concentrating
        """
        pass
    
    @abstractmethod
    def get_condition_effects(self, condition: Condition) -> Dict[str, Any]:
        """
        Get mechanical effects of a specific condition.
        
        Args:
            condition: Condition to check
            
        Returns:
            Dict[str, Any]: Mechanical effects of the condition
        """
        pass
    
    @abstractmethod
    def apply_damage_to_dying(self, damage: int) -> Dict[str, Any]:
        """
        Apply damage to a character at 0 HP.
        
        Per D&D 2024 rules:
        - Any damage causes a death saving throw failure
        - Critical hits cause two failures
        - Damage equal to max HP causes instant death
        
        Args:
            damage: Amount of damage taken
            
        Returns:
            Dict[str, Any]: Results of applying the damage
        """
        pass
    
    @abstractmethod
    def heal_from_dying(self, healing: int) -> Dict[str, Any]:
        """
        Apply healing to a dying character.
        
        Per D&D 2024 rules:
        - Any healing brings character back to consciousness with that HP
        - Resets death saving throws
        - Removes the unconscious condition
        
        Args:
            healing: Amount of healing received
            
        Returns:
            Dict[str, Any]: Results of the healing
        """
        pass
    
    @abstractmethod
    def get_conditional_modifiers(self) -> Dict[str, int]:
        """
        Get all modifiers to rolls caused by conditions.
        
        For example:
        - Poisoned: Disadvantage on attack rolls and ability checks
        - Prone: Disadvantage on attack rolls, etc.
        
        Returns:
            Dict[str, int]: Dictionary of roll types and their modifiers
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert condition data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of conditions
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
from typing import Dict, List, Optional, Union, Any, Tuple

class ExperienceSource(Enum):
    """Enumeration of experience point sources in D&D 5e (2024 Edition)."""
    COMBAT = auto()           # Combat encounters
    QUEST = auto()            # Completing quests/objectives
    ROLEPLAY = auto()         # Good roleplaying
    MILESTONE = auto()        # Story milestone achievements
    PUZZLE = auto()           # Solving puzzles
    EXPLORATION = auto()      # Discovering new areas or lore
    TRAINING = auto()         # Dedicated training during downtime
    CRAFTING = auto()         # Creating items
    RESEARCH = auto()         # Discovering knowledge
    OTHER = auto()            # Miscellaneous sources

class AdvancementMethod(Enum):
    """Enumeration of character advancement methods in D&D 5e (2024 Edition)."""
    EXPERIENCE_POINTS = auto()  # Traditional XP tracking
    MILESTONE = auto()          # Level up at story milestones
    TRAINING = auto()           # Combined XP and downtime training
    MIXED = auto()              # Combination of methods

class DowntimeActivity(Enum):
    """Enumeration of downtime activities in D&D 5e (2024 Edition)."""
    CRAFTING = auto()           # Creating items
    TRAINING = auto()           # Learning new skills or abilities
    CAROUSING = auto()          # Making social contacts
    RESEARCH = auto()           # Acquiring knowledge
    WORK = auto()               # Earning money
    CRIME = auto()              # Illegal activities
    RELIGIOUS_SERVICE = auto()  # Serving a deity or organization
    PIT_FIGHTING = auto()       # Participating in combat sports
    RECUPERATING = auto()       # Recovering from injuries or conditions
    SELLING_MAGIC_ITEMS = auto()  # Finding buyers for magic items
    BUYING_MAGIC_ITEMS = auto()   # Finding sellers of magic items
    SCRIBING_SPELLS = auto()      # Copying spells into a spellbook
    CUSTOM = auto()              # Custom activities

class AbstractExperience(ABC):
    """
    Abstract base class defining the contract for character experience and advancement
    in D&D 5e (2024 Edition).
    
    This class handles all aspects of character advancement including:
    - Experience point tracking and calculation
    - Level determination based on XP thresholds
    - Milestone-based advancement
    - Downtime activities and their benefits
    """
    
    # Official XP thresholds for each level as per D&D 2024 rules
    XP_THRESHOLDS = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000,
        11: 85000,
        12: 100000,
        13: 120000,
        14: 140000,
        15: 165000,
        16: 195000,
        17: 225000,
        18: 265000,
        19: 305000,
        20: 355000
    }
    
    # Challenge Rating to XP conversion table
    CR_TO_XP = {
        0: 10,
        1/8: 25,
        1/4: 50,
        1/2: 100,
        1: 200,
        2: 450,
        3: 700,
        4: 1100,
        5: 1800,
        6: 2300,
        7: 2900,
        8: 3900,
        9: 5000,
        10: 5900,
        11: 7200,
        12: 8400,
        13: 10000,
        14: 11500,
        15: 13000,
        16: 15000,
        17: 18000,
        18: 20000,
        19: 22000,
        20: 25000,
        21: 33000,
        22: 41000,
        23: 50000,
        24: 62000,
        25: 75000,
        26: 90000,
        27: 105000,
        28: 120000,
        29: 135000,
        30: 155000
    }
    
    # XP multipliers based on number of monsters (2024 rules)
    ENCOUNTER_XP_MULTIPLIERS = {
        1: 1.0,
        2: 1.5,
        3: 2.0,
        4: 2.0,
        5: 2.0,
        6: 2.0,
        7: 2.5,
        8: 2.5,
        9: 2.5,
        10: 2.5,
        11: 3.0,
        12: 3.0,
        13: 3.0,
        14: 3.0,
        15: 4.0
    }
    
    @abstractmethod
    def get_current_xp(self) -> int:
        """
        Get the character's current XP total.
        
        Returns:
            int: Current XP
        """
        pass
    
    @abstractmethod
    def get_current_level(self) -> int:
        """
        Get the character's current level based on XP or milestones.
        
        Per D&D 2024 rules, this is determined by:
        - For XP-based: Comparing current XP to the XP_THRESHOLDS
        - For milestone-based: The level granted by story progress
        
        Returns:
            int: Current character level (1-20)
        """
        pass
    
    @abstractmethod
    def get_advancement_method(self) -> AdvancementMethod:
        """
        Get the character's current advancement method.
        
        Returns:
            AdvancementMethod: Current advancement method
        """
        pass
    
    @abstractmethod
    def set_advancement_method(self, method: AdvancementMethod) -> bool:
        """
        Set the character's advancement method.
        
        Per D&D 2024 rules, DMs may choose between XP-based or milestone-based advancement.
        
        Args:
            method: The advancement method to use
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def add_xp(self, amount: int, source: ExperienceSource = ExperienceSource.OTHER) -> int:
        """
        Add XP to the character from a specified source.
        
        Args:
            amount: Amount of XP to add
            source: Source of the XP
            
        Returns:
            int: New XP total
        """
        pass
    
    @abstractmethod
    def check_level_up(self) -> Tuple[bool, Optional[int]]:
        """
        Check if the character has enough XP to level up.
        
        Returns:
            Tuple[bool, Optional[int]]: (Can level up, New level if applicable)
        """
        pass
    
    @abstractmethod
    def apply_milestone(self) -> Tuple[bool, int]:
        """
        Apply a milestone advancement to the character.
        
        Per D&D 2024 rules, milestone advancement grants a level when significant
        story goals are achieved, regardless of XP accumulated.
        
        Returns:
            Tuple[bool, int]: (Success, New level)
        """
        pass
    
    @abstractmethod
    def get_xp_to_next_level(self) -> int:
        """
        Get XP needed to reach the next level.
        
        Returns:
            int: XP needed
        """
        pass
    
    @abstractmethod
    def get_xp_for_encounter(self, monster_crs: List[float], party_size: int) -> int:
        """
        Calculate total XP award for an encounter.
        
        Per D&D 2024 rules:
        1. Sum base XP values for all monsters
        2. Apply multiplier based on number of monsters
        3. Divide by number of party members
        
        Args:
            monster_crs: List of monster Challenge Ratings
            party_size: Number of characters in the party
            
        Returns:
            int: XP to award to each character
        """
        pass
    
    @abstractmethod
    def get_encounter_difficulty(self, monster_crs: List[float], party_levels: List[int]) -> str:
        """
        Calculate the difficulty of an encounter.
        
        Per D&D 2024 rules, encounters are categorized as:
        - Easy
        - Medium
        - Hard
        - Deadly
        
        Args:
            monster_crs: List of monster Challenge Ratings
            party_levels: List of party member levels
            
        Returns:
            str: Difficulty rating
        """
        pass
    
    @abstractmethod
    def get_xp_history(self) -> Dict[str, Any]:
        """
        Get the character's XP history.
        
        Returns:
            Dict[str, Any]: XP by source and session
        """
        pass
    
    @abstractmethod
    def reset_xp(self) -> bool:
        """
        Reset the character's XP to 0 (level 1).
        
        Returns:
            bool: True if successfully reset
        """
        pass
    
    @abstractmethod
    def get_available_downtime_activities(self) -> Dict[DowntimeActivity, Dict[str, Any]]:
        """
        Get all downtime activities available to the character.
        
        Per D&D 2024 rules, available downtime activities may depend on:
        - Character level
        - Location
        - Character proficiencies and abilities
        - Faction memberships
        
        Returns:
            Dict[DowntimeActivity, Dict[str, Any]]: Available activities with details
        """
        pass
    
    @abstractmethod
    def perform_downtime_activity(self, activity: DowntimeActivity, days: int, **kwargs) -> Dict[str, Any]:
        """
        Perform a downtime activity.
        
        Per D&D 2024 rules, downtime activities:
        - Take a specific number of days
        - May require ability checks
        - Can provide various benefits (money, items, contacts, etc.)
        - May involve complications
        
        Args:
            activity: The downtime activity to perform
            days: Number of days spent
            **kwargs: Additional parameters for the activity
            
        Returns:
            Dict[str, Any]: Results of the activity
        """
        pass
    
    @abstractmethod
    def get_downtime_training_options(self) -> Dict[str, Any]:
        """
        Get training options available during downtime.
        
        Per D&D 2024 rules, characters can train to gain:
        - Tool proficiencies
        - Language proficiencies
        - Skill proficiencies (with DM approval)
        
        Training typically requires:
        - Time (at least 10 workweeks)
        - Money (at least 250 gp)
        - A suitable teacher
        
        Returns:
            Dict[str, Any]: Available training options
        """
        pass
    
    @abstractmethod
    def train_proficiency(self, proficiency_type: str, specific_proficiency: str, 
                       weeks: int, cost: int) -> bool:
        """
        Train to gain a new proficiency during downtime.
        
        Args:
            proficiency_type: Type of proficiency (skill, tool, language)
            specific_proficiency: The specific proficiency to learn
            weeks: Workweeks spent training
            cost: Gold cost of training
            
        Returns:
            bool: True if training was successful
        """
        pass
    
    @abstractmethod
    def get_crafting_options(self) -> Dict[str, Any]:
        """
        Get available crafting options.
        
        Per D&D 2024 rules:
        - Crafting requires appropriate tool proficiency
        - Item cost and rarity determine time required
        - Special materials may be needed for certain items
        
        Returns:
            Dict[str, Any]: Available crafting options
        """
        pass
    
    @abstractmethod
    def craft_item(self, item_name: str, days: int, cost: int, **kwargs) -> Dict[str, Any]:
        """
        Craft an item during downtime.
        
        Per D&D 2024 rules:
        - Character must be proficient with appropriate tools
        - Basic crafting: 5 gp of progress per day
        - Magic items have special requirements
        
        Args:
            item_name: Name of the item to craft
            days: Days spent crafting
            cost: Material cost
            **kwargs: Additional crafting parameters
            
        Returns:
            Dict[str, Any]: Result of crafting
        """
        pass
    
    @abstractmethod
    def get_research_topics(self) -> List[str]:
        """
        Get available research topics.
        
        Per D&D 2024 rules, research might:
        - Uncover lore about magical items
        - Reveal monster weaknesses
        - Provide historical information
        - Discover spell scrolls
        
        Returns:
            List[str]: Available research topics
        """
        pass
    
    @abstractmethod
    def research_topic(self, topic: str, days: int, cost: int) -> Dict[str, Any]:
        """
        Research a topic during downtime.
        
        Args:
            topic: Topic to research
            days: Days spent researching
            cost: Cost of research (library access, materials, etc.)
            
        Returns:
            Dict[str, Any]: Research results
        """
        pass
    
    @abstractmethod
    def get_xp_for_downtime(self, activity: DowntimeActivity, days: int, success: bool) -> int:
        """
        Calculate XP gained from downtime activities (if applicable).
        
        Some DMs award XP for significant downtime accomplishments.
        
        Args:
            activity: The activity performed
            days: Days spent
            success: Whether the activity was successful
            
        Returns:
            int: XP awarded (0 if none)
        """
        pass
    
    @abstractmethod
    def milestone_progress(self) -> Dict[str, Any]:
        """
        Get information about milestone progression.
        
        For milestone-based advancement, this tracks:
        - Completed story milestones
        - Current objectives
        - Progress toward next level
        
        Returns:
            Dict[str, Any]: Milestone progress information
        """
        pass
    
    @abstractmethod
    def predict_levels_by_sessions(self, avg_xp_per_session: int, sessions: int) -> Dict[int, int]:
        """
        Predict future levels based on average XP per session.
        
        A planning tool for DMs and players.
        
        Args:
            avg_xp_per_session: Average XP earned per session
            sessions: Number of future sessions
            
        Returns:
            Dict[int, int]: Mapping of session numbers to predicted levels
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert experience data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of experience data
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
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class GroupCheckMethod(Enum):
    """Methods for resolving group checks in D&D 5e (2024 Edition)."""
    MAJORITY = auto()        # Succeeds if majority of characters succeed
    AVERAGE = auto()         # Uses the average result of all checks
    BEST = auto()            # Uses the best individual result
    WORST = auto()           # Uses the worst individual result
    ASSISTED = auto()        # One character rolls with advantage from others

class GroupActivity(Enum):
    """Group activities in D&D 5e (2024 Edition)."""
    TRAVEL = auto()          # Overland travel
    EXPLORATION = auto()     # Searching a dungeon/area
    SOCIAL = auto()          # Group social interaction
    COMBAT = auto()          # Group combat tactics
    RESTING = auto()         # Group resting
    DOWNTIME = auto()        # Group downtime activities

class HelpActionType(Enum):
    """Types of help action in D&D 5e (2024 Edition)."""
    ABILITY_CHECK = auto()   # Help with ability checks (gives advantage)
    ATTACK = auto()          # Help with attack rolls (gives advantage)
    OTHER = auto()           # Other uses of the help action

class PartyRole(Enum):
    """Common party roles in D&D 5e (2024 Edition)."""
    TANK = auto()            # Absorbs damage, protects others
    STRIKER = auto()         # Deals high damage
    CONTROLLER = auto()      # Affects battlefield/multiple enemies
    SUPPORT = auto()         # Healing and buffs
    FACE = auto()            # Social interactions
    SCOUT = auto()           # Exploration and reconnaissance
    UTILITY = auto()         # Problem solving and special abilities

class AbstractGroupMechanics(ABC):
    """
    Abstract base class for group mechanics in D&D 5e (2024 Edition).
    
    This class handles all interactions between multiple characters including:
    - Group ability checks
    - Help action
    - Flanking and other tactical positioning
    - Shared resources
    - Party roles and synergies
    - Travel and exploration as a group
    """
    
    # Standard distances for group-related mechanics
    GROUP_VISIBILITY_DISTANCE = 60  # Standard distance in feet for group visibility
    CLOSE_FORMATION_DISTANCE = 10   # Distance in feet for close formation
    FLANKING_DISTANCE = 5           # Distance in feet for flanking
    
    @abstractmethod
    def perform_group_check(self, check_type: str, 
                         character_results: Dict[str, int], 
                         method: GroupCheckMethod = GroupCheckMethod.MAJORITY) -> Tuple[bool, int]:
        """
        Resolve a group ability check.
        
        Per D&D 2024 rules:
        - Group checks are used when multiple characters attempt something together
        - Success is determined by the group as a whole, not individuals
        - Standard method: Success if at least half the group succeeds
        - Used for: Stealth, Perception, Survival during travel, etc.
        
        Args:
            check_type: The type of check being performed
            character_results: Dictionary mapping character names to check results
            method: Method to determine group success
            
        Returns:
            Tuple[bool, int]: (Success, total/average result)
        """
        pass
    
    @abstractmethod
    def provide_help_action(self, helper_name: str, target_name: str, 
                         action_type: HelpActionType, task: str) -> Tuple[bool, str]:
        """
        Provide help action to another character.
        
        Per D&D 2024 rules:
        - Helper must be able to attempt the task alone
        - Must be within 5 feet for helping with attacks
        - Gives advantage on the ability check/attack roll
        - Uses the helper's action
        
        Args:
            helper_name: Character providing help
            target_name: Character receiving help
            action_type: Type of help being provided
            task: Specific task/check being helped with
            
        Returns:
            Tuple[bool, str]: (Success, description)
        """
        pass
    
    @abstractmethod
    def check_flanking(self, attacker1_name: str, attacker2_name: str, 
                     target_name: str, positions: Dict[str, Tuple[int, int]]) -> bool:
        """
        Check if creatures are flanking a target (optional rule).
        
        Per D&D 2024 rules (optional):
        - Attackers must be on opposite sides of the target
        - Both must be within 5 feet of the target
        - Neither can be incapacitated
        - Grants advantage on melee attack rolls
        
        Args:
            attacker1_name: First attacker
            attacker2_name: Second attacker
            target_name: Target being flanked
            positions: Dictionary mapping character names to (x,y) coordinates
            
        Returns:
            bool: True if flanking is achieved
        """
        pass
    
    @abstractmethod
    def share_resource(self, source_name: str, target_name: str, 
                     resource_type: str, amount: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Share a resource between characters.
        
        Per D&D 2024 guidelines:
        - Some items can be shared during play (healing potions, etc.)
        - Typically requires an action or interaction
        - Must be within reach of each other
        
        Args:
            source_name: Character sharing the resource
            target_name: Character receiving the resource
            resource_type: Type of resource being shared
            amount: Amount of resource to share
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, details of shared resource)
        """
        pass
    
    @abstractmethod
    def coordinate_group_travel(self, characters: List[str], 
                             travel_pace: str, 
                             roles: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Coordinate group travel.
        
        Per D&D 2024 rules:
        - Group travel pace (slow, normal, fast) affects stealth, perception
        - Characters can take specific roles during travel
        - Travel pace determines distance covered per day
        
        Args:
            characters: List of character names
            travel_pace: Pace of travel (slow, normal, fast)
            roles: Dictionary mapping roles to lists of character names
            
        Returns:
            Dict[str, Any]: Results of travel (distance, encounters, etc.)
        """
        pass
    
    @abstractmethod
    def manage_group_marching_order(self, characters: List[str], 
                                 formation: str) -> Dict[str, Tuple[int, int]]:
        """
        Manage the group's marching order.
        
        Per D&D 2024 guidelines:
        - Typical formations: Single file, two abreast, defensive, etc.
        - Affects surprise, opportunity for detection, etc.
        - Important for dungeon corridors and similar confined spaces
        
        Args:
            characters: List of character names
            formation: Type of formation
            
        Returns:
            Dict[str, Tuple[int, int]]: Positions of each character
        """
        pass
    
    @abstractmethod
    def distribute_loot(self, items: Dict[str, Any], 
                      characters: List[str]) -> Dict[str, List[str]]:
        """
        Assist with distributing loot among characters.
        
        Per D&D 2024 guidelines:
        - Track what items go to which characters
        - Optional methods: Even split, role-based, need-based
        - Includes gold, items, and other valuables
        
        Args:
            items: Dictionary of items to distribute
            characters: List of character names
            
        Returns:
            Dict[str, List[str]]: Distribution of items to characters
        """
        pass
    
    @abstractmethod
    def calculate_party_carrying_capacity(self, characters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate the party's total carrying capacity.
        
        Per D&D 2024 rules:
        - Based on Strength scores of all characters
        - Affected by magic items (Bags of Holding, etc.)
        - Different movement penalties at different thresholds
        
        Args:
            characters: Dictionary mapping character names to their details
            
        Returns:
            Dict[str, Any]: Carrying capacity details
        """
        pass
    
    @abstractmethod
    def set_watch_rotation(self, characters: List[str], 
                        rest_duration: int, 
                        watches: int) -> Dict[int, List[str]]:
        """
        Set up a watch rotation for long rests.
        
        Per D&D 2024 guidelines:
        - Typically 8-hour rest with 2-hour watches
        - Characters on watch can't benefit from rest during their watch
        - Watches allow perception checks against threats
        
        Args:
            characters: List of character names
            rest_duration: Duration of rest in hours
            watches: Number of watch shifts
            
        Returns:
            Dict[int, List[str]]: Characters assigned to each watch
        """
        pass
    
    @abstractmethod
    def coordinate_group_stealth(self, character_checks: Dict[str, int]) -> Tuple[bool, int]:
        """
        Coordinate group stealth.
        
        Per D&D 2024 rules:
        - Group stealth check: Everyone rolls Dexterity (Stealth)
        - Success if at least half the group succeeds
        - Failure may result in detection
        
        Args:
            character_checks: Dictionary mapping character names to stealth check results
            
        Returns:
            Tuple[bool, int]: (Success, group result)
        """
        pass
    
    @abstractmethod
    def evaluate_party_balance(self, character_classes: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate party balance across different roles.
        
        Per D&D 2024 guidelines:
        - Check coverage of key roles (tank, healer, damage, etc.)
        - Identify potential weaknesses
        - Not an official rule, but useful for party composition
        
        Args:
            character_classes: Dictionary mapping character names to their classes
            
        Returns:
            Dict[str, Any]: Analysis of party balance
        """
        pass
    
    @abstractmethod
    def calculate_party_xp_thresholds(self, character_levels: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate party-wide XP thresholds for encounters.
        
        Per D&D 2024 rules:
        - Based on individual character levels
        - Used to balance encounters (easy, medium, hard, deadly)
        - Accounts for party size adjustments
        
        Args:
            character_levels: Dictionary mapping character names to levels
            
        Returns:
            Dict[str, int]: XP thresholds for different difficulties
        """
        pass
    
    @abstractmethod
    def perform_group_ability_contest(self, party_checks: Dict[str, int], 
                                   opposing_checks: Dict[str, int],
                                   method: GroupCheckMethod) -> Tuple[bool, str]:
        """
        Resolve a group ability contest against opponents.
        
        Per D&D 2024 guidelines:
        - Used when party contests against a group of NPCs
        - Examples: Tug-of-war, group intimidation, etc.
        
        Args:
            party_checks: Dictionary mapping party character names to check results
            opposing_checks: Dictionary mapping opponent names to check results
            method: Method to determine group success
            
        Returns:
            Tuple[bool, str]: (Party won, description)
        """
        pass
    
    @abstractmethod
    def apply_inspiration_sharing(self, source_name: str, 
                               target_name: str) -> Tuple[bool, str]:
        """
        Share inspiration between party members.
        
        Per D&D 2024 rules:
        - A character with inspiration can give it to another character
        - This is a way to reward good roleplaying between characters
        - Can only have one inspiration at a time
        
        Args:
            source_name: Character giving inspiration
            target_name: Character receiving inspiration
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def coordinate_group_surprise(self, party_stealth: Dict[str, int],
                               enemy_perception: Dict[str, int]) -> Dict[str, bool]:
        """
        Determine surprise in group combat.
        
        Per D&D 2024 rules:
        - Compare Dexterity (Stealth) checks against passive Perception
        - Any creature that notices a threat is not surprised
        - Surprised creatures can't move or take actions on first turn
        
        Args:
            party_stealth: Dictionary mapping party names to stealth results
            enemy_perception: Dictionary mapping enemy names to perception results
            
        Returns:
            Dict[str, bool]: Which creatures are surprised
        """
        pass
    
    @abstractmethod
    def determine_group_initiative(self, character_initiatives: Dict[str, int]) -> Dict[int, List[str]]:
        """
        Determine initiative order for a group.
        
        Per D&D 2024 rules:
        - Each character rolls initiative (d20 + DEX modifier)
        - Optional rule: Group initiative (one roll for entire party)
        
        Args:
            character_initiatives: Dictionary mapping character names to initiative rolls
            
        Returns:
            Dict[int, List[str]]: Initiative order with characters at each count
        """
        pass
    
    @abstractmethod
    def assist_group_perception(self, character_checks: Dict[str, int]) -> Dict[str, Any]:
        """
        Manage group perception and investigation.
        
        Per D&D 2024 guidelines:
        - When multiple characters search an area
        - Can use best check or group check depending on circumstances
        - Different characters can focus on different aspects
        
        Args:
            character_checks: Dictionary mapping character names to perception/investigation results
            
        Returns:
            Dict[str, Any]: What the group discovers
        """
        pass
    
    @abstractmethod
    def coordinate_group_rest(self, characters: List[str], 
                           rest_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Coordinate a group rest.
        
        Per D&D 2024 rules:
        - Short rest (1 hour) or long rest (8 hours)
        - Interruptions affect the whole group
        - Resources recovered for each character
        - Watch shifts during long rests
        
        Args:
            characters: List of character names
            rest_type: Type of rest ("short" or "long")
            
        Returns:
            Dict[str, Dict[str, Any]]: Results of rest for each character
        """
        pass
    
    @abstractmethod
    def calculate_group_downtime(self, character_activities: Dict[str, str],
                              duration: int) -> Dict[str, Dict[str, Any]]:
        """
        Calculate results of group downtime activities.
        
        Per D&D 2024 guidelines:
        - Characters can engage in different or collaborative activities
        - Some activities benefit from multiple participants
        - Duration in days determines progress
        
        Args:
            character_activities: Dictionary mapping character names to chosen activities
            duration: Duration in days
            
        Returns:
            Dict[str, Dict[str, Any]]: Results for each character
        """
        pass
    
    @abstractmethod
    def coordinate_group_overland_travel(self, characters: Dict[str, Dict[str, Any]],
                                      distance: int,
                                      terrain: str) -> Dict[str, Any]:
        """
        Coordinate group overland travel.
        
        Per D&D 2024 rules:
        - Travel pace affects distance covered and perception
        - Different terrain affects travel speed
        - Group uses slowest member's speed
        - Mounts and vehicles can affect travel speed
        
        Args:
            characters: Dictionary mapping character names to their details
            distance: Distance to travel in miles
            terrain: Type of terrain
            
        Returns:
            Dict[str, Any]: Results of travel
        """
        pass
    
    @abstractmethod
    def manage_party_spell_combinations(self, spells_cast: Dict[str, str]) -> Dict[str, Any]:
        """
        Manage interactions between multiple spells cast by the party.
        
        Per D&D 2024 guidelines:
        - Some spell combinations have special interactions
        - Multiple concentration spells from different casters
        - Area effect overlaps
        
        Args:
            spells_cast: Dictionary mapping character names to spells they're casting
            
        Returns:
            Dict[str, Any]: Results of spell interactions
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert group mechanics data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of group mechanics
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class MagicItemRarity(Enum):
    """Magic item rarity classifications in D&D 5e (2024 Edition)."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    VERY_RARE = auto()
    LEGENDARY = auto()
    ARTIFACT = auto()

class MagicItemType(Enum):
    """Types of magic items in D&D 5e (2024 Edition)."""
    ARMOR = auto()
    WEAPON = auto()
    POTION = auto()
    RING = auto()
    ROD = auto()
    SCROLL = auto()
    STAFF = auto()
    WAND = auto()
    WONDEROUS = auto()

class ItemSlot(Enum):
    """Body slots where magic items can be worn in D&D 5e (2024 Edition)."""
    HEAD = auto()        # Helmets, circlets, etc.
    EYES = auto()        # Goggles, eye patches, etc.
    NECK = auto()        # Amulets, necklaces, etc.
    SHOULDERS = auto()   # Cloaks, mantles, etc.
    CHEST = auto()       # Armor, robes, etc.
    BODY = auto()        # Robes, vestments, etc. (full body)
    WAIST = auto()       # Belts, girdles, etc.
    WRISTS = auto()      # Bracers, bracelets, etc.
    HANDS = auto()       # Gloves, gauntlets, etc.
    FINGERS = auto()     # Rings (typically limited to 2)
    FEET = auto()        # Boots, shoes, etc.
    HELD = auto()        # Weapons, shields, orbs, etc.

class IdentificationState(Enum):
    """States of magic item identification in D&D 5e (2024 Edition)."""
    UNIDENTIFIED = auto()     # Properties unknown
    PARTIALLY_IDENTIFIED = auto()  # Some properties known
    IDENTIFIED = auto()       # All properties known
    ATTUNED = auto()          # Fully identified and attuned

class AbstractMagicItems(ABC):
    """
    Abstract base class for magic item mechanics in D&D 5e (2024 Edition).
    
    This class handles all aspects of magic item interaction including:
    - Item rarity and properties
    - Attunement rules
    - Charge management
    - Item identification
    - Item usage and effects
    """
    
    # Maximum number of attuned items per D&D 2024 rules
    MAX_ATTUNED_ITEMS = 3
    
    # Time required for attunement (in hours)
    ATTUNEMENT_TIME = 1
    
    # Base prices by rarity per DMG guidelines
    ITEM_PRICE_RANGES = {
        MagicItemRarity.COMMON: (50, 100),
        MagicItemRarity.UNCOMMON: (101, 500),
        MagicItemRarity.RARE: (501, 5000),
        MagicItemRarity.VERY_RARE: (5001, 50000),
        MagicItemRarity.LEGENDARY: (50001, 500000),
        MagicItemRarity.ARTIFACT: (None, None)  # Priceless
    }
    
    @abstractmethod
    def add_magic_item(self, item_name: str, item_type: MagicItemType, 
                     rarity: MagicItemRarity, requires_attunement: bool = False,
                     charges: Optional[int] = None, max_charges: Optional[int] = None,
                     properties: Dict[str, Any] = None) -> bool:
        """
        Add a magic item to the character's inventory.
        
        Per D&D 2024 rules, magic items have:
        - A type (armor, weapon, wondrous, etc.)
        - A rarity (common to artifact)
        - Some require attunement
        - Some have charges
        
        Args:
            item_name: Name of the item
            item_type: Type of magic item
            rarity: Item rarity
            requires_attunement: Whether attunement is required
            charges: Current charges (if applicable)
            max_charges: Maximum charges (if applicable)
            properties: Additional item properties
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def remove_magic_item(self, item_name: str) -> bool:
        """
        Remove a magic item from the character's inventory.
        
        Per D&D 2024 rules:
        - Removing an attuned item breaks attunement
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if successfully removed
        """
        pass
    
    @abstractmethod
    def get_magic_item_details(self, item_name: str) -> Dict[str, Any]:
        """
        Get details about a specific magic item.
        
        Returns:
            Dict[str, Any]: Complete item details
        """
        pass
    
    @abstractmethod
    def get_all_magic_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all magic items in the character's inventory.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping item names to details
        """
        pass
    
    @abstractmethod
    def attune_to_item(self, item_name: str) -> Tuple[bool, str]:
        """
        Attempt to attune to a magic item.
        
        Per D&D 2024 rules:
        - Characters can be attuned to a maximum of 3 items
        - Attunement requires a short rest (1 hour)
        - Some items have prerequisites for attunement
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def break_attunement(self, item_name: str) -> bool:
        """
        Break attunement with a magic item.
        
        Per D&D 2024 rules:
        - Attunement ends if:
            - Item is more than 100 feet away for 24+ hours
            - Character dies
            - Another character attunes to the item
            - Character voluntarily breaks attunement (during a short rest)
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if attunement was successfully broken
        """
        pass
    
    @abstractmethod
    def get_attuned_items(self) -> List[str]:
        """
        Get all items the character is currently attuned to.
        
        Returns:
            List[str]: Names of attuned items
        """
        pass
    
    @abstractmethod
    def can_attune_to_more_items(self) -> bool:
        """
        Check if character can attune to additional items.
        
        Per D&D 2024 rules:
        - Maximum of 3 attuned items per character
        - Some special features may modify this limit
        
        Returns:
            bool: True if character can attune to more items
        """
        pass
    
    @abstractmethod
    def get_attunement_limit(self) -> int:
        """
        Get character's maximum number of attunable items.
        
        Returns:
            int: Maximum number of items character can be attuned to
        """
        pass
    
    @abstractmethod
    def use_item_charge(self, item_name: str, charges: int = 1) -> Tuple[bool, int]:
        """
        Use charges from a magic item.
        
        Per D&D 2024 rules:
        - Many items have limited charges
        - Some are destroyed when last charge is used
        - Some risk being destroyed when last charge is used
        
        Args:
            item_name: Name of the item
            charges: Number of charges to use
            
        Returns:
            Tuple[bool, int]: (Success, charges remaining)
        """
        pass
    
    @abstractmethod
    def recharge_item(self, item_name: str, charges: Optional[int] = None) -> Tuple[bool, int]:
        """
        Recharge a magic item.
        
        Per D&D 2024 rules:
        - Many items recover charges at dawn
        - Some recover at other times or under special circumstances
        - Some recover a fixed amount, others variable (e.g., 1d4+2)
        
        Args:
            item_name: Name of the item
            charges: Number of charges to restore (None = full recharge)
            
        Returns:
            Tuple[bool, int]: (Success, new charge total)
        """
        pass
    
    @abstractmethod
    def recharge_all_items(self, time_of_day: str = "dawn") -> Dict[str, int]:
        """
        Recharge all magic items that recover at a specific time.
        
        Args:
            time_of_day: When items recharge ("dawn", "dusk", etc.)
            
        Returns:
            Dict[str, int]: Items recharged with their new charge totals
        """
        pass
    
    @abstractmethod
    def identify_item(self, item_name: str, 
                   method: str = "identify_spell") -> Tuple[bool, Dict[str, Any]]:
        """
        Attempt to identify a magic item.
        
        Per D&D 2024 rules:
        - The identify spell reveals most properties
        - A short rest with physical contact can reveal properties
        - Some properties only reveal themselves when certain conditions are met
        - Some cursed items disguise their true nature
        
        Args:
            item_name: Name of the item
            method: Method of identification
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, revealed properties)
        """
        pass
    
    @abstractmethod
    def get_item_identification_state(self, item_name: str) -> IdentificationState:
        """
        Get current identification state of an item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            IdentificationState: Current identification state
        """
        pass
    
    @abstractmethod
    def apply_item_bonuses(self, item_name: str) -> Dict[str, Any]:
        """
        Apply bonuses and effects from a magic item.
        
        Per D&D 2024 rules:
        - Items can grant bonuses to:
            - AC
            - Attack and damage rolls
            - Saving throws
            - Ability checks
            - Spell save DC and attack rolls
            - And many more specific effects
        
        Args:
            item_name: Name of the item
            
        Returns:
            Dict[str, Any]: Applied bonuses and effects
        """
        pass
    
    @abstractmethod
    def get_all_item_bonuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all bonuses from all magic items.
        
        Returns:
            Dict[str, Dict[str, Any]]: All bonuses by source
        """
        pass
    
    @abstractmethod
    def activate_item(self, item_name: str, 
                   activation_type: str = "command") -> Tuple[bool, Dict[str, Any]]:
        """
        Activate a magic item's power.
        
        Per D&D 2024 rules, activation types include:
        - Command word
        - Consumed (potions, scrolls)
        - Worn (constant effect while worn)
        - Action
        - Special
        
        Args:
            item_name: Name of the item
            activation_type: How the item is activated
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, effect details)
        """
        pass
    
    @abstractmethod
    def check_item_requirements(self, item_name: str) -> Tuple[bool, str]:
        """
        Check if character meets requirements to use an item.
        
        Per D&D 2024 rules:
        - Some items require:
            - Specific class
            - Spellcasting ability
            - Alignment
            - Species
            - Other special requirements
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Meets requirements, explanation)
        """
        pass
    
    @abstractmethod
    def equip_item(self, item_name: str, slot: Optional[ItemSlot] = None) -> Tuple[bool, str]:
        """
        Equip a magic item to a body slot.
        
        Per D&D 2024 rules:
        - Most wearable magic items occupy a specific body slot
        - Can't wear two items in the same slot (except rings)
        - Some slots have special rules (e.g., ring fingers limited to 2)
        
        Args:
            item_name: Name of the item
            slot: Body slot to equip to (None for automatic)
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def unequip_item(self, item_name: str) -> bool:
        """
        Unequip a magic item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if successfully unequipped
        """
        pass
    
    @abstractmethod
    def check_for_cursed_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Check for cursed items and their effects.
        
        Per D&D 2024 rules:
        - Cursed items may:
            - Prevent removal (attunement)
            - Apply negative effects
            - Have special removal conditions
        
        Returns:
            Dict[str, Dict[str, Any]]: Cursed items and their effects
        """
        pass
    
    @abstractmethod
    def get_item_value(self, item_name: str) -> Optional[int]:
        """
        Get the estimated gold piece value of a magic item.
        
        Per D&D 2024 rules:
        - Value depends primarily on rarity
        - Some items have specific values
        
        Args:
            item_name: Name of the item
            
        Returns:
            Optional[int]: Value in gold pieces (None if priceless)
        """
        pass
    
    @abstractmethod
    def get_items_by_rarity(self, rarity: MagicItemRarity) -> List[str]:
        """
        Get all items of a specific rarity.
        
        Args:
            rarity: Item rarity
            
        Returns:
            List[str]: Items of that rarity
        """
        pass
    
    @abstractmethod
    def get_items_by_type(self, item_type: MagicItemType) -> List[str]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: Item type
            
        Returns:
            List[str]: Items of that type
        """
        pass
    
    @abstractmethod
    def get_items_requiring_attunement(self) -> Dict[str, bool]:
        """
        Get all items requiring attunement and their attunement status.
        
        Returns:
            Dict[str, bool]: Dictionary mapping item names to attunement status
        """
        pass
    
    @abstractmethod
    def can_use_item(self, item_name: str) -> Tuple[bool, str]:
        """
        Check if character can use a specific magic item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Can use, explanation)
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert magic item data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of magic items
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple

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
        """
        Level up the character in their current class or a new class.
        
        Per D&D 2024 rules, leveling up includes:
        - Increasing hit points (roll or take average of class hit die + CON mod)
        - Gaining class features for the new level
        - Potentially gaining ASI (levels 4, 8, 12, 16, 19)
        - Potentially gaining new spell slots and spells
        - Updating proficiency bonus if applicable
        
        Args:
            new_class: If specified, multiclass into this new class
                      Otherwise, level up in the character's highest class
            
        Returns:
            Dict[str, Any]: Results of the level up process including:
                - new_level: The character's new level
                - hp_increase: Hit points gained
                - new_features: List of new features gained
                - proficiency_increase: Whether proficiency bonus increased
                - new_spells: New spell slots or spells gained (if applicable)
                - asi: Whether an ability score improvement was gained
        """
        pass
    
    @abstractmethod
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """
        Check if character meets ability score requirements to multiclass.
        
        This method should:
        1. Find the class definition for the requested class
        2. Get its multiclassing requirements using get_multiclass_requirements()
        3. Check character's ability scores against these requirements
        4. Support both official classes and custom classes
        
        Args:
            new_class: Class to check for multiclassing
            
        Returns:
            Tuple[bool, str]: (Can multiclass, explanation)
        """
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """
        Get proficiencies gained when multiclassing into a specific class.
        
        Per D&D 2024 rules, multiclass proficiency gains are more limited:
        - No saving throw proficiencies are gained
        - Limited skill proficiencies (typically 1, not the normal starting amount)
        - Limited weapon and armor proficiencies
        - Some tool proficiencies may be gained
        
        Args:
            new_class: Class being multiclassed into
            
        Returns:
            Dict[str, List[str]]: Proficiencies gained by category
        """
        pass
    
    @abstractmethod
    def calculate_multiclass_spellcaster_level(self) -> int:
        """
        Calculate effective spellcaster level for determining spell slots.
        
        Per D&D 2024 rules for multiclassed spellcasters:
        - Add all full-caster levels (Bard, Cleric, Druid, Sorcerer, Wizard)
        - Add half of half-caster levels (Paladin, Ranger), rounded down
        - Add one-third of third-caster levels (Fighter-Eldritch Knight, Rogue-Arcane Trickster), rounded down
        - Warlocks follow different rules and don't combine with other classes for spell slots
        
        Returns:
            int: Effective spellcaster level for spell slot determination
        """
        pass
    
    @abstractmethod
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """
        Get available spell slots based on multiclass spellcaster level.
        
        Per D&D 2024 rules, spell slots are determined by combined spellcaster level,
        regardless of which spells from which classes are being cast with those slots.
        
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to number of slots
        """
        pass
    
    @abstractmethod
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """
        Calculate hit points gained when leveling up in a multiclass.
        
        Per D&D 2024 rules:
        - First level in primary class: Maximum hit die + CON modifier
        - Any other level: Roll or take average of hit die + CON modifier
        
        Args:
            new_class: Class being leveled up in
            is_first_level: Whether this is the first level in this class
            
        Returns:
            int: Hit points gained
        """
        pass
    
    @abstractmethod
    def get_level_in_class(self, class_name: str) -> int:
        """
        Get character's level in a specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            int: Level in that class (0 if not taken)
        """
        pass
    
    @abstractmethod
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """
        Get features gained for a specific class at a specific level.
        
        Per D&D 2024 rules, some features don't stack when multiclassing:
        - Extra Attack from multiple classes doesn't provide additional attacks
        - Channel Divinity options stack, but not uses per rest
        - Unarmored Defense doesn't stack if gained from multiple classes
        
        Args:
            class_name: Name of the class
            level: Level in that class
            
        Returns:
            Dict[str, Any]: Features gained at that level
        """
        pass
    
    @abstractmethod
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """
        Apply choices made during level up (e.g., new spells, subclass, ASI).
        
        Args:
            choices: Dictionary of level-up choices
            
        Returns:
            bool: Success or failure
        """
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """
        Get levels at which a class grants Ability Score Improvements.
        
        Per D&D 2024 rules:
        - Most classes get ASIs at levels 4, 8, 12, 16, 19
        - Fighter gets additional ASIs at levels 6, 14
        - ASIs from different classes stack
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[int]: Levels at which the class grants ASIs
        """
        pass
    
    @abstractmethod
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """
        Check if character is eligible for level up based on XP.
        
        Per D&D 2024 rules, characters level up when reaching XP thresholds.
        
        Returns:
            Tuple[bool, str]: (Is eligible, explanation)
        """
        pass
    
    @abstractmethod
    def get_next_level_xp_threshold(self) -> int:
        """
        Get XP needed for next level.
        
        Returns:
            int: XP threshold for next level
        """
        pass
    
    @abstractmethod
    def calculate_character_level(self) -> int:
        """
        Calculate total character level from all class levels.
        
        Per D&D 2024 rules, character level equals the sum of all class levels.
        
        Returns:
            int: Total character level
        """
        pass
    
    @abstractmethod
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """
        Get all classes and whether character qualifies to multiclass into them.
        
        Returns:
            Dict[str, bool]: Dictionary mapping class names to qualification status
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple

class PersonalityTraitSource(Enum):
    """Enumeration of sources for personality traits in D&D 5e (2024 Edition)."""
    BACKGROUND = auto()   # From character background
    CUSTOM = auto()       # Player-defined
    RANDOM = auto()       # Randomly generated
    CLASS = auto()        # From character class
    SPECIES = auto()      # From character species
    ALIGNMENT = auto()    # From character alignment

class AbstractPersonality(ABC):
    """
    Abstract base class defining the contract for character personality in D&D 5e (2024 Edition).
    
    According to D&D 2024 rules, a character's personality is defined by:
    - Traits: Short statements that describe character behavior and attitudes
    - Ideals: Core principles and beliefs that motivate the character
    - Bonds: Connections to people, places, or things in the world
    - Flaws: Character weaknesses or vulnerabilities
    """
    
    @abstractmethod
    def get_personality_options(self, background: str) -> Dict[str, List[str]]:
        """
        Get official personality options based on background.
        
        Per D&D 2024 rules, each background suggests several personality traits,
        ideals, bonds, and flaws that fit its theme.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, List[str]]: Dictionary with personality options for traits, ideals, bonds, flaws
        """
        pass
    
    @abstractmethod
    def validate_personality(self, traits: List[str], ideals: List[str], 
                          bonds: List[str], flaws: List[str]) -> Tuple[bool, str]:
        """
        Validate personality elements against D&D 2024 rules.
        
        Per D&D 2024 rules, these elements should be concise and roleplay-focused.
        
        Args:
            traits: List of personality traits
            ideals: List of character ideals
            bonds: List of character bonds
            flaws: List of character flaws
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        pass
    
    @abstractmethod
    def get_personality_suggested_by_alignment(self, alignment: Tuple[str, str]) -> Dict[str, List[str]]:
        """
        Get personality traits suggested by a character's alignment.
        
        Per D&D 2024 rules, alignment can influence personality.
        
        Args:
            alignment: (ethical, moral) alignment tuple
            
        Returns:
            Dict[str, List[str]]: Suggested traits, ideals, bonds, flaws
        """
        pass
    
    @abstractmethod
    def format_backstory_template(self, background: str) -> Dict[BackstoryElement, str]:
        """
        Get a template for creating a backstory based on a background.
        
        Args:
            background: Character background
            
        Returns:
            Dict[BackstoryElement, str]: Template prompts for each backstory element
        """
        pass
    
    @abstractmethod
    def get_character_personality(self) -> Dict[str, List[str]]:
        """
        Get current personality elements for the character.
        
        Returns:
            Dict[str, List[str]]: Dictionary with traits, ideals, bonds, flaws
        """
        pass
    
    @abstractmethod
    def set_character_personality(self, personality_elements: Dict[str, List[str]]) -> bool:
        """
        Set personality elements for the character.
        
        Args:
            personality_elements: Dictionary with traits, ideals, bonds, flaws
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def get_backstory(self) -> Dict[BackstoryElement, str]:
        """
        Get the character's backstory elements.
        
        Returns:
            Dict[BackstoryElement, str]: Backstory elements
        """
        pass
    
    @abstractmethod
    def set_backstory(self, backstory: Dict[BackstoryElement, str]) -> bool:
        """
        Set the character's backstory elements.
        
        Args:
            backstory: Backstory elements
            
        Returns:
            bool: True if successfully set
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ProficiencyType(Enum):
    """Enumeration of proficiency types in D&D 5e (2024 Edition)."""
    SKILL = auto()      # Skill proficiencies (Perception, Stealth, etc.)
    SAVING_THROW = auto()  # Saving throw proficiencies (CON, DEX, etc.)
    TOOL = auto()       # Tool proficiencies (thieves' tools, herbalism kit, etc.)
    WEAPON = auto()     # Weapon proficiencies (simple, martial, specific)
    ARMOR = auto()      # Armor proficiencies (light, medium, heavy, shields)
    LANGUAGE = auto()   # Language proficiencies (Common, Elvish, etc.)

class ProficiencyLevel(Enum):
    """Enumeration of proficiency levels in D&D 5e (2024 Edition)."""
    NONE = 0            # No proficiency (0× proficiency bonus)
    HALF = 0.5          # Half proficiency (0.5× proficiency bonus, rounded down)
    PROFICIENT = 1      # Proficient (1× proficiency bonus)
    EXPERT = 2          # Expertise (2× proficiency bonus)

class WeaponCategory(Enum):
    """Weapon categories in D&D 5e (2024 Edition)."""
    SIMPLE = auto()
    MARTIAL = auto()
    SPECIFIC = auto()   # For specific weapon proficiencies

class ArmorCategory(Enum):
    """Armor categories in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()

class AbstractProficiency(ABC):
    """
    Abstract base class defining the contract for proficiency systems in D&D 5e (2024 Edition).
    
    In D&D, proficiencies represent a character's training and expertise with:
    - Skills (e.g., Perception, Athletics)
    - Saving throws (e.g., Constitution saves, Dexterity saves)
    - Tools (e.g., thieves' tools, alchemist's supplies)
    - Weapons (simple, martial, or specific weapons)
    - Armor (light, medium, heavy, shields)
    - Languages (Common, Elvish, etc.)
    
    Proficiencies grant bonuses to relevant ability checks, attack rolls, or other actions.
    """
    
    # Proficiency bonus by character level as per D&D 2024 rules
    PROFICIENCY_BONUS = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Standard skill list as per D&D 2024 rules
    SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Standard ability scores
    ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    # Standard tool categories
    TOOL_CATEGORIES = ["Artisan's Tools", "Gaming Sets", "Musical Instruments", "Other Tools"]
    
    # Common languages in D&D 2024
    STANDARD_LANGUAGES = [
        "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", 
        "Halfling", "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", 
        "Infernal", "Primordial", "Sylvan", "Undercommon"
    ]
    
    @abstractmethod
    def calculate_proficiency_bonus(self, character_level: int) -> int:
        """
        Calculate proficiency bonus based on character level.
        
        Per D&D 2024 rules:
        - Levels 1-4: +2
        - Levels 5-8: +3
        - Levels 9-12: +4
        - Levels 13-16: +5
        - Levels 17-20: +6
        
        Args:
            character_level: Total character level (1-20)
            
        Returns:
            int: Proficiency bonus
        """
        pass
    
    @abstractmethod
    def get_proficiency_level(self, prof_type: ProficiencyType, specific_prof: str) -> ProficiencyLevel:
        """
        Get the proficiency level for a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            ProficiencyLevel: Level of proficiency
        """
        pass
    
    @abstractmethod
    def set_proficiency_level(self, prof_type: ProficiencyType, specific_prof: str, 
                           level: ProficiencyLevel) -> bool:
        """
        Set the proficiency level for a specific proficiency.
        
        Per D&D 2024 rules:
        - Proficiency levels generally don't stack
        - When multiple features grant proficiency, take the highest level
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            level: Level of proficiency
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def add_proficiency(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Add a proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def add_expertise(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Add expertise for a proficiency.
        
        Per D&D 2024 rules, expertise doubles the proficiency bonus
        for checks using that proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if expertise was successfully added
        """
        pass
    
    @abstractmethod
    def apply_jack_of_all_trades(self) -> bool:
        """
        Apply the Jack of All Trades feature.
        
        Per D&D 2024 rules, Jack of All Trades allows adding half the proficiency
        bonus (rounded down) to any ability check that doesn't already include
        the proficiency bonus.
        
        Returns:
            bool: True if successfully applied
        """
        pass
    
    @abstractmethod
    def has_jack_of_all_trades(self) -> bool:
        """
        Check if the character has Jack of All Trades.
        
        Returns:
            bool: True if the character has Jack of All Trades
        """
        pass
    
    @abstractmethod
    def calculate_modifier(self, prof_type: ProficiencyType, specific_prof: str, 
                        ability_scores: Dict[str, int], character_level: int) -> int:
        """
        Calculate the total modifier for a check using this proficiency.
        
        Per D&D 2024 rules:
        - Base modifier is the relevant ability score modifier
        - Add proficiency bonus if proficient
        - Add twice proficiency bonus if expertise
        - Add half proficiency bonus (rounded down) if Jack of All Trades applies
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            ability_scores: Character's ability scores
            character_level: Character's level
            
        Returns:
            int: Total modifier
        """
        pass
    
    @abstractmethod
    def get_all_proficiencies(self) -> Dict[ProficiencyType, List[str]]:
        """
        Get all proficiencies the character has.
        
        Returns:
            Dict[ProficiencyType, List[str]]: All proficiencies by type
        """
        pass
    
    @abstractmethod
    def get_all_expertise(self) -> Dict[ProficiencyType, List[str]]:
        """
        Get all proficiencies the character has expertise in.
        
        Returns:
            Dict[ProficiencyType, List[str]]: All expertise proficiencies
        """
        pass
    
    @abstractmethod
    def has_proficiency(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Check if the character is proficient in a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if proficient
        """
        pass
    
    @abstractmethod
    def has_expertise(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Check if the character has expertise in a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if has expertise
        """
        pass
    
    @abstractmethod
    def get_proficiencies_by_source(self, source: str) -> Dict[ProficiencyType, List[str]]:
        """
        Get proficiencies from a specific source.
        
        Per D&D 2024 rules, proficiencies come from:
        - Character class
        - Background
        - Species
        - Feats
        
        Args:
            source: Source of proficiencies (class, background, species, feat)
            
        Returns:
            Dict[ProficiencyType, List[str]]: Proficiencies from that source
        """
        pass
    
    @abstractmethod
    def can_use_armor(self, armor_name: str) -> Tuple[bool, str]:
        """
        Check if character can use a specific armor.
        
        Per D&D 2024 rules:
        - Characters need proficiency to use armor effectively
        - Non-proficient use of armor imposes disadvantage on
          ability checks, saving throws, and attack rolls that use
          Strength or Dexterity, and prevents spellcasting
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            Tuple[bool, str]: (Can use, explanation)
        """
        pass
    
    @abstractmethod
    def can_use_weapon(self, weapon_name: str) -> bool:
        """
        Check if character can use a specific weapon.
        
        Per D&D 2024 rules:
        - Characters can use any weapon, but only add proficiency bonus
          to attack rolls with weapons they're proficient with
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            bool: True if proficient with the weapon
        """
        pass
    
    @abstractmethod
    def can_use_tool(self, tool_name: str) -> bool:
        """
        Check if character can use a specific tool.
        
        Per D&D 2024 rules:
        - Characters can attempt to use any tool
        - Proficiency adds the proficiency bonus to the check
        - Some tool uses might require proficiency
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: True if proficient with the tool
        """
        pass
    
    @abstractmethod
    def can_speak_language(self, language: str) -> bool:
        """
        Check if character can speak a specific language.
        
        Args:
            language: Name of the language
            
        Returns:
            bool: True if character knows the language
        """
        pass
    
    @abstractmethod
    def add_saving_throw_proficiency(self, ability: str) -> bool:
        """
        Add proficiency in a saving throw.
        
        Per D&D 2024 rules:
        - Each class grants proficiency in specific saving throws
        - Some features can grant additional saving throw proficiencies
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def is_proficient_in_saving_throw(self, ability: str) -> bool:
        """
        Check if character is proficient in a saving throw.
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            
        Returns:
            bool: True if proficient in that saving throw
        """
        pass
    
    @abstractmethod
    def calculate_saving_throw_modifier(self, ability: str, ability_scores: Dict[str, int], 
                                      character_level: int) -> int:
        """
        Calculate modifier for a saving throw.
        
        Per D&D 2024 rules:
        - Base is the ability score modifier
        - Add proficiency bonus if proficient in that saving throw
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            ability_scores: Character's ability scores
            character_level: Character's level
            
        Returns:
            int: Total saving throw modifier
        """
        pass
    
    @abstractmethod
    def get_tool_categories(self) -> Dict[str, List[str]]:
        """
        Get all tool categories and their tools.
        
        Per D&D 2024 rules, tools include:
        - Artisan's tools (smith's tools, carpenter's tools, etc.)
        - Gaming sets (dice set, playing card set)
        - Musical instruments (drum, lute, etc.)
        - Other tools (thieves' tools, navigator's tools, etc.)
        
        Returns:
            Dict[str, List[str]]: Tool categories and tools
        """
        pass
    
    @abstractmethod
    def get_weapons_by_category(self) -> Dict[WeaponCategory, List[str]]:
        """
        Get weapons organized by category.
        
        Per D&D 2024 rules, weapons are categorized as:
        - Simple weapons
        - Martial weapons
        - Specific weapons (for special proficiencies)
        
        Returns:
            Dict[WeaponCategory, List[str]]: Weapons by category
        """
        pass
    
    @abstractmethod
    def get_armor_by_category(self) -> Dict[ArmorCategory, List[str]]:
        """
        Get armor organized by category.
        
        Per D&D 2024 rules, armor is categorized as:
        - Light armor
        - Medium armor
        - Heavy armor
        - Shields
        
        Returns:
            Dict[ArmorCategory, List[str]]: Armor by category
        """
        pass
    
    @abstractmethod
    def get_languages_by_rarity(self) -> Dict[str, List[str]]:
        """
        Get languages organized by rarity.
        
        Per D&D 2024 rules, languages are categorized as:
        - Common languages (Common, Dwarvish, Elvish, etc.)
        - Exotic languages (Abyssal, Celestial, etc.)
        
        Returns:
            Dict[str, List[str]]: Languages by rarity
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_class(self, class_name: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a character class.
        
        Per D&D 2024 rules, each class grants:
        - Saving throw proficiencies (2)
        - Skill proficiencies (2-4 from a class list)
        - Armor proficiencies (varies)
        - Weapon proficiencies (varies)
        - Tool proficiencies (some classes)
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_background(self, background: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a background.
        
        Per D&D 2024 rules, backgrounds typically grant:
        - Two skill proficiencies
        - Tool proficiency or language
        
        Args:
            background: Name of the background
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_species(self, species: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a species.
        
        Per D&D 2024 rules, some species grant:
        - Skill proficiencies
        - Tool proficiencies
        - Weapon proficiencies
        - Languages
        
        Args:
            species: Name of the species
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_multiclass_proficiencies(self, new_class: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from multiclassing.
        
        Per D&D 2024 rules, multiclassing grants:
        - Limited armor/weapon proficiencies
        - No saving throw proficiencies
        - Limited skill proficiencies (typically 1)
        
        Args:
            new_class: New class being added
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert proficiency data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of proficiencies
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ResourceType(Enum):
    """Enumeration of character resource types in D&D 5e (2024 Edition)."""
    SPELL_SLOT = auto()      # Spell slots for spellcasting
    CLASS_RESOURCE = auto()  # Class-specific resources (ki, rage, etc.)
    FEATURE_USE = auto()     # Limited-use features (Channel Divinity, etc.)
    INSPIRATION = auto()     # D&D inspiration (advantage on one roll)
    ITEM_CHARGE = auto()     # Magic item charges
    CONSUMABLE = auto()      # Consumable items (potions, scrolls, etc.)
    HIT_DICE = auto()        # Hit dice for recovery
    ACTION = auto()          # Actions, bonus actions, reactions
    MOVEMENT = auto()        # Movement speed

class ResourceRecoveryTiming(Enum):
    """When resources recover in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()      # Recovers after short or long rest
    LONG_REST = auto()       # Recovers only after long rest
    DAWN = auto()            # Recovers at dawn
    DUSK = auto()            # Recovers at dusk
    TURN_START = auto()      # Recovers at start of creature's turn
    TURN_END = auto()        # Recovers at end of creature's turn
    INITIATIVE = auto()      # Recovers when initiative is rolled
    MILESTONE = auto()       # Recovers at story milestones
    SPECIAL = auto()         # Special recovery conditions
    NEVER = auto()           # Doesn't recover (consumables)

class AbstractResources(ABC):
    """
    Abstract base class for managing character resources in D&D 5e (2024 Edition).
    
    This class defines the interface for tracking and managing various character resources:
    - Spell slots for spellcasters
    - Class-specific resources like ki points, sorcery points, etc.
    - Limited-use features like Channel Divinity
    - Inspiration
    - Magic item charges and consumables
    """
    
    @abstractmethod
    def get_spell_slots(self) -> Dict[int, Dict[str, int]]:
        """
        Get current and maximum spell slots by level.
        
        Per D&D 2024 rules, spell slots are determined by:
        - Character's class and level
        - Spellcasting or Pact Magic features
        - Multiclassing rules for combined spellcasters
        
        Returns:
            Dict[int, Dict[str, int]]: Dictionary mapping spell levels to:
                - "current": Available spell slots
                - "maximum": Maximum spell slots
        """
        pass
    
    @abstractmethod
    def use_spell_slot(self, level: int) -> bool:
        """
        Use a spell slot of the specified level.
        
        Per D&D 2024 rules:
        - Cannot use a slot if none are available
        - Can use higher level slots for lower level spells
        - Warlocks have special rules for Pact Magic slots
        
        Args:
            level: Level of spell slot to use
            
        Returns:
            bool: True if successful, False if no slot available
        """
        pass
    
    @abstractmethod
    def recover_spell_slots(self, level: int, amount: int) -> int:
        """
        Recover spell slots of a specific level.
        
        Per D&D 2024 rules:
        - Most classes recover all slots on long rest
        - Warlocks recover all Pact Magic slots on short rest
        - Some features (Arcane Recovery, Natural Recovery) restore 
          slots during short rests
        
        Args:
            level: Level of spell slots to recover
            amount: Number of slots to recover
            
        Returns:
            int: Number of slots actually recovered
        """
        pass
    
    @abstractmethod
    def create_spell_slot(self, level: int) -> bool:
        """
        Create a new spell slot (for features like Sorcerer's Font of Magic).
        
        Per D&D 2024 rules, some features allow creating temporary spell slots.
        
        Args:
            level: Level of spell slot to create
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def get_class_resource(self, resource_name: str) -> Dict[str, int]:
        """
        Get information about a class-specific resource.
        
        Examples of class resources in D&D 2024:
        - Barbarian: Rage uses
        - Bard: Bardic Inspiration uses
        - Druid: Wild Shape uses
        - Ki Points (Monk)
        - Sorcery Points (Sorcerer)
        - Lay on Hands pool (Paladin)
        - Superiority Dice (Fighter)
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current amount
                - "maximum": Maximum amount
        """
        pass
    
    @abstractmethod
    def use_class_resource(self, resource_name: str, amount: int = 1) -> bool:
        """
        Use a specified amount of a class resource.
        
        Args:
            resource_name: Name of the resource
            amount: Amount to use
            
        Returns:
            bool: True if successful, False if insufficient resources
        """
        pass
    
    @abstractmethod
    def recover_class_resource(self, resource_name: str, amount: int) -> int:
        """
        Recover a specified amount of a class resource.
        
        Per D&D 2024 rules, recovery timing varies by class:
        - Some recover on short rest (Warlock spells, Fighter maneuvers)
        - Some recover on long rest (Wizard Arcane Recovery)
        - Some have special recovery (Natural Recovery, Font of Magic)
        
        Args:
            resource_name: Name of the resource
            amount: Amount to recover
            
        Returns:
            int: Amount actually recovered
        """
        pass
    
    @abstractmethod
    def add_class_resource(self, resource_name: str, maximum: int, recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new class resource.
        
        Args:
            resource_name: Name of the resource
            maximum: Maximum amount
            recovery: When the resource recovers
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def get_feature_uses(self, feature_name: str) -> Dict[str, int]:
        """
        Get current and maximum uses for a limited-use feature.
        
        Examples of limited-use features in D&D 2024:
        - Channel Divinity
        - Wild Shape
        - Action Surge
        - Second Wind
        - Cleansing Touch
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current uses
                - "maximum": Maximum uses
        """
        pass
    
    @abstractmethod
    def use_feature(self, feature_name: str) -> bool:
        """
        Use a limited-use feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            bool: True if successful, False if no uses remain
        """
        pass
    
    @abstractmethod
    def recover_feature_use(self, feature_name: str, amount: int = 1) -> int:
        """
        Recover uses of a limited-use feature.
        
        Args:
            feature_name: Name of the feature
            amount: Number of uses to recover
            
        Returns:
            int: Number of uses actually recovered
        """
        pass
    
    @abstractmethod
    def add_limited_feature(self, feature_name: str, uses: int, 
                         recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new limited-use feature.
        
        Args:
            feature_name: Name of the feature
            uses: Number of uses
            recovery: When uses recover
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def has_inspiration(self) -> bool:
        """
        Check if character has inspiration.
        
        Per D&D 2024 rules:
        - Inspiration is awarded by the DM for good roleplay, clever ideas, etc.
        - Some features can also grant inspiration
        - Characters can only have one inspiration at a time
        
        Returns:
            bool: True if character has inspiration
        """
        pass
    
    @abstractmethod
    def grant_inspiration(self) -> bool:
        """
        Grant inspiration to the character.
        
        Per D&D 2024 rules, a character can only have one inspiration at a time.
        
        Returns:
            bool: True if inspiration was granted (False if already had it)
        """
        pass
    
    @abstractmethod
    def use_inspiration(self) -> bool:
        """
        Use inspiration for advantage on a roll.
        
        Per D&D 2024 rules:
        - Inspiration can be used to gain advantage on one attack roll, 
          saving throw, or ability check
        - Using inspiration expends it
        
        Returns:
            bool: True if inspiration was used
        """
        pass
    
    @abstractmethod
    def get_item_charges(self, item_name: str) -> Dict[str, int]:
        """
        Get current and maximum charges for a magic item.
        
        Per D&D 2024 rules:
        - Many magic items have a limited number of charges
        - Charges are typically recovered at dawn (but can vary)
        - Some items are destroyed when the last charge is used
        
        Args:
            item_name: Name of the item
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current charges
                - "maximum": Maximum charges
        """
        pass
    
    @abstractmethod
    def use_item_charge(self, item_name: str, amount: int = 1) -> bool:
        """
        Use charges from a magic item.
        
        Args:
            item_name: Name of the item
            amount: Number of charges to use
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def recover_item_charges(self, item_name: str, amount: Optional[int] = None) -> int:
        """
        Recover charges for a magic item.
        
        Per D&D 2024 rules:
        - Many items recover a specific number of charges at dawn
        - Some recover all charges
        - Some have special recovery conditions
        
        Args:
            item_name: Name of the item
            amount: Number of charges to recover (None = all)
            
        Returns:
            int: Number of charges recovered
        """
        pass
    
    @abstractmethod
    def add_item_with_charges(self, item_name: str, charges: int, max_charges: int,
                           recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new item with charges to the inventory.
        
        Args:
            item_name: Name of the item
            charges: Current charges
            max_charges: Maximum charges
            recovery: When charges recover
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def get_consumables(self) -> Dict[str, int]:
        """
        Get all consumable items and their quantities.
        
        Consumables in D&D 2024 include:
        - Potions
        - Scrolls
        - Ammunition
        - Thrown weapons
        - Spell components with costs
        
        Returns:
            Dict[str, int]: Dictionary mapping item names to quantities
        """
        pass
    
    @abstractmethod
    def use_consumable(self, item_name: str, amount: int = 1) -> bool:
        """
        Use a consumable item.
        
        Args:
            item_name: Name of the item
            amount: Quantity to use
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def add_consumable(self, item_name: str, amount: int) -> int:
        """
        Add consumable items to inventory.
        
        Args:
            item_name: Name of the item
            amount: Quantity to add
            
        Returns:
            int: New total quantity
        """
        pass
    
    @abstractmethod
    def get_hit_dice(self) -> Dict[str, Dict[str, int]]:
        """
        Get current and maximum hit dice by die type.
        
        Per D&D 2024 rules:
        - Hit dice are used during short rests to recover HP
        - Characters have different die types based on class (d6, d8, d10, d12)
        - Long rest recovers up to half of maximum hit dice
        
        Returns:
            Dict[str, Dict[str, int]]: Dictionary mapping die types to:
                - "current": Available dice
                - "maximum": Maximum dice
        """
        pass
    
    @abstractmethod
    def use_hit_dice(self, die_type: str, amount: int = 1) -> Dict[str, int]:
        """
        Use hit dice during a short rest.
        
        Per D&D 2024 rules:
        - Each hit die recovers HP equal to die roll + CON modifier
        
        Args:
            die_type: Type of hit die (d6, d8, d10, d12)
            amount: Number of dice to use
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "dice_spent": Dice actually spent
                - "hp_recovered": HP recovered
        """
        pass
    
    @abstractmethod
    def recover_hit_dice(self, amount: Optional[int] = None) -> Dict[str, int]:
        """
        Recover hit dice after a long rest.
        
        Per D&D 2024 rules:
        - Long rest recovers up to half of max hit dice (minimum 1)
        
        Args:
            amount: Number to recover (None = half of maximum)
            
        Returns:
            Dict[str, int]: Dictionary mapping die types to dice recovered
        """
        pass
    
    @abstractmethod
    def get_actions_remaining(self) -> Dict[str, int]:
        """
        Get remaining actions for the current turn/round.
        
        Per D&D 2024 rules, characters typically have:
        - One action
        - One bonus action
        - One reaction per round
        - Movement up to their speed
        
        Returns:
            Dict[str, int]: Dictionary with available actions
        """
        pass
    
    @abstractmethod
    def use_action(self, action_type: str) -> bool:
        """
        Use an action type.
        
        Args:
            action_type: Type of action ("action", "bonus", "reaction")
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def reset_actions(self) -> None:
        """
        Reset available actions for a new turn.
        
        Per D&D 2024 rules:
        - Actions and bonus actions reset at the start of a turn
        - Reactions reset at the start of a turn
        - Movement resets at the start of a turn
        """
        pass
    
    @abstractmethod
    def get_all_resources(self) -> Dict[ResourceType, Any]:
        """
        Get all character resources.
        
        Returns:
            Dict[ResourceType, Any]: All resources by type
        """
        pass
    
    @abstractmethod
    def reset_resources_by_timing(self, recovery_timing: ResourceRecoveryTiming) -> Dict[str, Any]:
        """
        Reset all resources that recover at a specific timing.
        
        Args:
            recovery_timing: When resources recover
            
        Returns:
            Dict[str, Any]: Resources that were reset
        """
        pass
    
    @abstractmethod
    def get_resources_by_recovery(self, recovery_timing: ResourceRecoveryTiming) -> Dict[str, Any]:
        """
        Get all resources that recover at a specific timing.
        
        Args:
            recovery_timing: When resources recover
            
        Returns:
            Dict[str, Any]: Resources with that recovery timing
        """
        pass
    
    @abstractmethod
    def convert_resources(self, from_resource: str, to_resource: str, amount: int) -> Dict[str, int]:
        """
        Convert one resource type to another (e.g. sorcery points to spell slots).
        
        Per D&D 2024 rules:
        - Some classes can convert between resource types
        - Example: Sorcerer's Font of Magic can convert between sorcery points and spell slots
        - Example: Warlock's Pact Magic spell slots can be converted to sorcery points
        
        Args:
            from_resource: Resource to convert from
            to_resource: Resource to convert to
            amount: Amount to convert
            
        Returns:
            Dict[str, int]: Dictionary with conversion results
        """
        pass
    
    @abstractmethod
    def check_resource_availability(self, resource_type: ResourceType, 
                                 resource_name: str, amount: int = 1) -> bool:
        """
        Check if a specific amount of a resource is available.
        
        Args:
            resource_type: Type of resource
            resource_name: Name of the specific resource
            amount: Amount needed
            
        Returns:
            bool: True if the resource is available
        """
        pass
    
    @abstractmethod
    def apply_resource_modifiers(self, modifiers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply modifiers to resources (e.g. from magic items, feats, etc.).
        
        Examples:
        - Rod of the Pact Keeper: +N to Warlock spell save DC and attack rolls
        - Pearl of Power: Recover one expended spell slot up to 3rd level
        
        Args:
            modifiers: Dictionary of modifiers to apply
            
        Returns:
            Dict[str, Any]: Results of applying modifiers
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resource data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of resources
        """
        pass

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class RestType(Enum):
    """Types of rest in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()  # 1 hour of light activity
    LONG_REST = auto()   # 8 hours (6 hours sleep + 2 hours light activity)
    CATNAP = auto()      # 10-minute magical short rest (from spell)
    MEDITATION = auto()  # Special rest for certain species/classes (like Elves)

class ResourceRecoveryType(Enum):
    """When character resources recover in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()  # Resources that recover after a short or long rest
    LONG_REST = auto()   # Resources that recover only after a long rest
    DAILY = auto()       # Resources that recover at a specific time of day
    DAWN = auto()        # Resources that recover at dawn
    DUSK = auto()        # Resources that recover at dusk
    SPECIAL = auto()     # Custom recovery conditions

class AbstractResting(ABC):
    """
    Abstract base class for handling character resting in D&D 5e (2024 Edition).
    
    Resting is a critical mechanic in D&D that allows characters to recover:
    - Hit points
    - Hit dice
    - Spell slots
    - Class features
    - Magic item charges
    
    D&D 2024 defines two main types of rest:
    1. Short Rest (1 hour)
    2. Long Rest (8 hours, with at least 6 hours of sleep)
    """
    
    @abstractmethod
    def take_short_rest(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Perform a short rest.
        
        Per D&D 2024 rules:
        - Short rest requires 1 hour of light activity
        - Characters can spend one or more Hit Dice to recover HP
        - Each Hit Die spent recovers HP equal to die roll + CON modifier
        - Some class features recover after a short rest
        
        Args:
            duration_minutes: Time spent resting in minutes (normally 60)
            
        Returns:
            Dict[str, Any]: Results of the short rest including:
                - hit_dice_spent: Number of hit dice spent
                - hp_recovered: HP recovered from hit dice
                - features_recovered: List of features that recovered
                - complete: Whether the rest was completed successfully
        """
        pass
    
    @abstractmethod
    def take_long_rest(self, duration_hours: int = 8, sleep_hours: int = 6) -> Dict[str, Any]:
        """
        Perform a long rest.
        
        Per D&D 2024 rules:
        - Long rest requires 8 hours (at least 6 hours of sleep, 2 hours of light activity)
        - Recovers all HP
        - Recovers up to half of max Hit Dice (minimum 1)
        - Resets most class features with "long rest" recovery
        - Some features recharge "daily" or "at dawn/dusk" instead
        - Can only benefit from one long rest per 24-hour period
        - Must have at least 1 HP to benefit from a rest
        - Long rest can be interrupted by 1+ hour of strenuous activity
        
        Args:
            duration_hours: Total time spent resting in hours (normally 8)
            sleep_hours: Time spent sleeping in hours (normally 6+)
            
        Returns:
            Dict[str, Any]: Results of the long rest including:
                - hp_recovered: HP recovered
                - hit_dice_recovered: Hit dice recovered
                - features_recovered: List of features that recovered
                - spell_slots_recovered: Spell slots recovered
                - complete: Whether the rest was completed successfully
        """
        pass
    
    @abstractmethod
    def spend_hit_die(self, num_dice: int = 1) -> Dict[str, int]:
        """
        Spend hit dice to recover hit points during a short rest.
        
        Per D&D 2024 rules:
        - Each hit die recovers HP equal to the die roll + CON modifier
        - Character must have available hit dice to spend
        - Hit die type is based on character class
        
        Args:
            num_dice: Number of hit dice to spend
            
        Returns:
            Dict[str, int]: Dictionary with:
                - dice_spent: Number of dice actually spent
                - hp_recovered: HP recovered
        """
        pass
    
    @abstractmethod
    def get_available_hit_dice(self) -> Dict[str, int]:
        """
        Get available hit dice by type.
        
        Returns:
            Dict[str, int]: Dictionary mapping hit die types to count
        """
        pass
    
    @abstractmethod
    def recover_hit_points(self, amount: int) -> int:
        """
        Recover hit points.
        
        Per D&D 2024 rules:
        - Characters cannot exceed their maximum HP
        - Some special abilities modify HP recovery
        
        Args:
            amount: Amount of HP to recover
            
        Returns:
            int: Actual HP recovered
        """
        pass
    
    @abstractmethod
    def recover_hit_dice(self, amount: int) -> int:
        """
        Recover spent hit dice.
        
        Per D&D 2024 rules:
        - Long rest recovers up to half total hit dice (minimum 1)
        - Cannot exceed maximum hit dice
        
        Args:
            amount: Number of hit dice to recover
            
        Returns:
            int: Actual number of hit dice recovered
        """
        pass
    
    @abstractmethod
    def get_recoverable_resources(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Get all resources that can be recovered by a specific rest type.
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Dictionary of recoverable resources
        """
        pass
    
    @abstractmethod
    def recover_class_resources(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Recover class resources based on rest type.
        
        Per D&D 2024 rules:
        - Different class features recover based on rest type
        - Examples: Channel Divinity (short), Rage uses (long), etc.
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Dictionary mapping resource names to recovery amounts
        """
        pass
    
    @abstractmethod
    def recover_spell_slots(self) -> Dict[int, int]:
        """
        Recover spell slots after a long rest.
        
        Per D&D 2024 rules:
        - Long rest restores all expended spell slots
        - Warlocks have special rules (recover on short rest)
        
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to slots recovered
        """
        pass
    
    @abstractmethod
    def can_benefit_from_long_rest(self) -> Tuple[bool, str]:
        """
        Check if character can benefit from a long rest.
        
        Per D&D 2024 rules:
        - Character can only benefit from one long rest per 24 hours
        - Character must have at least 1 HP to benefit from a rest
        
        Returns:
            Tuple[bool, str]: (Can benefit, explanation)
        """
        pass
    
    @abstractmethod
    def is_resting_interrupted(self, activity_time_minutes: int, is_strenuous: bool) -> bool:
        """
        Check if a rest is interrupted.
        
        Per D&D 2024 rules:
        - Short rest: Interrupted by any combat or strenuous activity
        - Long rest: Can include up to 2 hours of light activity
        - Long rest: Interrupted by 1+ hour of strenuous activity
        
        Args:
            activity_time_minutes: Duration of the activity in minutes
            is_strenuous: Whether the activity is strenuous
            
        Returns:
            bool: True if rest is interrupted
        """
        pass
    
    @abstractmethod
    def get_time_since_last_long_rest(self) -> float:
        """
        Get time elapsed since the last long rest.
        
        Returns:
            float: Hours since last long rest
        """
        pass
    
    @abstractmethod
    def handle_special_rest_traits(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Apply special traits that modify resting.
        
        Per D&D 2024 rules, some species/classes have special rest traits:
        - Elves (Trance): Can get the benefits of a long rest in 4 hours
        - Warforged: Don't sleep but must still rest to benefit
        - Some feats/items may modify rest benefits
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Effects of special traits
        """
        pass
    
    @abstractmethod
    def recover_magic_item_charges(self) -> Dict[str, int]:
        """
        Recover magic item charges.
        
        Per D&D 2024 rules:
        - Many magic items recover charges at dawn
        - Some have different recovery schedules
        
        Returns:
            Dict[str, int]: Dictionary mapping item names to charges recovered
        """
        pass
    
    @abstractmethod
    def roll_for_exhaustion(self, sleep_hours: int) -> Tuple[bool, int]:
        """
        Roll for exhaustion after insufficient rest.
        
        Per D&D 2024 rules:
        - Characters who don't get a full long rest might gain exhaustion
        - DC 10 Constitution saving throw to avoid gaining a level of exhaustion
        
        Args:
            sleep_hours: Hours of sleep obtained
            
        Returns:
            Tuple[bool, int]: (Gained exhaustion, new exhaustion level)
        """
        pass
    
    @abstractmethod
    def restore_expended_features(self, feature_name: str) -> bool:
        """
        Restore a specific expended feature.
        
        Args:
            feature_name: Name of the feature to restore
            
        Returns:
            bool: True if successfully restored
        """
        pass
    
    @abstractmethod
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current resting state of the character.
        
        Returns:
            Dict[str, Any]: Dictionary with:
                - current_hp: Current hit points
                - max_hp: Maximum hit points
                - hit_dice: Available hit dice
                - exhaustion: Current exhaustion level
                - resources: Available class resources
                - spell_slots: Available spell slots
        """
        pass
    
    @abstractmethod
    def simulate_rest_benefits(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Simulate the benefits of a rest without applying them.
        
        A useful preview function for players.
        
        Args:
            rest_type: Type of rest to simulate
            
        Returns:
            Dict[str, Any]: Potential benefits
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resting data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of resting state
        """
        pass

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


