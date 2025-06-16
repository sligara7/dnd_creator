"""
Culture LLM Provider Interface Contract - Refactored Architecture

Clean Architecture implementation for AI-powered creative culture generation providers.
Follows CREATIVE_VALIDATION_APPROACH philosophy with complete enum integration.

Architecture Principles:
- Dependency Inversion: Core doesn't depend on implementations
- Single Responsibility: Culture generation contracts only
- Interface Segregation: Specialized provider interfaces
- Pure Abstractions: No implementation details
- Character Generation Focus: Gaming utility optimization
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
import uuid
from datetime import datetime

# Import enhanced core enums (inward dependency only)
from ..enums.culture_types import (
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    CultureEnhancementCategory,
    CultureEnhancementPriority,
    CultureGenerationStatus,
    CultureValidationCategory,
    CultureValidationSeverity,
    get_optimal_authenticity_for_characters,
    suggest_creative_culture_enhancements,
    calculate_character_generation_score,
    get_character_generation_recommendations,
    CHARACTER_CULTURE_PRESETS,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE,
    CHARACTER_GENERATION_TYPE_GUIDELINES
)

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class CultureGenerationPrompt:
    """Template-based prompt for culture generation."""
    template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    prompt_type: str = "culture_generation"
    provider_specific: Dict[str, Any] = field(default_factory=dict)
    
    def format(self, **kwargs) -> str:
        """Format prompt with variables."""
        all_vars = {**self.variables, **kwargs}
        try:
            return self.template.format(**all_vars)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def validate_template(self) -> List[str]:
        """Validate template format."""
        issues = []
        if not self.template or not self.template.strip():
            issues.append("Template cannot be empty")
        if self.template.count('{') != self.template.count('}'):
            issues.append("Unmatched braces in template")
        return issues

@dataclass(frozen=True)
class CultureLLMResponse:
    """Standardized response from culture LLM provider."""
    content: str
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    provider_name: str = ""
    generation_time_ms: int = 0
    token_count: Optional[int] = None
    confidence_score: Optional[float] = None
    
    @property
    def is_successful(self) -> bool:
        """Check if response is successful and has content."""
        return self.success and bool(self.content.strip())
    
    @property
    def content_length(self) -> int:
        """Get length of generated content."""
        return len(self.content) if self.content else 0

@dataclass(frozen=True)
class CultureGenerationRequest:
    """Enhanced culture generation request with complete enum integration."""
    # Core identification
    cultural_reference: str
    session_id: Optional[str] = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Generation parameters
    generation_type: CultureGenerationType = CultureGenerationType.CHARACTER_FOCUSED
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.GAMING
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED_CREATIVE
    source_type: CultureSourceType = CultureSourceType.CHARACTER_ARCHETYPAL
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.GAMING_READY
    
    # Cultural structure parameters
    naming_structure: Optional[CultureNamingStructure] = CultureNamingStructure.GAMING_FRIENDLY
    gender_system: Optional[CultureGenderSystem] = CultureGenderSystem.CHARACTER_INCLUSIVE
    linguistic_family: Optional[CultureLinguisticFamily] = None
    temporal_period: Optional[CultureTemporalPeriod] = CultureTemporalPeriod.CHARACTER_TIMELESS
    
    # Character generation focus
    character_focus: bool = True
    gaming_optimization: bool = True
    include_character_hooks: bool = True
    include_background_elements: bool = True
    prefer_pronunciation_ease: bool = True
    
    # Enhancement preferences
    target_enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    enhancement_priority_threshold: CultureEnhancementPriority = CultureEnhancementPriority.CHARACTER_IMPORTANT
    
    # Preset support
    preset_name: Optional[str] = None
    
    # Creative validation approach settings
    enable_creative_freedom: bool = True
    constructive_suggestions_only: bool = True
    character_generation_priority: bool = True
    
    # Legacy and advanced parameters
    user_constraints: Optional[Dict[str, Any]] = None
    advanced_parameters: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Apply preset configuration and ensure defaults."""
        # Apply preset if specified
        if self.preset_name and self.preset_name in CHARACTER_CULTURE_PRESETS:
            preset_config = CHARACTER_CULTURE_PRESETS[self.preset_name]
            for key, value in preset_config.items():
                if hasattr(self, key):
                    object.__setattr__(self, key, value)
        
        # Ensure target enhancement categories
        if not self.target_enhancement_categories:
            default_categories = [
                CultureEnhancementCategory.CHARACTER_NAMES,
                CultureEnhancementCategory.BACKGROUND_HOOKS,
                CultureEnhancementCategory.GAMING_UTILITY
            ]
            object.__setattr__(self, 'target_enhancement_categories', default_categories)

@dataclass(frozen=True)
class CultureGenerationResponse:
    """Enhanced culture generation response with character assessment."""
    # Core response data
    success: bool
    generated_content: str
    request_id: str
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    processing_time_ms: int = 0
    token_usage: Optional[Dict[str, int]] = None
    confidence_score: Optional[float] = None
    
    # Character generation assessment
    character_generation_score: Optional[float] = None
    character_support_score: float = 0.5
    gaming_usability_score: float = 0.5
    creative_inspiration_score: float = 0.5
    
    # Generation status and categorization
    generation_status: CultureGenerationStatus = CultureGenerationStatus.CHARACTER_READY
    identified_enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    
    # Constructive enhancement system
    enhancement_suggestions: List[str] = field(default_factory=list)
    creative_opportunities: List[str] = field(default_factory=list)
    prioritized_enhancements: List[Tuple[str, CultureEnhancementPriority]] = field(default_factory=list)
    
    # Character-focused recommendations
    character_generation_recommendations: List[str] = field(default_factory=list)
    gaming_optimization_tips: List[str] = field(default_factory=list)
    
    # Scoring breakdown
    enum_scoring_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Constructive validation
    validation_warnings: List[str] = field(default_factory=list)
    validation_suggestions: List[str] = field(default_factory=list)
    
    # Creative validation approach compliance
    creative_validation_compliant: bool = True
    character_ready_assessment: bool = True
    
    def __post_init__(self):
        """Ensure all lists are initialized and assess character readiness."""
        # Initialize empty lists
        for field_name in ['validation_warnings', 'enhancement_suggestions', 
                          'creative_opportunities', 'character_generation_recommendations']:
            if getattr(self, field_name) is None:
                object.__setattr__(self, field_name, [])
        
        # Auto-assess character readiness
        if self.character_generation_score and self.character_generation_score >= 0.3:
            object.__setattr__(self, 'character_ready_assessment', True)
        elif self.character_support_score >= 0.3:
            object.__setattr__(self, 'character_ready_assessment', True)

@dataclass(frozen=True)
class CultureEnhancementRequest:
    """Request to enhance existing culture data."""
    # Core enhancement data
    base_culture_data: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Enhancement categories and priorities
    enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    enhancement_priority: CultureEnhancementPriority = CultureEnhancementPriority.CHARACTER_IMPORTANT
    
    # Enhancement parameters
    enhancement_focus: List[str] = field(default_factory=list)
    authenticity_constraints: CultureAuthenticityLevel = CultureAuthenticityLevel.GAMING
    
    # Character generation enhancement preferences
    character_focused_enhancement: bool = True
    gaming_utility_enhancement: bool = True
    creative_freedom_preservation: bool = True
    
    # Target scores
    target_character_support_score: float = 0.8
    target_gaming_usability_score: float = 0.8
    target_creative_inspiration_score: float = 0.7
    
    # Enhancement options
    preserve_existing_elements: bool = True
    allow_creative_expansion: bool = True
    constructive_enhancement_only: bool = True
    
    def __post_init__(self):
        """Ensure enhancement categories are set."""
        if not self.enhancement_categories:
            default_categories = [
                CultureEnhancementCategory.CHARACTER_NAMES,
                CultureEnhancementCategory.BACKGROUND_HOOKS,
                CultureEnhancementCategory.GAMING_UTILITY
            ]
            object.__setattr__(self, 'enhancement_categories', default_categories)

@dataclass(frozen=True)
class CultureValidationRequest:
    """Request for creative validation with constructive approach."""
    # Core validation data
    culture_data: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Validation categories and severity
    validation_categories: List[CultureValidationCategory] = field(default_factory=list)
    severity_threshold: CultureValidationSeverity = CultureValidationSeverity.SUGGESTION
    
    # Legacy support
    validation_criteria: List[str] = field(default_factory=list)
    
    # Creative validation approach settings
    constructive_suggestions_only: bool = True
    character_generation_focus: bool = True
    gaming_utility_priority: bool = True
    creative_freedom_preservation: bool = True
    
    # Character readiness assessment
    assess_character_readiness: bool = True
    target_character_support_score: float = 0.5
    
    def __post_init__(self):
        """Set default validation categories."""
        if not self.validation_categories:
            default_categories = [
                CultureValidationCategory.CHARACTER_SUPPORT,
                CultureValidationCategory.GAMING_UTILITY,
                CultureValidationCategory.CREATIVE_INSPIRATION
            ]
            object.__setattr__(self, 'validation_categories', default_categories)

@dataclass(frozen=True)
class CreativeCultureAnalysisRequest:
    """Request for creative culture analysis and recommendations."""
    # Core analysis data
    text_input: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Analysis parameters
    analysis_focus: List[str] = field(default_factory=list)
    detect_cultural_references: bool = True
    suggest_character_applications: bool = True
    recommend_gaming_adaptations: bool = True
    
    # Character generation analysis
    character_concept_extraction: bool = True
    background_hook_suggestions: bool = True
    gaming_utility_assessment: bool = True
    
    # Creative enhancement preferences
    creative_expansion_suggestions: bool = True
    authenticity_level_recommendations: bool = True
    complexity_level_suggestions: bool = True
    
    def __post_init__(self):
        """Set default analysis focus."""
        if not self.analysis_focus:
            default_focus = [
                'cultural_references', 'character_concepts', 'gaming_applications',
                'creative_opportunities', 'authenticity_assessment'
            ]
            object.__setattr__(self, 'analysis_focus', default_focus)

# ============================================================================
# PROVIDER CAPABILITIES
# ============================================================================

class CultureLLMCapability(Enum):
    """Enhanced capabilities for culture LLM providers."""
    # Core generation capabilities
    BASIC_GENERATION = "basic_generation"
    ENHANCED_GENERATION = "enhanced_generation"
    CREATIVE_GENERATION = "creative_generation"
    
    # Character-focused capabilities
    CHARACTER_FOCUSED_GENERATION = "character_focused_generation"
    CHARACTER_BACKGROUND_HOOKS = "character_background_hooks"
    CHARACTER_NAME_GENERATION = "character_name_generation"
    
    # Gaming utility capabilities
    GAMING_OPTIMIZATION = "gaming_optimization"
    PRONUNCIATION_EASE = "pronunciation_ease"
    GAMING_TABLE_INTEGRATION = "gaming_table_integration"
    
    # Analysis and validation capabilities
    CULTURE_ANALYSIS = "culture_analysis"
    AUTHENTICITY_VALIDATION = "authenticity_validation"
    CREATIVE_VALIDATION = "creative_validation"
    
    # Enhancement capabilities
    CULTURE_ENHANCEMENT = "culture_enhancement"
    TARGETED_ENHANCEMENT = "targeted_enhancement"
    CREATIVE_EXPANSION = "creative_expansion"
    
    # Linguistic and structural capabilities
    LINGUISTIC_PATTERNS = "linguistic_patterns"
    NAMING_STRUCTURE_GENERATION = "naming_structure_generation"
    GENDER_SYSTEM_DESIGN = "gender_system_design"
    
    # Research and authenticity capabilities
    HISTORICAL_RESEARCH = "historical_research"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    AUTHENTICITY_ASSESSMENT = "authenticity_assessment"
    
    # Processing capabilities
    BATCH_PROCESSING = "batch_processing"
    STREAMING_GENERATION = "streaming_generation"
    PRESET_BASED_GENERATION = "preset_based_generation"
    
    # Creative approach capabilities
    CONSTRUCTIVE_SUGGESTIONS = "constructive_suggestions"
    CREATIVE_FREEDOM_SUPPORT = "creative_freedom_support"
    CHARACTER_READINESS_ASSESSMENT = "character_readiness_assessment"

# ============================================================================
# ABSTRACT PROVIDER INTERFACES
# ============================================================================

class CultureLLMProvider(ABC):
    """
    Abstract interface for culture generation LLM providers.
    
    Defines the contract for character-focused creative culture generation
    with gaming utility optimization and creative validation approach.
    """
    
    # Required Properties
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this LLM provider."""
        pass
    
    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Get the version of this LLM provider."""
        pass
    
    @property
    @abstractmethod
    def supported_capabilities(self) -> List[CultureLLMCapability]:
        """Get list of capabilities supported by this provider."""
        pass
    
    @property
    @abstractmethod
    def max_tokens_per_request(self) -> int:
        """Get maximum tokens per request for this provider."""
        pass
    
    @property
    @abstractmethod
    def supports_creative_validation_approach(self) -> bool:
        """Whether provider supports CREATIVE_VALIDATION_APPROACH."""
        pass
    
    @property
    @abstractmethod
    def character_generation_optimized(self) -> bool:
        """Whether provider is optimized for character generation."""
        pass
    
    # Core Generation Methods
    @abstractmethod
    async def generate_culture_content(
        self, 
        request: CultureGenerationRequest
    ) -> CultureGenerationResponse:
        """
        Generate culture content from enhanced request.
        
        Args:
            request: Culture generation request with enum integration
            
        Returns:
            Culture generation response with character assessment
        """
        pass
    
    @abstractmethod
    async def enhance_culture_data(
        self, 
        request: CultureEnhancementRequest
    ) -> CultureGenerationResponse:
        """
        Enhance existing culture data using enhancement categories.
        
        Args:
            request: Culture enhancement request with category targeting
            
        Returns:
            Enhanced culture data response
        """
        pass
    
    @abstractmethod
    async def validate_culture_creatively(
        self, 
        request: CultureValidationRequest
    ) -> Dict[str, Any]:
        """
        Validate culture with CREATIVE_VALIDATION_APPROACH.
        
        Args:
            request: Culture validation request
            
        Returns:
            Creative validation results with constructive suggestions
        """
        pass
    
    @abstractmethod
    async def analyze_cultural_elements(
        self, 
        request: CreativeCultureAnalysisRequest
    ) -> Dict[str, Any]:
        """
        Analyze text for cultural elements with character generation focus.
        
        Args:
            request: Cultural analysis request
            
        Returns:
            Analysis results with character generation recommendations
        """
        pass
    
    # Preset and Advanced Generation Methods
    @abstractmethod
    async def generate_culture_from_preset(
        self,
        preset_name: str,
        cultural_reference: str,
        session_id: Optional[str] = None
    ) -> CultureGenerationResponse:
        """Generate culture using CHARACTER_CULTURE_PRESETS."""
        pass
    
    @abstractmethod
    async def assess_character_generation_readiness(
        self,
        culture_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess culture's readiness for character generation."""
        pass
    
    @abstractmethod
    async def suggest_culture_enhancements(
        self,
        culture_data: Dict[str, Any],
        target_categories: List[CultureEnhancementCategory],
        priority_threshold: CultureEnhancementPriority = CultureEnhancementPriority.CHARACTER_IMPORTANT,
        session_id: Optional[str] = None
    ) -> List[Tuple[str, CultureEnhancementPriority]]:
        """Suggest specific culture enhancements using enum categories."""
        pass
    
    # Utility Methods
    def supports_capability(self, capability: CultureLLMCapability) -> bool:
        """Check if provider supports a specific capability."""
        return capability in self.supported_capabilities
    
    def supports_character_generation(self) -> bool:
        """Check if provider supports character-focused generation."""
        character_capabilities = [
            CultureLLMCapability.CHARACTER_FOCUSED_GENERATION,
            CultureLLMCapability.CHARACTER_BACKGROUND_HOOKS,
            CultureLLMCapability.CHARACTER_NAME_GENERATION
        ]
        return any(self.supports_capability(cap) for cap in character_capabilities)
    
    def supports_gaming_optimization(self) -> bool:
        """Check if provider supports gaming utility optimization."""
        gaming_capabilities = [
            CultureLLMCapability.GAMING_OPTIMIZATION,
            CultureLLMCapability.PRONUNCIATION_EASE,
            CultureLLMCapability.GAMING_TABLE_INTEGRATION
        ]
        return any(self.supports_capability(cap) for cap in gaming_capabilities)
    
    def supports_creative_approach(self) -> bool:
        """Check if provider supports CREATIVE_VALIDATION_APPROACH."""
        creative_capabilities = [
            CultureLLMCapability.CREATIVE_VALIDATION,
            CultureLLMCapability.CONSTRUCTIVE_SUGGESTIONS,
            CultureLLMCapability.CREATIVE_FREEDOM_SUPPORT
        ]
        return any(self.supports_capability(cap) for cap in creative_capabilities)
    
    @abstractmethod
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider status and health."""
        pass

class StreamingCultureLLMProvider(CultureLLMProvider):
    """Streaming interface for real-time culture generation."""
    
    @abstractmethod
    async def generate_culture_content_stream(
        self, 
        request: CultureGenerationRequest
    ) -> AsyncGenerator[CultureGenerationResponse, None]:
        """Generate culture content with streaming updates."""
        pass
    
    @abstractmethod
    async def enhance_culture_data_stream(
        self,
        request: CultureEnhancementRequest
    ) -> AsyncGenerator[CultureGenerationResponse, None]:
        """Stream culture enhancement with real-time updates."""
        pass

class BatchCultureLLMProvider(CultureLLMProvider):
    """Batch processing interface for multiple culture generation."""
    
    @abstractmethod
    async def generate_multiple_cultures(
        self, 
        requests: List[CultureGenerationRequest]
    ) -> List[CultureGenerationResponse]:
        """Generate multiple cultures in a single batch request."""
        pass
    
    @abstractmethod
    async def generate_cultures_from_presets(
        self,
        preset_requests: List[Tuple[str, str]],
        session_id: Optional[str] = None
    ) -> List[CultureGenerationResponse]:
        """Generate multiple cultures using different presets."""
        pass
    
    @abstractmethod
    async def enhance_multiple_cultures(
        self,
        enhancement_requests: List[CultureEnhancementRequest]
    ) -> List[CultureGenerationResponse]:
        """Enhance multiple cultures in a single batch."""
        pass

class PresetCultureLLMProvider(CultureLLMProvider):
    """Specialized interface for preset-based culture generation."""
    
    @abstractmethod
    async def list_available_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available culture generation presets."""
        pass
    
    @abstractmethod
    async def recommend_preset_for_concept(
        self,
        character_concept: str,
        gaming_focus: bool = True,
        creative_priority: bool = False
    ) -> Dict[str, Any]:
        """Recommend optimal preset for a character concept."""
        pass
    
    @abstractmethod
    async def customize_preset(
        self,
        base_preset_name: str,
        customizations: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create customized preset based on existing preset."""
        pass

class CultureLLMProviderFactory(ABC):
    """Abstract factory for creating culture LLM providers."""
    
    @abstractmethod
    def create_provider(
        self, 
        provider_type: str,
        configuration: Dict[str, Any]
    ) -> CultureLLMProvider:
        """Create a culture LLM provider instance."""
        pass
    
    @abstractmethod
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        pass
    
    @abstractmethod
    def get_provider_capabilities(self, provider_type: str) -> List[CultureLLMCapability]:
        """Get capabilities for a specific provider type."""
        pass
    
    @abstractmethod
    def get_character_optimized_providers(self) -> List[str]:
        """Get providers optimized for character generation."""
        pass
    
    @abstractmethod
    def get_creative_approach_providers(self) -> List[str]:
        """Get providers supporting CREATIVE_VALIDATION_APPROACH."""
        pass

# ============================================================================
# PROVIDER REGISTRY SYSTEM
# ============================================================================

# Global provider registry
_culture_provider_registry: Dict[str, CultureLLMProvider] = {}
_default_provider: Optional[CultureLLMProvider] = None

def register_culture_provider(name: str, provider: CultureLLMProvider) -> None:
    """Register a culture provider in the global registry."""
    if not name or not name.strip():
        raise ValueError("Provider name cannot be empty")
    if not provider:
        raise ValueError("Provider cannot be None")
    if not isinstance(provider, CultureLLMProvider):
        raise TypeError("Provider must implement CultureLLMProvider interface")
    
    global _culture_provider_registry
    _culture_provider_registry[name.strip()] = provider

def get_default_culture_provider() -> Optional[CultureLLMProvider]:
    """Get the default culture provider."""
    global _default_provider
    return _default_provider

def set_default_culture_provider(provider: CultureLLMProvider) -> None:
    """Set the default culture provider."""
    if not isinstance(provider, CultureLLMProvider):
        raise TypeError("Provider must implement CultureLLMProvider interface")
    global _default_provider
    _default_provider = provider

def get_registered_providers() -> Dict[str, CultureLLMProvider]:
    """Get all registered providers."""
    return _culture_provider_registry.copy()

def get_provider_by_name(name: str) -> Optional[CultureLLMProvider]:
    """Get a specific provider by name."""
    return _culture_provider_registry.get(name)

def list_provider_names() -> List[str]:
    """Get list of all registered provider names."""
    return list(_culture_provider_registry.keys())

def clear_provider_registry() -> None:
    """Clear all registered providers."""
    global _culture_provider_registry, _default_provider
    _culture_provider_registry.clear()
    _default_provider = None

def get_provider_registry_status() -> Dict[str, Any]:
    """Get status of provider registry."""
    return {
        'registered_count': len(_culture_provider_registry),
        'registered_names': list(_culture_provider_registry.keys()),
        'has_default_provider': _default_provider is not None,
        'default_provider_name': _default_provider.provider_name if _default_provider else None
    }

# ============================================================================
# UTILITY FUNCTIONS (Pure Functions)
# ============================================================================

def create_character_focused_culture_request(
    cultural_reference: str,
    preset_name: Optional[str] = None,
    gaming_optimized: bool = True,
    creative_freedom: bool = True
) -> CultureGenerationRequest:
    """Create a character-focused culture generation request."""
    # Determine optimal configuration
    if gaming_optimized:
        authenticity_level = CultureAuthenticityLevel.GAMING
        complexity_level = CultureComplexityLevel.GAMING_READY
        naming_structure = CultureNamingStructure.GAMING_FRIENDLY
    else:
        authenticity_level = CultureAuthenticityLevel.CREATIVE
        complexity_level = CultureComplexityLevel.MODERATE
        naming_structure = CultureNamingStructure.CHARACTER_FLEXIBLE
    
    if creative_freedom:
        creativity_level = CultureCreativityLevel.CREATIVE_FREEDOM
        source_type = CultureSourceType.CREATIVE_ORIGINAL
    else:
        creativity_level = CultureCreativityLevel.BALANCED_CREATIVE
        source_type = CultureSourceType.CHARACTER_ARCHETYPAL
    
    return CultureGenerationRequest(
        cultural_reference=cultural_reference,
        preset_name=preset_name,
        generation_type=CultureGenerationType.CHARACTER_FOCUSED,
        authenticity_level=authenticity_level,
        creativity_level=creativity_level,
        source_type=source_type,
        complexity_level=complexity_level,
        naming_structure=naming_structure,
        gender_system=CultureGenderSystem.CHARACTER_INCLUSIVE,
        temporal_period=CultureTemporalPeriod.CHARACTER_TIMELESS,
        character_focus=True,
        gaming_optimization=gaming_optimized,
        include_character_hooks=True,
        include_background_elements=True,
        prefer_pronunciation_ease=gaming_optimized,
        target_enhancement_categories=[
            CultureEnhancementCategory.CHARACTER_NAMES,
            CultureEnhancementCategory.BACKGROUND_HOOKS,
            CultureEnhancementCategory.GAMING_UTILITY
        ],
        enable_creative_freedom=creative_freedom,
        constructive_suggestions_only=True,
        character_generation_priority=True
    )

def create_quick_character_culture_request(
    cultural_reference: str,
    session_id: Optional[str] = None
) -> CultureGenerationRequest:
    """Create a quick character culture request using optimal presets."""
    return create_character_focused_culture_request(
        cultural_reference=cultural_reference,
        preset_name="quick_character_creation",
        gaming_optimized=True,
        creative_freedom=False
    )

def create_creative_character_culture_request(
    cultural_reference: str,
    session_id: Optional[str] = None
) -> CultureGenerationRequest:
    """Create a creative character culture request for unique concepts."""
    return create_character_focused_culture_request(
        cultural_reference=cultural_reference,
        preset_name="creative_character_backgrounds",
        gaming_optimized=False,
        creative_freedom=True
    )

def create_targeted_enhancement_request(
    base_culture_data: Dict[str, Any],
    enhancement_categories: List[CultureEnhancementCategory],
    priority: CultureEnhancementPriority = CultureEnhancementPriority.CHARACTER_IMPORTANT,
    character_focused: bool = True
) -> CultureEnhancementRequest:
    """Create a targeted culture enhancement request."""
    return CultureEnhancementRequest(
        base_culture_data=base_culture_data,
        enhancement_categories=enhancement_categories,
        enhancement_priority=priority,
        authenticity_constraints=CultureAuthenticityLevel.GAMING if character_focused else CultureAuthenticityLevel.CREATIVE,
        character_focused_enhancement=character_focused,
        gaming_utility_enhancement=character_focused,
        creative_freedom_preservation=True,
        target_character_support_score=0.8 if character_focused else 0.6,
        target_gaming_usability_score=0.8 if character_focused else 0.5,
        target_creative_inspiration_score=0.7,
        constructive_enhancement_only=True
    )

def create_creative_validation_request(
    culture_data: Dict[str, Any],
    character_readiness_focus: bool = True,
    gaming_utility_focus: bool = True
) -> CultureValidationRequest:
    """Create a creative validation request following CREATIVE_VALIDATION_APPROACH."""
    validation_categories = []
    
    if character_readiness_focus:
        validation_categories.extend([
            CultureValidationCategory.CHARACTER_SUPPORT,
            CultureValidationCategory.CHARACTER_READINESS
        ])
    
    if gaming_utility_focus:
        validation_categories.extend([
            CultureValidationCategory.GAMING_UTILITY,
            CultureValidationCategory.PRONUNCIATION_EASE
        ])
    
    validation_categories.append(CultureValidationCategory.CREATIVE_INSPIRATION)
    
    return CultureValidationRequest(
        culture_data=culture_data,
        validation_categories=validation_categories,
        severity_threshold=CultureValidationSeverity.SUGGESTION,
        constructive_suggestions_only=True,
        character_generation_focus=character_readiness_focus,
        gaming_utility_priority=gaming_utility_focus,
        creative_freedom_preservation=True,
        assess_character_readiness=True,
        target_character_support_score=0.5
    )

def validate_enhanced_generation_request(request: CultureGenerationRequest) -> List[str]:
    """Validate an enhanced culture generation request with constructive suggestions."""
    suggestions = []
    
    # Basic validation (constructive suggestions)
    if not request.cultural_reference or not request.cultural_reference.strip():
        suggestions.append("Consider providing a more detailed cultural reference for richer generation")
    elif len(request.cultural_reference) < 5:
        suggestions.append("A longer cultural reference description may yield more detailed results")
    elif len(request.cultural_reference) > 2000:
        suggestions.append("Consider condensing cultural reference for more focused generation")
    
    # Character focus suggestions
    if request.character_focus and not request.include_character_hooks:
        suggestions.append("Consider enabling character hooks for character-focused generation")
    
    if request.gaming_optimization and not request.prefer_pronunciation_ease:
        suggestions.append("Consider enabling pronunciation ease for gaming optimization")
    
    # Preset validation
    if request.preset_name and request.preset_name not in CHARACTER_CULTURE_PRESETS:
        suggestions.append(f"Preset '{request.preset_name}' not found - will use default configuration")
    
    # Creative approach validation
    if not request.enable_creative_freedom:
        suggestions.append("Consider enabling creative freedom for more unique results")
    
    return suggestions

def create_simple_culture_prompt(
    template: str,
    cultural_reference: str,
    **kwargs
) -> CultureGenerationPrompt:
    """Create a simple culture generation prompt."""
    variables = {'cultural_reference': cultural_reference, **kwargs}
    return CultureGenerationPrompt(
        template=template,
        variables=variables,
        prompt_type="simple_culture_generation"
    )

def create_character_focused_prompt(
    cultural_reference: str,
    character_focus: str = "general",
    gaming_optimized: bool = True
) -> CultureGenerationPrompt:
    """Create a character-focused culture generation prompt."""
    template = """
    Generate a character-focused culture based on: {cultural_reference}
    
    Character Focus: {character_focus}
    Gaming Optimized: {gaming_optimized}
    
    Please include:
    - Character naming conventions that are easy to pronounce
    - Background hooks for character development
    - Cultural traits that enhance roleplay
    - Gaming table integration notes
    
    Focus on creativity and character generation utility.
    """
    
    return CultureGenerationPrompt(
        template=template.strip(),
        variables={
            'cultural_reference': cultural_reference,
            'character_focus': character_focus,
            'gaming_optimized': 'Yes' if gaming_optimized else 'No'
        },
        prompt_type="character_focused_generation"
    )

def assess_provider_character_generation_readiness(
    provider: CultureLLMProvider
) -> Dict[str, Any]:
    """Assess provider's readiness for character-focused culture generation."""
    # Essential character generation capabilities
    essential_capabilities = [
        CultureLLMCapability.CHARACTER_FOCUSED_GENERATION,
        CultureLLMCapability.CHARACTER_NAME_GENERATION,
        CultureLLMCapability.CHARACTER_BACKGROUND_HOOKS
    ]
    
    # Gaming optimization capabilities
    gaming_capabilities = [
        CultureLLMCapability.GAMING_OPTIMIZATION,
        CultureLLMCapability.PRONUNCIATION_EASE,
        CultureLLMCapability.GAMING_TABLE_INTEGRATION
    ]
    
    # Creative approach capabilities
    creative_capabilities = [
        CultureLLMCapability.CREATIVE_VALIDATION,
        CultureLLMCapability.CONSTRUCTIVE_SUGGESTIONS,
        CultureLLMCapability.CREATIVE_FREEDOM_SUPPORT
    ]
    
    # Calculate scores
    character_score = sum(1 for cap in essential_capabilities if provider.supports_capability(cap)) / len(essential_capabilities)
    gaming_score = sum(1 for cap in gaming_capabilities if provider.supports_capability(cap)) / len(gaming_capabilities)
    creative_score = sum(1 for cap in creative_capabilities if provider.supports_capability(cap)) / len(creative_capabilities)
    
    # Identify missing capabilities
    missing_capabilities = []
    for cap in essential_capabilities + gaming_capabilities + creative_capabilities:
        if not provider.supports_capability(cap):
            missing_capabilities.append(cap.value)
    
    # Generate enhancement suggestions
    enhancement_suggestions = []
    if character_score < 0.8:
        enhancement_suggestions.append("Consider implementing character-focused generation capabilities")
    if gaming_score < 0.6:
        enhancement_suggestions.append("Consider adding gaming optimization features")
    if creative_score < 0.6:
        enhancement_suggestions.append("Consider implementing creative validation approach")
    
    return {
        'is_character_ready': character_score >= 0.6 and creative_score >= 0.3,
        'character_support_score': character_score,
        'gaming_optimization_score': gaming_score,
        'creative_approach_score': creative_score,
        'overall_readiness_score': (character_score * 0.5 + gaming_score * 0.3 + creative_score * 0.2),
        'missing_capabilities': missing_capabilities,
        'enhancement_suggestions': enhancement_suggestions,
        'provider_name': provider.provider_name,
        'creative_validation_approach_compliant': provider.supports_creative_validation_approach
    }

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Core data structures
    "CultureGenerationPrompt",
    "CultureLLMResponse",
    "CultureGenerationRequest",
    "CultureGenerationResponse",
    "CultureEnhancementRequest",
    "CultureValidationRequest",
    "CreativeCultureAnalysisRequest",
    
    # Provider interfaces
    "CultureLLMProvider",
    "StreamingCultureLLMProvider",
    "BatchCultureLLMProvider",
    "PresetCultureLLMProvider",
    "CultureLLMProviderFactory",
    
    # Enums and capabilities
    "CultureLLMCapability",
    
    # Provider registry functions
    "register_culture_provider",
    "get_default_culture_provider",
    "set_default_culture_provider",
    "get_registered_providers",
    "get_provider_by_name",
    "list_provider_names",
    "clear_provider_registry",
    "get_provider_registry_status",
    
    # Utility functions
    "create_character_focused_culture_request",
    "create_quick_character_culture_request",
    "create_creative_character_culture_request",
    "create_targeted_enhancement_request",
    "create_creative_validation_request",
    "validate_enhanced_generation_request",
    "create_simple_culture_prompt",
    "create_character_focused_prompt",
    "assess_provider_character_generation_readiness",
]

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "3.0.0"
__title__ = "Culture LLM Provider Interface Contract"
__description__ = "Clean Architecture interface for AI-powered creative culture generation"
__author__ = "D&D Character Creator Development Team"

# Module capabilities
MODULE_CAPABILITIES = {
    "architecture": "Clean Architecture with Dependency Inversion",
    "philosophy": "CREATIVE_VALIDATION_APPROACH - Enable creativity, don't restrict",
    "focus": "Character generation support with gaming utility optimization",
    "validation_style": "Constructive suggestions over blocking requirements",
    "enum_integration": "Complete culture_types enum system integration",
    "provider_support": "Pluggable AI providers with standard interfaces"
}

# Compliance with CREATIVE_VALIDATION_APPROACH
CREATIVE_VALIDATION_COMPLIANCE = {
    "constructive_suggestions_only": True,
    "character_generation_priority": True,
    "enable_creative_freedom": True,
    "gaming_utility_optimization": True,
    "preset_based_quick_creation": True,
    "enhancement_category_targeting": True,
    "non_blocking_validation": True,
    "creative_opportunity_identification": True,
    "character_readiness_assessment": True,
    "gaming_table_integration": True
}

# Registry initialization
def initialize_provider_registry() -> None:
    """Initialize provider registry with any default providers."""
    pass

# Initialize on module load
initialize_provider_registry()

if __name__ == "__main__":
    print(f"Culture LLM Provider Interface v{__version__}")
    print(f"Philosophy: {MODULE_CAPABILITIES['philosophy']}")
    print(f"Architecture: {MODULE_CAPABILITIES['architecture']}")
    print(f"Exported symbols: {len(__all__)}")
    print("🎨 CREATIVE_VALIDATION_APPROACH: Enable creativity rather than restrict it!")