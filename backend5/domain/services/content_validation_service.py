from typing import List, Dict, Any
from ...core.entities.character import Character
from ...core.value_objects.validation_result import ValidationIssue, ValidationSeverity
from .content_registry import ContentRegistry

class ContentValidationService:
    """
    Validates character content against abstract contracts.
    
    This is where the abstract rules are enforced during character creation
    and validation, ensuring custom content follows D&D mechanics.
    """
    
    def __init__(self, content_registry: ContentRegistry):
        self.content_registry = content_registry
    
    def validate_class_selection(self, character: Character, class_name: str, level: int) -> List[ValidationIssue]:
        """Validate class selection against abstract class contract."""
        issues = []
        
        class_impl = self.content_registry.get_class(class_name)
        if not class_impl:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="UNKNOWN_CLASS",
                message=f"Unknown character class: {class_name}",
                suggested_fix="Select a valid character class"
            ))
            return issues
        
        # Validate multiclass prerequisites if applicable
        if character.is_multiclass and class_name not in character.character_classes:
            prereq_errors = class_impl.validate_multiclass_prerequisites(character)
            for error in prereq_errors:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MULTICLASS_PREREQUISITE",
                    message=error,
                    suggested_fix="Meet the multiclass prerequisites"
                ))
        
        # Validate class features are properly applied
        expected_features = class_impl.get_class_features(level)
        for feature in expected_features:
            if not self._character_has_class_feature(character, class_name, feature.name):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="MISSING_CLASS_FEATURE",
                    message=f"Character missing {class_name} feature: {feature.name}",
                    suggested_fix="Add missing class feature"
                ))
        
        return issues
    
    def validate_species_selection(self, character: Character, species_name: str) -> List[ValidationIssue]:
        """Validate species selection against abstract species contract."""
        issues = []
        
        species_impl = self.content_registry.get_species(species_name)
        if not species_impl:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="UNKNOWN_SPECIES",
                message=f"Unknown species: {species_name}",
                suggested_fix="Select a valid species"
            ))
            return issues
        
        # Validate ability score increases are applied
        expected_asi = species_impl.get_ability_score_increases()
        for ability, increase in expected_asi.items():
            # Check if character has the expected racial bonus
            # This would require tracking base vs racial scores
            pass
        
        # Validate species traits are applied
        expected_traits = species_impl.get_species_traits()
        for trait in expected_traits:
            trait_name = trait.get("name", "")
            if not self._character_has_species_trait(character, trait_name):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="MISSING_SPECIES_TRAIT",
                    message=f"Character missing {species_name} trait: {trait_name}",
                    suggested_fix="Add missing species trait"
                ))
        
        return issues
    
    def validate_equipment_selection(self, character: Character, equipment: List[str]) -> List[ValidationIssue]:
        """Validate equipment against abstract equipment contracts."""
        issues = []
        
        for item_name in equipment:
            # Check weapons
            weapon = self.content_registry.get_weapon(item_name)
            if weapon:
                weapon_issues = self._validate_weapon_proficiency(character, weapon)
                issues.extend(weapon_issues)
            
            # Check armor
            armor = self.content_registry.get_armor(item_name)
            if armor:
                armor_issues = self._validate_armor_proficiency(character, armor)
                issues.extend(armor_issues)
        
        return issues
    
    def suggest_custom_content_creation(self, character_concept: str) -> Dict[str, Any]:
        """Suggest custom content based on character concept."""
        suggestions = {
            "custom_class": None,
            "custom_species": None,
            "custom_equipment": [],
            "template_recommendations": []
        }
        
        # Analyze concept and suggest templates
        # This would use NLP/LLM to understand what custom content might be needed
        
        return suggestions
    
    def _character_has_class_feature(self, character: Character, class_name: str, feature_name: str) -> bool:
        """Check if character has a specific class feature."""
        class_features = character.class_features.get(class_name, {})
        return feature_name in class_features
    
    def _character_has_species_trait(self, character: Character, trait_name: str) -> bool:
        """Check if character has a specific species trait."""
        return trait_name in character.species_traits
    
    def _validate_weapon_proficiency(self, character: Character, weapon) -> List[ValidationIssue]:
        """Validate weapon proficiency."""
        issues = []
        
        weapon_type = weapon.weapon_type  # "simple" or "martial"
        if not character.has_proficiency("weapon", weapon.name):
            if weapon_type == "martial" and not character.has_proficiency("weapon", "martial weapons"):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="WEAPON_PROFICIENCY",
                    message=f"Character not proficient with {weapon.name}",
                    suggested_fix="Gain weapon proficiency or accept attack penalty"
                ))
        
        return issues
    
    def _validate_armor_proficiency(self, character: Character, armor) -> List[ValidationIssue]:
        """Validate armor proficiency."""
        issues = []
        
        armor_type = armor.armor_type
        if not character.has_proficiency("armor", armor_type):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="ARMOR_PROFICIENCY",
                message=f"Character not proficient with {armor_type} armor",
                suggested_fix="Gain armor proficiency or remove armor"
            ))
        
        return issues
    
def validate_domain_integrity() -> dict:
    """
    Validate that all domain components are properly integrated.
    """
    results = {
        "valid": True,
        "issues": [],
        "component_status": {},
        "implementation_completeness": {}
    }
    
    for category, status in DOMAIN_COMPONENTS.items():
        implemented = status.get("implemented", [])
        missing = status.get("missing", [])
        
        results["component_status"][category] = {
            "implemented_count": len(implemented),
            "missing_count": len(missing),
            "completion_rate": len(implemented) / (len(implemented) + len(missing)) * 100
        }
        
        if missing:
            results["valid"] = False
            results["issues"].extend([
                f"Missing {category} component: {component}" 
                for component in missing
            ])
    
    # Calculate overall completeness
    total_implemented = sum(len(s.get("implemented", [])) for s in DOMAIN_COMPONENTS.values())
    total_missing = sum(len(s.get("missing", [])) for s in DOMAIN_COMPONENTS.values())
    
    results["implementation_completeness"] = {
        "total_components": total_implemented + total_missing,
        "implemented": total_implemented,
        "missing": total_missing,
        "completion_percentage": (total_implemented / (total_implemented + total_missing)) * 100
    }
    
    return results