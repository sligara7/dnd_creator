"""
Core Domain Services for D&D Creative Content Framework

Domain services encapsulate business logic that doesn't naturally fit within
entities or value objects. They provide coordination, orchestration, and
complex business operations that span multiple domain concepts.

Service Categories:
- Content Services: Core content generation and manipulation
- Validation Services: Business rule validation and compliance
- Analysis Services: Content analysis and evaluation
- Coordination Services: Cross-domain orchestration
- Utility Services: Common domain operations

These services maintain the business logic's purity while enabling complex
operations that require coordination between multiple domain concepts.
"""

from typing import List, Dict, Any, Optional, Type, Protocol
from abc import ABC, abstractmethod
import logging

# Core content services
from .content_generator import (
    ContentGeneratorService,
    SpeciesGeneratorService,
    ClassGeneratorService,
    EquipmentGeneratorService,
    SpellGeneratorService,
    FeatGeneratorService
)

# Validation and compliance services
from .validation_coordinator import (
    CoreValidationCoordinator,
    RuleComplianceService,
    BalanceValidationService,
    ThematicConsistencyService
)

# Analysis and evaluation services
from .balance_analyzer import (
    BalanceAnalyzerService,
    PowerLevelAnalyzer,
    MechanicalBalanceAnalyzer,
    GameplayImpactAnalyzer
)

from .content_analyzer import (
    ContentAnalyzerService,
    QualityAnalyzer,
    ComplexityAnalyzer,
    OriginalityAnalyzer
)

# Coordination and orchestration services
from .generation_coordinator import (
    GenerationCoordinatorService,
    DependencyResolver,
    ContentIntegrationService
)

from .theme_coordinator import (
    ThemeCoordinatorService,
    ThematicIntegrationService,
    CulturalConsistencyService
)

# Utility and support services
from .naming_service import (
    NamingService,
    CulturalNamingService,
    ThematicNamingService
)

from .template_service import (
    TemplateService,
    ContentTemplateService,
    StructureTemplateService
)

from .optimization_service import (
    OptimizationService,
    ContentOptimizer,
    PerformanceOptimizer
)

# Base service interfaces
from .base_service import (
    DomainService,
    ServiceRegistry,
    ServiceConfiguration
)

logger = logging.getLogger(__name__)


# Service factory for dependency injection and lifecycle management
class DomainServiceFactory:
    """Factory for creating and managing domain service instances."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._configurations: Dict[str, ServiceConfiguration] = {}
        self._registry = ServiceRegistry()
    
    def register_service(self, service_name: str, service_class: Type[DomainService], 
                        config: Optional[ServiceConfiguration] = None):
        """Register a service class with optional configuration."""
        self._registry.register(service_name, service_class)
        if config:
            self._configurations[service_name] = config
    
    def create_service(self, service_name: str, **kwargs) -> DomainService:
        """Create service instance with dependencies."""
        service_class = self._registry.get_service_class(service_name)
        if not service_class:
            raise ValueError(f"Unknown service: {service_name}")
        
        config = self._configurations.get(service_name, ServiceConfiguration())
        
        # Create service with configuration and dependencies
        return service_class(config=config, **kwargs)
    
    def get_or_create_service(self, service_name: str, **kwargs) -> DomainService:
        """Get existing service instance or create new one."""
        if service_name not in self._services:
            self._services[service_name] = self.create_service(service_name, **kwargs)
        return self._services[service_name]
    
    def create_content_generation_suite(self, **dependencies) -> Dict[str, DomainService]:
        """Create complete content generation service suite."""
        return {
            'content_generator': self.get_or_create_service('content_generator', **dependencies),
            'species_generator': self.get_or_create_service('species_generator', **dependencies),
            'class_generator': self.get_or_create_service('class_generator', **dependencies),
            'equipment_generator': self.get_or_create_service('equipment_generator', **dependencies),
            'spell_generator': self.get_or_create_service('spell_generator', **dependencies),
            'feat_generator': self.get_or_create_service('feat_generator', **dependencies),
            'generation_coordinator': self.get_or_create_service('generation_coordinator', **dependencies)
        }
    
    def create_validation_suite(self, **dependencies) -> Dict[str, DomainService]:
        """Create complete validation service suite."""
        return {
            'validation_coordinator': self.get_or_create_service('validation_coordinator', **dependencies),
            'rule_compliance': self.get_or_create_service('rule_compliance', **dependencies),
            'balance_validation': self.get_or_create_service('balance_validation', **dependencies),
            'thematic_consistency': self.get_or_create_service('thematic_consistency', **dependencies)
        }
    
    def create_analysis_suite(self, **dependencies) -> Dict[str, DomainService]:
        """Create complete analysis service suite."""
        return {
            'balance_analyzer': self.get_or_create_service('balance_analyzer', **dependencies),
            'content_analyzer': self.get_or_create_service('content_analyzer', **dependencies),
            'quality_analyzer': self.get_or_create_service('quality_analyzer', **dependencies),
            'power_level_analyzer': self.get_or_create_service('power_level_analyzer', **dependencies)
        }


# Service coordination and orchestration
class ServiceOrchestrator:
    """Orchestrates complex operations across multiple domain services."""
    
    def __init__(self, service_factory: DomainServiceFactory):
        self.service_factory = service_factory
        self.content_services = service_factory.create_content_generation_suite()
        self.validation_services = service_factory.create_validation_suite()
        self.analysis_services = service_factory.create_analysis_suite()
    
    async def orchestrate_content_generation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate complete content generation workflow."""
        try:
            # Step 1: Generate content
            generation_result = await self.content_services['content_generator'].generate_content(request)
            
            # Step 2: Validate generated content
            validation_result = await self.validation_services['validation_coordinator'].validate_content(
                generation_result['content']
            )
            
            # Step 3: Analyze quality and balance
            analysis_result = await self.analysis_services['content_analyzer'].analyze_content(
                generation_result['content']
            )
            
            # Step 4: Optimize if needed
            if analysis_result['needs_optimization']:
                optimization_service = self.service_factory.get_or_create_service('optimization_service')
                optimization_result = await optimization_service.optimize_content(
                    generation_result['content'], analysis_result['suggestions']
                )
                generation_result['content'] = optimization_result['optimized_content']
            
            return {
                'success': True,
                'content': generation_result['content'],
                'validation': validation_result,
                'analysis': analysis_result,
                'metadata': {
                    'generation_time': generation_result.get('processing_time', 0),
                    'validation_passed': validation_result.get('is_valid', False),
                    'quality_score': analysis_result.get('quality_score', 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Content generation orchestration failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'metadata': {'operation': 'content_generation_orchestration'}
            }
    
    async def orchestrate_content_validation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate comprehensive content validation."""
        validation_results = {}
        
        try:
            # Rule compliance validation
            rule_compliance = await self.validation_services['rule_compliance'].validate(content)
            validation_results['rule_compliance'] = rule_compliance
            
            # Balance validation
            balance_validation = await self.validation_services['balance_validation'].validate(content)
            validation_results['balance_validation'] = balance_validation
            
            # Thematic consistency validation
            thematic_validation = await self.validation_services['thematic_consistency'].validate(content)
            validation_results['thematic_consistency'] = thematic_validation
            
            # Overall validation assessment
            overall_valid = all(
                result.get('is_valid', False) for result in validation_results.values()
            )
            
            return {
                'success': True,
                'is_valid': overall_valid,
                'validation_results': validation_results,
                'summary': self._create_validation_summary(validation_results)
            }
            
        except Exception as e:
            logger.error(f"Content validation orchestration failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'is_valid': False
            }
    
    def _create_validation_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of validation results."""
        total_issues = sum(
            len(result.get('issues', [])) for result in validation_results.values()
        )
        critical_issues = sum(
            len([issue for issue in result.get('issues', []) if issue.get('severity') == 'critical'])
            for result in validation_results.values()
        )
        
        return {
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'validation_categories': len(validation_results),
            'passed_validations': sum(
                1 for result in validation_results.values() if result.get('is_valid', False)
            )
        }


# Comprehensive service registry with all available services
COMPREHENSIVE_SERVICE_REGISTRY = {
    # Content generation services
    'content_generator': ContentGeneratorService,
    'species_generator': SpeciesGeneratorService,
    'class_generator': ClassGeneratorService,
    'equipment_generator': EquipmentGeneratorService,
    'spell_generator': SpellGeneratorService,
    'feat_generator': FeatGeneratorService,
    
    # Validation services
    'validation_coordinator': CoreValidationCoordinator,
    'rule_compliance': RuleComplianceService,
    'balance_validation': BalanceValidationService,
    'thematic_consistency': ThematicConsistencyService,
    
    # Analysis services
    'balance_analyzer': BalanceAnalyzerService,
    'content_analyzer': ContentAnalyzerService,
    'quality_analyzer': QualityAnalyzer,
    'complexity_analyzer': ComplexityAnalyzer,
    'originality_analyzer': OriginalityAnalyzer,
    'power_level_analyzer': PowerLevelAnalyzer,
    'mechanical_balance_analyzer': MechanicalBalanceAnalyzer,
    'gameplay_impact_analyzer': GameplayImpactAnalyzer,
    
    # Coordination services
    'generation_coordinator': GenerationCoordinatorService,
    'theme_coordinator': ThemeCoordinatorService,
    'dependency_resolver': DependencyResolver,
    'content_integration': ContentIntegrationService,
    'thematic_integration': ThematicIntegrationService,
    'cultural_consistency': CulturalConsistencyService,
    
    # Utility services
    'naming_service': NamingService,
    'cultural_naming': CulturalNamingService,
    'thematic_naming': ThematicNamingService,
    'template_service': TemplateService,
    'content_template': ContentTemplateService,
    'structure_template': StructureTemplateService,
    'optimization_service': OptimizationService,
    'content_optimizer': ContentOptimizer,
    'performance_optimizer': PerformanceOptimizer
}


# Convenience functions for service creation
def create_default_service_factory() -> DomainServiceFactory:
    """Create service factory with all services registered."""
    factory = DomainServiceFactory()
    
    for service_name, service_class in COMPREHENSIVE_SERVICE_REGISTRY.items():
        factory.register_service(service_name, service_class)
    
    return factory


def create_service_orchestrator(service_factory: Optional[DomainServiceFactory] = None) -> ServiceOrchestrator:
    """Create service orchestrator with default or provided factory."""
    if service_factory is None:
        service_factory = create_default_service_factory()
    
    return ServiceOrchestrator(service_factory)


def get_service_class(service_name: str) -> Optional[Type[DomainService]]:
    """Get service class by name from registry."""
    return COMPREHENSIVE_SERVICE_REGISTRY.get(service_name)


def list_available_services() -> List[str]:
    """Get list of all available domain services."""
    return list(COMPREHENSIVE_SERVICE_REGISTRY.keys())


def get_services_by_category() -> Dict[str, List[str]]:
    """Get services organized by category."""
    categories = {
        'content_generation': [
            'content_generator', 'species_generator', 'class_generator',
            'equipment_generator', 'spell_generator', 'feat_generator'
        ],
        'validation': [
            'validation_coordinator', 'rule_compliance', 'balance_validation',
            'thematic_consistency'
        ],
        'analysis': [
            'balance_analyzer', 'content_analyzer', 'quality_analyzer',
            'complexity_analyzer', 'originality_analyzer', 'power_level_analyzer',
            'mechanical_balance_analyzer', 'gameplay_impact_analyzer'
        ],
        'coordination': [
            'generation_coordinator', 'theme_coordinator', 'dependency_resolver',
            'content_integration', 'thematic_integration', 'cultural_consistency'
        ],
        'utility': [
            'naming_service', 'cultural_naming', 'thematic_naming',
            'template_service', 'content_template', 'structure_template',
            'optimization_service', 'content_optimizer', 'performance_optimizer'
        ]
    }
    
    return categories


# Quick access functions for common service combinations
def create_content_generation_services(**dependencies) -> Dict[str, DomainService]:
    """Create content generation service suite."""
    factory = create_default_service_factory()
    return factory.create_content_generation_suite(**dependencies)


def create_validation_services(**dependencies) -> Dict[str, DomainService]:
    """Create validation service suite."""
    factory = create_default_service_factory()
    return factory.create_validation_suite(**dependencies)


def create_analysis_services(**dependencies) -> Dict[str, DomainService]:
    """Create analysis service suite."""
    factory = create_default_service_factory()
    return factory.create_analysis_suite(**dependencies)


# Export all public components
__all__ = [
    # Base classes and interfaces
    'DomainService',
    'ServiceRegistry',
    'ServiceConfiguration',
    
    # Content generation services
    'ContentGeneratorService',
    'SpeciesGeneratorService',
    'ClassGeneratorService',
    'EquipmentGeneratorService',
    'SpellGeneratorService',
    'FeatGeneratorService',
    
    # Validation services
    'CoreValidationCoordinator',
    'RuleComplianceService',
    'BalanceValidationService',
    'ThematicConsistencyService',
    
    # Analysis services
    'BalanceAnalyzerService',
    'ContentAnalyzerService',
    'QualityAnalyzer',
    'ComplexityAnalyzer',
    'OriginalityAnalyzer',
    'PowerLevelAnalyzer',
    'MechanicalBalanceAnalyzer',
    'GameplayImpactAnalyzer',
    
    # Coordination services
    'GenerationCoordinatorService',
    'ThemeCoordinatorService',
    'DependencyResolver',
    'ContentIntegrationService',
    'ThematicIntegrationService',
    'CulturalConsistencyService',
    
    # Utility services
    'NamingService',
    'CulturalNamingService',
    'ThematicNamingService',
    'TemplateService',
    'ContentTemplateService',
    'StructureTemplateService',
    'OptimizationService',
    'ContentOptimizer',
    'PerformanceOptimizer',
    
    # Factory and orchestration
    'DomainServiceFactory',
    'ServiceOrchestrator',
    
    # Convenience functions
    'create_default_service_factory',
    'create_service_orchestrator',
    'get_service_class',
    'list_available_services',
    'get_services_by_category',
    'create_content_generation_services',
    'create_validation_services',
    'create_analysis_services',
    
    # Registry
    'COMPREHENSIVE_SERVICE_REGISTRY'
]

# Version and metadata
__version__ = '1.0.0'
__description__ = 'Core domain services for D&D Creative Content Framework'

# Default configuration
DEFAULT_SERVICE_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_CACHE_TTL = 300