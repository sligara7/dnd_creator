"""
Application Use Cases Module

This module provides the primary business logic interfaces for the D&D Character Creator.
Use cases encapsulate specific business operations and orchestrate domain services.

Available Use Cases:
- ConceptProcessorUseCase: Analyze character background concepts
- GenerateContentUseCase: Generate D&D content from concepts  
- ValidationOrchestratorUseCase: Coordinate content validation
- BalanceAnalyzerUseCase: Analyze game balance implications
"""

# Core use cases
from .concept_processor import (
    ConceptProcessorUseCase,
    ConceptAnalysisRequest,
    ConceptAnalysisResponse,
    ThemeExtractor,
    CulturalAnalyzer,
    PowerLevelCalculator,
    MechanicalSuggestionEngine
)

from .generate_content import (
    GenerateContentUseCase,
    ContentGenerationRequest,
    ContentGenerationResponse,
    GenerationContext,
    ContentGenerationOrchestrator,
    GenerationPriority,
    # Specialized use cases
    GenerateSpeciesUseCase,
    GenerateClassUseCase,
    GenerateEquipmentUseCase,
    GenerateSpellSuiteUseCase,
    GenerateCompleteCharacterUseCase
)

# Validation and balance use cases
from .validation_orchestrator import (
    ValidationOrchestratorUseCase,
    ValidationRequest,
    ValidationResponse
)

from .balance_analyzer import (
    BalanceAnalyzerUseCase,
    BalanceAnalysisRequest,
    BalanceAnalysisResponse
)

# Factory functions for common use case combinations
def create_content_generation_pipeline():
    """Create a complete content generation pipeline with all dependencies."""
    from core.services import ContentGeneratorService, BalanceAnalyzerService
    
    # Initialize services (would be injected in real application)
    content_generator = ContentGeneratorService()
    balance_analyzer = BalanceAnalyzerService()
    concept_processor = ConceptProcessorUseCase()
    
    # Create main use case
    generate_content = GenerateContentUseCase(
        content_generator=content_generator,
        balance_analyzer=balance_analyzer,
        concept_processor=concept_processor
    )
    
    # Create specialized use cases
    return {
        'generate_content': generate_content,
        'generate_species': GenerateSpeciesUseCase(generate_content),
        'generate_class': GenerateClassUseCase(generate_content),
        'generate_equipment': GenerateEquipmentUseCase(generate_content),
        'generate_spells': GenerateSpellSuiteUseCase(generate_content),
        'generate_complete_character': GenerateCompleteCharacterUseCase(generate_content),
        'concept_processor': concept_processor
    }

def create_analysis_pipeline():
    """Create analysis pipeline for concept processing and validation."""
    concept_processor = ConceptProcessorUseCase()
    validation_orchestrator = ValidationOrchestratorUseCase()
    balance_analyzer = BalanceAnalyzerUseCase()
    
    return {
        'concept_processor': concept_processor,
        'validation_orchestrator': validation_orchestrator,
        'balance_analyzer': balance_analyzer
    }

# Convenience imports for common patterns
__all__ = [
    # Core use cases
    'ConceptProcessorUseCase',
    'GenerateContentUseCase', 
    'ValidationOrchestratorUseCase',
    'BalanceAnalyzerUseCase',
    
    # Request/Response objects
    'ConceptAnalysisRequest',
    'ConceptAnalysisResponse',
    'ContentGenerationRequest', 
    'ContentGenerationResponse',
    'ValidationRequest',
    'ValidationResponse',
    'BalanceAnalysisRequest',
    'BalanceAnalysisResponse',
    
    # Specialized use cases
    'GenerateSpeciesUseCase',
    'GenerateClassUseCase',
    'GenerateEquipmentUseCase',
    'GenerateSpellSuiteUseCase',
    'GenerateCompleteCharacterUseCase',
    
    # Supporting classes
    'GenerationContext',
    'ContentGenerationOrchestrator',
    'GenerationPriority',
    'ThemeExtractor',
    'CulturalAnalyzer',
    'PowerLevelCalculator',
    'MechanicalSuggestionEngine',
    
    # Factory functions
    'create_content_generation_pipeline',
    'create_analysis_pipeline'
]

# Version information
__version__ = '1.0.0'

# Module-level configuration
DEFAULT_QUALITY_THRESHOLD = 0.8
DEFAULT_GENERATION_TIMEOUT = 300
DEFAULT_MAX_ALTERNATIVES = 3

# Use case registry for dynamic discovery
USE_CASE_REGISTRY = {
    'concept_analysis': ConceptProcessorUseCase,
    'content_generation': GenerateContentUseCase,
    'validation': ValidationOrchestratorUseCase,
    'balance_analysis': BalanceAnalyzerUseCase,
    'species_generation': GenerateSpeciesUseCase,
    'class_generation': GenerateClassUseCase,
    'equipment_generation': GenerateEquipmentUseCase,
    'spell_generation': GenerateSpellSuiteUseCase,
    'complete_character_generation': GenerateCompleteCharacterUseCase
}

def get_use_case(use_case_name: str):
    """Get a use case by name from the registry."""
    return USE_CASE_REGISTRY.get(use_case_name)

def list_available_use_cases():
    """List all available use cases."""
    return list(USE_CASE_REGISTRY.keys())