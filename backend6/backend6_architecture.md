# D&D Character Creator - Backend6 Architecture

## Overview

A **Clean Architecture** implementation for a D&D 2024 creative content generation framework that transforms any character concept into balanced, rule-compliant D&D characters with complete level progression (1-20) and custom content generation.

## Architecture Principles

- **Clean Architecture**: Clear separation of concerns across four layers
- **Domain-Driven Design**: Business logic drives the architecture
- **Dependency Inversion**: Core and domain layers define interfaces, outer layers implement them
- **Single Responsibility**: Each component has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Testability**: Each layer can be tested independently

## Complete Backend6 Architecture

```
backend6/
├── core/                           # FOUNDATIONAL LAYER
│   ├── enums/                     # Type definitions
│   │   ├── __init__.py
│   │   ├── content_types.py       # Species, classes, spells, equipment types
│   │   ├── game_mechanics.py      # Damage types, action types, spell schools, conditions
│   │   ├── creativity_levels.py   # Creative freedom settings (conservative->maximum)
│   │   ├── balance_levels.py      # Balance enforcement levels (permissive->strict)
│   │   ├── export_formats.py      # VTT platforms, file formats, layout options
│   │   ├── progression_types.py   # Single-class, multiclass, milestone progressions
│   │   ├── validation_types.py    # Severity levels, validation categories
│   │   └── conversation_states.py # Interactive creation workflow states
│   ├── constants/                 # System constants
│   │   ├── __init__.py
│   │   ├── dnd_mechanics.py       # Core D&D 5e/2024 rules, proficiency bonuses
│   │   ├── balance_thresholds.py  # Power level limits, feature costs, review thresholds
│   │   ├── progression.py         # Level progression constants, tier definitions
│   │   ├── llm_prompts.py         # Structured LLM prompts for each content type
│   │   ├── validation_rules.py    # Rule compliance levels, deviation tolerances
│   │   ├── generation_limits.py   # Content creation boundaries, time/resource limits
│   │   └── export_templates.py    # VTT-specific templates, layout specifications
│   ├── utils/                     # Pure utility functions
│   │   ├── __init__.py
│   │   ├── dice_notation.py       # Dice parsing (1d8+3, 2d6+STR, etc.)
│   │   ├── text_processing.py     # Name generation, formatting, text analysis
│   │   ├── json_helpers.py        # Character sheet JSON utilities, validation
│   │   ├── math_helpers.py        # Statistical calculations, power level math
│   │   ├── balance_calculator.py  # Power level scoring, balance metrics
│   │   ├── content_utils.py       # Content analysis, theme extraction
│   │   ├── naming_validator.py    # Name validation, authenticity checking
│   │   ├── mechanical_parser.py   # Extract mechanical elements from text
│   │   └── rule_checker.py        # D&D rule validation utilities
│   ├── abstractions/              # Interface contracts
│   │   ├── __init__.py
│   │   ├── llm_provider.py        # LLM interface for content generation
│   │   ├── content_generator.py   # Content creation interface (species, classes)
│   │   ├── balance_analyzer.py    # Balance checking interface
│   │   ├── character_validator.py # Character validation interface
│   │   ├── character_repository.py # Character storage interface
│   │   ├── conversation_handler.py # Interactive session interface
│   │   └── export_service.py      # VTT export interface
│   └── exceptions/                # Base exception types
│       ├── __init__.py            # Centralized exception registry
│       ├── base.py                # Base exception classes, ValidationResult
│       ├── generation.py          # Content generation errors, LLM failures
│       ├── balance.py             # Balance validation errors, rule violations
│       ├── workflow.py            # Use case errors, workflow state errors
│       ├── export.py              # Export/conversion errors, VTT format issues
│       ├── persistence.py         # Database errors, repository failures
│       └── integration.py         # External service errors, API failures
│
├── domain/                         # BUSINESS LOGIC LAYER
│   ├── entities/                  # Business entities
│   │   ├── __init__.py
│   │   ├── character/             # Character entity complex
│   │   │   ├── __init__.py
│   │   │   ├── character.py       # Main character aggregate root
│   │   │   ├── progression.py     # Level progression entity with thematic evolution
│   │   │   └── character_sheet.py # JSON character sheet entity for VTT export
│   │   ├── content/               # D&D content entities
│   │   │   ├── __init__.py
│   │   │   ├── species.py         # Species/race entity with traits, lore
│   │   │   ├── character_class.py # Class entity with progression, features
│   │   │   ├── spell.py           # Spell entity with components, scaling
│   │   │   ├── feat.py            # Feat entity with prerequisites, effects
│   │   │   ├── weapon.py          # Weapon entity with properties, damage
│   │   │   ├── armor.py           # Armor entity with AC, properties
│   │   │   └── background.py      # Background entity with features, equipment
│   │   ├── generation/            # Generation-specific entities
│   │   │   ├── __init__.py
│   │   │   ├── character_concept.py # User concept entity with themes
│   │   │   ├── creative_constraints.py # Generation limits and parameters
│   │   │   ├── conversation.py    # Interactive session entity with state
│   │   │   └── content_request.py # Content generation request entity
│   │   └── base/                  # Base entity classes
│   │       ├── __init__.py
│   │       ├── entity.py          # Base entity with identity
│   │       └── aggregate_root.py  # Base aggregate root with domain events
│   ├── value_objects/             # Domain value objects
│   │   ├── __init__.py
│   │   ├── ability_scores.py      # Ability score collections with modifiers
│   │   ├── combat_stats.py        # AC, HP, initiative calculations
│   │   ├── spell_components.py    # Spell component data (V, S, M)
│   │   ├── balance_metrics.py     # Power level calculations, balance scores
│   │   ├── thematic_identity.py   # Character theme/concept data
│   │   ├── export_format.py       # VTT format specifications
│   │   ├── dice_expression.py     # Dice notation value object
│   │   └── progression_milestone.py # Level progression milestones
│   ├── services/                  # Domain services
│   │   ├── __init__.py
│   │   ├── character_generator.py # Core character generation orchestration
│   │   ├── content_creator.py     # Custom content creation (species, classes)
│   │   ├── balance_analyzer.py    # Power level analysis, balance validation
│   │   ├── progression_planner.py # Level 1-20 progression planning
│   │   ├── thematic_validator.py  # Concept consistency validation
│   │   ├── rule_enforcer.py       # D&D rule compliance enforcement
│   │   └── lore_generator.py      # Generate history/lore for custom content
│   ├── factories/                 # Entity factories
│   │   ├── __init__.py
│   │   ├── character_factory.py   # Character creation from concepts
│   │   ├── content_factory.py     # Custom content factory (species, classes)
│   │   ├── progression_factory.py # Level progression factory
│   │   └── conversation_factory.py # Interactive session factory
│   ├── specifications/            # Business rule specifications
│   │   ├── __init__.py
│   │   ├── balance_specs.py       # Balance requirement specifications
│   │   ├── rule_compliance_specs.py # D&D rule compliance specifications
│   │   ├── content_generation_specs.py # Generation constraint specifications
│   │   ├── thematic_consistency_specs.py # Theme validation specifications
│   │   └── export_compatibility_specs.py # VTT compatibility specifications
│   └── events/                    # Domain events
│       ├── __init__.py
│       ├── character_created.py   # Character creation events
│       ├── content_generated.py   # Custom content events
│       ├── balance_validated.py   # Balance check events
│       ├── progression_completed.py # Full progression events
│       ├── conversation_updated.py # Interactive session events
│       └── lore_generated.py      # Custom content lore events
│
├── application/                    # APPLICATION LAYER
│   ├── dtos/                      # Data transfer objects
│   │   ├── __init__.py
│   │   ├── requests/              # Request DTOs
│   │   │   ├── __init__.py
│   │   │   ├── character_creation.py # Character creation requests
│   │   │   ├── character_refinement.py # Refinement requests
│   │   │   ├── content_generation.py # Content generation requests
│   │   │   ├── conversation_requests.py # Interactive session requests
│   │   │   └── export_requests.py # Export format requests
│   │   └── responses/             # Response DTOs
│   │       ├── __init__.py
│   │       ├── character_response.py # Character data responses
│   │       ├── generation_response.py # Generation status responses
│   │       ├── validation_response.py # Validation results
│   │       ├── conversation_response.py # Interactive session responses
│   │       └── export_response.py # Export results
│   ├── use_cases/                 # Application use cases
│   │   ├── __init__.py
│   │   ├── interactive_creation/  # Interactive character creation workflow
│   │   │   ├── __init__.py
│   │   │   ├── start_conversation.py # Begin character creation session
│   │   │   ├── process_concept.py # Process initial concept input
│   │   │   ├── refine_character.py # Handle user feedback iteration
│   │   │   ├── validate_concept.py # Validate concept feasibility
│   │   │   └── finalize_character.py # Complete character creation
│   │   ├── generation/            # Content generation use cases
│   │   │   ├── __init__.py
│   │   │   ├── generate_character.py # Full character generation pipeline
│   │   │   ├── generate_custom_content.py # Custom species/class/spell creation
│   │   │   ├── generate_progression.py # Level 1-20 progression generation
│   │   │   ├── generate_lore.py   # Generate history/lore for custom content
│   │   │   └── validate_balance.py # Balance validation pipeline
│   │   ├── export/                # Export use cases
│   │   │   ├── __init__.py
│   │   │   ├── export_character_sheets.py # JSON export for all levels
│   │   │   ├── export_vtt_formats.py # VTT-specific format export
│   │   │   ├── export_custom_content.py # Custom content export
│   │   │   └── generate_summary_pdf.py # PDF summary generation
│   │   └── validation/            # Validation use cases
│   │       ├── __init__.py
│   │       ├── validate_character.py # Complete character validation
│   │       ├── validate_content.py # Custom content validation
│   │       └── validate_progression.py # Progression validation
│   └── services/                  # Application services
│       ├── __init__.py
│       ├── conversation_orchestrator.py # Interactive flow coordination
│       ├── generation_orchestrator.py # Content generation coordination
│       ├── validation_orchestrator.py # Multi-layer validation coordination
│       ├── export_orchestrator.py # Multi-format export coordination
│       └── workflow_coordinator.py # Overall workflow management
│
└── infrastructure/                 # INFRASTRUCTURE LAYER
    ├── config/                    # Configuration management
    │   ├── __init__.py
    │   ├── settings.py            # Application settings, environment variables
    │   ├── llm_config.py          # LLM provider configurations (OpenAI, Anthropic)
    │   ├── creativity_config.py   # Creative freedom settings
    │   ├── balance_config.py      # Balance enforcement configurations
    │   └── export_config.py       # Export format configurations
    ├── llm/                       # LLM provider implementations
    │   ├── __init__.py
    │   ├── base_provider.py       # Base LLM provider abstract class
    │   ├── openai_provider.py     # OpenAI implementation (primary creative)
    │   ├── anthropic_provider.py  # Anthropic implementation (balance analysis)
    │   ├── llm_factory.py         # Provider factory with fallback logic
    │   └── prompt_manager.py      # Prompt template management
    ├── repositories/              # Data access implementations
    │   ├── __init__.py
    │   ├── character_repository.py # Character storage (JSON files, database)
    │   ├── conversation_repository.py # Conversation state storage
    │   ├── content_repository.py  # Custom content storage and retrieval
    │   ├── template_repository.py # Character sheet templates
    │   └── cache_repository.py    # Caching layer for expensive operations
    ├── export/                    # Export service implementations
    │   ├── __init__.py
    │   ├── json_exporter.py       # Standard JSON export
    │   ├── vtt_exporters.py       # VTT-specific exporters (Roll20, FoundryVTT)
    │   ├── pdf_generator.py       # PDF generation service
    │   ├── export_factory.py      # Export service factory
    │   └── template_renderer.py   # Template rendering engine
    ├── validation/                # Validation service implementations
    │   ├── __init__.py
    │   ├── character_validator.py # Character validation implementation
    │   ├── content_validator.py   # Custom content validation
    │   ├── balance_validator.py   # Balance analysis implementation
    │   └── rule_validator.py      # D&D rule compliance validation
    └── persistence/               # Database/file storage
        ├── __init__.py
        ├── models/                # Data models
        │   ├── __init__.py
        │   ├── character_model.py # Character data model
        │   ├── conversation_model.py # Conversation state model
        │   ├── content_model.py   # Custom content model
        │   └── session_model.py   # User session model
        ├── migrations/            # Database migrations
        │   ├── __init__.py
        │   ├── 001_initial_schema.py # Initial database schema
        │   ├── 002_conversation_tables.py # Conversation storage
        │   └── 003_content_storage.py # Custom content storage
        └── seeders/               # Database seed data
            ├── __init__.py
            ├── official_content.py # Official D&D content seed
            └── sample_characters.py # Sample character data

# Additional files
├── container.py                   # Dependency injection container
├── main.py                       # Application entry point
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── docker-compose.yml            # Development environment setup
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data fixtures
└── _copy/                        # Legacy code for reference
    └── validation/
        └── unified_validator.py  # Your existing validator (to be refactored)
```

## Layer Details and Responsibilities

### Core Layer (`/core/`)
**Infrastructure-independent foundations**

- **Enums**: Type-safe definitions for all D&D content types, creativity levels, export formats
- **Constants**: D&D 5e/2024 rules, balance thresholds, LLM prompts, export templates
- **Utils**: Pure functions for calculations, parsing, validation, content analysis
- **Abstractions**: Interface contracts that outer layers must implement
- **Exceptions**: Comprehensive exception hierarchy with recovery suggestions

**Key Features**:
- No external dependencies (database, web framework, LLM providers)
- Contains all D&D business rules and constraints
- Provides utilities for balance calculation and content analysis
- Defines interfaces for all external concerns

### Domain Layer (`/domain/`)
**Pure business logic - D&D rules + creative content generation**

- **Entities**: Rich domain objects with behavior (Character, Species, Spell, etc.)
- **Value Objects**: Immutable data structures (AbilityScores, BalanceMetrics)
- **Services**: Complex business logic that doesn't fit in entities
- **Factories**: Entity creation from various inputs (concepts, LLM responses)
- **Specifications**: Business rule validation logic
- **Events**: Domain events for cross-cutting concerns

**Key Features**:
- Character entity manages complete 1-20 progression
- Content entities include custom species, classes, spells, equipment
- Balance analysis ensures all content meets power level standards
- Thematic validation maintains character concept consistency
- **NEW**: Lore generation service for custom content backstories

### Application Layer (`/application/`)
**Use case orchestration for creative content generation**

- **DTOs**: Data transfer objects for API boundaries
- **Use Cases**: Application workflows (interactive creation, content generation, export)
- **Services**: Application-level orchestration and coordination

**Key Features**:
- Interactive character creation workflow with user feedback loops
- Complete character generation pipeline with validation
- Multi-format export to VTT platforms
- **NEW**: Conversation management for interactive sessions
- **NEW**: Comprehensive validation pipeline coordination

### Infrastructure Layer (`/infrastructure/`)
**External concerns and implementation details**

- **Config**: Environment-specific configuration management
- **LLM**: Provider implementations for OpenAI, Anthropic with fallback
- **Repositories**: Data persistence with multiple storage options
- **Export**: VTT-specific export implementations
- **Validation**: Concrete validation service implementations
- **Persistence**: Database models, migrations, and seed data

**Key Features**:
- Multiple LLM provider support with intelligent fallback
- Flexible storage options (files, database, cache)
- VTT-specific export formats (Roll20, FoundryVTT, D&D Beyond)
- **NEW**: Caching layer for expensive operations
- **NEW**: Template rendering engine for exports

## Key Architecture Updates

### 1. Enhanced Exception Handling
```
core/exceptions/
├── base.py                # ValidationResult, base exception classes
├── generation.py          # LLM failures, content generation errors
├── balance.py             # Balance violations, rule compliance errors
├── workflow.py            # Use case errors, state management
├── export.py              # VTT format errors, conversion failures
├── persistence.py         # Database errors, storage failures
└── integration.py         # External service errors, API failures
```

### 2. Comprehensive Validation Pipeline
```
application/use_cases/validation/
├── validate_character.py     # Complete character validation
├── validate_content.py       # Custom content validation  
├── validate_progression.py   # Level progression validation
└── validate_balance.py       # Power level validation
```

### 3. Interactive Conversation Management
```
domain/entities/generation/
├── conversation.py           # Session state management
├── character_concept.py      # Concept evolution tracking
└── creative_constraints.py   # Generation parameter management
```

### 4. Custom Content Lore Generation
```
domain/services/
└── lore_generator.py         # Generate history/lore for custom content

application/use_cases/generation/
└── generate_lore.py          # Lore generation use case
```

### 5. Enhanced Export System
```
infrastructure/export/
├── json_exporter.py          # Standard JSON export
├── vtt_exporters.py          # VTT-specific formats
├── pdf_generator.py          # PDF character sheets
├── export_factory.py        # Export service factory
└── template_renderer.py     # Template rendering engine
```

## Development Workflow

### 1. Character Creation Flow
```
User Input → Conversation → Concept → Generation → Validation → Refinement → Export
```

### 2. Custom Content Pipeline  
```
Concept → LLM Generation → Balance Analysis → Rule Validation → Lore Generation → Integration
```

### 3. Export Pipeline
```
Character Data → Format Selection → Template Rendering → Validation → File Generation
```

## Configuration Management

### Environment Variables
```bash
# LLM Configuration
PRIMARY_LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
BALANCE_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key

# Generation Settings
DEFAULT_CREATIVITY_LEVEL=standard
DEFAULT_BALANCE_LEVEL=standard
MAX_CUSTOM_CONTENT_PER_CHARACTER=10

# Storage Configuration
DATABASE_URL=postgresql://localhost/dnd_creator
REDIS_URL=redis://localhost:6379
CHARACTER_STORAGE_PATH=./data/characters

# Export Settings
ENABLE_VTT_FORMATS=true
PDF_GENERATION_ENABLED=true
```

## Testing Strategy

### Unit Tests
- Each domain service, entity, and value object
- Core utilities and calculations
- Exception handling and recovery

### Integration Tests
- LLM provider integrations
- Database operations
- Export format generation
- Validation pipelines

### End-to-End Tests
- Complete character creation workflows
- Multi-format export processes
- Interactive conversation flows

## Deployment Considerations

### Docker Setup
```yaml
# docker-compose.yml
services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://db:5432/dnd_creator
      - REDIS_URL=redis://redis:6379
  
  db:
    image: postgres:15
    
  redis:
    image: redis:7
```

### Production Checklist
- [ ] LLM provider API keys configured
- [ ] Database migrations applied
- [ ] Export templates validated
- [ ] Balance thresholds calibrated
- [ ] Error monitoring configured
- [ ] Performance metrics enabled

This architecture provides a solid foundation for building a comprehensive D&D character creator that balances creative freedom with mechanical balance while maintaining clean separation of concerns.