from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import math
import random

class AbstractMulticlassAndLevelUp(ABC):
    """
    Abstract base class defining the contract for character level-up and multiclassing 
    in D&D 5e (2024 Edition).
    
    This interface focuses exclusively on the rules governing character advancement
    through level-up and multiclassing.
    """
    
    # Experience point thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Proficiency bonus by level
    PROFICIENCY_BONUS = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    @abstractmethod
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """Level up the character in their current class or a new class."""
        pass
    
    @abstractmethod
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """Check if character meets ability score requirements to multiclass."""
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """Get proficiencies gained when multiclassing into a specific class."""
        pass
    
    @abstractmethod
    def calculate_multiclass_spellcaster_level(self) -> int:
        """Calculate effective spellcaster level for determining spell slots."""
        pass
    
    @abstractmethod
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """Get available spell slots based on multiclass spellcaster level."""
        pass
    
    @abstractmethod
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """Calculate hit points gained when leveling up in a multiclass."""
        pass
    
    @abstractmethod
    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        pass
    
    @abstractmethod
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """Get features gained for a specific class at a specific level."""
        pass
    
    @abstractmethod
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """Apply choices made during level up."""
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """Get levels at which a class grants Ability Score Improvements."""
        pass
    
    @abstractmethod
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """Check if character is eligible for level up based on XP."""
        pass
    
    @abstractmethod
    def get_next_level_xp_threshold(self) -> int:
        """Get XP needed for next level."""
        pass
    
    @abstractmethod
    def calculate_character_level(self) -> int:
        """Calculate total character level from all class levels."""
        pass
    
    @abstractmethod
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """Get all classes and whether character qualifies to multiclass into them."""
        pass


class DNDMulticlassAndLevelUp(AbstractMulticlassAndLevelUp):
    """
    Concrete implementation of D&D 2024 multiclass and level-up rules.
    
    This class implements the actual game mechanics for character advancement.
    """
    
    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize with character data.
        
        Args:
            character_data: Current character information
        """
        self.character_data = character_data
        
        # D&D 2024 class data
        self.class_data = {
            "Barbarian": {
                "hit_die": 12,
                "primary_ability": "strength",
                "multiclass_requirements": {"strength": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": None,
                "multiclass_proficiencies": {
                    "armor": ["shields", "simple weapons", "martial weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Bard": {
                "hit_die": 8,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_any"],
                    "tools": ["choose_1_musical_instrument"]
                }
            },
            "Cleric": {
                "hit_die": 8,
                "primary_ability": "wisdom",
                "multiclass_requirements": {"wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "shields"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Druid": {
                "hit_die": 8,
                "primary_ability": "wisdom",
                "multiclass_requirements": {"wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "armor": ["leather_armor", "studded_leather", "shields"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Fighter": {
                "hit_die": 10,
                "primary_ability": ["strength", "dexterity"],  # Either works
                "multiclass_requirements": {"strength": 13, "dexterity": 13},  # Either 13+ works
                "asi_levels": [4, 6, 8, 12, 14, 16, 19],  # Fighter gets extra ASIs
                "spellcaster_type": None,  # Base class, subclasses may vary
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "heavy_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Monk": {
                "hit_die": 8,
                "primary_ability": ["dexterity", "wisdom"],
                "multiclass_requirements": {"dexterity": 13, "wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": None,
                "multiclass_proficiencies": {
                    "weapons": ["simple_weapons", "shortswords"],
                    "tools": ["choose_1_artisan_or_musical"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Paladin": {
                "hit_die": 10,
                "primary_ability": ["strength", "charisma"],
                "multiclass_requirements": {"strength": 13, "charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "half",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "heavy_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Ranger": {
                "hit_die": 10,
                "primary_ability": ["dexterity", "wisdom"],
                "multiclass_requirements": {"dexterity": 13, "wisdom": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "half",
                "multiclass_proficiencies": {
                    "armor": ["light_armor", "medium_armor", "shields"],
                    "weapons": ["simple_weapons", "martial_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Rogue": {
                "hit_die": 8,
                "primary_ability": "dexterity",
                "multiclass_requirements": {"dexterity": 13},
                "asi_levels": [4, 8, 10, 12, 16, 19],  # Rogue gets extra ASI at 10
                "spellcaster_type": None,  # Base class, Arcane Trickster is 1/3
                "multiclass_proficiencies": {
                    "armor": ["light_armor"],
                    "weapons": ["simple_weapons", "hand_crossbows", "longswords", "rapiers", "shortswords"],
                    "tools": ["thieves_tools"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Sorcerer": {
                "hit_die": 6,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Warlock": {
                "hit_die": 8,
                "primary_ability": "charisma",
                "multiclass_requirements": {"charisma": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "warlock",  # Special case - pact magic
                "multiclass_proficiencies": {
                    "armor": ["light_armor"],
                    "weapons": ["simple_weapons"],
                    "skills": ["choose_1_from_class_list"]
                }
            },
            "Wizard": {
                "hit_die": 6,
                "primary_ability": "intelligence",
                "multiclass_requirements": {"intelligence": 13},
                "asi_levels": [4, 8, 12, 16, 19],
                "spellcaster_type": "full",
                "multiclass_proficiencies": {
                    "skills": ["choose_1_from_class_list"]
                }
            }
        }
        
        # Full caster spell slot progression (levels 1-20)
        self.full_caster_slots = {
            1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
            6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        }
    
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """Level up the character in their current class or a new class."""
        current_level = self.calculate_character_level()
        new_level = current_level + 1
        
        if new_level > 20:
            return {"error": "Cannot exceed level 20"}
        
        # Determine class to level up in
        if new_class:
            # Multiclassing
            can_multiclass, reason = self.can_multiclass_into(new_class)
            if not can_multiclass:
                return {"error": f"Cannot multiclass into {new_class}: {reason}"}
            target_class = new_class
            is_first_level_in_class = self.get_level_in_class(new_class) == 0
        else:
            # Level up in existing class (primary class)
            classes = self.character_data.get("classes", {})
            if not classes:
                return {"error": "No classes found"}
            target_class = max(classes.items(), key=lambda x: x[1])[0]
            is_first_level_in_class = False
        
        # Calculate changes
        results = {
            "new_level": new_level,
            "class_leveled": target_class,
            "is_multiclass": new_class is not None,
            "is_first_level_in_class": is_first_level_in_class
        }
        
        # Hit point increase
        hp_increase = self.calculate_multiclass_hit_points(target_class, is_first_level_in_class)
        results["hp_increase"] = hp_increase
        
        # Update class levels
        current_classes = self.character_data.get("classes", {}).copy()
        new_class_level = current_classes.get(target_class, 0) + 1
        current_classes[target_class] = new_class_level
        results["new_class_levels"] = current_classes
        
        # Check for ASI
        asi_levels = self.get_ability_score_improvement_levels(target_class)
        if new_class_level in asi_levels:
            results["asi_available"] = True
            results["asi_options"] = self._get_asi_options()
        else:
            results["asi_available"] = False
        
        # Update proficiency bonus
        results["proficiency_bonus"] = self.PROFICIENCY_BONUS[new_level]
        
        # Get new class features
        features = self.get_features_for_multiclass(target_class, new_class_level)
        results["new_features"] = features
        
        # Handle spellcasting
        if self._is_spellcaster():
            results["spell_slots"] = self.get_multiclass_spell_slots()
            results["new_spells"] = self._calculate_new_spells(target_class, new_class_level)
        
        # Multiclass proficiencies (if applicable)
        if new_class and is_first_level_in_class:
            results["multiclass_proficiencies"] = self.get_multiclass_proficiencies(new_class)
        
        return results
    
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """Check if character meets ability score requirements to multiclass."""
        if new_class not in self.class_data:
            return False, f"Unknown class: {new_class}"
        
        # Check if already at level 20
        if self.calculate_character_level() >= 20:
            return False, "Already at maximum level (20)"
        
        class_info = self.class_data[new_class]
        requirements = class_info["multiclass_requirements"]
        ability_scores = self.character_data.get("ability_scores", {})
        
        # Check current class requirements (must have 13+ in primary ability to multiclass OUT)
        current_classes = self.character_data.get("classes", {})
        for current_class in current_classes:
            if current_class in self.class_data:
                current_requirements = self.class_data[current_class]["multiclass_requirements"]
                for ability, min_score in current_requirements.items():
                    if ability_scores.get(ability, 10) < min_score:
                        return False, f"Need {ability.title()} {min_score}+ to multiclass out of {current_class}"
        
        # Check new class requirements
        for ability, min_score in requirements.items():
            current_score = ability_scores.get(ability, 10)
            if current_score < min_score:
                return False, f"Need {ability.title()} {min_score}+ (currently {current_score})"
        
        return True, "Multiclass requirements met"
    
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """Get proficiencies gained when multiclassing into a specific class."""
        if new_class not in self.class_data:
            return {}
        
        return self.class_data[new_class].get("multiclass_proficiencies", {})
    
    def calculate_multiclass_spellcaster_level(self) -> int:
        """Calculate effective spellcaster level for determining spell slots."""
        classes = self.character_data.get("classes", {})
        total_caster_level = 0
        
        for class_name, class_level in classes.items():
            if class_name not in self.class_data:
                continue
                
            caster_type = self.class_data[class_name]["spellcaster_type"]
            
            if caster_type == "full":
                total_caster_level += class_level
            elif caster_type == "half":
                total_caster_level += class_level // 2
            elif caster_type == "third":
                total_caster_level += class_level // 3
            # Warlock pact magic doesn't contribute to multiclass spell slots
        
        return total_caster_level
    
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """Get available spell slots based on multiclass spellcaster level."""
        caster_level = self.calculate_multiclass_spellcaster_level()
        
        if caster_level == 0:
            return {}
        
        # Cap at 20 for spell slot purposes
        caster_level = min(caster_level, 20)
        
        return self.full_caster_slots.get(caster_level, {})
    
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """Calculate hit points gained when leveling up in a multiclass."""
        if new_class not in self.class_data:
            return 1  # Minimum 1 HP
        
        hit_die = self.class_data[new_class]["hit_die"]
        con_mod = self._get_ability_modifier("constitution")
        
        if is_first_level and self.calculate_character_level() == 0:
            # First character level ever - max hit die
            return hit_die + con_mod
        else:
            # Take average (rounded up) + CON modifier
            average_roll = (hit_die // 2) + 1
            return max(1, average_roll + con_mod)  # Minimum 1 HP per level
    
    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        classes = self.character_data.get("classes", {})
        return classes.get(class_name, 0)
    
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """Get features gained for a specific class at a specific level."""
        # This would be expanded with actual class feature data
        # For now, return basic information
        features = {
            "class": class_name,
            "level": level,
            "features": []
        }
        
        # Add some basic features based on common patterns
        if level == 1:
            features["features"].append(f"{class_name} proficiencies and starting features")
        elif level == 2:
            features["features"].append(f"{class_name} level 2 features")
        elif level == 3:
            features["features"].append(f"Subclass choice for {class_name}")
        
        # Add ASI notification
        asi_levels = self.get_ability_score_improvement_levels(class_name)
        if level in asi_levels:
            features["features"].append("Ability Score Improvement available")
        
        return features
    
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """Apply choices made during level up."""
        try:
            # Apply ability score improvements
            if "asi_choices" in choices:
                asi_choices = choices["asi_choices"]
                current_scores = self.character_data.get("ability_scores", {})
                
                for ability, increase in asi_choices.items():
                    if ability in current_scores:
                        new_score = min(20, current_scores[ability] + increase)
                        current_scores[ability] = new_score
                
                self.character_data["ability_scores"] = current_scores
            
            # Apply class level increases
            if "new_class_levels" in choices:
                self.character_data["classes"] = choices["new_class_levels"]
            
            # Update character level
            if "new_level" in choices:
                self.character_data["level"] = choices["new_level"]
            
            # Apply new spells
            if "spell_choices" in choices:
                current_spells = self.character_data.get("spells_known", {})
                for spell_level, spells in choices["spell_choices"].items():
                    if spell_level not in current_spells:
                        current_spells[spell_level] = []
                    current_spells[spell_level].extend(spells)
                self.character_data["spells_known"] = current_spells
            
            return True
            
        except Exception as e:
            print(f"Error applying level up choices: {e}")
            return False
    
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """Get levels at which a class grants Ability Score Improvements."""
        if class_name not in self.class_data:
            return [4, 8, 12, 16, 19]  # Default ASI levels
        
        return self.class_data[class_name]["asi_levels"]
    
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """Check if character is eligible for level up based on XP."""
        current_xp = self.character_data.get("experience_points", 0)
        current_level = self.calculate_character_level()
        
        if current_level >= 20:
            return False, "Already at maximum level (20)"
        
        next_threshold = self.get_next_level_xp_threshold()
        
        if current_xp >= next_threshold:
            return True, f"Ready to level up! (XP: {current_xp}/{next_threshold})"
        else:
            needed_xp = next_threshold - current_xp
            return False, f"Need {needed_xp} more XP to level up (XP: {current_xp}/{next_threshold})"
    
    def get_next_level_xp_threshold(self) -> int:
        """Get XP needed for next level."""
        current_level = self.calculate_character_level()
        next_level = min(current_level + 1, 20)
        return self.XP_THRESHOLDS[next_level]
    
    def calculate_character_level(self) -> int:
        """Calculate total character level from all class levels."""
        classes = self.character_data.get("classes", {})
        return sum(classes.values())
    
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """Get all classes and whether character qualifies to multiclass into them."""
        result = {}
        
        for class_name in self.class_data.keys():
            # Skip if already have this class
            if self.get_level_in_class(class_name) > 0:
                result[class_name] = False
            else:
                can_multiclass, _ = self.can_multiclass_into(class_name)
                result[class_name] = can_multiclass
        
        return result
    
    # Helper methods
    def _get_ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier from score."""
        score = self.character_data.get("ability_scores", {}).get(ability, 10)
        return (score - 10) // 2
    
    def _is_spellcaster(self) -> bool:
        """Check if character has any spellcasting abilities."""
        classes = self.character_data.get("classes", {})
        
        for class_name in classes.keys():
            if class_name in self.class_data:
                caster_type = self.class_data[class_name]["spellcaster_type"]
                if caster_type in ["full", "half", "third", "warlock"]:
                    return True
        
        return False
    
    def _get_asi_options(self) -> Dict[str, Any]:
        """Get available ASI options."""
        return {
            "ability_scores": {
                "strength": "Increase Strength by 1 or 2",
                "dexterity": "Increase Dexterity by 1 or 2", 
                "constitution": "Increase Constitution by 1 or 2",
                "intelligence": "Increase Intelligence by 1 or 2",
                "wisdom": "Increase Wisdom by 1 or 2",
                "charisma": "Increase Charisma by 1 or 2"
            },
            "feats": "Choose a feat instead of ability score increase",
            "notes": "Total increases cannot exceed +2, and no ability can exceed 20"
        }
    
    def _calculate_new_spells(self, class_name: str, class_level: int) -> Dict[str, List[str]]:
        """Calculate new spells learned at this level."""
        # Simplified spell learning - would need full spell progression tables
        new_spells = {}
        
        caster_type = self.class_data.get(class_name, {}).get("spellcaster_type")
        
        if caster_type == "full":
            # Full casters learn new spells regularly
            if class_level <= 17:  # Can learn up to 9th level spells
                max_spell_level = min((class_level + 1) // 2, 9)
                if class_level % 2 == 1:  # Odd levels often unlock new spell levels
                    new_spells[str(max_spell_level)] = [f"New {max_spell_level} level spell"]
        elif caster_type == "half":
            # Half casters learn spells more slowly
            if class_level >= 2 and class_level <= 17:
                max_spell_level = min((class_level - 1) // 4 + 1, 5)
                if class_level in [3, 5, 9, 13, 17]:  # Key spell learning levels
                    new_spells[str(max_spell_level)] = [f"New {max_spell_level} level spell"]
        
        return new_spells
    
    # Legacy compatibility methods (for existing character creator)
    def calculate_level_up_changes(self, current_character: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """Legacy method for backward compatibility with existing character creator."""
        self.character_data = current_character
        
        # Calculate what class to level up in
        current_level = current_character.get("level", 1)
        classes = current_character.get("classes", {"Fighter": current_level})
        
        # For single class, continue in that class
        if len(classes) == 1:
            target_class = list(classes.keys())[0]
        else:
            # For multiclass, level up primary class
            target_class = max(classes.items(), key=lambda x: x[1])[0]
        
        # Simulate level up
        level_up_result = self.level_up()
        
        # Convert to legacy format
        changes = {
            "proficiency_bonus": self.PROFICIENCY_BONUS[new_level],
            "class_levels": level_up_result.get("new_class_levels", classes),
            "hit_points": level_up_result.get("hp_increase", 1),
            "new_proficiencies": [],
            "suggested_equipment": self._suggest_level_appropriate_equipment(new_level)
        }
        
        if level_up_result.get("asi_available"):
            changes["ability_score_improvements"] = self._suggest_asi_improvements(current_character)
        
        if self._is_spellcaster():
            changes["new_spells"] = level_up_result.get("new_spells", {})
            changes["spell_slots"] = level_up_result.get("spell_slots", {})
        
        return changes
    
    def _suggest_asi_improvements(self, character: Dict[str, Any]) -> Dict[str, int]:
        """Legacy method: Suggest ability score improvements."""
        abilities = character.get("ability_scores", {})
        classes = character.get("classes", {})
        
        # Find primary class
        if classes:
            primary_class = max(classes.items(), key=lambda x: x[1])[0]
            if primary_class in self.class_data:
                primary_ability = self.class_data[primary_class]["primary_ability"]
                if isinstance(primary_ability, list):
                    # Choose the higher of the two abilities
                    primary_ability = max(primary_ability, key=lambda a: abilities.get(a, 10))
            else:
                primary_ability = "strength"
        else:
            primary_ability = "strength"
        
        # Suggest improving primary ability or constitution
        current_primary = abilities.get(primary_ability, 10)
        current_con = abilities.get("constitution", 10)
        
        if current_primary < 20:
            return {primary_ability: 2}
        elif current_con < 16:
            return {"constitution": 2}
        else:
            return {"dexterity": 2}  # Default fallback
    
    def _suggest_level_appropriate_equipment(self, new_level: int) -> List[str]:
        """Legacy method: Suggest equipment appropriate for the character level."""
        suggestions = []
        
        if new_level == 3:
            suggestions.append("Masterwork weapon")
        elif new_level == 5:
            suggestions.append("Magic weapon +1")
        elif new_level == 10:
            suggestions.append("Magic armor +1")
        elif new_level == 15:
            suggestions.append("Rare magical item")
        elif new_level == 20:
            suggestions.append("Legendary magical item")
        
        return suggestions