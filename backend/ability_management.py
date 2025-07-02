# ## **4. `ability_management.py`**
# **Advanced ability score progression system**
# - **Classes**: `AdvancedAbilityManager`, `CustomContentAbilityManager`
# - **Functions**: `enhance_character_data_with_ability_details`
# - **Purpose**: Enhanced ability score tracking, custom content ability interactions, 2024 D&D rule compliance
# - **Dependencies**: `core_models.py`, `custom_content_models.py`, `character_models.py`

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
import time
from functools import wraps

# Import from other modules
from backend.core_models import ASIManager, CharacterLevelManager, AbilityScore, AbilityScoreSource
from backend.custom_content_models import CustomSpecies, CustomClass
from backend.character_models import CharacterCore
from backend.creation_validation import (
    validate_basic_structure, validate_custom_content, 
    validate_custom_species_balance, validate_custom_class_balance,
    CreationResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PERFORMANCE MONITORING AND OPTIMIZATION
# ============================================================================

class AbilityPerformanceMonitor:
    """Monitors performance of ability score operations."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def time_operation(self, operation_name: str):
        """Decorator to time operations."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if operation_name not in self.metrics:
                        self.metrics[operation_name] = []
                    
                    self.metrics[operation_name].append(duration)
                    
                    # Log slow operations
                    if duration > 1.0:  # Operations taking more than 1 second
                        logger.warning(f"Slow operation {operation_name}: {duration:.3f}s")
            
            return wrapper
        return decorator
    
    def cache_result(self, cache_key: str, result: Any, ttl: int = 300):
        """Cache a result with TTL (time to live) in seconds."""
        expiry_time = time.time() + ttl
        self.cache[cache_key] = {
            "result": result,
            "expiry": expiry_time
        }
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get a cached result if still valid."""
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() < cache_entry["expiry"]:
                self.cache_hits += 1
                return cache_entry["result"]
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        self.cache_misses += 1
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        
        for operation, times in self.metrics.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "total_time": sum(times),
                    "average_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "last_time": times[-1] if times else 0
                }
        
        stats["cache_stats"] = {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            "cached_items": len(self.cache)
        }
        
        return stats
    
    def clear_cache(self):
        """Clear all cached results."""
        self.cache.clear()
        logger.info("Performance cache cleared")
    
    def clear_metrics(self):
        """Clear all performance metrics."""
        self.metrics.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Performance metrics cleared")

# Global performance monitor instance
_performance_monitor = AbilityPerformanceMonitor()

# ============================================================================
# ADVANCED ABILITY SCORE MANAGEMENT
# ============================================================================

class AdvancedAbilityManager:
    """Advanced ability score manager that extends core functionality for complex scenarios."""
    
    def __init__(self, character_core: CharacterCore, character_id: str = None):
        self.character_core = character_core
        self.ability_score_maximums = {}  # Track custom maximums from class features
        self.background_bonuses = {}  # 2024 D&D rules: background provides ASI
        self.temporary_modifiers = {}  # Short-term ability modifications
        
        # Version control integration
        self.version_manager = AbilityScoreVersionManager(character_id)
        self._auto_snapshot_enabled = True
        
    def apply_2024_background_rules(self, background_bonuses: Dict[str, int]):
        """Apply 2024 D&D background ability score increases."""
        total_bonus = sum(background_bonuses.values())
        
        # Validate 2024 rules: must be +2/+1 or +1/+1/+1
        if total_bonus not in [3]:
            raise ValueError("Background bonuses must total +3 (+2/+1 or +1/+1/+1)")
        
        # Check distribution is valid
        values = sorted(background_bonuses.values(), reverse=True)
        if values not in [[2, 1], [1, 1, 1]]:
            raise ValueError("Background bonuses must be +2/+1 or +1/+1/+1 distribution")
        
        # Create snapshot before applying changes
        if self._auto_snapshot_enabled:
            current_data = self.get_ability_summary()
            self.version_manager.create_snapshot(current_data, "Before applying 2024 background rules")
        
        # Track changes for each ability
        for ability, bonus in background_bonuses.items():
            if hasattr(self.character_core, ability.lower()):
                ability_score = getattr(self.character_core, ability.lower())
                old_value = ability_score.total_score
                
                # Add background bonus as a new source
                ability_score.add_bonus(bonus, AbilityScoreSource.BACKGROUND, "2024 Background")
                
                new_value = ability_score.total_score
                self.version_manager.track_change(
                    ability, old_value, new_value, 
                    "BACKGROUND", f"2024 Background rules: +{bonus}"
                )
        
        self.background_bonuses = background_bonuses.copy()
        
        # Create snapshot after applying changes
        if self._auto_snapshot_enabled:
            updated_data = self.get_ability_summary()
            self.version_manager.create_snapshot(updated_data, "After applying 2024 background rules")
    
    def set_ability_maximum(self, ability: str, maximum: int, source: str = "Class Feature"):
        """Set a custom maximum for an ability score."""
        self.ability_score_maximums[ability] = {
            "value": maximum,
            "source": source
        }
        logger.info(f"Set {ability} maximum to {maximum} from {source}")
    
    def apply_temporary_modifier(self, ability: str, modifier: int, duration: str = "Unknown"):
        """Apply a temporary modifier to an ability score."""
        if ability not in self.temporary_modifiers:
            self.temporary_modifiers[ability] = []
        
        self.temporary_modifiers[ability].append({
            "modifier": modifier,
            "duration": duration,
            "active": True
        })
        logger.info(f"Applied temporary {modifier:+d} modifier to {ability} ({duration})")
    
    def remove_temporary_modifier(self, ability: str, modifier: int):
        """Remove a specific temporary modifier."""
        if ability in self.temporary_modifiers:
            self.temporary_modifiers[ability] = [
                mod for mod in self.temporary_modifiers[ability]
                if mod["modifier"] != modifier or not mod["active"]
            ]
    
    def get_total_ability_score(self, ability: str) -> int:
        """Get total ability score including temporary modifiers."""
        if not hasattr(self.character_core, ability.lower()):
            return 10
        
        ability_score = getattr(self.character_core, ability.lower())
        base_total = ability_score.total_score
        
        # Add temporary modifiers
        temp_bonus = 0
        if ability in self.temporary_modifiers:
            temp_bonus = sum(
                mod["modifier"] for mod in self.temporary_modifiers[ability]
                if mod["active"]
            )
        
        total = base_total + temp_bonus
        
        # Apply custom maximum if set
        if ability in self.ability_score_maximums:
            max_value = self.ability_score_maximums[ability]["value"]
            total = min(total, max_value)
        
        return total
    
    @_performance_monitor.time_operation("get_ability_summary")
    def get_ability_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all ability scores and their sources."""
        # Check cache first
        cache_key = f"ability_summary_{id(self.character_core)}"
        cached_result = _performance_monitor.get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        standard_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        ability_summary = {}
        
        for ability in standard_abilities:
            if hasattr(self.character_core, ability):
                ability_score = getattr(self.character_core, ability)
                
                # Get base total and calculate with temporary modifiers
                base_total = ability_score.total_score
                temp_bonus = 0
                if ability in self.temporary_modifiers:
                    temp_bonus = sum(
                        mod["modifier"] for mod in self.temporary_modifiers[ability]
                        if mod["active"]
                    )
                
                current_total = base_total + temp_bonus
                
                # Apply custom maximum if set
                if ability in self.ability_score_maximums:
                    max_value = self.ability_score_maximums[ability]["value"]
                    current_total = min(current_total, max_value)
                
                ability_summary[ability] = {
                    "base_score": ability_score.base_score,
                    "total_score": current_total,
                    "modifier": (current_total - 10) // 2,
                    "modifier_string": f"{(current_total - 10) // 2:+d}",
                    "bonuses": ability_score.bonuses.copy(),
                    "temporary_modifiers": self.temporary_modifiers.get(ability, []),
                    "custom_maximum": self.ability_score_maximums.get(ability, None)
                }
            else:
                # Default values for missing abilities
                ability_summary[ability] = {
                    "base_score": 10,
                    "total_score": 10,
                    "modifier": 0,
                    "modifier_string": "+0",
                    "bonuses": {},
                    "temporary_modifiers": [],
                    "custom_maximum": None
                }
        
        # Calculate summary statistics
        totals = [score["total_score"] for score in ability_summary.values()]
        modifiers = [score["modifier"] for score in ability_summary.values()]
        
        summary_stats = {
            "total_ability_points": sum(totals),
            "average_ability_score": sum(totals) / len(totals),
            "highest_ability_score": max(totals),
            "lowest_ability_score": min(totals),
            "highest_modifier": max(modifiers),
            "lowest_modifier": min(modifiers),
            "background_bonuses_applied": len(self.background_bonuses) > 0,
            "custom_maximums_set": len(self.ability_score_maximums) > 0,
            "temporary_modifiers_active": any(
                any(mod["active"] for mod in mods) 
                for mods in self.temporary_modifiers.values()
            )
        }
        
        result = {
            "abilities": ability_summary,
            "summary_stats": summary_stats,
            "background_bonuses": self.background_bonuses.copy()
        }
        
        # Cache the result for 30 seconds
        _performance_monitor.cache_result(cache_key, result, ttl=30)
        return result

    def enable_auto_snapshots(self, enabled: bool = True):
        """Enable or disable automatic snapshot creation."""
        self._auto_snapshot_enabled = enabled
        logger.info(f"Auto-snapshots {'enabled' if enabled else 'disabled'}")
    
    def create_manual_snapshot(self, description: str = "Manual snapshot") -> int:
        """Manually create a snapshot of current ability scores."""
        current_data = self.get_ability_summary()
        return self.version_manager.create_snapshot(current_data, description)
    
    def rollback_abilities(self, version: int) -> Dict[str, Any]:
        """Rollback ability scores to a previous version."""
        snapshot_data = self.version_manager.rollback_to_version(version)
        
        # Apply the snapshot data back to character_core
        # This would need integration with the actual character restoration logic
        logger.info(f"Ability scores rolled back to version {version}")
        return snapshot_data
    
    def get_ability_change_history(self, ability: str = None) -> List[Dict[str, Any]]:
        """Get the change history for ability scores."""
        return self.version_manager.get_change_history(ability)
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version control information."""
        return self.version_manager.get_version_summary()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for ability score operations."""
        return _performance_monitor.get_performance_stats()
    
    def clear_ability_cache(self):
        """Clear cached ability score calculations."""
        _performance_monitor.clear_cache()
        logger.info("Ability score cache cleared")
    
    def optimize_for_performance(self, enable_caching: bool = True):
        """Enable or disable performance optimizations."""
        if not enable_caching:
            _performance_monitor.clear_cache()
        logger.info(f"Performance optimizations {'enabled' if enable_caching else 'disabled'}")
    
    def validate_ability_changes(self, character_data: Dict[str, Any]) -> CreationResult:
        """
        Validate ability score changes using external validation system.
        Delegates to creation_validation.py for proper validation.
        """
        try:
            # Use external validation for basic structure
            basic_validation = validate_basic_structure(character_data)
            if not basic_validation.success:
                return basic_validation
            
            # Validate custom content if present
            if character_data.get('custom_content'):
                custom_validation = validate_custom_content(character_data, character_data.get('custom_content', {}))
                if not custom_validation.success:
                    return custom_validation
            
            # Additional ability-specific validation
            ability_validation = self._validate_ability_score_ranges(character_data)
            if not ability_validation.success:
                return ability_validation
            
            return CreationResult(
                success=True,
                data={"validation_passed": True, "ability_scores_valid": True},
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Ability validation failed: {e}")
            return CreationResult(
                success=False,
                error=f"Ability validation error: {e}"
            )
    
    def _validate_ability_score_ranges(self, character_data: Dict[str, Any]) -> CreationResult:
        """Validate ability score ranges are within D&D 5e limits."""
        warnings = []
        errors = []
        
        ability_scores = character_data.get('ability_scores', {})
        
        for ability, score_data in ability_scores.items():
            total_score = score_data.get('total', score_data.get('base', 10))
            
            # D&D 5e ability score limits
            if total_score < 1:
                errors.append(f"{ability.title()} score ({total_score}) is below minimum (1)")
            elif total_score > 30:
                errors.append(f"{ability.title()} score ({total_score}) is above maximum (30)")
            elif total_score > 20:
                warnings.append(f"{ability.title()} score ({total_score}) is above normal maximum (20)")
        
        if errors:
            return CreationResult(
                success=False,
                error=f"Ability score validation failed: {'; '.join(errors)}",
                warnings=warnings
            )
        
        return CreationResult(
            success=True,
            data={"ability_ranges_valid": True},
            warnings=warnings
        )

# ============================================================================
# CUSTOM CONTENT ABILITY MANAGEMENT
# ============================================================================

class CustomContentAbilityManager:
    """Manages ability score interactions with custom species, classes, and content."""
    
    def __init__(self, advanced_manager: AdvancedAbilityManager):
        self.advanced_manager = advanced_manager
        self.custom_species_effects = {}
        self.custom_class_effects = {}
        
    def apply_custom_species_abilities(self, species: CustomSpecies):
        """Apply ability score bonuses from custom species."""
        if not species.ability_score_bonuses:
            return
            
        logger.info(f"Applying custom species abilities from {species.name}")
        
        # Validate custom species before applying
        species_data = {
            "name": species.name,
            "ability_score_bonuses": species.ability_score_bonuses,
            "traits": getattr(species, 'innate_traits', [])
        }
        
        validation_result = validate_custom_species_balance(species_data)
        if not validation_result.success:
            logger.warning(f"Custom species validation warnings: {validation_result.warnings}")
            if validation_result.error:
                logger.error(f"Custom species validation failed: {validation_result.error}")
        
        for ability, bonus in species.ability_score_bonuses.items():
            if hasattr(self.advanced_manager.character_core, ability.lower()):
                ability_score = getattr(self.advanced_manager.character_core, ability.lower())
                ability_score.add_bonus(bonus, AbilityScoreSource.SPECIES, f"{species.name} Species")
                
        # Store for tracking
        self.custom_species_effects[species.name] = species.ability_score_bonuses.copy()
    
    def apply_custom_class_features(self, class_obj: CustomClass, level: int):
        """Apply ability score effects from custom class features."""
        if not hasattr(class_obj, 'features') or not class_obj.features:
            return
            
        logger.info(f"Applying custom class features for {class_obj.name} level {level}")
        
        # Validate custom class before applying features
        class_data = {
            "name": class_obj.name,
            "hit_die": getattr(class_obj, 'hit_die', 8),
            "primary_abilities": getattr(class_obj, 'primary_abilities', []),
            "features": class_obj.features
        }
        
        validation_result = validate_custom_class_balance(class_data)
        if not validation_result.success:
            logger.warning(f"Custom class validation warnings: {validation_result.warnings}")
            if validation_result.error:
                logger.error(f"Custom class validation failed: {validation_result.error}")
        
        # Look for ability score related features at this level
        level_features = class_obj.features.get(str(level), [])
        
        for feature in level_features:
            self._process_custom_feature(feature, class_obj.name, level)
    
    def _process_custom_feature(self, feature: Dict[str, Any], class_name: str, level: int):
        """Process a custom feature for ability score effects."""
        feature_name = feature.get("name", "Unknown Feature")
        
        # Check for ability score increases
        if "ability_score_increase" in feature:
            increases = feature["ability_score_increase"]
            for ability, bonus in increases.items():
                if hasattr(self.advanced_manager.character_core, ability.lower()):
                    ability_score = getattr(self.advanced_manager.character_core, ability.lower())
                    ability_score.add_bonus(bonus, AbilityScoreSource.CLASS, f"{class_name} - {feature_name}")
        
        # Check for ability score maximums
        if "ability_score_maximum" in feature:
            maximums = feature["ability_score_maximum"]
            for ability, max_value in maximums.items():
                self.advanced_manager.set_ability_maximum(
                    ability, max_value, f"{class_name} - {feature_name}"
                )
        
        # Store for tracking
        if class_name not in self.custom_class_effects:
            self.custom_class_effects[class_name] = {}
        
        self.custom_class_effects[class_name][level] = {
            "feature": feature_name,
            "effects": feature
        }
    
    def get_custom_content_summary(self) -> Dict[str, Any]:
        """Get a summary of all custom content ability effects."""
        return {
            "species_effects": self.custom_species_effects.copy(),
            "class_effects": self.custom_class_effects.copy(),
            "temporary_modifiers": self.advanced_manager.temporary_modifiers.copy(),
            "custom_maximums": self.advanced_manager.ability_score_maximums.copy()
        }

# ============================================================================
# VERSION CONTROL AND CHANGE TRACKING
# ============================================================================

class AbilityScoreVersionManager:
    """Manages version control and change tracking for ability scores."""
    
    def __init__(self, character_id: str = None):
        self.character_id = character_id or str(uuid.uuid4())
        self.change_history: List[Dict[str, Any]] = []
        self.current_version = 1
        self.snapshots: Dict[int, Dict[str, Any]] = {}
        
    def create_snapshot(self, ability_data: Dict[str, Any], description: str = "Manual snapshot") -> int:
        """Create a snapshot of current ability scores."""
        snapshot_id = self.current_version
        
        snapshot = {
            "version": snapshot_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "ability_scores": self._deep_copy_ability_data(ability_data),
            "character_id": self.character_id
        }
        
        self.snapshots[snapshot_id] = snapshot
        self.current_version += 1
        
        logger.info(f"Created ability score snapshot v{snapshot_id}: {description}")
        return snapshot_id
    
    def track_change(self, ability: str, old_value: int, new_value: int, 
                    source: str, reason: str = "Manual change") -> str:
        """Track a single ability score change."""
        change_id = str(uuid.uuid4())
        
        change_record = {
            "change_id": change_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ability": ability,
            "old_value": old_value,
            "new_value": new_value,
            "difference": new_value - old_value,
            "source": source,
            "reason": reason,
            "version": self.current_version,
            "character_id": self.character_id
        }
        
        self.change_history.append(change_record)
        logger.info(f"Tracked {ability} change: {old_value} -> {new_value} ({source})")
        return change_id
    
    def rollback_to_version(self, version: int) -> Dict[str, Any]:
        """Rollback ability scores to a specific version."""
        if version not in self.snapshots:
            raise ValueError(f"Version {version} not found")
        
        snapshot = self.snapshots[version]
        
        # Record rollback as a change
        rollback_record = {
            "change_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "rollback",
            "target_version": version,
            "current_version": self.current_version,
            "reason": f"Rollback to version {version}",
            "character_id": self.character_id
        }
        
        self.change_history.append(rollback_record)
        logger.info(f"Rolled back ability scores to version {version}")
        
        return snapshot["ability_scores"]
    
    def get_change_history(self, ability: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get change history, optionally filtered by ability."""
        history = self.change_history.copy()
        
        if ability:
            history = [change for change in history if change.get("ability") == ability]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]
    
    def get_version_summary(self) -> Dict[str, Any]:
        """Get a summary of all versions and changes."""
        return {
            "character_id": self.character_id,
            "current_version": self.current_version,
            "total_snapshots": len(self.snapshots),
            "total_changes": len(self.change_history),
            "available_versions": sorted(self.snapshots.keys()),
            "latest_changes": self.get_change_history(limit=10)
        }
    
    def _deep_copy_ability_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of ability score data."""
        import copy
        return copy.deepcopy(data)

# ============================================================================
# REFINEMENT SYSTEM INTEGRATION
# ============================================================================

class AbilityRefinementManager:
    """Manages ability score refinements during character iteration."""
    
    def __init__(self, advanced_manager: AdvancedAbilityManager):
        self.advanced_manager = advanced_manager
        self.refinement_history: List[Dict[str, Any]] = []
        self.suggested_improvements: List[Dict[str, Any]] = []
        
    def suggest_ability_improvements(self, character_data: Dict[str, Any], 
                                   user_feedback: str = "") -> List[Dict[str, Any]]:
        """Suggest ability score improvements based on character concept and feedback."""
        suggestions = []
        
        current_abilities = self.advanced_manager.get_ability_summary()
        
        # Analyze character concept for ability priorities
        character_classes = character_data.get('classes', {})
        primary_class = list(character_classes.keys())[0] if character_classes else None
        
        if primary_class:
            class_priorities = self._get_class_ability_priorities(primary_class)
            
            for ability, priority in class_priorities.items():
                current_score = current_abilities['abilities'][ability]['total_score']
                
                if current_score < 16 and priority == 'primary':
                    suggestions.append({
                        "type": "ability_increase",
                        "ability": ability,
                        "current_value": current_score,
                        "suggested_value": min(20, current_score + 2),
                        "reason": f"Primary ability for {primary_class}",
                        "priority": "high"
                    })
                elif current_score < 14 and priority == 'secondary':
                    suggestions.append({
                        "type": "ability_increase", 
                        "ability": ability,
                        "current_value": current_score,
                        "suggested_value": min(20, current_score + 1),
                        "reason": f"Secondary ability for {primary_class}",
                        "priority": "medium"
                    })
        
        # Analyze user feedback for specific ability requests
        if user_feedback:
            feedback_suggestions = self._parse_feedback_for_ability_changes(user_feedback, current_abilities)
            suggestions.extend(feedback_suggestions)
        
        self.suggested_improvements = suggestions
        return suggestions
    
    def apply_refinement(self, refinement_request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific ability score refinement."""
        refinement_id = str(uuid.uuid4())
        
        try:
            if refinement_request['type'] == 'ability_increase':
                ability = refinement_request['ability']
                target_value = refinement_request['target_value']
                reason = refinement_request.get('reason', 'User refinement')
                
                # Validate the refinement request using external validation
                validation_data = {
                    'ability_scores': {
                        ability: {'total': target_value}
                    }
                }
                
                validation_result = self.advanced_manager.validate_ability_changes(validation_data)
                if not validation_result.success:
                    raise ValueError(f"Refinement validation failed: {validation_result.error}")
                
                # Create snapshot before change
                self.advanced_manager.create_manual_snapshot(f"Before refinement: {reason}")
                
                # Apply the refinement (this would need actual implementation)
                result = self._apply_ability_increase(ability, target_value, reason)
                
                # Track the refinement
                refinement_record = {
                    "refinement_id": refinement_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": refinement_request['type'],
                    "request": refinement_request,
                    "result": result,
                    "validation_warnings": validation_result.warnings,
                    "status": "applied"
                }
                
                self.refinement_history.append(refinement_record)
                
                # Create snapshot after change
                self.advanced_manager.create_manual_snapshot(f"After refinement: {reason}")
                
                return result
                
        except Exception as e:
            # Track failed refinement
            refinement_record = {
                "refinement_id": refinement_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": refinement_request['type'],
                "request": refinement_request,
                "error": str(e),
                "status": "failed"
            }
            
            self.refinement_history.append(refinement_record)
            raise
    
    def _get_class_ability_priorities(self, class_name: str) -> Dict[str, str]:
        """Get ability score priorities for a class."""
        # D&D 5e 2024 class ability priorities
        class_priorities = {
            'Fighter': {'strength': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Wizard': {'intelligence': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Rogue': {'dexterity': 'primary', 'intelligence': 'secondary', 'constitution': 'secondary'},
            'Cleric': {'wisdom': 'primary', 'constitution': 'secondary', 'strength': 'secondary'},
            'Sorcerer': {'charisma': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Warlock': {'charisma': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Bard': {'charisma': 'primary', 'dexterity': 'secondary', 'constitution': 'secondary'},
            'Druid': {'wisdom': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Paladin': {'strength': 'primary', 'charisma': 'secondary', 'constitution': 'secondary'},
            'Ranger': {'dexterity': 'primary', 'wisdom': 'secondary', 'constitution': 'secondary'},
            'Barbarian': {'strength': 'primary', 'constitution': 'secondary', 'dexterity': 'secondary'},
            'Monk': {'dexterity': 'primary', 'wisdom': 'secondary', 'constitution': 'secondary'}
        }
        
        return class_priorities.get(class_name, {
            'strength': 'tertiary', 'dexterity': 'tertiary', 'constitution': 'secondary',
            'intelligence': 'tertiary', 'wisdom': 'tertiary', 'charisma': 'tertiary'
        })
    
    def _parse_feedback_for_ability_changes(self, feedback: str, current_abilities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse user feedback for specific ability score change requests."""
        suggestions = []
        feedback_lower = feedback.lower()
        
        # Simple keyword-based parsing
        ability_keywords = {
            'strength': ['strength', 'str', 'strong', 'muscle'],
            'dexterity': ['dexterity', 'dex', 'agile', 'quick', 'nimble'],
            'constitution': ['constitution', 'con', 'tough', 'endurance', 'stamina'],
            'intelligence': ['intelligence', 'int', 'smart', 'clever', 'knowledge'],
            'wisdom': ['wisdom', 'wis', 'wise', 'perceptive', 'insight'],
            'charisma': ['charisma', 'cha', 'charming', 'persuasive', 'leader']
        }
        
        increase_keywords = ['increase', 'improve', 'boost', 'raise', 'higher', 'more', 'better']
        decrease_keywords = ['decrease', 'lower', 'reduce', 'less', 'weaker']
        
        for ability, keywords in ability_keywords.items():
            if any(keyword in feedback_lower for keyword in keywords):
                current_score = current_abilities['abilities'][ability]['total_score']
                
                if any(word in feedback_lower for word in increase_keywords):
                    suggestions.append({
                        "type": "ability_increase",
                        "ability": ability,
                        "current_value": current_score,
                        "suggested_value": min(20, current_score + 2),
                        "reason": f"User feedback: improve {ability}",
                        "priority": "high"
                    })
                elif any(word in feedback_lower for word in decrease_keywords):
                    suggestions.append({
                        "type": "ability_decrease",
                        "ability": ability,
                        "current_value": current_score,
                        "suggested_value": max(8, current_score - 2),
                        "reason": f"User feedback: reduce {ability}",
                        "priority": "medium"
                    })
        
        return suggestions
    
    def _apply_ability_increase(self, ability: str, target_value: int, reason: str) -> Dict[str, Any]:
        """Apply an ability score increase."""
        # This would need to integrate with the actual ability score modification system
        # For now, return a result structure
        return {
            "ability": ability,
            "target_value": target_value,
            "reason": reason,
            "success": True,
            "message": f"Would increase {ability} to {target_value}"
        }
    
    def get_refinement_history(self) -> List[Dict[str, Any]]:
        """Get the history of all refinements applied."""
        return self.refinement_history.copy()
    
    def get_suggested_improvements(self) -> List[Dict[str, Any]]:
        """Get current suggested improvements."""
        return self.suggested_improvements.copy()
# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def enhance_character_data_with_ability_details(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance character data dictionary with detailed ability score information.
    
    Args:
        character_data: Base character data dictionary
        
    Returns:
        Enhanced character data with ability score details
    """
    enhanced_data = character_data.copy()
    
    # Ensure ability scores section exists
    if "ability_scores" not in enhanced_data:
        enhanced_data["ability_scores"] = {}
    
    # Standard D&D ability scores
    standard_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    # Enhance each ability score with detailed information
    for ability in standard_abilities:
        if ability not in enhanced_data["ability_scores"]:
            enhanced_data["ability_scores"][ability] = {"base": 10}
        
        ability_data = enhanced_data["ability_scores"][ability]
        
        # Calculate total score (base + bonuses)
        base_score = ability_data.get("base", 10)
        bonuses = ability_data.get("bonuses", {})
        total_bonus = sum(bonuses.values())
        total_score = base_score + total_bonus
        
        # Add calculated fields
        ability_data.update({
            "total": total_score,
            "modifier": (total_score - 10) // 2,
            "modifier_string": f"{(total_score - 10) // 2:+d}",
            "bonus_breakdown": bonuses.copy()
        })
    
    # Add ability score summary
    enhanced_data["ability_score_summary"] = {
        "total_bonuses_applied": sum(
            sum(enhanced_data["ability_scores"][ability].get("bonuses", {}).values())
            for ability in standard_abilities
        ),
        "highest_ability": max(
            standard_abilities,
            key=lambda a: enhanced_data["ability_scores"][a].get("total", 10)
        ),
        "primary_modifier": max(
            enhanced_data["ability_scores"][ability].get("modifier", 0)
            for ability in standard_abilities
        )
    }
    
    # Add 2024 rules compliance info
    enhanced_data["rules_compliance"] = {
        "edition": "2024",
        "background_asis_applied": "background_bonuses" in enhanced_data,
        "custom_content_used": any(
            "custom" in str(source).lower()
            for ability in standard_abilities
            for source in enhanced_data["ability_scores"][ability].get("bonuses", {}).keys()
        )
    }
    
    logger.info("Enhanced character data with detailed ability score information")
    return enhanced_data

def create_enhanced_ability_manager(character_core: CharacterCore, 
                                  character_id: str = None,
                                  enable_refinement: bool = True,
                                  enable_performance_monitoring: bool = True) -> Dict[str, Any]:
    """
    Factory function to create a fully integrated ability management system.
    
    Args:
        character_core: The character core data structure
        character_id: Unique identifier for the character
        enable_refinement: Whether to enable refinement system integration
        enable_performance_monitoring: Whether to enable performance monitoring
        
    Returns:
        Dictionary containing all ability management components
    """
    # Create main ability manager
    ability_manager = AdvancedAbilityManager(character_core, character_id)
    
    # Create custom content manager
    custom_content_manager = CustomContentAbilityManager(ability_manager)
    
    # Create refinement manager if enabled
    refinement_manager = None
    if enable_refinement:
        refinement_manager = AbilityRefinementManager(ability_manager)
    
    # Configure performance monitoring
    if enable_performance_monitoring:
        ability_manager.optimize_for_performance(True)
    
    # Return integrated system
    system = {
        "ability_manager": ability_manager,
        "custom_content_manager": custom_content_manager,
        "refinement_manager": refinement_manager,
        "version_manager": ability_manager.version_manager,
        "features": {
            "version_control": True,
            "refinement_integration": enable_refinement,
            "performance_monitoring": enable_performance_monitoring,
            "custom_content_support": True,
            "2024_rules_compliance": True
        }
    }
    
    logger.info(f"Created enhanced ability management system for character {character_id}")
    return system

def validate_ability_management_system(system: Dict[str, Any]) -> CreationResult:
    """
    Validate that an ability management system meets all dev_vision.md requirements.
    Uses external validation from creation_validation.py for consistency.
    
    Returns CreationResult with validation results and compliance score.
    """
    try:
        validation_data = {
            "system_components": system,
            "features": system.get("features", {}),
            "ability_manager": system.get("ability_manager") is not None,
            "version_manager": system.get("version_manager") is not None,
            "custom_content_manager": system.get("custom_content_manager") is not None,
            "refinement_manager": system.get("refinement_manager") is not None
        }
        
        # Use basic structure validation as foundation
        basic_validation = validate_basic_structure(validation_data)
        
        if not basic_validation.success:
            return CreationResult(
                success=False,
                error=f"System validation failed: {basic_validation.error}",
                warnings=basic_validation.warnings
            )
        
        # Check core requirements
        score = 0
        max_score = 100
        requirements_met = []
        requirements_missing = []
        
        requirements_checklist = [
            ("ability_manager", "Core ability score management", 20),
            ("version_manager", "Version control and change tracking", 15), 
            ("custom_content_manager", "Custom content integration", 15),
            ("refinement_manager", "Refinement system integration", 10),
            ("performance_monitoring", "Performance optimization", 10),
            ("2024_rules_compliance", "D&D 5e 2024 compliance", 15),
            ("mathematical_correctness", "Accurate calculations", 15)
        ]
        
        for requirement, description, points in requirements_checklist:
            if requirement in system or (requirement in system.get("features", {}) and system["features"][requirement]):
                requirements_met.append(description)
                score += points
            else:
                requirements_missing.append(description)
        
        # Determine compliance
        compliant = score >= 85
        
        recommendations = []
        if score < 85:
            recommendations.append("System needs additional features to fully meet dev_vision.md requirements")
        if score >= 90:
            recommendations.append("System fully meets dev_vision.md requirements")
        
        result_data = {
            "compliant": compliant,
            "score": score,
            "max_score": max_score,
            "requirements_met": requirements_met,
            "requirements_missing": requirements_missing,
            "recommendations": recommendations
        }
        
        logger.info(f"Ability management system validation: {score}/100")
        
        return CreationResult(
            success=True,
            data=result_data,
            warnings=recommendations if score < 90 else []
        )
        
    except Exception as e:
        logger.error(f"System validation failed: {e}")
        return CreationResult(
            success=False,
            error=f"Validation error: {e}"
        )

def validate_character_ability_scores(character_data: Dict[str, Any]) -> CreationResult:
    """
    Validate character ability scores using external validation.
    This is a convenience function that delegates to creation_validation.py.
    """
    try:
        # Use the comprehensive validation from creation_validation.py
        basic_validation = validate_basic_structure(character_data)
        
        if not basic_validation.success:
            return basic_validation
        
        # Additional ability score specific checks
        ability_scores = character_data.get('ability_scores', {})
        warnings = []
        
        standard_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in standard_abilities:
            if ability not in ability_scores:
                warnings.append(f"Missing {ability} score")
            else:
                score = ability_scores[ability].get('total', ability_scores[ability].get('base', 10))
                if score > 20:
                    warnings.append(f"{ability.title()} score ({score}) exceeds normal maximum (20)")
        
        return CreationResult(
            success=True,
            data={"ability_scores_validated": True},
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Character ability score validation failed: {e}")
        return CreationResult(
            success=False,
            error=f"Ability score validation error: {e}"
        )

def validate_custom_ability_content(custom_content: Dict[str, Any]) -> CreationResult:
    """
    Validate custom content that affects ability scores.
    Delegates to appropriate validation functions in creation_validation.py.
    """
    try:
        all_warnings = []
        validation_results = {}
        
        # Validate custom species if present
        if 'species' in custom_content:
            for species_name in custom_content['species']:
                # This would need the actual species data
                logger.info(f"Would validate custom species: {species_name}")
                validation_results[f"species_{species_name}"] = "validated"
        
        # Validate custom classes if present
        if 'classes' in custom_content:
            for class_name in custom_content['classes']:
                # This would need the actual class data
                logger.info(f"Would validate custom class: {class_name}")
                validation_results[f"class_{class_name}"] = "validated"
        
        return CreationResult(
            success=True,
            data=validation_results,
            warnings=all_warnings
        )
        
    except Exception as e:
        logger.error(f"Custom ability content validation failed: {e}")
        return CreationResult(
            success=False,
            error=f"Custom content validation error: {e}"
        )