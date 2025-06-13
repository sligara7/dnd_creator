from typing import Dict, List, Any, Optional
from ...core.entities.character import Character
from ...core.value_objects.validation_result import ValidationIssue, ValidationSeverity

class MulticlassRules:
    """D&D 5e multiclassing rules implementation."""
    
    def __init__(self):
        self.multiclass_prerequisites = self._initialize_prerequisites()
        self.feature_interactions = self._initialize_feature_interactions()
    
    def _initialize_prerequisites(self) -> Dict[str, Dict[str, Any]]:
        """Initialize multiclass prerequisites for all classes."""
        return {
            "Barbarian": {
                "abilities": {"strength": 13},
                "restrictions": ["Cannot cast spells while raging"]
            },
            "Bard": {
                "abilities": {"charisma": 13},
                "benefits": ["Jack of All Trades stacks with proficiencies"]
            },
            "Cleric": {
                "abilities": {"wisdom": 13},
                "requirements": ["Must have a deity"]
            },
            "Druid": {
                "abilities": {"wisdom": 13},
                "restrictions": ["Cannot wear metal armor"]
            },
            "Fighter": {
                "abilities": {"strength": 13, "dexterity": 13},  # Either/or
                "benefits": ["Action Surge stacks with other actions"]
            },
            "Monk": {
                "abilities": {"dexterity": 13, "wisdom": 13},  # Both required
                "restrictions": ["Unarmored Defense doesn't stack", "Cannot use martial arts in armor"]
            },
            "Paladin": {
                "abilities": {"strength": 13, "charisma": 13},  # Both required
                "requirements": ["Must follow oath tenets"]
            },
            "Ranger": {
                "abilities": {"dexterity": 13, "wisdom": 13},  # Both required
                "benefits": ["Fighting Style stacks with other fighting styles"]
            },
            "Rogue": {
                "abilities": {"dexterity": 13},
                "benefits": ["Sneak Attack damage stacks with levels"]
            },
            "Sorcerer": {
                "abilities": {"charisma": 13},
                "benefits": ["Sorcery Points for spell slot manipulation"]
            },
            "Warlock": {
                "abilities": {"charisma": 13},
                "requirements": ["Must have a patron"],
                "special": ["Pact Magic uses different spell slot rules"]
            },
            "Wizard": {
                "abilities": {"intelligence": 13},
                "benefits": ["Ritual casting without preparing spells"]
            }
        }
    
    def _initialize_feature_interactions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known feature interactions."""
        return {
            "unarmored_defense": {
                "classes": ["Barbarian", "Monk"],
                "rule": "Choose one version, they don't stack",
                "calculation": {
                    "Barbarian": "10 + Dex + Con",
                    "Monk": "10 + Dex + Wis"
                }
            },
            "extra_attack": {
                "classes": ["Barbarian", "Fighter", "Monk", "Paladin", "Ranger"],
                "rule": "Extra Attack doesn't stack, but Fighter gets additional attacks",
                "levels": {
                    "Fighter": [5, 11, 20],  # 2, 3, 4 attacks
                    "Other": [5]  # 2 attacks only
                }
            },
            "spellcasting": {
                "full_casters": ["Bard", "Cleric", "Druid", "Sorcerer", "Wizard"],
                "half_casters": ["Paladin", "Ranger"],
                "rule": "Add levels for spell slots, but spells known/prepared separate"
            },
            "pact_magic": {
                "classes": ["Warlock"],
                "rule": "Pact Magic slots separate from Spellcasting slots"
            }
        }
    
    def validate_multiclass_combination(self, class_combination: List[str]) -> List[ValidationIssue]:
        """Validate a multiclass combination for potential issues."""
        issues = []
        
        # Check for problematic combinations
        if "Barbarian" in class_combination:
            spellcasting_classes = ["Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"]
            conflicting_casters = [cls for cls in class_combination if cls in spellcasting_classes]
            
            if conflicting_casters:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="RAGE_SPELLCASTING_CONFLICT",
                    message=f"Barbarian Rage prevents spellcasting from {', '.join(conflicting_casters)}",
                    suggested_fix="Consider how Rage affects spellcasting classes"
                ))
        
        # Check for Unarmored Defense conflicts
        unarmored_classes = [cls for cls in class_combination if cls in ["Barbarian", "Monk"]]
        if len(unarmored_classes) > 1:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="UNARMORED_DEFENSE_CONFLICT",
                message="Multiple Unarmored Defense features don't stack",
                suggested_fix="Choose which Unarmored Defense calculation to use"
            ))
        
        return issues
    
    def calculate_optimal_progression(self, classes: List[str], 
                                    target_level: int,
                                    priorities: Dict[str, int]) -> List[str]:
        """Calculate optimal level progression for multiclass build."""
        progression = []
        
        # This would implement complex optimization logic
        # For now, return a basic alternating pattern
        
        class_cycle = classes.copy()
        for level in range(1, target_level + 1):
            if level == 1:
                # First level should be the primary class
                primary_class = max(priorities.items(), key=lambda x: x[1])[0]
                progression.append(primary_class)
            else:
                # Rotate through classes based on priorities
                next_class = class_cycle[level % len(class_cycle)]
                progression.append(next_class)
        
        return progression
    
    def get_multiclass_breakpoints(self, classes: List[str]) -> Dict[str, List[int]]:
        """Get important level breakpoints for multiclass build."""
        breakpoints = {}
        
        class_breakpoints = {
            "Barbarian": [1, 2, 3, 5, 6, 9, 11, 14, 15, 17, 20],
            "Bard": [1, 2, 3, 4, 5, 6, 10, 14, 18, 20],
            "Cleric": [1, 2, 5, 6, 8, 10, 11, 14, 17, 19],
            "Druid": [1, 2, 4, 6, 8, 10, 14, 18, 20],
            "Fighter": [1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 18, 20],
            "Monk": [1, 2, 3, 4, 5, 6, 11, 14, 18, 20],
            "Paladin": [1, 2, 3, 5, 6, 7, 11, 14, 15, 18, 20],
            "Ranger": [1, 2, 3, 5, 6, 7, 11, 14, 15, 18, 20],
            "Rogue": [1, 2, 3, 4, 5, 9, 13, 17, 20],
            "Sorcerer": [1, 2, 3, 5, 6, 14, 18, 20],
            "Warlock": [1, 2, 3, 5, 6, 7, 9, 11, 12, 15, 17, 20],
            "Wizard": [1, 2, 5, 6, 10, 11, 14, 18, 20]
        }
        
        for class_name in classes:
            if class_name in class_breakpoints:
                breakpoints[class_name] = class_breakpoints[class_name]
        
        return breakpoints