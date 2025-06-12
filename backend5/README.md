# D&D Character Creator - Creative Content Framework

## Overview

This is a **background-driven creative content framework** for D&D 2024, designed to generate balanced, thematic, and rule-compliant content based on character background stories and concepts.

## Architecture

The system follows **Clean Architecture** with **Domain-Driven Design** principles, organized into layers that maintain clear separation of concerns and dependency direction.

### Layer Structure

```
backend5/
├── core/                           # Domain Layer (Business Logic)
├── application/                    # Application Layer (Use Cases)  
├── infrastructure/                 # Infrastructure Layer (External Concerns)
├── interfaces/                     # Interface Layer (API/UI)
└── tests/                         # Test Layer (All Test Types)
```

## Core Domain Layer

The `core/` directory contains the foundational domain model that defines D&D content creation and validation rules.

### Updated Core Structure

```
/backend5/core/
├── abstractions/                   # D&D Rule Contracts
│   ├── __init__.py
│   ├── character_class.py         # Abstract character class contracts
│   ├── species.py                 # Abstract species contracts  
│   ├── equipment.py               # Abstract equipment contracts
│   ├── spell.py                   # Abstract spell contracts
│   ├── feat.py                    # Abstract feat contracts
│   └── content_validator.py       # Abstract validation contracts
│
├── entities/                      # Core Domain Entities  
│   ├── __init__.py
│   ├── character.py               # Character entity
│   ├── generated_content.py       # Generated content entity
│   ├── character_concept.py       # Character concept entity
│   └── content_collection.py      # Content collection entity
│
├── value_objects/                 # Supporting Data Structures
│   ├── __init__.py
│   ├── balance_metrics.py         # Balance calculation data
│   ├── validation_result.py       # Validation result data
│   ├── content_metadata.py        # Content metadata
│   ├── generation_constraints.py  # Generation constraint data
│   └── thematic_elements.py       # Thematic element data
│
├── services/                      # Domain Services [NEW]
│   ├── __init__.py
│   ├── validation_coordinator.py  # Cross-entity validation coordination
│   ├── content_generator.py       # Content generation orchestration
│   └── balance_analyzer.py        # Balance analysis coordination
│
├── utils/                         # Pure Content Functions
│   ├── __init__.py
│   ├── content_utils.py           # Content manipulation utilities
│   ├── balance_calculator.py      # Balance calculation functions
│   ├── naming_validator.py        # Content naming validation
│   ├── mechanical_parser.py       # Mechanical text parsing
│   └── rule_checker.py            # D&D rule validation functions
│
├── enums/                         # Content Type Enumerations
│   ├── __init__.py
│   ├── content_types.py           # Content type definitions
│   ├── generation_methods.py      # Generation method types
│   ├── validation_types.py        # Validation type definitions
│   ├── mechanical_category.py     # Mechanical categorization
│   └── dnd_constants.py           # D&D mechanical constants
│
├── exceptions/                    # Core Domain Exceptions
│   ├── __init__.py
│   ├── generation_errors.py       # Content generation exceptions
│   ├── validation_errors.py       # Validation failure exceptions
│   └── rule_violation_errors.py   # D&D rule violation exceptions
│
└── __init__.py                    # Core module exports
```

### Key Architectural Changes

#### 1. Added Domain Services Layer (`/services/`)

Domain services handle coordination between entities and complex business logic that doesn't naturally belong to a single entity:

- **`validation_coordinator.py`** - Orchestrates validation across multiple content types
- **`content_generator.py`** - Coordinates content generation workflows  
- **`balance_analyzer.py`** - Performs complex balance analysis across content collections

#### 2. Enhanced Abstractions (`/abstractions/`)

Abstract base classes define D&D rule contracts that all concrete implementations must follow:

- **Character Class Contracts** - Define class feature, progression, and multiclassing rules
- **Species Contracts** - Define trait, ability score, and cultural feature rules
- **Equipment Contracts** - Define weapon, armor, and magic item mechanics
- **Spell Contracts** - Define spellcasting, targeting, and effect rules
- **Content Validation Contracts** - Define validation pipeline interfaces

#### 3. Structured Entities (`/entities/`)

Core domain entities represent the primary business objects:

- **`Character`** - Complete character with stats, features, and progression
- **`GeneratedContent`** - Individual generated content items with metadata
- **`CharacterConcept`** - Background-driven character concepts for generation
- **`ContentCollection`** - Collections of related generated content

#### 4. Comprehensive Value Objects (`/value_objects/`)

Immutable data structures supporting the domain model:

- **`BalanceMetrics`** - Power level, utility, and balance calculations
- **`ValidationResult`** - Validation outcomes with issues and suggestions
- **`ThematicElements`** - Theme, cultural, and power level data
- **`GenerationConstraints`** - Content generation parameters and limits

#### 5. Domain Services Integration

Domain services coordinate complex operations:

```python
# Example: CoreValidationCoordinator usage
from core.services import CoreValidationCoordinator

coordinator = CoreValidationCoordinator()
coordinator.register_validator("spell", SpellValidator())
coordinator.register_validator("feat", FeatValidator())

validation_results = coordinator.validate_all_content(content_collection)
summary = coordinator.get_validation_summary(validation_results)
```

## Application Layer

The application layer orchestrates domain services to fulfill specific use cases.

### Application Structure

```
/backend5/application/
├── use_cases/                     # Application Use Cases
│   ├── __init__.py
│   ├── concept_processor.py       # Background concept analysis [NEW]
│   ├── content_generator.py       # Content generation coordination
│   ├── validation_orchestrator.py # Validation workflow management
│   └── balance_analyzer.py        # Balance analysis workflows
│
├── dto/                          # Data Transfer Objects
│   ├── __init__.py
│   ├── requests.py               # Request DTOs
│   └── responses.py              # Response DTOs
│
├── services/                     # Application Services
│   ├── __init__.py
│   ├── llm_integration.py        # LLM service integration
│   ├── template_engine.py        # Template processing service
│   └── content_persistence.py    # Content storage service
│
└── __init__.py                   # Application module exports
```

### Key Use Cases

#### Background Concept Processing

The new **`concept_processor.py`** use case handles the analysis and processing of character background concepts:

```python
from application.use_cases import ConceptProcessorUseCase
from application.dto import ConceptAnalysisRequest

processor = ConceptProcessorUseCase()
request = ConceptAnalysisRequest(
    raw_concept="A former noble who lost everything and now seeks redemption through divine magic",
    character_name="Lysander",
    target_level=5
)

response = await processor.execute(request)
if response.success:
    concept = response.processed_concept
    themes = response.thematic_elements
    recommendations = response.recommended_content_types
```

## Infrastructure Layer

External concerns and technical implementations.

```
/backend5/infrastructure/
├── llm/                          # LLM Provider Implementations
├── persistence/                  # Data Storage Implementations  
├── templates/                    # Content Generation Templates
├── config/                       # Configuration Management
└── external/                     # External Service Integrations
```

## Interface Layer

API endpoints and user interface concerns.

```
/backend5/interfaces/
├── api/                          # REST API Endpoints
├── cli/                          # Command Line Interface
└── web/                          # Web Interface (if applicable)
```

## Testing Strategy

Comprehensive testing across all architectural layers.

```
/backend5/tests/
├── unit/                         # Unit Tests (Domain Logic)
├── integration/                  # Integration Tests (Cross-Layer)
├── application/                  # Application Use Case Tests
├── infrastructure/               # Infrastructure Component Tests
└── end_to_end/                   # Full System Tests
```

## Key Design Principles

### 1. Background-Driven Generation
All content generation starts with character background concepts, ensuring thematic coherence and narrative consistency.

### 2. Rule Compliance First
D&D 2024 rules are enforced through abstract contracts, ensuring all generated content meets official game standards.

### 3. Balance by Design
Balance metrics are calculated and validated at every stage, preventing overpowered or underwhelming content.

### 4. Thematic Coherence
Content generation maintains thematic consistency through extracted themes and cultural elements.

### 5. Clean Architecture
Clear separation of concerns with dependency inversion, making the system maintainable and testable.

## Getting Started

### Prerequisites
- Python 3.11+
- FastAPI for API layer
- Pydantic for data validation
- SQLAlchemy for persistence (if database storage is needed)

### Installation
```bash
cd backend5
pip install -r requirements.txt
```

### Basic Usage
```python
from core import ConceptProcessorUseCase, ContentGeneratorUseCase
from core.enums import ContentType

# Process background concept
concept_processor = ConceptProcessorUseCase()
concept_request = ConceptAnalysisRequest(
    raw_concept="A scholarly wizard seeking ancient knowledge",
    target_level=3
)

concept_response = await concept_processor.execute(concept_request)

# Generate content based on concept
if concept_response.success:
    content_generator = ContentGeneratorUseCase()
    generation_request = ContentGenerationRequest(
        concept=concept_response.processed_concept,
        content_types=[ContentType.SPELL, ContentType.FEAT]
    )
    
    content_response = await content_generator.execute(generation_request)
```

## Architecture Benefits

### Domain-Driven Design
- **Rich Domain Model** - Business logic encapsulated in domain entities and services
- **Ubiquitous Language** - D&D terminology used consistently throughout
- **Bounded Contexts** - Clear boundaries between content types and generation concerns

### Clean Architecture
- **Dependency Inversion** - Core domain independent of external concerns
- **Testability** - Easy unit testing of business logic
- **Flexibility** - Easy to swap infrastructure implementations

### Background-Driven Approach
- **Narrative Consistency** - All generated content fits the character's story
- **Thematic Coherence** - Content maintains consistent themes and cultural elements
- **Player Agency** - Players drive content through their background concepts

This architecture provides a solid foundation for generating high-quality, balanced, and thematically consistent D&D content while maintaining clean separation of concerns and testability.

# update the architecture with:

backend5/
├── core/
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── mechanics.py           # D&D 5e game mechanics
│   │   ├── content_generation.py  # Content generation constants
│   │   ├── validation.py          # Validation rules and thresholds
│   │   └── balance.py             # Game balance constants
│   └── ...
├── infrastructure/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Application settings (Pydantic)
│   │   ├── database.py            # Database configuration
│   │   ├── external_services.py   # External API configurations
│   │   └── environment.py         # Environment-specific configs
│   └── ...
└── config/                        # DELETE THIS DIRECTORY
    └── game_constants.py           # DELETE THIS FILE

# update architecture to reflect:

Based on my analysis of the `/backend5/domain` directory and its integration with the rest of the backend5 modules, here's my assessment and recommended architecture:

## Current Issues Identified

### 1. **Missing Domain Components**
- No domain services layer
- Incomplete entity relationships
- Missing domain events system
- No aggregate roots properly defined
- Lacking domain specifications/rules

### 2. **Integration Gaps**
- Domain entities don't align with infrastructure repositories
- Missing domain-to-DTO mapping layer
- No clear boundary between domain and application services

### 3. **Architectural Inconsistencies**
- Domain logic scattered across application layer
- Business rules not properly encapsulated in domain
- Missing domain validation at entity level

## Recommended Domain Architecture

```
/backend5/domain/
├── __init__.py                     # Domain layer exports
├── exceptions/                     # Domain-specific exceptions
│   ├── __init__.py
│   ├── base.py                    # Base domain exceptions
│   ├── validation.py              # Validation exceptions
│   ├── business_rules.py          # Business rule violations
│   └── content_creation.py        # Content creation exceptions
├── entities/                       # Core business entities
│   ├── __init__.py
│   ├── base/                      # Base entity classes
│   │   ├── __init__.py
│   │   ├── entity.py              # Base entity with ID
│   │   ├── aggregate_root.py      # Base aggregate root
│   │   └── value_object.py        # Base value objects
│   ├── content/                   # Content entities
│   │   ├── __init__.py
│   │   ├── species.py             # Species entity
│   │   ├── character_class.py     # Character class entity
│   │   ├── subclass.py            # Subclass entity
│   │   ├── spell.py               # Spell entity
│   │   ├── feat.py                # Feat entity
│   │   ├── equipment.py           # Equipment entity
│   │   ├── magic_item.py          # Magic item entity
│   │   ├── background.py          # Background entity
│   │   └── monster.py             # Monster entity
│   ├── generation/                # Generation-related entities
│   │   ├── __init__.py
│   │   ├── generation_request.py  # Generation request aggregate
│   │   ├── generation_result.py   # Generation result entity
│   │   ├── template.py            # Template entity
│   │   └── prompt.py              # Prompt entity
│   ├── validation/                # Validation entities
│   │   ├── __init__.py
│   │   ├── validation_result.py   # Validation result entity
│   │   ├── rule_violation.py      # Rule violation entity
│   │   └── balance_assessment.py  # Balance assessment entity
│   └── user/                      # User-related entities
│       ├── __init__.py
│       ├── user.py                # User aggregate root
│       ├── profile.py             # User profile entity
│       └── preferences.py         # User preferences entity
├── value_objects/                 # Domain value objects
│   ├── __init__.py
│   ├── content/                   # Content-related VOs
│   │   ├── __init__.py
│   │   ├── ability_scores.py      # Ability score collections
│   │   ├── skills.py              # Skill collections
│   │   ├── damage_resistance.py   # Damage resistances
│   │   ├── spell_components.py    # Spell component collections
│   │   └── equipment_properties.py # Equipment properties
│   ├── generation/                # Generation VOs
│   │   ├── __init__.py
│   │   ├── generation_config.py   # Generation configuration
│   │   ├── prompt_template.py     # Prompt template
│   │   └── quality_metrics.py     # Quality assessment metrics
│   └── common/                    # Common VOs
│       ├── __init__.py
│       ├── identifier.py          # Strong-typed IDs
│       ├── metadata.py            # Content metadata
│       ├── version.py             # Versioning info
│       └── tags.py                # Tag collections
├── services/                      # Domain services
│   ├── __init__.py
│   ├── content/                   # Content domain services
│   │   ├── __init__.py
│   │   ├── balance_analyzer.py    # Balance analysis service
│   │   ├── content_validator.py   # Content validation service
│   │   ├── dependency_resolver.py # Content dependency resolution
│   │   └── compatibility_checker.py # Content compatibility
│   ├── generation/                # Generation domain services
│   │   ├── __init__.py
│   │   ├── prompt_builder.py      # Prompt construction service
│   │   ├── template_matcher.py    # Template matching service
│   │   ├── quality_assessor.py    # Quality assessment service
│   │   └── iteration_manager.py   # Iteration management
│   └── user/                      # User domain services
│       ├── __init__.py
│       ├── preference_matcher.py  # User preference matching
│       └── content_recommender.py # Content recommendation
├── specifications/                # Domain specifications (business rules)
│   ├── __init__.py
│   ├── base.py                    # Base specification pattern
│   ├── content/                   # Content specifications
│   │   ├── __init__.py
│   │   ├── balance_specs.py       # Balance requirement specs
│   │   ├── complexity_specs.py    # Complexity requirement specs
│   │   ├── theme_specs.py         # Theme consistency specs
│   │   └── rule_compliance_specs.py # D&D rule compliance
│   ├── generation/                # Generation specifications
│   │   ├── __init__.py
│   │   ├── quality_specs.py       # Quality requirement specs
│   │   ├── template_specs.py      # Template matching specs
│   │   └── prompt_specs.py        # Prompt requirement specs
│   └── user/                      # User specifications
│       ├── __init__.py
│       ├── permission_specs.py    # User permission specs
│       └── preference_specs.py    # User preference specs
├── events/                        # Domain events
│   ├── __init__.py
│   ├── base.py                    # Base domain event
│   ├── content/                   # Content events
│   │   ├── __init__.py
│   │   ├── content_created.py     # Content creation events
│   │   ├── content_validated.py   # Content validation events
│   │   ├── content_updated.py     # Content update events
│   │   └── balance_assessed.py    # Balance assessment events
│   ├── generation/                # Generation events
│   │   ├── __init__.py
│   │   ├── generation_requested.py # Generation request events
│   │   ├── generation_completed.py # Generation completion events
│   │   ├── generation_failed.py   # Generation failure events
│   │   └── iteration_completed.py # Iteration completion events
│   └── user/                      # User events
│       ├── __init__.py
│       ├── user_registered.py     # User registration events
│       └── preferences_updated.py # Preference update events
├── repositories/                  # Domain repository interfaces
│   ├── __init__.py
│   ├── base.py                    # Base repository interface
│   ├── content_repository.py      # Content repository interface
│   ├── generation_repository.py   # Generation repository interface
│   ├── template_repository.py     # Template repository interface
│   ├── user_repository.py         # User repository interface
│   └── validation_repository.py   # Validation repository interface
├── factories/                     # Domain factories
│   ├── __init__.py
│   ├── content_factory.py         # Content entity factory
│   ├── generation_factory.py      # Generation entity factory
│   ├── template_factory.py        # Template factory
│   └── validation_factory.py      # Validation entity factory
└── aggregates/                    # Aggregate definitions
    ├── __init__.py
    ├── content_aggregate.py        # Content aggregate root
    ├── generation_aggregate.py     # Generation aggregate root
    ├── user_aggregate.py           # User aggregate root
    └── validation_aggregate.py     # Validation aggregate root
```

## Key Architectural Principles

### 1. **Aggregate Design**
```python
# Content Aggregate Root
class ContentAggregate:
    """
    Content aggregate managing content lifecycle,
    validation, and business rule enforcement.
    """
    - Content entity (root)
    - Validation results
    - Balance assessments
    - Version history
    - Dependencies
```

### 2. **Domain Service Responsibilities**
```python
# Clear separation of concerns
Domain Services:
    - Cross-aggregate business logic
    - Complex domain operations
    - Policy enforcement
    - External domain interactions

Application Services:
    - Orchestration
    - Transaction management
    - DTO conversion
    - Infrastructure coordination
```

### 3. **Specification Pattern**
```python
# Business rule encapsulation
class BalanceSpecification:
    """
    Encapsulates D&D 5e balance requirements
    as executable specifications.
    """
    def is_satisfied_by(self, content: Content) -> bool
    def get_violation_reasons(self, content: Content) -> List[str]
```

### 4. **Domain Events**
```python
# Event-driven domain behavior
class ContentCreatedEvent(DomainEvent):
    """
    Published when new content is created,
    triggering validation and analysis workflows.
    """
```

### 5. **Value Object Design**
```python
# Immutable domain concepts
class AbilityScores(ValueObject):
    """
    Encapsulates ability score collections
    with domain-specific validation and behavior.
    """
```

## Integration Points

### 1. **With Application Layer**
- Domain services called by application services
- Domain events handled by application event handlers
- Repository interfaces implemented by infrastructure

### 2. **With Infrastructure Layer**
- Repository implementations in infrastructure
- Event publishers in infrastructure
- External service adapters in infrastructure

### 3. **With Core Enums**
- Domain entities use core enums for type safety
- Value objects validate against enum constraints
- Specifications use enums for rule definitions

## Business Rule Encapsulation

### 1. **Entity-Level Rules**
- Invariants enforced in entity constructors
- State change validation in entity methods
- Aggregate consistency rules

### 2. **Domain Service Rules**
- Cross-entity business logic
- Complex validation rules
- Policy enforcement

### 3. **Specification Rules**
- Reusable business rule queries
- Complex criteria evaluation
- Rule composition and combination

This architecture ensures:
- **Clean separation** between domain logic and infrastructure
- **Proper encapsulation** of business rules
- **Event-driven** domain behavior
- **Testable** domain logic
- **Consistent** with DDD principles
- **Aligned** with the existing backend5 structure

The domain layer becomes the true heart of the application, containing all business logic while remaining independent of external concerns.