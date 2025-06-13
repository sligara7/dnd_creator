from typing import Dict, List, Type, Optional
from ...core.abstractions.character_class import AbstractCharacterClass
from ...core.abstractions.species import AbstractSpecies
from ...core.abstractions.equipment import AbstractWeapon, AbstractArmor

class ContentRegistry:
    """
    Registry for all game content implementations.
    
    This allows for dynamic loading of custom content while ensuring
    all implementations follow the abstract contracts.
    """
    
    def __init__(self):
        self._classes: Dict[str, Type[AbstractCharacterClass]] = {}
        self._species: Dict[str, Type[AbstractSpecie]] = {}
        self._weapons: Dict[str, Type[AbstractWeapon]] = {}
        self._armor: Dict[str, Type[AbstractArmor]] = {}
    
    # === Class Registration ===
    
    def register_class(self, class_impl: Type[AbstractCharacterClass]) -> None:
        """Register a character class implementation."""
        # Validate that it properly implements the abstract class
        if not issubclass(class_impl, AbstractCharacterClass):
            raise ValueError(f"{class_impl} must inherit from AbstractCharacterClass")
        
        instance = class_impl()
        self._classes[instance.class_name] = class_impl
    
    def get_class(self, class_name: str) -> Optional[AbstractCharacterClass]:
        """Get character class implementation by name."""
        class_type = self._classes.get(class_name)
        return class_type() if class_type else None
    
    def list_available_classes(self) -> List[str]:
        """List all registered character classes."""
        return list(self._classes.keys())
    
    # === Species Registration ===
    
    def register_species(self, species_impl: Type[AbstractSpecies]) -> None:
        """Register a species implementation."""
        if not issubclass(species_impl, AbstractSpecies):
            raise ValueError(f"{species_impl} must inherit from AbstractSpecies")
        
        instance = species_impl()
        self._species[instance.species_name] = species_impl
    
    def get_species(self, species_name: str) -> Optional[AbstractSpecies]:
        """Get species implementation by name."""
        species_type = self._species.get(species_name)
        return species_type() if species_type else None
    
    def list_available_species(self) -> List[str]:
        """List all registered species."""
        return list(self._species.keys())
    
    # === Equipment Registration ===
    
    def register_weapon(self, weapon_impl: Type[AbstractWeapon]) -> None:
        """Register a weapon implementation."""
        if not issubclass(weapon_impl, AbstractWeapon):
            raise ValueError(f"{weapon_impl} must inherit from AbstractWeapon")
        
        instance = weapon_impl()
        self._weapons[instance.name] = weapon_impl
    
    def register_armor(self, armor_impl: Type[AbstractArmor]) -> None:
        """Register an armor implementation."""
        if not issubclass(armor_impl, AbstractArmor):
            raise ValueError(f"{armor_impl} must inherit from AbstractArmor")
        
        instance = armor_impl()
        self._armor[instance.name] = armor_impl
    
    # === Validation Methods ===
    
    def validate_class_implementation(self, class_impl: Type[AbstractCharacterClass]) -> List[str]:
        """Validate that a class implementation follows D&D rules."""
        errors = []
        
        try:
            instance = class_impl()
            
            # Validate hit die is valid D&D size
            if instance.hit_die not in [4, 6, 8, 10, 12]:
                errors.append(f"Invalid hit die: {instance.hit_die}. Must be d4, d6, d8, d10, or d12")
            
            # Validate primary abilities are valid
            valid_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            for ability in instance.primary_ability:
                if ability not in valid_abilities:
                    errors.append(f"Invalid primary ability: {ability}")
            
            # Validate saving throw proficiencies
            for save in instance.saving_throw_proficiencies:
                if save not in valid_abilities:
                    errors.append(f"Invalid saving throw proficiency: {save}")
            
            if len(instance.saving_throw_proficiencies) != 2:
                errors.append("Classes must have exactly 2 saving throw proficiencies")
            
        except Exception as e:
            errors.append(f"Failed to instantiate class: {str(e)}")
        
        return errors
    
    def validate_species_implementation(self, species_impl: Type[AbstractSpecies]) -> List[str]:
        """Validate that a species implementation follows D&D rules."""
        errors = []
        
        try:
            instance = species_impl()
            
            # Validate size
            valid_sizes = ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]
            if instance.size not in valid_sizes:
                errors.append(f"Invalid size: {instance.size}")
            
            # Validate ability score increases don't exceed limits
            asi = instance.get_ability_score_increases()
            total_asi = sum(asi.values())
            if total_asi > 3:  # Most species give +2/+1 or +3 total
                errors.append(f"Total ability score increases ({total_asi}) exceed typical limits")
            
        except Exception as e:
            errors.append(f"Failed to instantiate species: {str(e)}")
        
        return errors

# Auto-register core D&D content
def register_core_content(registry: ContentRegistry) -> None:
    """Register all core D&D 5e content."""
    from ..content.classes.fighter import Fighter
    from ..content.classes.wizard import Wizard
    from ..content.classes.cleric import Cleric
    # ... import all core classes
    
    from ..content.species.human import Human
    from ..content.species.elf import Elf
    from ..content.species.dwarf import Dwarf
    # ... import all core species
    
    # Register classes
    registry.register_class(Fighter)
    registry.register_class(Wizard)
    registry.register_class(Cleric)
    # ... register all classes
    
    # Register species
    registry.register_species(Human)
    registry.register_species(Elf)
    registry.register_species(Dwarf)
    # ... register all species

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
    
    def register_core_species(self) -> None:
        """Register all core D&D 2024 species."""
        from ..content.species.human import Human
        from ..content.species.elf import Elf
        from ..content.species.dwarf import Dwarf
        # ... other species imports
        
        # Register core species
        self.register_species(Human)
        self.register_species(Elf)
        self.register_species(Dwarf)
        # ... register other species

    def get_core_species_names(self) -> List[str]:
        """Get names of core D&D 2024 species."""
        return [
            "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome",
            "Goliath", "Halfling", "Human", "Orc", "Tiefling"
        ]
    
# Update the DOMAIN_COMPONENTS to reflect actual implementation status
DOMAIN_COMPONENTS = {
    "abstractions": {
        "implemented": ["AbstractContentValidator"],  # Only if actually implemented
        "missing": ["AbstractCharacterClass", "AbstractSpecies", "AbstractEquipment", 
                   "AbstractWeapon", "AbstractArmor", "AbstractSpell", "AbstractFeat"]
    },
    "entities": {
        "implemented": ["CharacterConcept", "ContentCollection"],  # Based on file evidence
        "missing": ["Character", "GeneratedContent"]
    },
    "value_objects": {
        "implemented": ["ValidationResult", "BalanceMetrics"],  # Inferred from usage
        "missing": ["ContentMetadata", "GenerationConstraints", "ThematicElements"]
    },
    "utilities": {
        "implemented": ["balance_calculator", "content_utils", "naming_validator", 
                       "mechanical_parser", "rule_checker"],  # Based on file evidence
        "missing": []
    },
    "enums": {
        "implemented": ["content_types", "validation_types", "dnd_constants"],
        "missing": ["generation_methods", "mechanical_category"]
    },
    "exceptions": {
        "implemented": ["generation_errors", "validation_errors", "rule_violation_errors"],
        "missing": []
    }
}