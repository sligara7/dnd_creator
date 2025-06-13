from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from uuid import uuid4
from ..enums.content_types import ContentType, ContentSource
from ..enums.validation_types import ValidationResult


@dataclass
class ContentCollection:
    """
    Entity representing a thematic suite of generated content.
    
    A ContentCollection groups related generated content (species, classes, equipment, 
    spells, feats) that share common themes and work synergistically together.
    This supports the Creative Content Framework's goal of thematic consistency.
    """
    
    # === IDENTITY ===
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    
    # === THEMATIC ELEMENTS ===
    primary_themes: List[str] = field(default_factory=list)
    secondary_themes: List[str] = field(default_factory=list)
    cultural_elements: List[str] = field(default_factory=list)
    
    # === CONTENT ITEMS ===
    content_items: Dict[ContentType, List['GeneratedContent']] = field(default_factory=dict)
    
    # === GENERATION METADATA ===
    source_concept_id: Optional[str] = None  # CharacterConcept that generated this
    collection_balance_score: Optional[float] = None
    synergy_score: Optional[float] = None  # How well content works together
    validation_notes: List[str] = field(default_factory=list)
    
    # === USAGE TRACKING ===
    usage_count: int = 0
    characters_using: List[str] = field(default_factory=list)  # Character IDs
    last_used: Optional[datetime] = None
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Initialize content_items dictionary with empty lists for all content types."""
        for content_type in ContentType:
            if content_type not in self.content_items:
                self.content_items[content_type] = []
    
    # === CONTENT MANAGEMENT ===
    
    def add_content(self, content: 'GeneratedContent') -> None:
        """Add generated content to the collection."""
        content_type = content.content_type
        if content not in self.content_items[content_type]:
            self.content_items[content_type].append(content)
            self.last_modified = datetime.now()
    
    def remove_content(self, content: 'GeneratedContent') -> bool:
        """Remove content from the collection."""
        content_type = content.content_type
        if content in self.content_items[content_type]:
            self.content_items[content_type].remove(content)
            self.last_modified = datetime.now()
            return True
        return False
    
    def get_content_by_type(self, content_type: ContentType) -> List['GeneratedContent']:
        """Get all content of a specific type."""
        return self.content_items.get(content_type, [])
    
    def get_all_content(self) -> List['GeneratedContent']:
        """Get all content in the collection."""
        all_content = []
        for content_list in self.content_items.values():
            all_content.extend(content_list)
        return all_content
    
    def get_content_count(self) -> Dict[str, int]:
        """Get count of content by type."""
        return {
            content_type.value: len(content_list)
            for content_type, content_list in self.content_items.items()
            if content_list  # Only include types with content
        }
    
    def get_total_content_count(self) -> int:
        """Get total number of content items."""
        return sum(len(content_list) for content_list in self.content_items.values())
    
    def is_empty(self) -> bool:
        """Check if collection has no content."""
        return self.get_total_content_count() == 0
    
    # === THEMATIC ANALYSIS ===
    
    def get_all_themes(self) -> List[str]:
        """Get all themes combined."""
        return self.primary_themes + self.secondary_themes + self.cultural_elements
    
    def calculate_theme_coverage(self, target_themes: List[str]) -> float:
        """Calculate how well collection covers target themes (0.0 to 1.0)."""
        if not target_themes:
            return 1.0
        
        collection_themes = [theme.lower() for theme in self.get_all_themes()]
        matches = sum(
            1 for target in target_themes
            if any(target.lower() in collection_theme for collection_theme in collection_themes)
        )
        return matches / len(target_themes)
    
    def get_thematic_gaps(self, target_themes: List[str]) -> List[str]:
        """Identify themes not covered by collection content."""
        collection_themes = [theme.lower() for theme in self.get_all_themes()]
        gaps = []
        
        for target in target_themes:
            if not any(target.lower() in collection_theme for collection_theme in collection_themes):
                gaps.append(target)
        
        return gaps
    
    # === BALANCE AND VALIDATION ===
    
    def calculate_collection_balance(self) -> float:
        """Calculate overall balance score for the collection."""
        if self.is_empty():
            return 0.5  # Neutral for empty collection
        
        content_scores = []
        for content in self.get_all_content():
            if hasattr(content, 'balance_score') and content.balance_score is not None:
                content_scores.append(content.balance_score)
        
        if not content_scores:
            return 0.5  # Neutral if no scores available
        
        # Average balance score
        avg_balance = sum(content_scores) / len(content_scores)
        
        # Adjust for collection size (larger collections get slight penalty)
        size_factor = min(1.0, 10 / max(1, self.get_total_content_count()))
        
        return avg_balance * size_factor
    
    def calculate_synergy_score(self) -> float:
        """Calculate how well content items work together."""
        content_list = self.get_all_content()
        if len(content_list) < 2:
            return 1.0  # Perfect synergy for single/no items
        
        # Simple synergy based on shared themes
        theme_matches = 0
        total_comparisons = 0
        
        for i, content1 in enumerate(content_list):
            for content2 in content_list[i+1:]:
                total_comparisons += 1
                # Check if content shares themes
                themes1 = getattr(content1, 'themes', [])
                themes2 = getattr(content2, 'themes', [])
                
                shared_themes = set(theme.lower() for theme in themes1) & set(theme.lower() for theme in themes2)
                if shared_themes:
                    theme_matches += len(shared_themes)
        
        if total_comparisons == 0:
            return 1.0
        
        return min(1.0, theme_matches / total_comparisons)
    
    def validate_collection_coherence(self) -> List[ValidationResult]:
        """Validate that collection content works together coherently."""
        results = []
        
        # Check theme consistency
        if not self.primary_themes:
            results.append(ValidationResult(
                validation_type="coherence",
                severity="warning",
                message="Collection has no primary themes",
                is_valid=False
            ))
        
        # Check content diversity
        content_types_present = [ct for ct, items in self.content_items.items() if items]
        if len(content_types_present) == 1:
            results.append(ValidationResult(
                validation_type="coherence", 
                severity="info",
                message="Collection only contains one type of content",
                is_valid=True
            ))
        
        # Check balance consistency
        balance_scores = [
            content.balance_score for content in self.get_all_content()
            if hasattr(content, 'balance_score') and content.balance_score is not None
        ]
        
        if balance_scores:
            balance_range = max(balance_scores) - min(balance_scores)
            if balance_range > 0.4:  # Large balance variation
                results.append(ValidationResult(
                    validation_type="balance",
                    severity="warning", 
                    message="Large balance variation between collection items",
                    is_valid=False
                ))
        
        return results
    
    # === USAGE TRACKING ===
    
    def mark_used_by_character(self, character_id: str) -> None:
        """Mark collection as used by a character."""
        if character_id not in self.characters_using:
            self.characters_using.append(character_id)
        
        self.usage_count += 1
        self.last_used = datetime.now()
        self.last_modified = datetime.now()
    
    def unmark_used_by_character(self, character_id: str) -> None:
        """Remove character from users list."""
        if character_id in self.characters_using:
            self.characters_using.remove(character_id)
            self.last_modified = datetime.now()
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics for this collection."""
        return {
            "total_usage_count": self.usage_count,
            "unique_characters": len(self.characters_using),
            "characters_using": self.characters_using.copy(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat(),
            "days_since_creation": (datetime.now() - self.created_at).days,
            "days_since_last_use": (datetime.now() - self.last_used).days if self.last_used else None,
            "average_usage_per_day": self.usage_count / max(1, (datetime.now() - self.created_at).days),
            "is_popular": self.usage_count > 5,  # Arbitrary threshold for popularity
            "content_breakdown": self.get_content_count()
        }
    
    # === EXPORT/IMPORT ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "primary_themes": self.primary_themes,
            "secondary_themes": self.secondary_themes,
            "cultural_elements": self.cultural_elements,
            "content_items": {
                content_type.value: [content.to_dict() for content in content_list]
                for content_type, content_list in self.content_items.items()
                if content_list  # Only include non-empty lists
            },
            "source_concept_id": self.source_concept_id,
            "collection_balance_score": self.collection_balance_score,
            "synergy_score": self.synergy_score,
            "validation_notes": self.validation_notes,
            "usage_count": self.usage_count,
            "characters_using": self.characters_using,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], content_registry: Optional[Dict[str, 'GeneratedContent']] = None) -> 'ContentCollection':
        """Create collection from dictionary data."""
        collection = cls()
        collection.id = data.get("id", str(uuid4()))
        collection.name = data.get("name", "")
        collection.description = data.get("description", "")
        collection.primary_themes = data.get("primary_themes", [])
        collection.secondary_themes = data.get("secondary_themes", [])
        collection.cultural_elements = data.get("cultural_elements", [])
        
        # Reconstruct content items
        if content_registry:
            for content_type_str, content_list_data in data.get("content_items", {}).items():
                content_type = ContentType(content_type_str)
                for content_data in content_list_data:
                    content_id = content_data.get("id")
                    if content_id in content_registry:
                        collection.add_content(content_registry[content_id])
        
        collection.source_concept_id = data.get("source_concept_id")
        collection.collection_balance_score = data.get("collection_balance_score")
        collection.synergy_score = data.get("synergy_score")  
        collection.validation_notes = data.get("validation_notes", [])
        collection.usage_count = data.get("usage_count", 0)
        collection.characters_using = data.get("characters_using", [])
        
        if "last_used" in data and data["last_used"]:
            collection.last_used = datetime.fromisoformat(data["last_used"])
        if "created_at" in data:
            collection.created_at = datetime.fromisoformat(data["created_at"])
        if "last_modified" in data:
            collection.last_modified = datetime.fromisoformat(data["last_modified"])
        
        collection.created_by = data.get("created_by", "")
        collection.version = data.get("version", "1.0")
        
        return collection
    
    def __str__(self) -> str:
        """String representation of collection."""
        content_count = self.get_total_content_count()
        themes_str = ", ".join(self.primary_themes[:2])
        return f"Content Collection: {self.name} ({content_count} items, {themes_str})"
    
    def __repr__(self) -> str:
        """Developer representation of collection."""
        return f"ContentCollection(id='{self.id[:8]}...', name='{self.name}', items={self.get_total_content_count()})"