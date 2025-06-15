"""
Culture LLM Provider Interface Contract.

Defines the abstract interface for AI-powered culture generation providers
following Clean Architecture principles. This interface ensures dependency
inversion where the core business logic doesn't depend on specific LLM
implementations, allowing for pluggable AI providers.

Maintains:
- Pure abstraction with no implementation details
- Infrastructure independence 
- Dependency inversion principle
- Single responsibility for culture generation contracts
- Testability through mock implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Import core types (dependency flows inward)
from ..enums.culture_types import (
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureValidationSeverity
)


@dataclass(frozen=True)
class CultureGenerationRequest:
    """Immutable culture generation request data."""
    cultural_reference: str
    generation_type: CultureGenerationType
    authenticity_level: CultureAuthenticityLevel
    creativity_level: CultureCreativityLevel
    source_type: CultureSourceType
    complexity_level: CultureComplexityLevel
    user_constraints: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass(frozen=True)
class CultureGenerationResponse:
    """Immutable culture generation response data."""
    success: bool
    generated_content: str
    generation_metadata: Dict[str, Any]
    processing_time_ms: int
    token_usage: Optional[Dict[str, int]] = None
    confidence_score: Optional[float] = None
    validation_warnings: List[str] = None
    
    def __post_init__(self):
        # Ensure validation_warnings is never None
        if self.validation_warnings is None:
            object.__setattr__(self, 'validation_warnings', [])


@dataclass(frozen=True)
class CultureEnhancementRequest:
    """Request to enhance existing culture data."""
    base_culture_data: Dict[str, Any]
    enhancement_type: str
    enhancement_focus: List[str]
    authenticity_constraints: CultureAuthenticityLevel
    session_id: Optional[str] = None


@dataclass(frozen=True)
class CultureValidationRequest:
    """Request to validate culture authenticity."""
    culture_data: Dict[str, Any]
    validation_criteria: List[str]
    severity_threshold: CultureValidationSeverity
    session_id: Optional[str] = None


class CultureLLMCapability(Enum):
    """Capabilities that culture LLM providers may support."""
    BASIC_GENERATION = "basic_generation"
    ENHANCED_GENERATION = "enhanced_generation"
    CULTURE_ANALYSIS = "culture_analysis"
    AUTHENTICITY_VALIDATION = "authenticity_validation"
    LINGUISTIC_PATTERNS = "linguistic_patterns"
    HISTORICAL_RESEARCH = "historical_research"
    CULTURAL_ENHANCEMENT = "cultural_enhancement"
    BATCH_PROCESSING = "batch_processing"
    STREAMING_GENERATION = "streaming_generation"


class CultureLLMProvider(ABC):
    """
    Abstract interface for culture generation LLM providers.
    
    This interface defines the contract that all culture generation LLM
    providers must implement, ensuring:
    - Consistent behavior across different AI providers
    - Dependency inversion (core doesn't depend on infrastructure)
    - Testability through mock implementations
    - Infrastructure independence
    
    The interface is designed around Pure Functions and immutable data
    structures to maintain Clean Architecture principles.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this LLM provider."""
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
    
    @abstractmethod
    async def generate_culture_content(
        self, 
        request: CultureGenerationRequest
    ) -> CultureGenerationResponse:
        """
        Generate culture content from request.
        
        Pure function that transforms a culture generation request into
        generated cultural content without side effects.
        
        Args:
            request: Immutable culture generation request
            
        Returns:
            Immutable culture generation response
            
        Raises:
            CultureGenerationError: If generation fails
            ValidationError: If request is invalid
        """
        pass
    
    @abstractmethod
    async def enhance_culture_data(
        self, 
        request: CultureEnhancementRequest
    ) -> CultureGenerationResponse:
        """
        Enhance existing culture data.
        
        Pure function that takes existing culture data and enhances it
        based on the enhancement request parameters.
        
        Args:
            request: Immutable culture enhancement request
            
        Returns:
            Enhanced culture data response
            
        Raises:
            CultureEnhancementError: If enhancement fails
            ValidationError: If request is invalid
        """
        pass
    
    @abstractmethod
    async def validate_culture_authenticity(
        self, 
        request: CultureValidationRequest
    ) -> Dict[str, Any]:
        """
        Validate cultural authenticity and accuracy.
        
        Pure function that analyzes culture data for authenticity,
        historical accuracy, and cultural sensitivity.
        
        Args:
            request: Immutable culture validation request
            
        Returns:
            Dictionary containing validation results:
            - is_authentic: bool
            - authenticity_score: float (0.0-1.0)
            - validation_issues: List[Dict]
            - recommendations: List[str]
            
        Raises:
            CultureValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    async def analyze_cultural_elements(
        self, 
        text_input: str,
        analysis_focus: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze text for cultural elements and references.
        
        Pure function that extracts cultural information from user input
        like "I want to create Maui from Moana" -> Polynesian elements.
        
        Args:
            text_input: User input text to analyze
            analysis_focus: List of aspects to focus on
            
        Returns:
            Dictionary containing analysis results:
            - detected_cultures: List[str]
            - cultural_elements: Dict[str, List[str]]
            - confidence_scores: Dict[str, float]
            - recommendations: List[str]
            
        Raises:
            CultureAnalysisError: If analysis fails
        """
        pass
    
    def supports_capability(self, capability: CultureLLMCapability) -> bool:
        """
        Check if provider supports a specific capability.
        
        Pure function with no side effects.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if capability is supported
        """
        return capability in self.supported_capabilities
    
    @abstractmethod
    async def get_provider_status(self) -> Dict[str, Any]:
        """
        Get current provider status and health.
        
        Returns:
            Dictionary containing:
            - is_available: bool
            - response_time_ms: int
            - rate_limit_remaining: Optional[int]
            - last_error: Optional[str]
            - capabilities_status: Dict[str, bool]
        """
        pass


class StreamingCultureLLMProvider(CultureLLMProvider):
    """
    Extended interface for providers supporting streaming generation.
    
    Allows for real-time culture generation with progress updates,
    useful for complex cultural systems that take time to generate.
    """
    
    @abstractmethod
    async def generate_culture_content_stream(
        self, 
        request: CultureGenerationRequest
    ):
        """
        Generate culture content with streaming updates.
        
        Async generator that yields partial results as they become available.
        
        Args:
            request: Culture generation request
            
        Yields:
            Partial CultureGenerationResponse objects with incremental content
            
        Raises:
            CultureGenerationError: If streaming generation fails
        """
        pass


class BatchCultureLLMProvider(CultureLLMProvider):
    """
    Extended interface for providers supporting batch processing.
    
    Allows for efficient generation of multiple cultures simultaneously,
    useful for generating culture variations or related cultural systems.
    """
    
    @abstractmethod
    async def generate_multiple_cultures(
        self, 
        requests: List[CultureGenerationRequest]
    ) -> List[CultureGenerationResponse]:
        """
        Generate multiple cultures in a single batch request.
        
        Pure function that processes multiple culture generation requests
        efficiently, maintaining independence between generations.
        
        Args:
            requests: List of culture generation requests
            
        Returns:
            List of culture generation responses in same order
            
        Raises:
            BatchCultureGenerationError: If batch generation fails
        """
        pass


class CultureLLMProviderFactory(ABC):
    """
    Abstract factory for creating culture LLM providers.
    
    Follows Clean Architecture by providing an interface for creating
    providers without depending on specific implementations.
    """
    
    @abstractmethod
    def create_provider(
        self, 
        provider_type: str,
        configuration: Dict[str, Any]
    ) -> CultureLLMProvider:
        """
        Create a culture LLM provider instance.
        
        Args:
            provider_type: Type of provider to create
            configuration: Provider-specific configuration
            
        Returns:
            Culture LLM provider instance
            
        Raises:
            ProviderCreationError: If provider creation fails
            UnsupportedProviderError: If provider type not supported
        """
        pass
    
    @abstractmethod
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        pass
    
    @abstractmethod
    def get_provider_capabilities(self, provider_type: str) -> List[CultureLLMCapability]:
        """Get capabilities for a specific provider type."""
        pass


# ============================================================================
# UTILITY FUNCTIONS (Pure Functions - No Side Effects)
# ============================================================================

def create_basic_culture_request(
    cultural_reference: str,
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.MODERATE,
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED
) -> CultureGenerationRequest:
    """
    Create a basic culture generation request with sensible defaults.
    
    Pure function that creates request objects without side effects.
    
    Args:
        cultural_reference: Description of the culture to generate
        authenticity_level: Desired authenticity level
        creativity_level: Desired creativity level
        
    Returns:
        Configured CultureGenerationRequest
        
    Example:
        >>> request = create_basic_culture_request(
        ...     "Ancient Polynesian seafaring culture",
        ...     CultureAuthenticityLevel.HIGH
        ... )
        >>> print(request.cultural_reference)
    """
    return CultureGenerationRequest(
        cultural_reference=cultural_reference,
        generation_type=CultureGenerationType.CUSTOM,
        authenticity_level=authenticity_level,
        creativity_level=creativity_level,
        source_type=CultureSourceType.HISTORICAL,
        complexity_level=CultureComplexityLevel.STANDARD
    )


def create_enhancement_request(
    base_culture_data: Dict[str, Any],
    enhancement_focus: List[str],
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.MODERATE
) -> CultureEnhancementRequest:
    """
    Create a culture enhancement request.
    
    Pure function for creating enhancement requests.
    
    Args:
        base_culture_data: Existing culture data to enhance
        enhancement_focus: Areas to focus enhancement on
        authenticity_level: Authenticity constraints for enhancement
        
    Returns:
        Configured CultureEnhancementRequest
    """
    return CultureEnhancementRequest(
        base_culture_data=base_culture_data,
        enhancement_type="targeted_enhancement",
        enhancement_focus=enhancement_focus,
        authenticity_constraints=authenticity_level
    )


def validate_generation_request(request: CultureGenerationRequest) -> List[str]:
    """
    Validate a culture generation request.
    
    Pure function that validates request data without side effects.
    
    Args:
        request: Culture generation request to validate
        
    Returns:
        List of validation errors (empty if valid)
        
    Example:
        >>> request = create_basic_culture_request("Test culture")
        >>> errors = validate_generation_request(request)
        >>> print(f"Valid: {len(errors) == 0}")
    """
    errors = []
    
    if not request.cultural_reference or not request.cultural_reference.strip():
        errors.append("Cultural reference cannot be empty")
    
    if len(request.cultural_reference) < 3:
        errors.append("Cultural reference must be at least 3 characters")
    
    if len(request.cultural_reference) > 1000:
        errors.append("Cultural reference must be less than 1000 characters")
    
    # Validate enum values are set
    required_enums = [
        request.generation_type,
        request.authenticity_level,
        request.creativity_level,
        request.source_type,
        request.complexity_level
    ]
    
    if any(enum_val is None for enum_val in required_enums):
        errors.append("All enum fields must be set")
    
    return errors


def extract_provider_capabilities(provider: CultureLLMProvider) -> Dict[str, bool]:
    """
    Extract capabilities from a provider instance.
    
    Pure function that analyzes provider capabilities.
    
    Args:
        provider: Culture LLM provider instance
        
    Returns:
        Dictionary mapping capability names to availability
    """
    capabilities = {}
    
    for capability in CultureLLMCapability:
        capabilities[capability.value] = provider.supports_capability(capability)
    
    return capabilities


def compare_provider_capabilities(
    provider_a: CultureLLMProvider,
    provider_b: CultureLLMProvider
) -> Dict[str, Any]:
    """
    Compare capabilities between two providers.
    
    Pure function for capability comparison.
    
    Args:
        provider_a: First provider to compare
        provider_b: Second provider to compare
        
    Returns:
        Dictionary with comparison results
    """
    caps_a = extract_provider_capabilities(provider_a)
    caps_b = extract_provider_capabilities(provider_b)
    
    return {
        'provider_a_name': provider_a.provider_name,
        'provider_b_name': provider_b.provider_name,
        'capabilities_a': caps_a,
        'capabilities_b': caps_b,
        'common_capabilities': [
            cap for cap, supported in caps_a.items() 
            if supported and caps_b.get(cap, False)
        ],
        'unique_to_a': [
            cap for cap, supported in caps_a.items()
            if supported and not caps_b.get(cap, False)
        ],
        'unique_to_b': [
            cap for cap, supported in caps_b.items()
            if supported and not caps_a.get(cap, False)
        ]
    }


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Culture LLM Provider Interface Contract for Clean Architecture"

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/abstractions",
    "dependencies": ["abc", "typing", "enum", "dataclasses", "../enums/culture_types"],
    "dependents": ["domain/services", "infrastructure/llm", "application/use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "none",
    "focuses_on": "Interface contracts for culture generation LLM providers",
    "maintains_principles": [
        "Dependency Inversion",
        "Single Responsibility", 
        "Interface Segregation",
        "Open/Closed"
    ]
}

# Design principles documentation
DESIGN_PRINCIPLES = {
    "interface_segregation": "Separate interfaces for basic, streaming, and batch providers",
    "dependency_inversion": "Core defines interface, infrastructure implements",
    "pure_functions": "All utility functions are pure with no side effects",
    "immutable_data": "All data structures are immutable dataclasses",
    "single_responsibility": "Each interface focuses on one aspect of culture LLM interaction",
    "testability": "All interfaces can be easily mocked for testing"
}

# Usage patterns
USAGE_PATTERNS = {
    "basic_generation": """
        provider = get_culture_provider('openai')
        request = create_basic_culture_request('Ancient Norse culture')
        response = await provider.generate_culture_content(request)
    """,
    "enhanced_generation": """
        enhancement_request = create_enhancement_request(
            existing_culture_data, 
            ['names', 'titles'],
            CultureAuthenticityLevel.HIGH
        )
        response = await provider.enhance_culture_data(enhancement_request)
    """,
    "validation": """
        errors = validate_generation_request(request)
        if not errors:
            response = await provider.generate_culture_content(request)
    """,
    "capability_checking": """
        if provider.supports_capability(CultureLLMCapability.STREAMING_GENERATION):
            async for partial_response in provider.generate_culture_content_stream(request):
                update_progress(partial_response)
    """
}