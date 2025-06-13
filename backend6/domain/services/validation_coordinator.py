# ├── services/              # NEW: Domain Services
# │   ├── __init__.py
# │   ├── validation_coordinator.py
# │   ├── content_generator.py
# │   └── balance_analyzer.py

"""
Integration layer for validation across core components.
"""
from typing import List, Dict, Any
from ..abstractions import AbstractContentValidator
from ..value_objects import ValidationResult
from ..enums import ValidationType, ValidationSeverity

class CoreValidationCoordinator:
    """Coordinates validation across all core components."""
    
    def __init__(self):
        self.validators: Dict[str, AbstractContentValidator] = {}
    
    def register_validator(self, content_type: str, validator: AbstractContentValidator):
        """Register a validator for a specific content type."""
        self.validators[content_type] = validator
    
    def validate_all_content(self, content_collection: 'ContentCollection') -> List[ValidationResult]:
        """Validate all content in a collection."""
        results = []
        
        for content_type, items in content_collection.content_items.items():
            if content_type in self.validators:
                validator = self.validators[content_type]
                for item in items:
                    item_results = validator.validate(item)
                    results.extend(item_results)
        
        return results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate summary of validation results."""
        total = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total - passed
        
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "success_rate": (passed / total) * 100 if total > 0 else 0
        }
    
"""
Domain service for coordinating validation across core components.

This service orchestrates validation between entities, value objects, and abstractions,
providing a centralized validation coordination layer for the domain.
"""
from typing import List, Dict, Any, Optional
from ..abstractions import AbstractContentValidator
from ..value_objects import ValidationResult
from ..enums import ValidationType, ValidationSeverity
from ..entities import ContentCollection

class CoreValidationCoordinator:
    """Coordinates validation across all core components."""
    
    def __init__(self):
        self.validators: Dict[str, AbstractContentValidator] = {}
        self.validation_history: List[Dict[str, Any]] = []
    
    def register_validator(self, content_type: str, validator: AbstractContentValidator):
        """Register a validator for a specific content type."""
        self.validators[content_type] = validator
    
    def unregister_validator(self, content_type: str) -> bool:
        """Remove a validator for a content type."""
        return self.validators.pop(content_type, None) is not None
    
    def get_registered_validators(self) -> List[str]:
        """Get list of registered validator content types."""
        return list(self.validators.keys())
    
    def validate_all_content(self, content_collection: ContentCollection) -> List[ValidationResult]:
        """Validate all content in a collection."""
        results = []
        
        for content_type, items in content_collection.content_items.items():
            if content_type in self.validators:
                validator = self.validators[content_type]
                for item in items:
                    item_results = validator.validate(item)
                    if isinstance(item_results, list):
                        results.extend(item_results)
                    else:
                        results.append(item_results)
        
        # Record validation session
        self.validation_history.append({
            "collection_id": content_collection.collection_id,
            "timestamp": content_collection.creation_metadata.created_at,
            "total_validations": len(results),
            "validation_types": list(set(content_collection.content_items.keys()))
        })
        
        return results
    
    def validate_single_content(self, content_type: str, content_item: Any) -> Optional[ValidationResult]:
        """Validate a single content item."""
        if content_type not in self.validators:
            return None
        
        validator = self.validators[content_type]
        result = validator.validate(content_item)
        
        return result if isinstance(result, ValidationResult) else result[0] if result else None
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate summary of validation results."""
        if not results:
            return {
                "total_validations": 0,
                "passed": 0,
                "failed": 0,
                "error_count": 0,
                "warning_count": 0,
                "success_rate": 0
            }
        
        total = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total - passed
        
        errors = [r for r in results if hasattr(r, 'severity') and r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in results if hasattr(r, 'severity') and r.severity == ValidationSeverity.WARNING]
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "success_rate": (passed / total) * 100 if total > 0 else 0,
            "validation_types": list(set(r.validation_type.value for r in results if hasattr(r, 'validation_type') and r.validation_type))
        }
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get history of validation sessions."""
        return self.validation_history.copy()
    
    def clear_validation_history(self):
        """Clear validation history."""
        self.validation_history.clear()

# update to the following code snippet:

from typing import List, Dict, Any
from ...core.abstractions.character_validator import ICharacterValidator, IStepValidator
from ..value_objects.validation_result import ValidationResult

class ValidationCoordinator:
    """Coordinates multiple D&D 5e validators without legacy dependencies."""
    
    def __init__(self):
        self._validators: List[ICharacterValidator] = []
        self._step_validators: List[IStepValidator] = []
    
    def register_validator(self, validator: ICharacterValidator) -> None:
        """Register a character validator."""
        self._validators.append(validator)
        # Sort by priority
        self._validators.sort(key=lambda v: v.get_validation_priority())
    
    def register_step_validator(self, validator: IStepValidator) -> None:
        """Register a step validator."""
        self._step_validators.append(validator)
    
    def validate_character(self, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate character using all registered validators."""
        if not self._validators:
            return ValidationResult(
                valid=False,
                issues=["No validators registered"],
                warnings=[],
                validator_name="coordinator"
            )
        
        all_results = []
        
        for validator in self._validators:
            if validator.can_validate(character_data):
                try:
                    result = validator.validate(character_data)
                    all_results.append(result)
                except Exception as e:
                    error_result = ValidationResult(
                        valid=False,
                        issues=[f"{validator.name} validation failed: {str(e)}"],
                        warnings=[],
                        validator_name=validator.name
                    )
                    all_results.append(error_result)
        
        # Merge all results
        final_result = all_results[0]
        for result in all_results[1:]:
            final_result = final_result.merge_with(result)
        
        return ValidationResult(
            valid=final_result.valid,
            issues=final_result.issues,
            warnings=final_result.warnings,
            validator_name="coordinator",
            recommendations=final_result.recommendations,
            detailed_results={
                "individual_results": [r.to_dict() for r in all_results],
                "summary": {
                    "total_validators": len(all_results),
                    "passed_validators": len([r for r in all_results if r.valid]),
                    "total_issues": len(final_result.issues),
                    "total_warnings": len(final_result.warnings)
                }
            }
        )
    
    def validate_creation_step(self, step_name: str, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate a specific character creation step."""
        applicable_validators = [
            v for v in self._step_validators 
            if step_name in v.supported_steps()
        ]
        
        if not applicable_validators:
            # Fall back to full character validation
            return self.validate_character(character_data)
        
        results = []
        for validator in applicable_validators:
            try:
                result = validator.validate_step(step_name, character_data)
                results.append(result)
            except Exception as e:
                error_result = ValidationResult(
                    valid=False,
                    issues=[f"Step validation failed: {str(e)}"],
                    warnings=[],
                    validator_name=f"step_{validator.__class__.__name__}",
                    step_name=step_name
                )
                results.append(error_result)
        
        # Merge step results
        if results:
            final_result = results[0]
            for result in results[1:]:
                final_result = final_result.merge_with(result)
            return final_result
        
        return ValidationResult(
            valid=True,
            issues=[],
            warnings=["No step validators available"],
            validator_name="coordinator",
            step_name=step_name
        )