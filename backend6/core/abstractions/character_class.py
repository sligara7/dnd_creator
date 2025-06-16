from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from ..enums.dnd_constants import (
    Ability, SpellcastingType, ClassResource, SubclassType, SpellLevel
)
from ..enums.content_types import ContentSource
from ..enums.validation_types import ValidationResult


@dataclass
class ClassFeature:
    """Value object representing a character class feature."""
    name: str
    description: str
    level_acquired: int
    feature_type: str  # "passive", "active", "resource", "choice"
    uses_per_rest: Optional[str] = None  # "short", "long", "none"
    prerequisites: Optional[List[str]] = None
    choices: Optional[Dict[str, Any]] = None  # For features with choices


class AbstractCharacterClass(ABC):
    """
    Abstract contract for all D&D character classes in the Creative Content Framework.
    
    This interface defines the rules that both official and generated character classes
    must follow, ensuring D&D 2024 rule compliance while enabling creative freedom.
    
    Per D&D 2024 rules, all character classes must provide:
    - Hit die and proficiency progression
    - Class features at specific levels
    - Spellcasting rules (if applicable)
    - Multiclassing requirements
    - Subclass selection rules
    """
    
    # D&D 2024 standardized progression
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    MAX_LEVEL = 20
    
    @property
    @abstractmethod
    def class_name(self) -> str:
        """Official name of the character class."""
        pass
    
    @property
    @abstractmethod
    def hit_die(self) -> int:
        """Hit die size (6, 8, 10, or 12)."""
        pass
    
    @property
    @abstractmethod
    def primary_abilities(self) -> List[Ability]:
        """Primary ability scores for this class."""
        pass
    
    @property
    @abstractmethod
    def saving_throw_proficiencies(self) -> List[Ability]:
        """Saving throw proficiencies granted by this class."""
        pass
    
    @property 
    @abstractmethod
    def content_source(self) -> ContentSource:
        """Source of this class (core rules, generated, custom, etc.)."""
        pass
    
    @abstractmethod
    def get_class_features(self, level: int) -> List[ClassFeature]:
        """
        Get all class features available at the specified level.
        
        Args:
            level: Class level (1-20)
            
        Returns:
            List of ClassFeature objects available at that level
        """
        pass
    
    @abstractmethod
    def get_all_features_through_level(self, level: int) -> List[ClassFeature]:
        """
        Get all class features from level 1 through the specified level.
        
        Args:
            level: Maximum class level to include
            
        Returns:
            List of all ClassFeature objects through that level
        """
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self) -> List[int]:
        """
        Get levels at which this class gains Ability Score Improvements.
        
        Per D&D 2024 rules, most classes get ASIs at levels 4, 8, 12, 16, 19.
        Some classes (Fighter, Rogue) get additional ASIs.
        
        Returns:
            List of levels with ASI opportunities
        """
        pass
    
    @abstractmethod
    def get_subclass_selection_level(self) -> int:
        """
        Get the level at which this class chooses a subclass.
        
        Per D&D 2024 rules:
        - Most classes choose at level 3
        - Some choose at level 1 (Cleric, Sorcerer)
        - Some choose at level 2 (Wizard)
        
        Returns:
            Level at which subclass is chosen
        """
        pass
    
    @abstractmethod
    def get_spellcasting_info(self) -> Optional[Dict[str, Any]]:
        """
        Get spellcasting information if this class has spellcasting.
        
        Returns:
            Dictionary with spellcasting details or None if not a spellcaster
        """
        pass
    
    @abstractmethod
    def get_spell_slots_by_level(self, class_level: int) -> Dict[int, int]:
        """
        Get spell slots available at a specific class level.
        
        Args:
            class_level: Level in this class
            
        Returns:
            Dictionary mapping spell levels to number of slots
        """
        pass
    
    @abstractmethod
    def get_spells_known_by_level(self, class_level: int, 
                                ability_modifier: int = 0) -> Dict[str, int]:
        """
        Get number of spells known/prepared at a specific level.
        
        Args:
            class_level: Level in this class
            ability_modifier: Spellcasting ability modifier (for prepared casters)
            
        Returns:
            Dictionary with cantrips known, spells known/prepared
        """
        pass
    
    @abstractmethod
    def validate_multiclass_prerequisites(self, character_data: Dict[str, Any]) -> List[str]:
        """
        Validate prerequisites for multiclassing into this class.
        
        Per D&D 2024 rules, multiclassing requires minimum ability scores
        in both the current class and the new class.
        
        Args:
            character_data: Character information including ability scores
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies gained when multiclassing into this class.
        
        Per D&D 2024 rules, multiclass proficiencies are typically
        a subset of the full class starting proficiencies.
        
        Returns:
            Dictionary of proficiency categories and their values
        """
        pass
    
    @abstractmethod
    def get_class_resources(self, level: int) -> Dict[ClassResource, int]:
        """
        Get class-specific resources available at a given level.
        
        Examples: Rage uses, Bardic Inspiration, Channel Divinity, etc.
        
        Args:
            level: Class level
            
        Returns:
            Dictionary of class resources and their quantities
        """
        pass
    
    @abstractmethod
    def get_equipment_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get equipment proficiencies granted by this class.
        
        Returns:
            Dictionary with armor, weapon, and tool proficiencies
        """
        pass
    
    @abstractmethod
    def get_skill_choices(self) -> Tuple[List[str], int]:
        """
        Get available skill choices for this class.
        
        Returns:
            Tuple of (available skills, number to choose)
        """
        pass
    
    @abstractmethod
    def get_starting_equipment_options(self) -> Dict[str, Any]:
        """
        Get starting equipment options for this class.
        
        Returns:
            Dictionary describing equipment choices
        """
        pass
    
    @abstractmethod
    def validate_class_balance(self) -> List[ValidationResult]:
        """
        Validate that this class meets D&D balance guidelines.
        
        For generated/custom classes, this ensures:
        - Appropriate power scaling
        - Balanced feature distribution
        - Reasonable resource management
        
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def get_thematic_elements(self) -> Dict[str, Any]:
        """
        Get thematic elements that define this class's identity.
        
        Used by the Creative Content Framework for generating
        complementary content (equipment, spells, etc.)
        
        Returns:
            Dictionary of thematic elements and flavor
        """
        pass
    
    def calculate_hit_points_for_level(self, level: int, constitution_modifier: int,
                                     method: str = "average") -> int:
        """
        Calculate hit points gained at a specific level.
        
        Args:
            level: Character level (1 for first level, 2+ for level-ups)
            constitution_modifier: Constitution modifier
            method: "max", "average", or "roll"
            
        Returns:
            Hit points gained at that level
        """
        if level == 1:
            return self.hit_die + constitution_modifier
        
        if method == "max":
            return self.hit_die + constitution_modifier
        elif method == "average":
            return (self.hit_die // 2) + 1 + constitution_modifier
        else:  # "roll" - would integrate with dice system
            return (self.hit_die // 2) + 1 + constitution_modifier  # Default to average
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Get proficiency bonus for a given level (standardized across all classes)."""
        return self.PROFICIENCY_BONUS_BY_LEVEL.get(level, 2)
    
    def calculate_total_hit_points(self, class_levels: Dict[str, int], 
                                 constitution_modifier: int,
                                 method: str = "average") -> int:
        """
        Calculate total hit points for multiclass characters.
        
        Args:
            class_levels: Dictionary of class names to levels
            constitution_modifier: Constitution modifier
            method: Hit point calculation method
            
        Returns:
            Total hit points across all classes
        """
        total_hp = 0
        character_level = 0
        
        for class_name, levels in class_levels.items():
            for level in range(1, levels + 1):
                character_level += 1
                if character_level == 1:
                    # First level always max
                    total_hp += self.hit_die + constitution_modifier
                else:
                    total_hp += self.calculate_hit_points_for_level(
                        level, constitution_modifier, method
                    )
        
        return total_hp