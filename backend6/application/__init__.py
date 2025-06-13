"""
Application Layer

The application layer orchestrates business workflows and coordinates between
the domain layer and infrastructure concerns. It contains use cases, DTOs,
and application services that implement the primary business operations
of the D&D Character Creator.

Architecture:
- Use Cases: Business workflow orchestration
- DTOs: Data transfer objects for layer communication
- Services: Application-level services and coordination
- Interfaces: Contracts for external dependencies

This layer is framework-agnostic and focuses purely on business logic coordination.
"""

# Core application components
from .use_cases import (
    # Primary use cases
    ConceptProcessorUseCase,
    GenerateContentUseCase,
    ValidationOrchestratorUseCase,
    BalanceAnalyzerUseCase,
    
    # Specialized use cases
    GenerateSpeciesUseCase,
    GenerateClassUseCase,
    GenerateEquipmentUseCase,
    GenerateSpellSuiteUseCase,
    GenerateCompleteCharacterUseCase,
    
    # Factory functions
    create_content_generation_pipeline,
    create_analysis_pipeline
)

from .dtos import (
    # Request DTOs
    ConceptAnalysisRequestDTO,
    ContentGenerationRequestDTO,
    ValidationRequestDTO,
    BalanceAnalysisRequestDTO,
    
    # Response DTOs
    ConceptAnalysisResponseDTO,
    ContentGenerationResponseDTO,
    ValidationResponseDTO,
    BalanceAnalysisResponseDTO,
    
    # Content DTOs
    SpeciesDTO,
    CharacterClassDTO,
    EquipmentDTO,
    SpellDTO,
    FeatDTO,
    
    # Utility functions
    create_request_dto,
    create_response_dto,
    entity_to_dto,
    dto_to_entity
)

from .services import (
    ApplicationService,
    ContentGenerationCoordinatorService,
    ValidationCoordinatorService,
    NotificationService,
    CacheService,
    EventPublisherService
)

# Application-level interfaces (contracts for infrastructure)
from .interfaces import (
    IRepositoryManager,
    IExternalServiceAdapter,
    IContentGeneratorAdapter,
    IValidationAdapter,
    INotificationAdapter,
    ICacheAdapter,
    IEventBusAdapter
)

# Application configuration and setup
class ApplicationConfig:
    """Application layer configuration."""
    
    def __init__(self):
        self.enable_caching = True
        self.enable_notifications = True
        self.enable_events = True
        self.default_timeout = 300
        self.max_concurrent_operations = 10
        self.quality_threshold = 0.8
        self.enable_metrics = True

# Application factory for dependency injection
class ApplicationFactory:
    """Factory for creating application layer components with proper dependencies."""
    
    def __init__(self, config: ApplicationConfig):
        self.config = config
        self._use_cases = {}
        self._services = {}
    
    def create_concept_processor(self, **dependencies) -> ConceptProcessorUseCase:
        """Create concept processor with dependencies."""
        if 'concept_processor' not in self._use_cases:
            self._use_cases['concept_processor'] = ConceptProcessorUseCase()
        return self._use_cases['concept_processor']
    
    def create_content_generator(self, **dependencies) -> GenerateContentUseCase:
        """Create content generator with dependencies."""
        if 'content_generator' not in self._use_cases:
            # Inject required dependencies
            content_generator_service = dependencies.get('content_generator_service')
            balance_analyzer_service = dependencies.get('balance_analyzer_service')
            concept_processor = self.create_concept_processor()
            
            self._use_cases['content_generator'] = GenerateContentUseCase(
                content_generator=content_generator_service,
                balance_analyzer=balance_analyzer_service,
                concept_processor=concept_processor
            )
        return self._use_cases['content_generator']
    
    def create_validation_orchestrator(self, **dependencies) -> ValidationOrchestratorUseCase:
        """Create validation orchestrator with dependencies."""
        if 'validation_orchestrator' not in self._use_cases:
            self._use_cases['validation_orchestrator'] = ValidationOrchestratorUseCase()
        return self._use_cases['validation_orchestrator']
    
    def create_application_facade(self, **dependencies) -> 'ApplicationFacade':
        """Create application facade with all use cases."""
        return ApplicationFacade(
            concept_processor=self.create_concept_processor(**dependencies),
            content_generator=self.create_content_generator(**dependencies),
            validation_orchestrator=self.create_validation_orchestrator(**dependencies),
            config=self.config
        )

# Application facade for simplified access
class ApplicationFacade:
    """
    Simplified facade for application layer operations.
    
    Provides a clean interface for common application workflows
    while hiding the complexity of individual use cases.
    """
    
    def __init__(self, 
                 concept_processor: ConceptProcessorUseCase,
                 content_generator: GenerateContentUseCase,
                 validation_orchestrator: ValidationOrchestratorUseCase,
                 config: ApplicationConfig):
        self.concept_processor = concept_processor
        self.content_generator = content_generator
        self.validation_orchestrator = validation_orchestrator
        self.config = config
    
    async def analyze_and_generate_content(self, 
                                         concept_text: str,
                                         character_name: str = None,
                                         content_types: list = None) -> dict:
        """Complete workflow: analyze concept and generate content."""
        # Step 1: Analyze concept
        analysis_request = ConceptAnalysisRequestDTO(
            raw_concept=concept_text,
            character_name=character_name
        )
        analysis_response = await self.concept_processor.execute(analysis_request)
        
        if not analysis_response.success:
            return {'success': False, 'errors': analysis_response.errors}
        
        # Step 2: Generate content
        generation_request = ContentGenerationRequestDTO(
            concept=analysis_response.processed_concept,
            content_types=content_types or ['species', 'class'],
            target_quality_threshold=self.config.quality_threshold
        )
        generation_response = await self.content_generator.execute(generation_request)
        
        return {
            'success': generation_response.success,
            'analysis': analysis_response,
            'generated_content': generation_response,
            'errors': generation_response.errors
        }
    
    async def generate_species_from_concept(self, concept_text: str) -> dict:
        """Specialized workflow for species generation."""
        analysis_request = ConceptAnalysisRequestDTO(raw_concept=concept_text)
        analysis_response = await self.concept_processor.execute(analysis_request)
        
        if not analysis_response.success:
            return {'success': False, 'errors': analysis_response.errors}
        
        generation_request = ContentGenerationRequestDTO(
            concept=analysis_response.processed_concept,
            content_types=['species'],
            target_quality_threshold=0.85
        )
        generation_response = await self.content_generator.execute(generation_request)
        
        return {
            'success': generation_response.success,
            'species': generation_response.generated_collection,
            'errors': generation_response.errors
        }
    
    async def generate_complete_character(self, concept_text: str, 
                                        character_name: str = None) -> dict:
        """Generate complete character with all content types."""
        return await self.analyze_and_generate_content(
            concept_text=concept_text,
            character_name=character_name,
            content_types=['species', 'class', 'equipment', 'spells', 'feats']
        )

# Event handling setup
class ApplicationEventBus:
    """Application-level event bus for coordination."""
    
    def __init__(self):
        self._handlers = {}
    
    def subscribe(self, event_type: str, handler):
        """Subscribe to application events."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event_type: str, event_data: dict):
        """Publish application event."""
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                # Log error but don't break other handlers
                print(f"Event handler error: {e}")

# Application metrics and monitoring
class ApplicationMetrics:
    """Application-level metrics collection."""
    
    def __init__(self):
        self.concept_analyses_count = 0
        self.content_generations_count = 0
        self.validation_runs_count = 0
        self.average_processing_time = 0.0
        self.success_rate = 0.0
    
    def record_concept_analysis(self, processing_time: float, success: bool):
        """Record concept analysis metrics."""
        self.concept_analyses_count += 1
        self._update_averages(processing_time, success)
    
    def record_content_generation(self, processing_time: float, success: bool):
        """Record content generation metrics."""
        self.content_generations_count += 1
        self._update_averages(processing_time, success)
    
    def _update_averages(self, processing_time: float, success: bool):
        """Update running averages."""
        total_operations = (self.concept_analyses_count + 
                          self.content_generations_count + 
                          self.validation_runs_count)
        
        # Update average processing time
        self.average_processing_time = (
            (self.average_processing_time * (total_operations - 1) + processing_time) 
            / total_operations
        )
        
        # Update success rate (simplified)
        if success:
            self.success_rate = (self.success_rate * (total_operations - 1) + 1.0) / total_operations
        else:
            self.success_rate = (self.success_rate * (total_operations - 1)) / total_operations

# Convenience functions for common operations
async def analyze_concept(concept_text: str, **options) -> ConceptAnalysisResponseDTO:
    """Convenience function for concept analysis."""
    processor = ConceptProcessorUseCase()
    request = ConceptAnalysisRequestDTO(raw_concept=concept_text, **options)
    return await processor.execute(request)

async def generate_content_from_concept(concept_text: str, 
                                      content_types: list = None,
                                      **options) -> ContentGenerationResponseDTO:
    """Convenience function for content generation."""
    # First analyze concept
    analysis_response = await analyze_concept(concept_text)
    if not analysis_response.success:
        return ContentGenerationResponseDTO(
            success=False, 
            errors=analysis_response.errors
        )
    
    # Then generate content
    factory = ApplicationFactory(ApplicationConfig())
    generator = factory.create_content_generator()
    request = ContentGenerationRequestDTO(
        concept=analysis_response.processed_concept,
        content_types=content_types or ['species', 'class'],
        **options
    )
    return await generator.execute(request)

# Export all public components
__all__ = [
    # Use cases
    'ConceptProcessorUseCase',
    'GenerateContentUseCase',
    'ValidationOrchestratorUseCase',
    'BalanceAnalyzerUseCase',
    'GenerateSpeciesUseCase',
    'GenerateClassUseCase',
    'GenerateEquipmentUseCase',
    'GenerateSpellSuiteUseCase',
    'GenerateCompleteCharacterUseCase',
    
    # DTOs
    'ConceptAnalysisRequestDTO',
    'ContentGenerationRequestDTO',
    'ValidationRequestDTO',
    'BalanceAnalysisRequestDTO',
    'ConceptAnalysisResponseDTO',
    'ContentGenerationResponseDTO',
    'ValidationResponseDTO',
    'BalanceAnalysisResponseDTO',
    
    # Services
    'ApplicationService',
    'ContentGenerationCoordinatorService',
    'ValidationCoordinatorService',
    'NotificationService',
    'CacheService',
    'EventPublisherService',
    
    # Infrastructure interfaces
    'IRepositoryManager',
    'IExternalServiceAdapter',
    'IContentGeneratorAdapter',
    'IValidationAdapter',
    'INotificationAdapter',
    'ICacheAdapter',
    'IEventBusAdapter',
    
    # Application setup
    'ApplicationConfig',
    'ApplicationFactory',
    'ApplicationFacade',
    'ApplicationEventBus',
    'ApplicationMetrics',
    
    # Convenience functions
    'analyze_concept',
    'generate_content_from_concept',
    'create_content_generation_pipeline',
    'create_analysis_pipeline'
]

# Version and metadata
__version__ = '1.0.0'
__description__ = 'Application layer for D&D Character Creator'

# Default configuration
DEFAULT_CONFIG = ApplicationConfig()