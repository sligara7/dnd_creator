"""
Core domain entities for the D&D Creative Content Framework.

This module contains the fundamental business objects that represent the core concepts
of the creative content generation system, including characters, generated content,
character concepts, and content collections.

These entities encapsulate both data and behavior, following Domain-Driven Design
principles while supporting the framework's background-driven content generation.
"""

from typing import List, Dict, Any, Optional
from .character import Character
from .generated_content import GeneratedContent
from .character_concept import CharacterConcept
from .content_collection import ContentCollection

__all__ = [
    # Core Entities
    'Character',
    'GeneratedContent', 
    'CharacterConcept',
    'ContentCollection',
    
    # Entity Operations
    'create_character_from_concept',
    'validate_character_integrity',
    'merge_content_collections',
    'get_entity_metadata',
    
    # Registry Functions
    'get_entity_class',
    'list_available_entities',
    'validate_entity_relationships',
    'get_entity_dependencies',
]

# Entity Type Registry for dynamic loading
ENTITY_REGISTRY = {
    'character': Character,
    'generated_content': GeneratedContent,
    'character_concept': CharacterConcept,
    'content_collection': ContentCollection,
}


def create_character_from_concept(concept: CharacterConcept) -> Character:
    """
    Create a character from a background concept.
    
    Args:
        concept: The character concept to base the character on
        
    Returns:
        Newly created Character entity
        
    Raises:
        ValueError: If concept is invalid or incomplete
    """
    if not concept.concept_name:
        raise ValueError("Character concept must have a name")
    
    if not concept.background_story:
        raise ValueError("Character concept must have a background story")
    
    # Create character with concept data
    character = Character(
        name=concept.concept_name,
        level=1,  # New characters start at level 1
        species=None,  # Will be populated by generation services
        character_classes=[],  # Will be populated by generation services
        ability_scores={},  # Will be calculated by generation services
        background=concept.background_story,
        personality_traits=getattr(concept, 'personality_traits', []),
        ideals=getattr(concept, 'ideals', []),
        bonds=getattr(concept, 'bonds', []),
        flaws=getattr(concept, 'flaws', [])
    )
    
    # Copy thematic elements if available
    if hasattr(concept, 'thematic_elements'):
        character.thematic_elements = concept.thematic_elements
    
    return character


def validate_character_integrity(character: Character) -> List[str]:
    """
    Validate that character data is internally consistent.
    
    Args:
        character: The character to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Basic required fields
    if not character.name:
        issues.append("Character must have a name")
    
    if character.level < 1 or character.level > 20:
        issues.append("Character level must be between 1 and 20")
    
    if character.level > 1 and not character.species:
        issues.append("Character above level 1 must have a species")
    
    if character.level > 1 and not character.character_classes:
        issues.append("Character above level 1 must have at least one class")
    
    # Ability score validation
    if character.ability_scores:
        required_abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for ability in required_abilities:
            if ability not in character.ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = character.ability_scores[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score} (must be 1-30)")
    
    # Class level consistency
    if character.character_classes:
        total_class_levels = sum(cls.level for cls in character.character_classes)
        if total_class_levels != character.level:
            issues.append(f"Character level ({character.level}) doesn't match sum of class levels ({total_class_levels})")
    
    return issues


def merge_content_collections(collections: List[ContentCollection]) -> ContentCollection:
    """
    Merge multiple content collections into one.
    
    Args:
        collections: List of content collections to merge
        
    Returns:
        Merged content collection
        
    Raises:
        ValueError: If collections list is empty
    """
    if not collections:
        raise ValueError("Cannot merge empty collection list")
    
    # Use first collection as base
    base_collection = collections[0]
    
    merged = ContentCollection(
        collection_id=f"merged_{len(collections)}_collections",
        name="Merged Collection",
        description="Combined content collection",
        content_items={},
        primary_themes=[],
        creation_metadata=base_collection.creation_metadata
    )
    
    # Merge all collections
    for collection in collections:
        # Merge content items
        for content_type, items in collection.content_items.items():
            if content_type not in merged.content_items:
                merged.content_items[content_type] = []
            merged.content_items[content_type].extend(items)
        
        # Merge themes
        if hasattr(collection, 'primary_themes'):
            merged.primary_themes.extend(collection.primary_themes)
    
    # Remove duplicate themes
    merged.primary_themes = list(set(merged.primary_themes))
    
    # Update metadata
    merged.creation_metadata.merged_from = [c.collection_id for c in collections]
    merged.creation_metadata.total_source_collections = len(collections)
    
    return merged


def get_entity_metadata() -> Dict[str, Any]:
    """
    Get metadata about available entities.
    
    Returns:
        Dictionary with entity system metadata
    """
    return {
        "entities": list(ENTITY_REGISTRY.keys()),
        "total_count": len(ENTITY_REGISTRY),
        "supports_generation": True,
        "supports_validation": True,
        "supports_serialization": True,
        "primary_entities": ["character", "generated_content"],
        "supporting_entities": ["character_concept", "content_collection"]
    }


def get_entity_class(entity_type: str) -> Optional[type]:
    """
    Get entity class by type name.
    
    Args:
        entity_type: String identifier for the entity type
        
    Returns:
        Entity class or None if not found
    """
    return ENTITY_REGISTRY.get(entity_type.lower())


def list_available_entities() -> List[str]:
    """
    Get list of all available entity types.
    
    Returns:
        List of entity type names
    """
    return list(ENTITY_REGISTRY.keys())


def validate_entity_relationships() -> Dict[str, List[str]]:
    """
    Validate relationships between entities for consistency.
    
    Returns:
        Dictionary mapping entity types to relationship issues
    """
    issues = {}
    
    for entity_type, entity_class in ENTITY_REGISTRY.items():
        entity_issues = []
        
        # Check for required methods
        required_methods = ['to_dict', 'from_dict', 'validate']
        for method in required_methods:
            if not hasattr(entity_class, method):
                entity_issues.append(f"Missing required method: {method}")
        
        # Check for proper initialization
        try:
            # This is a basic check - in practice you'd use proper test data
            if hasattr(entity_class, '__init__'):
                pass  # Could check __init__ signature
        except Exception as e:
            entity_issues.append(f"Initialization issue: {e}")
        
        if entity_issues:
            issues[entity_type] = entity_issues
    
    return issues


def get_entity_dependencies() -> Dict[str, List[str]]:
    """
    Get dependency relationships between entities.
    
    Returns:
        Dictionary mapping entity types to their dependencies
    """
    dependencies = {
        'character': ['character_concept'],  # Character can be created from concept
        'generated_content': ['character', 'content_collection'],  # Content relates to characters and collections
        'character_concept': [],  # No dependencies
        'content_collection': ['generated_content'],  # Collections contain generated content
    }
    
    return dependencies


def create_entity_from_dict(entity_type: str, data: Dict[str, Any]) -> Any:
    """
    Create an entity instance from dictionary data.
    
    Args:
        entity_type: Type of entity to create
        data: Dictionary with entity data
        
    Returns:
        Entity instance
        
    Raises:
        ValueError: If entity type is unknown or data is invalid
    """
    entity_class = get_entity_class(entity_type)
    if not entity_class:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    if hasattr(entity_class, 'from_dict'):
        return entity_class.from_dict(data)
    else:
        # Fallback to direct initialization
        try:
            return entity_class(**data)
        except TypeError as e:
            raise ValueError(f"Invalid data for {entity_type}: {e}")


def batch_validate_entities(entities: List[Any]) -> Dict[str, Any]:
    """
    Validate a batch of entities and return summary.
    
    Args:
        entities: List of entity instances to validate
        
    Returns:
        Validation summary dictionary
    """
    results = {
        "total_entities": len(entities),
        "valid_entities": 0,
        "invalid_entities": 0,
        "validation_issues": {},
        "entity_type_counts": {}
    }
    
    for i, entity in enumerate(entities):
        entity_type = type(entity).__name__.lower()
        
        # Count entity types
        results["entity_type_counts"][entity_type] = results["entity_type_counts"].get(entity_type, 0) + 1
        
        # Validate entity
        if hasattr(entity, 'validate'):
            issues = entity.validate()
            if issues:
                results["invalid_entities"] += 1
                results["validation_issues"][f"{entity_type}_{i}"] = issues
            else:
                results["valid_entities"] += 1
        else:
            # Try type-specific validation
            if entity_type == 'character':
                issues = validate_character_integrity(entity)
                if issues:
                    results["invalid_entities"] += 1
                    results["validation_issues"][f"{entity_type}_{i}"] = issues
                else:
                    results["valid_entities"] += 1
            else:
                results["valid_entities"] += 1  # Assume valid if no validation method
    
    return results