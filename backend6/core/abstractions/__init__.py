"""
Core abstractions for the D&D Creative Content Framework.

This module defines the fundamental contracts that all content types must follow,
ensuring D&D 2024 rule compliance while enabling creative freedom in content generation.

These abstractions enforce Clean Architecture boundaries by defining interfaces
that are infrastructure-independent and focused on business rules.
"""

import warnings
from typing import Dict, List, Optional, Type, Any

# ============ SAFE IMPORTS WITH ERROR HANDLING ============
# Import only what exists, warn about missing abstractions

# Infrastructure Layer Abstractions
try:
    from .llm_provider import ILLMProvider
    _HAS_LLM_PROVIDER = True
except ImportError:
    ILLMProvider = None
    _HAS_LLM_PROVIDER = False
    warnings.warn("ILLMProvider not available - create llm_provider.py")

try:
    from .export_service import IExportService
    _HAS_EXPORT_SERVICE = True
except ImportError:
    IExportService = None
    _HAS_EXPORT_SERVICE = False
    warnings.warn("IExportService not available - create export_service.py")

# Application Layer Abstractions
try:
    from .character_repository import ICharacterRepository
    _HAS_CHARACTER_REPO = True
except ImportError:
    ICharacterRepository = None
    _HAS_CHARACTER_REPO = False
    warnings.warn("ICharacterRepository not available - create character_repository.py")

try:
    from .conversation_repository import IConversationRepository
    _HAS_CONVERSATION_REPO = True
except ImportError:
    IConversationRepository = None
    _HAS_CONVERSATION_REPO = False
    warnings.warn("IConversationRepository not available - create conversation_repository.py")

try:
    from .content_repository import IContentRepository
    _HAS_CONTENT_REPO = True
except ImportError:
    IContentRepository = None
    _HAS_CONTENT_REPO = False
    warnings.warn("IContentRepository not available - create content_repository.py")

# Domain Service Abstractions
try:
    from .content_generator import IContentGenerator
    _HAS_CONTENT_GENERATOR = True
except ImportError:
    IContentGenerator = None
    _HAS_CONTENT_GENERATOR = False
    warnings.warn("IContentGenerator not available - create content_generator.py")

try:
    from .balance_analyzer import IBalanceAnalyzer
    _HAS_BALANCE_ANALYZER = True
except ImportError:
    IBalanceAnalyzer = None
    _HAS_BALANCE_ANALYZER = False
    warnings.warn("IBalanceAnalyzer not available - create balance_analyzer.py")

try:
    from .content_validator import IContentValidator
    _HAS_CONTENT_VALIDATOR = True
except ImportError:
    IContentValidator = None
    _HAS_CONTENT_VALIDATOR = False
    warnings.warn("IContentValidator not available - create content_validator.py")

# Domain Entity Abstractions - Character Building Blocks
try:
    from .species import ISpecies
    _HAS_SPECIES = True
except ImportError:
    ISpecies = None
    _HAS_SPECIES = False
    warnings.warn("ISpecies not available - create species.py")

try:
    from .character_class import ICharacterClass, ISubclass
    _HAS_CHARACTER_CLASS = True
except ImportError:
    ICharacterClass = None
    ISubclass = None
    _HAS_CHARACTER_CLASS = False
    warnings.warn("ICharacterClass/ISubclass not available - create character_class.py")

try:
    from .background import IBackground
    _HAS_BACKGROUND = True
except ImportError:
    IBackground = None
    _HAS_BACKGROUND = False
    warnings.warn("IBackground not available - create background.py")

# Domain Entity Abstractions - Content Types
try:
    from .feat import IFeat
    _HAS_FEAT = True
except ImportError:
    IFeat = None
    _HAS_FEAT = False
    warnings.warn("IFeat not available - create feat.py")

try:
    from .spell import ISpell
    _HAS_SPELL = True
except ImportError:
    ISpell = None
    _HAS_SPELL = False
    warnings.warn("ISpell not available - create spell.py")

try:
    from .equipment import IEquipment, IWeapon, IArmor, IMagicItem
    _HAS_EQUIPMENT = True
except ImportError:
    IEquipment = None
    IWeapon = None
    IArmor = None
    IMagicItem = None
    _HAS_EQUIPMENT = False
    warnings.warn("Equipment interfaces not available - create equipment.py")

# Domain Entity Abstractions - Character System
try:
    from .character import ICharacter
    _HAS_CHARACTER = True
except ImportError:
    ICharacter = None
    _HAS_CHARACTER = False
    warnings.warn("ICharacter not available - create character.py")

try:
    from .character_sheet import ICharacterSheet
    _HAS_CHARACTER_SHEET = True
except ImportError:
    ICharacterSheet = None
    _HAS_CHARACTER_SHEET = False
    warnings.warn("ICharacterSheet not available - create character_sheet.py")

try:
    from .progression import IProgression
    _HAS_PROGRESSION = True
except ImportError:
    IProgression = None
    _HAS_PROGRESSION = False
    warnings.warn("IProgression not available - create progression.py")

# ============ CONDITIONAL EXPORTS ============
# Only export what's actually available

_AVAILABLE_ABSTRACTIONS = []

# Infrastructure Boundaries
if _HAS_LLM_PROVIDER:
    _AVAILABLE_ABSTRACTIONS.append('ILLMProvider')
if _HAS_EXPORT_SERVICE:
    _AVAILABLE_ABSTRACTIONS.append('IExportService')

# Data Access Boundaries
if _HAS_CHARACTER_REPO:
    _AVAILABLE_ABSTRACTIONS.append('ICharacterRepository')
if _HAS_CONVERSATION_REPO:
    _AVAILABLE_ABSTRACTIONS.append('IConversationRepository')
if _HAS_CONTENT_REPO:
    _AVAILABLE_ABSTRACTIONS.append('IContentRepository')

# Business Logic Boundaries
if _HAS_CONTENT_GENERATOR:
    _AVAILABLE_ABSTRACTIONS.append('IContentGenerator')
if _HAS_BALANCE_ANALYZER:
    _AVAILABLE_ABSTRACTIONS.append('IBalanceAnalyzer')
if _HAS_CONTENT_VALIDATOR:
    _AVAILABLE_ABSTRACTIONS.append('IContentValidator')

# Domain Entity Contracts
if _HAS_SPECIES:
    _AVAILABLE_ABSTRACTIONS.append('ISpecies')
if _HAS_CHARACTER_CLASS:
    _AVAILABLE_ABSTRACTIONS.extend(['ICharacterClass', 'ISubclass'])
if _HAS_BACKGROUND:
    _AVAILABLE_ABSTRACTIONS.append('IBackground')
if _HAS_FEAT:
    _AVAILABLE_ABSTRACTIONS.append('IFeat')
if _HAS_SPELL:
    _AVAILABLE_ABSTRACTIONS.append('ISpell')
if _HAS_EQUIPMENT:
    _AVAILABLE_ABSTRACTIONS.extend(['IEquipment', 'IWeapon', 'IArmor', 'IMagicItem'])
if _HAS_CHARACTER:
    _AVAILABLE_ABSTRACTIONS.append('ICharacter')
if _HAS_CHARACTER_SHEET:
    _AVAILABLE_ABSTRACTIONS.append('ICharacterSheet')
if _HAS_PROGRESSION:
    _AVAILABLE_ABSTRACTIONS.append('IProgression')

# Always include utility functions
_AVAILABLE_ABSTRACTIONS.extend([
    'get_available_abstractions',
    'validate_abstraction_implementation', 
    'get_abstraction_registry',
    'check_clean_architecture_compliance',
    'get_missing_abstractions',
    'create_abstraction_template'
])

__all__ = _AVAILABLE_ABSTRACTIONS

# ============ DYNAMIC REGISTRY BASED ON AVAILABLE ABSTRACTIONS ============

def _build_abstraction_registry() -> Dict[str, Dict[str, Optional[Type]]]:
    """Build registry with only available abstractions."""
    registry = {
        'infrastructure': {},
        'application': {},
        'domain': {}
    }
    
    # Infrastructure Layer
    if _HAS_LLM_PROVIDER:
        registry['infrastructure']['llm_provider'] = ILLMProvider
    if _HAS_EXPORT_SERVICE:
        registry['infrastructure']['export_service'] = IExportService
    
    # Application Layer
    if _HAS_CHARACTER_REPO:
        registry['application']['character_repository'] = ICharacterRepository
    if _HAS_CONVERSATION_REPO:
        registry['application']['conversation_repository'] = IConversationRepository
    if _HAS_CONTENT_REPO:
        registry['application']['content_repository'] = IContentRepository
    
    # Domain Layer - Services
    if _HAS_CONTENT_GENERATOR:
        registry['domain']['content_generator'] = IContentGenerator
    if _HAS_BALANCE_ANALYZER:
        registry['domain']['balance_analyzer'] = IBalanceAnalyzer
    if _HAS_CONTENT_VALIDATOR:
        registry['domain']['content_validator'] = IContentValidator
    
    # Domain Layer - Entities
    if _HAS_CHARACTER:
        registry['domain']['character'] = ICharacter
    if _HAS_CHARACTER_SHEET:
        registry['domain']['character_sheet'] = ICharacterSheet
    if _HAS_PROGRESSION:
        registry['domain']['progression'] = IProgression
    if _HAS_SPECIES:
        registry['domain']['species'] = ISpecies
    if _HAS_CHARACTER_CLASS:
        registry['domain']['character_class'] = ICharacterClass
        registry['domain']['subclass'] = ISubclass
    if _HAS_BACKGROUND:
        registry['domain']['background'] = IBackground
    if _HAS_FEAT:
        registry['domain']['feat'] = IFeat
    if _HAS_SPELL:
        registry['domain']['spell'] = ISpell
    if _HAS_EQUIPMENT:
        registry['domain']['equipment'] = IEquipment
        registry['domain']['weapon'] = IWeapon
        registry['domain']['armor'] = IArmor
        registry['domain']['magic_item'] = IMagicItem
    
    return registry

# Build registry with available abstractions
ABSTRACTION_REGISTRY = _build_abstraction_registry()

# ============ UTILITY FUNCTIONS ============

def get_available_abstractions() -> Dict[str, List[str]]:
    """
    Get all available abstractions organized by Clean Architecture layer.
    
    Returns:
        Dictionary mapping layers to their available abstractions
    """
    return {
        layer: list(abstractions.keys()) 
        for layer, abstractions in ABSTRACTION_REGISTRY.items()
        if abstractions  # Only include layers that have abstractions
    }

def get_missing_abstractions() -> Dict[str, List[str]]:
    """
    Get missing abstractions that should be created.
    
    Returns:
        Dictionary mapping layers to missing abstractions
    """
    expected_abstractions = {
        'infrastructure': [
            ('llm_provider', _HAS_LLM_PROVIDER),
            ('export_service', _HAS_EXPORT_SERVICE)
        ],
        'application': [
            ('character_repository', _HAS_CHARACTER_REPO),
            ('conversation_repository', _HAS_CONVERSATION_REPO),
            ('content_repository', _HAS_CONTENT_REPO)
        ],
        'domain': [
            ('content_generator', _HAS_CONTENT_GENERATOR),
            ('balance_analyzer', _HAS_BALANCE_ANALYZER),
            ('content_validator', _HAS_CONTENT_VALIDATOR),
            ('character', _HAS_CHARACTER),
            ('character_sheet', _HAS_CHARACTER_SHEET),
            ('progression', _HAS_PROGRESSION),
            ('species', _HAS_SPECIES),
            ('character_class', _HAS_CHARACTER_CLASS),
            ('background', _HAS_BACKGROUND),
            ('feat', _HAS_FEAT),
            ('spell', _HAS_SPELL),
            ('equipment', _HAS_EQUIPMENT)
        ]
    }
    
    missing = {}
    for layer, abstractions in expected_abstractions.items():
        missing_in_layer = [name for name, available in abstractions if not available]
        if missing_in_layer:
            missing[layer] = missing_in_layer
    
    return missing

def get_abstraction_registry() -> Dict[str, Dict[str, Optional[Type]]]:
    """Get the complete abstraction registry organized by layer."""
    return ABSTRACTION_REGISTRY.copy()

def check_clean_architecture_compliance() -> Dict[str, List[str]]:
    """
    Validate Clean Architecture compliance of available abstractions.
    
    Returns:
        Dictionary of compliance issues by layer
    """
    issues = {}
    
    # Check infrastructure layer - should have minimal abstractions
    infra_abstractions = ABSTRACTION_REGISTRY.get('infrastructure', {})
    if len(infra_abstractions) > 5:  # Should be minimal
        issues['infrastructure'] = ['Too many infrastructure abstractions - violates Clean Architecture']
    
    # Check domain layer - should contain business logic abstractions
    domain_abstractions = ABSTRACTION_REGISTRY.get('domain', {})
    required_domain = ['content_generator', 'balance_analyzer', 'character']
    missing_domain = [abs_name for abs_name in required_domain if abs_name not in domain_abstractions]
    if missing_domain:
        issues['domain'] = [f'Missing critical domain abstraction: {abs_name}' for abs_name in missing_domain]
    
    # Check application layer - should have orchestration abstractions
    app_abstractions = ABSTRACTION_REGISTRY.get('application', {})
    if not app_abstractions:
        issues['application'] = ['Application layer has no abstractions']
    
    # Check for missing abstractions
    missing = get_missing_abstractions()
    for layer, missing_abstractions in missing.items():
        if missing_abstractions:
            if layer not in issues:
                issues[layer] = []
            issues[layer].extend([f'Missing abstraction file: {abs_name}.py' for abs_name in missing_abstractions])
    
    return issues

def validate_abstraction_implementation(impl_class: Type, expected_abstract: Type) -> List[str]:
    """
    Validate that a concrete class properly implements an abstraction.
    
    Args:
        impl_class: The concrete implementation class to validate
        expected_abstract: The abstract base class it should implement
        
    Returns:
        List of validation issues (empty if valid)
    """
    if expected_abstract is None:
        return [f"Cannot validate - abstract class not available"]
    
    issues = []
    
    # Check inheritance
    if not issubclass(impl_class, expected_abstract):
        issues.append(f"{impl_class.__name__} does not inherit from {expected_abstract.__name__}")
        return issues
    
    # Check for required abstract methods
    abstract_methods = getattr(expected_abstract, '__abstractmethods__', set())
    for method_name in abstract_methods:
        if not hasattr(impl_class, method_name):
            issues.append(f"Missing required method: {method_name}")
        else:
            method = getattr(impl_class, method_name)
            if getattr(method, '__isabstractmethod__', False):
                issues.append(f"Method {method_name} is not properly implemented")
    
    return issues

def get_abstractions_by_layer(layer: str) -> Dict[str, Optional[Type]]:
    """Get abstractions for a specific Clean Architecture layer."""
    return ABSTRACTION_REGISTRY.get(layer.lower(), {})

def get_domain_entity_abstractions() -> Dict[str, Optional[Type]]:
    """Get domain entity abstractions specifically."""
    domain_abstractions = ABSTRACTION_REGISTRY.get('domain', {})
    entity_abstractions = {}
    
    # Entity abstractions (not services)
    entity_names = [
        'character', 'character_sheet', 'progression', 'species', 
        'character_class', 'subclass', 'background', 'feat', 'spell', 
        'equipment', 'weapon', 'armor', 'magic_item'
    ]
    
    for name in entity_names:
        if name in domain_abstractions:
            entity_abstractions[name] = domain_abstractions[name]
    
    return entity_abstractions

def get_domain_service_abstractions() -> Dict[str, Optional[Type]]:
    """Get domain service abstractions specifically."""
    domain_abstractions = ABSTRACTION_REGISTRY.get('domain', {})
    service_abstractions = {}
    
    # Service abstractions
    service_names = ['content_generator', 'balance_analyzer', 'content_validator']
    
    for name in service_names:
        if name in domain_abstractions:
            service_abstractions[name] = domain_abstractions[name]
    
    return service_abstractions

def get_infrastructure_abstractions() -> Dict[str, Optional[Type]]:
    """Get infrastructure boundary abstractions."""
    return ABSTRACTION_REGISTRY.get('infrastructure', {})

def get_application_abstractions() -> Dict[str, Optional[Type]]:
    """Get application layer abstractions."""
    return ABSTRACTION_REGISTRY.get('application', {})

def create_abstraction_template(abstraction_name: str, layer: str) -> str:
    """
    Generate a template for a missing abstraction.
    
    Args:
        abstraction_name: Name of the abstraction to create
        layer: Clean Architecture layer (infrastructure, application, domain)
        
    Returns:
        Template code for the abstraction
    """
    class_name = f"I{abstraction_name.title().replace('_', '')}"
    
    template = f'''"""
{abstraction_name.title().replace('_', ' ')} Interface - {layer.title()} Layer Boundary.

TODO: Complete this abstraction according to Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class {class_name}(ABC):
    """
    Interface for {abstraction_name.replace('_', ' ')}.
    
    TODO: Add detailed interface documentation here.
    """
    
    @abstractmethod
    def example_method(self) -> None:
        """
        TODO: Define the required methods for this interface.
        
        This is a placeholder method - replace with actual interface methods.
        """
        pass
'''
    
    return template

def get_implementation_status() -> Dict[str, Dict[str, bool]]:
    """
    Get implementation status of all expected abstractions.
    
    Returns:
        Dictionary showing which abstractions are implemented
    """
    status = {}
    
    expected = {
        'infrastructure': ['llm_provider', 'export_service'],
        'application': ['character_repository', 'conversation_repository', 'content_repository'],
        'domain': [
            'content_generator', 'balance_analyzer', 'content_validator',
            'character', 'character_sheet', 'progression', 'species',
            'character_class', 'background', 'feat', 'spell', 'equipment'
        ]
    }
    
    flags = {
        'llm_provider': _HAS_LLM_PROVIDER,
        'export_service': _HAS_EXPORT_SERVICE,
        'character_repository': _HAS_CHARACTER_REPO,
        'conversation_repository': _HAS_CONVERSATION_REPO,
        'content_repository': _HAS_CONTENT_REPO,
        'content_generator': _HAS_CONTENT_GENERATOR,
        'balance_analyzer': _HAS_BALANCE_ANALYZER,
        'content_validator': _HAS_CONTENT_VALIDATOR,
        'character': _HAS_CHARACTER,
        'character_sheet': _HAS_CHARACTER_SHEET,
        'progression': _HAS_PROGRESSION,
        'species': _HAS_SPECIES,
        'character_class': _HAS_CHARACTER_CLASS,
        'background': _HAS_BACKGROUND,
        'feat': _HAS_FEAT,
        'spell': _HAS_SPELL,
        'equipment': _HAS_EQUIPMENT
    }
    
    for layer, abstractions in expected.items():
        status[layer] = {abs_name: flags.get(abs_name, False) for abs_name in abstractions}
    
    return status

def print_implementation_status():
    """Print a formatted report of abstraction implementation status."""
    status = get_implementation_status()
    missing = get_missing_abstractions()
    
    print("=== D&D Character Creator - Abstraction Implementation Status ===\n")
    
    for layer, abstractions in status.items():
        print(f"{layer.upper()} LAYER:")
        for abs_name, implemented in abstractions.items():
            status_symbol = "✅" if implemented else "❌"
            print(f"  {status_symbol} {abs_name}")
        print()
    
    if missing:
        print("MISSING ABSTRACTIONS TO CREATE:")
        for layer, missing_abstractions in missing.items():
            print(f"  {layer}: {', '.join(missing_abstractions)}")
        print()
    
    total_expected = sum(len(abstractions) for abstractions in status.values())
    total_implemented = sum(sum(abstractions.values()) for abstractions in status.values())
    completion_percentage = (total_implemented / total_expected) * 100 if total_expected > 0 else 0
    
    print(f"COMPLETION: {total_implemented}/{total_expected} ({completion_percentage:.1f}%)")

# Module metadata
__version__ = '1.0.0'
__description__ = 'Clean Architecture abstractions for D&D Creative Content Framework'

# Print status on import (can be disabled)
PRINT_STATUS_ON_IMPORT = True

if PRINT_STATUS_ON_IMPORT:
    import sys
    if not sys.flags.quiet:  # Only print if not in quiet mode
        print_implementation_status()