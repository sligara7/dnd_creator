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