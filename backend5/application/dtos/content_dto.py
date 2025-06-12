"""
Consolidated Content DTOs

All data transfer objects for content generation, validation, and integration.
This consolidates DTOs for species, classes, equipment, spells, feats, and
system integration while maintaining the background-driven creative philosophy.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from ...core.entities.character import Character
from ...core.entities.character_concept import CharacterConcept
from ...core.entities.generated_content import GeneratedContent
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.thematic_elements import ThematicElements
from ...core.value_objects.generation_constraints import GenerationConstraints

# === Content Generation DTOs ===

@dataclass
class ContentGenerationRequest:
    """Unified request for generating any type of D&D content."""
    character_concept: CharacterConcept
    content_type: str  # "species", "class", "equipment", "spell", "feat"
    constraints: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any] = None
    register_content: bool = False

@dataclass
class ContentGenerationResponse:
    """Unified response from content generation."""
    success: bool
    content_type: Optional[str] = None
    generated_content: Optional[Dict[str, Any]] = None
    thematic_analysis: Optional[ThematicElements] = None
    validation_result: Optional[ValidationResult] = None
    constraints_applied: Optional[GenerationConstraints] = None
    registration_result: Optional[Dict[str, Any]] = None
    generation_metadata: Dict[str, Any] = None
    regeneration_context: Optional[Dict[str, Any]] = None  # For feedback-based regeneration
    errors: List[str] = None

@dataclass
class ThematicSuiteRequest:
    """Request for generating a complete thematic content suite."""
    character_concept: CharacterConcept
    requested_content_types: List[str]  # ["species", "class", "equipment", "spells", "feats"]
    content_priorities: Dict[str, int] = None  # Priority weighting for generation order
    register_content: bool = False

@dataclass
class ThematicSuiteResponse:
    """Response from thematic suite generation."""
    success: bool
    character_concept: Optional[CharacterConcept] = None
    thematic_analysis: Optional[ThematicElements] = None
    generation_roadmap: Dict[str, Any] = None
    content_suite: Dict[str, Any] = None  # content_type -> generated_content
    suite_validation: Dict[str, Any] = None
    registration_results: Dict[str, Any] = None
    suite_metadata: Dict[str, Any] = None
    errors: List[str] = None

# === Content Validation DTOs ===

@dataclass
class ContentValidationRequest:
    """Request for validating generated content."""
    content: Dict[str, Any]
    content_type: str
    character_concept: Optional[CharacterConcept] = None
    context: Dict[str, Any] = None
    include_llm_analysis: bool = True

@dataclass
class ContentValidationResponse:
    """Response from content validation."""
    success: bool
    content_type: Optional[str] = None
    rule_validation: Optional[ValidationResult] = None
    balance_validation: Optional[ValidationResult] = None
    llm_validation: Optional[Dict[str, Any]] = None
    thematic_validation: Optional[ValidationResult] = None
    integration_validation: Optional[ValidationResult] = None
    validation_report: Optional[str] = None
    overall_score: float = 0.0
    is_valid: bool = False
    errors: List[str] = None

@dataclass
class CharacterValidationRequest:
    """Request for character validation."""
    character_id: str
    validation_types: List[str]  # ["comprehensive", "creation_step", "optimization", "balance", "thematic_consistency"]
    step_name: Optional[str] = None
    context: Dict[str, Any] = None
    include_statistics: bool = False

@dataclass
class CharacterValidationResponse:
    """Response from character validation."""
    success: bool
    character_id: Optional[str] = None
    character_name: Optional[str] = None
    validation_results: Dict[str, ValidationResult] = None
    character_statistics: Optional[Dict[str, Any]] = None
    improvement_suggestions: List[Dict[str, Any]] = None
    validation_summary: Optional[str] = None
    overall_valid: bool = False
    errors: List[str] = None

# === Multiclass DTOs ===

@dataclass
class MulticlassRequest:
    """Request for multiclass character creation or validation."""
    character_concept: CharacterConcept
    class_combination: List[str]
    target_level: int = 20
    optimization_goals: List[str] = None
    save_character: bool = True

@dataclass
class MulticlassResponse:
    """Response from multiclass operations."""
    success: bool
    character: Optional[Character] = None
    level_progression: Dict[str, Any] = None
    feature_interactions: Dict[str, Any] = None
    spellcasting_progression: Optional[Dict[str, Any]] = None
    build_recommendations: List[Dict[str, Any]] = None
    saved_character_id: Optional[str] = None
    multiclass_score: float = 0.0
    errors: List[str] = None

@dataclass
class MulticlassValidationRequest:
    """Request for multiclass build validation."""
    character_id: str
    target_classes: Optional[List[str]] = None
    optimization_goals: List[str] = None

@dataclass
class MulticlassValidationResponse:
    """Response from multiclass validation."""
    success: bool
    character_id: Optional[str] = None
    prerequisite_validation: Optional[ValidationResult] = None
    feature_interaction_validation: Optional[ValidationResult] = None
    spellcasting_validation: Optional[ValidationResult] = None
    optimization_analysis: Dict[str, Any] = None
    multiclass_recommendations: List[Dict[str, Any]] = None
    is_valid_multiclass: bool = False
    errors: List[str] = None

# === Integration DTOs ===

@dataclass
class IntegrationRequest:
    """Request for integrating content with D&D systems."""
    content: Dict[str, Any]
    content_type: str
    target_systems: List[str] = None  # Systems to test compatibility with
    target_character_id: Optional[str] = None
    test_multiclass_compatibility: bool = False
    register_on_success: bool = False

@dataclass
class IntegrationResponse:
    """Response from content integration."""
    success: bool
    content_type: Optional[str] = None
    rule_validation: Optional[ValidationResult] = None
    system_compatibility: Dict[str, Any] = None
    multiclass_integration: Optional[Dict[str, Any]] = None
    character_integration: Optional[Dict[str, Any]] = None
    integration_recommendations: List[Dict[str, Any]] = None
    registration_result: Optional[Dict[str, Any]] = None
    integration_score: float = 0.0
    errors: List[str] = None

@dataclass
class SystemValidationRequest:
    """Request for system-wide validation."""
    validation_scopes: List[str]  # ["content_character_integration", "multiclass_integration", "custom_content_integration", "rule_system_compliance"]
    content: Optional[Dict[str, Any]] = None
    character_id: Optional[str] = None
    custom_content: List[Dict[str, Any]] = None
    system_components: List[str] = None
    integration_context: Dict[str, Any] = None

@dataclass
class SystemValidationResponse:
    """Response from system validation."""
    success: bool
    validation_results: Dict[str, ValidationResult] = None
    integration_report: Optional[str] = None
    overall_integration_valid: bool = False
    errors: List[str] = None

# === Content Analysis DTOs ===

@dataclass
class ContentAnalysisRequest:
    """Request for analyzing generated content."""
    content: Dict[str, Any]
    content_type: str
    analysis_types: List[str]  # ["balance", "thematic", "mechanical", "optimization"]
    comparison_baseline: Optional[str] = None  # "official", "community", "custom"

@dataclass
class ContentAnalysisResponse:
    """Response from content analysis."""
    success: bool
    content_type: Optional[str] = None
    analysis_results: Dict[str, Any] = None
    balance_metrics: Dict[str, float] = None
    thematic_analysis: Dict[str, Any] = None
    optimization_suggestions: List[Dict[str, Any]] = None
    comparison_results: Optional[Dict[str, Any]] = None
    errors: List[str] = None

# === Content Management DTOs ===

@dataclass
class ContentRegistrationRequest:
    """Request for registering content in the system."""
    content: Dict[str, Any]
    content_type: str
    metadata: Dict[str, Any] = None
    make_available_for_generation: bool = True

@dataclass
class ContentRegistrationResponse:
    """Response from content registration."""
    success: bool
    content_id: Optional[str] = None
    registration_metadata: Dict[str, Any] = None
    validation_performed: bool = False
    validation_result: Optional[ValidationResult] = None
    errors: List[str] = None

@dataclass
class ContentSearchRequest:
    """Request for searching registered content."""
    content_types: List[str] = None
    themes: List[str] = None
    compatibility_requirements: Dict[str, Any] = None
    balance_constraints: Dict[str, Any] = None
    limit: int = 10

@dataclass
class ContentSearchResponse:
    """Response from content search."""
    success: bool
    matching_content: List[Dict[str, Any]] = None
    search_metadata: Dict[str, Any] = None
    total_matches: int = 0
    errors: List[str] = None

# === Shared DTOs for Complex Operations ===

@dataclass
class GenerationConstraintsData:
    """Data structure for generation constraints."""
    power_level: str = "standard"  # "low", "standard", "high"
    complexity: str = "medium"  # "simple", "medium", "complex"
    thematic_requirements: List[str] = None
    mechanical_requirements: List[str] = None
    balance_targets: Dict[str, float] = None
    exclusions: List[str] = None

@dataclass
class ThematicAnalysisData:
    """Data structure for thematic analysis results."""
    primary_themes: List[str]
    secondary_themes: List[str] = None
    narrative_elements: List[str] = None
    aesthetic_elements: List[str] = None
    cultural_elements: List[str] = None
    mechanical_implications: Dict[str, Any] = None
    integration_opportunities: List[str] = None

@dataclass
class BalanceMetrics:
    """Data structure for balance analysis metrics."""
    power_score: float
    complexity_score: float
    versatility_score: float
    niche_score: float
    interaction_score: float
    baseline_comparison: Dict[str, float] = None
    outlier_analysis: Dict[str, Any] = None

@dataclass
class ContentOptimizationSuggestion:
    """Suggestion for content optimization."""
    optimization_type: str  # "balance", "thematic", "mechanical", "integration"
    description: str
    impact_analysis: Dict[str, Any]
    implementation_difficulty: str  # "easy", "medium", "hard"
    priority: str  # "high", "medium", "low"
    prerequisites: List[str] = None
    potential_conflicts: List[str] = None

# === Base Response Pattern ===

@dataclass
class BaseContentResponse:
    """Base response pattern for all content operations."""
    success: bool
    operation_type: str
    timestamp: str
    content_type: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None