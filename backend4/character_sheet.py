from typing import Dict, Any, Optional
import logging

from character_core import CharacterCore
from character_state import CharacterState
from character_stats import CharacterStats

logger = logging.getLogger(__name__)

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
                from unified_validator import create_unified_validator
                validator = create_unified_validator()
                character_data = self.to_dict()
                result = validator.validate_character(character_data, self)
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
