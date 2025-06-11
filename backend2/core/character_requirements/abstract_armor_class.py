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