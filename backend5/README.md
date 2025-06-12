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