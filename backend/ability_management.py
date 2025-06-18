# ## **4. `ability_management.py`**
# **Advanced ability score progression system**
# - **Classes**: `AdvancedAbilityManager`, `CustomContentAbilityManager`
# - **Functions**: `enhance_character_data_with_ability_details`
# - **Purpose**: Enhanced ability score tracking, custom content ability interactions, 2024 D&D rule compliance
# - **Dependencies**: `core_models.py`, `custom_content_models.py`, `character_models.py`

from typing import Dict, Any, List, Optional
import logging

# Import from other modules
from core_models import ASIManager, CharacterLevelManager, AbilityScore, AbilityScoreSource
from custom_content_models import CustomSpecies, CustomClass
from character_models import CharacterCore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ADVANCED ABILITY SCORE MANAGEMENT
# ============================================================================

class AdvancedAbilityManager:
    """Advanced ability score manager that extends core functionality for complex scenarios."""
    
    def __init__(self, character_core: CharacterCore):
        self.character_core = character_core
        self.ability_score_maximums = {}  # Track custom maximums from class features
        self.background_bonuses = {}  # 2024 D&D rules: background provides ASI
        self.temporary_modifiers = {}  # Short-term ability modifications
        
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
        
        self.background_bonuses = background_bonuses.copy()
        
        # Apply the bonuses to character
        for ability, bonus in background_bonuses.items():
            if hasattr(self.character_core, ability.lower()):
                ability_score = getattr(self.character_core, ability.lower())
                # Add background bonus as a new source
                ability_score.add_bonus(bonus, AbilityScoreSource.BACKGROUND, "2024 Background")
    
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
    
    def get_ability_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all ability scores and their sources."""
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
        
        return {
            "abilities": ability_summary,
            "summary_stats": summary_stats,
            "background_bonuses": self.background_bonuses.copy()
        }

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