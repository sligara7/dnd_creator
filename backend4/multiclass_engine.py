from typing import Dict, Any, Tuple
import logging

from abstract_multiclass_and_level_up import DNDMulticlassAndLevelUp
from .content_registry import ContentRegistry

logger = logging.getLogger(__name__)

class MulticlassEngine:
    """Handles all multiclass and level-up operations."""
    
    def __init__(self):
        self.content_registry = ContentRegistry()
    
    def calculate_level_up_changes(self, current_character: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """Calculate changes when a character levels up."""
        handler = DNDMulticlassAndLevelUp(current_character)
        return handler.calculate_level_up_changes(current_character, new_level)
    
    def validate_multiclass_eligibility(self, character_data: Dict[str, Any], new_class: str) -> Tuple[bool, str]:
        """Validate if character can multiclass into a new class."""
        handler = DNDMulticlassAndLevelUp(character_data)
        return handler.can_multiclass_into(new_class)
    
    def calculate_spell_slots(self, character_data: Dict[str, Any]) -> Dict[int, int]:
        """Calculate spell slots for multiclass spellcasters."""
        handler = DNDMulticlassAndLevelUp(character_data)
        return handler.get_multiclass_spell_slots()
    
    def get_level_up_options(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available options when leveling up."""
        handler = DNDMulticlassAndLevelUp(character_data)
        current_level = handler.calculate_character_level()
        
        # Check if character can level up
        can_level, message = handler.check_level_up_eligibility()
        if not can_level:
            return {"can_level_up": False, "message": message}
        
        # Get available classes for multiclassing
        available_classes = handler.get_available_classes_for_multiclass()
        current_classes = list(character_data.get("classes", {}).keys())
        
        return {
            "can_level_up": True,
            "current_level": current_level,
            "next_level": current_level + 1,
            "xp_needed": handler.get_next_level_xp_threshold(),
            "current_classes": current_classes,
            "multiclass_options": {
                class_name: eligible for class_name, eligible in available_classes.items()
                if class_name not in current_classes
            },
            "level_up_in_existing": {
                class_name: f"Continue as {class_name}"
                for class_name in current_classes
            }
        }
    
    def apply_level_up(self, character_data: Dict[str, Any], level_up_choices: Dict[str, Any]) -> Dict[str, Any]:
        """Apply level up choices to character data."""
        handler = DNDMulticlassAndLevelUp(character_data)
        
        # Determine which class to level up in
        target_class = level_up_choices.get("class")
        if not target_class:
            # Default to primary class
            classes = character_data.get("classes", {})
            if classes:
                target_class = max(classes.items(), key=lambda x: x[1])[0]
            else:
                return {"error": "No class specified and no existing classes found"}
        
        # Perform the level up
        level_up_result = handler.level_up(target_class if target_class not in character_data.get("classes", {}) else None)
        
        if "error" in level_up_result:
            return level_up_result
        
        # Apply choices
        if level_up_choices:
            success = handler.apply_level_up_choices(level_up_choices)
            if not success:
                return {"error": "Failed to apply level up choices"}
        
        # Return updated character data
        updated_data = character_data.copy()
        updated_data.update({
            "level": level_up_result["new_level"],
            "classes": level_up_result["new_class_levels"],
            "experience_points": character_data.get("experience_points", 0)
        })
        
        return {
            "success": True,
            "updated_character": updated_data,
            "level_up_summary": level_up_result
        }