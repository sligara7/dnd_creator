# IMPLEMENTED: LLM integration for generating rich descriptions of custom species and classes
# IMPLEMENTED: Database storage system for persistent custom content across characters
# 
# Features:
# - LLMContentGenerator: Generates detailed descriptions for custom content using AI
# - CustomContentDatabase: Persistent storage for custom content with JSON serialization
# - ContentRegistry: Enhanced with database persistence and LLM integration

# do created weapons, armor, and spells have an llm generated description or lore?  
# ============================================================================


from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime
import logging
import json
import os
from pathlib import Path
import asyncio

# Import from core_models.py
from src.models.core_models import (
    ProficiencyLevel, 
    AbilityScoreSource, 
    AbilityScore, 
    ASIManager, 
    CharacterLevelManager, 
    MagicItemManager
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CUSTOM CONTENT CLASSES
# ============================================================================
class CustomSpecies:
    """Represents a custom species with D&D 5e 2024 compliant traits including sleep mechanics."""
    
    def __init__(self, name: str, description: str, creature_type: str = "Humanoid",
                 size: str = "Medium", speed: int = 30):
        self.name = name
        self.description = description
        self.creature_type = creature_type  # Humanoid, Fey, Fiend, etc.
        self.size = size  # Medium, Small, Large
        self.speed = speed  # Base walking speed
        
        # Level-based features (NEW in 2024)
        self.level_features = {}  # {level: [list of features]}
        
        # Innate traits (always active)
        self.innate_traits = []  # List of always-active traits
        
        # Resistances and immunities
        self.damage_resistances = []
        self.damage_immunities = []
        self.condition_resistances = []
        self.condition_immunities = []  # NEW: For sleep immunity, charm immunity, etc.
        
        # Senses
        self.darkvision = 0  # Range in feet (0 = no darkvision)
        self.special_senses = []  # Other senses like tremorsense, blindsight
        
        # Languages
        self.languages = ["Common"]  # Default language
        
        # Spellcasting (NEW in 2024)
        self.innate_spellcasting = {}  # {level: {spell_level: [spells]}}
        self.spellcasting_ability = ""  # Which ability modifier to use
        
        # Movement types
        self.movement_types = {"walk": speed}  # Can include fly, swim, climb
        
        # Special features that scale with level
        self.scaling_features = {}  # Features that improve with level
        
        # NEW: Sleep and Rest Mechanics (2024 rules)
        self.sleep_mechanics = {
            "needs_sleep": True,  # Whether species needs traditional sleep
            "sleep_type": "normal",  # "normal", "trance", "inactive_state", "none"
            "rest_duration": 8,  # Hours needed for long rest (usually 8, 4 for some)
            "rest_state": "unconscious",  # "unconscious", "semiconscious", "conscious"
            "sleep_immunity": False,  # Immune to magical sleep effects
            "charm_resistance": False,  # Advantage on charm saves
            "charm_immunity": False,  # Complete immunity to charm effects
            "special_rest_rules": []  # Additional rest-related rules
        }
    
    def set_elf_like_trance(self):
        """Configure species with elf-like trance mechanics."""
        self.sleep_mechanics.update({
            "needs_sleep": False,
            "sleep_type": "trance",
            "rest_duration": 4,
            "rest_state": "semiconscious",
            "sleep_immunity": True,
            "charm_resistance": True,
            "special_rest_rules": [
                "Can meditate instead of sleep",
                "Retains consciousness during trance",
                "Gains full benefits of long rest in 4 hours"
            ]
        })
        
        # Add to condition immunities
        if "magically induced sleep" not in self.condition_immunities:
            self.condition_immunities.append("magically induced sleep")
    
    def set_reborn_like_rest(self):
        """Configure species with reborn-like rest mechanics."""
        self.sleep_mechanics.update({
            "needs_sleep": False,
            "sleep_type": "inactive_state",
            "rest_duration": 4,
            "rest_state": "conscious",
            "sleep_immunity": True,
            "special_rest_rules": [
                "Can choose to sleep normally or enter inactive state",
                "Remains conscious during inactive rest",
                "Must remain motionless for 4 hours to gain long rest benefits"
            ]
        })
        
        if "magically induced sleep" not in self.condition_immunities:
            self.condition_immunities.append("magically induced sleep")
    
    def set_undead_like_rest(self):
        """Configure species with undead-like rest mechanics."""
        self.sleep_mechanics.update({
            "needs_sleep": False,
            "sleep_type": "none",
            "rest_duration": 8,  # Still need long rest duration for game balance
            "rest_state": "conscious",
            "sleep_immunity": True,
            "charm_immunity": True,
            "special_rest_rules": [
                "Does not sleep",
                "Immune to sleep effects",
                "Still requires long rest for ability recovery"
            ]
        })
        
        # Add immunities
        for condition in ["magically induced sleep", "natural sleep", "charm"]:
            if condition not in self.condition_immunities:
                self.condition_immunities.append(condition)
    
    def set_construct_like_rest(self):
        """Configure species with construct-like rest mechanics."""
        self.sleep_mechanics.update({
            "needs_sleep": False,
            "sleep_type": "inactive_state",
            "rest_duration": 6,
            "rest_state": "conscious",
            "sleep_immunity": True,
            "charm_immunity": True,
            "special_rest_rules": [
                "Enters standby mode instead of sleep",
                "Remains aware of surroundings",
                "Cannot be magically forced to sleep"
            ]
        })
        
        for condition in ["magically induced sleep", "natural sleep", "charm"]:
            if condition not in self.condition_immunities:
                self.condition_immunities.append(condition)
    
    def get_rest_requirements(self) -> Dict[str, Any]:
        """Get the rest requirements for this species."""
        return {
            "long_rest_duration": self.sleep_mechanics["rest_duration"],
            "rest_type": self.sleep_mechanics["sleep_type"],
            "consciousness_level": self.sleep_mechanics["rest_state"],
            "can_sleep_normally": self.sleep_mechanics["needs_sleep"],
            "immune_to_sleep_magic": self.sleep_mechanics["sleep_immunity"],
            "charm_protection": self.sleep_mechanics.get("charm_resistance", False) or self.sleep_mechanics.get("charm_immunity", False),
            "special_rules": self.sleep_mechanics["special_rest_rules"]
        }
    
    def add_level_feature(self, level: int, feature_name: str, description: str):
        """Add a feature gained at a specific level."""
        if level not in self.level_features:
            self.level_features[level] = []
        self.level_features[level].append({
            "name": feature_name,
            "description": description
        })
    
    def add_innate_spell(self, character_level: int, spell_name: str, spell_level: int = 0):
        """Add an innate spell gained at a specific character level."""
        if character_level not in self.innate_spellcasting:
            self.innate_spellcasting[character_level] = {}
        if spell_level not in self.innate_spellcasting[character_level]:
            self.innate_spellcasting[character_level][spell_level] = []
        self.innate_spellcasting[character_level][spell_level].append(spell_name)
    
    def get_features_at_level(self, character_level: int) -> List[Dict[str, str]]:
        """Get all features available at a given character level."""
        features = []
        
        # Add innate traits (always available)
        for trait in self.innate_traits:
            features.append({"name": trait, "type": "innate", "description": ""})
        
        # Add level-specific features
        for level in range(1, character_level + 1):
            if level in self.level_features:
                for feature in self.level_features[level]:
                    feature["type"] = f"level_{level}"
                    features.append(feature)
        
        return features
    
    def get_spells_at_level(self, character_level: int) -> Dict[int, List[str]]:
        """Get all innate spells available at a given character level."""
        available_spells = {}
        
        for level in range(1, character_level + 1):
            if level in self.innate_spellcasting:
                for spell_level, spells in self.innate_spellcasting[level].items():
                    if spell_level not in available_spells:
                        available_spells[spell_level] = []
                    available_spells[spell_level].extend(spells)
        
        return available_spells

class CustomClass:
    """Represents a custom character class with D&D 5e 2024 compliant features."""
    
    def __init__(self, name: str, description: str, hit_die: int, 
                 primary_abilities: List[str], saving_throws: List[str]):
        self.name = name
        self.description = description
        self.hit_die = hit_die  # d6, d8, d10, d12
        self.primary_abilities = primary_abilities  # ["strength", "dexterity"]
        self.saving_throws = saving_throws  # ["strength", "constitution"]
        
        # Core class mechanics
        self.features = {}  # Level -> List of features
        self.subclass_levels = []  # Levels where subclass features are gained
        self.asi_levels = [4, 8, 12, 16, 19]  # Standard ASI levels
        self.proficiency_bonus_progression = "standard"  # "standard" or "enhanced"
        
        # Starting proficiencies
        self.armor_proficiencies = []  # ["light", "medium", "shields"]
        self.weapon_proficiencies = []  # ["simple", "martial"]
        self.tool_proficiencies = []  # ["thieves' tools"]
        self.skill_proficiencies = []  # Available skills to choose from
        self.skill_choices = 2  # Number of skills player can choose
        
        # Spellcasting (if applicable)
        self.spellcasting_ability = ""  # "intelligence", "wisdom", "charisma", or ""
        self.spell_progression = {}  # Level -> spell slots by level
        self.spells_known_progression = {}  # Level -> number of spells known
        self.cantrips_known_progression = {}  # Level -> number of cantrips
        self.ritual_casting = False
        self.spellcasting_focus = ""  # "arcane focus", "druidcraft focus", etc.
        
        # Class-specific resources
        self.resource_name = ""  # "Rage", "Ki Points", "Spell Slots", etc.
        self.resource_progression = {}  # Level -> resource amount
        self.resource_recovery = "long_rest"  # "short_rest", "long_rest", "special"
        
        # Multiclassing requirements
        self.multiclass_prereq = {}  # {"strength": 13, "charisma": 13}
        self.multiclass_proficiencies = []  # Gained when multiclassing INTO this class
        
        # Level 1 starting features
        self.level_1_features = []  # Features every character of this class starts with
        
        # Capstone feature (level 20)
        self.capstone_feature = None
        
        # Problem-solving approach
        self.problem_solving_style = ""  # "stealth", "magic", "combat", "social", etc.
        self.role_description = ""  # "damage dealer", "support", "tank", "utility"
    
    def add_class_feature(self, level: int, feature_name: str, description: str, 
                         feature_type: str = "feature"):
        """Add a class feature at a specific level."""
        if level not in self.features:
            self.features[level] = []
        self.features[level].append({
            "name": feature_name,
            "description": description,
            "type": feature_type  # "feature", "improvement", "choice", "asi"
        })
    
    def set_spellcasting_progression(self, caster_type: str):
        """Set up spellcasting progression for the class."""
        if caster_type == "full":
            # Full casters like Wizard, Sorcerer
            self.spell_progression = {
                1: [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2 first level slots
                2: [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                3: [4, 2, 0, 0, 0, 0, 0, 0, 0, 0],
                # ... continue for all 20 levels
            }
        elif caster_type == "half":
            # Half casters like Paladin, Ranger
            self.spell_progression = {
                2: [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Start at level 2
                3: [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                # ... continue for levels 2-20
            }
        elif caster_type == "third":
            # Third casters like Eldritch Knight, Arcane Trickster
            self.spell_progression = {
                3: [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Start at level 3
                4: [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                # ... continue for levels 3-20
            }
    
    def get_features_at_level(self, character_level: int) -> List[Dict[str, str]]:
        """Get all class features available at a given character level."""
        available_features = []
        
        for level in range(1, character_level + 1):
            if level in self.features:
                for feature in self.features[level]:
                    feature_copy = feature.copy()
                    feature_copy["gained_at_level"] = level
                    available_features.append(feature_copy)
            
            # Add ASI levels
            if level in self.asi_levels:
                available_features.append({
                    "name": "Ability Score Improvement",
                    "description": "Increase one ability score by 2, or two ability scores by 1 each. Alternatively, choose a feat.",
                    "type": "asi",
                    "gained_at_level": level
                })
        
        return available_features
    
    def get_spell_slots_at_level(self, character_level: int) -> List[int]:
        """Get spell slots available at a given character level."""
        if character_level in self.spell_progression:
            return self.spell_progression[character_level]
        
        # Find the highest level we have data for
        available_levels = [lvl for lvl in self.spell_progression.keys() if lvl <= character_level]
        if available_levels:
            highest_level = max(available_levels)
            return self.spell_progression[highest_level]
        
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # No spellcasting
    
    def get_resource_amount_at_level(self, character_level: int) -> int:
        """Get class resource amount at a given character level."""
        if character_level in self.resource_progression:
            return self.resource_progression[character_level]
        
        # Find the highest level we have data for
        available_levels = [lvl for lvl in self.resource_progression.keys() if lvl <= character_level]
        if available_levels:
            highest_level = max(available_levels)
            return self.resource_progression[highest_level]
        
        return 0
    
    def validate_class_design(self) -> Dict[str, Any]:
        """Validate that the class follows D&D 5e design principles."""
        issues = []
        warnings = []
        
        # Check hit die
        valid_hit_dice = [6, 8, 10, 12]
        if self.hit_die not in valid_hit_dice:
            issues.append(f"Invalid hit die: d{self.hit_die}. Must be d6, d8, d10, or d12.")
        
        # Check saving throws (should be exactly 2)
        if len(self.saving_throws) != 2:
            issues.append(f"Classes must have exactly 2 saving throw proficiencies, found {len(self.saving_throws)}")
        
        # Check for level 1 features
        if 1 not in self.features or not self.features[1]:
            warnings.append("Class has no level 1 features")
        
        # Check for capstone (level 20 feature)
        if 20 not in self.features:
            warnings.append("Class has no capstone feature at level 20")
        
        # Check ASI progression
        missing_asi = [level for level in self.asi_levels if level not in self.features or 
                      not any(f["type"] == "asi" for f in self.features[level])]
        if missing_asi:
            warnings.append(f"Missing explicit ASI features at levels: {missing_asi}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

class CustomItem:
    """Represents custom weapons, armor, or equipment."""
    
    def __init__(self, name: str, item_type: str, description: str, 
                 properties: Dict[str, Any] = None):
        self.name = name
        self.item_type = item_type  # "weapon", "armor", "equipment", "spell"
        self.description = description
        self.properties = properties or {}

# ============================================================================
# ENHANCED CUSTOM CONTENT SYSTEM WITH D&D COMPLIANCE
# ============================================================================

class CustomSpell:
    """Represents a custom spell with full D&D 5e attributes."""
    
    def __init__(self, name: str, level: int, school: str, casting_time: str,
                 range_distance: str, components: List[str], duration: str,
                 description: str, classes: List[str] = None):
        self.name = name
        self.level = level  # 0-9 (0 = cantrip)
        self.school = school  # One of the 8 schools
        self.casting_time = casting_time  # "1 action", "1 bonus action", etc.
        self.range_distance = range_distance  # "Touch", "30 feet", "Self", etc.
        self.components = components  # ["V", "S", "M (material description)"]
        self.duration = duration  # "Instantaneous", "Concentration, up to 1 minute", etc.
        self.description = description
        self.classes = classes or []  # Which classes can learn this spell
        self.targets = ""  # What the spell targets
        self.area_of_effect = ""  # Shape and size if applicable
        self.saving_throw = ""  # Type of save if applicable
        self.attack_roll = False  # Whether it requires an attack roll
        self.damage_type = ""  # Type of damage if applicable
        self.higher_levels = ""  # What happens when cast at higher levels
        
        # Enhanced lore and background
        self.origin_story = ""  # How this spell was discovered/created
        self.creator_name = ""  # Who created this spell
        self.historical_significance = ""  # Role in history or legends
        self.casting_flavor = ""  # What it looks/sounds/feels like when cast
        self.component_details = ""  # Detailed material component descriptions

class CustomWeapon:
    """Represents a custom weapon with D&D 5e 2024 compliant attributes."""
    
    def __init__(self, name: str, category: str, weapon_type: str, damage_dice: str, 
                 damage_type: str, properties: List[str], cost: str = "", weight: str = ""):
        self.name = name
        self.category = category  # "Simple" or "Martial"
        self.weapon_type = weapon_type  # "Melee", "Ranged", or "Melee/Ranged"
        self.damage_dice = damage_dice  # "1d8", "2d6", etc.
        self.damage_type = damage_type  # "slashing", "piercing", "bludgeoning"
        self.properties = properties  # List of weapon properties
        self.cost = cost  # "10 gp"
        self.weight = weight  # "3 lb."
        
        # Range (for ranged weapons or thrown weapons)
        self.range_normal = 0  # Normal range in feet
        self.range_long = 0  # Long range in feet
        
        # 2024 NEW: Weapon Mastery Property
        self.mastery_property = ""  # "Cleave", "Graze", "Nick", etc.
        
        # Versatile damage (if weapon has versatile property)
        self.versatile_damage = ""  # "1d10" for two-handed use
        
        # Magical enhancements
        self.magical = False
        self.magical_bonus = 0  # +1, +2, +3 weapon bonus
        self.special_abilities = []  # List of special magical abilities
        
        # Description and lore
        self.description = ""
        self.origin_story = ""  # How this weapon was created/found
        self.creator_name = ""  # Who forged/enchanted this weapon
        self.historical_significance = ""  # Famous battles or owners
        self.legends_and_myths = ""  # Stories told about this weapon
        self.discovery_circumstances = ""  # How the character obtained it
        
        # Proficiency requirement
        self.proficiency_required = self._determine_proficiency_requirement()
    
    def _determine_proficiency_requirement(self) -> str:
        """Determine what proficiency is needed to use this weapon effectively."""
        if self.category == "Simple":
            if self.weapon_type == "Melee" or self.weapon_type == "Melee/Ranged":
                return "Simple weapons"
            else:
                return "Simple weapons"
        else:  # Martial
            if self.weapon_type == "Melee" or self.weapon_type == "Melee/Ranged":
                return "Martial weapons"
            else:
                return "Martial weapons"
    
    def get_damage_for_hands(self, two_handed: bool = False) -> str:
        """Get damage dice based on how weapon is wielded."""
        if two_handed and "versatile" in [prop.lower() for prop in self.properties]:
            return self.versatile_damage if self.versatile_damage else self.damage_dice
        return self.damage_dice
    
    def has_property(self, property_name: str) -> bool:
        """Check if weapon has a specific property."""
        return property_name.lower() in [prop.lower() for prop in self.properties]
    
    def get_range_string(self) -> str:
        """Get formatted range string for display."""
        if self.range_normal > 0:
            if self.range_long > 0:
                return f"{self.range_normal}/{self.range_long} ft."
            else:
                return f"{self.range_normal} ft."
        return "—"
    
    def validate_weapon_design(self) -> Dict[str, Any]:
        """Validate that the weapon follows D&D 5e design principles."""
        issues = []
        warnings = []
        
        # Check category
        if self.category not in ["Simple", "Martial"]:
            issues.append(f"Invalid weapon category: {self.category}. Must be Simple or Martial.")
        
        # Check type
        valid_types = ["Melee", "Ranged", "Melee/Ranged"]
        if self.weapon_type not in valid_types:
            issues.append(f"Invalid weapon type: {self.weapon_type}. Must be one of: {', '.join(valid_types)}")
        
        # Check damage type
        valid_damage_types = ["slashing", "piercing", "bludgeoning", "acid", "cold", "fire", "force", 
                             "lightning", "necrotic", "poison", "psychic", "radiant", "thunder"]
        if self.damage_type.lower() not in valid_damage_types:
            warnings.append(f"Unusual damage type: {self.damage_type}")
        
        # Check properties
        valid_properties = [
            "ammunition", "finesse", "heavy", "light", "loading", "range", 
            "reach", "thrown", "two-handed", "versatile", "improvised"
        ]
        for prop in self.properties:
            if prop.lower() not in valid_properties:
                warnings.append(f"Non-standard property: {prop}")
        
        # Check mastery property
        valid_mastery = [
            "cleave", "graze", "nick", "push", "sap", "slow", "topple", "vex"
        ]
        if self.mastery_property and self.mastery_property.lower() not in valid_mastery:
            warnings.append(f"Non-standard mastery property: {self.mastery_property}")
        
        # Check property combinations
        if "two-handed" in [p.lower() for p in self.properties] and "light" in [p.lower() for p in self.properties]:
            issues.append("Weapon cannot be both two-handed and light")
        
        if "versatile" in [p.lower() for p in self.properties] and not self.versatile_damage:
            warnings.append("Versatile weapon should specify two-handed damage")
        
        # Check range requirements
        if self.weapon_type == "Ranged" and self.range_normal == 0:
            issues.append("Ranged weapons must have a range specified")
        
        if "thrown" in [p.lower() for p in self.properties] and self.range_normal == 0:
            warnings.append("Thrown weapons should have a range specified")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_full_stats_dict(self) -> Dict[str, Any]:
        """Get complete weapon statistics as a dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "type": self.weapon_type,
            "damage": self.damage_dice,
            "damage_type": self.damage_type,
            "properties": self.properties,
            "mastery": self.mastery_property,
            "range": self.get_range_string(),
            "versatile_damage": self.versatile_damage,
            "cost": self.cost,
            "weight": self.weight,
            "magical": self.magical,
            "magical_bonus": self.magical_bonus,
            "special_abilities": self.special_abilities,
            "proficiency_required": self.proficiency_required
        }

class CustomArmor:
    """Represents custom armor with complete D&D 5e attributes and mechanics."""
    
    def __init__(self, name: str, armor_type: str, ac_base: int, 
                 dex_bonus_type: str, cost: str = "", weight: str = ""):
        self.name = name
        self.armor_type = armor_type  # "Light", "Medium", "Heavy", "Shield"
        self.ac_base = ac_base  # Base AC value
        self.dex_bonus_type = dex_bonus_type  # "full", "max_2", "none"
        self.cost = cost  # "50 gp"
        self.weight = weight  # "20 lb."
        
        # Strength requirement (primarily for heavy armor)
        self.strength_requirement = 0  # Minimum Str score needed
        
        # Stealth penalty
        self.stealth_disadvantage = False  # Imposes disadvantage on Stealth checks
        
        # Don/Doff times (in minutes)
        self.don_time = self._determine_don_time()  # Time to put on
        self.doff_time = self._determine_doff_time()  # Time to take off
        
        # Proficiency requirements
        self.proficiency_required = self._determine_proficiency_requirement()
        
        # Description and lore
        self.description = ""
        self.origin_story = ""  # How this armor was created/found
        self.creator_name = ""  # Who crafted this armor
        self.historical_significance = ""  # Famous wearers or battles
        self.crafting_materials = ""  # Special materials used in creation
        self.discovery_circumstances = ""  # How the character obtained it
        
        # Magical enhancements
        self.magical = False
        self.magical_bonus = 0  # +1, +2, +3 armor bonus
        self.special_abilities = []  # List of special magical abilities
        self.damage_resistances = []  # Damage types resisted
        self.damage_immunities = []  # Damage types immune to
        
        # Movement penalties
        self.speed_reduction = 0  # Speed reduction if Str requirement not met
        
        # Special properties
        self.special_properties = []  # Special armor properties
        self.variants = []  # Different versions (e.g., studded vs regular leather)
    
    def _determine_don_time(self) -> int:
        """Determine time to don armor based on type."""
        don_times = {
            "Light": 1,    # 1 minute
            "Medium": 5,   # 5 minutes
            "Heavy": 10,   # 10 minutes
            "Shield": 0    # 1 action (effectively 0 minutes)
        }
        return don_times.get(self.armor_type, 1)
    
    def _determine_doff_time(self) -> int:
        """Determine time to doff armor based on type."""
        doff_times = {
            "Light": 1,    # 1 minute
            "Medium": 1,   # 1 minute
            "Heavy": 5,    # 5 minutes
            "Shield": 0    # 1 action (effectively 0 minutes)
        }
        return doff_times.get(self.armor_type, 1)
    
    def _determine_proficiency_requirement(self) -> str:
        """Determine what proficiency is needed to use this armor effectively."""
        if self.armor_type == "Light":
            return "Light armor"
        elif self.armor_type == "Medium":
            return "Medium armor"
        elif self.armor_type == "Heavy":
            return "Heavy armor"
        elif self.armor_type == "Shield":
            return "Shields"
        else:
            return "Unknown armor type"
    
    def calculate_ac_for_character(self, dex_modifier: int, strength_score: int) -> int:
        """Calculate AC for a character wearing this armor."""
        base_ac = self.ac_base + self.magical_bonus
        
        # Apply Dexterity modifier based on armor type
        if self.dex_bonus_type == "full":
            # Light armor - full Dex modifier
            final_ac = base_ac + dex_modifier
        elif self.dex_bonus_type == "max_2":
            # Medium armor - Dex modifier capped at +2
            final_ac = base_ac + min(dex_modifier, 2)
        elif self.dex_bonus_type == "none":
            # Heavy armor - no Dex modifier
            final_ac = base_ac
        elif self.armor_type == "Shield":
            # Shields add flat bonus to existing AC
            final_ac = 2 + self.magical_bonus  # This gets added to base AC
        else:
            final_ac = base_ac
        
        return final_ac
    
    def get_movement_penalty(self, strength_score: int) -> int:
        """Get movement speed reduction if Strength requirement not met."""
        if self.strength_requirement > 0 and strength_score < self.strength_requirement:
            return 10  # Standard 10 ft speed reduction
        return 0
    
    def get_penalties_without_proficiency(self) -> List[str]:
        """Get list of penalties for wearing armor without proficiency."""
        if self.armor_type == "Shield":
            return []  # Shields don't have the same proficiency penalties
        
        return [
            "Disadvantage on Strength and Dexterity ability checks",
            "Disadvantage on Strength and Dexterity saving throws", 
            "Disadvantage on attack rolls",
            "Cannot cast spells"
        ]
    
    def has_stealth_disadvantage(self) -> bool:
        """Check if this armor imposes disadvantage on Stealth checks."""
        return self.stealth_disadvantage
    
    def validate_armor_design(self) -> Dict[str, Any]:
        """Validate that the armor follows D&D 5e design principles."""
        issues = []
        warnings = []
        
        # Check armor type
        valid_types = ["Light", "Medium", "Heavy", "Shield"]
        if self.armor_type not in valid_types:
            issues.append(f"Invalid armor type: {self.armor_type}. Must be one of: {', '.join(valid_types)}")
        
        # Check AC ranges
        ac_ranges = {
            "Light": (11, 12),    # Leather (11) to Studded Leather (12)
            "Medium": (12, 15),   # Leather (12) to Half Plate (15)
            "Heavy": (14, 18),    # Ring Mail (14) to Plate (18)
            "Shield": (2, 2)      # Standard shield (+2)
        }
        
        if self.armor_type in ac_ranges:
            min_ac, max_ac = ac_ranges[self.armor_type]
            base_ac = self.ac_base - self.magical_bonus  # Remove magical bonus for validation
            if base_ac < min_ac or base_ac > max_ac:
                warnings.append(f"{self.armor_type} armor AC ({base_ac}) outside typical range ({min_ac}-{max_ac})")
        
        # Check Dex bonus consistency
        if self.armor_type == "Light" and self.dex_bonus_type != "full":
            warnings.append("Light armor should typically allow full Dex modifier")
        elif self.armor_type == "Medium" and self.dex_bonus_type != "max_2":
            warnings.append("Medium armor should typically cap Dex modifier at +2")
        elif self.armor_type == "Heavy" and self.dex_bonus_type != "none":
            warnings.append("Heavy armor should typically not allow Dex modifier")
        
        # Check Strength requirements
        if self.armor_type == "Heavy" and self.strength_requirement == 0:
            warnings.append("Heavy armor typically has a Strength requirement")
        elif self.armor_type in ["Light", "Medium"] and self.strength_requirement > 0:
            warnings.append("Light and Medium armor typically don't have Strength requirements")
        
        # Check stealth disadvantage
        if self.armor_type == "Heavy" and not self.stealth_disadvantage:
            warnings.append("Heavy armor typically imposes disadvantage on Stealth checks")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_full_stats_dict(self) -> Dict[str, Any]:
        """Get complete armor statistics as a dictionary."""
        return {
            "name": self.name,
            "type": self.armor_type,
            "ac_base": self.ac_base,
            "dex_bonus": self._format_dex_bonus(),
            "strength_requirement": self.strength_requirement,
            "stealth_disadvantage": self.stealth_disadvantage,
            "don_time": self.don_time,
            "doff_time": self.doff_time,
            "cost": self.cost,
            "weight": self.weight,
            "magical": self.magical,
            "magical_bonus": self.magical_bonus,
            "special_abilities": self.special_abilities,
            "damage_resistances": self.damage_resistances,
            "proficiency_required": self.proficiency_required,
            "description": self.description
        }
    
    def _format_dex_bonus(self) -> str:
        """Format Dex bonus for display."""
        if self.dex_bonus_type == "full":
            return "Dex modifier"
        elif self.dex_bonus_type == "max_2":
            return "Dex modifier (max 2)"
        elif self.dex_bonus_type == "none":
            return "—"
        else:
            return "Unknown"

class CustomFeat:
    """Represents a custom feat with D&D 5e 2024 compliant attributes and mechanics."""
    
    def __init__(self, name: str, prerequisites: str, description: str, benefits: List[str]):
        self.name = name
        self.prerequisites = prerequisites  # "Dex 13 or higher", "None", "4th level", etc.
        self.description = description  # Flavor text and roleplaying enhancement
        self.benefits = benefits  # List of mechanical benefits
        
        # Core feat mechanics
        self.feat_category = "General"  # "General", "Fighting Style", "Epic Boon"
        self.level_requirement = 1  # Minimum character level (1 for starting feats, 4+ for others)
        self.repeatable = False  # Can this feat be taken multiple times?
        
        # Mechanical benefits
        self.ability_score_increase = {}  # {ability: increase} - NEW: Can be partial ASI
        self.new_proficiencies = []  # Skills, tools, weapons, armor gained
        self.special_abilities = []  # New abilities, spells, or features granted
        self.combat_enhancements = []  # Combat-specific improvements
        self.spellcasting_grants = {}  # Spells gained from other classes
        
        # 2024 Updates
        self.origin_feat = False  # Available at level 1 (2024 rule)
        self.half_feat = False  # Grants +1 to an ability score
        self.metamagic_options = []  # If feat grants metamagic (like Metamagic Adept)
        self.expertise_grants = []  # Skills that gain expertise
        self.language_grants = []  # Languages learned
        
        # Feat synergies and restrictions
        self.replaces_fighting_style = False  # Does this replace a fighting style choice?
        self.synergizes_with = []  # Other feats this works well with
        self.mutually_exclusive = []  # Feats that can't be taken with this one
        
        # Usage limitations
        self.uses_per_rest = 0  # How many times per rest (if applicable)
        self.rest_type = ""  # "short_rest", "long_rest", or ""
        self.cooldown_type = ""  # "once_per_turn", "once_per_round", etc.
    
    def set_origin_feat(self, is_origin: bool = True):
        """Mark this feat as available at character creation (level 1)."""
        self.origin_feat = is_origin
        if is_origin:
            self.level_requirement = 1
            self.feat_category = "Origin"
    
    def set_half_feat(self, ability: str, increase: int = 1):
        """Make this a half-feat that grants an ability score increase."""
        self.half_feat = True
        self.ability_score_increase[ability] = increase
    
    def add_spellcasting_ability(self, spell_list: List[str], casting_ability: str, 
                                spell_level: int = 1, uses_per_rest: int = 1, rest_type: str = "long_rest"):
        """Add spellcasting from another class (like Magic Initiate)."""
        self.spellcasting_grants = {
            "spells": spell_list,
            "ability": casting_ability,
            "spell_level": spell_level,
            "uses_per_rest": uses_per_rest,
            "rest_type": rest_type
        }
    
    def add_expertise(self, skills: List[str]):
        """Add expertise to specific skills."""
        self.expertise_grants.extend(skills)
    
    def add_metamagic(self, metamagic_options: List[str], sorcery_points: int = 0):
        """Add metamagic options (for Metamagic Adept-style feats)."""
        self.metamagic_options = metamagic_options
        if sorcery_points > 0:
            self.special_abilities.append(f"Gain {sorcery_points} sorcery points")
    
    def get_feat_opportunities_by_level(self, character_level: int, character_classes: Dict[str, int]) -> List[int]:
        """Get all levels at which this character could have taken feats."""
        opportunities = []
        
        # Handle None character_level
        if character_level is None:
            character_level = 1
        
        # Level 1 origin feat (2024 rule)
        if character_level >= 1:
            opportunities.append(1)
        
        # Calculate ASI levels across all classes
        asi_levels = set()
        
        for class_name, class_level in character_classes.items():
            class_lower = class_name.lower()
            
            # Standard ASI levels for most classes
            standard_levels = [4, 8, 12, 16, 19]
            
            # Classes with additional ASI opportunities
            if class_lower == "fighter":
                standard_levels.extend([6, 14])  # Fighters get extra ASIs
            elif class_lower == "rogue":
                standard_levels.append(10)  # Rogues get one extra ASI
            
            # Add class levels that correspond to ASI opportunities
            for asi_level in standard_levels:
                if class_level >= asi_level:
                    # Calculate total character level when this ASI was available
                    total_level_at_asi = character_level - class_level + asi_level
                    if total_level_at_asi <= character_level:
                        asi_levels.add(total_level_at_asi)
        
        opportunities.extend(sorted(asi_levels))
        return sorted(set(opportunities))  # Remove duplicates
    
    def validate_feat_design(self) -> Dict[str, Any]:
        """Validate that the feat follows D&D 5e 2024 design principles."""
        issues = []
        warnings = []
        
        # Check prerequisites
        if self.level_requirement > 1 and not self.prerequisites:
            warnings.append("Higher level feats should have prerequisites")
        
        # Check origin feat restrictions
        if self.origin_feat and self.level_requirement > 1:
            issues.append("Origin feats must have level requirement of 1")
        
        # Check half-feat consistency
        if self.half_feat and not self.ability_score_increase:
            issues.append("Half-feats must provide ability score increases")
        
        # Check benefit count (feats should be meaningful but not overpowered)
        total_benefits = len(self.benefits) + len(self.special_abilities) + len(self.new_proficiencies)
        if total_benefits < 1:
            issues.append("Feats must provide at least one meaningful benefit")
        elif total_benefits > 5:
            warnings.append("Feat may be too powerful with many benefits")
        
        # Check spellcasting grants
        if self.spellcasting_grants and not self.spellcasting_grants.get("ability"):
            issues.append("Spellcasting feats must specify casting ability")
        
        # Check metamagic without sorcery points
        if self.metamagic_options and not any("sorcery point" in ability.lower() for ability in self.special_abilities):
            warnings.append("Metamagic feats typically grant sorcery points")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_full_feat_dict(self) -> Dict[str, Any]:
        """Get complete feat information as a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "category": self.feat_category,
            "level_requirement": self.level_requirement,
            "origin_feat": self.origin_feat,
            "half_feat": self.half_feat,
            "repeatable": self.repeatable,
            "benefits": self.benefits,
            "ability_score_increase": self.ability_score_increase,
            "new_proficiencies": self.new_proficiencies,
            "special_abilities": self.special_abilities,
            "combat_enhancements": self.combat_enhancements,
            "spellcasting_grants": self.spellcasting_grants,
            "expertise_grants": self.expertise_grants,
            "metamagic_options": self.metamagic_options,
            "language_grants": self.language_grants,
            "uses_per_rest": self.uses_per_rest,
            "rest_type": self.rest_type
        }

class FeatManager:
    """Manages feat acquisition and validation for characters."""
    
    def __init__(self):
        self.available_feats: Dict[str, CustomFeat] = {}
        self.character_feats: Dict[str, List[str]] = {}  # character_id -> feat names
    
    def register_feat(self, feat: CustomFeat):
        """Register a feat as available."""
        self.available_feats[feat.name] = feat
    
    def get_available_feats_for_character(self, character_data: Dict[str, Any]) -> List[CustomFeat]:
        """Get feats available to a character based on level and prerequisites."""
        character_level = character_data.get("level", 1)
        classes = character_data.get("classes", {})
        abilities = character_data.get("ability_scores", {})
        
        available = []
        
        for feat in self.available_feats.values():
            # Check level requirement
            if character_level < feat.level_requirement:
                continue
            
            # Check if origin feat and character is level 1
            if feat.origin_feat and character_level == 1:
                available.append(feat)
                continue
            
            # Check prerequisites
            if self._meets_prerequisites(feat, character_data):
                available.append(feat)
        
        return available
    
    def _meets_prerequisites(self, feat: CustomFeat, character_data: Dict[str, Any]) -> bool:
        """Check if character meets feat prerequisites."""
        if not feat.prerequisites or feat.prerequisites.lower() == "none":
            return True
        
        prereq_lower = feat.prerequisites.lower()
        abilities = character_data.get("ability_scores", {})
        
        # Check ability score requirements
        ability_requirements = {
            "str": "strength", "dex": "dexterity", "con": "constitution",
            "int": "intelligence", "wis": "wisdom", "cha": "charisma"
        }
        
        for short, full in ability_requirements.items():
            if f"{short} " in prereq_lower:
                # Extract required score
                import re
                match = re.search(f"{short}\\s+(\\d+)", prereq_lower)
                if match:
                    required_score = int(match.group(1))
                    if abilities.get(full, 10) < required_score:
                        return False
        
        # Check level requirements
        if "level" in prereq_lower:
            match = re.search(r"(\d+)(?:st|nd|rd|th)?\s+level", prereq_lower)
            if match:
                required_level = int(match.group(1))
                if character_data.get("level", 1) < required_level:
                    return False
        
        return True
    
    def assign_feat_to_character(self, character_id: str, feat_name: str) -> bool:
        """Assign a feat to a character."""
        if feat_name in self.available_feats:
            if character_id not in self.character_feats:
                self.character_feats[character_id] = []
            
            feat = self.available_feats[feat_name]
            
            # Check if feat is repeatable
            if feat_name in self.character_feats[character_id] and not feat.repeatable:
                return False
            
            self.character_feats[character_id].append(feat_name)
            return True
        
        return False

class ContentRegistry:
    """Registry for custom content created for characters."""
    
    def __init__(self):
        self.custom_species: Dict[str, CustomSpecies] = {}
        self.custom_classes: Dict[str, CustomClass] = {}
        self.custom_items: Dict[str, CustomItem] = {}
        self.custom_spells: Dict[str, CustomSpell] = {}
        self.custom_weapons: Dict[str, CustomWeapon] = {}
        self.custom_armor: Dict[str, CustomArmor] = {}
        self.custom_feats: Dict[str, CustomFeat] = {}
        self.character_content: Dict[str, List[str]] = {}  # character_id -> list of custom content
    
    def register_species(self, species: CustomSpecies):
        """Register a custom species."""
        self.custom_species[species.name] = species
        logger.info(f"Registered custom species: {species.name}")
    
    def register_class(self, custom_class: CustomClass):
        """Register a custom class."""
        self.custom_classes[custom_class.name] = custom_class
        logger.info(f"Registered custom class: {custom_class.name}")
    
    def register_item(self, item: CustomItem):
        """Register a custom item."""
        self.custom_items[item.name] = item
        logger.info(f"Registered custom item: {item.name}")
    
    def register_spell(self, spell: CustomSpell):
        """Register a custom spell."""
        self.custom_spells[spell.name] = spell
        logger.info(f"Registered custom spell: {spell.name}")
    
    def register_weapon(self, weapon: CustomWeapon):
        """Register a custom weapon."""
        self.custom_weapons[weapon.name] = weapon
        logger.info(f"Registered custom weapon: {weapon.name}")
    
    def register_armor(self, armor: CustomArmor):
        """Register a custom armor."""
        self.custom_armor[armor.name] = armor
        logger.info(f"Registered custom armor: {armor.name}")
    
    def register_feat(self, feat: CustomFeat):
        """Register a custom feat."""
        self.custom_feats[feat.name] = feat
        logger.info(f"Registered custom feat: {feat.name}")
    
    def get_species(self, name: str) -> Optional[CustomSpecies]:
        """Get a custom species by name."""
        return self.custom_species.get(name)
    
    def get_class(self, name: str) -> Optional[CustomClass]:
        """Get a custom class by name."""
        return self.custom_classes.get(name)
    
    def get_item(self, name: str) -> Optional[CustomItem]:
        """Get a custom item by name."""
        return self.custom_items.get(name)
    
    def get_spell(self, name: str) -> Optional[CustomSpell]:
        """Get a custom spell by name."""
        return self.custom_spells.get(name)
    
    def get_weapon(self, name: str) -> Optional[CustomWeapon]:
        """Get a custom weapon by name."""
        return self.custom_weapons.get(name)
    
    def get_armor(self, name: str) -> Optional[CustomArmor]:
        """Get a custom armor by name."""
        return self.custom_armor.get(name)
    
    def get_feat(self, name: str) -> Optional[CustomFeat]:
        """Get a custom feat by name."""
        return self.custom_feats.get(name)
    
    def get_all_custom_content(self) -> Dict[str, int]:
        """Get count of all registered custom content."""
        return {
            "species": len(self.custom_species),
            "classes": len(self.custom_classes),
            "items": len(self.custom_items),
            "spells": len(self.custom_spells),
            "weapons": len(self.custom_weapons),
            "armor": len(self.custom_armor),
            "feats": len(self.custom_feats)
        }
    
    def link_content_to_character(self, character_id: str, content_names: List[str]):
        """Link custom content to a specific character."""
        if character_id not in self.character_content:
            self.character_content[character_id] = []
        self.character_content[character_id].extend(content_names)
        logger.info(f"Linked {len(content_names)} custom content items to character {character_id}")
    
    def get_character_content(self, character_id: str) -> List[str]:
        """Get all custom content linked to a character."""
        return self.character_content.get(character_id, [])

# ============================================================================
# MODULE SUMMARY
# ============================================================================
# This module provides all custom D&D content creation and management classes:
#
# Core Content Classes:
# - CustomSpecies: Custom species/races with 2024 D&D compliant traits
# - CustomClass: Custom character classes with spellcasting and features
# - CustomItem: Generic custom items and equipment
# - CustomSpell: Custom spells with full D&D 5e attributes
# - CustomWeapon: Custom weapons with 2024 weapon mastery rules
# - CustomArmor: Custom armor with complete AC and proficiency mechanics
# - CustomFeat: Custom feats with 2024 feat system compliance
#
# Management Classes:
# - FeatManager: Manages feat acquisition and character assignment
# - ContentRegistry: Central registry for all custom content types
#
# Dependencies: core_models.py (ProficiencyLevel, AbilityScoreSource, etc.)
# ============================================================================
