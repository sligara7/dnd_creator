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