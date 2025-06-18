# Couldn't find '/home/ajs7/.ollama/id_ed25519'. Generating new private key.
# Your new public key is: 
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPWX2w5ykeyQYzJtlznpHlTz+X8pilc5UD+14K9FXBun

"""
D&D Character Backend Service - Enhanced with Iterative Creation and Compelling Backstories
Combines all essential classes and methods for character creation and management.
"""

import json
import os
import random
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CORE ENUMS AND DATA STRUCTURES
# ============================================================================

class ProficiencyLevel(Enum):
    """Proficiency levels for D&D 5e skills and abilities."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2


class AbilityScoreSource(Enum):
    """Sources of ability score bonuses."""
    BASE = "base"
    ASI = "ability_score_improvement"
    FEAT = "feat"
    MAGIC_ITEM = "magic_item"
    CLASS_FEATURE = "class_feature"
    SPECIES_TRAIT = "species_trait"
    TEMPORARY = "temporary"

class AbilityScore:
    """Enhanced ability score with multiple sources and proper level tracking."""
    
    def __init__(self, base_score: int = 10):
        self.base_score = base_score
        self.improvements: Dict[AbilityScoreSource, List[Dict[str, Any]]] = {
            source: [] for source in AbilityScoreSource
        }
        self._cached_total = None
        self._cached_modifier = None
    
    def add_improvement(self, source: AbilityScoreSource, amount: int, 
                       description: str = "", level_gained: int = 0, 
                       feat_name: str = "", temporary: bool = False):
        """Add an ability score improvement from a specific source."""
        improvement = {
            "amount": amount,
            "description": description,
            "level_gained": level_gained,
            "feat_name": feat_name,
            "temporary": temporary
        }
        
        self.improvements[source].append(improvement)
        self._invalidate_cache()
    
    def remove_improvement(self, source: AbilityScoreSource, description: str = ""):
        """Remove a specific improvement (useful for temporary effects)."""
        if description:
            self.improvements[source] = [
                imp for imp in self.improvements[source] 
                if imp["description"] != description
            ]
        else:
            self.improvements[source].clear()
        self._invalidate_cache()
    
    @property
    def total_score(self) -> int:
        """Calculate total ability score including all improvements."""
        if self._cached_total is None:
            total = self.base_score
            
            for source, improvements in self.improvements.items():
                for improvement in improvements:
                    total += improvement["amount"]
            
            # Enforce maximum of 30 (epic-level campaigns) or typical max of 20
            # Some magic items and class features can exceed 20
            max_score = 30
            self._cached_total = min(max_score, max(1, total))
        
        return self._cached_total
    
    @property
    def modifier(self) -> int:
        """Calculate ability modifier."""
        if self._cached_modifier is None:
            self._cached_modifier = (self.total_score - 10) // 2
        return self._cached_modifier
    
    @property
    def asi_improvements(self) -> int:
        """Get total ASI points spent on this ability."""
        return sum(imp["amount"] for imp in self.improvements[AbilityScoreSource.ASI])
    
    @property
    def feat_improvements(self) -> int:
        """Get total feat improvements to this ability."""
        return sum(imp["amount"] for imp in self.improvements[AbilityScoreSource.FEAT])
    
    def get_improvement_history(self) -> List[Dict[str, Any]]:
        """Get chronological history of all improvements."""
        history = []
        
        for source, improvements in self.improvements.items():
            for improvement in improvements:
                history.append({
                    "source": source.value,
                    "amount": improvement["amount"],
                    "description": improvement["description"],
                    "level_gained": improvement["level_gained"],
                    "feat_name": improvement["feat_name"]
                })
        
        # Sort by level gained
        return sorted(history, key=lambda x: x["level_gained"])
    
    def _invalidate_cache(self):
        """Invalidate cached values when improvements change."""
        self._cached_total = None
        self._cached_modifier = None


class ASIManager:
    """Manages Ability Score Improvements across all classes and levels."""
    
    def __init__(self):
        self.class_asi_levels = {
            # Standard progression for most classes
            "standard": [4, 8, 12, 16, 19],
            # Fighter gets additional ASIs
            "fighter": [4, 6, 8, 12, 14, 16, 19],
            # Rogue gets one additional ASI
            "rogue": [4, 8, 10, 12, 16, 19]
        }
        
        self.total_asi_points_used = 0
        self.asi_history: List[Dict[str, Any]] = []
    
    def get_asi_levels_for_class(self, class_name: str) -> List[int]:
        """Get ASI levels for a specific class."""
        class_lower = class_name.lower()
        
        if class_lower == "fighter":
            return self.class_asi_levels["fighter"]
        elif class_lower == "rogue":
            return self.class_asi_levels["rogue"]
        else:
            return self.class_asi_levels["standard"]
    
    def calculate_available_asis(self, character_classes: Dict[str, int]) -> Dict[str, Any]:
        """Calculate total available ASIs based on character's class levels."""
        
        available_asis = []
        total_character_level = sum(character_classes.values())
        
        for class_name, class_level in character_classes.items():
            asi_levels = self.get_asi_levels_for_class(class_name)
            
            for asi_level in asi_levels:
                if class_level >= asi_level:
                    # Calculate what character level this ASI became available
                    # This is approximate for multiclass characters
                    character_level_when_gained = self._estimate_character_level_for_asi(
                        class_name, asi_level, character_classes, total_character_level
                    )
                    
                    available_asis.append({
                        "class": class_name,
                        "class_level": asi_level,
                        "character_level": character_level_when_gained,
                        "used": False  # Will be updated based on ASI history
                    })
        
        # Sort by character level when gained
        available_asis.sort(key=lambda x: x["character_level"])
        
        # Mark ASIs as used based on history
        for i, asi in enumerate(available_asis):
            if i < len(self.asi_history):
                asi["used"] = True
                asi["improvement"] = self.asi_history[i]
        
        return {
            "total_available": len(available_asis),
            "total_used": len(self.asi_history),
            "remaining": len(available_asis) - len(self.asi_history),
            "asis": available_asis
        }
    
    def _estimate_character_level_for_asi(self, asi_class: str, asi_level: int, 
                                        character_classes: Dict[str, int], 
                                        total_level: int) -> int:
        """Estimate when an ASI became available for multiclass characters."""
        
        # For single-class characters, it's straightforward
        if len(character_classes) == 1:
            return asi_level
        
        # For multiclass, estimate based on class distribution
        # This is a simplified approach - exact calculation would require level-up history
        class_proportion = character_classes[asi_class] / total_level
        estimated_level = int(asi_level / class_proportion)
        
        return min(estimated_level, total_level)
    
    def apply_asi(self, ability_scores: Dict[str, AbilityScore], 
                  improvements: Dict[str, int], character_level: int, 
                  description: str = "ASI"):
        """Apply an ASI to ability scores."""
        
        # Validate ASI points (must total 2)
        total_points = sum(improvements.values())
        if total_points != 2:
            raise ValueError(f"ASI must use exactly 2 points, got {total_points}")
        
        # Validate ability score maximums (20 for normal ASIs)
        for ability, increase in improvements.items():
            if ability not in ability_scores:
                raise ValueError(f"Unknown ability score: {ability}")
            
            current_score = ability_scores[ability].total_score
            if current_score + increase > 20:
                raise ValueError(f"Cannot increase {ability} above 20 with ASI (current: {current_score})")
        
        # Apply improvements
        for ability, increase in improvements.items():
            ability_scores[ability].add_improvement(
                AbilityScoreSource.ASI,
                increase,
                description,
                character_level
            )
        
        # Record in history
        self.asi_history.append({
            "level": character_level,
            "improvements": improvements.copy(),
            "description": description
        })
        
        self.total_asi_points_used += total_points

class CharacterLevelManager:
    """Manages character leveling including multiclassing and ability score tracking."""
    
    def __init__(self, character_core: 'CharacterCore'):
        self.character_core = character_core
        self.asi_manager = ASIManager()
        self.level_history: List[Dict[str, Any]] = []
    
    def add_level(self, class_name: str, new_level: int, 
                  asi_choice: Optional[Dict[str, Any]] = None):
        """Add a level in a specific class."""
        
        # Update class level
        if class_name not in self.character_core.character_classes:
            self.character_core.character_classes[class_name] = 0
        
        old_level = self.character_core.character_classes[class_name]
        self.character_core.character_classes[class_name] = new_level
        
        # Calculate new total level
        total_level = sum(self.character_core.character_classes.values())
        
        # Record level-up
        level_up_record = {
            "class": class_name,
            "old_class_level": old_level,
            "new_class_level": new_level,
            "total_character_level": total_level,
            "gained_features": self._get_features_gained(class_name, new_level)
        }
        
        # Check if this level grants an ASI
        asi_levels = self.asi_manager.get_asi_levels_for_class(class_name)
        if new_level in asi_levels:
            level_up_record["grants_asi"] = True
            
            if asi_choice:
                if asi_choice["type"] == "asi":
                    # Apply ability score improvement
                    self.asi_manager.apply_asi(
                        self._get_ability_scores_dict(),
                        asi_choice["improvements"],
                        total_level,
                        f"ASI at {class_name} level {new_level}"
                    )
                    level_up_record["asi_used"] = asi_choice
                
                elif asi_choice["type"] == "feat":
                    # Apply feat (which may include ability score bonuses)
                    feat_name = asi_choice["feat_name"]
                    ability_bonuses = asi_choice.get("ability_bonuses", {})
                    
                    if ability_bonuses:
                        ability_scores = self._get_ability_scores_dict()
                        for ability, bonus in ability_bonuses.items():
                            ability_scores[ability].add_improvement(
                                AbilityScoreSource.FEAT,
                                bonus,
                                f"Feat: {feat_name}",
                                total_level,
                                feat_name
                            )
                    
                    level_up_record["feat_chosen"] = feat_name
            else:
                level_up_record["asi_pending"] = True
        
        self.level_history.append(level_up_record)
    
    def _get_ability_scores_dict(self) -> Dict[str, AbilityScore]:
        """Get ability scores as a dictionary."""
        return {
            "strength": self.character_core.strength,
            "dexterity": self.character_core.dexterity,
            "constitution": self.character_core.constitution,
            "intelligence": self.character_core.intelligence,
            "wisdom": self.character_core.wisdom,
            "charisma": self.character_core.charisma
        }
    
    def _get_features_gained(self, class_name: str, level: int) -> List[str]:
        """Get features gained at this class level."""
        # This would integrate with your class feature system
        # For now, return a placeholder
        return [f"{class_name} level {level} features"]
    
    def get_pending_asis(self) -> List[Dict[str, Any]]:
        """Get list of pending ASI choices."""
        pending = []
        
        for record in self.level_history:
            if record.get("asi_pending", False):
                pending.append({
                    "class": record["class"],
                    "level": record["new_class_level"],
                    "total_level": record["total_character_level"]
                })
        
        return pending
    
    def get_level_progression_summary(self) -> Dict[str, Any]:
        """Get summary of character's level progression."""
        
        total_level = sum(self.character_core.character_classes.values())
        asi_info = self.asi_manager.calculate_available_asis(self.character_core.character_classes)
        
        return {
            "total_level": total_level,
            "class_levels": self.character_core.character_classes.copy(),
            "multiclass": len(self.character_core.character_classes) > 1,
            "asi_info": asi_info,
            "pending_asis": self.get_pending_asis(),
            "level_history": self.level_history.copy()
        }

class MagicItemManager:
    """Manages magic items that affect ability scores."""
    
    def __init__(self, character_core: 'CharacterCore'):
        self.character_core = character_core
        self.active_items: Dict[str, Dict[str, Any]] = {}
    
    def add_magic_item(self, item_name: str, ability_bonuses: Dict[str, int], 
                      sets_score: Dict[str, int] = None, temporary: bool = False):
        """Add a magic item that affects ability scores."""
        
        ability_scores = self._get_ability_scores_dict()
        
        # Handle items that set scores to specific values (like Belt of Giant Strength)
        if sets_score:
            for ability, score in sets_score.items():
                if ability in ability_scores:
                    # Remove any existing magic item bonuses for this ability
                    ability_scores[ability].remove_improvement(
                        AbilityScoreSource.MAGIC_ITEM, item_name
                    )
                    
                    # Calculate the effective bonus to reach the target score
                    current_without_magic = (ability_scores[ability].base_score + 
                                           ability_scores[ability].asi_improvements +
                                           ability_scores[ability].feat_improvements)
                    
                    if score > current_without_magic:
                        bonus = score - current_without_magic
                        ability_scores[ability].add_improvement(
                            AbilityScoreSource.MAGIC_ITEM,
                            bonus,
                            f"{item_name} (sets to {score})",
                            temporary=temporary
                        )
        
        # Handle items that provide flat bonuses
        if ability_bonuses:
            for ability, bonus in ability_bonuses.items():
                if ability in ability_scores:
                    ability_scores[ability].add_improvement(
                        AbilityScoreSource.MAGIC_ITEM,
                        bonus,
                        f"{item_name} (+{bonus})",
                        temporary=temporary
                    )
        
        # Record the item
        self.active_items[item_name] = {
            "ability_bonuses": ability_bonuses or {},
            "sets_score": sets_score or {},
            "temporary": temporary
        }
    
    def remove_magic_item(self, item_name: str):
        """Remove a magic item and its effects."""
        if item_name not in self.active_items:
            return
        
        ability_scores = self._get_ability_scores_dict()
        
        # Remove all improvements from this item
        for ability_score in ability_scores.values():
            ability_score.remove_improvement(AbilityScoreSource.MAGIC_ITEM, item_name)
        
        del self.active_items[item_name]
    
    def _get_ability_scores_dict(self) -> Dict[str, AbilityScore]:
        """Get ability scores as a dictionary."""
        return {
            "strength": self.character_core.strength,
            "dexterity": self.character_core.dexterity,
            "constitution": self.character_core.constitution,
            "intelligence": self.character_core.intelligence,
            "wisdom": self.character_core.wisdom,
            "charisma": self.character_core.charisma
        }
# ============================================================================
# CUSTOM CONTENT SYSTEM
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
                 description: str, classes: List[str]):
        self.name = name
        self.level = level  # 0-9 (0 = cantrip)
        self.school = school  # One of the 8 schools
        self.casting_time = casting_time  # "1 action", "1 bonus action", etc.
        self.range_distance = range_distance  # "Touch", "30 feet", "Self", etc.
        self.components = components  # ["V", "S", "M (material description)"]
        self.duration = duration  # "Instantaneous", "Concentration, up to 1 minute", etc.
        self.description = description
        self.classes = classes  # Which classes can learn this spell
        self.targets = ""  # What the spell targets
        self.area_of_effect = ""  # Shape and size if applicable
        self.saving_throw = ""  # Type of save if applicable
        self.attack_roll = False  # Whether it requires an attack roll
        self.damage_type = ""  # Type of damage if applicable
        self.higher_levels = ""  # What happens when cast at higher levels

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
        self.character_content: Dict[str, List[str]] = {}  # character_id -> list of custom content
    
    def register_species(self, species: CustomSpecies):
        self.custom_species[species.name] = species
    
    def register_class(self, custom_class: CustomClass):
        self.custom_classes[custom_class.name] = custom_class
    
    def register_item(self, item: CustomItem):
        self.custom_items[item.name] = item
    
    def get_species(self, name: str) -> Optional[CustomSpecies]:
        return self.custom_species.get(name)
    
    def get_class(self, name: str) -> Optional[CustomClass]:
        return self.custom_classes.get(name)
    
    def get_item(self, name: str) -> Optional[CustomItem]:
        return self.custom_items.get(name)
    
    def link_content_to_character(self, character_id: str, content_names: List[str]):
        if character_id not in self.character_content:
            self.character_content[character_id] = []
        self.character_content[character_id].extend(content_names)

# ============================================================================
# CHARACTER ITERATION CACHE
# ============================================================================

class CharacterIterationCache:
    """Manages character iterations and changes during the creation process."""
    
    def __init__(self):
        self.iterations: List[Dict[str, Any]] = []
        self.current_character: Dict[str, Any] = {}
        self.modification_history: List[str] = []
        self.user_feedback: List[str] = []
        
    def add_iteration(self, character_data: Dict[str, Any], modification: str = ""):
        """Add a new iteration of the character."""
        self.current_character = character_data.copy()
        self.iterations.append(character_data.copy())
        if modification:
            self.modification_history.append(modification)
    
    def get_current_character(self) -> Dict[str, Any]:
        """Get the current character data."""
        return self.current_character.copy()
    
    def get_iteration_count(self) -> int:
        """Get the number of iterations."""
        return len(self.iterations)
    
    def add_user_feedback(self, feedback: str):
        """Add user feedback for the current iteration."""
        self.user_feedback.append(feedback)
    
    def get_modification_history(self) -> List[str]:
        """Get the history of modifications."""
        return self.modification_history.copy()

# ============================================================================
# BACKSTORY GENERATOR
# ============================================================================

class BackstoryGenerator:
    """Enhanced backstory generator with aggressive timeout management."""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.max_attempts = 2  # Reduced attempts
        self.base_timeout = 15  # Shorter base timeout
    
    def generate_compelling_backstory(self, character_data: Dict[str, Any], 
                                    user_description: str) -> Dict[str, str]:
        """Generate backstory with aggressive timeout and comprehensive fallbacks."""
        
        logger.info("Starting backstory generation...")
        
        # Try simplified backstory generation first
        try:
            return self._generate_simple_backstory(character_data, user_description)
        except Exception as e:
            logger.warning(f"Simple backstory generation failed: {e}")
            return self._get_fallback_backstory(character_data, user_description)
    
    def _generate_simple_backstory(self, character_data: Dict[str, Any], 
                                 user_description: str) -> Dict[str, str]:
        """Generate a simplified backstory with very short timeout."""
        
        name = character_data.get('name', 'Unknown')
        species = character_data.get('species', 'Human')
        classes = list(character_data.get('classes', {}).keys())
        primary_class = classes[0] if classes else 'Adventurer'
        
        # Ultra-compact prompt for speed
        prompt = f"""Character: {name}, {species} {primary_class}
Description: {user_description}

Return ONLY this JSON (no other text):
{{"main_backstory":"2 sentences about their past","origin":"Where from","motivation":"What drives them","secret":"Hidden aspect","relationships":"Key connections"}}"""
        
        try:
            # Very short timeout for backstory
            response = self.llm_service.generate(prompt, timeout_seconds=self.base_timeout)
            
            # Clean and parse response
            cleaned_response = self._clean_json_response(response)
            backstory_data = json.loads(cleaned_response)
            
            # Validate required fields
            required_fields = ["main_backstory", "origin", "motivation", "secret", "relationships"]
            if all(field in backstory_data for field in required_fields):
                logger.info("Backstory generation successful")
                return backstory_data
            else:
                logger.warning("Generated backstory missing required fields")
                return self._get_fallback_backstory(character_data, user_description)
                
        except (TimeoutError, json.JSONDecodeError) as e:
            logger.warning(f"Backstory generation failed: {e}")
            return self._get_fallback_backstory(character_data, user_description)
    
    def _clean_json_response(self, response: str) -> str:
        """Aggressively clean JSON response."""
        if not response:
            raise ValueError("Empty response")
        
        # Remove markdown and extra text
        response = response.strip()
        response = response.replace('```json', '').replace('```', '')
        
        # Find JSON boundaries
        start = response.find('{')
        end = response.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[start:end+1]
        
        # Fix common JSON issues
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        json_str = ' '.join(json_str.split())  # Normalize whitespace
        
        return json_str
    
    def _get_fallback_backstory(self, character_data: Dict[str, Any], 
                              user_description: str) -> Dict[str, str]:
        """Generate fallback backstory using templates."""
        
        name = character_data.get('name', 'Unknown')
        species = character_data.get('species', 'Human')
        classes = list(character_data.get('classes', {}).keys())
        primary_class = classes[0] if classes else 'Adventurer'
        
        # Template-based fallback backstories
        backstory_templates = {
            "main_backstory": f"{name} was born a {species} in a distant land, where they discovered their calling as a {primary_class}. Through trials and hardship, they developed the skills that would define their path as an adventurer.",
            
            "origin": f"Hails from a {species} community where {primary_class.lower()} traditions run deep in the culture.",
            
            "motivation": f"Driven by a desire to master the {primary_class.lower()} arts and prove themselves worthy of their heritage.",
            
            "secret": f"Carries a burden from their past that they've never shared with anyone, related to how they became a {primary_class}.",
            
            "relationships": f"Maintains connections to their {species} roots while forging new bonds with fellow adventurers who share their goals."
        }
        
        # Customize based on description keywords
        description_lower = user_description.lower()
        
        if any(word in description_lower for word in ["tragic", "loss", "death"]):
            backstory_templates["secret"] = "Haunted by a tragic loss that set them on their current path."
            backstory_templates["motivation"] = "Seeks redemption or justice for past wrongs."
        
        if any(word in description_lower for word in ["noble", "royal"]):
            backstory_templates["origin"] = "Born into nobility but chose the adventurer's life for reasons they keep private."
        
        if any(word in description_lower for word in ["mysterious", "unknown"]):
            backstory_templates["origin"] = "Origins shrouded in mystery, even to themselves."
            backstory_templates["secret"] = "Possesses knowledge or abilities they don't fully understand."
        
        logger.info("Using fallback backstory template")
        return backstory_templates
# ============================================================================
# CUSTOM CONTENT GENERATOR
# ============================================================================

class CustomContentGenerator:
    """Enhanced generator for custom species, classes, items, and spells aligned with character concept."""
    
    def __init__(self, llm_service, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
        self.enhanced_generator = EnhancedCustomContentGenerator(llm_service, content_registry)
    
    def generate_custom_content_for_character(self, character_data: Dict[str, Any], 
                                            user_description: str) -> Dict[str, List[str]]:
        """Generate comprehensive custom content aligned with the character concept."""
        
        created_content = {
            "species": [],
            "classes": [],
            "spells": [],
            "weapons": [],
            "armor": [],
            "feats": [],
            "items": []
        }
        
        # Generate custom species if needed
        if self._should_create_custom_species(character_data, user_description):
            species = self._generate_custom_species(character_data, user_description)
            if species:
                self.content_registry.register_species(species)
                created_content["species"].append(species.name)
        
        # Generate custom class if needed
        if self._should_create_custom_class(character_data, user_description):
            custom_class = self._generate_custom_class(character_data, user_description)
            if custom_class:
                self.content_registry.register_class(custom_class)
                created_content["classes"].append(custom_class.name)
        
        # Generate custom spells
        if self._character_is_spellcaster(character_data):
            spells = self.enhanced_generator.generate_custom_spells_for_character(
                character_data, user_description, count=2
            )
            for spell in spells:
                created_content["spells"].append(spell.name)
        
        # Generate custom weapons
        weapons = self.enhanced_generator.generate_custom_weapons_for_character(
            character_data, user_description, count=1
        )
        for weapon in weapons:
            created_content["weapons"].append(weapon.name)
        
        # Generate custom armor
        armor = self.enhanced_generator.generate_custom_armor_for_character(
            character_data, user_description
        )
        if armor:
            created_content["armor"].append(armor.name)
        
        # Generate custom feat
        feat = self.enhanced_generator.generate_custom_feat_for_character(
            character_data, user_description
        )
        if feat:
            created_content["feats"].append(feat.name)
        
        # Generate miscellaneous custom items
        items = self._generate_custom_items(character_data, user_description)
        for item in items:
            self.content_registry.register_item(item)
            created_content["items"].append(item.name)
        
        return created_content
    
    def _character_is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character has spellcasting capabilities."""
        classes = list(character_data.get("classes", {}).keys())
        spellcasting_classes = [
            "wizard", "sorcerer", "warlock", "cleric", "druid", "bard",
            "paladin", "ranger", "eldritch knight", "arcane trickster"
        ]
        
        return any(cls.lower() in spellcasting_classes for cls in classes)
    
    def _should_create_custom_species(self, character_data: Dict[str, Any], 
                                    user_description: str) -> bool:
        """Determine if a custom species should be created."""
        description_lower = user_description.lower()
        
        # Look for unique species indicators
        unique_indicators = [
            "unique race", "custom species", "hybrid", "transformed", "cursed form",
            "elemental being", "construct", "undead", "celestial", "fiend", "fey creature"
        ]
        
        return any(indicator in description_lower for indicator in unique_indicators)
    
    def _should_create_custom_class(self, character_data: Dict[str, Any], 
                                  user_description: str) -> bool:
        """Determine if a custom class should be created."""
        description_lower = user_description.lower()
        
        # Look for unique class concepts
        unique_class_indicators = [
            "unique class", "custom abilities", "special powers", "new type of",
            "combines", "fusion of", "never-before-seen", "revolutionary"
        ]
        
        return any(indicator in description_lower for indicator in unique_class_indicators)
####
    def _generate_custom_armor_for_character(self, character_data: Dict[str, Any], 
                                        user_description: str) -> Optional[CustomArmor]:
        """Generate custom armor with complete D&D 5e compliance."""
        
        character_level = character_data.get("level", 1)
        classes = list(character_data.get("classes", {}).keys())
        primary_class = classes[0] if classes else "Fighter"
        
        # Determine appropriate armor type and AC based on class
        if primary_class.lower() in ["wizard", "sorcerer", "warlock"]:
            armor_type = "Light"
            base_ac = 11
            dex_bonus = "full"
            str_req = 0
            stealth_disadvantage = False
        elif primary_class.lower() in ["rogue", "ranger", "bard", "monk"]:
            armor_type = "Medium"
            base_ac = 13
            dex_bonus = "max_2"
            str_req = 0
            stealth_disadvantage = False
        else:  # Fighter, Paladin, Cleric, etc.
            armor_type = "Heavy"
            base_ac = 16
            dex_bonus = "none"
            str_req = 13
            stealth_disadvantage = True
        
        magical = character_level >= 5
        magical_bonus = 1 if magical else 0
        
        prompt = f"""Create unique D&D 5e armor that fits this character concept. Return ONLY valid JSON.

    CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {primary_class}
    DESCRIPTION: {user_description}
    CHARACTER LEVEL: {character_level}
    ARMOR TYPE: {armor_type}
    MAGICAL ARMOR: {"Yes" if magical else "No"}

    IMPORTANT: Follow complete D&D 5e armor rules including proficiency, don/doff times, and penalties.

    JSON Format:
    {{
        "name": "Unique Armor Name",
        "armor_type": "{armor_type}",
        "ac_base": {base_ac + magical_bonus},
        "dex_bonus_type": "{dex_bonus}",
        "strength_requirement": {str_req},
        "stealth_disadvantage": {str(stealth_disadvantage).lower()},
        "cost": "150 gp",
        "weight": "25 lb.",
        "description": "Detailed armor description, appearance, and craftsmanship",
        "origin_story": "How this armor was created or came to be",
        "magical": {str(magical).lower()},
        "magical_bonus": {magical_bonus},
        "special_abilities": ["Special magical ability if applicable"],
        "damage_resistances": ["fire"],
        "special_properties": ["Unique property of this armor"]
    }}

    ARMOR RULES:
    - Light Armor: AC 11-12, full Dex modifier, no Str requirement, no stealth penalty
    - Medium Armor: AC 12-15, Dex modifier (max +2), no Str requirement, some stealth penalty
    - Heavy Armor: AC 14-18, no Dex modifier, Str requirement 13-15, stealth disadvantage
    - Don/Doff times: Light (1 min), Medium (5 min don/1 min doff), Heavy (10 min don/5 min doff)

    DEX BONUS TYPES:
    - "full": Add full Dexterity modifier (Light armor)
    - "max_2": Add Dexterity modifier, maximum +2 (Medium armor)  
    - "none": No Dexterity modifier added (Heavy armor)

    REQUIREMENTS:
    - Match armor to character's class and fighting style
    - Follow D&D 5e armor design principles and AC ranges
    - Include appropriate restrictions and requirements
    - Balance magical abilities for character level
    - Make the armor feel unique and thematic"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            armor = CustomArmor(
                name=data["name"],
                armor_type=data["armor_type"],
                ac_base=data["ac_base"],
                dex_bonus_type=data["dex_bonus_type"],
                cost=data.get("cost", ""),
                weight=data.get("weight", "")
            )
            
            # Set D&D 5e specific attributes
            armor.strength_requirement = data.get("strength_requirement", 0)
            armor.stealth_disadvantage = data.get("stealth_disadvantage", False)
            
            # Set descriptions
            armor.description = data.get("description", "")
            armor.origin_story = data.get("origin_story", "")
            
            # Set magical properties
            armor.magical = data.get("magical", False)
            armor.magical_bonus = data.get("magical_bonus", 0)
            armor.special_abilities = data.get("special_abilities", [])
            armor.damage_resistances = data.get("damage_resistances", [])
            armor.special_properties = data.get("special_properties", [])
            
            # Validate the armor design
            validation = armor.validate_armor_design()
            if validation["warnings"]:
                logger.warning(f"Custom armor validation warnings: {validation['warnings']}")
            if not validation["valid"]:
                logger.error(f"Custom armor validation failed: {validation['issues']}")
                # Try to fix common issues
                armor = self._fix_armor_issues(armor, validation["issues"])
            
            return armor
            
        except Exception as e:
            logger.error(f"Failed to generate custom armor: {e}")
            return None

    def _fix_armor_issues(self, armor: CustomArmor, issues: List[str]) -> CustomArmor:
        """Attempt to fix common armor design issues."""
        
        for issue in issues:
            if "Invalid armor type" in issue:
                armor.armor_type = "Medium"  # Default to medium
                armor.dex_bonus_type = "max_2"
            elif "AC" in issue and "outside typical range" in issue:
                # Adjust AC to be within typical range
                ac_ranges = {
                    "Light": (11, 12),
                    "Medium": (12, 15), 
                    "Heavy": (14, 18),
                    "Shield": (2, 2)
                }
                if armor.armor_type in ac_ranges:
                    min_ac, max_ac = ac_ranges[armor.armor_type]
                    base_ac = armor.ac_base - armor.magical_bonus
                    if base_ac < min_ac:
                        armor.ac_base = min_ac + armor.magical_bonus
                    elif base_ac > max_ac:
                        armor.ac_base = max_ac + armor.magical_bonus
        
        return armor
####
    def _generate_custom_class(self, character_data: Dict[str, Any], 
                            user_description: str) -> Optional[CustomClass]:
        """Generate a custom class compliant with D&D 5e 2024 rules."""
        
        character_level = character_data.get("level", 1)
        
        prompt = f"""Create a unique D&D 5e (2024 rules) character class based on this description. Return ONLY valid JSON.

    DESCRIPTION: {user_description}
    CHARACTER CONCEPT: {character_data.get('name', 'Unknown')} - {', '.join(character_data.get('classes', {}).keys())}

    IMPORTANT: Follow D&D 5e 2024 rules:
    - Classes define core mechanics and problem-solving approaches
    - Each level grants new features and improvements
    - ASI levels at 4, 8, 12, 16, 19 (standard progression)
    - Hit die should be d6, d8, d10, or d12
    - Exactly 2 saving throw proficiencies
    - Clear role and problem-solving style

    JSON Format:
    {{
        "name": "Custom Class Name",
        "description": "Detailed description of the class concept and theme",
        "hit_die": 8,
        "primary_abilities": ["dexterity", "wisdom"],
        "saving_throws": ["dexterity", "wisdom"],
        "problem_solving_style": "stealth and precision",
        "role_description": "striker and scout",
        "armor_proficiencies": ["light"],
        "weapon_proficiencies": ["simple", "shortswords", "longswords"],
        "skill_proficiencies": ["Acrobatics", "Athletics", "Deception", "Insight", "Investigation", "Perception", "Sleight of Hand", "Stealth"],
        "skill_choices": 4,
        "spellcasting_ability": "wisdom",
        "caster_type": "none",
        "resource_name": "Focus Points",
        "resource_recovery": "short_rest",
        "multiclass_prereq": {{"dexterity": 13}},
        "level_features": {{
            "1": [
                {{"name": "Starting Feature 1", "description": "Core class ability", "type": "feature"}},
                {{"name": "Starting Feature 2", "description": "Another core ability", "type": "feature"}}
            ],
            "2": [
                {{"name": "Level 2 Feature", "description": "Gained at level 2", "type": "feature"}}
            ],
            "3": [
                {{"name": "Subclass Choice", "description": "Choose specialization", "type": "choice"}}
            ],
            "4": [
                {{"name": "Ability Score Improvement", "description": "ASI or feat", "type": "asi"}}
            ],
            "5": [
                {{"name": "Major Feature", "description": "Significant power increase", "type": "feature"}}
            ],
            "20": [
                {{"name": "Capstone Feature", "description": "Ultimate class ability", "type": "feature"}}
            ]
        }},
        "resource_progression": {{
            "1": 1, "2": 1, "3": 2, "4": 2, "5": 3
        }}
    }}

    REQUIREMENTS:
    - Create a class that offers a unique problem-solving approach
    - Include meaningful features at key levels (1, 2, 3, 5, 6, 10, 14, 18, 20)
    - Balance power progression appropriately
    - Define clear role and mechanics
    - Match the theme to the character description"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            custom_class = CustomClass(
                name=data["name"],
                description=data["description"],
                hit_die=data.get("hit_die", 8),
                primary_abilities=data["primary_abilities"],
                saving_throws=data["saving_throws"]
            )
            
            # Set core attributes
            custom_class.problem_solving_style = data.get("problem_solving_style", "")
            custom_class.role_description = data.get("role_description", "")
            
            # Set proficiencies
            custom_class.armor_proficiencies = data.get("armor_proficiencies", [])
            custom_class.weapon_proficiencies = data.get("weapon_proficiencies", [])
            custom_class.skill_proficiencies = data.get("skill_proficiencies", [])
            custom_class.skill_choices = data.get("skill_choices", 2)
            
            # Set spellcasting if applicable
            custom_class.spellcasting_ability = data.get("spellcasting_ability", "")
            caster_type = data.get("caster_type", "none")
            if caster_type != "none":
                custom_class.set_spellcasting_progression(caster_type)
            
            # Set class resource
            custom_class.resource_name = data.get("resource_name", "")
            custom_class.resource_recovery = data.get("resource_recovery", "long_rest")
            custom_class.resource_progression = data.get("resource_progression", {})
            
            # Set multiclassing
            custom_class.multiclass_prereq = data.get("multiclass_prereq", {})
            
            # Set level features
            level_features = data.get("level_features", {})
            for level_str, features in level_features.items():
                level = int(level_str)
                for feature in features:
                    custom_class.add_class_feature(
                        level, 
                        feature["name"], 
                        feature["description"],
                        feature.get("type", "feature")
                    )
            
            # Validate the class design
            validation = custom_class.validate_class_design()
            if validation["warnings"]:
                logger.warning(f"Custom class validation warnings: {validation['warnings']}")
            if not validation["valid"]:
                logger.error(f"Custom class validation failed: {validation['issues']}")
                return None
            
            return custom_class
            
        except Exception as e:
            logger.error(f"Failed to generate custom class: {e}")
            return None

####   
    def _generate_custom_species(self, character_data: Dict[str, Any], 
                            user_description: str) -> Optional[CustomSpecies]:
        """Generate a custom species compliant with D&D 5e 2024 rules including sleep mechanics."""
        
        character_level = character_data.get("level", 1)
        
        prompt = f"""Create a unique D&D 5e (2024 rules) species based on this description. Return ONLY valid JSON.

    DESCRIPTION: {user_description}
    CHARACTER CONCEPT: {character_data.get('name', 'Unknown')} - {', '.join(character_data.get('classes', {}).keys())}
    CHARACTER LEVEL: {character_level}

    IMPORTANT: Follow D&D 5e 2024 rules:
    - Species do NOT provide ability score bonuses (those come from background)
    - Species can have features that scale with character level
    - Species can gain innate spellcasting at specific levels
    - Focus on unique traits, resistances, and special abilities
    - Consider sleep and rest mechanics for non-humanoid species

    JSON Format:
    {{
        "name": "Species Name",
        "description": "Detailed description of the species, their culture, and appearance",
        "creature_type": "Humanoid",
        "size": "Medium",
        "speed": 30,
        "innate_traits": [
            "Trait Name: Description of always-active ability",
            "Another Trait: Another constant ability"
        ],
        "level_features": {{
            "1": [
                {{"name": "Starting Feature", "description": "What this feature does"}}
            ],
            "3": [
                {{"name": "Level 3 Feature", "description": "Feature gained at level 3"}}
            ],
            "7": [
                {{"name": "Level 7 Feature", "description": "Feature gained at level 7"}}
            ]
        }},
        "damage_resistances": ["fire", "poison"],
        "condition_immunities": ["magically induced sleep"],
        "darkvision": 60,
        "languages": ["Common", "Species Language"],
        "movement_types": {{"walk": 30, "swim": 20}},
        "innate_spellcasting": {{
            "3": {{"0": ["Light"], "1": ["Detect Magic"]}},
            "7": {{"2": ["Misty Step"]}}
        }},
        "spellcasting_ability": "charisma",
        "scaling_features": {{
            "breath_weapon": "Damage increases by 1d6 at levels 6, 11, and 16"
        }},
        "sleep_mechanics": {{
            "needs_sleep": false,
            "sleep_type": "trance",
            "rest_duration": 4,
            "rest_state": "semiconscious",
            "sleep_immunity": true,
            "charm_resistance": true,
            "special_rest_rules": ["Meditates instead of sleeping", "Retains consciousness during rest"]
        }}
    }}

    SLEEP/REST TYPES:
    - "normal": Traditional 8-hour sleep (most humanoids)
    - "trance": 4-hour meditation while semiconscious (elf-like)
    - "inactive_state": 4-6 hour motionless state while conscious (reborn-like)
    - "none": No sleep needed but still requires rest periods (undead-like)

    REST STATES:
    - "unconscious": Traditional sleep
    - "semiconscious": Aware but resting (trance)
    - "conscious": Fully aware but inactive

    REQUIREMENTS:
    - Create features that are thematically appropriate for the description
    - Include level-based progression (features at levels 1, 3, 7, etc.)
    - Add innate spellcasting if appropriate for the concept
    - Include resistances/immunities that make sense
    - Consider unique sleep/rest mechanics for non-standard species
    - Make species feel unique and impactful"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            species = CustomSpecies(
                name=data["name"],
                description=data["description"],
                creature_type=data.get("creature_type", "Humanoid"),
                size=data.get("size", "Medium"),
                speed=data.get("speed", 30)
            )
            
            # Set innate traits
            species.innate_traits = data.get("innate_traits", [])
            
            # Set level features
            level_features = data.get("level_features", {})
            for level_str, features in level_features.items():
                level = int(level_str)
                for feature in features:
                    species.add_level_feature(level, feature["name"], feature["description"])
            
            # Set resistances and immunities
            species.damage_resistances = data.get("damage_resistances", [])
            species.damage_immunities = data.get("damage_immunities", [])
            species.condition_immunities = data.get("condition_immunities", [])
            
            # Set senses
            species.darkvision = data.get("darkvision", 0)
            species.special_senses = data.get("special_senses", [])
            
            # Set languages
            species.languages = data.get("languages", ["Common"])
            
            # Set movement
            movement_types = data.get("movement_types", {"walk": 30})
            species.movement_types = movement_types
            
            # Set innate spellcasting
            innate_spells = data.get("innate_spellcasting", {})
            species.spellcasting_ability = data.get("spellcasting_ability", "")
            for level_str, spell_dict in innate_spells.items():
                level = int(level_str)
                for spell_level_str, spells in spell_dict.items():
                    spell_level = int(spell_level_str)
                    for spell in spells:
                        species.add_innate_spell(level, spell, spell_level)
            
            # Set scaling features
            species.scaling_features = data.get("scaling_features", {})
            
            # NEW: Set sleep mechanics
            sleep_data = data.get("sleep_mechanics", {})
            if sleep_data:
                species.sleep_mechanics.update(sleep_data)
            
            # Auto-configure common sleep types
            sleep_type = species.sleep_mechanics.get("sleep_type", "normal")
            if sleep_type == "trance":
                species.set_elf_like_trance()
            elif sleep_type == "inactive_state" and species.creature_type == "Undead":
                species.set_reborn_like_rest()
            elif sleep_type == "none":
                species.set_undead_like_rest()
            elif species.creature_type == "Construct":
                species.set_construct_like_rest()
            
            return species
            
        except Exception as e:
            logger.error(f"Failed to generate custom species: {e}")
            return None
####
    
    def _generate_custom_items(self, character_data: Dict[str, Any], 
                             user_description: str) -> List[CustomItem]:
        """Generate custom items for the character."""
        
        prompt = f"""Create 2-3 unique items for this D&D character. Return ONLY valid JSON array.

DESCRIPTION: {user_description}
CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {', '.join(character_data.get('classes', {}).keys())}

JSON Format:
[
    {{
        "name": "Item Name",
        "type": "weapon",
        "description": "Detailed description of the item and its significance",
        "properties": {{
            "damage": "1d8",
            "damage_type": "slashing",
            "magical": true,
            "special_abilities": ["Ability 1", "Ability 2"]
        }}
    }},
    {{
        "name": "Another Item",
        "type": "equipment",
        "description": "Description of special equipment",
        "properties": {{
            "magical": true,
            "uses_per_day": 3,
            "effect": "What it does"
        }}
    }}
]"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            items = []
            for item_data in data:
                item = CustomItem(
                    name=item_data["name"],
                    item_type=item_data["type"],
                    description=item_data["description"],
                    properties=item_data.get("properties", {})
                )
                items.append(item)
            
            return items
        except Exception as e:
            logger.error(f"Failed to generate custom items: {e}")
            return []

# ============================================================================
# LLM SERVICE LAYER
# ============================================================================
import threading
import time
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

@contextmanager
def timeout_context(duration):
    """Cross-platform timeout context manager using threading."""
    result = {}
    exception = {}
    
    def target():
        try:
            result['value'] = yield
        except Exception as e:
            exception['error'] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=duration)
    
    if thread.is_alive():
        # Thread is still running, timeout occurred
        raise TimeoutError(f"Operation timed out after {duration} seconds")
    
    if 'error' in exception:
        raise exception['error']
    
    return result.get('value')

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(self, prompt: str, timeout_seconds: int = 30) -> str:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass

class OllamaLLMService(LLMService):
    """Ollama LLM service implementation with enhanced timeout and error handling."""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        try:
            import ollama
            self.model = model
            self.client = ollama.Client(host=host)
            self.executor = ThreadPoolExecutor(max_workers=1)
        except ImportError:
            raise ImportError("Ollama package not installed. Run: pip install ollama")
    
    def generate(self, prompt: str, timeout_seconds: int = 30) -> str:
        """Generate response with robust timeout protection and fallback."""
        
        # Pre-validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Empty prompt provided")
        
        # Shorten prompt if too long to prevent timeouts
        if len(prompt) > 8000:
            logger.warning("Prompt too long, truncating...")
            prompt = prompt[:8000] + "\n\nCRITICAL: Return complete valid JSON only."
        
        try:
            logger.info(f"Sending request to Ollama (timeout: {timeout_seconds}s)...")
            
            # Use ThreadPoolExecutor for better timeout control
            future = self.executor.submit(self._make_ollama_request, prompt)
            
            try:
                content = future.result(timeout=timeout_seconds)
                logger.info(f"Received response: {len(content)} characters")
                return content
                
            except FutureTimeoutError:
                logger.error(f"Request timed out after {timeout_seconds} seconds")
                future.cancel()  # Try to cancel the request
                raise TimeoutError(f"LLM request timed out after {timeout_seconds} seconds")
                
        except TimeoutError:
            raise  # Re-raise timeout errors
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    def _make_ollama_request(self, prompt: str) -> str:
        """Make the actual Ollama request (to be run in thread)."""
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a D&D assistant. Respond ONLY with valid JSON. No explanations, no markdown, no extra text. Just JSON."
                },
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,  # Further reduced for speed
                "num_ctx": 2048,     # Reduced context window
                "stop": ["```", "Note:", "Here's", "I'll", "**"],
                "stream": False      # Ensure non-streaming response
            }
        )
        
        content = response["message"]["content"]
        if not content or not content.strip():
            raise Exception("Empty response from Ollama")
        
        return content
    
    def test_connection(self) -> bool:
        """Test connection with short timeout."""
        try:
            future = self.executor.submit(
                self.client.generate, 
                model=self.model, 
                prompt="Test"
            )
            future.result(timeout=5)  # 5-second test timeout
            return True
        except Exception:
            return False
    
    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# ============================================================================
# CHARACTER DATA MODELS (Enhanced)
# ============================================================================

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
        self.level_manager = CharacterLevelManager(self)
        self.magic_item_manager = MagicItemManager(self)
        
        # Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        
        # Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory = ""
        
        # Enhanced backstory elements
        self.detailed_backstory: Dict[str, str] = {}
        self.custom_content_used: List[str] = []
    
    @property
    def total_level(self) -> int:
        return sum(self.character_classes.values()) if self.character_classes else 1
    
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
    
    def validate(self) -> Dict[str, Any]:
        issues = []
        warnings = []
        
        if not self.name.strip():
            warnings.append("Character name is empty")
        if not self.species:
            issues.append("Species is required")
        if not self.character_classes:
            issues.append("At least one class is required")
        
        return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}

class CharacterState:
    """Current character state - changes during gameplay."""
    
    def __init__(self):
        # Hit points
        self.current_hit_points = 0
        self.temporary_hit_points = 0
        
        # Equipment
        self.armor = ""
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        
        # Conditions
        self.active_conditions: Dict[str, Any] = {}
        self.exhaustion_level = 0
        
        # Currency
        self.currency = {"copper": 0, "silver": 0, "gold": 0, "platinum": 0}
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        result = {"temp_hp_damage": 0, "hp_damage": 0}
        
        if self.temporary_hit_points > 0:
            temp_damage = min(damage, self.temporary_hit_points)
            self.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        if damage > 0:
            self.current_hit_points -= damage
            result["hp_damage"] = damage
            if self.current_hit_points < 0:
                self.current_hit_points = 0
        
        return result

class CharacterStats:
    """Calculated character statistics."""
    
    def __init__(self, core: CharacterCore, state: CharacterState):
        self.core = core
        self.state = state
        self._cache = {}
    
    @property
    def proficiency_bonus(self) -> int:
        if "proficiency_bonus" not in self._cache:
            level = self.core.total_level
            self._cache["proficiency_bonus"] = 2 + ((level - 1) // 4)
        return self._cache["proficiency_bonus"]
    
    @property
    def armor_class(self) -> int:
        if "armor_class" not in self._cache:
            base_ac = 10 + self.core.dexterity.modifier
            # Enhanced armor calculation
            armor_name = self.state.armor.lower()
            if "leather" in armor_name:
                base_ac = 11 + self.core.dexterity.modifier
            elif "studded" in armor_name:
                base_ac = 12 + self.core.dexterity.modifier
            elif "chain shirt" in armor_name:
                base_ac = 13 + min(self.core.dexterity.modifier, 2)
            elif "chain mail" in armor_name:
                base_ac = 16
            elif "plate" in armor_name:
                base_ac = 18
            elif "magical" in armor_name or "enchanted" in armor_name:
                base_ac = 16 + 2  # Assume +2 magical armor
            
            self._cache["armor_class"] = base_ac
        return self._cache["armor_class"]
    
    @property
    def max_hit_points(self) -> int:
        if "max_hit_points" not in self._cache:
            if not self.core.character_classes:
                self._cache["max_hit_points"] = 1
                return 1
            
            hit_die_sizes = {
                "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                "Wizard": 6, "Sorcerer": 6, "Rogue": 8, "Bard": 8,
                "Cleric": 8, "Druid": 8, "Monk": 8, "Warlock": 8
            }
            
            total = 0
            con_mod = self.core.constitution.modifier
            
            for class_name, level in self.core.character_classes.items():
                hit_die = hit_die_sizes.get(class_name, 8)  # Default to d8
                if level > 0:
                    # First level gets max hit die + con mod
                    total += hit_die + con_mod
                    # Subsequent levels get average + con mod
                    total += (level - 1) * ((hit_die // 2) + 1 + con_mod)
            
            self._cache["max_hit_points"] = max(1, total)
        return self._cache["max_hit_points"]
    
    def invalidate_cache(self):
        self._cache.clear()

# ============================================================================
# MAIN CHARACTER SHEET (Enhanced)
# ============================================================================

class CharacterSheet:
    """Main character sheet combining all components."""
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
    
    def get_character_summary(self) -> Dict[str, Any]:
        return {
            "name": self.core.name,
            "species": self.core.species,
            "level": self.core.total_level,
            "classes": self.core.character_classes,
            "background": self.core.background,
            "alignment": self.core.alignment,
            "ability_scores": {
                "strength": self.core.strength.total_score,
                "dexterity": self.core.dexterity.total_score,
                "constitution": self.core.constitution.total_score,
                "intelligence": self.core.intelligence.total_score,
                "wisdom": self.core.wisdom.total_score,
                "charisma": self.core.charisma.total_score
            },
            "ability_modifiers": {
                "strength": self.core.strength.modifier,
                "dexterity": self.core.dexterity.modifier,
                "constitution": self.core.constitution.modifier,
                "intelligence": self.core.intelligence.modifier,
                "wisdom": self.core.wisdom.modifier,
                "charisma": self.core.charisma.modifier
            },
            "ac": self.stats.armor_class,
            "hp": {
                "current": self.state.current_hit_points,
                "max": self.stats.max_hit_points,
                "temp": self.state.temporary_hit_points
            },
            "proficiency_bonus": self.stats.proficiency_bonus,
            "proficient_skills": [skill for skill, prof in self.core.skill_proficiencies.items() 
                                if prof != ProficiencyLevel.NONE],
            "personality_traits": self.core.personality_traits,
            "ideals": self.core.ideals,
            "bonds": self.core.bonds,
            "flaws": self.core.flaws,
            "backstory": self.core.backstory,
            "detailed_backstory": self.core.detailed_backstory,
            "custom_content": self.core.custom_content_used,
            "armor": self.state.armor,
            "weapons": self.state.weapons,
            "equipment": self.state.equipment
        }
    
    def calculate_all_derived_stats(self):
        self.stats.invalidate_cache()
        if self.state.current_hit_points == 0:  # Only set if not already set
            self.state.current_hit_points = self.stats.max_hit_points

# ============================================================================
# ENHANCED CHARACTER CREATOR WITH ITERATION
# ============================================================================

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable

@dataclass
class CreationConfig:
    """Configuration for character creation process."""
    base_timeout: int = 20
    backstory_timeout: int = 15
    custom_content_timeout: int = 30
    max_retries: int = 2
    enable_progress_feedback: bool = True
    auto_save: bool = False
    
class CreationResult:
    """Result container for character creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        return self.success and bool(self.data)

class CharacterValidator:
    """Handles validation of character data."""
    
    @staticmethod
    def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
        """Validate basic character data structure."""
        result = CreationResult()
        
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        missing_fields = [field for field in required_fields if field not in character_data]
        
        if missing_fields:
            result.error = f"Missing required fields: {', '.join(missing_fields)}"
            return result
        
        # Validate ability scores
        abilities = character_data.get("ability_scores", {})
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in abilities:
                result.add_warning(f"Missing ability score: {ability}")
            else:
                score = abilities[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    result.add_warning(f"Invalid {ability} score: {score}")
        
        # Validate level
        level = character_data.get("level", 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            result.add_warning(f"Invalid character level: {level}")
        
        result.success = True
        result.data = character_data
        return result
    
    @staticmethod
    def validate_custom_content(character_data: Dict[str, Any], description: str,
                              needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
        """Validate that custom content was created when needed."""
        result = CreationResult(success=True, data=character_data)
        
        # Check species
        if needs_custom_species:
            species = character_data.get("species", "").lower()
            standard_species = [
                "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
                "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
                "goliath", "tabaxi", "kenku", "lizardfolk", "tortle"
            ]
            
            if species in standard_species:
                result.add_warning(f"Used standard species '{species}' when custom was expected")
                # Fix by generating custom species name
                character_data["species"] = CharacterDataGenerator._generate_custom_species_name(description)
        
        # Check class
        if needs_custom_class:
            classes = character_data.get("classes", {})
            class_names = [name.lower() for name in classes.keys()]
            standard_classes = [
                "barbarian", "bard", "cleric", "druid", "fighter", "monk",
                "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
                "artificer", "blood hunter"
            ]
            
            for class_name in class_names:
                if class_name in standard_classes:
                    result.add_warning(f"Used standard class '{class_name}' when custom was expected")
                    # Fix by replacing with custom class
                    old_level = classes[list(classes.keys())[0]]
                    custom_class = CharacterDataGenerator._generate_custom_class_name(description)
                    character_data["classes"] = {custom_class: old_level}
                    break
        
        return result

class CharacterDataGenerator:
    """Handles core character data generation."""
    
    def __init__(self, llm_service, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    def generate_character_data(self, description: str, level: int) -> CreationResult:
        """Generate core character data with retry logic."""
        start_time = time.time()
        
        needs_custom_species = self._needs_custom_species(description)
        needs_custom_class = self._needs_custom_class(description)
        
        # Create targeted prompt
        prompt = self._create_character_prompt(description, level, needs_custom_species, needs_custom_class)
        
        timeout_progression = [self.config.base_timeout, self.config.base_timeout - 5]
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Character generation attempt {attempt + 1}/{self.config.max_retries}")
                
                timeout = timeout_progression[min(attempt, len(timeout_progression) - 1)]
                response = self.llm_service.generate(prompt, timeout_seconds=timeout)
                
                # Clean and parse response
                cleaned_response = self._clean_json_response(response)
                character_data = json.loads(cleaned_response)
                character_data["level"] = level
                
                # Validate basic structure
                validation_result = self.validator.validate_basic_structure(character_data)
                if not validation_result.success:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(f"Validation failed: {validation_result.error}, retrying...")
                        continue
                    else:
                        character_data = self._apply_fixes(character_data, validation_result.warnings, description, level)
                
                # Validate and fix custom content
                custom_validation = self.validator.validate_custom_content(
                    character_data, description, needs_custom_species, needs_custom_class
                )
                character_data = custom_validation.data
                
                result = CreationResult(success=True, data=character_data)
                result.warnings.extend(validation_result.warnings + custom_validation.warnings)
                result.creation_time = time.time() - start_time
                
                logger.info("Character generation successful")
                return result
                
            except (TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    prompt = self._get_simplified_prompt(description, level)
                    continue
                else:
                    logger.error("All attempts failed, using fallback")
                    return self._get_fallback_result(description, level, start_time)
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    return self._get_fallback_result(description, level, start_time)
        
        return self._get_fallback_result(description, level, start_time)
    
    def _create_character_prompt(self, description: str, level: int, 
                               needs_custom_species: bool, needs_custom_class: bool) -> str:
        """Create optimized character generation prompt."""
        
        custom_instructions = ""
        if needs_custom_species:
            custom_instructions += "CREATE custom species name matching description. "
        if needs_custom_class:
            custom_instructions += "CREATE custom class name matching description. "
        
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}
{custom_instructions}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Skill1","Skill2"],"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":[{{"name":"Item","quantity":1}}],"backstory":"Brief backstory"}}

Match description exactly. Return complete JSON only."""
    
    def _get_simplified_prompt(self, description: str, level: int) -> str:
        """Get simplified prompt for retry attempts."""
        return f"""Character: {description}, Level {level}
JSON: {{"name":"Name","species":"Human","level":{level},"classes":{{"Fighter":{level}}},"background":"Folk Hero","alignment":["Neutral","Good"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Athletics"],"personality_traits":["Brave"],"ideals":["Justice"],"bonds":["Community"],"flaws":["Stubborn"],"armor":"Leather","weapons":[{{"name":"Sword","damage":"1d8","properties":["versatile"]}}],"equipment":[{{"name":"Pack","quantity":1}}],"backstory":"A brave {description} warrior."}}"""
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response."""
        if not response:
            raise ValueError("Empty response")
        
        # Remove markdown and find JSON boundaries
        response = response.replace('```json', '').replace('```', '').strip()
        
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[first_brace:last_brace + 1]
        
        # Basic JSON repair
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json_str
    
    def _apply_fixes(self, character_data: Dict[str, Any], warnings: List[str], 
                    description: str, level: int) -> Dict[str, Any]:
        """Apply fixes for common character data issues."""
        
        # Fix missing fields
        defaults = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "classes": {"Fighter": level},
            "ability_scores": {
                "strength": 13, "dexterity": 12, "constitution": 14,
                "intelligence": 10, "wisdom": 11, "charisma": 8
            },
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"]
        }
        
        for field, default_value in defaults.items():
            if field not in character_data or not character_data[field]:
                character_data[field] = default_value
                logger.info(f"Added default value for missing field: {field}")
        
        return character_data
    
    def _get_fallback_result(self, description: str, level: int, start_time: float) -> CreationResult:
        """Generate fallback character result."""
        character_data = self._generate_fallback_character(description, level)
        result = CreationResult(success=True, data=character_data)
        result.add_warning("Used fallback character generation")
        result.creation_time = time.time() - start_time
        return result
    
    def _generate_fallback_character(self, description: str, level: int) -> Dict[str, Any]:
        """Generate a basic fallback character."""
        return {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "ability_scores": {
                "strength": 15, "dexterity": 14, "constitution": 13,
                "intelligence": 12, "wisdom": 10, "charisma": 8
            },
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "personality_traits": [f"A {description} with a strong sense of duty"],
            "ideals": ["Protection of the innocent"],
            "bonds": ["My community depends on me"],
            "flaws": ["I'm slow to trust strangers"],
            "armor": "Chain Mail",
            "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventuring Pack", "quantity": 1}],
            "backstory": f"A {description} who rose to prominence through determination and skill."
        }
    
    def _needs_custom_species(self, description: str) -> bool:
        """Determine if description requires custom species."""
        description_lower = description.lower()
        
        custom_indicators = [
            "frog", "toad", "amphibian", "reptilian", "avian", "bird", "cat", "dog", 
            "wolf", "dragon", "serpent", "snake", "fish", "aquatic", "elemental", 
            "construct", "undead", "ghost", "spirit", "demon", "devil", "angel", 
            "celestial", "plant", "tree", "flower", "fungus", "crystal", "gem",
            "mechanical", "clockwork", "automaton", "unique race", "custom species"
        ]
        
        standard_species = [
            "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
            "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
            "goliath", "tabaxi", "kenku", "lizardfolk", "tortle"
        ]
        
        has_custom = any(indicator in description_lower for indicator in custom_indicators)
        has_standard = any(species in description_lower for species in standard_species)
        
        return has_custom and not has_standard
    
    def _needs_custom_class(self, description: str) -> bool:
        """Determine if description requires custom class."""
        description_lower = description.lower()
        
        custom_indicators = [
            "assassin", "ninja", "samurai", "witch", "necromancer", "elementalist",
            "psion", "telepath", "shaman", "oracle", "inquisitor", "gunslinger",
            "alchemist", "inventor", "tinkerer", "mad scientist", "plague doctor",
            "shadow dancer", "death knight", "divine oracle", "storm caller",
            "beast master", "dragon rider", "demon hunter", "angel warrior",
            "unique class", "custom abilities", "new type of"
        ]
        
        standard_classes = [
            "barbarian", "bard", "cleric", "druid", "fighter", "monk",
            "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
            "artificer", "blood hunter"
        ]
        
        has_custom = any(indicator in description_lower for indicator in custom_indicators)
        has_standard = any(cls in description_lower for cls in standard_classes)
        
        return has_custom and not has_standard
    
    @staticmethod
    def _generate_custom_species_name(description: str) -> str:
        """Generate custom species name from description."""
        description_lower = description.lower()
        
        species_mapping = {
            "frog": "Batraxi", "toad": "Bufonid", "amphibian": "Amphibian-born",
            "bird": "Aarakocra-kin", "cat": "Tabaxi-kin", "dog": "Canine-folk", 
            "wolf": "Lupine", "dragon": "Dragonborn-variant", "serpent": "Serpentine",
            "snake": "Yuan-ti-kin", "fish": "Triton-kin", "plant": "Verdant-born",
            "tree": "Sylvan-touched", "crystal": "Gem-touched", "mechanical": "Warforged-variant",
            "undead": "Death-touched", "ghost": "Spirit-bound", "demon": "Fiend-touched",
            "angel": "Celestial-born", "fey": "Fey-touched", "elemental": "Genasi-variant"
        }
        
        for indicator, species_name in species_mapping.items():
            if indicator in description_lower:
                return species_name
        
        return "Unique-born"
    
    @staticmethod
    def _generate_custom_class_name(description: str) -> str:
        """Generate custom class name from description."""
        description_lower = description.lower()
        
        class_mapping = {
            "assassin": "Assassin", "ninja": "Ninja", "samurai": "Samurai", 
            "witch": "Witch", "necromancer": "Necromancer", "elementalist": "Elementalist",
            "psion": "Psion", "shaman": "Shaman", "oracle": "Oracle",
            "gunslinger": "Gunslinger", "alchemist": "Alchemist", "inventor": "Inventor",
            "mad scientist": "Mad Scientist", "plague doctor": "Plague Doctor",
            "shadow dancer": "Shadow Dancer", "death knight": "Death Knight",
            "storm caller": "Storm Caller", "beast master": "Beast Master",
            "dragon rider": "Dragon Rider", "demon hunter": "Demon Hunter"
        }
        
        for indicator, class_name in class_mapping.items():
            if indicator in description_lower:
                return class_name
        
        return "Unique Adventurer"
    
    def _generate_name_from_description(self, description: str) -> str:
        """Generate appropriate name from description."""
        description_lower = description.lower()
        
        if "wizard" in description_lower or "magic" in description_lower:
            return "Merlin"
        elif "rogue" in description_lower or "thief" in description_lower:
            return "Shadow"
        elif "knight" in description_lower or "paladin" in description_lower:
            return "Sir Galahad"
        elif "ranger" in description_lower or "archer" in description_lower:
            return "Robin"
        else:
            return "Adventurer"

class AsyncContentGenerator:
    """Handles asynchronous generation of backstory and custom content."""
    
    def __init__(self, backstory_generator, content_generator, config: CreationConfig):
        self.backstory_generator = backstory_generator
        self.content_generator = content_generator
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def generate_backstory_async(self, character_data: Dict[str, Any], description: str) -> CreationResult:
        """Generate backstory with timeout and progress feedback."""
        if self.config.enable_progress_feedback:
            print("📖 Creating backstory (15-20 seconds max)...")
        
        future = self.executor.submit(
            self.backstory_generator.generate_compelling_backstory,
            character_data, description
        )
        
        return self._wait_for_completion(
            future, 
            self.config.backstory_timeout,
            "backstory",
            lambda: self.backstory_generator._get_fallback_backstory(character_data, description)
        )
    
    def generate_custom_content_async(self, character_data: Dict[str, Any], 
                                    description: str) -> CreationResult:
        """Generate custom content with timeout."""
        if self.config.enable_progress_feedback:
            print("✨ Generating custom content...")
        
        future = self.executor.submit(
            self.content_generator.generate_custom_content_for_character,
            character_data, description
        )
        
        return self._wait_for_completion(
            future,
            self.config.custom_content_timeout,
            "custom content",
            lambda: {}
        )
    
    def _wait_for_completion(self, future, timeout: int, content_type: str, 
                           fallback_func: Callable) -> CreationResult:
        """Wait for async operation with progress feedback."""
        
        for i in range(timeout):
            try:
                result = future.result(timeout=1)
                if self.config.enable_progress_feedback:
                    print(f"   ✅ {content_type.title()} complete!")
                return CreationResult(success=True, data=result)
            except FutureTimeoutError:
                if i < timeout - 1:
                    if self.config.enable_progress_feedback:
                        print(f"   ⏳ Generating... ({i+1}s)")
                    continue
                else:
                    if self.config.enable_progress_feedback:
                        print(f"   ⚠️  {content_type.title()} generation timed out, using fallback")
                    future.cancel()
                    fallback_result = fallback_func()
                    result = CreationResult(success=True, data=fallback_result)
                    result.add_warning(f"{content_type.title()} generation timed out")
                    return result
        
        # Shouldn't reach here, but just in case
        fallback_result = fallback_func()
        result = CreationResult(success=True, data=fallback_result)
        result.add_warning(f"{content_type.title()} generation failed")
        return result
    
    def cleanup(self):
        """Clean up executor resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

class CharacterIterationManager:
    """Manages character iterations and user feedback."""
    
    def __init__(self):
        self.iterations: List[Dict[str, Any]] = []
        self.current_character: Dict[str, Any] = {}
        self.modification_history: List[str] = []
        self.user_feedback: List[str] = []
    
    def add_iteration(self, character_data: Dict[str, Any], modification: str = ""):
        """Add a new iteration of the character."""
        self.current_character = character_data.copy()
        self.iterations.append(character_data.copy())
        if modification:
            self.modification_history.append(modification)
    
    def get_current_character(self) -> Dict[str, Any]:
        """Get the current character data."""
        return self.current_character.copy()
    
    def get_iteration_count(self) -> int:
        """Get the number of iterations."""
        return len(self.iterations)
    
    def add_user_feedback(self, feedback: str):
        """Add user feedback for the current iteration."""
        self.user_feedback.append(feedback)
    
    def get_modification_history(self) -> List[str]:
        """Get the history of modifications."""
        return self.modification_history.copy()

class CharacterModifier:
    """Handles character modifications based on user feedback."""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def apply_modifications(self, current_character: Dict[str, Any], 
                          changes: str, original_description: str) -> CreationResult:
        """Apply user-requested modifications to the character."""
        
        prompt = f"""Modify this D&D character based on user changes. Return ONLY valid JSON.

CURRENT CHARACTER:
{json.dumps(current_character, indent=2)}

ORIGINAL DESCRIPTION: {original_description}
REQUESTED CHANGES: {changes}

INSTRUCTIONS:
- Keep all existing data unless specifically mentioned in changes
- Only modify aspects user specifically requested
- Maintain character consistency and D&D 5e rules
- If changing abilities/stats, keep them balanced
- Return complete modified character in same JSON format

Return only the modified character JSON, no other text."""
        
        try:
            response = self.llm_service.generate(prompt, timeout_seconds=20)
            modified_character = json.loads(response.strip())
            
            # Validate the modified character
            required_fields = ["name", "species", "level", "classes", "ability_scores"]
            if all(field in modified_character for field in required_fields):
                return CreationResult(success=True, data=modified_character)
            else:
                return CreationResult(error="Modified character missing required fields")
                
        except Exception as e:
            logger.error(f"Failed to apply character modifications: {e}")
            return CreationResult(error=f"Modification failed: {e}")

class CharacterCreator:
    """Refactored CharacterCreator with improved architecture and error handling."""
    
    def __init__(self, llm_service: 'LLMService', config: CreationConfig = None):
        self.llm_service = llm_service
        self.config = config or CreationConfig()
        
        # Core components
        self.character = CharacterSheet()
        self.content_registry = ContentRegistry()
        self.iteration_manager = CharacterIterationManager()
        
        # Generators and processors
        self.data_generator = CharacterDataGenerator(llm_service, self.config)
        self.backstory_generator = BackstoryGenerator(llm_service)
        self.content_generator = CustomContentGenerator(llm_service, self.content_registry)
        self.async_generator = AsyncContentGenerator(
            self.backstory_generator, self.content_generator, self.config
        )
        self.modifier = CharacterModifier(llm_service)
        
        # State
        self._creation_stats = {
            "total_time": 0.0,
            "iterations": 0,
            "warnings": []
        }
    
    def test_connection(self) -> bool:
        """Test LLM service connection."""
        return self.llm_service.test_connection()
    
    def create_character_iteratively(self, description: str, level: int = None,
                                   generate_custom_content: bool = True) -> Dict[str, Any]:
        """Create character with iterative refinement process."""
        
        # Auto-determine level if not provided
        if level is None:
            level = determine_level_from_description(description)
        
        if self.config.enable_progress_feedback:
            print(f"🎲 Starting iterative character creation at level {level}...")
        
        # Generate initial character
        initial_result = self._generate_initial_character(description, level, generate_custom_content)
        
        if not initial_result.is_valid():
            raise Exception(f"Initial character generation failed: {initial_result.error}")
        
        self.iteration_manager.add_iteration(initial_result.data, "Initial generation")
        self._creation_stats["warnings"].extend(initial_result.warnings)
        
        # Iterative refinement loop
        current_character = initial_result.data
        
        while True:
            # Display current character
            self._display_character_summary(current_character)
            
            # Get user choice
            choice = self._get_user_choice()
            
            if choice == "1":  # Accept character
                if self.config.enable_progress_feedback:
                    print("\n✅ Character accepted!")
                break
                
            elif choice == "2":  # Make changes
                changes = self._get_user_changes()
                if changes:
                    modification_result = self._apply_character_modifications(
                        current_character, changes, description
                    )
                    
                    if modification_result.is_valid():
                        current_character = modification_result.data
                        self.iteration_manager.add_iteration(current_character, changes)
                        self._creation_stats["warnings"].extend(modification_result.warnings)
                    else:
                        print(f"❌ Failed to apply changes: {modification_result.error}")
                        
            elif choice == "3":  # Regenerate
                if self.config.enable_progress_feedback:
                    print("\n🎲 Regenerating character...")
                
                regen_result = self._generate_initial_character(description, level, generate_custom_content)
                if regen_result.is_valid():
                    current_character = regen_result.data
                    self.iteration_manager.add_iteration(current_character, "Complete regeneration")
                    self._creation_stats["warnings"].extend(regen_result.warnings)
                else:
                    print(f"❌ Regeneration failed: {regen_result.error}")
                    
            elif choice == "4":  # View detailed backstory
                self._display_detailed_backstory(current_character)
                
            elif choice == "5":  # Start over
                if self.config.enable_progress_feedback:
                    print("\n🔄 Starting over...")
                self.iteration_manager = CharacterIterationManager()
                return self.create_character_iteratively(description, level, generate_custom_content)
                
            else:
                print("Invalid choice. Please select 1-5.")
        
        # Finalize character
        self._populate_character_from_data(current_character)
        
        # Update stats
        self._creation_stats["iterations"] = self.iteration_manager.get_iteration_count()
        
        if self.config.enable_progress_feedback:
            print(f"\n🎉 Character creation complete after {self._creation_stats['iterations']} iterations!")
            
            # Show warnings if any
            if self._creation_stats["warnings"]:
                print(f"\n💡 Notes ({len(self._creation_stats['warnings'])} warnings):")
                for warning in set(self._creation_stats["warnings"]):  # Remove duplicates
                    print(f"  • {warning}")
        
        # Auto-save if enabled
        if self.config.auto_save:
            try:
                filename = save_character(current_character)
                print(f"💾 Character auto-saved: {filename}")
            except Exception as e:
                logger.warning(f"Auto-save failed: {e}")
        
        return self.character.get_character_summary()
    
    def create_character(self, description: str, level: int = 1, 
                        generate_custom_content: bool = True) -> Dict[str, Any]:
        """Create character without iteration (single-shot)."""
        
        if self.config.enable_progress_feedback:
            print("🎲 Generating character data...")
        
        # Generate character data
        data_result = self.data_generator.generate_character_data(description, level)
        if not data_result.is_valid():
            raise Exception(f"Character generation failed: {data_result.error}")
        
        character_data = data_result.data
        
        # Generate backstory
        backstory_result = self.async_generator.generate_backstory_async(character_data, description)
        if backstory_result.is_valid():
            character_data["detailed_backstory"] = backstory_result.data
        else:
            character_data["detailed_backstory"] = {"main_backstory": "A mysterious past awaits discovery."}
        
        # Generate custom content if requested
        if generate_custom_content:
            content_result = self.async_generator.generate_custom_content_async(character_data, description)
            if content_result.is_valid():
                all_custom_content = []
                for content_type, items in content_result.data.items():
                    all_custom_content.extend(items)
                character_data["custom_content"] = all_custom_content
            else:
                character_data["custom_content"] = []
        
        # Populate character sheet
        if self.config.enable_progress_feedback:
            print("🔧 Assembling character sheet...")
        
        self._populate_character_from_data(character_data)
        
        if self.config.enable_progress_feedback:
            print("✅ Character creation complete!")
        
        return self.character.get_character_summary()
    
    def _generate_initial_character(self, description: str, level: int, 
                                   generate_custom_content: bool) -> CreationResult:
        """Generate the initial character with all components."""
        
        start_time = time.time()
        
        if self.config.enable_progress_feedback:
            print("🎲 Generating initial character data...")
        
        # Generate core character data
        data_result = self.data_generator.generate_character_data(description, level)
        if not data_result.is_valid():
            return data_result
        
        character_data = data_result.data
        warnings = data_result.warnings.copy()
        
        # Generate backstory asynchronously
        backstory_result = self.async_generator.generate_backstory_async(character_data, description)
        character_data["detailed_backstory"] = backstory_result.data
        warnings.extend(backstory_result.warnings)
        
        # Generate custom content if requested
        if generate_custom_content:
            content_result = self.async_generator.generate_custom_content_async(character_data, description)
            
            if content_result.is_valid():
                all_custom_content = []
                for content_type, items in content_result.data.items():
                    all_custom_content.extend(items)
                character_data["custom_content"] = all_custom_content
            else:
                character_data["custom_content"] = []
            
            warnings.extend(content_result.warnings)
        else:
            character_data["custom_content"] = []
        
        result = CreationResult(success=True, data=character_data)
        result.warnings = warnings
        result.creation_time = time.time() - start_time
        
        return result
    
    def _display_character_summary(self, character_data: Dict[str, Any]):
        """Display character summary for iteration review."""
        print("\n" + "="*60)
        print("CURRENT CHARACTER")
        print("="*60)
        print(self._format_character_summary_brief(character_data))
    
    def _get_user_choice(self) -> str:
        """Get user choice for character iteration."""
        print("\n" + "="*40)
        print("REFINEMENT OPTIONS")
        print("="*40)
        print("1. Accept this character")
        print("2. Change something specific")
        print("3. Regenerate completely")
        print("4. View detailed backstory")
        print("5. Start over")
        
        return input("\nWhat would you like to do? (1-5): ").strip()
    
    def _get_user_changes(self) -> str:
        """Get specific changes from user."""
        print("\nWhat would you like to change? You can specify:")
        print("- Name, species, class, background")
        print("- Ability scores (e.g., 'higher strength')")
        print("- Personality traits, ideals, bonds, flaws")
        print("- Equipment or weapons")
        print("- Backstory elements")
        print("- Any other aspect of the character")
        
        changes = input("\nDescribe the changes you want: ").strip()
        
        if not changes:
            print("No changes specified.")
            return ""
        
        return changes
    
    def _apply_character_modifications(self, current_character: Dict[str, Any], 
                                     changes: str, original_description: str) -> CreationResult:
        """Apply user-requested modifications."""
        
        if self.config.enable_progress_feedback:
            print(f"\n🔄 Applying changes: {changes}")
        
        return self.modifier.apply_modifications(current_character, changes, original_description)
    
    def _format_character_summary_brief(self, character_data: Dict[str, Any]) -> str:
        """Format brief character summary for iteration display."""
        
        output = []
        
        # Basic info
        output.append(f"Name: {character_data.get('name', 'Unknown')}")
        output.append(f"Species: {character_data.get('species', 'Unknown')}")
        
        classes = character_data.get('classes', {})
        class_str = ", ".join([f"{cls} {lvl}" for cls, lvl in classes.items()])
        output.append(f"Classes: {class_str}")
        output.append(f"Background: {character_data.get('background', 'Unknown')}")
        
        alignment = character_data.get('alignment', ['Unknown', 'Unknown'])
        output.append(f"Alignment: {alignment[0]} {alignment[1]}")
        output.append("")
        
        # Ability scores (brief)
        abilities = character_data.get("ability_scores", {})
        ability_line = []
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = abilities.get(ability, 10)
            ability_line.append(f"{ability[:3].upper()}: {score}")
        output.append("Abilities: " + " | ".join(ability_line))
        output.append("")
        
        # Personality (brief)
        traits = character_data.get("personality_traits", [])
        if traits:
            output.append(f"Personality: {traits[0]}")
        
        ideals = character_data.get("ideals", [])
        if ideals:
            output.append(f"Ideals: {ideals[0]}")
        
        # Equipment (brief)
        armor = character_data.get("armor", "None")
        weapons = character_data.get("weapons", [])
        weapon_names = [w.get("name", str(w)) if isinstance(w, dict) else str(w) for w in weapons[:2]]
        output.append(f"Equipment: {armor}, {', '.join(weapon_names) if weapon_names else 'No weapons'}")
        
        # Custom content
        custom_content = character_data.get("custom_content", [])
        if custom_content:
            output.append(f"Custom Content: {', '.join(custom_content[:3])}")
        
        return "\n".join(output)
    
    def _display_detailed_backstory(self, character_data: Dict[str, Any]):
        """Display detailed backstory."""
        print("\n" + "="*60)
        print("DETAILED BACKSTORY")
        print("="*60)
        
        detailed_backstory = character_data.get("detailed_backstory", {})
        
        if detailed_backstory:
            main_backstory = detailed_backstory.get("main_backstory", "")
            if main_backstory:
                print(main_backstory)
                print()
            
            sections = [
                ("FAMILY HERITAGE", "family_history"),
                ("FORMATIVE EVENTS", "formative_events"),
                ("CURRENT MOTIVATIONS", "current_motivations"),
                ("SECRETS & FEARS", "secrets_and_fears")
            ]
            
            for title, key in sections:
                content = detailed_backstory.get(key, "")
                if content:
                    print(title)
                    print("-" * len(title))
                    print(content)
                    print()
        else:
            backstory = character_data.get("backstory", "No backstory available.")
            print(backstory)
        
        input("\nPress Enter to continue...")
    
    def _populate_character_from_data(self, character_data: Dict[str, Any]):
        """Populate character sheet from final character data."""
        
        self.character = CharacterSheet(character_data.get("name", "Unnamed"))
        
        # Basic info
        self.character.core.species = character_data.get("species", "Human")
        self.character.core.background = character_data.get("background", "")
        self.character.core.alignment = character_data.get("alignment", ["Neutral", "Neutral"])
        
        # Store detailed information
        species_details = character_data.get("species_details", {})
        if species_details:
            self.character.core.species_details = species_details
        
        class_details = character_data.get("class_details", {})
        if class_details:
            self.character.core.class_details = class_details
        
        armor_details = character_data.get("armor_details", {})
        if armor_details:
            self.character.core.armor_details = armor_details
        
        # Classes
        self.character.core.character_classes = character_data.get("classes", {"Fighter": 1})
        
        # Ability scores
        abilities = character_data.get("ability_scores", {})
        for ability, score in abilities.items():
            ability_obj = self.character.core.get_ability_score(ability)
            if ability_obj:
                ability_obj.base_score = score
        
        # Skills
        for skill in character_data.get("skill_proficiencies", []):
            self.character.core.skill_proficiencies[skill] = ProficiencyLevel.PROFICIENT
        
        # Personality
        self.character.core.personality_traits = character_data.get("personality_traits", [])
        self.character.core.ideals = character_data.get("ideals", [])
        self.character.core.bonds = character_data.get("bonds", [])
        self.character.core.flaws = character_data.get("flaws", [])
        
        # Backstory
        detailed_backstory = character_data.get("detailed_backstory", {})
        if detailed_backstory:
            self.character.core.set_detailed_backstory(detailed_backstory)
        else:
            self.character.core.backstory = character_data.get("backstory", "")
        
        # Custom content tracking
        self.character.core.custom_content_used = character_data.get("custom_content", [])
        
        # Equipment
        self.character.state.armor = character_data.get("armor", "")
        self.character.state.weapons = character_data.get("weapons", [])
        self.character.state.equipment = character_data.get("equipment", [])
        
        # Calculate derived stats
        self.character.calculate_all_derived_stats()
        
        # Override AC calculation if we have armor details
        if armor_details:
            character_data["ac"] = calculate_character_ac(character_data)
    
    def get_creation_stats(self) -> Dict[str, Any]:
        """Get statistics about the character creation process."""
        return self._creation_stats.copy()
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'async_generator'):
            self.async_generator.cleanup()

# Factory function update
def create_character_service(use_mock: bool = False) -> CharacterCreator:
    """Enhanced factory function with better error diagnosis."""
    
    print("🔧 Initializing character creation service...")
    
    # Check if Ollama is accessible
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            raise Exception(f"Ollama API returned status {response.status_code}")
        print("✅ Ollama API is accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama API at http://localhost:11434")
        print("\n💡 SOLUTION STEPS:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Pull a model: ollama pull llama3")
        print("3. Start service: ollama serve")
        print("4. Verify it's running: ollama list")
        raise Exception("Ollama service not accessible")
    except Exception as e:
        print(f"❌ Error checking Ollama API: {e}")
        raise Exception(f"Ollama API check failed: {e}")
    
    # Try to create LLM service
    max_connection_attempts = 3
    
    for attempt in range(max_connection_attempts):
        try:
            logger.info(f"Attempting to connect to Ollama (attempt {attempt + 1}/{max_connection_attempts})")
            print(f"🔄 Connection attempt {attempt + 1}/{max_connection_attempts}...")
            
            llm_service = OllamaLLMService()
            
            if llm_service.test_connection():
                logger.info("Ollama connection successful")
                print("✅ Ollama connection established")
                return CharacterCreator(llm_service)
            else:
                logger.warning(f"Ollama connection test failed on attempt {attempt + 1}")
                print(f"⚠️  Connection test failed (attempt {attempt + 1})")
                if attempt < max_connection_attempts - 1:
                    print("   Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Ollama connection test failed after all attempts")
                    
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt == max_connection_attempts - 1:
                print("\n💡 TROUBLESHOOTING:")
                print("- Make sure Ollama is installed and running")
                print("- Check if port 11434 is available")
                print("- Try: ollama serve")
                print("- Verify with: curl http://localhost:11434/api/tags")
                raise Exception(f"Failed to initialize Ollama service after {max_connection_attempts} attempts: {e}")
            time.sleep(2)

def check_ollama_setup() -> Dict[str, Any]:
    """Check Ollama setup and provide diagnostic information."""
    
    status = {
        "ollama_installed": False,
        "ollama_running": False,
        "models_available": [],
        "api_accessible": False,
        "issues": [],
        "solutions": []
    }
    
    # Check if ollama command exists
    try:
        import subprocess
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            status["ollama_installed"] = True
            print(f"✅ Ollama installed: {result.stdout.strip()}")
        else:
            status["issues"].append("Ollama command failed")
            status["solutions"].append("Reinstall Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    except FileNotFoundError:
        status["issues"].append("Ollama not installed")
        status["solutions"].append("Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    except Exception as e:
        status["issues"].append(f"Error checking Ollama installation: {e}")
    
    # Check if API is accessible
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            status["api_accessible"] = True
            status["ollama_running"] = True
            
            # Get available models
            models_data = response.json()
            status["models_available"] = [model.get("name", "unknown") for model in models_data.get("models", [])]
            print(f"✅ Ollama API accessible with {len(status['models_available'])} models")
            
            if not status["models_available"]:
                status["issues"].append("No models available")
                status["solutions"].append("Pull a model: ollama pull llama3")
                
        else:
            status["issues"].append(f"Ollama API returned status {response.status_code}")
            status["solutions"].append("Restart Ollama: ollama serve")
            
    except requests.exceptions.ConnectionError:
        status["issues"].append("Cannot connect to Ollama API")
        status["solutions"].append("Start Ollama service: ollama serve")
    except Exception as e:
        status["issues"].append(f"API check failed: {e}")
    
    return status

# Updated interactive creation function
def interactive_character_creation():
    """Enhanced interactive character creation with setup checking."""
    print("🎲 D&D Enhanced Character Creator 🎲")
    print("=" * 50)
    
    # Check Ollama setup first
    print("🔍 Checking Ollama setup...")
    setup_status = check_ollama_setup()
    
    if setup_status["issues"]:
        print("\n❌ SETUP ISSUES DETECTED:")
        for issue in setup_status["issues"]:
            print(f"  • {issue}")
        
        print("\n💡 RECOMMENDED SOLUTIONS:")
        for i, solution in enumerate(setup_status["solutions"], 1):
            print(f"  {i}. {solution}")
        
        # Ask if user wants to continue anyway
        if not input("\nTry to continue anyway? (y/n): ").lower().startswith('y'):
            return
    
    try:
        creator = create_character_service()
    except Exception as e:
        print(f"\n❌ Failed to initialize character creator: {e}")
        return
    
    print("✅ Character creation service ready")
    print()
    
    # Get user input
    print("Describe your character concept:")
    print("(Be as detailed as you like - mention personality, background, abilities, level, etc.)")
    description = input("> ")
    
    if not description.strip():
        print("No description provided. Using default...")
        description = "A brave adventurer seeking to make their mark on the world"
    
    # Determine level
    level = determine_level_from_description(description)
    print(f"📊 Determined character level: {level}")
    
    print(f"\n⏰ ESTIMATED TIME: 30-60 seconds total")
    print("- Character data: ~20 seconds")
    print("- Backstory: ~15 seconds") 
    print("- Custom content: ~30 seconds")
    print("\n" + "="*50)
    print("🎭 CREATING YOUR CHARACTER...")
    print("="*50)
    
    # Create character
    start_time = time.time()
    try:
        summary = creator.create_character_iteratively(description, level, generate_custom_content=True)
        end_time = time.time()
        
        print(f"\n⏱️  Total generation time: {end_time - start_time:.1f} seconds")
        
        # Show creation stats
        stats = creator.get_creation_stats()
        print(f"📊 Creation completed in {stats['iterations']} iterations")
        
        print("\n" + format_character_summary(summary))
        
        # Save options
        print("\n" + "="*30)
        print("SAVE OPTIONS")
        print("="*30)
        
        save_choice = input("Save character data? (y/n): ")
        if save_choice.lower().startswith('y'):
            filename = save_character(summary)
            print(f"✅ Character data saved: {filename}")
        
        backstory_choice = input("Save backstory as text file? (y/n): ")
        if backstory_choice.lower().startswith('y'):
            backstory_file = save_backstory_as_text(summary)
            print(f"✅ Backstory saved: {backstory_file}")
        
        sheet_choice = input("Export complete character sheet? (y/n): ")
        if sheet_choice.lower().startswith('y'):
            sheet_file = export_character_sheet(summary)
            print(f"✅ Character sheet exported: {sheet_file}")
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"Character creation failed after {end_time - start_time:.1f} seconds: {e}")
        print(f"❌ Character creation failed: {e}")
        print("💡 Try a simpler character description or check your Ollama connection")
##### end of character creator class

def create_character_service(use_mock: bool = False) -> CharacterCreator:
    """Factory function with enhanced error handling."""
    max_connection_attempts = 3
    
    for attempt in range(max_connection_attempts):
        try:
            logger.info(f"Attempting to connect to Ollama (attempt {attempt + 1}/{max_connection_attempts})")
            llm_service = OllamaLLMService()
            
            if llm_service.test_connection():
                logger.info("Ollama connection successful")
                return CharacterCreator(llm_service)
            else:
                logger.warning(f"Ollama connection test failed on attempt {attempt + 1}")
                if attempt < max_connection_attempts - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    raise Exception("Ollama connection test failed after all attempts")
                    
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt == max_connection_attempts - 1:
                raise Exception(f"Failed to initialize Ollama service after {max_connection_attempts} attempts: {e}")
            time.sleep(2)  # Wait before retry

def interactive_character_creation():
    """Interactive character creation with timeout feedback."""
    print("🎲 D&D Enhanced Character Creator 🎲")
    print("=" * 50)
    
    try:
        creator = create_character_service()
    except Exception as e:
        print(f"❌ Failed to initialize character creator: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return
    
    print("✅ Character creation service ready")
    print()
    
    # Get user input
    print("Describe your character concept:")
    print("(Be descriptive but concise for faster generation)")
    description = input("> ")
    
    if not description.strip():
        print("No description provided. Using default...")
        description = "A brave adventurer seeking to make their mark on the world"
    
    # Auto-determine level
    level = determine_level_from_description(description)
    print(f"📊 Determined character level: {level}")
    
    print(f"\n⏰ ESTIMATED TIME: 30-60 seconds total")
    print("- Character data: ~20 seconds")
    print("- Backstory: ~15 seconds") 
    print("- Custom content: ~30 seconds")
    print("\n" + "="*50)
    print("🎭 CREATING YOUR CHARACTER...")
    print("="*50)
    
    # Create character with timeout awareness
    start_time = time.time()
    try:
        summary = creator.create_character_iteratively(description, level, generate_custom_content=True)
        end_time = time.time()
        
        print(f"\n⏱️  Total generation time: {end_time - start_time:.1f} seconds")
        print("\n" + format_character_summary(summary))
        
        # Rest of the interactive creation process...
        # [Save options, validation, etc. - keep existing code]
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"Character creation failed after {end_time - start_time:.1f} seconds: {e}")
        print(f"❌ Character creation failed: {e}")
        print("💡 Try a simpler character description or check your Ollama connection")

# [Keeping all the existing utility functions from before - format_character_summary, save_character, etc.]

# ============================================================================
# ENHANCED UTILITY FUNCTIONS (Complete Implementation)
# ============================================================================
def check_armor_proficiency(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if character is proficient with their armor."""
    
    armor_details = character_data.get("armor_details", {})
    if not armor_details:
        return {"proficient": True, "penalties": []}
    
    armor_type = armor_details.get("armor_type", "Light")
    required_prof = armor_details.get("proficiency_required", f"{armor_type} armor")
    
    # Get character's class proficiencies (simplified)
    classes = character_data.get("classes", {})
    proficiencies = []
    
    for class_name in classes.keys():
        class_lower = class_name.lower()
        if class_lower in ["fighter", "paladin", "cleric"]:
            proficiencies.extend(["Light armor", "Medium armor", "Heavy armor", "Shields"])
        elif class_lower in ["barbarian", "ranger"]:
            proficiencies.extend(["Light armor", "Medium armor", "Shields"])
        elif class_lower in ["bard", "warlock"]:
            proficiencies.extend(["Light armor"])
        elif class_lower == "monk":
            # Monks can't wear armor
            pass
        else:
            # Default for other classes
            proficiencies.extend(["Light armor"])
    
    is_proficient = required_prof in proficiencies
    penalties = [] if is_proficient else [
        "Disadvantage on Strength and Dexterity checks and saves",
        "Disadvantage on attack rolls", 
        "Cannot cast spells"
    ]
    
    return {
        "proficient": is_proficient,
        "penalties": penalties,
        "required_proficiency": required_prof,
        "character_proficiencies": proficiencies
    }

def calculate_character_ac(character_data: Dict[str, Any]) -> int:
    """Calculate character's AC including armor, dex modifier, and magical bonuses."""
    
    # Get ability scores
    abilities = character_data.get("ability_scores", {})
    dex_mod = ((abilities.get("dexterity", 10) - 10) // 2)
    
    # Get armor details
    armor_details = character_data.get("armor_details", {})
    if not armor_details:
        # No detailed armor data, use basic calculation
        return 10 + dex_mod
    
    ac_base = armor_details.get("ac_base", 10)
    dex_bonus_type = armor_details.get("dex_bonus_type", "full")
    magical_bonus = armor_details.get("magical_bonus", 0)
    
    # Calculate based on armor type
    if dex_bonus_type == "full":
        final_ac = ac_base + dex_mod + magical_bonus
    elif dex_bonus_type == "max_2":
        final_ac = ac_base + min(dex_mod, 2) + magical_bonus
    elif dex_bonus_type == "none":
        final_ac = ac_base + magical_bonus
    else:
        final_ac = ac_base + magical_bonus
    
    # Add shield bonus if present
    # (You'd need to check for shields in equipment)
    
    return final_ac

def format_ability_scores_detailed(character_data: Dict[str, Any]) -> str:
    """Format detailed ability scores showing all sources of bonuses."""
    
    output = []
    output.append("ABILITY SCORES (DETAILED)")
    output.append("=" * 26)
    
    ability_scores = character_data.get("ability_scores", {})
    ability_details = character_data.get("ability_score_details", {})
    
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = ability_scores.get(ability, 10)
        modifier = (score - 10) // 2
        mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
        
        output.append(f"{ability.capitalize():12} {score:2} ({mod_str})")
        
        # Show breakdown if available
        if ability in ability_details:
            details = ability_details[ability]
            base = details.get("base", 10)
            asi_total = details.get("asi_improvements", 0)
            feat_total = details.get("feat_improvements", 0)
            magic_total = details.get("magic_item_bonuses", 0)
            
            breakdown = [f"Base: {base}"]
            if asi_total > 0:
                breakdown.append(f"ASI: +{asi_total}")
            if feat_total > 0:
                breakdown.append(f"Feat: +{feat_total}")
            if magic_total > 0:
                breakdown.append(f"Magic: +{magic_total}")
            
            if len(breakdown) > 1:
                output.append(f"             ({', '.join(breakdown)})")
        
        # Show improvement history if available
        history = ability_details.get(ability, {}).get("history", [])
        if history:
            output.append(f"             Improvements:")
            for improvement in history[-3:]:  # Show last 3 improvements
                source = improvement.get("source", "unknown")
                amount = improvement.get("amount", 0)
                level = improvement.get("level_gained", 0)
                desc = improvement.get("description", "")
                
                if level > 0:
                    output.append(f"               Level {level}: +{amount} ({desc})")
                else:
                    output.append(f"               +{amount} ({desc})")
    
    output.append("")
    return "\n".join(output)

def format_asi_progression(character_data: Dict[str, Any]) -> str:
    """Format ASI progression and opportunities."""
    
    output = []
    output.append("ABILITY SCORE IMPROVEMENTS")
    output.append("=" * 26)
    
    level = character_data.get("level", 1)
    classes = character_data.get("classes", {})
    asi_info = character_data.get("asi_info", {})
    
    if not asi_info:
        output.append("No ASI information available")
        return "\n".join(output)
    
    output.append(f"Total Available: {asi_info.get('total_available', 0)}")
    output.append(f"Used: {asi_info.get('total_used', 0)}")
    output.append(f"Remaining: {asi_info.get('remaining', 0)}")
    output.append("")
    
    # Show ASI progression
    asis = asi_info.get("asis", [])
    if asis:
        output.append("ASI PROGRESSION")
        output.append("-" * 15)
        
        for asi in asis:
            class_name = asi["class"]
            class_level = asi["class_level"]
            char_level = asi["character_level"]
            used = asi["used"]
            
            status = "✓" if used else "○"
            output.append(f"{status} Level {char_level} ({class_name} {class_level})")
            
            if used and "improvement" in asi:
                imp = asi["improvement"]
                improvements = imp.get("improvements", {})
                imp_str = ", ".join([f"{ability} +{bonus}" for ability, bonus in improvements.items()])
                output.append(f"    Applied: {imp_str}")
    
    output.append("")
    return "\n".join(output)

def format_multiclass_progression(character_data: Dict[str, Any]) -> str:
    """Format multiclass progression details."""
    
    classes = character_data.get("classes", {})
    if len(classes) <= 1:
        return ""
    
    output = []
    output.append("MULTICLASS PROGRESSION")
    output.append("=" * 21)
    
    total_level = sum(classes.values())
    output.append(f"Total Character Level: {total_level}")
    output.append("")
    
    output.append("CLASS LEVELS")
    output.append("-" * 12)
    for class_name, class_level in classes.items():
        percentage = (class_level / total_level) * 100
        output.append(f"{class_name:12} {class_level:2} ({percentage:4.1f}%)")
    
    output.append("")
    
    # Show level history if available
    level_history = character_data.get("level_history", [])
    if level_history:
        output.append("LEVEL-UP HISTORY")
        output.append("-" * 15)
        
        for i, record in enumerate(level_history[-5:], 1):  # Show last 5 level-ups
            class_name = record.get("class", "Unknown")
            new_level = record.get("new_class_level", 0)
            total_at_time = record.get("total_character_level", 0)
            
            output.append(f"{total_at_time:2}. {class_name} level {new_level}")
            
            if record.get("grants_asi"):
                if "asi_used" in record:
                    asi = record["asi_used"]
                    improvements = asi.get("improvements", {})
                    imp_str = ", ".join([f"{ability} +{bonus}" for ability, bonus in improvements.items()])
                    output.append(f"     ASI: {imp_str}")
                elif "feat_chosen" in record:
                    output.append(f"     Feat: {record['feat_chosen']}")
                elif record.get("asi_pending"):
                    output.append(f"     ASI: Pending choice")
    
    output.append("")
    return "\n".join(output)

def enhanced_format_character_summary(character_data: Dict[str, Any]) -> str:
    """Enhanced character summary with detailed ability score progression."""
    
    # Enhance the data first
    character_data = enhance_character_data_with_ability_details(character_data)
    
    # Use existing format_character_summary as base
    output = format_character_summary(character_data).split('\n')
    
    # Find where ability scores section ends and insert enhanced details
    ability_section_end = -1
    for i, line in enumerate(output):
        if line.startswith("COMBAT STATISTICS"):
            ability_section_end = i
            break
    
    if ability_section_end > 0:
        # Insert enhanced ability score details
        enhanced_abilities = format_ability_scores_detailed(character_data).split('\n')
        
        # Replace the basic ability scores with enhanced version
        ability_start = -1
        for i in range(ability_section_end):
            if "ABILITY SCORES" in output[i]:
                ability_start = i
                break
        
        if ability_start >= 0:
            # Remove old ability section
            while ability_start < len(output) and not output[ability_start].startswith("COMBAT"):
                output.pop(ability_start)
            
            # Insert enhanced section
            for line in reversed(enhanced_abilities):
                output.insert(ability_start, line)
    
    # Add ASI progression section
    asi_section = format_asi_progression(character_data)
    if asi_section.strip():
        # Insert after combat statistics
        combat_end = -1
        for i, line in enumerate(output):
            if line.startswith("PROFICIENT SKILLS") or line.startswith("EQUIPMENT"):
                combat_end = i
                break
        
        if combat_end > 0:
            asi_lines = asi_section.split('\n')
            for line in reversed(asi_lines):
                output.insert(combat_end, line)
    
    # Add multiclass progression if applicable
    multiclass_section = format_multiclass_progression(character_data)
    if multiclass_section.strip():
        output.extend(['', multiclass_section])
    
    return '\n'.join(output)

# Example usage functions
def example_character_leveling():
    """Example of how to use the enhanced ability score system."""
    
    # Create a character
    character = CharacterCore("Thorin Ironforge")
    
    # Set starting ability scores
    character.apply_starting_ability_scores({
        "strength": 15,
        "dexterity": 10,
        "constitution": 14,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 8
    })
    
    # Add starting class
    character.character_classes["Fighter"] = 1
    
    # Level up to 4 and take ASI
    character.level_up("Fighter", {
        "type": "asi",
        "improvements": {"strength": 2}
    })
    character.character_classes["Fighter"] = 4
    
    # Level up to 6 (Fighter gets extra ASI)
    character.level_up("Fighter", {
        "type": "feat",
        "feat_name": "Great Weapon Master",
        "ability_bonuses": {"strength": 1}  # If it's a half-feat
    })
    character.character_classes["Fighter"] = 6
    
    # Add magic item
    character.magic_item_manager.add_magic_item(
        "Belt of Giant Strength",
        ability_bonuses={},
        sets_score={"strength": 21}
    )
    
    # Multiclass into Rogue
    character.character_classes["Rogue"] = 1
    
    # Show progression
    progression = character.level_manager.get_level_progression_summary()
    print("Character Progression:")
    print(f"Total Level: {progression['total_level']}")
    print(f"Classes: {progression['class_levels']}")
    print(f"Available ASIs: {progression['asi_info']['total_available']}")
    print(f"Used ASIs: {progression['asi_info']['total_used']}")
    
    # Show ability scores
    print(f"\nStrength: {character.strength.total_score} (modifier: {character.strength.modifier})")
    print("Strength history:", character.strength.get_improvement_history())

def create_leveling_interface():
    """Create an interface for leveling up characters."""
    
    def level_up_character(character_data: Dict[str, Any], 
                          class_name: str, 
                          asi_choice: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Level up a character and return updated data."""
        
        # This would integrate with your existing character system
        # For now, simulate the level-up process
        
        classes = character_data.get("classes", {})
        current_level = classes.get(class_name, 0)
        new_level = current_level + 1
        
        # Update class level
        classes[class_name] = new_level
        character_data["classes"] = classes
        character_data["level"] = sum(classes.values())
        
        # Handle ASI if provided
        if asi_choice:
            asi_manager = ASIManager()
            asi_levels = asi_manager.get_asi_levels_for_class(class_name)
            
            if new_level in asi_levels:
                # Apply the ASI choice
                if asi_choice["type"] == "asi":
                    # Update ability scores
                    ability_scores = character_data.get("ability_scores", {})
                    for ability, improvement in asi_choice["improvements"].items():
                        if ability in ability_scores:
                            ability_scores[ability] += improvement
                    character_data["ability_scores"] = ability_scores
                
                # Record the choice
                if "level_history" not in character_data:
                    character_data["level_history"] = []
                
                character_data["level_history"].append({
                    "class": class_name,
                    "new_class_level": new_level,
                    "total_character_level": character_data["level"],
                    "asi_choice": asi_choice
                })
        
        # Enhance with detailed ability information
        character_data = enhance_character_data_with_ability_details(character_data)
        
        return character_data
    
    return level_up_character

def format_feat_opportunities(character_data: Dict[str, Any]) -> str:
    """Format feat opportunities for the character summary."""
    
    level = character_data.get("level", 1)
    classes = character_data.get("classes", {})
    
    output = []
    output.append("FEAT OPPORTUNITIES")
    output.append("-" * 18)
    
    # Calculate total feat opportunities
    opportunities = []
    
    # Origin feat at level 1 (2024 rule)
    if level >= 1:
        opportunities.append("Level 1 (Origin Feat)")
    
    # ASI levels that can be feats
    asi_levels = set()
    for class_name, class_level in classes.items():
        class_lower = class_name.lower()
        
        # Standard ASI levels
        standard = [4, 8, 12, 16, 19]
        
        # Additional ASI levels for specific classes
        if class_lower == "fighter":
            standard.extend([6, 14])
        elif class_lower == "rogue":
            standard.append(10)
        
        for asi_level in standard:
            if class_level >= asi_level:
                asi_levels.add(asi_level)
    
    for asi_level in sorted(asi_levels):
        if asi_level <= level:
            opportunities.append(f"Level {asi_level} (ASI or Feat)")
    
    if opportunities:
        output.append(f"Available opportunities: {len(opportunities)}")
        for opportunity in opportunities:
            output.append(f"  • {opportunity}")
    else:
        output.append("No feat opportunities yet")
    
    output.append("")
    return "\n".join(output)

def format_armor_details(armor_data: Dict[str, Any]) -> str:
    """Format armor details for display according to D&D 5e rules."""
    
    if not armor_data:
        return ""
    
    output = []
    
    # Handle both dict and CustomArmor object
    if hasattr(armor_data, 'name'):
        # CustomArmor object
        a = armor_data
        name = a.name
        armor_type = a.armor_type
        ac_base = a.ac_base
        dex_bonus = a._format_dex_bonus()
        str_req = a.strength_requirement
        stealth_penalty = a.stealth_disadvantage
        don_time = a.don_time
        doff_time = a.doff_time
        cost = a.cost
        weight = a.weight
        magical = a.magical
        magical_bonus = a.magical_bonus
        special_abilities = a.special_abilities
        damage_resistances = a.damage_resistances
        proficiency = a.proficiency_required
        description = a.description
    else:
        # Dictionary
        name = armor_data.get("name", "Unknown Armor")
        armor_type = armor_data.get("armor_type", armor_data.get("type", "Medium"))
        ac_base = armor_data.get("ac_base", armor_data.get("ac", 12))
        dex_bonus = armor_data.get("dex_bonus", "Dex modifier")
        str_req = armor_data.get("strength_requirement", 0)
        stealth_penalty = armor_data.get("stealth_disadvantage", False)
        don_time = armor_data.get("don_time", 5)
        doff_time = armor_data.get("doff_time", 1)
        cost = armor_data.get("cost", "")
        weight = armor_data.get("weight", "")
        magical = armor_data.get("magical", False)
        magical_bonus = armor_data.get("magical_bonus", 0)
        special_abilities = armor_data.get("special_abilities", [])
        damage_resistances = armor_data.get("damage_resistances", [])
        proficiency = armor_data.get("proficiency_required", f"{armor_type} armor")
        description = armor_data.get("description", "")
    
    # Format armor header
    output.append(f"🛡️  ARMOR: {name.upper()}")
    if magical and magical_bonus > 0:
        output.append(f"   Magical: +{magical_bonus} {armor_type} Armor")
    else:
        output.append(f"   Type: {armor_type} Armor")
    
    # Core stats
    if armor_type == "Shield":
        output.append(f"   AC Bonus: +{ac_base}")
    else:
        if dex_bonus == "—":
            output.append(f"   Armor Class: {ac_base}")
        else:
            output.append(f"   Armor Class: {ac_base} + {dex_bonus}")
    
    # Requirements and penalties
    requirements = []
    if str_req > 0:
        requirements.append(f"Str {str_req}")
    if stealth_penalty:
        requirements.append("Stealth disadvantage")
    if requirements:
        output.append(f"   Requirements: {', '.join(requirements)}")
    
    # Proficiency required
    output.append(f"   Proficiency: {proficiency}")
    
    # Don/Doff times
    if armor_type != "Shield":
        if don_time == doff_time:
            output.append(f"   Don/Doff Time: {don_time} minute{'s' if don_time != 1 else ''}")
        else:
            output.append(f"   Don Time: {don_time} minute{'s' if don_time != 1 else ''}")
            output.append(f"   Doff Time: {doff_time} minute{'s' if doff_time != 1 else ''}")
    else:
        output.append(f"   Equip/Unequip: 1 action")
    
    # Cost and weight
    if cost or weight:
        details = []
        if cost:
            details.append(f"Cost: {cost}")
        if weight:
            details.append(f"Weight: {weight}")
        output.append(f"   {', '.join(details)}")
    
    # Damage resistances
    if damage_resistances:
        output.append(f"   Resistances: {', '.join(damage_resistances)}")
    
    # Special abilities
    if special_abilities:
        output.append(f"   Special: {', '.join(special_abilities)}")
    
    # Description
    if description:
        output.append(f"   Description: {description}")
    
    # Penalties without proficiency
    if armor_type != "Shield":
        output.append(f"   Without Proficiency: Disadvantage on ability checks, saves, attacks; no spellcasting")
    
    output.append("")
    return "\n".join(output)

def format_rest_mechanics_summary(character_data: Dict[str, Any]) -> str:
    """Format a summary of the character's rest mechanics for quick reference."""
    
    species_data = character_data.get("species_details", {})
    sleep_mechanics = species_data.get("sleep_mechanics", {})
    
    if not sleep_mechanics or sleep_mechanics.get("needs_sleep", True):
        return "Rest: Requires 8 hours of sleep for long rest"
    
    sleep_type = sleep_mechanics.get("sleep_type", "normal")
    duration = sleep_mechanics.get("rest_duration", 8)
    state = sleep_mechanics.get("rest_state", "unconscious")
    
    if sleep_type == "trance":
        return f"Rest: Meditates for {duration} hours ({state}) - Immune to magical sleep"
    elif sleep_type == "inactive_state":
        return f"Rest: Inactive state for {duration} hours ({state}) - No sleep needed"
    elif sleep_type == "none":
        return f"Rest: No sleep, but {duration} hours needed for ability recovery"
    
    return f"Rest: {duration} hours in {sleep_type} state"

def format_weapon_details(weapon_data: Dict[str, Any]) -> str:
    """Format weapon details for display according to 2024 rules."""
    
    if not weapon_data:
        return ""
    
    output = []
    
    # Handle both dict and CustomWeapon object
    if hasattr(weapon_data, 'name'):
        # CustomWeapon object
        w = weapon_data
        name = w.name
        category = w.category
        weapon_type = w.weapon_type
        damage = w.damage_dice
        damage_type = w.damage_type
        properties = w.properties
        mastery = w.mastery_property
        range_str = w.get_range_string()
        versatile = w.versatile_damage
        cost = w.cost
        weight = w.weight
        magical = w.magical
        magical_bonus = w.magical_bonus
        special_abilities = w.special_abilities
        description = w.description
    else:
        # Dictionary
        name = weapon_data.get("name", "Unknown Weapon")
        category = weapon_data.get("category", "Simple")
        weapon_type = weapon_data.get("weapon_type", "Melee")
        damage = weapon_data.get("damage_dice", weapon_data.get("damage", "1d4"))
        damage_type = weapon_data.get("damage_type", "bludgeoning")
        properties = weapon_data.get("properties", [])
        mastery = weapon_data.get("mastery_property", "")
        range_str = weapon_data.get("range", "—")
        versatile = weapon_data.get("versatile_damage", "")
        cost = weapon_data.get("cost", "")
        weight = weapon_data.get("weight", "")
        magical = weapon_data.get("magical", False)
        magical_bonus = weapon_data.get("magical_bonus", 0)
        special_abilities = weapon_data.get("special_abilities", [])
        description = weapon_data.get("description", "")
    
    # Format weapon header
    output.append(f"⚔️  WEAPON: {name.upper()}")
    if magical and magical_bonus > 0:
        output.append(f"   Magical: +{magical_bonus} {category} {weapon_type}")
    else:
        output.append(f"   Type: {category} {weapon_type}")
    
    # Core stats
    output.append(f"   Damage: {damage} {damage_type}")
    if versatile:
        output.append(f"   Versatile: {versatile} {damage_type} (two-handed)")
    
    # Range (if applicable)
    if range_str != "—":
        output.append(f"   Range: {range_str}")
    
    # Properties
    if properties:
        prop_str = ", ".join(properties)
        output.append(f"   Properties: {prop_str}")
    
    # NEW: Mastery property
    if mastery:
        mastery_desc = get_mastery_description(mastery)
        output.append(f"   Mastery: {mastery} - {mastery_desc}")
    
    # Cost and weight
    if cost or weight:
        details = []
        if cost:
            details.append(f"Cost: {cost}")
        if weight:
            details.append(f"Weight: {weight}")
        output.append(f"   {', '.join(details)}")
    
    # Special abilities
    if special_abilities:
        output.append(f"   Special: {', '.join(special_abilities)}")
    
    # Description
    if description:
        output.append(f"   Description: {description}")
    
    output.append("")
    return "\n".join(output)

def get_mastery_description(mastery_property: str) -> str:
    """Get description of weapon mastery property."""
    mastery_descriptions = {
        "cleave": "Hit adjacent enemy when you kill a creature",
        "graze": "Deal damage equal to ability modifier even on miss",
        "nick": "Make extra attack with light weapon in off-hand",
        "push": "Move target 10 feet away on hit",
        "sap": "Reduce target's next damage roll by proficiency bonus",
        "slow": "Reduce target's speed by 10 feet until start of next turn",
        "topple": "Force prone on critical hit if target is Large or smaller",
        "vex": "Next attack against target has advantage"
    }
    
    return mastery_descriptions.get(mastery_property.lower(), "Unknown mastery property")

def format_equipment_section(character_data: Dict[str, Any]) -> str:
    """Format equipment section with enhanced armor and weapon details."""
    
    output = []
    output.append("EQUIPMENT & WEAPONS")
    output.append("=" * 19)
    
    # Enhanced Armor Display
    armor = character_data.get("armor", "None")
    if armor != "None":
        # Check if we have detailed armor data
        armor_details = character_data.get("armor_details", {})
        if armor_details:
            armor_display = format_armor_details(armor_details)
            output.append(armor_display)
        else:
            # Simple armor display
            output.append(f"🛡️  ARMOR: {armor}")
            output.append("")
    
    # Weapons with full details (already implemented)
    weapons = character_data.get("weapons", [])
    if weapons:
        for weapon in weapons:
            weapon_details = format_weapon_details(weapon)
            output.append(weapon_details)
    
    # Other equipment
    equipment = character_data.get("equipment", [])
    if equipment:
        output.append("OTHER EQUIPMENT")
        output.append("-" * 15)
        for item in equipment:
            if isinstance(item, dict):
                name = item.get("name", "Unknown Item")
                qty = item.get("quantity", 1)
                desc = item.get("description", "")
                qty_str = f" (x{qty})" if qty > 1 else ""
                desc_str = f" - {desc}" if desc else ""
                output.append(f"• {name}{qty_str}{desc_str}")
            else:
                output.append(f"• {item}")
        output.append("")
    
    return "\n".join(output)

def format_class_features(character_data: Dict[str, Any], character_level: int) -> str:
    """Format class features for display according to 2024 rules."""
    
    classes = character_data.get("classes", {})
    output = []
    
    for class_name, class_level in classes.items():
        output.append(f"CLASS: {class_name.upper()}")
        output.append("=" * (len(class_name) + 7))
        
        # If we have detailed class data, show it
        class_data = character_data.get("class_details", {}).get(class_name, {})
        if class_data:
            # Basic class info
            hit_die = class_data.get("hit_die", 8)
            primary_abilities = class_data.get("primary_abilities", [])
            saving_throws = class_data.get("saving_throws", [])
            problem_solving = class_data.get("problem_solving_style", "")
            role = class_data.get("role_description", "")
            
            output.append(f"Hit Die: d{hit_die}")
            output.append(f"Primary Abilities: {', '.join(primary_abilities).title()}")
            output.append(f"Saving Throws: {', '.join(saving_throws).title()}")
            if problem_solving:
                output.append(f"Problem Solving: {problem_solving.title()}")
            if role:
                output.append(f"Role: {role.title()}")
            output.append("")
            
            # Class features by level
            level_features = class_data.get("level_features", {})
            current_features = []
            
            for level in range(1, class_level + 1):
                if str(level) in level_features:
                    for feature in level_features[str(level)]:
                        current_features.append((level, feature))
            
            if current_features:
                output.append("CLASS FEATURES")
                output.append("-" * 14)
                
                for level, feature in current_features:
                    name = feature.get("name", "Unknown Feature")
                    desc = feature.get("description", "")
                    feature_type = feature.get("type", "feature")
                    
                    if feature_type == "asi":
                        output.append(f"• {name} (Level {level})")
                    else:
                        output.append(f"• {name} (Level {level}): {desc}")
                output.append("")
            
            # Spellcasting info
            spellcasting_ability = class_data.get("spellcasting_ability", "")
            if spellcasting_ability:
                output.append("SPELLCASTING")
                output.append("-" * 12)
                output.append(f"Spellcasting Ability: {spellcasting_ability.title()}")
                
                # Show spell slots if we have the progression
                spell_progression = class_data.get("spell_progression", {})
                if str(class_level) in spell_progression:
                    slots = spell_progression[str(class_level)]
                    slot_display = []
                    for i, slot_count in enumerate(slots):
                        if slot_count > 0:
                            level_name = "Cantrips" if i == 0 else f"Level {i}"
                            slot_display.append(f"{level_name}: {slot_count}")
                    if slot_display:
                        output.append(f"Spell Slots: {', '.join(slot_display)}")
                output.append("")
            
            # Class resource
            resource_name = class_data.get("resource_name", "")
            if resource_name:
                resource_progression = class_data.get("resource_progression", {})
                resource_amount = resource_progression.get(str(class_level), 0)
                resource_recovery = class_data.get("resource_recovery", "long_rest")
                
                output.append("CLASS RESOURCE")
                output.append("-" * 14)
                output.append(f"{resource_name}: {resource_amount}")
                output.append(f"Recovery: {resource_recovery.replace('_', ' ').title()}")
                output.append("")
        
        output.append("")
    
    return "\n".join(output)


def format_species_features(character_data: Dict[str, Any], character_level: int) -> str:
    """Format species features for display according to 2024 rules including sleep mechanics."""
    
    species_name = character_data.get("species", "Unknown")
    output = []
    
    output.append(f"SPECIES: {species_name.upper()}")
    output.append("=" * (len(species_name) + 9))
    
    # If we have detailed species data, show it
    species_data = character_data.get("species_details", {})
    if species_data:
        # Basic info
        creature_type = species_data.get("creature_type", "Humanoid")
        size = species_data.get("size", "Medium")
        speed = species_data.get("speed", 30)
        
        output.append(f"Type: {creature_type}")
        output.append(f"Size: {size}")
        output.append(f"Speed: {speed} feet")
        
        # Movement types
        movement = species_data.get("movement_types", {})
        if len(movement) > 1:
            move_strs = [f"{move_type} {speed} ft." for move_type, speed in movement.items()]
            output.append(f"Movement: {', '.join(move_strs)}")
        
        # Senses
        darkvision = species_data.get("darkvision", 0)
        if darkvision > 0:
            output.append(f"Darkvision: {darkvision} feet")
        
        special_senses = species_data.get("special_senses", [])
        if special_senses:
            output.append(f"Special Senses: {', '.join(special_senses)}")
        
        # Resistances and immunities
        resistances = species_data.get("damage_resistances", [])
        if resistances:
            output.append(f"Damage Resistances: {', '.join(resistances)}")
        
        immunities = species_data.get("damage_immunities", [])
        if immunities:
            output.append(f"Damage Immunities: {', '.join(immunities)}")
        
        condition_immunities = species_data.get("condition_immunities", [])
        if condition_immunities:
            output.append(f"Condition Immunities: {', '.join(condition_immunities)}")
        
        # Languages
        languages = species_data.get("languages", ["Common"])
        output.append(f"Languages: {', '.join(languages)}")
        
        # NEW: Sleep and Rest Mechanics
        sleep_mechanics = species_data.get("sleep_mechanics", {})
        if sleep_mechanics and not sleep_mechanics.get("needs_sleep", True):
            output.append("")
            output.append("SLEEP & REST")
            output.append("-" * 12)
            
            sleep_type = sleep_mechanics.get("sleep_type", "normal")
            rest_duration = sleep_mechanics.get("rest_duration", 8)
            rest_state = sleep_mechanics.get("rest_state", "unconscious")
            
            if sleep_type == "trance":
                output.append(f"Trance: Does not sleep, meditates for {rest_duration} hours")
                output.append(f"Consciousness: Remains {rest_state} during rest")
            elif sleep_type == "inactive_state":
                output.append(f"Inactive Rest: Remains motionless for {rest_duration} hours")
                output.append(f"Consciousness: Stays {rest_state} and aware")
            elif sleep_type == "none":
                output.append("No Sleep: Does not require sleep")
                output.append(f"Long Rest: Still needs {rest_duration} hours for recovery")
            
            if sleep_mechanics.get("sleep_immunity", False):
                output.append("Sleep Immunity: Cannot be magically forced to sleep")
            
            if sleep_mechanics.get("charm_resistance", False):
                output.append("Charm Resistance: Advantage on saves against charm effects")
            elif sleep_mechanics.get("charm_immunity", False):
                output.append("Charm Immunity: Immune to charm effects")
            
            special_rules = sleep_mechanics.get("special_rest_rules", [])
            if special_rules:
                for rule in special_rules:
                    output.append(f"• {rule}")
        
        output.append("")
        
        # Innate traits
        innate_traits = species_data.get("innate_traits", [])
        if innate_traits:
            output.append("INNATE TRAITS")
            output.append("-" * 13)
            for trait in innate_traits:
                output.append(f"• {trait}")
            output.append("")
        
        # Level-based features
        level_features = species_data.get("level_features", {})
        current_features = []
        for level in range(1, character_level + 1):
            if str(level) in level_features:
                for feature in level_features[str(level)]:
                    current_features.append((level, feature))
        
        if current_features:
            output.append("SPECIES FEATURES")
            output.append("-" * 15)
            for level, feature in current_features:
                name = feature.get("name", "Unknown Feature")
                desc = feature.get("description", "")
                output.append(f"• {name} (Level {level}): {desc}")
            output.append("")
        
        # Innate spellcasting
        spellcasting = species_data.get("innate_spellcasting", {})
        current_spells = {}
        for level in range(1, character_level + 1):
            if str(level) in spellcasting:
                for spell_level, spells in spellcasting[str(level)].items():
                    if spell_level not in current_spells:
                        current_spells[spell_level] = []
                    current_spells[spell_level].extend(spells)
        
        if current_spells:
            ability = species_data.get("spellcasting_ability", "charisma")
            output.append("INNATE SPELLCASTING")
            output.append("-" * 18)
            output.append(f"Spellcasting Ability: {ability.capitalize()}")
            
            for spell_level in sorted(current_spells.keys()):
                level_name = "Cantrips" if spell_level == "0" else f"Level {spell_level}"
                spells = current_spells[spell_level]
                output.append(f"{level_name}: {', '.join(spells)}")
            output.append("")
        
        # Scaling features
        scaling = species_data.get("scaling_features", {})
        if scaling:
            output.append("SCALING FEATURES")
            output.append("-" * 16)
            for feature_name, scaling_desc in scaling.items():
                output.append(f"• {feature_name.replace('_', ' ').title()}: {scaling_desc}")
            output.append("")
    
    return "\n".join(output)

def format_character_summary(character_data: Dict[str, Any]) -> str:
    """Format character data into readable text with enhanced backstory, species, class, weapon, and rest features."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("CHARACTER SUMMARY")
    output.append("=" * 60)
    
    # Basic Info
    output.append(f"Name: {character_data.get('name', 'Unknown')}")
    output.append(f"Species: {character_data.get('species', 'Unknown')}")
    output.append(f"Level: {character_data.get('level', 1)}")
    
    classes = character_data.get('classes', {})
    class_str = ", ".join([f"{cls} {lvl}" for cls, lvl in classes.items()])
    output.append(f"Classes: {class_str}")
    output.append(f"Background: {character_data.get('background', 'Unknown')}")
    
    alignment = character_data.get('alignment', ['Unknown', 'Unknown'])
    output.append(f"Alignment: {alignment[0]} {alignment[1]}")
    output.append("")
    
    # Species Features (2024 rules including sleep mechanics)
    character_level = character_data.get('level', 1)
    species_section = format_species_features(character_data, character_level)
    if species_section:
        output.append(species_section)
    
    # Class Features (2024 rules)
    class_section = format_class_features(character_data, character_level)
    if class_section:
        output.append(class_section)
    
    # Ability Scores
    output.append("ABILITY SCORES")
    output.append("-" * 20)
    abilities = character_data.get("ability_scores", {})
    modifiers = character_data.get("ability_modifiers", {})
    
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = abilities.get(ability, 10)
        mod = modifiers.get(ability, 0)
        mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
        output.append(f"{ability.capitalize():12} {score:2} ({mod_str})")
    output.append("")
    
    # Combat Stats (including rest mechanics)
    output.append("COMBAT STATISTICS")
    output.append("-" * 20)
    output.append(f"Armor Class: {character_data.get('ac', 10)}")
    hp = character_data.get('hp', {})
    output.append(f"Hit Points: {hp.get('current', 0)}/{hp.get('max', 0)}")
    if hp.get('temp', 0) > 0:
        output.append(f"Temporary HP: {hp.get('temp', 0)}")
    output.append(f"Proficiency Bonus: +{character_data.get('proficiency_bonus', 2)}")
    
    # NEW: Add rest mechanics to combat stats
    rest_summary = format_rest_mechanics_summary(character_data)
    output.append(rest_summary)
    output.append("")
    
    # Skills
    skills = character_data.get("proficient_skills", [])
    if skills:
        output.append("PROFICIENT SKILLS")
        output.append("-" * 20)
        for skill in sorted(skills):
            output.append(f"• {skill}")
        output.append("")
    
    # Feat Opportunities
        # Add feat section after skills
    skills_section_index = output.index("") + 1  # Find where to insert
    
    # Insert feat opportunities
    feat_section = format_feat_opportunities(character_data)
    output.insert(skills_section_index, feat_section)
    
    # Enhanced Equipment Section (NEW with 2024 weapon details)
    equipment_section = format_equipment_section(character_data)
    if equipment_section:
        output.append(equipment_section)
    
    # Personality
    output.append("PERSONALITY")
    output.append("-" * 20)
    
    traits = character_data.get("personality_traits", [])
    if traits:
        output.append("Personality Traits:")
        for trait in traits:
            output.append(f"  • {trait}")
    
    ideals = character_data.get("ideals", [])
    if ideals:
        output.append("Ideals:")
        for ideal in ideals:
            output.append(f"  • {ideal}")
    
    bonds = character_data.get("bonds", [])
    if bonds:
        output.append("Bonds:")
        for bond in bonds:
            output.append(f"  • {bond}")
    
    flaws = character_data.get("flaws", [])
    if flaws:
        output.append("Flaws:")
        for flaw in flaws:
            output.append(f"  • {flaw}")
    output.append("")
    
    # Enhanced Backstory
    detailed_backstory = character_data.get("detailed_backstory", {})
    if detailed_backstory:
        output.append("DETAILED BACKSTORY")
        output.append("=" * 20)
        
        main_backstory = detailed_backstory.get("main_backstory", "")
        if main_backstory:
            output.append(main_backstory)
            output.append("")
        
        family_history = detailed_backstory.get("family_history", "")
        if family_history:
            output.append("FAMILY HISTORY")
            output.append("-" * 15)
            output.append(family_history)
            output.append("")
        
        formative_events = detailed_backstory.get("formative_events", "")
        if formative_events:
            output.append("FORMATIVE EVENTS")
            output.append("-" * 17)
            output.append(formative_events)
            output.append("")
        
        motivations = detailed_backstory.get("current_motivations", "")
        if motivations:
            output.append("CURRENT MOTIVATIONS")
            output.append("-" * 19)
            output.append(motivations)
            output.append("")
        
        secrets = detailed_backstory.get("secrets_and_fears", "")
        if secrets:
            output.append("SECRETS & FEARS")
            output.append("-" * 15)
            output.append(secrets)
            output.append("")
    
    else:
        # Fallback to basic backstory
        backstory = character_data.get("backstory", "")
        if backstory:
            output.append("BACKSTORY")
            output.append("-" * 10)
            output.append(backstory)
            output.append("")
    
    # Custom Content
    custom_content = character_data.get("custom_content", [])
    if custom_content:
        output.append("CUSTOM CONTENT CREATED")
        output.append("-" * 23)
        output.append("This character features unique, custom-created content:")
        for content in custom_content:
            output.append(f"  • {content}")
        output.append("")
    
    output.append("=" * 60)
    return "\n".join(output)

####
def format_custom_content_section(character_data: Dict[str, Any]) -> str:
    """Format custom content section with detailed D&D attributes."""
    
    custom_content = character_data.get("custom_content", [])
    if not custom_content:
        return ""
    
    output = []
    output.append("CUSTOM CONTENT CREATED")
    output.append("=" * 23)
    
    # Group custom content by type
    content_registry = ContentRegistry()  # You'd need access to the actual registry
    
    for content_name in custom_content:
        # Check what type of content this is and format accordingly
        item = content_registry.get_item(content_name)
        if item and item.item_type == "spell":
            props = item.properties
            output.append(f"🔮 SPELL: {content_name}")
            output.append(f"   Level: {props.get('level', 'Unknown')}")
            output.append(f"   School: {props.get('school', 'Unknown')}")
            output.append(f"   Casting Time: {props.get('casting_time', 'Unknown')}")
            output.append(f"   Range: {props.get('range', 'Unknown')}")
            output.append(f"   Components: {', '.join(props.get('components', []))}")
            output.append(f"   Duration: {props.get('duration', 'Unknown')}")
            output.append("")
        elif item and item.item_type == "weapon":
            props = item.properties
            output.append(f"⚔️  WEAPON: {content_name}")
            output.append(f"   Damage: {props.get('damage', 'Unknown')} {props.get('damage_type', '')}")
            output.append(f"   Properties: {', '.join(props.get('properties', []))}")
            if props.get('magical'):
                output.append(f"   Magical: Yes")
            output.append("")
        elif item and item.item_type == "armor":
            props = item.properties
            output.append(f"🛡️  ARMOR: {content_name}")
            output.append(f"   AC: {props.get('ac', 'Unknown')}")
            output.append(f"   Type: {props.get('type', 'Unknown')}")
            if props.get('magical'):
                output.append(f"   Magical: Yes")
            output.append("")
        else:
            output.append(f"✨ {content_name}")
    
    return "\n".join(output)
####
def save_character(character_data: Dict[str, Any], save_dir: str = None) -> str:
    """Save character to JSON file with enhanced data."""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_characters')
    
    os.makedirs(save_dir, exist_ok=True)
    
    char_name = character_data.get('name', 'unnamed_character')
    safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"{safe_name}_{timestamp}.json")
    
    # Add metadata
    save_data = character_data.copy()
    save_data['_metadata'] = {
        'created_at': datetime.now().isoformat(),
        'version': '3.0',
        'iterative_creation': True
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    return filename

def load_character(filename: str) -> Dict[str, Any]:
    """Load a character from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
        return character_data
    except Exception as e:
        logger.error(f"Failed to load character from {filename}: {e}")
        return {}

def format_backstory_only(character_data: Dict[str, Any]) -> str:
    """Format only the backstory elements for focused reading."""
    output = []
    
    name = character_data.get('name', 'Unknown')
    output.append(f"THE STORY OF {name.upper()}")
    output.append("=" * (len(name) + 13))
    
    detailed_backstory = character_data.get("detailed_backstory", {})
    
    if detailed_backstory:
        main_backstory = detailed_backstory.get("main_backstory", "")
        if main_backstory:
            output.append(main_backstory)
            output.append("")
        
        sections = [
            ("FAMILY HERITAGE", "family_history"),
            ("LIFE'S TURNING POINTS", "formative_events"),
            ("DRIVING FORCES", "current_motivations"),
            ("HIDDEN DEPTHS", "secrets_and_fears")
        ]
        
        for title, key in sections:
            content = detailed_backstory.get(key, "")
            if content:
                output.append(title)
                output.append("-" * len(title))
                output.append(content)
                output.append("")
    else:
        backstory = character_data.get("backstory", "No backstory available.")
        output.append(backstory)
    
    return "\n".join(output)

def save_backstory_as_text(character_data: Dict[str, Any], save_dir: str = None) -> str:
    """Save the backstory as a readable text file."""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_characters')
    
    os.makedirs(save_dir, exist_ok=True)
    
    char_name = character_data.get('name', 'unnamed_character')
    safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"{safe_name}_backstory_{timestamp}.txt")
    
    backstory_text = format_backstory_only(character_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(backstory_text)
    
    return filename

def export_character_sheet(character_data: Dict[str, Any], save_dir: str = None) -> str:
    """Export a complete character sheet as a formatted text file."""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_characters')
    
    os.makedirs(save_dir, exist_ok=True)
    
    char_name = character_data.get('name', 'unnamed_character')
    safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"{safe_name}_character_sheet_{timestamp}.txt")
    
    sheet_text = format_character_summary(character_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sheet_text)
    
    return filename

def validate_character_data(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate character data for completeness and consistency."""
    issues = []
    warnings = []
    
    # Required fields
    required_fields = ["name", "species", "level", "classes", "ability_scores"]
    for field in required_fields:
        if field not in character_data or not character_data[field]:
            issues.append(f"Missing required field: {field}")
    
    # Validate ability scores
    if "ability_scores" in character_data:
        abilities = character_data["ability_scores"]
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            if ability not in abilities:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = abilities[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score}")
                elif score < 8:
                    warnings.append(f"{ability.capitalize()} score ({score}) is very low")
    
    # Validate level
    level = character_data.get("level", 0)
    if not isinstance(level, int) or level < 1 or level > 20:
        issues.append(f"Invalid character level: {level}")
    
    # Validate classes
    classes = character_data.get("classes", {})
    if isinstance(classes, dict):
        total_levels = sum(classes.values())
        if total_levels != level:
            warnings.append(f"Class levels ({total_levels}) don't match character level ({level})")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }

def get_character_stats_summary(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get a quick summary of character's key statistics."""
    abilities = character_data.get("ability_scores", {})
    modifiers = character_data.get("ability_modifiers", {})
    
    # Find highest ability
    highest_ability = max(abilities.items(), key=lambda x: x[1]) if abilities else ("unknown", 0)
    
    # Calculate average ability score
    avg_ability = sum(abilities.values()) / len(abilities) if abilities else 0
    
    return {
        "total_level": character_data.get("level", 1),
        "primary_class": list(character_data.get("classes", {}).keys())[0] if character_data.get("classes") else "Unknown",
        "highest_ability": {"name": highest_ability[0], "score": highest_ability[1]},
        "average_ability_score": round(avg_ability, 1),
        "armor_class": character_data.get("ac", 10),
        "max_hit_points": character_data.get("hp", {}).get("max", 0),
        "proficiency_bonus": character_data.get("proficiency_bonus", 2),
        "skill_count": len(character_data.get("proficient_skills", [])),
        "has_detailed_backstory": bool(character_data.get("detailed_backstory")),
        "has_custom_content": bool(character_data.get("custom_content"))
    }

def create_character_service(use_mock: bool = False) -> CharacterCreator:
    """Factory function to create character service."""
    try:
        llm_service = OllamaLLMService()
        if not llm_service.test_connection():
            raise Exception("Ollama connection failed")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama service: {e}")
        raise Exception("LLM service initialization failed")
    
    return CharacterCreator(llm_service)


def interactive_character_creation():
    """Streamlined interactive character creation - always iterative with custom content."""
    print("🎲 D&D Enhanced Character Creator 🎲")
    print("=" * 50)
    
    try:
        creator = create_character_service()
    except Exception as e:
        print(f"❌ Failed to initialize character creator: {e}")
        return
    
    print("✅ Character creation service ready")
    print()
    
    # Get user input - only description needed
    print("Describe your character concept:")
    print("(Be as detailed as you like - mention personality, background, abilities, level, etc.)")
    description = input("> ")
    
    if not description.strip():
        print("No description provided. Using default...")
        description = "A brave adventurer seeking to make their mark on the world"
    
    # Determine appropriate level from description
    level = determine_level_from_description(description)
    print(f"📊 Determined character level: {level}")
    
    print("\n" + "="*50)
    print("🎭 CREATING YOUR CHARACTER...")
    print("="*50)
    
    # Create character - always iterative with custom content
    try:
        summary = creator.create_character_iteratively(description, level, generate_custom_content=True)
        
        print("\n" + format_character_summary(summary))
        
        # Show validation results
        validation = validate_character_data(summary)
        if not validation["valid"]:
            print("\n⚠️  CHARACTER VALIDATION ISSUES:")
            for issue in validation["issues"]:
                print(f"  • {issue}")
        
        if validation["warnings"]:
            print("\n💡 NOTES:")
            for warning in validation["warnings"]:
                print(f"  • {warning}")
        
        # Show stats summary
        stats = get_character_stats_summary(summary)
        print(f"\n📊 QUICK STATS:")
        print(f"  Primary Class: {stats['primary_class']}")
        print(f"  Highest Ability: {stats['highest_ability']['name'].title()} ({stats['highest_ability']['score']})")
        print(f"  AC: {stats['armor_class']} | HP: {stats['max_hit_points']} | Skills: {stats['skill_count']}")
        
        # Save options
        print("\n" + "="*30)
        print("SAVE OPTIONS")
        print("="*30)
        
        save_choice = input("Save character data? (y/n): ")
        if save_choice.lower().startswith('y'):
            filename = save_character(summary)
            print(f"✅ Character data saved: {filename}")
        
        backstory_choice = input("Save backstory as text file? (y/n): ")
        if backstory_choice.lower().startswith('y'):
            backstory_file = save_backstory_as_text(summary)
            print(f"✅ Backstory saved: {backstory_file}")
        
        sheet_choice = input("Export complete character sheet? (y/n): ")
        if sheet_choice.lower().startswith('y'):
            sheet_file = export_character_sheet(summary)
            print(f"✅ Character sheet exported: {sheet_file}")
        
        # Show backstory option
        view_backstory = input("\nView detailed backstory? (y/n): ")
        if view_backstory.lower().startswith('y'):
            print("\n" + format_backstory_only(summary))
        
    except Exception as e:
        logger.error(f"Character creation failed: {e}")
        print(f"❌ Character creation failed: {e}")

def determine_level_from_description(description: str) -> int:
    """Determine appropriate character level from description."""
    description_lower = description.lower()
    
    # Look for explicit level mentions
    import re
    level_match = re.search(r'level\s*(\d+)', description_lower)
    if level_match:
        level = int(level_match.group(1))
        return max(1, min(20, level))
    
    # Look for experience indicators
    high_level_indicators = [
        "veteran", "master", "legendary", "ancient", "experienced", "seasoned",
        "elite", "renowned", "famous", "powerful", "mighty", "epic",
        "years of experience", "decades", "long career", "many battles"
    ]
    
    mid_level_indicators = [
        "skilled", "trained", "competent", "capable", "proven", "established",
        "journeyman", "professional", "accomplished", "some experience"
    ]
    
    low_level_indicators = [
        "young", "new", "novice", "beginning", "fresh", "inexperienced",
        "rookie", "apprentice", "student", "learning", "starting out"
    ]
    
    # Count indicators
    high_score = sum(1 for indicator in high_level_indicators if indicator in description_lower)
    mid_score = sum(1 for indicator in mid_level_indicators if indicator in description_lower)
    low_score = sum(1 for indicator in low_level_indicators if indicator in description_lower)
    
    # Determine level based on scores
    if high_score > mid_score and high_score > low_score:
        return random.randint(11, 20)  # High level
    elif mid_score > low_score:
        return random.randint(5, 10)   # Mid level
    elif low_score > 0:
        return random.randint(1, 4)    # Low level
    else:
        # No clear indicators - look at class/role complexity
        complex_roles = [
            "assassin", "archmage", "warlock", "sorcerer", "paladin",
            "high priest", "master thief", "dragon slayer", "lich hunter"
        ]
        
        if any(role in description_lower for role in complex_roles):
            return random.randint(8, 15)  # Complex roles suggest mid-high level
        else:
            return random.randint(3, 8)   # Default to low-mid level

# custom content generator
class EnhancedCustomContentGenerator:
    """Enhanced generator for D&D-compliant custom content."""
    
    def __init__(self, llm_service, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
        
        # D&D 5e reference data
        self.spell_schools = [
            "Abjuration", "Conjuration", "Divination", "Enchantment",
            "Evocation", "Illusion", "Necromancy", "Transmutation"
        ]
        
        self.damage_types = [
            "acid", "bludgeoning", "cold", "fire", "force", "lightning",
            "necrotic", "piercing", "poison", "psychic", "radiant", 
            "slashing", "thunder"
        ]
        
        self.weapon_properties = [
            "ammunition", "finesse", "heavy", "light", "loading", "range",
            "reach", "special", "thrown", "two-handed", "versatile"
        ]
    
    def generate_custom_feat_for_character(self, character_data: Dict[str, Any], 
                                         user_description: str) -> Optional[CustomFeat]:
        """Generate a custom feat aligned with the character concept using 2024 rules."""
        
        character_level = character_data.get("level", 1)
        classes = list(character_data.get("classes", {}).keys())
        primary_class = classes[0] if classes else "Fighter"
        
        # Determine if this should be an origin feat
        is_origin_feat = character_level <= 4  # More likely to be origin feat for low levels
        
        prompt = f"""Create a unique D&D 5e (2024 rules) feat that fits this character concept. Return ONLY valid JSON.

CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {primary_class}
DESCRIPTION: {user_description}
CHARACTER LEVEL: {character_level}
ORIGIN FEAT: {"Yes - Available at level 1" if is_origin_feat else "No - Requires level 4+"}

IMPORTANT: Follow D&D 5e 2024 feat rules:
- Feats are now available at level 1 (Origin Feats) and at ASI levels (4, 8, 12, 16, 19)
- Some feats are "half-feats" that provide +1 to an ability score
- Feats should provide meaningful mechanical benefits
- Consider spellcasting grants, expertise, or special combat abilities

JSON Format:
{{
    "name": "Unique Feat Name",
    "description": "Detailed flavor text describing what this feat represents",
    "prerequisites": "None" or "Dex 13 or higher" or "4th level",
    "feat_category": "Origin" or "General" or "Fighting Style",
    "level_requirement": {1 if is_origin_feat else 4},
    "origin_feat": {str(is_origin_feat).lower()},
    "half_feat": true,
    "ability_score_increase": {{"dexterity": 1}},
    "benefits": [
        "Specific mechanical benefit 1",
        "Specific mechanical benefit 2",
        "Specific mechanical benefit 3"
    ],
    "new_proficiencies": ["Stealth", "Thieves' Tools"],
    "special_abilities": [
        "Special ability: Description of what it does",
        "Another ability: How it works mechanically"
    ],
    "combat_enhancements": [
        "Combat improvement: Specific benefit in combat"
    ],
    "spellcasting_grants": {{
        "spells": ["Light", "Mage Hand", "Cure Wounds"],
        "ability": "wisdom",
        "spell_level": 1,
        "uses_per_rest": 1,
        "rest_type": "long_rest"
    }},
    "expertise_grants": ["Investigation", "Insight"],
    "language_grants": ["Elvish", "Draconic"],
    "uses_per_rest": 1,
    "rest_type": "short_rest",
    "repeatable": false
}}

FEAT TYPES TO CONSIDER:
- Half-Feats: Provide +1 to an ability score plus other benefits
- Spellcasting Feats: Grant spells from another class (like Magic Initiate)
- Expertise Feats: Double proficiency bonus for certain skills
- Combat Feats: Improve weapon use, damage, or tactical options
- Utility Feats: Enhance exploration, social, or problem-solving abilities

REQUIREMENTS:
- Match feat to character's theme and fighting style
- Provide meaningful but balanced mechanical benefits
- Follow 2024 feat design principles
- Include appropriate prerequisites if needed
- Consider both combat and non-combat applications"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            feat = CustomFeat(
                name=data["name"],
                prerequisites=data.get("prerequisites", "None"),
                description=data["description"],
                benefits=data.get("benefits", [])
            )
            
            # Set 2024-specific attributes
            feat.feat_category = data.get("feat_category", "General")
            feat.level_requirement = data.get("level_requirement", 4)
            feat.origin_feat = data.get("origin_feat", False)
            feat.half_feat = data.get("half_feat", False)
            feat.repeatable = data.get("repeatable", False)
            
            # Set mechanical benefits
            feat.ability_score_increase = data.get("ability_score_increase", {})
            feat.new_proficiencies = data.get("new_proficiencies", [])
            feat.special_abilities = data.get("special_abilities", [])
            feat.combat_enhancements = data.get("combat_enhancements", [])
            feat.expertise_grants = data.get("expertise_grants", [])
            feat.language_grants = data.get("language_grants", [])
            
            # Set spellcasting grants
            spellcasting = data.get("spellcasting_grants", {})
            if spellcasting:
                feat.spellcasting_grants = spellcasting
            
            # Set usage limitations
            feat.uses_per_rest = data.get("uses_per_rest", 0)
            feat.rest_type = data.get("rest_type", "")
            
            # Validate the feat design
            validation = feat.validate_feat_design()
            if validation["warnings"]:
                logger.warning(f"Custom feat validation warnings: {validation['warnings']}")
            if not validation["valid"]:
                logger.error(f"Custom feat validation failed: {validation['issues']}")
                # Try to fix common issues
                feat = self._fix_feat_issues(feat, validation["issues"])
            
            # Register with content registry
            self.content_registry.register_item(CustomItem(
                name=feat.name,
                item_type="feat",
                description=feat.description,
                properties=feat.get_full_feat_dict()
            ))
            
            return feat
            
        except Exception as e:
            logger.error(f"Failed to generate custom feat: {e}")
            return None
    
    def _fix_feat_issues(self, feat: CustomFeat, issues: List[str]) -> CustomFeat:
        """Attempt to fix common feat design issues."""
        
        for issue in issues:
            if "Origin feats must have level requirement of 1" in issue:
                feat.level_requirement = 1
            elif "Half-feats must provide ability score increases" in issue:
                if not feat.ability_score_increase:
                    feat.ability_score_increase = {"strength": 1}  # Default ASI
            elif "must provide at least one meaningful benefit" in issue:
                if not feat.benefits:
                    feat.benefits = ["Gain advantage on a specific type of ability check"]
            elif "Spellcasting feats must specify casting ability" in issue:
                if feat.spellcasting_grants and not feat.spellcasting_grants.get("ability"):
                    feat.spellcasting_grants["ability"] = "wisdom"  # Default casting ability
        
        return feat

    def generate_custom_spells_for_character(self, character_data: Dict[str, Any], 
                                           user_description: str, count: int = 3) -> List[CustomSpell]:
        """Generate custom spells aligned with the character concept."""
        
        spells = []
        character_level = character_data.get("level", 1)
        classes = list(character_data.get("classes", {}).keys())
        primary_class = classes[0] if classes else "Wizard"
        
        # Determine appropriate spell levels based on character level
        max_spell_level = min(9, (character_level + 1) // 2)
        
        for i in range(count):
            spell_level = random.randint(0, max_spell_level)
            spell = self._generate_single_spell(character_data, user_description, spell_level, primary_class)
            if spell:
                spells.append(spell)
                self.content_registry.register_item(CustomItem(
                    name=spell.name,
                    item_type="spell",
                    description=spell.description,
                    properties={
                        "level": spell.level,
                        "school": spell.school,
                        "casting_time": spell.casting_time,
                        "range": spell.range_distance,
                        "components": spell.components,
                        "duration": spell.duration
                    }
                ))
        
        return spells
    
    def _generate_single_spell(self, character_data: Dict[str, Any], user_description: str,
                              spell_level: int, caster_class: str) -> Optional[CustomSpell]:
        """Generate a single custom spell."""
        
        prompt = f"""Create a unique D&D 5e spell that fits this character concept. Return ONLY valid JSON.

CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {', '.join(character_data.get('classes', {}).keys())}
DESCRIPTION: {user_description}
SPELL LEVEL: {spell_level} {"(Cantrip)" if spell_level == 0 else ""}
PRIMARY CLASS: {caster_class}

Create a spell that reflects the character's unique nature and abilities.

JSON Format:
{{
    "name": "Unique Spell Name",
    "level": {spell_level},
    "school": "One of: Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation",
    "casting_time": "1 action",
    "range": "30 feet",
    "components": ["V", "S"],
    "duration": "Instantaneous",
    "description": "Detailed spell description explaining what it does and how it works",
    "classes": ["{caster_class}"],
    "targets": "What the spell targets",
    "saving_throw": "Dexterity" or "",
    "attack_roll": false,
    "damage_type": "fire" or "",
    "higher_levels": "What happens when cast at higher spell levels"
}}

REQUIREMENTS:
- Match the spell to the character's theme and abilities
- Follow D&D 5e spell design principles
- Be creative but balanced for the spell level
- Include all required spell attributes"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            spell = CustomSpell(
                name=data["name"],
                level=data["level"],
                school=data["school"],
                casting_time=data["casting_time"],
                range_distance=data["range"],
                components=data["components"],
                duration=data["duration"],
                description=data["description"],
                classes=data["classes"]
            )
            
            # Set additional attributes
            spell.targets = data.get("targets", "")
            spell.saving_throw = data.get("saving_throw", "")
            spell.attack_roll = data.get("attack_roll", False)
            spell.damage_type = data.get("damage_type", "")
            spell.higher_levels = data.get("higher_levels", "")
            
            return spell
            
        except Exception as e:
            logger.error(f"Failed to generate custom spell: {e}")
            return None
    
    def generate_custom_weapons_for_character(self, character_data: Dict[str, Any], 
                                            user_description: str, count: int = 2) -> List[CustomWeapon]:
        """Generate custom weapons aligned with the character concept."""
        
        weapons = []
        character_level = character_data.get("level", 1)
        
        for i in range(count):
            weapon = self._generate_single_weapon(character_data, user_description, character_level)
            if weapon:
                weapons.append(weapon)
                self.content_registry.register_item(CustomItem(
                    name=weapon.name,
                    item_type="weapon",
                    description=weapon.description,
                    properties={
                        "damage": weapon.damage_dice,
                        "damage_type": weapon.damage_type,
                        "properties": weapon.properties,
                        "magical": weapon.magical
                    }
                ))
        
        return weapons

####   
    def _generate_single_weapon(self, character_data: Dict[str, Any], user_description: str,
                            character_level: int) -> Optional[CustomWeapon]:
        """Generate a single custom weapon with full 2024 compliance."""
        
        # Determine if weapon should be magical based on level
        magical = character_level >= 5
        magical_bonus = 1 if magical and character_level >= 8 else 0
        
        # Determine weapon complexity based on character classes
        classes = list(character_data.get("classes", {}).keys())
        martial_classes = ["fighter", "paladin", "ranger", "barbarian", "monk"]
        is_martial_user = any(cls.lower() in martial_classes for cls in classes)
        
        category = "Martial" if is_martial_user else "Simple"
        
        prompt = f"""Create a unique D&D 5e (2024 rules) weapon that fits this character concept. Return ONLY valid JSON.

    CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {', '.join(character_data.get('classes', {}).keys())}
    DESCRIPTION: {user_description}
    CHARACTER LEVEL: {character_level}
    WEAPON CATEGORY: {category}
    MAGICAL WEAPON: {"Yes" if magical else "No"}

    IMPORTANT: Follow D&D 5e 2024 rules including the NEW Weapon Mastery system.

    JSON Format:
    {{
        "name": "Unique Weapon Name",
        "category": "{category}",
        "weapon_type": "Melee, Ranged, or Melee/Ranged",
        "damage_dice": "1d8",
        "damage_type": "slashing, piercing, bludgeoning, or magical type",
        "properties": ["finesse", "light"],
        "mastery_property": "One of: Cleave, Graze, Nick, Push, Sap, Slow, Topple, Vex",
        "versatile_damage": "1d10" or "",
        "range_normal": 20,
        "range_long": 60,
        "cost": "25 gp",
        "weight": "2 lb.",
        "description": "Detailed weapon description and appearance",
        "origin_story": "How this weapon was created or came to be",
        "magical": {str(magical).lower()},
        "magical_bonus": {magical_bonus},
        "special_abilities": ["Special magical ability if applicable"]
    }}

    WEAPON PROPERTIES: ammunition, finesse, heavy, light, loading, range, reach, thrown, two-handed, versatile, improvised

    MASTERY PROPERTIES:
    - Cleave: Hit adjacent enemy on kill
    - Graze: Deal damage even on miss
    - Nick: Extra attack with light weapon
    - Push: Force movement on hit
    - Sap: Reduce enemy damage
    - Slow: Reduce enemy speed
    - Topple: Knock prone on critical hit
    - Vex: Grant advantage to next attack

    DAMAGE TYPES: slashing, piercing, bludgeoning, acid, cold, fire, force, lightning, necrotic, poison, psychic, radiant, thunder

    REQUIREMENTS:
    - Match weapon to character's fighting style and theme
    - Follow D&D 5e 2024 weapon design principles
    - Include appropriate mastery property for weapon type
    - Balance magical abilities appropriately for character level
    - Ensure property combinations are valid"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            weapon = CustomWeapon(
                name=data["name"],
                category=data["category"],
                weapon_type=data["weapon_type"],
                damage_dice=data["damage_dice"],
                damage_type=data["damage_type"],
                properties=data["properties"],
                cost=data.get("cost", ""),
                weight=data.get("weight", "")
            )
            
            # Set 2024-specific attributes
            weapon.mastery_property = data.get("mastery_property", "")
            weapon.versatile_damage = data.get("versatile_damage", "")
            
            # Set range
            weapon.range_normal = data.get("range_normal", 0)
            weapon.range_long = data.get("range_long", 0)
            
            # Set descriptions
            weapon.description = data.get("description", "")
            weapon.origin_story = data.get("origin_story", "")
            
            # Set magical properties
            weapon.magical = data.get("magical", False)
            weapon.magical_bonus = data.get("magical_bonus", 0)
            weapon.special_abilities = data.get("special_abilities", [])
            
            # Validate the weapon design
            validation = weapon.validate_weapon_design()
            if validation["warnings"]:
                logger.warning(f"Custom weapon validation warnings: {validation['warnings']}")
            if not validation["valid"]:
                logger.error(f"Custom weapon validation failed: {validation['issues']}")
                # Try to fix common issues
                weapon = self._fix_weapon_issues(weapon, validation["issues"])
            
            return weapon
            
        except Exception as e:
            logger.error(f"Failed to generate custom weapon: {e}")
            return None

    def _fix_weapon_issues(self, weapon: CustomWeapon, issues: List[str]) -> CustomWeapon:
        """Attempt to fix common weapon design issues."""
        
        for issue in issues:
            if "Invalid weapon category" in issue:
                weapon.category = "Simple"  # Default to simple
            elif "Invalid weapon type" in issue:
                weapon.weapon_type = "Melee"  # Default to melee
            elif "two-handed and light" in issue:
                # Remove light property if weapon is two-handed
                if "two-handed" in [p.lower() for p in weapon.properties]:
                    weapon.properties = [p for p in weapon.properties if p.lower() != "light"]
                else:
                    weapon.properties = [p for p in weapon.properties if p.lower() != "two-handed"]
            elif "Ranged weapons must have a range" in issue:
                weapon.range_normal = 80  # Default range
                weapon.range_long = 320
        
        return weapon
    
    def generate_custom_armor_for_character(self, character_data: Dict[str, Any], 
                                          user_description: str) -> Optional[CustomArmor]:
        """Generate custom armor aligned with the character concept."""
        
        character_level = character_data.get("level", 1)
        classes = list(character_data.get("classes", {}).keys())
        primary_class = classes[0] if classes else "Fighter"
        
        # Determine appropriate armor type based on class
        if primary_class.lower() in ["wizard", "sorcerer", "warlock"]:
            armor_type = "Light"
            base_ac = 11
        elif primary_class.lower() in ["rogue", "ranger", "bard"]:
            armor_type = "Medium"
            base_ac = 13
        else:
            armor_type = "Heavy"
            base_ac = 16
        
        magical = character_level >= 5
        
        prompt = f"""Create unique D&D 5e armor that fits this character concept. Return ONLY valid JSON.

CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {primary_class}
DESCRIPTION: {user_description}
CHARACTER LEVEL: {character_level}
ARMOR TYPE: {armor_type}
MAGICAL ARMOR: {"Yes" if magical else "No"}

JSON Format:
{{
    "name": "Unique Armor Name",
    "armor_type": "{armor_type}",
    "ac_base": {base_ac + (1 if magical else 0)},
    "dex_bonus": "Dex mod" or "Dex mod (max 2)" or "—",
    "cost": "150 gp",
    "weight": "20 lb.",
    "strength_requirement": 0,
    "stealth_disadvantage": false,
    "description": "Detailed armor description and appearance",
    "magical": {str(magical).lower()},
    "magical_bonus": {1 if magical else 0},
    "special_abilities": ["Special magical ability if applicable"]
}}

REQUIREMENTS:
- Match armor to character's class and theme
- Follow D&D 5e armor design principles
- Balance magical abilities appropriately for character level"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            armor = CustomArmor(
                name=data["name"],
                armor_type=data["armor_type"],
                ac_base=data["ac_base"],
                dex_bonus=data["dex_bonus"],
                cost=data.get("cost", ""),
                weight=data.get("weight", "")
            )
            
            # Set additional attributes
            armor.strength_requirement = data.get("strength_requirement", 0)
            armor.stealth_disadvantage = data.get("stealth_disadvantage", False)
            armor.description = data.get("description", "")
            armor.magical = data.get("magical", False)
            armor.magical_bonus = data.get("magical_bonus", 0)
            armor.special_abilities = data.get("special_abilities", [])
            
            self.content_registry.register_item(CustomItem(
                name=armor.name,
                item_type="armor",
                description=armor.description,
                properties={
                    "ac": armor.ac_base,
                    "type": armor.armor_type,
                    "magical": armor.magical
                }
            ))
            
            return armor
            
        except Exception as e:
            logger.error(f"Failed to generate custom armor: {e}")
            return None
    
    def generate_custom_feat_for_character(self, character_data: Dict[str, Any], 
                                         user_description: str) -> Optional[CustomFeat]:
        """Generate a custom feat aligned with the character concept."""
        
        prompt = f"""Create a unique D&D 5e feat that fits this character concept. Return ONLY valid JSON.

CHARACTER: {character_data.get('name', 'Unknown')} - {character_data.get('species', 'Human')} {', '.join(character_data.get('classes', {}).keys())}
DESCRIPTION: {user_description}

Create a feat that enhances the character's unique abilities or theme.

JSON Format:
{{
    "name": "Unique Feat Name",
    "prerequisites": "Dex 13 or higher" or "None",
    "description": "Flavor text describing the feat",
    "benefits": [
        "Specific mechanical benefit 1",
        "Specific mechanical benefit 2"
    ],
    "ability_score_increase": {{"dexterity": 1}},
    "new_proficiencies": ["Stealth", "Thieves' Tools"],
    "special_abilities": ["New ability or feature gained"]
}}

REQUIREMENTS:
- Match feat to character's theme and abilities
- Follow D&D 5e feat design principles
- Provide meaningful mechanical benefits
- Balance power level appropriately"""
        
        try:
            response = self.llm_service.generate(prompt)
            data = json.loads(response.strip())
            
            feat = CustomFeat(
                name=data["name"],
                prerequisites=data["prerequisites"],
                description=data["description"],
                benefits=data["benefits"]
            )
            
            # Set additional attributes
            feat.ability_score_increase = data.get("ability_score_increase", {})
            feat.new_proficiencies = data.get("new_proficiencies", [])
            feat.special_abilities = data.get("special_abilities", [])
            
            self.content_registry.register_item(CustomItem(
                name=feat.name,
                item_type="feat",
                description=feat.description,
                properties={
                    "prerequisites": feat.prerequisites,
                    "benefits": feat.benefits
                }
            ))
            
            return feat
            
        except Exception as e:
            logger.error(f"Failed to generate custom feat: {e}")
            return None


# ...existing code...

class AbilityScoreManager:
    """Manages ability score progression, ASIs, and modifications."""
    
    def __init__(self):
        self.base_scores = {}  # Initial rolled/assigned scores
        self.species_bonuses = {}  # Species-based bonuses (2024: from background instead)
        self.background_bonuses = {}  # 2024 rule: background provides ASI
        self.asi_improvements = []  # List of ASI choices made
        self.feat_bonuses = {}  # Bonuses from feats
        self.magic_item_bonuses = {}  # Temporary/permanent magical bonuses
        self.temporary_bonuses = {}  # Short-term effects
        self.score_overrides = {}  # Items that set scores (like Belt of Giant Strength)
    
    def calculate_final_score(self, ability: str) -> int:
        """Calculate the final ability score including all modifiers."""
        # Check for score overrides first (items that set scores)
        if ability in self.score_overrides:
            return self.score_overrides[ability]
        
        # Start with base score
        total = self.base_scores.get(ability, 10)
        
        # Add all bonuses
        total += self.species_bonuses.get(ability, 0)
        total += self.background_bonuses.get(ability, 0)
        total += self.feat_bonuses.get(ability, 0)
        total += self.magic_item_bonuses.get(ability, 0)
        total += self.temporary_bonuses.get(ability, 0)
        
        # Add ASI improvements
        for asi in self.asi_improvements:
            total += asi.get(ability, 0)
        
        # Cap at 20 unless overridden by magic items
        if ability not in self.score_overrides:
            total = min(total, 20)
        
        return max(1, min(30, total))  # Absolute limits: 1-30
    
    def add_asi_improvement(self, improvements: Dict[str, int]):
        """Add an ASI improvement (e.g., {Strength: 2} or {Strength: 1, Dexterity: 1})."""
        self.asi_improvements.append(improvements.copy())
    
    def apply_feat_bonus(self, feat_name: str, ability: str, bonus: int):
        """Apply ability score bonus from a feat."""
        if ability not in self.feat_bonuses:
            self.feat_bonuses[ability] = 0
        self.feat_bonuses[ability] += bonus
    
    def set_magic_item_override(self, ability: str, score: int):
        """Set score override from magic item (like Belt of Giant Strength)."""
        self.score_overrides[ability] = score
    
    def remove_magic_item_override(self, ability: str):
        """Remove magic item score override."""
        if ability in self.score_overrides:
            del self.score_overrides[ability]

class LevelUpManager:
    """Manages level-up progression including ASIs and multiclassing."""
    
    def __init__(self):
        self.class_asi_levels = {
            # Standard progression
            "default": [4, 8, 12, 16, 19],
            # Classes with extra ASIs
            "Fighter": [4, 6, 8, 12, 14, 16, 19],
            "Rogue": [4, 8, 10, 12, 16, 19]
        }
    
    def get_asi_levels_for_class(self, class_name: str) -> List[int]:
        """Get ASI levels for a specific class."""
        return self.class_asi_levels.get(class_name, self.class_asi_levels["default"])
    
    def calculate_available_asis(self, character_classes: Dict[str, int]) -> List[Dict[str, Any]]:
        """Calculate all available ASIs for a multiclass character."""
        available_asis = []
        
        for class_name, class_level in character_classes.items():
            asi_levels = self.get_asi_levels_for_class(class_name)
            
            for asi_level in asi_levels:
                if class_level >= asi_level:
                    available_asis.append({
                        "class": class_name,
                        "level": asi_level,
                        "total_character_level": self._calculate_character_level_at_class_asi(
                            character_classes, class_name, asi_level
                        )
                    })
        
        return sorted(available_asis, key=lambda x: x["total_character_level"])
    
    def _calculate_character_level_at_class_asi(self, character_classes: Dict[str, int], 
                                              target_class: str, target_level: int) -> int:
        """Calculate what total character level was when a specific class ASI was gained."""
        # This is complex for multiclass - simplified implementation
        total_levels = sum(character_classes.values())
        class_level = character_classes[target_class]
        
        # Estimate based on even distribution (more complex logic could be added)
        return total_levels - class_level + target_level
    
    def level_up_character(self, character_data: Dict[str, Any], 
                          target_class: str) -> Dict[str, Any]:
        """Level up a character in a specific class."""
        if "classes" not in character_data:
            character_data["classes"] = {}
        
        # Increase class level
        current_level = character_data["classes"].get(target_class, 0)
        character_data["classes"][target_class] = current_level + 1
        new_level = current_level + 1
        
        # Update total level
        character_data["level"] = sum(character_data["classes"].values())
        
        # Check if this grants an ASI
        asi_levels = self.get_asi_levels_for_class(target_class)
        if new_level in asi_levels:
            character_data.setdefault("pending_asis", []).append({
                "class": target_class,
                "level": new_level,
                "available": True
            })
        
        return character_data

class CustomSpeciesAbilityManager:
    """Manages ability score interactions for custom species."""
    
    @staticmethod
    def apply_2024_species_rules(species: CustomSpecies, character_data: Dict[str, Any]):
        """Apply 2024 D&D rules - species don't grant ability bonuses."""
        # In 2024 rules, species don't provide ability score increases
        # Background provides the +2/+1 or +1/+1/+1 distribution instead
        
        # Custom species might have special rules that affect abilities
        for feature in species.innate_traits:
            if "ability score" in feature.lower():
                # Handle special cases where species do affect abilities
                # (like size changes affecting Strength)
                pass
    
    @staticmethod
    def handle_size_ability_effects(species: CustomSpecies, character_data: Dict[str, Any]):
        """Handle ability score effects from non-standard sizes."""
        size = species.size.lower()
        
        if size == "tiny":
            # Tiny creatures might have Strength limitations
            max_str = character_data.get("ability_score_maximums", {})
            max_str["strength"] = min(max_str.get("strength", 20), 6)
            character_data["ability_score_maximums"] = max_str
        
        elif size == "large" or size == "huge":
            # Large creatures might have enhanced carrying capacity
            # But not automatic ability score bonuses in 2024 rules
            pass

class CustomClassAbilityManager:
    """Manages ability score interactions for custom classes."""
    
    @staticmethod
    def calculate_custom_class_asi_levels(custom_class: CustomClass) -> List[int]:
        """Calculate ASI levels for a custom class."""
        if custom_class.proficiency_bonus_progression == "enhanced":
            # Enhanced progression might grant additional ASIs
            return [4, 6, 8, 12, 14, 16, 19]  # Fighter-like progression
        else:
            return [4, 8, 12, 16, 19]  # Standard progression
    
    @staticmethod
    def apply_class_ability_features(custom_class: CustomClass, 
                                   character_level: int,
                                   character_data: Dict[str, Any]):
        """Apply class features that affect ability scores."""
        features = custom_class.get_features_at_level(character_level)
        
        for feature in features:
            feature_name = feature["name"].lower()
            
            # Look for ability score enhancements
            if "ability score" in feature_name or "asi" in feature_name:
                # Handle special ASI features
                pass
            elif "maximum" in feature_name:
                # Handle features that increase ability score maximums
                # (like Barbarian's Primal Champion)
                CustomClassAbilityManager._handle_maximum_increases(
                    feature, character_data
                )
    
    @staticmethod
    def _handle_maximum_increases(feature: Dict[str, str], character_data: Dict[str, Any]):
        """Handle features that increase ability score maximums."""
        description = feature["description"].lower()
        
        # Parse description for ability score maximum increases
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in abilities:
            if ability in description and "maximum" in description:
                # Extract new maximum (simplified parsing)
                if "24" in description:
                    new_max = 24
                elif "22" in description:
                    new_max = 22
                else:
                    new_max = 20
                
                maximums = character_data.setdefault("ability_score_maximums", {})
                maximums[ability] = max(maximums.get(ability, 20), new_max)

def enhance_character_data_with_ability_details(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance character data with detailed ability score information."""
    
    # Create enhanced ability score details
    ability_details = {}
    ability_scores = character_data.get("ability_scores", {})
    
    for ability, score in ability_scores.items():
        ability_details[ability] = {
            "total_score": score,
            "base": score,  # Assuming starting scores for now
            "asi_improvements": 0,
            "feat_improvements": 0,
            "magic_item_bonuses": 0,
            "temporary_bonuses": 0,
            "history": []
        }
    
    character_data["ability_score_details"] = ability_details
    
    # Calculate ASI information
    level = character_data.get("level", 1)
    classes = character_data.get("classes", {})
    
    asi_manager = ASIManager()
    asi_info = asi_manager.calculate_available_asis(classes)
    character_data["asi_info"] = asi_info
    
    return character_data

# Update the CharacterCreator to use enhanced ability score system
def update_character_creator_populate_method():
    """Update the _populate_character_from_data method in CharacterCreator."""
    
    def _populate_character_from_data(self, character_data: Dict[str, Any]):
        """Enhanced population method with proper ability score handling."""
        
        self.character = CharacterSheet(character_data.get("name", "Unnamed"))
        
        # Basic info
        self.character.core.species = character_data.get("species", "Human")
        self.character.core.background = character_data.get("background", "")
        self.character.core.alignment = character_data.get("alignment", ["Neutral", "Neutral"])
        
        # Classes
        classes = character_data.get("classes", {"Fighter": 1})
        self.character.core.character_classes = classes
        
        # Enhanced ability scores with proper tracking
        abilities = character_data.get("ability_scores", {})
        for ability, score in abilities.items():
            ability_obj = self.character.core.get_ability_score(ability)
            if ability_obj:
                # Set as base score for now - in a full implementation,
                # you'd want to parse the actual sources
                ability_obj.base_score = score
        
        # Enhance character data with detailed ability information
        character_data = enhance_character_data_with_ability_details(character_data)
        
        # Skills and other attributes
        for skill in character_data.get("skill_proficiencies", []):
            self.character.core.skill_proficiencies[skill] = ProficiencyLevel.PROFICIENT
        
        # Personality
        self.character.core.personality_traits = character_data.get("personality_traits", [])
        self.character.core.ideals = character_data.get("ideals", [])
        self.character.core.bonds = character_data.get("bonds", [])
        self.character.core.flaws = character_data.get("flaws", [])
        
        # Backstory
        detailed_backstory = character_data.get("detailed_backstory", {})
        if detailed_backstory:
            self.character.core.set_detailed_backstory(detailed_backstory)
        else:
            self.character.core.backstory = character_data.get("backstory", "")
        
        # Custom content tracking
        self.character.core.custom_content_used = character_data.get("custom_content", [])
        
        # Equipment
        self.character.state.armor = character_data.get("armor", "")
        self.character.state.weapons = character_data.get("weapons", [])
        self.character.state.equipment = character_data.get("equipment", [])
        
        # Calculate derived stats
        self.character.calculate_all_derived_stats()

# Update format_character_summary to include enhanced ability score information
def enhanced_format_character_summary(character_data: Dict[str, Any]) -> str:
    """Enhanced character summary with detailed ability score progression."""
    
    # Enhance the data first
    character_data = enhance_character_data_with_ability_details(character_data)
    
    # Use existing format_character_summary as base
    output = format_character_summary(character_data).split('\n')
    
    # Find where ability scores section ends and insert enhanced details
    ability_section_end = -1
    for i, line in enumerate(output):
        if line.startswith("COMBAT STATISTICS"):
            ability_section_end = i
            break
    
    if ability_section_end > 0:
        # Insert enhanced ability score details
        enhanced_abilities = format_ability_scores_detailed(character_data).split('\n')
        
        # Replace the basic ability scores with enhanced version
        ability_start = -1
        for i in range(ability_section_end):
            if "ABILITY SCORES" in output[i]:
                ability_start = i
                break
        
        if ability_start >= 0:
            # Remove old ability section
            while ability_start < len(output) and not output[ability_start].startswith("COMBAT"):
                output.pop(ability_start)
            
            # Insert enhanced section
            for line in reversed(enhanced_abilities):
                output.insert(ability_start, line)
    
    # Add ASI progression section
    asi_section = format_asi_progression(character_data)
    if asi_section.strip():
        # Insert after combat statistics
        combat_end = -1
        for i, line in enumerate(output):
            if line.startswith("PROFICIENT SKILLS") or line.startswith("EQUIPMENT"):
                combat_end = i
                break
        
        if combat_end > 0:
            asi_lines = asi_section.split('\n')
            for line in reversed(asi_lines):
                output.insert(combat_end, line)
    
    # Add multiclass progression if applicable
    multiclass_section = format_multiclass_progression(character_data)
    if multiclass_section.strip():
        output.extend(['', multiclass_section])
    
    return '\n'.join(output)

class EnhancedAbilityScore:
    """Enhanced ability score class with comprehensive tracking."""
    
    def __init__(self, base_score: int = 10):
        self.base_score = base_score
        self.manager = AbilityScoreManager()
        self.manager.base_scores = {"main": base_score}  # Simplified for single score
    
    @property
    def total_score(self) -> int:
        return self.manager.calculate_final_score("main")
    
    @property
    def modifier(self) -> int:
        return (self.total_score - 10) // 2
    
    def add_asi_improvement(self, bonus: int):
        """Add ASI improvement to this ability score."""
        self.manager.add_asi_improvement({"main": bonus})
    
    def add_feat_bonus(self, feat_name: str, bonus: int):
        """Add feat bonus to this ability score."""
        self.manager.apply_feat_bonus(feat_name, "main", bonus)
    
    def set_magic_item_score(self, score: int):
        """Set score from magic item."""
        self.manager.set_magic_item_override("main", score)

# Enhanced CharacterCore with improved ability score management
class EnhancedCharacterCore(CharacterCore):
    """Enhanced character core with comprehensive ability score management."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        
        # Enhanced ability score management
        self.ability_manager = AbilityScoreManager()
        self.level_manager = LevelUpManager()
        
        # Track ability score history
        self.ability_score_history = []  # Track changes over time
        self.asi_choices_made = []  # Track ASI decisions
        self.pending_asi_choices = []  # ASIs available but not yet chosen
        
        # 2024 D&D rules - background provides ability increases
        self.background_ability_bonuses = {}  # +2/+1 or +1/+1/+1 from background
        
        # Custom content ability interactions
        self.custom_species_effects = {}
        self.custom_class_effects = {}
    
    def set_base_ability_scores(self, scores: Dict[str, int]):
        """Set the base ability scores (from rolling/point buy)."""
        self.ability_manager.base_scores = scores.copy()
        
        # Update individual AbilityScore objects
        for ability, score in scores.items():
            if hasattr(self, ability):
                ability_obj = getattr(self, ability)
                ability_obj.base_score = score
    
    def apply_background_bonuses(self, bonuses: Dict[str, int]):
        """Apply ability score bonuses from background (2024 rules)."""
        self.ability_manager.background_bonuses = bonuses.copy()
        self.background_ability_bonuses = bonuses.copy()
    
    def level_up_in_class(self, class_name: str) -> Dict[str, Any]:
        """Level up in a specific class and handle ASIs."""
        result = self.level_manager.level_up_character(
            self.to_dict(), class_name
        )
        
        # Update character data
        self.character_classes = result["classes"]
        
        # Handle pending ASIs
        if "pending_asis" in result:
            self.pending_asi_choices.extend(result["pending_asis"])
        
        return {
            "success": True,
            "new_level": self.character_classes[class_name],
            "total_level": self.total_level,
            "pending_asis": len(self.pending_asi_choices),
            "available_asi": len(self.pending_asi_choices) > 0
        }
    
    def apply_asi_choice(self, improvements: Dict[str, int], asi_index: int = 0):
        """Apply an ASI choice."""
        if asi_index >= len(self.pending_asi_choices):
            raise ValueError("No pending ASI available")
        
        # Validate improvements
        total_points = sum(improvements.values())
        if total_points != 2:
            raise ValueError("ASI must total 2 points (+2 to one or +1 to two different)")
        
        for ability, bonus in improvements.items():
            if bonus not in [1, 2]:
                raise ValueError("Individual bonuses must be +1 or +2")
            if bonus == 2 and len(improvements) > 1:
                raise ValueError("Cannot give +2 to multiple abilities")
        
        # Apply the improvement
        self.ability_manager.add_asi_improvement(improvements)
        
        # Record the choice
        asi_info = self.pending_asi_choices.pop(asi_index)
        asi_info["improvements"] = improvements
        self.asi_choices_made.append(asi_info)
        
        # Update individual AbilityScore objects
        for ability, bonus in improvements.items():
            if hasattr(self, ability):
                ability_obj = getattr(self, ability)
                ability_obj.add_asi_improvement(bonus)
    
    def apply_custom_species_effects(self, custom_species: CustomSpecies):
        """Apply custom species effects on ability scores."""
        CustomSpeciesAbilityManager.apply_2024_species_rules(
            custom_species, self.to_dict()
        )
        CustomSpeciesAbilityManager.handle_size_ability_effects(
            custom_species, self.to_dict()
        )
    
    def apply_custom_class_effects(self, custom_class: CustomClass, class_level: int):
        """Apply custom class effects on ability scores."""
        CustomClassAbilityManager.apply_class_ability_features(
            custom_class, class_level, self.to_dict()
        )
    
    def get_available_asis(self) -> List[Dict[str, Any]]:
        """Get all available ASIs for this character."""
        return self.level_manager.calculate_available_asis(self.character_classes)
    
    def get_ability_score_summary(self) -> Dict[str, Any]:
        """Get comprehensive ability score summary."""
        summary = {}
        
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in abilities:
            ability_obj = getattr(self, ability)
            final_score = self.ability_manager.calculate_final_score(ability)
            
            summary[ability] = {
                "base_score": self.ability_manager.base_scores.get(ability, 10),
                "background_bonus": self.ability_manager.background_bonuses.get(ability, 0),
                "asi_bonuses": sum(asi.get(ability, 0) for asi in self.ability_manager.asi_improvements),
                "feat_bonuses": self.ability_manager.feat_bonuses.get(ability, 0),
                "magic_item_effects": ability in self.ability_manager.score_overrides,
                "final_score": final_score,
                "modifier": (final_score - 10) // 2,
                "maximum": self.to_dict().get("ability_score_maximums", {}).get(ability, 20)
            }
        
        return summary
    
    def validate_ability_scores(self) -> Dict[str, Any]:
        """Validate character ability scores."""
        issues = []
        warnings = []
        
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in abilities:
            final_score = self.ability_manager.calculate_final_score(ability)
            maximum = self.to_dict().get("ability_score_maximums", {}).get(ability, 20)
            
            if final_score > maximum:
                issues.append(f"{ability.title()} score ({final_score}) exceeds maximum ({maximum})")
            elif final_score < 1:
                issues.append(f"{ability.title()} score cannot be less than 1")
            elif final_score > 20 and ability not in self.ability_manager.score_overrides:
                warnings.append(f"{ability.title()} score ({final_score}) above 20 without magic item")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

# Update the character creation process to handle ability scores properly
class EnhancedCharacterCreator(CharacterCreator):
    """Enhanced character creator with proper ability score management."""
    
    def create_character_with_ability_management(self, description: str, level: int = 1) -> Dict[str, Any]:
        """Create character with comprehensive ability score management."""
        
        # Generate base character
        character_data = self.create_character(description, level)
        
        # Create enhanced character core
        enhanced_core = EnhancedCharacterCore(character_data.get("name", ""))
        
        # Set base ability scores
        ability_scores = character_data.get("ability_scores", {})
        enhanced_core.set_base_ability_scores(ability_scores)
        
        # Apply background bonuses (2024 rules)
        background_bonuses = self._determine_background_bonuses(
            character_data.get("background", ""), description
        )
        enhanced_core.apply_background_bonuses(background_bonuses)
        
        # Handle multiclass leveling and ASIs
        classes = character_data.get("classes", {})
        for class_name, class_level in classes.items():
            # Simulate leveling up to current level
            for level_up in range(1, class_level + 1):
                if level_up > 1:  # Skip level 1
                    enhanced_core.level_up_in_class(class_name)
        
        # Apply custom species/class effects if present
        if "custom_content" in character_data:
            self._apply_custom_content_effects(enhanced_core, character_data)
        
        # Update character data with enhanced ability scores
        character_data["enhanced_abilities"] = enhanced_core.get_ability_score_summary()
        character_data["available_asis"] = enhanced_core.get_available_asis()
        character_data["pending_asis"] = len(enhanced_core.pending_asi_choices)
        
        return character_data
    
    def _determine_background_bonuses(self, background: str, description: str) -> Dict[str, int]:
        """Determine ability score bonuses from background (2024 rules)."""
        # 2024 D&D: Background provides +2/+1 or +1/+1/+1 to abilities
        # This is a simplified implementation - could be more sophisticated
        
        description_lower = description.lower()
        
        # Analyze description for primary/secondary abilities
        ability_indicators = {
            "strength": ["strong", "muscular", "warrior", "fighter", "physical"],
            "dexterity": ["agile", "quick", "nimble", "thief", "rogue", "archer"],
            "constitution": ["hardy", "tough", "resilient", "enduring"],
            "intelligence": ["smart", "clever", "wizard", "scholar", "learned"],
            "wisdom": ["wise", "perceptive", "cleric", "druid", "insightful"],
            "charisma": ["charming", "leader", "bard", "sorcerer", "persuasive"]
        }
        
        # Score abilities based on description
        ability_scores = {}
        for ability, indicators in ability_indicators.items():
            score = sum(1 for indicator in indicators if indicator in description_lower)
            ability_scores[ability] = score
        
        # Find top 2 abilities
        sorted_abilities = sorted(ability_scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_abilities[0][1] > sorted_abilities[1][1]:
            # Clear primary ability gets +2, secondary gets +1
            return {
                sorted_abilities[0][0]: 2,
                sorted_abilities[1][0]: 1
            }
        else:
            # Tied scores, distribute +1/+1/+1 to top 3
            return {
                sorted_abilities[0][0]: 1,
                sorted_abilities[1][0]: 1,
                sorted_abilities[2][0]: 1
            }
    
    def _apply_custom_content_effects(self, enhanced_core: EnhancedCharacterCore, 
                                    character_data: Dict[str, Any]):
        """Apply custom species and class effects to ability scores."""
        
        # Apply custom species effects
        custom_species_name = character_data.get("species", "")
        if custom_species_name in self.content_registry.custom_species:
            custom_species = self.content_registry.custom_species[custom_species_name]
            enhanced_core.apply_custom_species_effects(custom_species)
        
        # Apply custom class effects
        classes = character_data.get("classes", {})
        for class_name, class_level in classes.items():
            if class_name in self.content_registry.custom_classes:
                custom_class = self.content_registry.custom_classes[class_name]
                enhanced_core.apply_custom_class_effects(custom_class, class_level)





def main():
    """Simplified main entry point with 3 options only."""
    while True:
        print("\n🎲 D&D Character Creator - Main Menu")
        print("=" * 40)
        print("1. Create New Character (Iterative)")
        print("2. Load Existing Character")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            interactive_character_creation()
            
        elif choice == "2":
            filename = input("Enter character file path: ").strip()
            if os.path.exists(filename):
                character_data = load_character(filename)
                if character_data:
                    print("\n" + format_character_summary(character_data))
                    
                    # Option to view just backstory
                    if input("\nView detailed backstory only? (y/n): ").lower().startswith('y'):
                        print("\n" + format_backstory_only(character_data))
                else:
                    print("Failed to load character data")
            else:
                print("File not found")
                
        elif choice == "3":
            print("Goodbye! May your adventures be legendary! 🗺️")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()