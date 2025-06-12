"""
Application Data Transfer Objects (DTOs)

This module contains data transfer objects used for communication between
application layers, API endpoints, and external services. DTOs provide
a stable interface for data exchange and help decouple internal domain
models from external representations.

Categories:
- Request DTOs: Input data structures for use cases
- Response DTOs: Output data structures from use cases  
- API DTOs: Data structures for REST API communication
- Integration DTOs: Data structures for external service integration
"""

# Request DTOs
from .requests import (
    ConceptAnalysisRequestDTO,
    ContentGenerationRequestDTO,
    ValidationRequestDTO,
    BalanceAnalysisRequestDTO,
    SpeciesGenerationRequestDTO,
    ClassGenerationRequestDTO,
    EquipmentGenerationRequestDTO,
    SpellGenerationRequestDTO,
    FeatGenerationRequestDTO
)

# Response DTOs
from .responses import (
    ConceptAnalysisResponseDTO,
    ContentGenerationResponseDTO,
    ValidationResponseDTO,
    BalanceAnalysisResponseDTO,
    GeneratedContentDTO,
    ContentCollectionDTO,
    ThematicElementsDTO,
    CulturalInsightsDTO,
    MechanicalSuggestionsDTO
)

# API DTOs for REST endpoints
from .api import (
    CreateConceptRequestDTO,
    CreateConceptResponseDTO,
    GenerateContentRequestDTO,
    GenerateContentResponseDTO,
    ValidationResultDTO,
    ErrorResponseDTO,
    PaginatedResponseDTO,
    HealthCheckResponseDTO
)

# Integration DTOs for external services
from .integrations import (
    LLMGenerationRequestDTO,
    LLMGenerationResponseDTO,
    DatabaseEntityDTO,
    CacheEntryDTO,
    FileStorageDTO,
    NotificationDTO
)

# Common/Shared DTOs
from .common import (
    BaseDTO,
    TimestampedDTO,
    IdentifiedDTO,
    MetadataDTO,
    PaginationDTO,
    SortingDTO,
    FilterDTO
)

# Content-specific DTOs
from .content import (
    SpeciesDTO,
    CharacterClassDTO,
    EquipmentDTO,
    SpellDTO,
    FeatDTO,
    TraitDTO,
    FeatureDTO,
    AbilityDTO,
    SkillDTO
)

# Validation and Error DTOs
from .validation import (
    ValidationIssueDTO,
    ValidationResultDTO,
    BalanceMetricsDTO,
    QualityScoreDTO,
    ComplianceCheckDTO
)

# Factory functions for common DTO patterns
def create_request_dto(dto_type: str, data: dict):
    """Factory function to create request DTOs dynamically."""
    dto_mapping = {
        'concept_analysis': ConceptAnalysisRequestDTO,
        'content_generation': ContentGenerationRequestDTO,
        'validation': ValidationRequestDTO,
        'balance_analysis': BalanceAnalysisRequestDTO,
        'species_generation': SpeciesGenerationRequestDTO,
        'class_generation': ClassGenerationRequestDTO,
        'equipment_generation': EquipmentGenerationRequestDTO,
        'spell_generation': SpellGenerationRequestDTO,
        'feat_generation': FeatGenerationRequestDTO
    }
    
    dto_class = dto_mapping.get(dto_type)
    if not dto_class:
        raise ValueError(f"Unknown DTO type: {dto_type}")
    
    return dto_class(**data)

def create_response_dto(dto_type: str, data: dict):
    """Factory function to create response DTOs dynamically."""
    dto_mapping = {
        'concept_analysis': ConceptAnalysisResponseDTO,
        'content_generation': ContentGenerationResponseDTO,
        'validation': ValidationResponseDTO,
        'balance_analysis': BalanceAnalysisResponseDTO
    }
    
    dto_class = dto_mapping.get(dto_type)
    if not dto_class:
        raise ValueError(f"Unknown DTO type: {dto_type}")
    
    return dto_class(**data)

# Conversion utilities
def entity_to_dto(entity, dto_class):
    """Convert domain entity to DTO."""
    if hasattr(entity, 'to_dict'):
        return dto_class(**entity.to_dict())
    else:
        # Use reflection to map fields
        entity_dict = {
            field: getattr(entity, field)
            for field in dto_class.__dataclass_fields__.keys()
            if hasattr(entity, field)
        }
        return dto_class(**entity_dict)

def dto_to_entity(dto, entity_class):
    """Convert DTO to domain entity."""
    if hasattr(dto, 'to_dict'):
        return entity_class(**dto.to_dict())
    else:
        # Use dataclass fields
        dto_dict = {
            field: getattr(dto, field)
            for field in entity_class.__dataclass_fields__.keys()
            if hasattr(dto, field)
        }
        return entity_class(**dto_dict)

# Validation utilities
def validate_dto(dto, strict: bool = True):
    """Validate DTO structure and constraints."""
    errors = []
    
    # Check required fields
    if hasattr(dto, '__dataclass_fields__'):
        for field_name, field_info in dto.__dataclass_fields__.items():
            if field_info.default == field_info.default_factory == dataclasses.MISSING:
                if not hasattr(dto, field_name) or getattr(dto, field_name) is None:
                    errors.append(f"Required field '{field_name}' is missing")
    
    # Custom validation if available
    if hasattr(dto, 'validate'):
        try:
            dto.validate()
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
    
    if errors and strict:
        raise ValueError(f"DTO validation failed: {'; '.join(errors)}")
    
    return errors

# Serialization utilities
def serialize_dto(dto) -> dict:
    """Serialize DTO to dictionary."""
    if hasattr(dto, 'to_dict'):
        return dto.to_dict()
    elif hasattr(dto, '__dataclass_fields__'):
        return dataclasses.asdict(dto)
    else:
        return dto.__dict__

def deserialize_dto(data: dict, dto_class):
    """Deserialize dictionary to DTO."""
    return dto_class(**data)

# Batch operations
def serialize_dto_list(dtos: list) -> list:
    """Serialize list of DTOs."""
    return [serialize_dto(dto) for dto in dtos]

def deserialize_dto_list(data_list: list, dto_class) -> list:
    """Deserialize list of dictionaries to DTOs."""
    return [deserialize_dto(data, dto_class) for data in data_list]

# DTO registry for dynamic discovery
DTO_REGISTRY = {
    # Request DTOs
    'concept_analysis_request': ConceptAnalysisRequestDTO,
    'content_generation_request': ContentGenerationRequestDTO,
    'validation_request': ValidationRequestDTO,
    'balance_analysis_request': BalanceAnalysisRequestDTO,
    
    # Response DTOs
    'concept_analysis_response': ConceptAnalysisResponseDTO,
    'content_generation_response': ContentGenerationResponseDTO,
    'validation_response': ValidationResponseDTO,
    'balance_analysis_response': BalanceAnalysisResponseDTO,
    
    # Content DTOs
    'species': SpeciesDTO,
    'character_class': CharacterClassDTO,
    'equipment': EquipmentDTO,
    'spell': SpellDTO,
    'feat': FeatDTO,
    
    # Common DTOs
    'base': BaseDTO,
    'timestamped': TimestampedDTO,
    'identified': IdentifiedDTO,
    'metadata': MetadataDTO
}

def get_dto_class(dto_name: str):
    """Get DTO class by name."""
    return DTO_REGISTRY.get(dto_name)

def list_available_dtos():
    """List all available DTO types."""
    return list(DTO_REGISTRY.keys())

# Export all public symbols
__all__ = [
    # Request DTOs
    'ConceptAnalysisRequestDTO',
    'ContentGenerationRequestDTO',
    'ValidationRequestDTO',
    'BalanceAnalysisRequestDTO',
    'SpeciesGenerationRequestDTO',
    'ClassGenerationRequestDTO',
    'EquipmentGenerationRequestDTO',
    'SpellGenerationRequestDTO',
    'FeatGenerationRequestDTO',
    
    # Response DTOs
    'ConceptAnalysisResponseDTO',
    'ContentGenerationResponseDTO',
    'ValidationResponseDTO',
    'BalanceAnalysisResponseDTO',
    'GeneratedContentDTO',
    'ContentCollectionDTO',
    'ThematicElementsDTO',
    'CulturalInsightsDTO',
    'MechanicalSuggestionsDTO',
    
    # API DTOs
    'CreateConceptRequestDTO',
    'CreateConceptResponseDTO',
    'GenerateContentRequestDTO',
    'GenerateContentResponseDTO',
    'ValidationResultDTO',
    'ErrorResponseDTO',
    'PaginatedResponseDTO',
    'HealthCheckResponseDTO',
    
    # Integration DTOs
    'LLMGenerationRequestDTO',
    'LLMGenerationResponseDTO',
    'DatabaseEntityDTO',
    'CacheEntryDTO',
    'FileStorageDTO',
    'NotificationDTO',
    
    # Common DTOs
    'BaseDTO',
    'TimestampedDTO',
    'IdentifiedDTO',
    'MetadataDTO',
    'PaginationDTO',
    'SortingDTO',
    'FilterDTO',
    
    # Content DTOs
    'SpeciesDTO',
    'CharacterClassDTO',
    'EquipmentDTO',
    'SpellDTO',
    'FeatDTO',
    'TraitDTO',
    'FeatureDTO',
    'AbilityDTO',
    'SkillDTO',
    
    # Validation DTOs
    'ValidationIssueDTO',
    'ValidationResultDTO',
    'BalanceMetricsDTO',
    'QualityScoreDTO',
    'ComplianceCheckDTO',
    
    # Utility functions
    'create_request_dto',
    'create_response_dto',
    'entity_to_dto',
    'dto_to_entity',
    'validate_dto',
    'serialize_dto',
    'deserialize_dto',
    'serialize_dto_list',
    'deserialize_dto_list',
    'get_dto_class',
    'list_available_dtos'
]

# Version and metadata
__version__ = '1.0.0'
__author__ = 'D&D Character Creator Team'
__description__ = 'Data Transfer Objects for D&D Character Creator Application'

# Configuration
DEFAULT_SERIALIZATION_FORMAT = 'json'
STRICT_VALIDATION = True
ENABLE_TYPE_CHECKING = True