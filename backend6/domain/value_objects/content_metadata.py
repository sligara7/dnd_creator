from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..enums.generation_methods import GenerationMethod, LLMProvider
from ..enums.content_types import ContentSource


@dataclass(frozen=True)
class ContentMetadata:
    """
    Value object containing metadata about generated content creation.
    
    This supports the Creative Content Framework's traceability and attribution
    requirements for all generated content.
    """
    
    # === CREATION INFO ===
    created_at: datetime
    created_by: str  # User identifier or system name
    content_id: str
    
    # === GENERATION METHOD ===
    generation_method: GenerationMethod
    llm_provider: Optional[LLMProvider] = None
    llm_model: Optional[str] = None
    
    # === SOURCE INFORMATION ===
    source_concept_id: Optional[str] = None  # CharacterConcept that drove generation
    content_source: ContentSource = ContentSource.GENERATED
    
    # === GENERATION PARAMETERS ===
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    template_used: Optional[str] = None
    iteration_count: int = 1
    
    # === VALIDATION INFO ===
    validation_passed: bool = False
    validation_timestamp: Optional[datetime] = None
    validation_notes: List[str] = field(default_factory=list)
    
    # === VERSIONING ===
    version: str = "1.0"
    parent_version: Optional[str] = None  # If this is a revision
    
    # === ATTRIBUTION ===
    attribution_notes: List[str] = field(default_factory=list)
    inspiration_sources: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate metadata on creation."""
        if self.llm_provider and not self.llm_model:
            raise ValueError("LLM model must be specified when LLM provider is set")
        
        if self.generation_method == GenerationMethod.LLM and not self.llm_provider:
            raise ValueError("LLM provider must be specified for LLM generation method")
    
    @property
    def is_llm_generated(self) -> bool:
        """Check if content was generated using LLM."""
        return self.generation_method in [GenerationMethod.LLM, GenerationMethod.HYBRID]
    
    @property
    def is_template_based(self) -> bool:
        """Check if content used templates."""
        return self.generation_method in [GenerationMethod.TEMPLATE, GenerationMethod.HYBRID]
    
    @property
    def generation_age_days(self) -> int:
        """Get age of generated content in days."""
        return (datetime.now() - self.created_at).days
    
    @property
    def is_validated(self) -> bool:
        """Check if content has passed validation."""
        return self.validation_passed and self.validation_timestamp is not None
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of generation process."""
        return {
            "method": self.generation_method.value,
            "llm_used": f"{self.llm_provider.value}:{self.llm_model}" if self.llm_provider else None,
            "template_used": self.template_used,
            "iterations": self.iteration_count,
            "source_concept": self.source_concept_id,
            "validated": self.is_validated,
            "age_days": self.generation_age_days
        }
    
    def add_validation_note(self, note: str) -> 'ContentMetadata':
        """Add a validation note (returns new instance since frozen)."""
        new_notes = list(self.validation_notes) + [note]
        return self.__class__(
            **{**self.__dict__, 'validation_notes': new_notes}
        )
    
    def mark_validated(self, timestamp: Optional[datetime] = None) -> 'ContentMetadata':
        """Mark content as validated (returns new instance since frozen)."""
        if timestamp is None:
            timestamp = datetime.now()
        
        return self.__class__(
            **{**self.__dict__, 
               'validation_passed': True, 
               'validation_timestamp': timestamp}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "content_id": self.content_id,
            "generation_method": self.generation_method.value,
            "llm_provider": self.llm_provider.value if self.llm_provider else None,
            "llm_model": self.llm_model,
            "source_concept_id": self.source_concept_id,
            "content_source": self.content_source.value,
            "generation_parameters": self.generation_parameters,
            "template_used": self.template_used,
            "iteration_count": self.iteration_count,
            "validation_passed": self.validation_passed,
            "validation_timestamp": self.validation_timestamp.isoformat() if self.validation_timestamp else None,
            "validation_notes": self.validation_notes,
            "version": self.version,
            "parent_version": self.parent_version,
            "attribution_notes": self.attribution_notes,
            "inspiration_sources": self.inspiration_sources
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentMetadata':
        """Create from dictionary representation."""
        # Convert string dates back to datetime objects
        created_at = datetime.fromisoformat(data["created_at"])
        validation_timestamp = None
        if data.get("validation_timestamp"):
            validation_timestamp = datetime.fromisoformat(data["validation_timestamp"])
        
        # Convert enum strings back to enums
        generation_method = GenerationMethod(data["generation_method"])
        llm_provider = LLMProvider(data["llm_provider"]) if data.get("llm_provider") else None
        content_source = ContentSource(data["content_source"])
        
        return cls(
            created_at=created_at,
            created_by=data["created_by"],
            content_id=data["content_id"],
            generation_method=generation_method,
            llm_provider=llm_provider,
            llm_model=data.get("llm_model"),
            source_concept_id=data.get("source_concept_id"),
            content_source=content_source,
            generation_parameters=data.get("generation_parameters", {}),
            template_used=data.get("template_used"),
            iteration_count=data.get("iteration_count", 1),
            validation_passed=data.get("validation_passed", False),
            validation_timestamp=validation_timestamp,
            validation_notes=data.get("validation_notes", []),
            version=data.get("version", "1.0"),
            parent_version=data.get("parent_version"),
            attribution_notes=data.get("attribution_notes", []),
            inspiration_sources=data.get("inspiration_sources", [])
        )
    
"""
Supporting Data Structures for D&D Creative Content Framework.
"""
from .content_metadata import ContentMetadata
from .generation_constraints import GenerationConstraints
from .thematic_elements import ThematicElements
from .validation_result import ValidationResult
from .balance_metrics import BalanceMetrics
from datetime import datetime

def create_default_metadata(created_by: str = "system") -> ContentMetadata:
    """Create default metadata for content generation."""
    return ContentMetadata(
        created_at=datetime.now(),
        created_by=created_by,
        generation_method="template",
        version="1.0"
    )

def merge_thematic_elements(elements: List[ThematicElements]) -> ThematicElements:
    """Merge multiple thematic element sets."""
    if not elements:
        raise ValueError("Cannot merge empty elements list")
    
    merged_themes = set()
    merged_keywords = set()
    merged_cultural = set()
    
    for element in elements:
        merged_themes.update(element.primary_themes)
        merged_keywords.update(element.theme_keywords)
        merged_cultural.update(element.cultural_elements)
    
    return ThematicElements(
        primary_themes=list(merged_themes),
        theme_keywords=list(merged_keywords),
        cultural_elements=list(merged_cultural),
        power_level=elements[0].power_level  # Use first element's power level
    )

def calculate_combined_balance(metrics: List[BalanceMetrics]) -> BalanceMetrics:
    """Calculate combined balance metrics."""
    if not metrics:
        raise ValueError("Cannot calculate balance for empty metrics list")
    
    total_power = sum(m.power_level_score for m in metrics)
    total_utility = sum(m.utility_score for m in metrics)
    total_versatility = sum(m.versatility_score for m in metrics)
    
    count = len(metrics)
    
    return BalanceMetrics(
        power_level_score=total_power / count,
        utility_score=total_utility / count,
        versatility_score=total_versatility / count,
        overall_balance_score=(total_power + total_utility + total_versatility) / (count * 3)
    )

__all__ = [
    'ContentMetadata', 'GenerationConstraints', 'ThematicElements',
    'ValidationResult', 'BalanceMetrics', 'create_default_metadata',
    'merge_thematic_elements', 'calculate_combined_balance'
]