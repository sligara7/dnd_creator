"""
Core abstractions for the D&D Creative Content Framework.

This module defines the fundamental contracts that all content types must follow,
ensuring D&D 2024 rule compliance while enabling creative freedom in content generation.

These abstractions enforce Clean Architecture boundaries by defining interfaces
that are infrastructure-independent and focused on business rules.
"""

# ============ CORE LAYER ABSTRACTIONS ============
# Foundation interfaces - infrastructure independent

# LLM Provider Interface (Infrastructure boundary)
from .llm_provider import ILLMProvider

# Content Generation Interfaces (Business logic boundary)
from .content_generator import IContentGenerator
from .balance_analyzer import IBalanceAnalyzer

# Repository Interfaces (Data access boundary)
from .character_repository import ICharacterRepository
from .conversation_repository import IConversationRepository
from .content_repository import IContentRepository

# Export Service Interface (External systems boundary)  
from .export_service import IExportService

# Validation Interface (Business rule enforcement)
from .content_validator import IContentValidator

# ============ DOMAIN ENTITY ABSTRACTIONS ============
# Business entity contracts

# Character Building Blocks
from .species import ISpecies
from .character_class import ICharacterClass, ISubclass
from .background import IBackground

# Content Types
from .feat import IFeat
from .spell import ISpell
from .equipment import IEquipment, IWeapon, IArmor, IMagicItem

# Character Progression
from .character import ICharacter
from .character_sheet import ICharacterSheet
from .progression import IProgression

# Export all public interfaces organized by architectural concern
__all__ = [
    # ============ INFRASTRUCTURE BOUNDARIES ============
    'ILLMProvider',           # LLM service abstraction
    'IExportService',         # VTT export abstraction
    
    # ============ DATA ACCESS BOUNDARIES ============
    'ICharacterRepository',   # Character persistence
    'IConversationRepository', # Conversation state
    'IContentRepository',     # Custom content storage
    
    # ============ BUSINESS LOGIC BOUNDARIES ============
    'IContentGenerator',      # Content creation logic
    'IBalanceAnalyzer',       # Power level analysis
    'IContentValidator',      # Rule compliance checking
    
    # ============ DOMAIN ENTITY CONTRACTS ============
    # Character Building Blocks
    'ISpecies',              # Species/race interface
    'ICharacterClass',       # Class interface
    'ISubclass',             # Subclass interface  
    'IBackground',           # Background interface
    
    # Content Entities
    'IFeat',                 # Feat interface
    'ISpell',                # Spell interface
    'IEquipment',            # Equipment interface
    'IWeapon',               # Weapon interface
    'IArmor',                # Armor interface
    'IMagicItem',            # Magic item interface
    
    # Character System
    'ICharacter',            # Character entity
    'ICharacterSheet',       # Character sheet (JSON export)
    'IProgression',          # Level progression
    
    # Utility Functions
    'get_available_abstractions',
    'validate_abstraction_implementation',
    'get_abstraction_registry',
    'check_clean_architecture_compliance',
]

# Registry organized by Clean Architecture layers
ABSTRACTION_REGISTRY = {
    # ============ INFRASTRUCTURE LAYER ============
    'infrastructure': {
        'llm_provider': ILLMProvider,
        'export_service': IExportService,
    },
    
    # ============ APPLICATION LAYER ============  
    'application': {
        'character_repository': ICharacterRepository,
        'conversation_repository': IConversationRepository,
        'content_repository': IContentRepository,
    },
    
    # ============ DOMAIN LAYER ============
    'domain': {
        # Business Services
        'content_generator': IContentGenerator,
        'balance_analyzer': IBalanceAnalyzer,
        'content_validator': IContentValidator,
        
        # Domain Entities
        'character': ICharacter,
        'character_sheet': ICharacterSheet,
        'progression': IProgression,
        'species': ISpecies,
        'character_class': ICharacterClass,
        'subclass': ISubclass,
        'background': IBackground,
        'feat': IFeat,
        'spell': ISpell,
        'equipment': IEquipment,
        'weapon': IWeapon,
        'armor': IArmor,
        'magic_item': IMagicItem,
    }
}

def get_available_abstractions() -> dict[str, list[str]]:
    """
    Get all available abstractions organized by Clean Architecture layer.
    
    Returns:
        Dictionary mapping layers to their abstractions
    """
    return {
        layer: list(abstractions.keys()) 
        for layer, abstractions in ABSTRACTION_REGISTRY.items()
    }

def get_abstraction_registry() -> dict[str, dict[str, type]]:
    """Get the complete abstraction registry organized by layer."""
    return ABSTRACTION_REGISTRY.copy()

def check_clean_architecture_compliance() -> dict[str, list[str]]:
    """
    Validate Clean Architecture compliance of all abstractions.
    
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
    
    return issues

def validate_abstraction_implementation(impl_class: type, expected_abstract: type) -> list[str]:
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

def get_abstractions_by_layer(layer: str) -> dict[str, type]:
    """Get abstractions for a specific Clean Architecture layer."""
    return ABSTRACTION_REGISTRY.get(layer.lower(), {})

def get_domain_entity_abstractions() -> dict[str, type]:
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

def get_domain_service_abstractions() -> dict[str, type]:
    """Get domain service abstractions specifically."""
    domain_abstractions = ABSTRACTION_REGISTRY.get('domain', {})
    service_abstractions = {}
    
    # Service abstractions
    service_names = ['content_generator', 'balance_analyzer', 'content_validator']
    
    for name in service_names:
        if name in domain_abstractions:
            service_abstractions[name] = domain_abstractions[name]
    
    return service_abstractions

def get_infrastructure_abstractions() -> dict[str, type]:
    """Get infrastructure boundary abstractions."""
    return ABSTRACTION_REGISTRY.get('infrastructure', {})

def get_application_abstractions() -> dict[str, type]:
    """Get application layer abstractions."""
    return ABSTRACTION_REGISTRY.get('application', {})