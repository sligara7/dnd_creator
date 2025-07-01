# ## **3. `character_models.py`**
# **Character sheet and data models**
# - **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`, `CharacterIterationCache`
# - **Purpose**: Character data structures, hit points, equipment, calculated statistics
# - **Dependencies**: `core_models.py`
#
# REFACTORED: Added journal tracking, D&D 5e 2024 exhaustion rules, comprehensive conditions,
# getter/setter methods for RESTful API access


from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from enum import Enum

# Import from core_models.py
from core_models import (
    ProficiencyLevel,
    AbilityScoreSource,
    AbilityScore,
    ASIManager,
    CharacterLevelManager,
    MagicItemManager,
    SpellcastingManager
)

# Import from centralized enums
from enums import DnDCondition, FeatureType, FeatureCategory, FeatureUsage, SpeciesTraitType, ClassFeatureType

# ============================================================================
# D&D 5E 2024 CONDITIONS
# ============================================================================

class ExhaustionLevel:
    """D&D 5e 2024 Exhaustion level effects."""
    
    EFFECTS = {
        0: {"d20_penalty": 0, "speed_penalty": 0, "description": "No exhaustion"},
        1: {"d20_penalty": -2, "speed_penalty": -5, "description": "Fatigued"},
        2: {"d20_penalty": -4, "speed_penalty": -10, "description": "Tired"},
        3: {"d20_penalty": -6, "speed_penalty": -15, "description": "Weary"},
        4: {"d20_penalty": -8, "speed_penalty": -20, "description": "Exhausted"},
        5: {"d20_penalty": -10, "speed_penalty": -25, "description": "Severely Exhausted"},
        6: {"d20_penalty": 0, "speed_penalty": 0, "description": "Death"}
    }
    
    @classmethod
    def get_effects(cls, level: int) -> Dict[str, Any]:
        """Get effects for a given exhaustion level."""
        return cls.EFFECTS.get(min(max(level, 0), 6), cls.EFFECTS[0])
    
    @classmethod
    def is_dead(cls, level: int) -> bool:
        """Check if character dies from exhaustion."""
        return level >= 6

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CHARACTER DATA MODELS
# ============================================================================

class CharacterFeature:
    """Represents a single character feature or trait."""
    
    def __init__(self, name: str, description: str, feature_type: FeatureType, 
                 category: FeatureCategory = FeatureCategory.PASSIVE,
                 usage: FeatureUsage = FeatureUsage.ALWAYS):
        self.name = name
        self.description = description
        self.feature_type = feature_type
        self.category = category
        self.usage = usage
        self.source = ""  # What granted this feature (class name, species, background, etc.)
        self.level_gained = 1  # What level this feature was gained
        self.prerequisites = []  # Any prerequisites for this feature
        self.mechanical_effects = {}  # Concrete mechanical benefits
        self.active = True  # Whether the feature is currently active
        self.uses_remaining = None  # For limited-use features
        self.max_uses = None  # Maximum uses per rest/day
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature to dictionary for API responses."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.feature_type.value,
            "category": self.category.value,
            "usage": self.usage.value,
            "source": self.source,
            "level_gained": self.level_gained,
            "prerequisites": self.prerequisites,
            "mechanical_effects": self.mechanical_effects,
            "active": self.active,
            "uses_remaining": self.uses_remaining,
            "max_uses": self.max_uses
        }

class FeaturesAndTraitsManager:
    """Manages all character features and traits from various sources."""
    
    def __init__(self, character_core: 'CharacterCore'):
        self.character_core = character_core
        self.features: List[CharacterFeature] = []
        self.species_traits: List[CharacterFeature] = []
        self.class_features: Dict[str, List[CharacterFeature]] = {}  # class_name -> features
        self.background_features: List[CharacterFeature] = []
        self.feat_features: List[CharacterFeature] = []
        self.item_features: List[CharacterFeature] = []
        self.temporary_features: List[CharacterFeature] = []
        
    def add_species_trait(self, trait_name: str, description: str, trait_type: SpeciesTraitType,
                         category: FeatureCategory = FeatureCategory.PASSIVE) -> CharacterFeature:
        """Add a species trait to the character."""
        feature = CharacterFeature(
            name=trait_name,
            description=description,
            feature_type=FeatureType.SPECIES_TRAIT,
            category=category
        )
        feature.source = self.character_core.species
        feature.level_gained = 1  # Species traits are gained at character creation
        
        self.species_traits.append(feature)
        self.features.append(feature)
        
        logger.info(f"Added species trait: {trait_name} from {self.character_core.species}")
        return feature
    
    def add_class_feature(self, class_name: str, feature_name: str, description: str,
                         level_gained: int, feature_type: ClassFeatureType,
                         category: FeatureCategory = FeatureCategory.PASSIVE,
                         usage: FeatureUsage = FeatureUsage.ALWAYS) -> CharacterFeature:
        """Add a class feature to the character."""
        feature = CharacterFeature(
            name=feature_name,
            description=description,
            feature_type=FeatureType.CLASS_FEATURE,
            category=category,
            usage=usage
        )
        feature.source = class_name
        feature.level_gained = level_gained
        
        if class_name not in self.class_features:
            self.class_features[class_name] = []
        
        self.class_features[class_name].append(feature)
        self.features.append(feature)
        
        logger.info(f"Added class feature: {feature_name} from {class_name} at level {level_gained}")
        return feature
    
    def add_background_feature(self, feature_name: str, description: str,
                              category: FeatureCategory = FeatureCategory.SOCIAL) -> CharacterFeature:
        """Add a background feature to the character."""
        feature = CharacterFeature(
            name=feature_name,
            description=description,
            feature_type=FeatureType.BACKGROUND_FEATURE,
            category=category
        )
        feature.source = self.character_core.background
        feature.level_gained = 1  # Background features are gained at character creation
        
        self.background_features.append(feature)
        self.features.append(feature)
        
        logger.info(f"Added background feature: {feature_name} from {self.character_core.background}")
        return feature
    
    def add_feat_feature(self, feat_name: str, feature_name: str, description: str,
                        category: FeatureCategory = FeatureCategory.UTILITY,
                        usage: FeatureUsage = FeatureUsage.ALWAYS) -> CharacterFeature:
        """Add a feat-granted feature to the character."""
        feature = CharacterFeature(
            name=feature_name,
            description=description,
            feature_type=FeatureType.FEAT_ABILITY,
            category=category,
            usage=usage
        )
        feature.source = f"Feat: {feat_name}"
        
        self.feat_features.append(feature)
        self.features.append(feature)
        
        logger.info(f"Added feat feature: {feature_name} from feat {feat_name}")
        return feature
    
    def add_item_feature(self, item_name: str, feature_name: str, description: str,
                        category: FeatureCategory = FeatureCategory.UTILITY,
                        temporary: bool = False) -> CharacterFeature:
        """Add a magic item granted feature to the character."""
        feature = CharacterFeature(
            name=feature_name,
            description=description,
            feature_type=FeatureType.MAGIC_ITEM_PROPERTY,
            category=category
        )
        feature.source = f"Item: {item_name}"
        
        if temporary:
            self.temporary_features.append(feature)
        else:
            self.item_features.append(feature)
        
        self.features.append(feature)
        
        logger.info(f"Added item feature: {feature_name} from {item_name} (temporary: {temporary})")
        return feature
    
    def get_features_by_type(self, feature_type: FeatureType) -> List[CharacterFeature]:
        """Get all features of a specific type."""
        return [f for f in self.features if f.feature_type == feature_type]
    
    def get_features_by_category(self, category: FeatureCategory) -> List[CharacterFeature]:
        """Get all features of a specific category."""
        return [f for f in self.features if f.category == category]
    
    def get_features_by_source(self, source: str) -> List[CharacterFeature]:
        """Get all features from a specific source."""
        return [f for f in self.features if f.source == source]
    
    def get_features_at_level(self, level: int) -> List[CharacterFeature]:
        """Get all features gained at a specific level."""
        return [f for f in self.features if f.level_gained == level]
    
    def get_active_features(self) -> List[CharacterFeature]:
        """Get all currently active features."""
        return [f for f in self.features if f.active]
    
    def get_combat_features(self) -> List[CharacterFeature]:
        """Get all combat-related features."""
        return self.get_features_by_category(FeatureCategory.COMBAT)
    
    def get_exploration_features(self) -> List[CharacterFeature]:
        """Get all exploration-related features."""
        return self.get_features_by_category(FeatureCategory.EXPLORATION)
    
    def get_social_features(self) -> List[CharacterFeature]:
        """Get all social interaction features."""
        return self.get_features_by_category(FeatureCategory.SOCIAL)
    
    def get_spellcasting_features(self) -> List[CharacterFeature]:
        """Get all spellcasting-related features."""
        return self.get_features_by_category(FeatureCategory.SPELLCASTING)
    
    def deactivate_feature(self, feature_name: str) -> bool:
        """Deactivate a feature (for temporary effects or conditions)."""
        for feature in self.features:
            if feature.name == feature_name:
                feature.active = False
                logger.info(f"Deactivated feature: {feature_name}")
                return True
        return False
    
    def reactivate_feature(self, feature_name: str) -> bool:
        """Reactivate a previously deactivated feature."""
        for feature in self.features:
            if feature.name == feature_name:
                feature.active = True
                logger.info(f"Reactivated feature: {feature_name}")
                return True
        return False
    
    def remove_temporary_features(self) -> int:
        """Remove all temporary features and return count removed."""
        removed_count = len(self.temporary_features)
        
        # Remove from main features list
        self.features = [f for f in self.features if f not in self.temporary_features]
        
        # Clear temporary features
        self.temporary_features.clear()
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} temporary features")
        
        return removed_count
    
    def use_limited_feature(self, feature_name: str) -> bool:
        """Use a limited-use feature, decreasing its remaining uses."""
        for feature in self.features:
            if (feature.name == feature_name and 
                feature.uses_remaining is not None and 
                feature.uses_remaining > 0):
                feature.uses_remaining -= 1
                logger.info(f"Used feature: {feature_name} ({feature.uses_remaining} uses remaining)")
                return True
        return False
    
    def reset_feature_uses(self, rest_type: str = "long_rest") -> int:
        """Reset feature uses based on rest type."""
        reset_count = 0
        
        for feature in self.features:
            if feature.max_uses is not None:
                if (rest_type == "long_rest" or 
                    (rest_type == "short_rest" and feature.usage == FeatureUsage.SHORT_REST)):
                    feature.uses_remaining = feature.max_uses
                    reset_count += 1
        
        if reset_count > 0:
            logger.info(f"Reset {reset_count} features after {rest_type}")
        
        return reset_count
    
    def get_features_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all features."""
        return {
            "total_features": len(self.features),
            "active_features": len(self.get_active_features()),
            "species_traits": len(self.species_traits),
            "class_features": {class_name: len(features) for class_name, features in self.class_features.items()},
            "background_features": len(self.background_features),
            "feat_features": len(self.feat_features),
            "item_features": len(self.item_features),
            "temporary_features": len(self.temporary_features),
            "by_category": {
                category.value: len(self.get_features_by_category(category))
                for category in FeatureCategory
            },
            "by_usage": {
                usage.value: len([f for f in self.features if f.usage == usage])
                for usage in FeatureUsage
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all features to dictionary for API responses."""
        return {
            "features": [feature.to_dict() for feature in self.features],
            "species_traits": [feature.to_dict() for feature in self.species_traits],
            "class_features": {
                class_name: [feature.to_dict() for feature in features]
                for class_name, features in self.class_features.items()
            },
            "background_features": [feature.to_dict() for feature in self.background_features],
            "feat_features": [feature.to_dict() for feature in self.feat_features],
            "item_features": [feature.to_dict() for feature in self.item_features],
            "temporary_features": [feature.to_dict() for feature in self.temporary_features],
            "summary": self.get_features_summary()
        }

class CharacterCore:
    """Enhanced core character data with level and ASI management."""
    
    def __init__(self, name: str = ""):
        # Basic identity
        self.name = name
        self.species = ""
        self.character_classes: Dict[str, int] = {}
        self.background = ""
        self.alignment = ["Neutral", "Neutral"]
        
        # Enhanced ability scores
        self.strength = AbilityScore(10)
        self.dexterity = AbilityScore(10)
        self.constitution = AbilityScore(10)
        self.intelligence = AbilityScore(10)
        self.wisdom = AbilityScore(10)
        self.charisma = AbilityScore(10)
        
        # Managers
        self.level_manager = CharacterLevelManager()
        self.magic_item_manager = MagicItemManager()
        # Features manager will be initialized after class definition
        
        # Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.armor_proficiency: List[str] = []
        self.weapon_proficiency: List[str] = []
        self.tool_proficiency: List[str] = []
        self.languages: List[str] = []
        
        # Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory = ""
        
        # Enhanced backstory elements
        self.detailed_backstory: Dict[str, str] = {}
        self.custom_content_used: List[str] = []
        
        # Spellcasting information (NEW)
        self.spellcasting_info: Dict[str, Any] = {}
        self._update_spellcasting_info()
        
        # Initialize features manager after all core attributes are set
        self.features_manager = FeaturesAndTraitsManager(self)
    
    @property
    def total_level(self) -> int:
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def initiative(self) -> int:
        """Initiative is always equal to the Dexterity modifier."""
        return self.dexterity.modifier
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        ability_map = {
            "strength": self.strength, "dexterity": self.dexterity,
            "constitution": self.constitution, "intelligence": self.intelligence,
            "wisdom": self.wisdom, "charisma": self.charisma
        }
        return ability_map.get(ability.lower())
    
    def level_up(self, class_name: str, asi_choice: Optional[Dict[str, Any]] = None):
        """Level up in a specific class."""
        current_level = self.character_classes.get(class_name, 0)
        new_level = current_level + 1
        
        self.level_manager.add_level(class_name, new_level, asi_choice)
    
    def apply_starting_ability_scores(self, scores: Dict[str, int]):
        """Apply starting ability scores (from character creation)."""
        for ability, score in scores.items():
            ability_obj = self.get_ability_score(ability)
            if ability_obj:
                ability_obj.base_score = score
    
    def apply_species_bonuses(self, bonuses: Dict[str, int], species_name: str):
        """Apply species-based ability score bonuses (for older editions/variants)."""
        for ability, bonus in bonuses.items():
            ability_obj = self.get_ability_score(ability)
            if ability_obj and bonus != 0:
                ability_obj.add_improvement(
                    AbilityScoreSource.SPECIES_TRAIT,
                    bonus,
                    f"{species_name} species bonus",
                    0  # Gained at character creation
                )
    
    def set_detailed_backstory(self, backstory_elements: Dict[str, str]):
        """Set the detailed backstory elements."""
        self.detailed_backstory = backstory_elements
        # Set main backstory for compatibility
        self.backstory = backstory_elements.get("main_backstory", "")
    
    def _update_spellcasting_info(self):
        """Update spellcasting information based on current classes."""
        self.spellcasting_info = SpellcastingManager.get_combined_spellcasting(self.character_classes)
    
    def get_spellcasting_info(self) -> Dict[str, Any]:
        """Get current spellcasting information."""
        # Refresh spellcasting info in case classes have changed
        self._update_spellcasting_info()
        return self.spellcasting_info.copy()
    
    def is_spellcaster(self) -> bool:
        """Check if character is a spellcaster."""
        return self.get_spellcasting_info().get("is_spellcaster", False)
    
    def can_swap_spells_on_rest(self) -> bool:
        """Check if character can swap spells after a long rest."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return False
        
        # Check if any spellcasting class allows spell swapping
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            if class_info["info"].get("can_swap_spells_on_rest", False):
                return True
        return False
    
    def can_cast_rituals(self) -> bool:
        """Check if character can cast ritual spells."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return False
        
        # Check if any spellcasting class allows ritual casting
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            if class_info["info"].get("can_cast_rituals", False):
                return True
        return False
    
    def get_spellcasting_abilities(self) -> List[str]:
        """Get list of spellcasting abilities used by this character."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return []
        
        abilities = set()
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            abilities.add(class_info["info"]["spellcasting_ability"])
        
        return list(abilities)
    
    def get_spell_save_dc(self, spellcasting_ability: str = None) -> int:
        """Calculate spell save DC for a given spellcasting ability."""
        if not self.is_spellcaster():
            return 8  # Default, though character can't cast spells
        
        # If no ability specified, use primary spellcasting ability
        if not spellcasting_ability:
            abilities = self.get_spellcasting_abilities()
            if not abilities:
                return 8
            spellcasting_ability = abilities[0]  # Use first (primary) ability
        
        # Get ability modifier
        ability_obj = self.get_ability_score(spellcasting_ability)
        if not ability_obj:
            return 8
        
        # Calculate proficiency bonus (simplified - should use level manager)
        proficiency_bonus = 2 + ((self.level - 1) // 4)
        
        return 8 + proficiency_bonus + ability_obj.modifier
    
    def get_spell_attack_bonus(self, spellcasting_ability: str = None) -> int:
        """Calculate spell attack bonus for a given spellcasting ability."""
        if not self.is_spellcaster():
            return 0
        
        # If no ability specified, use primary spellcasting ability
        if not spellcasting_ability:
            abilities = self.get_spellcasting_abilities()
            if not abilities:
                return 0
            spellcasting_ability = abilities[0]
        
        # Get ability modifier
        ability_obj = self.get_ability_score(spellcasting_ability)
        if not ability_obj:
            return 0
        
        # Calculate proficiency bonus (simplified - should use level manager)
        proficiency_bonus = 2 + ((self.level - 1) // 4)
        
        return proficiency_bonus + ability_obj.modifier
    
    # ============================================================================
    # GETTER METHODS FOR API ACCESS
    # ============================================================================
    
    def get_name(self) -> str:
        """Get character name."""
        return self.name
    
    def get_species(self) -> str:
        """Get character species."""
        return self.species
    
    def get_character_classes(self) -> Dict[str, int]:
        """Get character classes and levels."""
        return self.character_classes.copy()
    
    def get_background(self) -> str:
        """Get character background."""
        return self.background
    
    def get_alignment(self) -> List[str]:
        """Get character alignment."""
        return self.alignment.copy()
    
    def get_ability_scores(self) -> Dict[str, int]:
        """Get all ability scores."""
        return {
            "strength": self.strength.total_score,
            "dexterity": self.dexterity.total_score,
            "constitution": self.constitution.total_score,
            "intelligence": self.intelligence.total_score,
            "wisdom": self.wisdom.total_score,
            "charisma": self.charisma.total_score
        }
    
    def get_ability_modifiers(self) -> Dict[str, int]:
        """Get all ability score modifiers."""
        return {
            "strength": self.strength.modifier,
            "dexterity": self.dexterity.modifier,
            "constitution": self.constitution.modifier,
            "intelligence": self.intelligence.modifier,
            "wisdom": self.wisdom.modifier,
            "charisma": self.charisma.modifier
        }
    
    def get_proficiencies(self) -> Dict[str, Any]:
        """Get all proficiencies."""
        return {
            "skills": dict(self.skill_proficiencies),
            "saving_throws": dict(self.saving_throw_proficiencies),
            "armor": self.armor_proficiency.copy(),
            "weapons": self.weapon_proficiency.copy(),
            "tools": self.tool_proficiency.copy(),
            "languages": self.languages.copy()
        }
    
    def get_personality_traits(self) -> List[str]:
        """Get personality traits."""
        return self.personality_traits.copy()
    
    def get_ideals(self) -> List[str]:
        """Get ideals."""
        return self.ideals.copy()
    
    def get_bonds(self) -> List[str]:
        """Get bonds."""
        return self.bonds.copy()
    
    def get_flaws(self) -> List[str]:
        """Get flaws."""
        return self.flaws.copy()
    
    def get_backstory(self) -> str:
        """Get main backstory."""
        return self.backstory
    
    def get_detailed_backstory(self) -> Dict[str, str]:
        """Get detailed backstory elements."""
        return self.detailed_backstory.copy()
    
    # ============================================================================
    # FEATURES AND TRAITS GETTER METHODS
    # ============================================================================
    
    def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all character features and traits."""
        return [feature.to_dict() for feature in self.features_manager.get_active_features()]
    
    def get_species_traits(self) -> List[Dict[str, Any]]:
        """Get all species traits."""
        return [feature.to_dict() for feature in self.features_manager.species_traits]
    
    def get_class_features(self, class_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get class features, optionally filtered by class name."""
        if class_name:
            features = self.features_manager.class_features.get(class_name, [])
            return [feature.to_dict() for feature in features]
        else:
            all_class_features = []
            for features in self.features_manager.class_features.values():
                all_class_features.extend([feature.to_dict() for feature in features])
            return all_class_features
    
    def get_background_features(self) -> List[Dict[str, Any]]:
        """Get all background features."""
        return [feature.to_dict() for feature in self.features_manager.background_features]
    
    def get_feat_features(self) -> List[Dict[str, Any]]:
        """Get all feat-granted features."""
        return [feature.to_dict() for feature in self.features_manager.feat_features]
    
    def get_item_features(self) -> List[Dict[str, Any]]:
        """Get all magic item features."""
        return [feature.to_dict() for feature in self.features_manager.item_features]
    
    def get_features_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get features by category (combat, exploration, social, etc.)."""
        try:
            feature_category = FeatureCategory(category)
            features = self.features_manager.get_features_by_category(feature_category)
            return [feature.to_dict() for feature in features]
        except ValueError:
            logger.warning(f"Invalid feature category: {category}")
            return []
    
    def get_combat_features(self) -> List[Dict[str, Any]]:
        """Get all combat-related features."""
        return [feature.to_dict() for feature in self.features_manager.get_combat_features()]
    
    def get_exploration_features(self) -> List[Dict[str, Any]]:
        """Get all exploration-related features."""
        return [feature.to_dict() for feature in self.features_manager.get_exploration_features()]
    
    def get_social_features(self) -> List[Dict[str, Any]]:
        """Get all social interaction features."""
        return [feature.to_dict() for feature in self.features_manager.get_social_features()]
    
    def get_spellcasting_features(self) -> List[Dict[str, Any]]:
        """Get all spellcasting-related features."""
        return [feature.to_dict() for feature in self.features_manager.get_spellcasting_features()]
    
    def get_features_summary(self) -> Dict[str, Any]:
        """Get a summary of all features and traits."""
        return self.features_manager.get_features_summary()
    
    def get_features_at_level(self, level: int) -> List[Dict[str, Any]]:
        """Get all features gained at a specific level."""
        features = self.features_manager.get_features_at_level(level)
        return [feature.to_dict() for feature in features]
    
    def apply_feat_effects(self):
        """Apply effects from all feats the character has."""
        try:
            # Get all feat features from the features manager
            feat_features = self.get_feat_features()
            
            # Process each feat feature for mechanical effects
            for feat_feature in feat_features:
                feat_name = feat_feature.get("name", "")
                feat_description = feat_feature.get("description", "")
                
                # Apply common feat effects based on feat name/description
                self._apply_individual_feat_effects(feat_name, feat_description)
                
            logger.debug(f"Applied feat effects for character {self.name}")
            
        except Exception as e:
            logger.warning(f"Error applying feat effects: {e}")
    
    def _apply_individual_feat_effects(self, feat_name: str, feat_description: str):
        """Apply effects from a specific feat."""
        try:
            feat_name_lower = feat_name.lower()
            description_lower = feat_description.lower()
            
            # Ability Score Improvement feats
            if "ability score improvement" in feat_name_lower or "asi" in feat_name_lower:
                # ASI feats are typically handled by the level manager
                pass
            
            # Alert feat
            elif "alert" in feat_name_lower:
                # Alert provides +5 to initiative - handled by initiative calculation
                pass
            
            # Lucky feat  
            elif "lucky" in feat_name_lower:
                # Lucky provides luck points - handled by features system
                pass
            
            # Skill-based feats
            elif "skilled" in feat_name_lower:
                # Skilled feat provides skill proficiencies - typically handled during feat selection
                pass
            
            # Weapon Master feat
            elif "weapon master" in feat_name_lower:
                # Weapon proficiencies would be added during feat selection
                pass
            
            # Magic Initiate feat
            elif "magic initiate" in feat_name_lower:
                # Spells would be added to character's spell list during feat selection
                pass
            
            # Most feat effects are handled by the features system or during feat selection
            # This method serves as a hook for any additional mechanical processing needed
            
        except Exception as e:
            logger.warning(f"Error applying individual feat effect for {feat_name}: {e}")
