# where does this file fit in /backend/core structure?

"""
Integration layer for validation across core components.
"""
from typing import List, Dict, Any
from .abstractions import AbstractContentValidator
from .value_objects import ValidationResult
from .enums import ValidationType, ValidationSeverity

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