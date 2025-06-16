"""
Core Domain Layer Entry Point - D&D Creative Content Framework.

SIMPLIFIED VERSION: Focuses on essential D&D mechanics with minimal culture support
that enhances character creation without overwhelming complexity.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple, supportive features only
- Creative freedom is paramount
"""

# ============================================================================
# MINIMAL DIRECT IMPORTS - Only standard library
# ============================================================================

import sys
from typing import Dict, Any, List, Optional, Union

# ============================================================================
# CORE VERSION AND METADATA
# ============================================================================

__version__ = "3.0.0"
__dnd_version__ = "5e"
__architecture__ = "Domain-Driven Design with Clean Architecture"

CORE_VERSION = "3.0.0"
SUPPORTED_DND_VERSION = "5e" 
ARCHITECTURE_PATTERN = "Domain-Driven Design with Clean Architecture"

# ============================================================================
# SAFE MODULE CHECKING
# ============================================================================

def _check_module_exists(module_path: str) -> bool:
    """Check if a module exists without importing it."""
    try:
        import importlib.util
        spec = importlib.util.find_spec(module_path)
        return spec is not None
    except (ImportError, ValueError, AttributeError):
        return False

def _safe_import_from_module(module_path: str, item_name: str, default=None):
    """Safely import an item from a module."""
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, item_name, default)
    except (ImportError, AttributeError):
        return default

# ============================================================================
# MODULE STATUS CHECKING
# ============================================================================

# Check which core modules actually exist
AVAILABLE_MODULES = {}
POTENTIAL_MODULES = ["enums", "value_objects", "abstractions", "entities", "utils", "exceptions"]

for module_name in POTENTIAL_MODULES:
    module_path = f"backend6.core.{module_name}"
    exists = _check_module_exists(module_path)
    AVAILABLE_MODULES[module_name] = exists

# ============================================================================
# SIMPLIFIED CORE INTERFACES
# ============================================================================

class CoreLayerInterface:
    """
    Primary interface for domain layer interaction with core functionality.
    
    SIMPLIFIED: Only exposes essential functionality that actually exists.
    """
    
    @staticmethod
    def get_available_modules():
        """Get list of modules that actually exist."""
        return {k: v for k, v in AVAILABLE_MODULES.items() if v}
    
    @staticmethod
    def get_module_status():
        """Get detailed status of all potential modules."""
        return AVAILABLE_MODULES.copy()
    
    @staticmethod 
    def get_enum_system():
        """Get enum system if available."""
        if AVAILABLE_MODULES.get("enums", False):
            try:
                import importlib
                enums_module = importlib.import_module("backend6.core.enums")
                
                # Only return what actually exists - SIMPLIFIED culture enums
                available_enums = {}
                enum_candidates = [
                    # Core D&D mechanics
                    'Ability', 'Skill', 'DamageType', 'ProficiencyLevel',
                    # Simple culture enums only
                    'CultureAuthenticityLevel', 'CultureType',
                    # Content types
                    'ContentType', 'CreativityLevel', 'BalanceLevel'
                ]
                
                for enum_name in enum_candidates:
                    if hasattr(enums_module, enum_name):
                        available_enums[enum_name] = getattr(enums_module, enum_name)
                
                return {
                    'status': 'available',
                    'enums': available_enums,
                    'culture_support': 'simple_only'
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            return {
                'status': 'module_not_found',
                'available_modules': list(AVAILABLE_MODULES.keys())
            }
    
    @staticmethod
    def get_simple_culture_capabilities():
        """Get simplified culture capabilities if available."""
        if AVAILABLE_MODULES.get("utils", False):
            try:
                # Try to get simple culture utilities
                culture_parser = _safe_import_from_module("backend6.core.utils.culture_parser", "SimpleCultureParser")
                culture_validator = _safe_import_from_module("backend6.core.utils.culture_validator", "SimpleCultureValidator")
                text_processing = _safe_import_from_module("backend6.core.utils.text_processing", "format_text_for_character")
                
                if culture_parser and culture_validator:
                    return {
                        'status': 'simple_culture_available',
                        'features': {
                            'character_name_extraction': True,
                            'culture_parsing': True,
                            'character_validation': True,
                            'text_processing': bool(text_processing)
                        },
                        'philosophy': 'Culture enhances but never restricts character creation'
                    }
                else:
                    return {
                        'status': 'culture_utilities_not_found',
                        'available_modules': self.get_available_modules()
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            return {
                'status': 'utils_module_not_found',
                'available_modules': self.get_available_modules()
            }
    
    @staticmethod
    def get_essential_d3d_capabilities():
        """Get essential D&D mechanics capabilities."""
        if AVAILABLE_MODULES.get("utils", False):
            try:
                # Check for essential D&D utilities
                rule_checker = _safe_import_from_module("backend6.core.utils.rule_checker", "validate_ability_scores")
                balance_calc = _safe_import_from_module("backend6.core.utils.balance_calculator", "calculate_overall_balance_score")
                mechanical_parser = _safe_import_from_module("backend6.core.utils.mechanical_parser", "extract_mechanical_elements")
                
                return {
                    'status': 'available',
                    'features': {
                        'rule_validation': bool(rule_checker),
                        'balance_calculation': bool(balance_calc),
                        'mechanical_parsing': bool(mechanical_parser)
                    }
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            return {
                'status': 'utils_module_not_found'
            }

class CoreTestingInterface:
    """
    SIMPLIFIED testing interface that only exposes what actually exists.
    """
    
    @staticmethod
    def get_testable_components():
        """Get components that can actually be tested."""
        return {
            'available_modules': AVAILABLE_MODULES,
            'existing_modules': [k for k, v in AVAILABLE_MODULES.items() if v],
            'missing_modules': [k for k, v in AVAILABLE_MODULES.items() if not v],
            'interfaces': ['CoreLayerInterface', 'CoreTestingInterface'],
            'culture_support': 'simple_character_focused'
        }
    
    @staticmethod
    def get_integration_test_points():
        """Get integration test points based on what exists."""
        return {
            'module_status': AVAILABLE_MODULES,
            'testable_interfaces': ['CoreLayerInterface', 'CoreTestingInterface'],
            'safe_functions': [
                'get_available_modules',
                'get_module_status', 
                'get_testable_components',
                'get_simple_culture_capabilities',
                'get_essential_d3d_capabilities'
            ],
            'culture_testing': 'simple_validation_only'
        }

# ============================================================================
# SAFE IMPORTS - Only What Actually Exists
# ============================================================================

# Try to import core modules safely
try:
    if AVAILABLE_MODULES.get("enums", False):
        from . import enums
        # Import only essential enums that we know exist
        try:
            from .enums import (
                # Core D&D mechanics
                Ability, Skill, DamageType, ProficiencyLevel,
                # Simple culture enums only
                CultureAuthenticityLevel, CultureType,
                # Essential content types
                ContentType, CreativityLevel, BalanceLevel
            )
            ENUMS_AVAILABLE = True
        except ImportError:
            ENUMS_AVAILABLE = False
    else:
        ENUMS_AVAILABLE = False
except ImportError:
    ENUMS_AVAILABLE = False

try:
    if AVAILABLE_MODULES.get("exceptions", False):
        from . import exceptions
        # Import only essential exceptions
        try:
            from .exceptions import (
                # Simple culture exceptions
                CultureError, CultureGenerationError, CultureParsingError, CultureNotFoundError,
                # Essential D&D exceptions
                ValidationError, GenerationError, BalanceError
            )
            EXCEPTIONS_AVAILABLE = True
        except ImportError:
            EXCEPTIONS_AVAILABLE = False
    else:
        EXCEPTIONS_AVAILABLE = False
except ImportError:
    EXCEPTIONS_AVAILABLE = False

try:
    if AVAILABLE_MODULES.get("utils", False):
        from . import utils
        # Import only essential utilities
        try:
            # Simple culture utilities
            from .utils.culture_parser import SimpleCultureParser, parse_culture_response
            from .utils.culture_validator import SimpleCultureValidator, validate_culture_for_characters
            from .utils.text_processing import format_text_for_character, clean_text_for_character_sheet
            
            # Essential D&D utilities
            from .utils.rule_checker import validate_ability_scores, calculate_proficiency_bonus
            from .utils.balance_calculator import calculate_overall_balance_score
            from .utils.mechanical_parser import extract_mechanical_elements
            
            UTILS_AVAILABLE = True
        except ImportError:
            UTILS_AVAILABLE = False
    else:
        UTILS_AVAILABLE = False
except ImportError:
    UTILS_AVAILABLE = False

# ============================================================================
# SIMPLIFIED UTILITY FUNCTIONS
# ============================================================================

def get_domain_info() -> dict:
    """Get information about what's actually available."""
    return {
        "version": CORE_VERSION,
        "dnd_version": SUPPORTED_DND_VERSION,
        "architecture": ARCHITECTURE_PATTERN,
        "available_modules": AVAILABLE_MODULES,
        "existing_modules": [k for k, v in AVAILABLE_MODULES.items() if v],
        "missing_modules": [k for k, v in AVAILABLE_MODULES.items() if not v],
        "status": "simplified_character_focused",
        "culture_support": "simple_character_enhancement",
        "philosophy": "Culture enhances character creation without restrictions"
    }

def validate_domain_integrity() -> dict:
    """Validate what's actually working."""
    existing_count = sum(1 for v in AVAILABLE_MODULES.values() if v)
    total_count = len(AVAILABLE_MODULES)
    
    return {
        "overall_status": "simplified" if existing_count > 0 else "missing_modules",
        "existing_modules": existing_count,
        "total_expected_modules": total_count,
        "completion_percentage": (existing_count / total_count) * 100,
        "available_modules": AVAILABLE_MODULES,
        "culture_approach": "simple_character_focused",
        "recommendations": [
            "Focus on essential D&D mechanics first",
            "Keep culture features simple and supportive",
            "Prioritize character creation workflow",
            "Avoid complex culture validation systems"
        ]
    }

def get_simple_culture_features() -> dict:
    """Get available simple culture features."""
    features = {
        "character_name_extraction": False,
        "culture_parsing": False,
        "simple_validation": False,
        "text_processing": False
    }
    
    if UTILS_AVAILABLE:
        try:
            from .utils.culture_parser import SimpleCultureParser
            features["culture_parsing"] = True
            features["character_name_extraction"] = True
        except ImportError:
            pass
        
        try:
            from .utils.culture_validator import SimpleCultureValidator
            features["simple_validation"] = True
        except ImportError:
            pass
        
        try:
            from .utils.text_processing import format_text_for_character
            features["text_processing"] = True
        except ImportError:
            pass
    
    return {
        "available_features": features,
        "philosophy": "Culture enhances but never restricts character creation",
        "approach": "simple_supportive_only"
    }

def get_essential_d3d_features() -> dict:
    """Get available essential D&D features."""
    features = {
        "rule_validation": False,
        "balance_calculation": False,
        "mechanical_parsing": False,
        "ability_scores": False
    }
    
    if UTILS_AVAILABLE:
        try:
            from .utils.rule_checker import validate_ability_scores
            features["rule_validation"] = True
            features["ability_scores"] = True
        except ImportError:
            pass
        
        try:
            from .utils.balance_calculator import calculate_overall_balance_score
            features["balance_calculation"] = True
        except ImportError:
            pass
        
        try:
            from .utils.mechanical_parser import extract_mechanical_elements
            features["mechanical_parsing"] = True
        except ImportError:
            pass
    
    return {
        "available_features": features,
        "focus": "essential_d3d_mechanics_only"
    }

# ============================================================================
# SIMPLIFIED EXPORTS - Only What Actually Exists
# ============================================================================

# Build exports list dynamically based on what's available
__all__ = [
    # Core interfaces that definitely exist
    'CoreLayerInterface',
    'CoreTestingInterface',
    
    # Utility functions that exist
    'get_domain_info',
    'validate_domain_integrity',
    'get_simple_culture_features',
    'get_essential_d3d_features',
    
    # Metadata
    '__version__',
    'CORE_VERSION',
    'SUPPORTED_DND_VERSION',
    'ARCHITECTURE_PATTERN',
    'AVAILABLE_MODULES'
]

# Add enums if available
if ENUMS_AVAILABLE:
    enum_exports = []
    try:
        # Only add enums that actually exist
        if 'Ability' in globals():
            enum_exports.extend(['Ability', 'Skill', 'DamageType', 'ProficiencyLevel'])
        if 'CultureAuthenticityLevel' in globals():
            enum_exports.extend(['CultureAuthenticityLevel', 'CultureType'])
        if 'ContentType' in globals():
            enum_exports.extend(['ContentType', 'CreativityLevel', 'BalanceLevel'])
        
        __all__.extend(enum_exports)
    except:
        pass

# Add exceptions if available
if EXCEPTIONS_AVAILABLE:
    exception_exports = []
    try:
        # Only add exceptions that actually exist
        if 'CultureError' in globals():
            exception_exports.extend(['CultureError', 'CultureGenerationError', 'CultureParsingError', 'CultureNotFoundError'])
        if 'ValidationError' in globals():
            exception_exports.extend(['ValidationError', 'GenerationError', 'BalanceError'])
        
        __all__.extend(exception_exports)
    except:
        pass

# Add utilities if available
if UTILS_AVAILABLE:
    utility_exports = []
    try:
        # Only add utilities that actually exist
        if 'SimpleCultureParser' in globals():
            utility_exports.extend(['SimpleCultureParser', 'parse_culture_response'])
        if 'SimpleCultureValidator' in globals():
            utility_exports.extend(['SimpleCultureValidator', 'validate_culture_for_characters'])
        if 'format_text_for_character' in globals():
            utility_exports.extend(['format_text_for_character', 'clean_text_for_character_sheet'])
        if 'validate_ability_scores' in globals():
            utility_exports.extend(['validate_ability_scores', 'calculate_proficiency_bonus'])
        if 'calculate_overall_balance_score' in globals():
            utility_exports.append('calculate_overall_balance_score')
        if 'extract_mechanical_elements' in globals():
            utility_exports.append('extract_mechanical_elements')
        
        __all__.extend(utility_exports)
    except:
        pass

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Simple initialization without complex dependencies
MODULE_LOAD_STATUS = "simplified_character_focused"
MODULE_LOAD_ERRORS = []

# Check for any critical issues
missing_modules = [k for k, v in AVAILABLE_MODULES.items() if not v]
if missing_modules:
    MODULE_LOAD_STATUS = "partial_missing_modules"

# Module information
MODULE_INFO = {
    "name": "core",
    "version": CORE_VERSION,
    "load_status": MODULE_LOAD_STATUS,
    "available_modules": [k for k, v in AVAILABLE_MODULES.items() if v],
    "missing_modules": missing_modules,
    "export_count": len(__all__),
    "circular_import_safe": True,
    "culture_approach": "simple_character_focused",
    "philosophy": "Culture enhances but never restricts character creation",
    "enums_available": ENUMS_AVAILABLE,
    "exceptions_available": EXCEPTIONS_AVAILABLE,
    "utils_available": UTILS_AVAILABLE
}

# Development output
if __name__ == "__main__":
    print(f"Core Layer v{CORE_VERSION} - {MODULE_LOAD_STATUS}")
    print(f"Available modules: {MODULE_INFO['available_modules']}")
    print(f"Missing modules: {MODULE_INFO['missing_modules']}")
    print(f"Exports: {MODULE_INFO['export_count']}")
    print(f"Culture approach: {MODULE_INFO['culture_approach']}")
    print(f"Philosophy: {MODULE_INFO['philosophy']}")
    
    if MODULE_INFO['missing_modules']:
        print(f"\n⚠️  Missing modules need to be created:")
        for module in MODULE_INFO['missing_modules']:
            print(f"   - backend6/core/{module}.py")
    
    # Show what's actually available
    culture_features = get_simple_culture_features()
    d3d_features = get_essential_d3d_features()
    
    print(f"\n✅ Available culture features:")
    for feature, available in culture_features['available_features'].items():
        status = "✓" if available else "✗"
        print(f"   {status} {feature}")
    
    print(f"\n✅ Available D&D features:")
    for feature, available in d3d_features['available_features'].items():
        status = "✓" if available else "✗"
        print(f"   {status} {feature}")

# ============================================================================
# SIMPLIFIED MODULE METADATA
# ============================================================================

__version__ = "3.0.0"
__description__ = "Simplified Core Layer for D&D Character Creation - Culture Enhances, Never Restricts"

# Simplified configuration
ENABLE_CULTURE_FEATURES = True  # But keep them simple
CULTURE_PHILOSOPHY = "enhance_not_restrict"
CHARACTER_CREATION_FIRST = True
SIMPLE_VALIDATION_APPROACH = True

# Feature flags
FEATURES = {
    "simple_culture_parsing": UTILS_AVAILABLE,
    "simple_culture_validation": UTILS_AVAILABLE,
    "essential_d3d_mechanics": UTILS_AVAILABLE,
    "character_focused_text_processing": UTILS_AVAILABLE,
    "simple_culture_enums": ENUMS_AVAILABLE,
    "graceful_error_handling": EXCEPTIONS_AVAILABLE
}

# Export feature status for external checking
def get_feature_status() -> dict:
    """Get status of all features."""
    return FEATURES.copy()

def is_culture_support_available() -> bool:
    """Check if simple culture support is available."""
    return FEATURES.get("simple_culture_parsing", False) and FEATURES.get("simple_culture_validation", False)

def is_d3d_mechanics_available() -> bool:
    """Check if essential D&D mechanics are available."""
    return FEATURES.get("essential_d3d_mechanics", False)

# Add feature functions to exports
__all__.extend(['get_feature_status', 'is_culture_support_available', 'is_d3d_mechanics_available'])