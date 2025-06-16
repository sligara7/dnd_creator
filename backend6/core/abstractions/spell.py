from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from ..enums.dnd_constants import (
    SpellLevel, MagicSchool, CastingTime, SpellRange, SpellDuration, 
    DamageType, AreaOfEffect
)
from ..enums.content_types import ContentSource
from ..enums.validation_types import ValidationResult


class AbstractSpell(ABC):
    """
    Abstract contract for all D&D spells in the Creative Content Framework.
    
    This interface defines the rules that both official and generated spells
    must follow, ensuring D&D 2024 rule compliance while enabling creative freedom.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Spell name."""
        pass
    
    @property
    @abstractmethod
    def level(self) -> SpellLevel:
        """Spell level (0-9)."""
        pass
    
    @property
    @abstractmethod
    def school(self) -> MagicSchool:
        """School of magic."""
        pass
    
    @property
    @abstractmethod
    def content_source(self) -> ContentSource:
        """Source of this spell (core rules, generated, custom, etc.)."""
        pass
    
    @abstractmethod
    def get_casting_time(self) -> Union[CastingTime, str]:
        """
        Get spell casting time.
        
        Returns:
            Standard casting time or custom string
        """
        pass
    
    @abstractmethod
    def get_range(self) -> Union[SpellRange, int, str]:
        """
        Get spell range.
        
        Returns:
            Standard range, distance in feet, or custom description
        """
        pass
    
    @abstractmethod
    def get_duration(self) -> Union[SpellDuration, str]:
        """
        Get spell duration.
        
        Returns:
            Standard duration or custom description
        """
        pass
    
    @abstractmethod
    def get_components(self) -> Dict[str, Any]:
        """
        Get spell components required.
        
        Returns:
            Dictionary with verbal, somatic, material components
        """
        pass
    
    @abstractmethod
    def requires_concentration(self) -> bool:
        """
        Check if spell requires concentration.
        
        Returns:
            True if concentration is required
        """
        pass
    
    @abstractmethod
    def is_ritual(self) -> bool:
        """
        Check if spell can be cast as a ritual.
        
        Returns:
            True if ritual casting is allowed
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get full spell description.
        
        Returns:
            Complete spell description
        """
        pass
    
    @abstractmethod
    def get_classes(self) -> List[str]:
        """
        Get classes that can learn this spell.
        
        Returns:
            List of class names
        """
        pass
    
    @abstractmethod
    def get_damage_info(self) -> Optional[Dict[str, Any]]:
        """
        Get damage information if spell deals damage.
        
        Returns:
            Dictionary with damage dice, type, etc. or None
        """
        pass
    
    @abstractmethod
    def get_healing_info(self) -> Optional[Dict[str, Any]]:
        """
        Get healing information if spell heals.
        
        Returns:
            Dictionary with healing dice, type, etc. or None
        """
        pass
    
    @abstractmethod
    def get_saving_throw(self) -> Optional[str]:
        """
        Get saving throw required if any.
        
        Returns:
            Ability name for save or None
        """
        pass
    
    @abstractmethod
    def get_area_of_effect(self) -> Optional[Dict[str, Any]]:
        """
        Get area of effect if applicable.
        
        Returns:
            Dictionary with shape, size, etc. or None
        """
        pass
    
    @abstractmethod
    def get_higher_level_effects(self) -> Optional[str]:
        """
        Get description of effects when cast at higher levels.
        
        Returns:
            Higher level description or None
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell attack bonus for this spell.
        
        Args:
            character_data: Character information
            
        Returns:
            Spell attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_save_dc(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate saving throw DC for this spell.
        
        Args:
            character_data: Character information
            
        Returns:
            Spell save DC
        """
        pass
    
    @abstractmethod
    def validate_spell_balance(self) -> List[ValidationResult]:
        """
        Validate spell power level for its level and school.
        
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def get_thematic_elements(self) -> Dict[str, Any]:
        """
        Get thematic elements for content generation.
        
        Returns:
            Dictionary of themes, keywords, and flavor elements
        """
        pass