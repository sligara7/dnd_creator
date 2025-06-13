"""
Consolidated Character DTOs

All data transfer objects for character management operations including creation,
modification, validation, state management, and analysis. This consolidation
supports the unified character management philosophy while maintaining clean
separation of concerns.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from ...core.entities.character import Character
from ...core.entities.character_concept import CharacterConcept
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.character_state import CharacterState
from ...core.value_objects.thematic_elements import ThematicElements

# === Character Creation DTOs ===

@dataclass
class CharacterCreationRequest:
    """Request for creating a character from background concept."""
    character_concept: Optional[CharacterConcept] = None
    background_description: Optional[str] = None  # For LLM concept enhancement
    preferences: Dict[str, Any] = None
    creation_options: Dict[str, Any] = None
    target_level: int = 1
    apply_custom_content: bool = False

@dataclass 
class CharacterCreationResponse:
    """Response from character creation."""
    success: bool
    character: Optional[Character] = None
    character_concept: Optional[CharacterConcept] = None
    validation_result: Optional[ValidationResult] = None
    creation_metadata: Dict[str, Any] = None
    errors: List[str] = None

# === Multiclass Character DTOs ===

@dataclass
class MulticlassRequest:
    """Request for creating multiclass character."""
    character_concept: CharacterConcept
    class_combination: List[str]
    target_level: int = 20
    optimization_goals: List[str] = None  # ["damage", "versatility", "survivability"]
    save_character: bool = True

@dataclass
class MulticlassResponse:
    """Response from multiclass character creation."""
    success: bool
    character: Optional[Character] = None
    level_progression: Dict[str, Any] = None
    feature_interactions: Dict[str, Any] = None
    spellcasting_progression: Optional[Dict[str, Any]] = None
    build_recommendations: List[Dict[str, Any]] = None
    saved_character_id: Optional[str] = None
    multiclass_score: float = 0.0
    errors: List[str] = None

# === Character Modification DTOs ===

@dataclass
class CharacterModificationRequest:
    """Request for modifying existing character."""
    character_id: str
    modification_type: str  # "level_up", "respec", "equipment_change", "feat_change", "custom_content_integration"
    modification_data: Dict[str, Any]
    validate_changes: bool = True

@dataclass
class CharacterModificationResponse:
    """Response from character modification."""
    success: bool
    character: Optional[Character] = None
    modifications_applied: List[Dict[str, Any]] = None
    validation_result: Optional[ValidationResult] = None
    errors: List[str] = None

# === Character Validation DTOs ===

@dataclass
class CharacterValidationRequest:
    """Request for character validation."""
    character_id: str
    validation_types: List[str]  # ["comprehensive", "creation_step", "optimization", "multiclass", "thematic_consistency"]
    step_name: Optional[str] = None  # For creation_step validation
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

# === Character State Management DTOs ===

@dataclass
class CharacterStateRequest:
    """Request for character state management."""
    character_id: str
    operation: str  # "take_damage", "heal", "rest", "use_resource", "cast_spell"
    operation_data: Dict[str, Any]

@dataclass
class CharacterStateResponse:
    """Response from character state management."""
    success: bool
    character: Optional[Character] = None
    state_changes: List[Dict[str, Any]] = None
    current_state: Optional[CharacterState] = None
    errors: List[str] = None

# === Character Analysis DTOs ===

@dataclass
class CharacterAnalysisRequest:
    """Request for character analysis."""
    character_id: str
    analysis_types: List[str]  # ["comprehensive", "combat", "skills", "optimization", "thematic_consistency"]

@dataclass
class CharacterAnalysisResponse:
    """Response from character analysis."""
    success: bool
    character_id: Optional[str] = None
    character_name: Optional[str] = None
    analysis_results: Dict[str, Any] = None
    analysis_summary: Optional[str] = None
    errors: List[str] = None

# === Shared DTOs for Complex Operations ===

@dataclass
class CharacterProgressionPlan:
    """Plan for character level progression."""
    character_id: str
    current_level: int
    target_level: int
    progression_steps: List[Dict[str, Any]]
    optimization_recommendations: List[Dict[str, Any]] = None
    thematic_consistency_score: float = 0.0

@dataclass
class CharacterConceptAnalysis:
    """Analysis of character concept for creation guidance."""
    concept: CharacterConcept
    thematic_elements: ThematicElements
    suggested_species: List[str] = None
    suggested_classes: List[str] = None
    suggested_backgrounds: List[str] = None
    customization_opportunities: List[Dict[str, Any]] = None
    narrative_hooks: List[str] = None

@dataclass
class CharacterOptimizationSuggestion:
    """Suggestion for character optimization."""
    suggestion_type: str  # "feat", "spell", "equipment", "multiclass", "asi"
    description: str
    impact_analysis: Dict[str, Any]
    implementation_steps: List[str]
    priority: str  # "high", "medium", "low"
    prerequisites: List[str] = None
    trade_offs: List[str] = None

@dataclass
class CharacterFeatureInteraction:
    """Analysis of character feature interactions."""
    interacting_features: List[str]
    interaction_type: str  # "synergy", "conflict", "redundancy"
    impact_description: str
    optimization_suggestions: List[str] = None
    severity: str = "medium"  # "high", "medium", "low"

# === Utility DTOs ===

@dataclass
class CharacterComparisonRequest:
    """Request for comparing two characters."""
    character_1_id: str
    character_2_id: str
    comparison_aspects: List[str]  # ["stats", "abilities", "effectiveness", "thematic"]

@dataclass
class CharacterComparisonResponse:
    """Response from character comparison."""
    success: bool
    character_1: Optional[Character] = None
    character_2: Optional[Character] = None
    comparison_results: Dict[str, Any] = None
    summary: Optional[str] = None
    errors: List[str] = None

@dataclass
class CharacterExportRequest:
    """Request for exporting character data."""
    character_id: str
    export_format: str  # "json", "pdf", "roll20", "dndbeyond"
    include_metadata: bool = True
    include_creation_history: bool = False

@dataclass
class CharacterExportResponse:
    """Response from character export."""
    success: bool
    character_id: Optional[str] = None
    export_format: Optional[str] = None
    exported_data: Any = None  # Format depends on export_format
    export_metadata: Dict[str, Any] = None
    errors: List[str] = None

# === Base Response Pattern ===

@dataclass
class BaseCharacterResponse:
    """Base response pattern for all character operations."""
    success: bool
    operation_type: str
    timestamp: str
    character_id: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None