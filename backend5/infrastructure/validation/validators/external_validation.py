from typing import List, Dict, Any
import logging
from ...domain.services.validation_engine import ValidationRule
from ...core.entities.character import Character
from ...core.value_objects.validation_result import ValidationIssue, ValidationSeverity

logger = logging.getLogger(__name__)

class ExternalValidationRule:
    """Adapter for external validation systems."""
    
    def __init__(self, external_validator_config: Dict[str, Any]):
        self.config = external_validator_config
        self.rule_name = "external_validator"
    
    def validate(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate using external system."""
        issues = []
        
        try:
            # Interface with external validation system
            external_result = self._call_external_validator(character, context)
            
            # Convert external format to internal format
            for ext_issue in external_result.get("issues", []):
                issues.append(ValidationIssue(
                    severity=self._convert_severity(ext_issue.get("severity", "error")),
                    code=ext_issue.get("code", "EXTERNAL_ISSUE"),
                    message=ext_issue.get("message", "External validation issue"),
                    field=ext_issue.get("field"),
                    suggested_fix=ext_issue.get("suggestion")
                ))
                
        except Exception as e:
            logger.error(f"External validator failed: {e}")
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="EXTERNAL_VALIDATOR_ERROR",
                message=f"External validator failed: {str(e)}"
            ))
        
        return issues
    
    def _call_external_validator(self, character: Character, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call external validation system."""
        # Implementation depends on external system
        pass
    
    def _convert_severity(self, external_severity: str) -> ValidationSeverity:
        """Convert external severity to internal format."""
        mapping = {
            "info": ValidationSeverity.INFO,
            "warning": ValidationSeverity.WARNING,
            "error": ValidationSeverity.ERROR,
            "critical": ValidationSeverity.CRITICAL
        }
        return mapping.get(external_severity.lower(), ValidationSeverity.ERROR)