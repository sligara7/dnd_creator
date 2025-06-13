from typing import Optional, Dict, Any
import logging
from ...domain.services.validation_service import CharacterValidator, ValidationResult
from ...core.entities.character import Character

logger = logging.getLogger(__name__)

class LegacyValidatorAdapter:
    """Adapter for legacy validation systems."""
    
    name = "legacy_adapter"
    
    def __init__(self):
        self.legacy_validator = None
        self._initialize_legacy_validator()
    
    def _initialize_legacy_validator(self) -> None:
        """Attempt to initialize legacy validator."""
        try:
            # Try to import and initialize legacy validator
            # This is where you'd adapt the old validation system
            pass
        except ImportError as e:
            logger.warning(f"Legacy validator not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize legacy validator: {e}")
    
    def validate(self, character: Character) -> ValidationResult:
        """Validate using legacy system if available."""
        if not self.legacy_validator:
            return ValidationResult(
                is_valid=True,
                issues=[],
                warnings=["Legacy validator not available"],
                validator_name=self.name
            )
        
        try:
            # Convert character to legacy format
            legacy_data = self._convert_to_legacy_format(character)
            
            # Run legacy validation
            legacy_result = self.legacy_validator.validate_full_character(legacy_data)
            
            return ValidationResult(
                is_valid=legacy_result.get("valid", False),
                issues=legacy_result.get("issues", []),
                warnings=legacy_result.get("warnings", []),
                validator_name=self.name
            )
            
        except Exception as e:
            logger.error(f"Legacy validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                issues=[f"Legacy validation error: {str(e)}"],
                warnings=[],
                validator_name=self.name
            )
    
    def _convert_to_legacy_format(self, character: Character) -> Dict[str, Any]:
        """Convert Character entity to legacy format."""
        return character.to_dict()