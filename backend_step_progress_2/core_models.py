"""
Core D&D models and business logic.

This module provides the fundamental D&D mechanics including:
- Ability scores with multiple sources and tracking
- ASI (Ability Score Improvement) management
- Magic item effects on ability scores
- Character leveling system

Dependencies: None (pure domain logic)
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

# Import from centralized enums
from enums import (
    ProficiencyLevel, 
    AbilityScoreSource, 
    SpellcastingType, 
    SpellcastingAbility, 
    RitualCastingType
)

if TYPE_CHECKING:
    from character_models import CharacterCore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED AND CLEANED MODULE - 2024 D&D COMPLIANCE

This module provides core D&D mechanics and business logic:

CLASSES:
- ProficiencyLevel: Enum for skill proficiency levels
- AbilityScoreSource: Enum for tracking sources of ability score bonuses
- AbilityScore: Enhanced ability score with multiple source tracking
- ASIManager: Comprehensive ASI management with validation
- MagicItemManager: Magic item effects on ability scores
- CharacterLevelManager: Level progression and ASI tracking

KEY FEATURES:
- 2024 D&D rules compliance
- Comprehensive ASI tracking and validation
- Magic item effects management
- Level progression tracking
- No dependencies on other modules (pure domain logic)

REFACTORING NOTES:
- Removed dependency on CharacterCore class (now passed as parameter)
- Added proper type hints with TYPE_CHECKING
- Simplified class interfaces for better modularity
- Enhanced error handling and logging
- Removed duplicate/legacy code
"""

# ============================================================================
# CORE ENUMS AND DATA STRUCTURES
# ============================================================================

# ============================================================================
# ENHANCED ABILITY SCORE SYSTEM
# ============================================================================

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
            "temporary": temporary,
            "timestamp": datetime.now().isoformat()
        }
        
        self.improvements[source].append(improvement)
        self._invalidate_cache()
        
        logger.info(f"Added {amount} {source.value} improvement: {description}")
    
    def remove_improvement(self, source: AbilityScoreSource, description: str = ""):
        """Remove a specific improvement (useful for temporary effects)."""
        if description:
            original_count = len(self.improvements[source])
            self.improvements[source] = [
                imp for imp in self.improvements[source] 
                if imp["description"] != description
            ]
            removed_count = original_count - len(self.improvements[source])
            if removed_count > 0:
                logger.info(f"Removed {removed_count} {source.value} improvements matching: {description}")
        else:
            self.improvements[source].clear()
            logger.info(f"Cleared all {source.value} improvements")
        
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
                    "feat_name": improvement["feat_name"],
                    "timestamp": improvement.get("timestamp", "")
                })
        
        # Sort by level gained, then by timestamp
        return sorted(history, key=lambda x: (x["level_gained"], x["timestamp"]))
    
    def _invalidate_cache(self):
        """Invalidate cached values when improvements change."""
        self._cached_total = None
        self._cached_modifier = None

# ============================================================================
# ENHANCED ASI MANAGER
# ============================================================================

class ASIManager:
    """Enhanced ASI Manager with comprehensive tracking and validation."""
    
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
        self.pending_asis: List[Dict[str, Any]] = []
    
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
                    character_level_when_gained = self._estimate_character_level_for_asi(
                        class_name, asi_level, character_classes, total_character_level
                    )
                    
                    available_asis.append({
                        "class": class_name,
                        "class_level": asi_level,
                        "character_level": character_level_when_gained,
                        "used": False,  # Will be updated based on ASI history
                        "id": f"{class_name}_{asi_level}"
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
    
    def validate_asi_choice(self, ability_scores: Dict[str, AbilityScore], 
                           improvements: Dict[str, int]) -> Dict[str, Any]:
        """Validate an ASI choice before applying it."""
        issues = []
        warnings = []
        
        # Validate ASI points (must total 2)
        total_points = sum(improvements.values())
        if total_points != 2:
            issues.append(f"ASI must use exactly 2 points, got {total_points}")
        
        # Validate individual improvements
        for ability, increase in improvements.items():
            if ability not in ability_scores:
                issues.append(f"Unknown ability score: {ability}")
                continue
            
            if increase <= 0:
                issues.append(f"Invalid increase amount for {ability}: {increase}")
                continue
            
            if increase > 2:
                issues.append(f"Cannot increase {ability} by more than 2 in a single ASI")
                continue
            
            # Check if this would exceed the normal maximum
            current_score = ability_scores[ability].total_score
            new_score = current_score + increase
            
            if new_score > 20:
                warnings.append(f"Increasing {ability} to {new_score} (above normal max of 20)")
            
            if new_score > 30:
                issues.append(f"Cannot increase {ability} above absolute maximum of 30")
        
        # Validate point distribution
        if len(improvements) > 2:
            issues.append("Cannot improve more than 2 different abilities with one ASI")
        
        if len(improvements) == 2:
            values = list(improvements.values())
            if not all(v == 1 for v in values):
                issues.append("When improving 2 abilities, each must receive exactly +1")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def apply_asi(self, ability_scores: Dict[str, AbilityScore], 
                  improvements: Dict[str, int], character_level: int, 
                  description: str = "ASI") -> Dict[str, Any]:
        """Apply an ASI to ability scores with comprehensive validation and logging."""
        
        logger.info(f"Applying ASI at level {character_level}: {improvements}")
        
        # Validate the ASI choice
        validation = self.validate_asi_choice(ability_scores, improvements)
        
        if not validation["valid"]:
            error_msg = f"Invalid ASI choice: {'; '.join(validation['issues'])}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log warnings
        for warning in validation["warnings"]:
            logger.warning(f"ASI Warning: {warning}")
        
        # Apply improvements
        applied_improvements = {}
        for ability, increase in improvements.items():
            old_score = ability_scores[ability].total_score
            
            ability_scores[ability].add_improvement(
                AbilityScoreSource.ASI,
                increase,
                description,
                character_level
            )
            
            new_score = ability_scores[ability].total_score
            applied_improvements[ability] = {
                "old_score": old_score,
                "new_score": new_score,
                "increase": increase
            }
            
            logger.info(f"Increased {ability} from {old_score} to {new_score} (+{increase})")
        
        # Record in history with timestamp
        asi_record = {
            "level": character_level,
            "improvements": improvements.copy(),
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "applied_changes": applied_improvements
        }
        
        self.asi_history.append(asi_record)
        self.total_asi_points_used += sum(improvements.values())
        
        # Check if there are more ASIs available
        remaining_asis = len(self.pending_asis) - len(self.asi_history)
        
        result = {
            "success": True,
            "applied_improvements": applied_improvements,
            "total_points_used": self.total_asi_points_used,
            "remaining_asis": remaining_asis,
            "warnings": validation["warnings"]
        }
        
        logger.info(f"ASI applied successfully. Total points used: {self.total_asi_points_used}")
        return result
    
    def get_asi_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of ASI usage."""
        return {
            "total_points_used": self.total_asi_points_used,
            "asis_applied": len(self.asi_history),
            "history": self.asi_history.copy(),
            "last_asi": self.asi_history[-1] if self.asi_history else None,
            "average_points_per_asi": (
                self.total_asi_points_used / len(self.asi_history) 
                if self.asi_history else 0
            )
        }
    
    def undo_last_asi(self, ability_scores: Dict[str, AbilityScore]) -> Dict[str, Any]:
        """Undo the last applied ASI (for testing/correction purposes)."""
        if not self.asi_history:
            raise ValueError("No ASI history to undo")
        
        last_asi = self.asi_history.pop()
        improvements = last_asi["improvements"]
        description = last_asi["description"]
        
        # Remove the improvements
        for ability, increase in improvements.items():
            if ability in ability_scores:
                ability_scores[ability].remove_improvement(
                    AbilityScoreSource.ASI, 
                    description
                )
        
        self.total_asi_points_used -= sum(improvements.values())
        
        logger.info(f"Undid ASI: {improvements}")
        
        return {
            "success": True,
            "undone_asi": last_asi,
            "remaining_points": self.total_asi_points_used
        }

# ============================================================================
# ENHANCED MAGIC ITEM MANAGER
# ============================================================================

class MagicItemManager:
    """Manages magic items and their effects on character ability scores."""
    
    def __init__(self):
        self.active_items: Dict[str, Dict[str, Any]] = {}
        self.item_history: List[Dict[str, Any]] = []
    
    def add_magic_item(self, item_name: str, ability_bonuses: Dict[str, int] = None, 
                      sets_score: Dict[str, int] = None, temporary: bool = False,
                      duration: str = "permanent", 
                      ability_scores: Dict[str, 'AbilityScore'] = None) -> Dict[str, Any]:
        """Add a magic item that affects ability scores."""
        
        if not ability_scores:
            raise ValueError("ability_scores dict is required")
        
        applied_effects = {}
        
        # Handle items that set scores to specific values (like Belt of Giant Strength)
        if sets_score:
            for ability, score in sets_score.items():
                if ability in ability_scores:
                    old_score = ability_scores[ability].total_score
                    
                    # Remove any existing magic item bonuses for this ability from this item
                    ability_scores[ability].remove_improvement(
                        AbilityScoreSource.MAGIC_ITEM, item_name
                    )
                    
                    # Calculate the effective bonus to reach the target score
                    current_without_magic = (
                        ability_scores[ability].base_score + 
                        ability_scores[ability].asi_improvements +
                        ability_scores[ability].feat_improvements
                    )
                    
                    if score > current_without_magic:
                        bonus = score - current_without_magic
                        ability_scores[ability].add_improvement(
                            AbilityScoreSource.MAGIC_ITEM,
                            bonus,
                            f"{item_name} (sets to {score})",
                            temporary=temporary
                        )
                        
                        applied_effects[ability] = {
                            "type": "set_score",
                            "old_score": old_score,
                            "new_score": score,
                            "effective_bonus": bonus
                        }
        
        # Handle items that provide flat bonuses
        if ability_bonuses:
            for ability, bonus in ability_bonuses.items():
                if ability in ability_scores:
                    old_score = ability_scores[ability].total_score
                    
                    ability_scores[ability].add_improvement(
                        AbilityScoreSource.MAGIC_ITEM,
                        bonus,
                        f"{item_name} (+{bonus})",
                        temporary=temporary
                    )
                    
                    new_score = ability_scores[ability].total_score
                    applied_effects[ability] = {
                        "type": "flat_bonus",
                        "old_score": old_score,
                        "new_score": new_score,
                        "bonus": bonus
                    }
        
        # Record the item
        item_record = {
            "name": item_name,
            "ability_bonuses": ability_bonuses or {},
            "sets_score": sets_score or {},
            "temporary": temporary,
            "duration": duration,
            "applied_at": datetime.now().isoformat(),
            "applied_effects": applied_effects
        }
        
        self.active_items[item_name] = item_record
        self.item_history.append({
            "action": "added",
            "item": item_record.copy(),
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Added magic item: {item_name} with effects: {applied_effects}")
        
        return {
            "success": True,
            "item_name": item_name,
            "applied_effects": applied_effects,
            "temporary": temporary
        }
    
    def remove_magic_item(self, item_name: str, 
                          ability_scores: Dict[str, 'AbilityScore']) -> Dict[str, Any]:
        """Remove a magic item and its effects."""
        if item_name not in self.active_items:
            raise ValueError(f"Magic item '{item_name}' not found")
        
        item_record = self.active_items[item_name]
        removed_effects = {}
        
        # Remove all improvements from this item
        for ability_name, ability_score in ability_scores.items():
            old_score = ability_score.total_score
            ability_score.remove_improvement(AbilityScoreSource.MAGIC_ITEM, item_name)
            new_score = ability_score.total_score
            
            if old_score != new_score:
                removed_effects[ability_name] = {
                    "old_score": old_score,
                    "new_score": new_score,
                    "change": new_score - old_score
                }
        
        # Record removal
        self.item_history.append({
            "action": "removed",
            "item": item_record.copy(),
            "removed_effects": removed_effects,
            "timestamp": datetime.now().isoformat()
        })
        
        del self.active_items[item_name]
        
        logger.info(f"Removed magic item: {item_name} with effects: {removed_effects}")
        
        return {
            "success": True,
            "item_name": item_name,
            "removed_effects": removed_effects
        }
    
    def get_active_items_summary(self) -> Dict[str, Any]:
        """Get summary of all active magic items."""
        return {
            "count": len(self.active_items),
            "items": list(self.active_items.keys()),
            "temporary_items": [
                name for name, item in self.active_items.items() 
                if item["temporary"]
            ],
            "permanent_items": [
                name for name, item in self.active_items.items() 
                if not item["temporary"]
            ]
        }

# ============================================================================
# CHARACTER LEVEL MANAGER
# ============================================================================

class CharacterLevelManager:
    """Manages character leveling progression and ASI tracking."""
    
    def __init__(self):
        self.asi_manager = ASIManager()
        self.level_history: List[Dict[str, Any]] = []
        self.pending_choices: List[Dict[str, Any]] = []
    
    def add_level(self, class_name: str, new_level: int, character_classes: Dict[str, int],
                  ability_scores: Dict[str, 'AbilityScore'], 
                  asi_choice: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a level in a specific class with comprehensive tracking."""
        
        # Validate level progression
        if class_name not in character_classes:
            character_classes[class_name] = 0
        
        old_level = character_classes[class_name]
        
        if new_level != old_level + 1:
            raise ValueError(f"Invalid level progression: {old_level} -> {new_level}")
        
        # Update class level
        character_classes[class_name] = new_level
        
        # Calculate new total level
        total_level = sum(character_classes.values())
        
        # Record level-up
        level_up_record = {
            "class": class_name,
            "old_class_level": old_level,
            "new_class_level": new_level,
            "total_character_level": total_level,
            "gained_features": self._get_features_gained(class_name, new_level),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if this level grants an ASI
        asi_levels = self.asi_manager.get_asi_levels_for_class(class_name)
        if new_level in asi_levels:
            level_up_record["grants_asi"] = True
            
            if asi_choice:
                if asi_choice["type"] == "asi":
                    # Apply ability score improvement
                    asi_result = self.asi_manager.apply_asi(
                        ability_scores,
                        asi_choice["improvements"],
                        total_level,
                        f"ASI at {class_name} level {new_level}"
                    )
                    level_up_record["asi_used"] = asi_choice
                    level_up_record["asi_result"] = asi_result
                
                elif asi_choice["type"] == "feat":
                    # Apply feat (which may include ability score bonuses)
                    feat_name = asi_choice["feat_name"]
                    ability_bonuses = asi_choice.get("ability_bonuses", {})
                    
                    if ability_bonuses:
                        for ability, bonus in ability_bonuses.items():
                            if ability in ability_scores:
                                ability_scores[ability].add_improvement(
                                    AbilityScoreSource.FEAT,
                                    bonus,
                                    f"Feat: {feat_name}",
                                    total_level,
                                    feat_name
                                )
                    
                    level_up_record["feat_chosen"] = feat_name
                    level_up_record["feat_ability_bonuses"] = ability_bonuses
            else:
                level_up_record["asi_pending"] = True
                self.pending_choices.append({
                    "type": "asi",
                    "class": class_name,
                    "level": new_level,
                    "total_level": total_level
                })
        
        self.level_history.append(level_up_record)
        
        logger.info(f"Leveled up to {class_name} {new_level} (total level {total_level})")
        
        return {
            "success": True,
            "class": class_name,
            "new_level": new_level,
            "total_level": total_level,
            "grants_asi": level_up_record.get("grants_asi", False),
            "pending_choices": len(self.pending_choices)
        }
    
    def _get_features_gained(self, class_name: str, level: int) -> List[str]:
        """Get features gained at this class level."""
        # This would integrate with your class feature system
        # For now, return a placeholder
        return [f"{class_name} level {level} features"]
    
    def get_pending_choices(self) -> List[Dict[str, Any]]:
        """Get list of pending character choices (ASIs, feats, etc.)."""
        return self.pending_choices.copy()
    
    def resolve_pending_choice(self, choice_index: int, resolution: Dict[str, Any],
                              ability_scores: Dict[str, 'AbilityScore']) -> Dict[str, Any]:
        """Resolve a pending character choice."""
        if choice_index >= len(self.pending_choices):
            raise ValueError(f"Invalid choice index: {choice_index}")
        
        choice = self.pending_choices.pop(choice_index)
        
        if choice["type"] == "asi":
            # Apply the ASI choice
            asi_result = self.asi_manager.apply_asi(
                ability_scores,
                resolution["improvements"],
                choice["total_level"],
                f"ASI at {choice['class']} level {choice['level']}"
            )
            
            return {
                "success": True,
                "choice_type": "asi",
                "result": asi_result
            }
        
        return {"success": False, "error": "Unknown choice type"}
    
    def get_level_progression_summary(self, character_classes: Dict[str, int]) -> Dict[str, Any]:
        """Get comprehensive summary of character's level progression."""
        
        total_level = sum(character_classes.values())
        asi_info = self.asi_manager.calculate_available_asis(character_classes)
        
        return {
            "total_level": total_level,
            "class_levels": character_classes.copy(),
            "multiclass": len(character_classes) > 1,
            "asi_info": asi_info,
            "asi_summary": self.asi_manager.get_asi_summary(),
            "pending_choices": self.get_pending_choices(),
            "level_history": self.level_history.copy(),
            "levels_gained": len(self.level_history)
        }

# ============================================================================
# D&D 5E SPELLCASTING SYSTEM
# ============================================================================

@dataclass
class SpellcastingProgression:
    """Spellcasting progression data for a class."""
    spellcasting_type: SpellcastingType
    spellcasting_ability: SpellcastingAbility
    ritual_casting: RitualCastingType
    spell_slots_per_level: Dict[int, Dict[int, int]]  # character_level -> {spell_level: slots}
    spells_known_per_level: Dict[int, int]  # character_level -> spells_known (for known casters)
    spells_prepared_formula: str  # Formula for prepared spells (e.g., "ability_modifier + class_level")
    cantrips_known_per_level: Dict[int, int]  # character_level -> cantrips_known
    first_spell_level: int = 1  # Level when spellcasting begins
    spell_list_name: str = ""  # Name of the spell list used

# ============================================================================
# SPELLCASTING CLASS DEFINITIONS
# ============================================================================

class SpellcastingManager:
    """Manages spellcasting information for D&D 5e 2024 classes."""
    
    # Define spellcasting progressions for each class
    CLASS_SPELLCASTING = {
        "artificer": SpellcastingProgression(
            spellcasting_type=SpellcastingType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
            ritual_casting=RitualCastingType.PREPARED_ONLY,
            spell_slots_per_level={
                1: {}, 2: {1: 2}, 3: {1: 3}, 4: {1: 3}, 5: {1: 4, 2: 2},
                6: {1: 4, 2: 2}, 7: {1: 4, 2: 3}, 8: {1: 4, 2: 3}, 9: {1: 4, 2: 3, 3: 2},
                10: {1: 4, 2: 3, 3: 2}, 11: {1: 4, 2: 3, 3: 3}, 12: {1: 4, 2: 3, 3: 3},
                13: {1: 4, 2: 3, 3: 3, 4: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 2}, 16: {1: 4, 2: 3, 3: 3, 4: 2},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
            },
            spells_known_per_level={},  # Prepared caster
            spells_prepared_formula="intelligence_modifier + (artificer_level // 2)",
            cantrips_known_per_level={1: 2, 10: 3, 14: 4},
            first_spell_level=2,
            spell_list_name="Artificer"
        ),
        
        "bard": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
            ritual_casting=RitualCastingType.PREPARED_ONLY,
            spell_slots_per_level={
                1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1}
            },
            spells_known_per_level={1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15, 13: 16, 14: 18, 15: 19, 16: 19, 17: 20, 18: 22, 19: 22, 20: 22},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={1: 2, 4: 3, 10: 4},
            first_spell_level=1,
            spell_list_name="Bard"
        ),
        
        "cleric": SpellcastingProgression(
            spellcasting_type=SpellcastingType.PREPARED,
            spellcasting_ability=SpellcastingAbility.WISDOM,
            ritual_casting=RitualCastingType.PREPARED_ONLY,
            spell_slots_per_level={
                1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1}
            },
            spells_known_per_level={},  # Prepared caster
            spells_prepared_formula="wisdom_modifier + cleric_level",
            cantrips_known_per_level={1: 3, 4: 4, 10: 5},
            first_spell_level=1,
            spell_list_name="Divine"
        ),
        
        "druid": SpellcastingProgression(
            spellcasting_type=SpellcastingType.PREPARED,
            spellcasting_ability=SpellcastingAbility.WISDOM,
            ritual_casting=RitualCastingType.PREPARED_ONLY,
            spell_slots_per_level={
                1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1}
            },
            spells_known_per_level={},  # Prepared caster
            spells_prepared_formula="wisdom_modifier + druid_level",
            cantrips_known_per_level={1: 2, 4: 3, 10: 4},
            first_spell_level=1,
            spell_list_name="Primal"
        ),
        
        "paladin": SpellcastingProgression(
            spellcasting_type=SpellcastingType.PREPARED,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                1: {}, 2: {1: 2}, 3: {1: 3}, 4: {1: 3}, 5: {1: 4, 2: 2},
                6: {1: 4, 2: 2}, 7: {1: 4, 2: 3}, 8: {1: 4, 2: 3}, 9: {1: 4, 2: 3, 3: 2},
                10: {1: 4, 2: 3, 3: 2}, 11: {1: 4, 2: 3, 3: 3}, 12: {1: 4, 2: 3, 3: 3},
                13: {1: 4, 2: 3, 3: 3, 4: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 2}, 16: {1: 4, 2: 3, 3: 3, 4: 2},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
            },
            spells_known_per_level={},  # Prepared caster
            spells_prepared_formula="charisma_modifier + (paladin_level // 2)",
            cantrips_known_per_level={},  # No cantrips
            first_spell_level=2,
            spell_list_name="Divine"
        ),
        
        "ranger": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.WISDOM,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                1: {}, 2: {1: 2}, 3: {1: 3}, 4: {1: 3}, 5: {1: 4, 2: 2},
                6: {1: 4, 2: 2}, 7: {1: 4, 2: 3}, 8: {1: 4, 2: 3}, 9: {1: 4, 2: 3, 3: 2},
                10: {1: 4, 2: 3, 3: 2}, 11: {1: 4, 2: 3, 3: 3}, 12: {1: 4, 2: 3, 3: 3},
                13: {1: 4, 2: 3, 3: 3, 4: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 2}, 16: {1: 4, 2: 3, 3: 3, 4: 2},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
            },
            spells_known_per_level={2: 2, 3: 3, 5: 4, 7: 5, 9: 6, 11: 7, 13: 8, 15: 9, 17: 10, 19: 11},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={},  # No cantrips by default
            first_spell_level=2,
            spell_list_name="Primal"
        ),
        
        "sorcerer": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1}
            },
            spells_known_per_level={1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={1: 4, 4: 5, 10: 6},
            first_spell_level=1,
            spell_list_name="Arcane"
        ),
        
        "warlock": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                1: {1: 1}, 2: {1: 2}, 3: {2: 2}, 4: {2: 2}, 5: {3: 2}, 6: {3: 2},
                7: {4: 2}, 8: {4: 2}, 9: {5: 2}, 10: {5: 2}, 11: {5: 3}, 12: {5: 3},
                13: {5: 3}, 14: {5: 3}, 15: {5: 3}, 16: {5: 3}, 17: {5: 4}, 18: {5: 4},
                19: {5: 4}, 20: {5: 4}
            },
            spells_known_per_level={1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10, 11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={1: 2, 4: 3, 10: 4},
            first_spell_level=1,
            spell_list_name="Arcane"
        ),
        
        "wizard": SpellcastingProgression(
            spellcasting_type=SpellcastingType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
            ritual_casting=RitualCastingType.SPELLBOOK,
            spell_slots_per_level={
                1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3}, 5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, 18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1}
            },
            spells_known_per_level={},  # Prepared caster
            spells_prepared_formula="intelligence_modifier + wizard_level",
            cantrips_known_per_level={1: 3, 4: 4, 10: 5},
            first_spell_level=1,
            spell_list_name="Arcane"
        ),
        
        # Subclasses with limited spellcasting
        "eldritch_knight": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                3: {1: 2}, 4: {1: 3}, 7: {1: 4, 2: 2}, 8: {1: 4, 2: 2}, 10: {1: 4, 2: 3},
                11: {1: 4, 2: 3}, 13: {1: 4, 2: 3, 3: 2}, 14: {1: 4, 2: 3, 3: 2},
                16: {1: 4, 2: 3, 3: 3}, 17: {1: 4, 2: 3, 3: 3}, 19: {1: 4, 2: 3, 3: 3, 4: 1},
                20: {1: 4, 2: 3, 3: 3, 4: 1}
            },
            spells_known_per_level={3: 3, 4: 4, 7: 5, 8: 6, 10: 7, 11: 8, 13: 9, 14: 10, 16: 11, 19: 12, 20: 13},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={3: 2, 10: 3},
            first_spell_level=3,
            spell_list_name="Arcane"
        ),
        
        "arcane_trickster": SpellcastingProgression(
            spellcasting_type=SpellcastingType.KNOWN,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
            ritual_casting=RitualCastingType.NONE,
            spell_slots_per_level={
                3: {1: 2}, 4: {1: 3}, 7: {1: 4, 2: 2}, 8: {1: 4, 2: 2}, 10: {1: 4, 2: 3},
                11: {1: 4, 2: 3}, 13: {1: 4, 2: 3, 3: 2}, 14: {1: 4, 2: 3, 3: 2},
                16: {1: 4, 2: 3, 3: 3}, 17: {1: 4, 2: 3, 3: 3}, 19: {1: 4, 2: 3, 3: 3, 4: 1},
                20: {1: 4, 2: 3, 3: 3, 4: 1}
            },
            spells_known_per_level={3: 3, 4: 4, 7: 5, 8: 6, 10: 7, 11: 8, 13: 9, 14: 10, 16: 11, 19: 12, 20: 13},
            spells_prepared_formula="",  # Known caster
            cantrips_known_per_level={3: 3, 10: 4},
            first_spell_level=3,
            spell_list_name="Arcane"
        )
    }
    
    @classmethod
    def get_spellcasting_info(cls, class_name: str, class_level: int) -> Optional[Dict[str, Any]]:
        """Get spellcasting information for a class at a specific level."""
        class_lower = class_name.lower()
        
        if class_lower not in cls.CLASS_SPELLCASTING:
            return None
        
        progression = cls.CLASS_SPELLCASTING[class_lower]
        
        # Check if spellcasting has started
        if class_level < progression.first_spell_level:
            return None
        
        # Calculate current spellcasting information
        spell_slots = progression.spell_slots_per_level.get(class_level, {})
        spells_known = progression.spells_known_per_level.get(class_level, 0)
        cantrips_known = progression.cantrips_known_per_level.get(class_level, 0)
        
        # Calculate spells prepared (for prepared casters)
        spells_prepared = 0
        if progression.spellcasting_type == SpellcastingType.PREPARED:
            # This would need to be calculated based on the character's ability scores
            # For now, return the formula
            spells_prepared = progression.spells_prepared_formula
        
        return {
            "spellcasting_type": progression.spellcasting_type.value,
            "spellcasting_ability": progression.spellcasting_ability.value,
            "ritual_casting": progression.ritual_casting.value,
            "spell_slots": spell_slots,
            "spells_known": spells_known,
            "spells_prepared_formula": spells_prepared,
            "cantrips_known": cantrips_known,
            "spell_list_name": progression.spell_list_name,
            "can_swap_spells_on_rest": progression.spellcasting_type == SpellcastingType.PREPARED,
            "can_cast_rituals": progression.ritual_casting != RitualCastingType.NONE,
            "ritual_casting_type": progression.ritual_casting.value
        }
    
    @classmethod
    def is_spellcaster(cls, class_name: str, class_level: int = 1) -> bool:
        """Check if a class is a spellcaster at the given level."""
        return cls.get_spellcasting_info(class_name, class_level) is not None
    
    @classmethod
    def get_combined_spellcasting(cls, character_classes: Dict[str, int]) -> Dict[str, Any]:
        """Get combined spellcasting information for multiclass characters."""
        spellcasting_classes = []
        total_caster_levels = 0
        
        # Collect spellcasting classes and calculate caster levels
        for class_name, class_level in character_classes.items():
            spellcasting_info = cls.get_spellcasting_info(class_name, class_level)
            if spellcasting_info:
                spellcasting_classes.append({
                    "class": class_name,
                    "level": class_level,
                    "info": spellcasting_info
                })
                
                # Calculate multiclass spellcaster level
                if class_name.lower() in ["artificer", "paladin", "ranger"]:
                    # Half casters
                    total_caster_levels += max(1, class_level // 2)
                elif class_name.lower() in ["eldritch_knight", "arcane_trickster"]:
                    # Third casters
                    total_caster_levels += max(1, class_level // 3)
                else:
                    # Full casters
                    total_caster_levels += class_level
        
        if not spellcasting_classes:
            return {"is_spellcaster": False}
        
        # For multiclass, use full caster spell slot progression
        if len(spellcasting_classes) > 1:
            multiclass_slots = cls.CLASS_SPELLCASTING["wizard"].spell_slots_per_level.get(
                min(total_caster_levels, 20), {}
            )
        else:
            multiclass_slots = spellcasting_classes[0]["info"]["spell_slots"]
        
        return {
            "is_spellcaster": True,
            "spellcasting_classes": spellcasting_classes,
            "total_caster_level": total_caster_levels,
            "multiclass_spell_slots": multiclass_slots,
            "primary_spellcasting_class": spellcasting_classes[0]["class"] if spellcasting_classes else None,
            "has_multiple_spellcasting_abilities": len(set(sc["info"]["spellcasting_ability"] for sc in spellcasting_classes)) > 1
        }
