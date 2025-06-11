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