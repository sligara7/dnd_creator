from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ...core.entities.character import Character
from ...core.utils.character_utils import CharacterValidator
from ..rules.character_creation import CharacterCreationRules

logger = logging.getLogger(__name__)

class CharacterUtilityService:
    """
    Domain service for character utility operations.
    
    Contains business logic for character manipulation that doesn't
    fit into other specific services.
    """
    
    def __init__(self):
        self.creation_rules = CharacterCreationRules()
    
    def generate_random_character(self, constraints: Optional[Dict[str, Any]] = None) -> Character:
        """Generate a random character based on constraints."""
        # Implementation for random character generation
        pass
    
    def clone_character(self, character: Character, new_name: Optional[str] = None) -> Character:
        """Create a copy of an existing character."""
        # Create a deep copy of the character
        cloned_data = character.to_dict()
        cloned_data["name"] = new_name or f"{character.name} (Copy)"
        cloned_data["created_at"] = datetime.now().isoformat()
        cloned_data["last_modified"] = datetime.now().isoformat()
        
        return Character.from_dict(cloned_data)
    
    def merge_characters(self, base_character: Character, 
                        override_character: Character) -> Character:
        """Merge two characters, with override taking precedence."""
        # Implementation for merging character data
        pass
    
    def calculate_character_point_buy_cost(self, ability_scores: Dict[str, int]) -> int:
        """Calculate point buy cost for ability score array."""
        point_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5,
            14: 7, 15: 9
        }
        
        total_cost = 0
        for ability, score in ability_scores.items():
            if score in point_costs:
                total_cost += point_costs[score]
            else:
                raise ValueError(f"Invalid point buy score: {score}")
        
        return total_cost
    
    def suggest_ability_score_improvements(self, character: Character) -> List[Dict[str, Any]]:
        """Suggest ability score improvements for character optimization."""
        suggestions = []
        
        # Suggest improving primary ability scores
        primary_abilities = self._get_primary_abilities_for_classes(character.character_classes)
        
        for ability in primary_abilities:
            current_score = character.get_ability_score_value(ability)
            if current_score < 20 and current_score % 2 == 1:  # Odd scores benefit most
                suggestions.append({
                    "type": "ability_improvement",
                    "ability": ability,
                    "current_score": current_score,
                    "suggested_increase": 1,
                    "reason": f"Improve {ability} modifier for {character.primary_class}"
                })
        
        return suggestions
    
    def validate_character_build(self, character: Character) -> Dict[str, Any]:
        """Comprehensive character build validation."""
        issues = []
        warnings = []
        suggestions = []
        
        # Basic validation
        basic_errors = CharacterValidator.validate_level_data(character.character_classes)
        issues.extend(basic_errors)
        
        # Advanced validation
        if character.is_multiclass:
            multiclass_issues = self._validate_multiclass_build(character)
            issues.extend(multiclass_issues)
        
        # Optimization suggestions
        optimization_suggestions = self.suggest_ability_score_improvements(character)
        suggestions.extend(optimization_suggestions)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _get_primary_abilities_for_classes(self, classes: Dict[str, int]) -> List[str]:
        """Get primary abilities for character classes."""
        primary_abilities = set()
        
        class_abilities = {
            "Fighter": ["strength", "dexterity"],
            "Wizard": ["intelligence"],
            "Cleric": ["wisdom"],
            "Rogue": ["dexterity"],
            "Ranger": ["dexterity", "wisdom"],
            # ... more class mappings
        }
        
        for class_name in classes.keys():
            if class_name in class_abilities:
                primary_abilities.update(class_abilities[class_name])
        
        return list(primary_abilities)
    
    def _validate_multiclass_build(self, character: Character) -> List[str]:
        """Validate multiclass character build."""
        issues = []
        # Implementation for multiclass validation
        return issues