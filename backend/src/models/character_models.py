# ## **3. `character_models.py`**
# **Character sheet and data models**
# - **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`
# - **Purpose**: Complete D&D 5e 2024 character data structures and calculations
# - **Dependencies**: None (self-contained)
#
# COMPREHENSIVE CHARACTER SHEET IMPLEMENTATION:
# - CharacterCore: Core character build data (species, classes, abilities, feats)
# - CharacterState: Current gameplay state (HP, spell slots, conditions, equipment)
# - CharacterStats: Calculated/derived statistics (AC, spell save DC, proficiency bonus)
# - CharacterSheet: Main orchestrator that combines all three components

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CORE ENUMS AND CONSTANTS
# ============================================================================

class ProficiencyLevel(Enum):
    """Enumeration for proficiency levels in D&D 5e."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class FeatureType(Enum):
    """Types of character features."""
    SPECIES_TRAIT = "species_trait"
    CLASS_FEATURE = "class_feature"
    BACKGROUND_FEATURE = "background_feature"
    FEAT_ABILITY = "feat_ability"
    MAGIC_ITEM_PROPERTY = "magic_item_property"
    SPELL_ABILITY = "spell_ability"
    TEMPORARY_EFFECT = "temporary_effect"

class FeatureCategory(Enum):
    """Categories of character features for organization."""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    SPELLCASTING = "spellcasting"
    UTILITY = "utility"
    PASSIVE = "passive"
    DEFENSE = "defense"
    MOVEMENT = "movement"

class FeatureUsage(Enum):
    """How often a feature can be used."""
    ALWAYS = "always"
    PER_TURN = "per_turn"
    PER_SHORT_REST = "per_short_rest"
    PER_LONG_REST = "per_long_rest"
    PER_DAY = "per_day"
    LIMITED_USE = "limited_use"
    ONE_TIME = "one_time"

class AbilityScore:
    """Class representing a D&D ability score with its component values."""
    
    def __init__(self, base_score: int = 10):
        self.base_score: int = base_score
        self.bonus: int = 0
        self.set_score: Optional[int] = None
        self.stacking_bonuses: Dict[str, int] = {}
    
    @property
    def total_score(self) -> int:
        if self.set_score is not None:
            return self.set_score
        return max(1, min(30, self.base_score + self.bonus + sum(self.stacking_bonuses.values())))
    
    @property
    def modifier(self) -> int:
        return (self.total_score - 10) // 2

# ============================================================================
# CHARACTER CORE - FUNDAMENTAL CHARACTER DATA
# ============================================================================

class CharacterCore:
    """
    CORE INDEPENDENT VARIABLES - Set during character creation/leveling.
    
    These variables define the fundamental character build and rarely change
    except through leveling up or major story events.
    """
    
    def __init__(self, name: str = ""):
        # Basic Character Identity
        self.name: str = name
        self.species: str = ""
        self.species_variants: List[str] = []
        self.lineage: Optional[str] = None
        self.character_classes: Dict[str, int] = {}  # {"Fighter": 3, "Wizard": 2}
        self.subclasses: Dict[str, str] = {}  # {"Fighter": "Champion"}
        self.background: str = ""
        self.alignment_ethical: str = ""  # Lawful, Neutral, Chaotic
        self.alignment_moral: str = ""    # Good, Neutral, Evil
        
        # Appearance and Identity
        self.height: str = ""
        self.weight: str = ""
        self.age: int = 0
        self.eyes: str = ""
        self.hair: str = ""
        self.skin: str = ""
        self.gender: str = ""
        self.pronouns: str = ""
        self.size: str = "Medium"
        
        # Base Ability Scores
        self.strength: AbilityScore = AbilityScore(10)
        self.dexterity: AbilityScore = AbilityScore(10)
        self.constitution: AbilityScore = AbilityScore(10)
        self.intelligence: AbilityScore = AbilityScore(10)
        self.wisdom: AbilityScore = AbilityScore(10)
        self.charisma: AbilityScore = AbilityScore(10)
        
        # Core Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.weapon_proficiencies: Set[str] = set()
        self.armor_proficiencies: Set[str] = set()
        self.tool_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.languages: Set[str] = set()
        
        # Core Features and Traits
        self.species_traits: Dict[str, Any] = {}
        self.class_features: Dict[str, Any] = {}
        self.background_feature: str = ""
        self.feats: List[str] = []
        
        # Core Movement and Senses
        self.base_speed: int = 30
        self.base_vision_types: Dict[str, int] = {}  # {"darkvision": 60}
        self.base_movement_types: Dict[str, int] = {}  # {"swim": 30, "fly": 0}
        
        # Core Defenses
        self.base_damage_resistances: Set[str] = set()
        self.base_damage_immunities: Set[str] = set()
        self.base_damage_vulnerabilities: Set[str] = set()
        self.base_condition_immunities: Set[str] = set()
        
        # Core Spellcasting Abilities
        self.spellcasting_ability: Optional[str] = None
        self.spellcasting_classes: Dict[str, Dict[str, Any]] = {}
        self.ritual_casting_classes: Dict[str, bool] = {}
        
        # Character Background & Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory: str = ""
        
        # Hit Dice (base values from class)
        self.hit_dice: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Character Sheet Metadata
        self.creation_date: str = ""
        self.player_name: str = ""
        self.campaign: str = ""
        self.sources_used: Set[str] = set()
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level or first class)."""
        if not self.character_classes:
            return ""
        return max(self.character_classes.items(), key=lambda x: x[1])[0]
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        """Get the AbilityScore object for a specific ability."""
        ability_map = {
            "strength": self.strength, "str": self.strength,
            "dexterity": self.dexterity, "dex": self.dexterity,
            "constitution": self.constitution, "con": self.constitution,
            "intelligence": self.intelligence, "int": self.intelligence,
            "wisdom": self.wisdom, "wis": self.wisdom,
            "charisma": self.charisma, "cha": self.charisma
        }
        return ability_map.get(ability.lower())
    
    def validate(self) -> Dict[str, Any]:
        """Validate core character data."""
        issues = []
        warnings = []
        
        # Basic validation
        if not self.name.strip():
            warnings.append("Character name is empty")
        
        if not self.species:
            issues.append("Species is required")
        
        if not self.character_classes:
            issues.append("At least one character class is required")
        
        # Ability score validation
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability = self.get_ability_score(ability_name)
            if ability and (ability.total_score < 1 or ability.total_score > 30):
                issues.append(f"{ability_name.title()} score ({ability.total_score}) must be between 1 and 30")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def validate_character_data(self) -> Dict[str, Any]:
        """Alias for validate() for API compatibility."""
        return self.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "species_variants": self.species_variants,
            "lineage": self.lineage,
            "character_classes": self.character_classes,
            "subclasses": self.subclasses,
            "background": self.background,
            "alignment": [self.alignment_ethical, self.alignment_moral],
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            "proficiencies": {
                "skills": {k: v.value for k, v in self.skill_proficiencies.items()},
                "saving_throws": {k: v.value for k, v in self.saving_throw_proficiencies.items()},
                "weapons": list(self.weapon_proficiencies),
                "armor": list(self.armor_proficiencies),
                "tools": {k: v.value for k, v in self.tool_proficiencies.items()},
                "languages": list(self.languages)
            },
            "features": {
                "species_traits": self.species_traits,
                "class_features": self.class_features,
                "background_feature": self.background_feature,
                "feats": self.feats
            },
            "spellcasting": {
                "ability": self.spellcasting_ability,
                "classes": self.spellcasting_classes
            },
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
                "backstory": self.backstory
            }
        }

# ============================================================================
# CHARACTER STATE - CURRENT GAMEPLAY STATE
# ============================================================================

class CharacterState:
    """
    IN-GAME INDEPENDENT VARIABLES - Updated during gameplay.
    
    These variables track the character's current state and resources,
    changing frequently during gameplay sessions.
    """
    
    def __init__(self):
        # Experience Points
        self.experience_points: int = 0
        
        # Hit Points - Current Values
        self.current_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_point_maximum_modifier: int = 0
        
        # Hit Dice - Current Values
        self.hit_dice_remaining: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Spell Slots - Current Values
        self.spell_slots_total: Dict[int, int] = {}     # {1: 4, 2: 3, 3: 2}
        self.spell_slots_remaining: Dict[int, int] = {}  # {1: 2, 2: 1, 3: 0}
        self.spells_known: Dict[int, List[str]] = {}    # {0: ["Fire Bolt"], 1: ["Magic Missile"]}
        self.spells_prepared: List[str] = []
        self.ritual_book_spells: List[str] = []
        
        # Equipment - Current Items
        self.armor: Optional[str] = None
        self.shield: bool = False
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.magical_items: List[Dict[str, Any]] = []
        self.attuned_items: List[str] = []
        self.max_attunement_slots: int = 3
        
        # UUID-Based Allocated Items from Unified Catalog
        self.allocated_spells: Dict[str, List[Dict[str, Any]]] = {
            "spells_known": [], "spells_prepared": []
        }
        self.allocated_equipment: Dict[str, List[Dict[str, Any]]] = {
            "inventory": [], "equipped": []
        }
        self.all_allocated_items: List[Dict[str, Any]] = []
        
        # Currency
        self.currency: Dict[str, int] = {
            "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
        }
        
        # Conditions and Effects
        self.active_conditions: Dict[str, Dict[str, Any]] = {}
        self.exhaustion_level: int = 0
        
        # Temporary Defenses
        self.temp_damage_resistances: Set[str] = set()
        self.temp_damage_immunities: Set[str] = set()
        self.temp_damage_vulnerabilities: Set[str] = set()
        self.temp_condition_immunities: Set[str] = set()
        
        # Action Economy - Current State
        self.actions_per_turn: int = 1
        self.bonus_actions_per_turn: int = 1
        self.reactions_per_turn: int = 1
        self.actions_used: int = 0
        self.bonus_actions_used: int = 0
        self.reactions_used: int = 0
        
        # Companion Creatures
        self.beast_companion: Optional[Dict[str, Any]] = None
        
        # Adventure Notes
        self.notes: Dict[str, str] = {
            'organizations': "", 'allies': "", 'enemies': "", 'backstory': "", 'other': ""
        }
        
        # Timestamps
        self.last_updated: str = ""
        self.last_long_rest: Optional[str] = None
        self.last_short_rest: Optional[str] = None
    
    def reset_action_economy(self) -> None:
        """Reset action economy for a new turn."""
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.reactions_used = 0
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = {"temp_hp_damage": 0, "hp_damage": 0, "overkill": 0}
        
        # Apply to temporary HP first
        if self.temporary_hit_points > 0:
            temp_damage = min(damage, self.temporary_hit_points)
            self.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then to regular HP
        if damage > 0:
            self.current_hit_points -= damage
            result["hp_damage"] = damage
            
            if self.current_hit_points < 0:
                result["overkill"] = abs(self.current_hit_points)
                self.current_hit_points = 0
        
        return result
    
    def use_spell_slot(self, level: int) -> bool:
        """Use a spell slot of the specified level."""
        if level not in self.spell_slots_remaining or self.spell_slots_remaining[level] <= 0:
            return False
        
        self.spell_slots_remaining[level] -= 1
        return True
    
    def add_condition(self, condition: str, duration: Optional[int] = None, 
                     source: Optional[str] = None) -> None:
        """Apply a condition to the character."""
        self.active_conditions[condition] = {
            "duration": duration,
            "source": source,
            "applied_at": datetime.now().isoformat()
        }
    
    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the character."""
        if condition in self.active_conditions:
            del self.active_conditions[condition]
            return True
        return False
    
    def take_short_rest(self, hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Perform a short rest."""
        result = {"hp_recovered": 0, "hit_dice_spent": {}}
        
        if hit_dice_spent:
            # Process hit dice healing
            for die_type, count in hit_dice_spent.items():
                available = self.hit_dice_remaining.get(die_type, 0)
                if available >= count:
                    self.hit_dice_remaining[die_type] = available - count
                    result["hit_dice_spent"][die_type] = count
                    # HP recovery calculation would need CharacterStats
        
        self.last_short_rest = datetime.now().isoformat()
        return result
    
    def take_long_rest(self) -> Dict[str, Any]:
        """Perform a long rest."""
        result = {"hp_recovered": 0, "spell_slots_recovered": {}, "hit_dice_recovered": {}}
        
        # Restore spell slots
        for level, total in self.spell_slots_total.items():
            old_slots = self.spell_slots_remaining.get(level, 0)
            self.spell_slots_remaining[level] = total
            result["spell_slots_recovered"][level] = total - old_slots
        
        # Reduce exhaustion by 1
        if self.exhaustion_level > 0:
            self.exhaustion_level -= 1
        
        self.last_long_rest = datetime.now().isoformat()
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_points": self.experience_points,
            "hit_points": {
                "current": self.current_hit_points,
                "temporary": self.temporary_hit_points,
                "max_modifier": self.hit_point_maximum_modifier
            },
            "spell_slots": {
                "total": self.spell_slots_total,
                "remaining": self.spell_slots_remaining
            },
            "spells": {
                "known": self.spells_known,
                "prepared": self.spells_prepared,
                "ritual_book": self.ritual_book_spells
            },
            "equipment": {
                "armor": self.armor,
                "shield": self.shield,
                "weapons": self.weapons,
                "items": self.equipment,
                "magical_items": self.magical_items,
                "attuned": self.attuned_items
            },
            # UUID-based allocated items from unified catalog
            "allocated_spells": self.allocated_spells,
            "allocated_equipment": self.allocated_equipment,
            "all_allocated_items": self.all_allocated_items,
            "currency": self.currency,
            "conditions": {
                "active": self.active_conditions,
                "exhaustion": self.exhaustion_level
            },
            "action_economy": {
                "actions_used": self.actions_used,
                "bonus_actions_used": self.bonus_actions_used,
                "reactions_used": self.reactions_used
            },
            "notes": self.notes,
            "timestamps": {
                "last_updated": self.last_updated,
                "last_long_rest": self.last_long_rest,
                "last_short_rest": self.last_short_rest
            }
        }

# ============================================================================
# CHARACTER STATS - CALCULATED VALUES
# ============================================================================

class CharacterStats:
    """
    DEPENDENT VARIABLES - Calculated from other variables.
    
    These variables are computed based on core character data and current state.
    They should be recalculated whenever their dependencies change.
    """
    
    def __init__(self, core: CharacterCore, state: CharacterState):
        self.core = core
        self.state = state
        
        # Cached calculated values
        self._proficiency_bonus: Optional[int] = None
        self._armor_class: Optional[int] = None
        self._max_hit_points: Optional[int] = None
        self._initiative: Optional[int] = None
        self._spell_save_dc: Optional[int] = None
        self._spell_attack_bonus: Optional[int] = None
        self._passive_perception: Optional[int] = None
        self._passive_investigation: Optional[int] = None
        self._passive_insight: Optional[int] = None
        
        # Available actions (computed based on class features, etc.)
        self._available_actions: Dict[str, Dict[str, Any]] = {}
        self._available_reactions: Dict[str, Dict[str, Any]] = {}
        
        # Dependencies tracking for cache invalidation
        self._last_core_hash: Optional[int] = None
        self._last_state_hash: Optional[int] = None
    
    def invalidate_cache(self) -> None:
        """Invalidate all cached calculations."""
        self._proficiency_bonus = None
        self._armor_class = None
        self._max_hit_points = None
        self._initiative = None
        self._spell_save_dc = None
        self._spell_attack_bonus = None
        self._passive_perception = None
        self._passive_investigation = None
        self._passive_insight = None
        self._available_actions = {}
        self._available_reactions = {}
    
    def _needs_recalculation(self) -> bool:
        """Check if recalculation is needed based on dependencies."""
        # Simple hash-based dependency tracking
        core_hash = hash(str(self.core.to_dict()))
        state_hash = hash(str(self.state.to_dict()))
        
        if (self._last_core_hash != core_hash or 
            self._last_state_hash != state_hash):
            self._last_core_hash = core_hash
            self._last_state_hash = state_hash
            return True
        return False
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        if self._proficiency_bonus is None or self._needs_recalculation():
            level = self.core.total_level
            self._proficiency_bonus = 2 + ((level - 1) // 4)
        return self._proficiency_bonus
    
    @property
    def armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        if self._armor_class is None or self._needs_recalculation():
            self._armor_class = self._calculate_armor_class()
        return self._armor_class
    
    @property
    def max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if self._max_hit_points is None or self._needs_recalculation():
            self._max_hit_points = self._calculate_max_hit_points()
        return self._max_hit_points
    
    @property
    def initiative(self) -> int:
        """Calculate initiative bonus."""
        if self._initiative is None or self._needs_recalculation():
            self._initiative = self._calculate_initiative()
        return self._initiative
    
    @property
    def spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if self._spell_save_dc is None or self._needs_recalculation():
            self._spell_save_dc = self._calculate_spell_save_dc()
        return self._spell_save_dc
    
    @property
    def spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if self._spell_attack_bonus is None or self._needs_recalculation():
            self._spell_attack_bonus = self._calculate_spell_attack_bonus()
        return self._spell_attack_bonus
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive Perception score."""
        if self._passive_perception is None or self._needs_recalculation():
            self._passive_perception = self._calculate_passive_perception()
        return self._passive_perception
    
    def _calculate_armor_class(self) -> int:
        """Internal method to calculate armor class."""
        base_ac = 10
        dex_mod = self.core.dexterity.modifier
        
        # Check for worn armor
        if self.state.armor:
            armor_type = self.state.armor.lower()
            
            # Light armor
            if any(a in armor_type for a in ["padded", "leather"]):
                if "studded" in armor_type:
                    base_ac = 12 + dex_mod
                else:
                    base_ac = 11 + dex_mod
            
            # Medium armor
            elif any(a in armor_type for a in ["chain shirt", "scale", "breastplate", "half plate"]):
                if "chain shirt" in armor_type:
                    base_ac = 13 + min(dex_mod, 2)
                elif "scale" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "breastplate" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "half plate" in armor_type:
                    base_ac = 15 + min(dex_mod, 2)
            
            # Heavy armor
            elif any(a in armor_type for a in ["ring mail", "chain mail", "splint", "plate"]):
                if "ring mail" in armor_type:
                    base_ac = 14
                elif "chain mail" in armor_type:
                    base_ac = 16
                elif "splint" in armor_type:
                    base_ac = 17
                elif "plate" in armor_type:
                    base_ac = 18
        else:
            # Unarmored Defense
            if "Barbarian" in self.core.character_classes:
                con_mod = self.core.constitution.modifier
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
            
            if "Monk" in self.core.character_classes:
                wis_mod = self.core.wisdom.modifier
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self.state.shield:
            base_ac += 2
        
        return base_ac
    
    def _calculate_max_hit_points(self) -> int:
        """Internal method to calculate maximum hit points."""
        if not self.core.character_classes:
            return 1
        
        con_mod = self.core.constitution.modifier
        total = 0
        
        hit_die_sizes = {
            "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
            "Wizard": 6, "Sorcerer": 6
        }
        
        for class_name, level in self.core.character_classes.items():
            if level <= 0:
                continue
                
            hit_die = hit_die_sizes.get(class_name, 8)
            
            # First level is max hit die + CON
            if class_name == self.core.primary_class:
                total += hit_die + con_mod
                remaining_levels = level - 1
            else:
                remaining_levels = level
            
            # Average for remaining levels
            total += remaining_levels * ((hit_die // 2) + 1 + con_mod)
        
        # Add modifiers from state
        total += self.state.hit_point_maximum_modifier
        
        return max(1, total)
    
    def _calculate_initiative(self) -> int:
        """Internal method to calculate initiative."""
        dex_mod = self.core.dexterity.modifier
        bonus = 0
        
        # Check for feats and features
        if "Alert" in self.core.feats:
            bonus += 5
        
        if "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:  # Jack of All Trades
                bonus += self.proficiency_bonus // 2
        
        return dex_mod + bonus
    
    def _calculate_spell_save_dc(self) -> int:
        """Internal method to calculate spell save DC."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return 8 + self.proficiency_bonus + ability_mod
    
    def _calculate_spell_attack_bonus(self) -> int:
        """Internal method to calculate spell attack bonus."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return self.proficiency_bonus + ability_mod
    
    def _calculate_passive_perception(self) -> int:
        """Internal method to calculate passive Perception."""
        wis_mod = self.core.wisdom.modifier
        prof_bonus = 0
        
        perception_prof = self.core.skill_proficiencies.get("Perception", ProficiencyLevel.NONE)
        if perception_prof == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif perception_prof == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        feat_bonus = 5 if "Observant" in self.core.feats else 0
        
        return 10 + wis_mod + prof_bonus + feat_bonus
    
    def calculate_skill_bonus(self, skill_name: str) -> int:
        """Calculate bonus for a specific skill check."""
        skill_abilities = {
            "Athletics": "strength", "Acrobatics": "dexterity",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity",
            "Arcana": "intelligence", "History": "intelligence",
            "Investigation": "intelligence", "Nature": "intelligence", "Religion": "intelligence",
            "Animal Handling": "wisdom", "Insight": "wisdom", "Medicine": "wisdom",
            "Perception": "wisdom", "Survival": "wisdom",
            "Deception": "charisma", "Intimidation": "charisma",
            "Performance": "charisma", "Persuasion": "charisma"
        }
        
        if skill_name not in skill_abilities:
            return 0
        
        ability = skill_abilities[skill_name]
        ability_mod = self.core.get_ability_score(ability).modifier
        
        # Check proficiency
        prof_level = self.core.skill_proficiencies.get(skill_name, ProficiencyLevel.NONE)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Jack of All Trades for non-proficient skills
        if prof_level == ProficiencyLevel.NONE and "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:
                prof_bonus = self.proficiency_bonus // 2
        
        return ability_mod + prof_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calculated stats to dictionary."""
        return {
            "proficiency_bonus": self.proficiency_bonus,
            "armor_class": self.armor_class,
            "max_hit_points": self.max_hit_points,
            "initiative": self.initiative,
            "spell_save_dc": self.spell_save_dc,
            "spell_attack_bonus": self.spell_attack_bonus,
            "passive_perception": self.passive_perception,
            "available_actions": self._available_actions,
            "available_reactions": self._available_reactions
        }

# ============================================================================
# CHARACTER SHEET - MAIN ORCHESTRATOR
# ============================================================================

class CharacterSheet:
    """
    Main character sheet class that orchestrates the three sub-components:
    - CharacterCore: Core character build data
    - CharacterState: Current gameplay state
    - CharacterStats: Calculated/derived statistics
    """
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
        
        # Validation tracking
        self._last_validation_result: Optional[Dict[str, Any]] = None
        self._validation_timestamp: Optional[str] = None
    
    def validate_against_rules(self, use_unified: bool = True) -> Dict[str, Any]:
        """Validate entire character sheet against D&D rules."""
        try:
            if use_unified:
                try:
                    from unified_validator import create_unified_validator
                    validator = create_unified_validator()
                    character_data = self.to_dict()
                    result = validator.validate_character(character_data, self)
                except ImportError:
                    # Fall back to core validation if unified validator not available
                    core_validation = self.core.validate()
                    result = {
                        "overall_valid": core_validation["valid"],
                        "summary": {
                            "total_issues": len(core_validation["issues"]),
                            "total_warnings": len(core_validation["warnings"]),
                            "validators_run": 1,
                            "validators_passed": 1 if core_validation["valid"] else 0
                        },
                        "all_issues": core_validation["issues"],
                        "all_warnings": core_validation["warnings"],
                        "detailed_results": {"core": core_validation}
                    }
            else:
                # Fallback validation
                core_validation = self.core.validate()
                result = {
                    "overall_valid": core_validation["valid"],
                    "summary": {
                        "total_issues": len(core_validation["issues"]),
                        "total_warnings": len(core_validation["warnings"]),
                        "validators_run": 1,
                        "validators_passed": 1 if core_validation["valid"] else 0
                    },
                    "all_issues": core_validation["issues"],
                    "all_warnings": core_validation["warnings"],
                    "detailed_results": {"core": core_validation}
                }
            
            self._last_validation_result = result
            return result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "overall_valid": False,
                "summary": {"total_issues": 1, "validators_run": 0, "validators_passed": 0},
                "all_issues": [f"Validation error: {str(e)}"],
                "all_warnings": [],
                "detailed_results": {}
            }
    
    def calculate_all_derived_stats(self) -> None:
        """Trigger recalculation of all derived statistics."""
        self.stats.invalidate_cache()
        # Accessing properties will trigger recalculation
        _ = self.stats.proficiency_bonus
        _ = self.stats.armor_class
        _ = self.stats.max_hit_points
        _ = self.stats.initiative
    
    # Convenience properties that delegate to appropriate sub-components
    @property
    def name(self) -> str:
        return self.core.name
    
    @property
    def total_level(self) -> int:
        return self.core.total_level
    
    @property
    def armor_class(self) -> int:
        return self.stats.armor_class
    
    @property
    def current_hit_points(self) -> int:
        return self.state.current_hit_points
    
    @property
    def max_hit_points(self) -> int:
        return self.stats.max_hit_points
    
    # Convenience methods for common operations
    def level_up(self, class_name: str) -> None:
        """Level up in the specified class."""
        current_level = self.core.character_classes.get(class_name, 0)
        self.core.character_classes[class_name] = current_level + 1
        self.calculate_all_derived_stats()
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = self.state.take_damage(damage)
        # Check if character died
        if self.state.current_hit_points == 0:
            # Handle death/unconsciousness
            self.state.add_condition("unconscious")
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character."""
        old_hp = self.state.current_hit_points
        self.state.current_hit_points = min(self.stats.max_hit_points, old_hp + healing)
        healed = self.state.current_hit_points - old_hp
        
        # Remove unconscious condition if healed above 0
        if self.state.current_hit_points > 0 and "unconscious" in self.state.active_conditions:
            self.state.remove_condition("unconscious")
        
        return healed
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Create a comprehensive character summary."""
        return {
            # Core identity
            "name": self.core.name,
            "species": self.core.species,
            "level": self.core.total_level,
            "classes": self.core.character_classes,
            "background": self.core.background,
            
            # Ability scores
            "ability_scores": {
                "strength": self.core.strength.total_score,
                "dexterity": self.core.dexterity.total_score,
                "constitution": self.core.constitution.total_score,
                "intelligence": self.core.intelligence.total_score,
                "wisdom": self.core.wisdom.total_score,
                "charisma": self.core.charisma.total_score
            },
            
            # Combat stats
            "armor_class": self.stats.armor_class,
            "hit_points": {
                "current": self.state.current_hit_points,
                "max": self.stats.max_hit_points,
                "temp": self.state.temporary_hit_points
            },
            "initiative": self.stats.initiative,
            "proficiency_bonus": self.stats.proficiency_bonus,
            
            # Current state
            "conditions": list(self.state.active_conditions.keys()),
            "exhaustion_level": self.state.exhaustion_level,
            
            # Equipment
            "armor": self.state.armor,
            "shield": self.state.shield,
            "weapons": self.state.weapons,
            
            # Validation
            "is_valid": self._last_validation_result.get("overall_valid", False) if self._last_validation_result else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire character sheet to dictionary."""
        return {
            "core": self.core.to_dict(),
            "state": self.state.to_dict(),
            "stats": self.stats.to_dict(),
            "validation": self._last_validation_result
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load character sheet from dictionary."""
        if "core" in data:
            # Load core data
            core_data = data["core"]
            self.core.name = core_data.get("name", "")
            self.core.species = core_data.get("species", "")
            # ... load other core data
        
        if "state" in data:
            # Load state data
            state_data = data["state"]
            self.state.current_hit_points = state_data.get("hit_points", {}).get("current", 0)
            # ... load other state data
        
        # Recalculate stats after loading
        self.calculate_all_derived_stats()

# ============================================================================
# API COMPATIBILITY ALIASES
# ============================================================================

# For backward compatibility with existing API endpoints
Character = CharacterSheet  # Main character class alias
