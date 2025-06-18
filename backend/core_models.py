# ## **1. `core_models.py`**
# **Domain entities and core business logic**
# - **Classes**: `ProficiencyLevel`, `AbilityScoreSource`, `AbilityScore`, `ASIManager`, `CharacterLevelManager`, `MagicItemManager`
# - **Purpose**: Core D&D mechanics, ability scores, ASI management, leveling systems
# - **Dependencies**: None (pure domain logic)

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
    
# classes will be imported in: 

# ## **2. `custom_content_models.py`**
# **Custom D&D content domain models**
# - **Classes**: `CustomSpecies`, `CustomClass`, `CustomItem`, `CustomSpell`, `CustomWeapon`, `CustomArmor`, `CustomFeat`, `FeatManager`, `ContentRegistry`
# - **Purpose**: All custom content creation and management for species, classes, items, spells, weapons, armor, and feats
# - **Dependencies**: `core_models.py`

# ## **3. `character_models.py`**
# **Character sheet and data models**
# - **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`, `CharacterIterationCache`
# - **Purpose**: Character data structures, hit points, equipment, calculated statistics
# - **Dependencies**: `core_models.py`

# ## **4. `ability_management.py`**
# **Advanced ability score progression system**
# - **Classes**: `AbilityScoreManager`, `LevelUpManager`, `CustomSpeciesAbilityManager`, `CustomClassAbilityManager`, `EnhancedAbilityScore`, `EnhancedCharacterCore`
# - **Functions**: `enhance_character_data_with_ability_details`, `create_leveling_interface`, `example_character_leveling`
# - **Purpose**: Enhanced ability score tracking, ASI progression, multiclassing effects, custom content ability interactions
# - **Dependencies**: `core_models.py`, `custom_content_models.py`, `character_models.py`

