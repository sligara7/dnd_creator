from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..enums.validation_types import ValidationType, ValidationSeverity, BalanceCategory
from ..enums.content_types import ContentType
from ..value_objects.validation_result import ValidationResult


class AbstractContentValidator(ABC):
    """
    Abstract contract for validating generated content in the Creative Content Framework.
    
    This interface ensures all generated content meets D&D 2024 rules and
    maintains appropriate balance for gameplay.
    """
    
    @abstractmethod
    def validate_content(self, content_data: Dict[str, Any], 
                        content_type: ContentType) -> List[ValidationResult]:
        """
        Validate generated content against D&D rules.
        
        Args:
            content_data: Content to validate
            content_type: Type of content being validated
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def validate_mechanical_balance(self, content_data: Dict[str, Any],
                                  content_type: ContentType) -> ValidationResult:
        """
        Validate mechanical balance and power level.
        
        Args:
            content_data: Content to validate
            content_type: Type of content
            
        Returns:
            Balance validation result
        """
        pass
    
    @abstractmethod
    def validate_rule_compliance(self, content_data: Dict[str, Any],
                               content_type: ContentType) -> List[ValidationResult]:
        """
        Validate compliance with D&D 2024 rules.
        
        Args:
            content_data: Content to validate
            content_type: Type of content
            
        Returns:
            List of rule compliance results
        """
        pass
    
    @abstractmethod
    def validate_thematic_consistency(self, content_data: Dict[str, Any],
                                    theme_context: Dict[str, Any]) -> ValidationResult:
        """
        Validate thematic consistency with character concept.
        
        Args:
            content_data: Content to validate
            theme_context: Thematic context and requirements
            
        Returns:
            Thematic validation result
        """
        pass
    
    @abstractmethod
    def calculate_balance_score(self, content_data: Dict[str, Any],
                              content_type: ContentType) -> float:
        """
        Calculate numerical balance score (0.0 to 1.0).
        
        Args:
            content_data: Content to score
            content_type: Type of content
            
        Returns:
            Balance score (0.0 = underpowered, 0.5 = balanced, 1.0 = overpowered)
        """
        pass
    
    @abstractmethod
    def get_balance_recommendations(self, content_data: Dict[str, Any],
                                  content_type: ContentType) -> List[str]:
        """
        Get recommendations for improving balance.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            
        Returns:
            List of balance improvement suggestions
        """
        pass