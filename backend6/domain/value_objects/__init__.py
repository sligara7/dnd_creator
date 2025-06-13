"""
Core value objects for the D&D Creative Content Framework.

Value objects are immutable data structures that represent important concepts
in the domain. They provide behavior related to their data while maintaining
immutability and supporting the framework's validation-first design.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .balance_metrics import BalanceMetrics, AttackMetrics, DefensiveMetrics, ResourceMetrics
from .validation_result import ValidationResult, ValidationIssue, ValidationSummary
from .content_metadata import ContentMetadata
from .generation_constraints import GenerationConstraints
from .thematic_elements import ThematicElements, ThemeCategory

__all__ = [
    # Balance and Metrics
    'BalanceMetrics',
    'AttackMetrics', 
    'DefensiveMetrics',
    'ResourceMetrics',
    
    # Validation
    'ValidationResult',
    'ValidationIssue',
    'ValidationSummary',
    
    # Content Generation
    'ContentMetadata',
    'GenerationConstraints',
    'ThematicElements',
    'ThemeCategory',
    
    # Utility Functions
    'create_default_metadata',
    'merge_thematic_elements',
    'calculate_combined_balance',
    'create_empty_validation_result',
    'merge_validation_results',
    'create_generation_constraints',
    'validate_value_object_integrity',
]

# Value Object Registry for dynamic loading
VALUE_OBJECT_REGISTRY = {
    'balance_metrics': BalanceMetrics,
    'attack_metrics': AttackMetrics,
    'defensive_metrics': DefensiveMetrics,
    'resource_metrics': ResourceMetrics,
    'validation_result': ValidationResult,
    'validation_issue': ValidationIssue,
    'validation_summary': ValidationSummary,
    'content_metadata': ContentMetadata,
    'generation_constraints': GenerationConstraints,
    'thematic_elements': ThematicElements,
}


def create_default_metadata(created_by: str = "system") -> ContentMetadata:
    """
    Create default metadata for content generation.
    
    Args:
        created_by: Who created the content
        
    Returns:
        Default ContentMetadata instance
    """
    return ContentMetadata(
        created_at=datetime.now(),
        created_by=created_by,
        generation_method="template",
        version="1.0",
        source="system",
        tags=[],
        custom_properties={}
    )


def merge_thematic_elements(elements: List[ThematicElements]) -> ThematicElements:
    """
    Merge multiple thematic element sets.
    
    Args:
        elements: List of ThematicElements to merge
        
    Returns:
        Merged ThematicElements
        
    Raises:
        ValueError: If elements list is empty
    """
    if not elements:
        raise ValueError("Cannot merge empty elements list")
    
    merged_themes = set()
    merged_keywords = set()
    merged_cultural = set()
    
    for element in elements:
        merged_themes.update(element.primary_themes)
        merged_keywords.update(element.theme_keywords)
        merged_cultural.update(element.cultural_elements)
    
    # Use the first element's power level as base, or calculate average
    power_levels = [e.power_level for e in elements if hasattr(e, 'power_level') and e.power_level is not None]
    avg_power_level = sum(power_levels) / len(power_levels) if power_levels else None
    
    return ThematicElements(
        primary_themes=list(merged_themes),
        theme_keywords=list(merged_keywords),
        cultural_elements=list(merged_cultural),
        power_level=avg_power_level
    )


def calculate_combined_balance(metrics: List[BalanceMetrics]) -> BalanceMetrics:
    """
    Calculate combined balance metrics.
    
    Args:
        metrics: List of BalanceMetrics to combine
        
    Returns:
        Combined BalanceMetrics
        
    Raises:
        ValueError: If metrics list is empty
    """
    if not metrics:
        raise ValueError("Cannot calculate balance for empty metrics list")
    
    total_power = sum(m.power_level_score for m in metrics)
    total_utility = sum(m.utility_score for m in metrics)
    total_versatility = sum(m.versatility_score for m in metrics)
    
    count = len(metrics)
    
    return BalanceMetrics(
        power_level_score=total_power / count,
        utility_score=total_utility / count,
        versatility_score=total_versatility / count,
        overall_balance_score=(total_power + total_utility + total_versatility) / (count * 3),
        scaling_score=sum(getattr(m, 'scaling_score', 0) for m in metrics) / count,
        complexity_score=sum(getattr(m, 'complexity_score', 0) for m in metrics) / count
    )


def create_empty_validation_result() -> ValidationResult:
    """
    Create an empty validation result for initialization.
    
    Returns:
        Empty ValidationResult
    """
    return ValidationResult(
        is_valid=True,
        issues=[],
        warnings=[],
        suggestions=[],
        validation_timestamp=datetime.now()
    )


def merge_validation_results(results: List[ValidationResult]) -> ValidationResult:
    """
    Merge multiple validation results into one.
    
    Args:
        results: List of ValidationResult objects to merge
        
    Returns:
        Merged ValidationResult
    """
    if not results:
        return create_empty_validation_result()
    
    merged_issues = []
    merged_warnings = []
    merged_suggestions = []
    overall_valid = True
    
    for result in results:
        merged_issues.extend(result.issues)
        merged_warnings.extend(result.warnings)
        merged_suggestions.extend(result.suggestions)
        
        if not result.is_valid:
            overall_valid = False
    
    return ValidationResult(
        is_valid=overall_valid,
        issues=merged_issues,
        warnings=merged_warnings,
        suggestions=list(set(merged_suggestions)),  # Remove duplicates
        validation_timestamp=datetime.now()
    )


def create_generation_constraints(
    content_type: str,
    max_complexity: float = 1.0,
    theme_requirements: Optional[List[str]] = None,
    balance_requirements: Optional[Dict[str, float]] = None
) -> GenerationConstraints:
    """
    Create generation constraints for content creation.
    
    Args:
        content_type: Type of content to generate
        max_complexity: Maximum complexity allowed
        theme_requirements: Required themes
        balance_requirements: Balance requirement thresholds
        
    Returns:
        GenerationConstraints instance
    """
    return GenerationConstraints(
        content_type=content_type,
        max_complexity_score=max_complexity,
        required_themes=theme_requirements or [],
        balance_thresholds=balance_requirements or {},
        generation_timeout=300,  # 5 minutes default
        max_iterations=10,
        enforce_uniqueness=True
    )


def validate_value_object_integrity() -> Dict[str, List[str]]:
    """
    Validate all value objects for consistency and completeness.
    
    Returns:
        Dictionary mapping value object types to any issues found
    """
    validation_results = {}
    
    for vo_type, vo_class in VALUE_OBJECT_REGISTRY.items():
        issues = []
        
        # Check for required methods
        required_methods = ['__eq__', '__hash__']  # Value objects should be comparable and hashable
        for method in required_methods:
            if not hasattr(vo_class, method):
                issues.append(f"Missing required method: {method}")
        
        # Check for immutability indicators
        if hasattr(vo_class, '__slots__'):
            # Good practice for value objects
            pass
        elif hasattr(vo_class, '__dataclass_fields__'):
            # Check if dataclass is frozen
            if not getattr(vo_class, '__dataclass_params__', None) or not vo_class.__dataclass_params__.frozen:
                issues.append("Dataclass value object should be frozen")
        
        # Check for proper initialization
        try:
            # This is a basic check - would need proper test data in practice
            if hasattr(vo_class, '__init__'):
                pass  # Could check __init__ signature
        except Exception as e:
            issues.append(f"Initialization issue: {e}")
        
        if issues:
            validation_results[vo_type] = issues
    
    return validation_results


def get_value_object_class(vo_type: str) -> Optional[type]:
    """
    Get value object class by type name.
    
    Args:
        vo_type: String identifier for the value object type
        
    Returns:
        Value object class or None if not found
    """
    return VALUE_OBJECT_REGISTRY.get(vo_type.lower())


def list_available_value_objects() -> List[str]:
    """
    Get list of all available value object types.
    
    Returns:
        List of value object type names
    """
    return list(VALUE_OBJECT_REGISTRY.keys())


def create_value_object_from_dict(vo_type: str, data: Dict[str, Any]) -> Any:
    """
    Create a value object instance from dictionary data.
    
    Args:
        vo_type: Type of value object to create
        data: Dictionary with value object data
        
    Returns:
        Value object instance
        
    Raises:
        ValueError: If value object type is unknown or data is invalid
    """
    vo_class = get_value_object_class(vo_type)
    if not vo_class:
        raise ValueError(f"Unknown value object type: {vo_type}")
    
    if hasattr(vo_class, 'from_dict'):
        return vo_class.from_dict(data)
    else:
        # Fallback to direct initialization
        try:
            return vo_class(**data)
        except TypeError as e:
            raise ValueError(f"Invalid data for {vo_type}: {e}")


def get_value_object_schema(vo_type: str) -> Optional[Dict[str, Any]]:
    """
    Get schema information for a value object type.
    
    Args:
        vo_type: Type of value object
        
    Returns:
        Schema dictionary or None if not found
    """
    vo_class = get_value_object_class(vo_type)
    if not vo_class:
        return None
    
    schema = {
        "type": vo_type,
        "class_name": vo_class.__name__,
        "fields": {},
        "methods": []
    }
    
    # Extract field information
    if hasattr(vo_class, '__dataclass_fields__'):
        for field_name, field in vo_class.__dataclass_fields__.items():
            schema["fields"][field_name] = {
                "type": str(field.type),
                "required": field.default == field.default_factory,
                "default": str(field.default) if field.default != field.default_factory else None
            }
    
    # Extract method information
    for attr_name in dir(vo_class):
        if not attr_name.startswith('_') and callable(getattr(vo_class, attr_name)):
            schema["methods"].append(attr_name)
    
    return schema


def validate_value_object_data(vo_type: str, data: Dict[str, Any]) -> List[str]:
    """
    Validate data before creating a value object.
    
    Args:
        vo_type: Type of value object
        data: Data to validate
        
    Returns:
        List of validation issues
    """
    issues = []
    vo_class = get_value_object_class(vo_type)
    
    if not vo_class:
        issues.append(f"Unknown value object type: {vo_type}")
        return issues
    
    # Try to create instance to validate data
    try:
        create_value_object_from_dict(vo_type, data)
    except ValueError as e:
        issues.append(str(e))
    except Exception as e:
        issues.append(f"Unexpected error: {e}")
    
    return issues