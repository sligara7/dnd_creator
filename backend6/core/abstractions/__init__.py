"""
Core abstractions for the D&D Creative Content Framework.

This module defines the fundamental contracts that all content types must follow,
ensuring D&D 2024 rule compliance while enabling creative freedom in content generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from .character_class import AbstractCharacterClass, ClassFeature
from .species import AbstractSpecies
from .equipment import AbstractEquipment, AbstractWeapon, AbstractArmor, AbstractMagicItem
from .spell import AbstractSpell
from .feat import AbstractFeat
from .content_validator import AbstractContentValidator

__all__ = [
    # Character Classes
    'AbstractCharacterClass',
    'ClassFeature',
    
    # Species
    'AbstractSpecies', 
    
    # Equipment
    'AbstractEquipment',
    'AbstractWeapon',
    'AbstractArmor', 
    'AbstractMagicItem',
    
    # Spells
    'AbstractSpell',
    
    # Feats
    'AbstractFeat',
    
    # Validation
    'AbstractContentValidator',
    
    # Utility Functions
    'get_available_abstractions',
    'validate_abstraction_implementation',
    'get_abstraction_registry',
    'check_abstraction_completeness',
]

# Registry of all available abstractions
ABSTRACTION_REGISTRY = {
    'character_class': AbstractCharacterClass,
    'species': AbstractSpecies,
    'equipment': AbstractEquipment,
    'weapon': AbstractWeapon,
    'armor': AbstractArmor,
    'magic_item': AbstractMagicItem,
    'spell': AbstractSpell,
    'feat': AbstractFeat,
    'content_validator': AbstractContentValidator,
}


def get_available_abstractions() -> List[str]:
    """
    Get list of all available abstract contracts.
    
    Returns:
        List of abstraction class names
    """
    return [
        "AbstractCharacterClass", "AbstractSpecies", "AbstractEquipment",
        "AbstractWeapon", "AbstractArmor", "AbstractMagicItem", "AbstractSpell", 
        "AbstractFeat", "AbstractContentValidator"
    ]


def validate_abstraction_implementation(impl_class: Type, expected_abstract: Type) -> List[str]:
    """
    Validate that a concrete class properly implements an abstraction.
    
    Args:
        impl_class: The concrete implementation class to validate
        expected_abstract: The abstract base class it should implement
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check inheritance
    if not issubclass(impl_class, expected_abstract):
        issues.append(f"{impl_class.__name__} does not inherit from {expected_abstract.__name__}")
        return issues  # Can't continue validation without proper inheritance
    
    # Check for required abstract methods
    abstract_methods = getattr(expected_abstract, '__abstractmethods__', set())
    for method_name in abstract_methods:
        if not hasattr(impl_class, method_name):
            issues.append(f"Missing required method: {method_name}")
        else:
            # Check if method is still abstract (not properly implemented)
            method = getattr(impl_class, method_name)
            if getattr(method, '__isabstractmethod__', False):
                issues.append(f"Method {method_name} is not properly implemented (still abstract)")
    
    # Check for required properties
    for attr_name in dir(expected_abstract):
        if not attr_name.startswith('_'):
            attr = getattr(expected_abstract, attr_name)
            if isinstance(attr, property) and hasattr(attr, '__isabstractmethod__'):
                if not hasattr(impl_class, attr_name):
                    issues.append(f"Missing required property: {attr_name}")
    
    return issues


def get_abstraction_registry() -> Dict[str, Type]:
    """
    Get the registry of all available abstractions.
    
    Returns:
        Dictionary mapping abstraction names to their classes
    """
    return ABSTRACTION_REGISTRY.copy()


def check_abstraction_completeness() -> Dict[str, Any]:
    """
    Check the completeness and integrity of all abstractions.
    
    Returns:
        Dictionary with completeness analysis
    """
    results = {
        "total_abstractions": len(ABSTRACTION_REGISTRY),
        "abstract_methods_count": {},
        "inheritance_tree": {},
        "validation_status": "complete"
    }
    
    for name, abstract_class in ABSTRACTION_REGISTRY.items():
        # Count abstract methods
        abstract_methods = getattr(abstract_class, '__abstractmethods__', set())
        results["abstract_methods_count"][name] = len(abstract_methods)
        
        # Build inheritance tree
        mro = abstract_class.__mro__
        results["inheritance_tree"][name] = [cls.__name__ for cls in mro if cls != object]
        
        # Basic validation
        if not abstract_methods and abstract_class != AbstractContentValidator:
            # Most abstractions should have at least some abstract methods
            results["validation_status"] = "warning"
    
    return results


def get_abstraction_by_name(name: str) -> Optional[Type]:
    """
    Get an abstraction class by its name.
    
    Args:
        name: Name of the abstraction (key from registry)
        
    Returns:
        Abstraction class or None if not found
    """
    return ABSTRACTION_REGISTRY.get(name.lower())


def list_abstract_methods(abstract_class: Type) -> List[str]:
    """
    List all abstract methods for a given abstraction.
    
    Args:
        abstract_class: The abstract class to analyze
        
    Returns:
        List of abstract method names
    """
    abstract_methods = getattr(abstract_class, '__abstractmethods__', set())
    return list(abstract_methods)


def get_implementation_template(abstract_class: Type) -> str:
    """
    Generate a basic implementation template for an abstraction.
    
    Args:
        abstract_class: The abstract class to create template for
        
    Returns:
        String containing implementation template
    """
    class_name = abstract_class.__name__.replace('Abstract', 'Concrete')
    abstract_methods = getattr(abstract_class, '__abstractmethods__', set())
    
    template_lines = [
        f"class {class_name}({abstract_class.__name__}):",
        f'    """Concrete implementation of {abstract_class.__name__}."""',
        ""
    ]
    
    for method_name in sorted(abstract_methods):
        method = getattr(abstract_class, method_name)
        if callable(method):
            template_lines.extend([
                f"    def {method_name}(self, *args, **kwargs):",
                f'        """Implement {method_name} method."""',
                f"        # TODO: Implement {method_name}",
                f"        raise NotImplementedError('Method {method_name} must be implemented')",
                ""
            ])
    
    return "\n".join(template_lines)


def validate_all_abstractions() -> Dict[str, List[str]]:
    """
    Validate all abstractions for consistency and completeness.
    
    Returns:
        Dictionary mapping abstraction names to any issues found
    """
    validation_results = {}
    
    for name, abstract_class in ABSTRACTION_REGISTRY.items():
        issues = []
        
        # Check that it's actually abstract
        if not getattr(abstract_class, '__abstractmethods__', None):
            if abstract_class != AbstractContentValidator:  # Special case
                issues.append("Class has no abstract methods - may not be properly abstract")
        
        # Check for proper ABC inheritance
        if not issubclass(abstract_class, ABC):
            issues.append("Abstract class should inherit from ABC")
        
        # Check for docstring
        if not abstract_class.__doc__:
            issues.append("Abstract class missing docstring")
        
        validation_results[name] = issues
    
    return validation_results