# ## **3. `character_models.py`**
# **Character sheet and data models**
# - **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`, `CharacterIterationCache`
# - **Purpose**: Character data structures, hit points, equipment, calculated statistics
# - **Dependencies**: `core_models.py`

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import from core_models.py
from core_models import (
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
# CHARACTER DATA MODELS
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
    
    def heal(self, healing: int) -> Dict[str, int]:
        """Apply healing to the character."""
        if healing <= 0:
            return {"healing_applied": 0, "hp_remaining": self.current_hit_points}
        
        old_hp = self.current_hit_points
        self.current_hit_points += healing
        
        result = {
            "healing_applied": healing,
            "old_hp": old_hp,
            "new_hp": self.current_hit_points
        }
        
        logger.info(f"Character healed for {healing}. HP: {self.current_hit_points}")
        return result
    
    def add_condition(self, condition_name: str, duration: str = "indefinite", 
                     save_dc: int = 0, save_ability: str = ""):
        """Add a condition to the character."""
        self.active_conditions[condition_name] = {
            "duration": duration,
            "save_dc": save_dc,
            "save_ability": save_ability,
            "applied_at": datetime.now().isoformat()
        }
        logger.info(f"Applied condition: {condition_name}")
    
    def remove_condition(self, condition_name: str):
        """Remove a condition from the character."""
        if condition_name in self.active_conditions:
            del self.active_conditions[condition_name]
            logger.info(f"Removed condition: {condition_name}")
    
    def add_equipment(self, item: Dict[str, Any]):
        """Add an item to the character's equipment."""
        self.equipment.append(item)
        logger.info(f"Added equipment: {item.get('name', 'Unknown Item')}")
    
    def add_weapon(self, weapon: Dict[str, Any]):
        """Add a weapon to the character's arsenal."""
        self.weapons.append(weapon)
        logger.info(f"Added weapon: {weapon.get('name', 'Unknown Weapon')}")
    
    def get_total_currency_value_in_gold(self) -> float:
        """Get total currency value converted to gold pieces."""
        return (self.currency["copper"] * 0.01 + 
                self.currency["silver"] * 0.1 + 
                self.currency["gold"] + 
                self.currency["platinum"] * 10)

# ============================================================================
# CHARACTER STATISTICS
# ============================================================================

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
        """Recalculate all derived statistics."""
        self.stats.invalidate_cache()
        if self.state.current_hit_points == 0:  # Only set if not already set
            self.state.current_hit_points = self.stats.max_hit_points
    
    def level_up(self, class_name: str, asi_choice: Optional[Dict[str, Any]] = None):
        """Level up the character in the specified class."""
        self.core.level_up(class_name, asi_choice)
        self.calculate_all_derived_stats()
        logger.info(f"Character {self.core.name} leveled up to {class_name} level {self.core.character_classes.get(class_name, 0)}")
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        max_hp = self.stats.max_hit_points
        result = self.state.take_damage(damage)
        
        # Ensure current HP doesn't exceed max HP after calculation
        if self.state.current_hit_points > max_hp:
            self.state.current_hit_points = max_hp
            
        return result
    
    def heal(self, healing: int) -> Dict[str, int]:
        """Heal the character."""
        max_hp = self.stats.max_hit_points
        result = self.state.heal(healing)
        
        # Cap healing at max HP
        if self.state.current_hit_points > max_hp:
            actual_healing = healing - (self.state.current_hit_points - max_hp)
            self.state.current_hit_points = max_hp
            result["healing_applied"] = actual_healing
            result["new_hp"] = max_hp
            
        return result
    
    def validate_character(self) -> Dict[str, Any]:
        """Validate the complete character sheet."""
        core_validation = self.core.validate()
        
        # Additional validations
        issues = core_validation["issues"].copy()
        warnings = core_validation["warnings"].copy()
        
        # Check if HP is set properly
        if self.state.current_hit_points > self.stats.max_hit_points:
            issues.append("Current HP exceeds maximum HP")
        
        # Check for basic equipment
        if not self.state.armor and not self.state.weapons:
            warnings.append("Character has no armor or weapons equipped")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

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
# MODULE SUMMARY
# ============================================================================
# This module provides character sheet and data model classes:
#
# Core Data Classes:
# - CharacterCore: Core character data with ability scores, classes, and identity
# - CharacterState: Mutable character state (HP, equipment, conditions, currency)
# - CharacterStats: Calculated statistics (AC, max HP, proficiency bonus)
#
# Main Interface:
# - CharacterSheet: Combined character sheet with validation and management methods
#
# Utility Classes:
# - CharacterIterationCache: Manages character creation iterations and feedback
#
# Dependencies: core_models.py (AbilityScore, ASIManager, etc.)
#
# Key Features:
# - Complete D&D 5e character representation
# - Automatic stat calculation and caching
# - Damage/healing with proper HP management
# - Equipment and condition tracking
# - Character progression and validation
# ============================================================================