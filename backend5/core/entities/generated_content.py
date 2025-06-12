from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4
from ..enums.content_types import ContentType, ContentSource
from ..enums.validation_types import ValidationResult
from ..value_objects.content_metadata import ContentMetadata


@dataclass
class GeneratedContent:
    """
    Entity representing any generated D&D content in the Creative Content Framework.
    
    This entity encapsulates content created by the framework, including its data,
    metadata, validation results, and relationships to other content.
    """
    
    # === IDENTITY ===
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    content_type: ContentType = ContentType.SPECIES
    content_source: ContentSource = ContentSource.GENERATED
    
    # === CONTENT DATA ===
    description: str = ""
    mechanical_data: Dict[str, Any] = field(default_factory=dict)
    flavor_data: Dict[str, Any] = field(default_factory=dict)
    
    # === GENERATION METADATA ===
    generation_metadata: ContentMetadata = field(default_factory=lambda: ContentMetadata(
        created_at=datetime.now(),
        created_by="system",
        generation_method="llm"
    ))
    
    # === VALIDATION ===
    validation_results: List[ValidationResult] = field(default_factory=list)
    is_validated: bool = False
    validation_timestamp: Optional[datetime] = None
    
    # === RELATIONSHIPS ===
    parent_concept_id: Optional[str] = None  # CharacterConcept that generated this
    related_content_ids: List[str] = field(default_factory=list)  # Other content in the same theme
    dependencies: List[str] = field(default_factory=list)  # Content this depends on
    
    # === USAGE TRACKING ===
    usage_count: int = 0
    last_used: Optional[datetime] = None
    characters_using: List[str] = field(default_factory=list)  # Character IDs using this content
    
    # === VERSIONING ===
    version: str = "1.0"
    revision_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # === BALANCE AND POWER ===
    balance_score: Optional[float] = None  # 0.0 = underpowered, 0.5 = balanced, 1.0 = overpowered
    power_level: str = "standard"  # "low", "standard", "high"
    balance_notes: List[str] = field(default_factory=list)
    
    # === VALIDATION METHODS ===
    
    def is_valid(self) -> bool:
        """Check if content has passed all validations."""
        if not self.validation_results:
            return False
        
        # Check if any validation failed critically
        for result in self.validation_results:
            if result.severity == "critical" and not result.passed:
                return False
        
        return self.is_validated
    
    def get_validation_issues(self) -> List[ValidationResult]:
        """Get all validation issues (warnings and errors)."""
        return [
            result for result in self.validation_results 
            if not result.passed
        ]
    
    def get_critical_issues(self) -> List[ValidationResult]:
        """Get critical validation issues that block usage."""
        return [
            result for result in self.validation_results 
            if result.severity == "critical" and not result.passed
        ]
    
    def add_validation_result(self, result: ValidationResult) -> None:
        """Add a validation result."""
        self.validation_results.append(result)
        
        # Update validation status
        if not self.get_critical_issues():
            self.is_validated = True
            self.validation_timestamp = datetime.now()
    
    def get_balance_assessment(self) -> Dict[str, Any]:
        """Get balance assessment information."""
        return {
            "balance_score": self.balance_score,
            "power_level": self.power_level,
            "is_balanced": 0.3 <= (self.balance_score or 0.5) <= 0.7,
            "balance_notes": self.balance_notes,
            "needs_review": self.balance_score is not None and (
                self.balance_score < 0.3 or self.balance_score > 0.7
            )
        }
    
    # === USAGE TRACKING ===
    
    def mark_as_used(self, character_id: str) -> None:
        """Mark content as used by a character."""
        if character_id not in self.characters_using:
            self.characters_using.append(character_id)
        
        self.usage_count += 1
        self.last_used = datetime.now()
    
    def remove_usage(self, character_id: str) -> None:
        """Remove usage tracking for a character."""
        if character_id in self.characters_using:
            self.characters_using.remove(character_id)
    
    def is_used_by(self, character_id: str) -> bool:
        """Check if content is used by a specific character."""
        return character_id in self.characters_using
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "characters_using_count": len(self.characters_using),
            "is_popular": self.usage_count > 5
        }
    
    # === RELATIONSHIPS ===
    
    def add_related_content(self, content_id: str) -> None:
        """Add related content ID."""
        if content_id not in self.related_content_ids:
            self.related_content_ids.append(content_id)
    
    def remove_related_content(self, content_id: str) -> None:
        """Remove related content ID."""
        if content_id in self.related_content_ids:
            self.related_content_ids.remove(content_id)
    
    def add_dependency(self, content_id: str) -> None:
        """Add dependency on other content."""
        if content_id not in self.dependencies:
            self.dependencies.append(content_id)
    
    def has_dependency(self, content_id: str) -> bool:
        """Check if content depends on other content."""
        return content_id in self.dependencies
    
    def get_all_relationships(self) -> Dict[str, List[str]]:
        """Get all content relationships."""
        return {
            "related": self.related_content_ids,
            "dependencies": self.dependencies,
            "parent_concept": [self.parent_concept_id] if self.parent_concept_id else []
        }
    
    # === VERSIONING ===
    
    def create_revision(self, changes: Dict[str, Any], reason: str = "") -> None:
        """Create a new revision of the content."""
        revision = {
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "reason": reason,
            "previous_balance_score": self.balance_score
        }
        
        self.revision_history.append(revision)
        
        # Update version number
        version_parts = self.version.split(".")
        minor_version = int(version_parts[-1]) + 1
        self.version = f"{'.'.join(version_parts[:-1])}.{minor_version}"
        
        # Reset validation status for new version
        self.is_validated = False
        self.validation_timestamp = None
        self.validation_results = []
    
    def get_revision_history(self) -> List[Dict[str, Any]]:
        """Get complete revision history."""
        return self.revision_history.copy()
    
    def rollback_to_version(self, target_version: str) -> bool:
        """Rollback to a previous version (if data exists)."""
        # Implementation would restore from revision history
        # This is a placeholder for the concept
        for revision in self.revision_history:
            if revision["version"] == target_version:
                # Restore data from revision
                self.version = target_version
                return True
        return False
    
    # === CONTENT SPECIFIC METHODS ===
    
    def get_mechanical_summary(self) -> Dict[str, Any]:
        """Get summary of mechanical effects."""
        summary = {}
        
        if self.content_type == ContentType.SPECIES:
            summary = {
                "ability_increases": self.mechanical_data.get("ability_score_increases", {}),
                "traits": len(self.mechanical_data.get("traits", [])),
                "resistances": self.mechanical_data.get("damage_resistances", []),
                "speed": self.mechanical_data.get("base_speed", 30)
            }
        elif self.content_type == ContentType.CHARACTER_CLASS:
            summary = {
                "hit_die": self.mechanical_data.get("hit_die", 8),
                "saving_throws": self.mechanical_data.get("saving_throw_proficiencies", []),
                "spellcasting": self.mechanical_data.get("spellcasting_info") is not None,
                "features_per_level": len(self.mechanical_data.get("features", {}))
            }
        elif self.content_type == ContentType.EQUIPMENT:
            summary = {
                "rarity": self.mechanical_data.get("rarity", "common"),
                "requires_attunement": self.mechanical_data.get("requires_attunement", False),
                "damage": self.mechanical_data.get("damage", {}),
                "properties": self.mechanical_data.get("properties", [])
            }
        
        return summary
    
    def get_theme_tags(self) -> List[str]:
        """Get thematic tags for this content."""
        tags = []
        
        # Extract from flavor data
        if "themes" in self.flavor_data:
            tags.extend(self.flavor_data["themes"])
        
        # Extract from generation metadata
        if hasattr(self.generation_metadata, "source_concept"):
            concept = self.generation_metadata.source_concept
            if concept and hasattr(concept, "all_themes"):
                tags.extend(concept.all_themes)
        
        return list(set(tags))  # Remove duplicates
    
    # === UTILITY METHODS ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert content to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "content_type": self.content_type.value,
            "content_source": self.content_source.value,
            "description": self.description,
            "mechanical_data": self.mechanical_data,
            "flavor_data": self.flavor_data,
            "generation_metadata": self.generation_metadata.to_dict(),
            "validation_results": [result.to_dict() for result in self.validation_results],
            "is_validated": self.is_validated,
            "validation_timestamp": self.validation_timestamp.isoformat() if self.validation_timestamp else None,
            "parent_concept_id": self.parent_concept_id,
            "related_content_ids": self.related_content_ids,
            "dependencies": self.dependencies,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "characters_using": self.characters_using,
            "version": self.version,
            "balance_score": self.balance_score,
            "power_level": self.power_level,
            "balance_notes": self.balance_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedContent':
        """Create content from dictionary data."""
        content = cls()
        content.id = data.get("id", str(uuid4()))
        content.name = data.get("name", "")
        content.content_type = ContentType(data.get("content_type", "species"))
        content.content_source = ContentSource(data.get("content_source", "generated"))
        content.description = data.get("description", "")
        content.mechanical_data = data.get("mechanical_data", {})
        content.flavor_data = data.get("flavor_data", {})
        
        # Restore metadata
        if "generation_metadata" in data:
            content.generation_metadata = ContentMetadata.from_dict(data["generation_metadata"])
        
        # Restore validation results
        if "validation_results" in data:
            content.validation_results = [
                ValidationResult.from_dict(result) for result in data["validation_results"]
            ]
        
        content.is_validated = data.get("is_validated", False)
        if "validation_timestamp" in data and data["validation_timestamp"]:
            content.validation_timestamp = datetime.fromisoformat(data["validation_timestamp"])
        
        # Restore relationships
        content.parent_concept_id = data.get("parent_concept_id")
        content.related_content_ids = data.get("related_content_ids", [])
        content.dependencies = data.get("dependencies", [])
        
        # Restore usage tracking
        content.usage_count = data.get("usage_count", 0)
        if "last_used" in data and data["last_used"]:
            content.last_used = datetime.fromisoformat(data["last_used"])
        content.characters_using = data.get("characters_using", [])
        
        # Restore versioning
        content.version = data.get("version", "1.0")
        content.revision_history = data.get("revision_history", [])
        
        # Restore balance data
        content.balance_score = data.get("balance_score")
        content.power_level = data.get("power_level", "standard")
        content.balance_notes = data.get("balance_notes", [])
        
        return content
    
    def __str__(self) -> str:
        """String representation of content."""
        validation_status = "✓" if self.is_valid() else "⚠"
        usage_note = f" (used {self.usage_count}x)" if self.usage_count > 0 else ""
        return f"{validation_status} {self.name} ({self.content_type.value}){usage_note}"
    
    def __repr__(self) -> str:
        """Developer representation of content."""
        return f"GeneratedContent(id='{self.id}', name='{self.name}', type='{self.content_type.value}', valid={self.is_valid()})"