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
    MagicItemManager
)

# ============================================================================
# D&D 5E 2024 CONDITIONS
# ============================================================================

class DnDCondition(Enum):
    """D&D 5e 2024 conditions with their effects."""
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"

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
    
    @property
    def total_level(self) -> int:
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def level(self) -> int:
        """Calculate total character level from all classes."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CharacterCore to dictionary representation."""
        return {
            "name": self.name,
            "species": self.species,
            "level": self.level,
            "classes": self.character_classes,
            "background": self.background,
            "alignment": self.alignment,
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            "backstory": self.backstory,
            "detailed_backstory": self.detailed_backstory,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "proficiencies": {
                "skills": dict(self.skill_proficiencies),
                "saving_throws": dict(self.saving_throw_proficiencies),
                "armor": self.armor_proficiency,
                "weapons": self.weapon_proficiency,
                "tools": self.tool_proficiency,
                "languages": self.languages
            }
        }

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
        
        # Enhanced Conditions (D&D 5e 2024)
        self.active_conditions: Dict[str, Dict[str, Any]] = {}
        self.exhaustion_level = 0
        
        # Journal tracking
        self.journal_entries: List[Dict[str, Any]] = []
        
        # Currency
        self.currency = {"copper": 0, "silver": 0, "gold": 0, "platinum": 0}
    
    # ============================================================================
    # HIT POINT MANAGEMENT
    # ============================================================================
    
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
    
    # ============================================================================
    # ENHANCED CONDITION MANAGEMENT (D&D 5e 2024)
    # ============================================================================
    
    def add_condition(self, condition: DnDCondition, duration: str = "indefinite", 
                     save_dc: int = 0, save_ability: str = "", source: str = ""):
        """Add a D&D 5e 2024 condition to the character."""
        self.active_conditions[condition.value] = {
            "condition": condition,
            "duration": duration,
            "save_dc": save_dc,
            "save_ability": save_ability,
            "source": source,
            "applied_at": datetime.now().isoformat()
        }
        logger.info(f"Applied condition: {condition.value}")
    
    def remove_condition(self, condition: DnDCondition):
        """Remove a condition from the character."""
        condition_key = condition.value
        if condition_key in self.active_conditions:
            del self.active_conditions[condition_key]
            logger.info(f"Removed condition: {condition_key}")
    
    def has_condition(self, condition: DnDCondition) -> bool:
        """Check if character has a specific condition."""
        return condition.value in self.active_conditions
    
    def get_condition_effects(self) -> Dict[str, Any]:
        """Get the mechanical effects of all active conditions."""
        effects = {
            "disadvantage_on": [],
            "advantage_on": [],
            "auto_fail": [],
            "speed_modifications": 0,
            "d20_penalty": 0,
            "special_effects": []
        }
        
        for condition_name, condition_data in self.active_conditions.items():
            condition = condition_data["condition"]
            
            if condition == DnDCondition.BLINDED:
                effects["disadvantage_on"].extend(["attack_rolls"])
                effects["auto_fail"].extend(["sight_based_checks"])
                effects["special_effects"].append("Attacks against you have advantage")
                
            elif condition == DnDCondition.CHARMED:
                effects["special_effects"].append("Cannot attack charmer or target with harmful effects")
                
            elif condition == DnDCondition.DEAFENED:
                effects["auto_fail"].extend(["hearing_based_checks"])
                
            elif condition == DnDCondition.FRIGHTENED:
                effects["disadvantage_on"].extend(["attack_rolls", "ability_checks"])
                effects["special_effects"].append("Cannot move closer to fear source")
                
            elif condition == DnDCondition.GRAPPLED:
                effects["disadvantage_on"].extend(["attacks_vs_non_grappler"])
                
            elif condition == DnDCondition.INCAPACITATED:
                effects["special_effects"].append("Cannot take actions or reactions")
                
            elif condition == DnDCondition.INVISIBLE:
                effects["advantage_on"].extend(["attack_rolls"])
                effects["special_effects"].append("Attacks against you have disadvantage")
                
            elif condition == DnDCondition.PARALYZED:
                effects["special_effects"].extend([
                    "Incapacitated", "Cannot move or speak",
                    "Auto-fail Strength and Dexterity saves",
                    "Attacks against you have advantage",
                    "Hits within 5 feet are critical hits"
                ])
                
            elif condition == DnDCondition.PETRIFIED:
                effects["special_effects"].extend([
                    "Transformed to solid inanimate substance",
                    "Incapacitated", "Cannot move or speak",
                    "Resistance to all damage",
                    "Immune to poison and disease"
                ])
                
            elif condition == DnDCondition.POISONED:
                effects["disadvantage_on"].extend(["attack_rolls", "ability_checks"])
                
            elif condition == DnDCondition.PRONE:
                effects["speed_modifications"] = 0  # Speed becomes 0
                effects["special_effects"].extend([
                    "Attacks within 5 feet have advantage",
                    "Ranged attacks have disadvantage",
                    "Disadvantage on ranged attacks"
                ])
                
            elif condition == DnDCondition.RESTRAINED:
                effects["speed_modifications"] = 0  # Speed becomes 0
                effects["disadvantage_on"].extend(["attack_rolls", "dexterity_saves"])
                effects["special_effects"].append("Attacks against you have advantage")
                
            elif condition == DnDCondition.STUNNED:
                effects["special_effects"].extend([
                    "Incapacitated", "Cannot move or speak",
                    "Auto-fail Strength and Dexterity saves"
                ])
                
            elif condition == DnDCondition.UNCONSCIOUS:
                effects["special_effects"].extend([
                    "Incapacitated", "Cannot move or speak", "Unaware of surroundings",
                    "Drops held items", "Falls prone",
                    "Auto-fail Strength and Dexterity saves",
                    "Attacks against you have advantage",
                    "Hits within 5 feet are critical hits"
                ])
        
        # Add exhaustion effects
        if self.exhaustion_level > 0:
            exhaustion_effects = ExhaustionLevel.get_effects(self.exhaustion_level)
            effects["d20_penalty"] = exhaustion_effects["d20_penalty"]
            effects["speed_modifications"] += exhaustion_effects["speed_penalty"]
            
            if ExhaustionLevel.is_dead(self.exhaustion_level):
                effects["special_effects"].append("CHARACTER IS DEAD")
        
        return effects
    
    # ============================================================================
    # EXHAUSTION MANAGEMENT (D&D 5e 2024)
    # ============================================================================
    
    def add_exhaustion(self, levels: int = 1) -> Dict[str, Any]:
        """Add exhaustion levels."""
        old_level = self.exhaustion_level
        self.exhaustion_level = min(self.exhaustion_level + levels, 6)
        
        result = {
            "old_level": old_level,
            "new_level": self.exhaustion_level,
            "is_dead": ExhaustionLevel.is_dead(self.exhaustion_level),
            "effects": ExhaustionLevel.get_effects(self.exhaustion_level)
        }
        
        logger.info(f"Added {levels} exhaustion level(s). New level: {self.exhaustion_level}")
        return result
    
    def remove_exhaustion(self, levels: int = 1, method: str = "long_rest") -> Dict[str, Any]:
        """Remove exhaustion levels."""
        old_level = self.exhaustion_level
        
        if method == "potion_of_vitality":
            # Potion of Vitality removes all exhaustion
            self.exhaustion_level = 0
        else:
            # Long rest or Greater Restoration removes 1 level
            self.exhaustion_level = max(self.exhaustion_level - levels, 0)
        
        result = {
            "old_level": old_level,
            "new_level": self.exhaustion_level,
            "method": method,
            "effects": ExhaustionLevel.get_effects(self.exhaustion_level)
        }
        
        logger.info(f"Removed exhaustion via {method}. New level: {self.exhaustion_level}")
        return result
    
    # ============================================================================
    # JOURNAL MANAGEMENT
    # ============================================================================
    
    def add_journal_entry(self, entry: str, session_date: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> None:
        """Add a journal entry."""
        journal_entry = {
            "entry": entry,
            "timestamp": datetime.now().isoformat(),
            "session_date": session_date or datetime.now().strftime("%Y-%m-%d"),
            "tags": tags or []
        }
        self.journal_entries.append(journal_entry)
        logger.info("Added journal entry")
    
    def get_journal_entries(self) -> List[Dict[str, Any]]:
        """Get all journal entries."""
        return self.journal_entries.copy()
    
    def clear_journal(self) -> None:
        """Clear all journal entries."""
        self.journal_entries.clear()
        logger.info("Cleared all journal entries")
    
    def get_journal_summary(self) -> Dict[str, Any]:
        """Get journal summary for character evolution analysis."""
        if not self.journal_entries:
            return {"total_entries": 0, "themes": [], "character_evolution": ""}
        
        # Simple analysis - could be enhanced with AI
        all_text = " ".join([entry["entry"] for entry in self.journal_entries])
        
        # Basic keyword analysis for character themes
        combat_words = ["fight", "battle", "attack", "combat", "weapon", "armor"]
        stealth_words = ["sneak", "hide", "assassin", "shadow", "quiet", "stealth"]
        social_words = ["persuade", "negotiate", "charm", "diplomat", "talk", "convince"]
        magic_words = ["spell", "magic", "cast", "ritual", "arcane", "divine"]
        
        themes = []
        text_lower = all_text.lower()
        
        if any(word in text_lower for word in combat_words):
            themes.append("Combat-focused")
        if any(word in text_lower for word in stealth_words):
            themes.append("Stealth-oriented")
        if any(word in text_lower for word in social_words):
            themes.append("Social interactions")
        if any(word in text_lower for word in magic_words):
            themes.append("Magic user")
        
        return {
            "total_entries": len(self.journal_entries),
            "themes": themes,
            "character_evolution": f"Based on {len(self.journal_entries)} journal entries, character shows tendencies toward: {', '.join(themes) if themes else 'general adventuring'}"
        }
    
    # ============================================================================
    # EQUIPMENT MANAGEMENT
    # ============================================================================
    
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
    # GETTER METHODS FOR API ACCESS
    # ============================================================================
    
    def get_current_hit_points(self) -> int:
        """Get current hit points."""
        return self.current_hit_points
    
    def get_temporary_hit_points(self) -> int:
        """Get temporary hit points."""
        return self.temporary_hit_points
    
    def get_armor(self) -> str:
        """Get equipped armor."""
        return self.armor
    
    def get_weapons(self) -> List[Dict[str, Any]]:
        """Get equipped weapons."""
        return self.weapons.copy()
    
    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment."""
        return self.equipment.copy()
    
    def get_active_conditions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active conditions."""
        return self.active_conditions.copy()
    
    def get_exhaustion_level(self) -> int:
        """Get current exhaustion level."""
        return self.exhaustion_level
    
    def get_currency(self) -> Dict[str, int]:
        """Get currency amounts."""
        return self.currency.copy()
    
    # ============================================================================
    # SETTER METHODS FOR API ACCESS
    # ============================================================================
    
    def set_current_hit_points(self, hp: int) -> None:
        """Set current hit points."""
        self.current_hit_points = max(0, hp)
    
    def set_temporary_hit_points(self, temp_hp: int) -> None:
        """Set temporary hit points."""
        self.temporary_hit_points = max(0, temp_hp)
    
    def set_armor(self, armor: str) -> None:
        """Set equipped armor."""
        self.armor = armor
    
    def set_currency(self, currency: Dict[str, int]) -> None:
        """Set currency amounts."""
        self.currency.update(currency)

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
    """Main character sheet combining all components with journal tracking."""
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
        
        # Add initial journal entry for new characters
        if name:
            self.state.add_journal_entry(
                f"Character '{name}' has been created and begins their adventure!",
                tags=["character_creation", "beginning"]
            )
    
    # ============================================================================
    # COMPREHENSIVE GETTER METHODS FOR API
    # ============================================================================
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get complete character summary including journal."""
        return {
            "name": self.core.name,
            "species": self.core.species,
            "level": self.core.total_level,
            "classes": self.core.character_classes,
            "background": self.core.background,
            "alignment": self.core.alignment,
            "ability_scores": self.core.get_ability_scores(),
            "ability_modifiers": self.core.get_ability_modifiers(),
            "ac": self.stats.armor_class,
            "hp": {
                "current": self.state.current_hit_points,
                "max": self.stats.max_hit_points,
                "temp": self.state.temporary_hit_points
            },
            "proficiency_bonus": self.stats.proficiency_bonus,
            "proficiencies": self.core.get_proficiencies(),
            "personality": {
                "traits": self.core.get_personality_traits(),
                "ideals": self.core.get_ideals(),
                "bonds": self.core.get_bonds(),
                "flaws": self.core.get_flaws()
            },
            "backstory": self.core.get_backstory(),
            "detailed_backstory": self.core.get_detailed_backstory(),
            "custom_content": self.core.custom_content_used,
            "equipment": {
                "armor": self.state.armor,
                "weapons": self.state.weapons,
                "items": self.state.equipment
            },
            "conditions": self.state.get_active_conditions(),
            "condition_effects": self.state.get_condition_effects(),
            "exhaustion_level": self.state.exhaustion_level,
            "exhaustion_effects": ExhaustionLevel.get_effects(self.state.exhaustion_level),
            "currency": self.state.get_currency(),
            "journal": {
                "entries": self.state.get_journal_entries(),
                "summary": self.state.get_journal_summary()
            }
        }
    
    # Individual getter methods for specific data
    def get_name(self) -> str:
        return self.core.get_name()
    
    def get_species(self) -> str:
        return self.core.get_species()
    
    def get_level(self) -> int:
        return self.core.total_level
    
    def get_classes(self) -> Dict[str, int]:
        return self.core.get_character_classes()
    
    def get_background(self) -> str:
        return self.core.get_background()
    
    def get_alignment(self) -> List[str]:
        return self.core.get_alignment()
    
    def get_ability_scores(self) -> Dict[str, int]:
        return self.core.get_ability_scores()
    
    def get_ability_modifiers(self) -> Dict[str, int]:
        return self.core.get_ability_modifiers()
    
    def get_armor_class(self) -> int:
        return self.stats.armor_class
    
    def get_hit_points(self) -> Dict[str, int]:
        return {
            "current": self.state.get_current_hit_points(),
            "max": self.stats.max_hit_points,
            "temp": self.state.get_temporary_hit_points()
        }
    
    def get_proficiency_bonus(self) -> int:
        return self.stats.proficiency_bonus
    
    def get_proficiencies(self) -> Dict[str, Any]:
        return self.core.get_proficiencies()
    
    def get_personality(self) -> Dict[str, List[str]]:
        return {
            "traits": self.core.get_personality_traits(),
            "ideals": self.core.get_ideals(),
            "bonds": self.core.get_bonds(),
            "flaws": self.core.get_flaws()
        }
    
    def get_backstory(self) -> str:
        return self.core.get_backstory()
    
    def get_detailed_backstory(self) -> Dict[str, str]:
        return self.core.get_detailed_backstory()
    
    def get_equipment(self) -> Dict[str, Any]:
        return {
            "armor": self.state.get_armor(),
            "weapons": self.state.get_weapons(),
            "items": self.state.get_equipment()
        }
    
    def get_conditions(self) -> Dict[str, Dict[str, Any]]:
        return self.state.get_active_conditions()
    
    def get_condition_effects(self) -> Dict[str, Any]:
        return self.state.get_condition_effects()
    
    def get_exhaustion_level(self) -> int:
        return self.state.get_exhaustion_level()
    
    def get_exhaustion_effects(self) -> Dict[str, Any]:
        return ExhaustionLevel.get_effects(self.state.exhaustion_level)
    
    def get_currency(self) -> Dict[str, int]:
        return self.state.get_currency()
    
    def get_journal_entries(self) -> List[Dict[str, Any]]:
        return self.state.get_journal_entries()
    
    def get_journal_summary(self) -> Dict[str, Any]:
        return self.state.get_journal_summary()
    
    # ============================================================================
    # SETTER METHODS FOR GAMEPLAY STATE (API ACCESSIBLE)
    # ============================================================================
    
    def set_current_hit_points(self, hp: int) -> None:
        """Set current hit points."""
        max_hp = self.stats.max_hit_points
        self.state.set_current_hit_points(min(hp, max_hp))
    
    def set_temporary_hit_points(self, temp_hp: int) -> None:
        """Set temporary hit points."""
        self.state.set_temporary_hit_points(temp_hp)
    
    def set_armor(self, armor: str) -> None:
        """Set equipped armor."""
        self.state.set_armor(armor)
        self.stats.invalidate_cache()  # Recalculate AC
    
    def set_currency(self, currency: Dict[str, int]) -> None:
        """Set currency amounts."""
        self.state.set_currency(currency)
    
    def add_journal_entry(self, entry: str, session_date: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> None:
        """Add a journal entry."""
        self.state.add_journal_entry(entry, session_date, tags)
    
    def clear_journal(self) -> None:
        """Clear all journal entries."""
        self.state.clear_journal()
    
    def add_condition(self, condition: DnDCondition, duration: str = "indefinite", 
                     save_dc: int = 0, save_ability: str = "", source: str = "") -> None:
        """Add a condition to the character."""
        self.state.add_condition(condition, duration, save_dc, save_ability, source)
    
    def remove_condition(self, condition: DnDCondition) -> None:
        """Remove a condition from the character."""
        self.state.remove_condition(condition)
    
    def add_exhaustion(self, levels: int = 1) -> Dict[str, Any]:
        """Add exhaustion levels."""
        return self.state.add_exhaustion(levels)
    
    def remove_exhaustion(self, levels: int = 1, method: str = "long_rest") -> Dict[str, Any]:
        """Remove exhaustion levels."""
        return self.state.remove_exhaustion(levels, method)
    
    def add_equipment_item(self, item: Dict[str, Any]) -> None:
        """Add equipment item."""
        self.state.add_equipment(item)
    
    def add_weapon(self, weapon: Dict[str, Any]) -> None:
        """Add weapon."""
        self.state.add_weapon(weapon)
    
    # ============================================================================
    # ENHANCED GAMEPLAY METHODS
    # ============================================================================
    
    def generate_sheet(self) -> Dict[str, Any]:
        """Generate a complete character sheet - alias for get_character_summary."""
        return self.get_character_summary()
    
    def calculate_all_derived_stats(self):
        """Recalculate all derived statistics."""
        self.stats.invalidate_cache()
        if self.state.current_hit_points == 0:  # Only set if not already set
            self.state.current_hit_points = self.stats.max_hit_points
    
    def level_up(self, class_name: str, asi_choice: Optional[Dict[str, Any]] = None):
        """Level up the character in the specified class."""
        old_level = self.core.character_classes.get(class_name, 0)
        self.core.level_up(class_name, asi_choice)
        new_level = self.core.character_classes.get(class_name, 0)
        
        # Add journal entry for level up
        self.state.add_journal_entry(
            f"Leveled up in {class_name} from level {old_level} to {new_level}!",
            tags=["level_up", class_name.lower()]
        )
        
        self.calculate_all_derived_stats()
        logger.info(f"Character {self.core.name} leveled up to {class_name} level {new_level}")
    
    def take_damage(self, damage: int, source: str = "") -> Dict[str, int]:
        """Apply damage to the character."""
        max_hp = self.stats.max_hit_points
        result = self.state.take_damage(damage)
        
        # Ensure current HP doesn't exceed max HP after calculation
        if self.state.current_hit_points > max_hp:
            self.state.current_hit_points = max_hp
        
        # Add journal entry for significant damage
        if damage > 0:
            self.state.add_journal_entry(
                f"Took {damage} damage{' from ' + source if source else ''}. HP: {self.state.current_hit_points}/{max_hp}",
                tags=["combat", "damage"]
            )
            
        return result
    
    def heal(self, healing: int, source: str = "") -> Dict[str, int]:
        """Heal the character."""
        max_hp = self.stats.max_hit_points
        result = self.state.heal(healing)
        
        # Cap healing at max HP
        if self.state.current_hit_points > max_hp:
            actual_healing = healing - (self.state.current_hit_points - max_hp)
            self.state.current_hit_points = max_hp
            result["healing_applied"] = actual_healing
            result["new_hp"] = max_hp
        
        # Add journal entry for healing
        if healing > 0:
            self.state.add_journal_entry(
                f"Healed for {result['healing_applied']} HP{' from ' + source if source else ''}. HP: {self.state.current_hit_points}/{max_hp}",
                tags=["healing", "recovery"]
            )
            
        return result
    
    def long_rest(self) -> Dict[str, Any]:
        """Perform a long rest, restoring HP and removing exhaustion."""
        max_hp = self.stats.max_hit_points
        old_hp = self.state.current_hit_points
        old_exhaustion = self.state.exhaustion_level
        
        # Restore HP to max
        self.state.current_hit_points = max_hp
        
        # Remove 1 level of exhaustion
        exhaustion_result = self.state.remove_exhaustion(1, "long_rest")
        
        # Add journal entry
        self.state.add_journal_entry(
            f"Completed a long rest. HP restored from {old_hp} to {max_hp}. " +
            f"Exhaustion reduced from {old_exhaustion} to {self.state.exhaustion_level}.",
            tags=["rest", "recovery"]
        )
        
        return {
            "hp_restored": max_hp - old_hp,
            "exhaustion_removed": exhaustion_result,
            "new_hp": max_hp,
            "new_exhaustion": self.state.exhaustion_level
        }
    
    def get_character_evolution_analysis(self) -> Dict[str, Any]:
        """Analyze character evolution based on journal entries."""
        journal_analysis = self.state.get_journal_summary()
        
        # Enhanced analysis combining journal with current build
        primary_class = max(self.core.character_classes.items(), key=lambda x: x[1])[0] if self.core.character_classes else "Unknown"
        
        analysis = {
            "primary_class": primary_class,
            "journal_analysis": journal_analysis,
            "suggested_evolution": [],
            "character_arc": ""
        }
        
        themes = journal_analysis.get("themes", [])
        
        # Suggest evolution based on journal themes vs current class
        if "Stealth-oriented" in themes and primary_class not in ["Rogue", "Ranger"]:
            analysis["suggested_evolution"].append("Consider multiclassing into Rogue for stealth abilities")
        
        if "Social interactions" in themes and primary_class not in ["Bard", "Paladin", "Warlock"]:
            analysis["suggested_evolution"].append("Consider developing social skills or Charisma-based abilities")
        
        if "Magic user" in themes and primary_class not in ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid"]:
            analysis["suggested_evolution"].append("Consider multiclassing into a spellcasting class")
        
        if "Combat-focused" in themes and primary_class not in ["Fighter", "Barbarian", "Paladin"]:
            analysis["suggested_evolution"].append("Consider combat feats or martial multiclassing")
        
        # Create character arc summary
        entry_count = journal_analysis.get("total_entries", 0)
        if entry_count > 0:
            analysis["character_arc"] = f"Through {entry_count} adventures, {self.core.name} has grown from a {primary_class} into a character with strong {', '.join(themes) if themes else 'general adventuring'} tendencies."
        
        return analysis
    
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
        
        # Check for deadly conditions
        if ExhaustionLevel.is_dead(self.state.exhaustion_level):
            issues.append("Character is dead from exhaustion")
        
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
# This module provides comprehensive character sheet and data model classes:
#
# Core Data Classes:
# - CharacterCore: Core character data with ability scores, classes, and identity
#   * Enhanced with comprehensive getter methods for API access
#   * Immutable core attributes (only changed during character creation/updates)
#
# - CharacterState: Mutable character state (HP, equipment, conditions, currency, journal)
#   * Enhanced with D&D 5e 2024 exhaustion rules (6 levels with cumulative penalties)
#   * Comprehensive condition tracking with mechanical effects
#   * Journal tracking system for character evolution analysis
#   * Full getter/setter methods for RESTful API access
#
# - CharacterStats: Calculated statistics (AC, max HP, proficiency bonus)
#   * Caching system for performance
#
# Main Interface:
# - CharacterSheet: Combined character sheet with validation and management methods
#   * Comprehensive API for frontend integration
#   * Journal-based character evolution analysis
#   * Enhanced gameplay methods (long rest, condition management, etc.)
#   * Automatic journal entry generation for significant events
#
# Utility Classes:
# - CharacterIterationCache: Manages character creation iterations and feedback
# - DnDCondition: Enum for D&D 5e 2024 conditions
# - ExhaustionLevel: Handler for D&D 5e 2024 exhaustion mechanics
#
# Dependencies: core_models.py (AbilityScore, ASIManager, etc.)
#
# Key Features:
# - Complete D&D 5e 2024 character representation
# - Journal tracking for character evolution and storytelling
# - Enhanced condition system with mechanical effect calculations
# - Comprehensive getter/setter API for frontend integration
# - Automatic stat calculation and caching
# - Advanced damage/healing with proper HP management
# - Equipment and condition tracking
# - Character progression and validation
# - Long rest mechanics with exhaustion recovery
# - Character evolution analysis based on play history
# ============================================================================