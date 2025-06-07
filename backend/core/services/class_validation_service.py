import logging
from typing import Dict, List, Any, Tuple, Optional
from backend.core.classes.class_models import CustomClass, SpellcastingType

logger = logging.getLogger(__name__)

class ClassValidationService:
    """
    Service for validating and ensuring balance of custom character classes.
    Acts as a checkpoint in the iterative class creation process.
    """
    
    def __init__(self, llm_service=None):
        """Initialize with optional LLM service for complex validations"""
        self.llm_service = llm_service
        
        # Define balance constraints
        self.balance_constraints = {
            "hit_die": {
                "min": 6,
                "max": 12,
                "valid_values": [6, 8, 10, 12]
            },
            "saving_throws": {
                "max_count": 2,
                "strong_saves": ["Dexterity", "Constitution", "Wisdom"],
                "weak_saves": ["Strength", "Intelligence", "Charisma"],
                "recommended_pattern": "1 strong + 1 weak"
            },
            "features_per_level": {
                "max": {
                    "1": 3,  # Level 1: max 3 features
                    "default": 2   # Other levels: max 2 features
                }
            }
        }
    
    def validate_class(self, custom_class: CustomClass, 
                      validation_level: str = "standard") -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a custom class for balance and adherence to D&D design principles.
        
        Args:
            custom_class: The class to validate
            validation_level: Level of strictness ("minimal", "standard", "strict")
            
        Returns:
            Tuple of (is_valid, issues) where issues is a list of problems found
        """
        issues = []
        
        # Run applicable validation checks based on level
        if validation_level in ["minimal", "standard", "strict"]:
            issues.extend(self._validate_basic_structure(custom_class))
            
        if validation_level in ["standard", "strict"]:
            issues.extend(self._validate_game_balance(custom_class))
            
        if validation_level == "strict":
            issues.extend(self._validate_advanced_balance(custom_class))
            
        # Determine if the class is valid
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        is_valid = len(critical_issues) == 0
        
        return is_valid, issues
    
    def _validate_basic_structure(self, custom_class: CustomClass) -> List[Dict[str, Any]]:
        """Validate the basic structure of the class."""
        issues = []
        
        # Check required attributes
        if not custom_class.name:
            issues.append({
                "component": "name",
                "issue": "Class name is required",
                "severity": "critical"
            })
            
        # Check hit die validity
        if custom_class.hit_die not in self.balance_constraints["hit_die"]["valid_values"]:
            issues.append({
                "component": "hit_die",
                "issue": f"Hit die must be one of {self.balance_constraints['hit_die']['valid_values']}",
                "severity": "critical",
                "recommendation": "Use d8 as a default hit die for balanced classes"
            })
        
        # Check saving throw count
        if len(custom_class.saving_throw_proficiencies) > self.balance_constraints["saving_throws"]["max_count"]:
            issues.append({
                "component": "saving_throws",
                "issue": f"Too many saving throw proficiencies: {len(custom_class.saving_throw_proficiencies)}",
                "severity": "critical",
                "recommendation": "Classes should have exactly 2 saving throw proficiencies"
            })
            
        # Check class features structure
        if not custom_class.class_features:
            issues.append({
                "component": "class_features",
                "issue": "No class features defined",
                "severity": "critical"
            })
        elif "1" not in custom_class.class_features and 1 not in custom_class.class_features:
            issues.append({
                "component": "class_features",
                "issue": "No level 1 features defined",
                "severity": "critical"
            })
        
        return issues
    
    def _validate_game_balance(self, custom_class: CustomClass) -> List[Dict[str, Any]]:
        """Validate game balance aspects of the class."""
        issues = []
        
        # Check saving throw balance (should have 1 strong, 1 weak)
        strong_saves = self.balance_constraints["saving_throws"]["strong_saves"]
        weak_saves = self.balance_constraints["saving_throws"]["weak_saves"]
        
        strong_count = sum(1 for save in custom_class.saving_throw_proficiencies if save in strong_saves)
        weak_count = sum(1 for save in custom_class.saving_throw_proficiencies if save in weak_saves)
        
        if strong_count > 1:
            issues.append({
                "component": "saving_throws",
                "issue": f"Too many strong saving throws: {strong_count}",
                "severity": "warning",
                "recommendation": "Classes typically have 1 strong save and 1 weak save"
            })
        
        # Check feature count per level
        for level_str, features in custom_class.class_features.items():
            level = int(level_str) if isinstance(level_str, str) else level_str
            max_features = self.balance_constraints["features_per_level"]["max"].get(
                level, self.balance_constraints["features_per_level"]["max"]["default"]
            )
            
            if len(features) > max_features:
                issues.append({
                    "component": "class_features",
                    "issue": f"Too many features at level {level}: {len(features)}",
                    "severity": "warning",
                    "recommendation": f"Level {level} should have at most {max_features} features"
                })
        
        # Check spellcasting balance
        if custom_class.spellcasting_type in [SpellcastingType.FULL, SpellcastingType.PACT]:
            # Full casters typically have fewer combat abilities
            combat_feature_count = self._count_combat_features(custom_class)
            if combat_feature_count > 3:
                issues.append({
                    "component": "class_features",
                    "issue": f"Full spellcaster has too many combat features: {combat_feature_count}",
                    "severity": "warning",
                    "recommendation": "Full spellcasters should have fewer direct combat abilities"
                })
        
        return issues
    
    def _validate_advanced_balance(self, custom_class: CustomClass) -> List[Dict[str, Any]]:
        """Perform advanced balance validation, potentially using LLM."""
        issues = []
        
        # This could use an LLM to evaluate balance in more nuanced ways
        if self.llm_service:
            prompt = (
                f"Analyze this D&D class for balance issues:\n\n"
                f"{custom_class.to_dict()}\n\n"
                f"Identify any concerns about power level, feature interactions, or rules conflicts. "
                f"Return a JSON array of issues with 'component', 'issue', 'severity', and 'recommendation' fields."
            )
            
            try:
                response = self.llm_service.generate(prompt)
                llm_issues = self._extract_json(response)
                if isinstance(llm_issues, list):
                    issues.extend(llm_issues)
            except Exception as e:
                logger.error(f"Error during advanced validation: {e}")
                issues.append({
                    "component": "validation",
                    "issue": "Advanced validation failed",
                    "severity": "info",
                    "recommendation": "Consider manual review of class balance"
                })
        
        return issues
    
    def _count_combat_features(self, custom_class: CustomClass) -> int:
        """Count features that appear to be combat-focused."""
        combat_count = 0
        combat_keywords = ["attack", "damage", "combat", "weapon", "strike", "hit", "slay"]
        
        for level_features in custom_class.class_features.values():
            for feature in level_features:
                name = feature.get("name", "").lower()
                desc = feature.get("description", "").lower()
                
                if any(keyword in name or keyword in desc for keyword in combat_keywords):
                    combat_count += 1
                    
        return combat_count
    
    def _extract_json(self, response: str) -> Any:
        """Extract JSON from LLM response."""
        try:
            import re
            import json
            
            # Try to find JSON array/object
            json_match = re.search(r'(\[.*\]|\{.*\})', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
        
        return None
    
    def apply_balance_corrections(self, custom_class: CustomClass, 
                               issues: List[Dict[str, Any]]) -> CustomClass:
        """
        Apply automatic corrections to balance issues when possible.
        
        Args:
            custom_class: The class to correct
            issues: List of validation issues
            
        Returns:
            Corrected CustomClass instance
        """
        # Create a copy to modify
        class_data = custom_class.to_dict()
        
        # First handle critical issues with direct fixes
        for issue in issues:
            component = issue.get("component")
            severity = issue.get("severity")
            
            if severity != "critical":
                continue
                
            if component == "hit_die" and "hit_die" in class_data:
                # Fix invalid hit die
                if class_data["hit_die"] not in self.balance_constraints["hit_die"]["valid_values"]:
                    class_data["hit_die"] = 8  # Default to d8
                    
            elif component == "saving_throws" and "saving_throw_proficiencies" in class_data:
                # Fix saving throw issues
                if len(class_data["saving_throw_proficiencies"]) > 2:
                    # Keep just two saves, preferably one strong and one weak
                    strong_saves = self.balance_constraints["saving_throws"]["strong_saves"]
                    weak_saves = self.balance_constraints["saving_throws"]["weak_saves"]
                    
                    strong_candidates = [s for s in class_data["saving_throw_proficiencies"] if s in strong_saves]
                    weak_candidates = [s for s in class_data["saving_throw_proficiencies"] if s in weak_saves]
                    
                    new_saves = []
                    if strong_candidates:
                        new_saves.append(strong_candidates[0])
                    if weak_candidates and len(new_saves) < 2:
                        new_saves.append(weak_candidates[0])
                    
                    # If we still don't have 2 saves, add from original list
                    remaining = [s for s in class_data["saving_throw_proficiencies"] if s not in new_saves]
                    while len(new_saves) < 2 and remaining:
                        new_saves.append(remaining.pop(0))
                        
                    class_data["saving_throw_proficiencies"] = new_saves[:2]
                    
            elif component == "class_features":
                # Ensure level 1 features exist
                if not class_data.get("class_features"):
                    class_data["class_features"] = {
                        "1": [{"name": "Class Feature", "description": "Basic class feature"}]
                    }
                elif "1" not in class_data["class_features"] and 1 not in class_data["class_features"]:
                    class_data["class_features"]["1"] = [
                        {"name": "Class Feature", "description": "Basic class feature"}
                    ]
        
        # Handle warnings with LLM assistance if available
        warning_issues = [i for i in issues if i.get("severity") == "warning"]
        if warning_issues and self.llm_service:
            class_data = self._llm_assisted_correction(class_data, warning_issues)
        
        # Convert spellcasting type back to enum if needed
        if "spellcasting_type" in class_data and isinstance(class_data["spellcasting_type"], str):
            try:
                class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
            except ValueError:
                class_data["spellcasting_type"] = SpellcastingType.NONE
        
        # Create new class instance with corrections
        return CustomClass(**class_data)
    
    def _llm_assisted_correction(self, class_data: Dict[str, Any], 
                              issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to help correct balance issues that require more nuance."""
        if not self.llm_service:
            return class_data
            
        issues_text = "\n".join([
            f"- {issue['component']}: {issue['issue']}" for issue in issues
        ])
        
        prompt = (
            f"Balance this D&D class to address these issues:\n\n"
            f"ISSUES:\n{issues_text}\n\n"
            f"CLASS:\n{class_data}\n\n"
            f"Make targeted changes to resolve the balance issues while preserving the class concept. "
            f"Return the balanced class as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            balanced_data = self._extract_json(response)
            
            if balanced_data and isinstance(balanced_data, dict):
                return balanced_data
        except Exception as e:
            logger.error(f"Error during LLM-assisted correction: {e}")
            
        return class_data