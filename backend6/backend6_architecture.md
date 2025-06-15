# D&D Character Creator - Backend6 Architecture

## Overview

A **Clean Architecture** implementation for a D&D 2024 creative content generation framework that transforms any character concept into balanced, rule-compliant D&D characters with complete level progression (1-20) and custom content generation. **Enhanced with AI-powered dynamic culture generation** that creates authentic cultural naming systems on-demand from user prompts.

## Architecture Principles

- **Clean Architecture**: Clear separation of concerns across four layers
- **Domain-Driven Design**: Business logic drives the architecture
- **Dependency Inversion**: Core and domain layers define interfaces, outer layers implement them
- **Single Responsibility**: Each component has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Testability**: Each layer can be tested independently
- **Cultural Authenticity**: AI-generated cultures maintain educational accuracy and respect

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
│   │   ├── conversation_states.py # Interactive creation workflow states
│   │   └── culture_types.py       # 🆕 Culture generation types, authenticity levels
│   ├── constants/                 # System constants
│   │   ├── __init__.py
│   │   ├── dnd_mechanics.py       # Core D&D 5e/2024 rules, proficiency bonuses
│   │   ├── balance_thresholds.py  # Power level limits, feature costs, review thresholds
│   │   ├── progression.py         # Level progression constants, tier definitions
│   │   ├── llm_prompts.py         # Structured LLM prompts for each content type
│   │   ├── validation_rules.py    # Rule compliance levels, deviation tolerances
│   │   ├── generation_limits.py   # Content creation boundaries, time/resource limits
│   │   ├── export_templates.py    # VTT-specific templates, layout specifications
│   │   └── culture_prompts.py     # 🆕 Culture generation prompt templates, research guidelines
│   ├── utils/                     # Pure utility functions
│   │   ├── __init__.py
│   │   ├── dice_notation.py       # Dice parsing (1d8+3, 2d6+STR, etc.)
│   │   ├── text_processing.py     # ✅ Name generation, formatting, text analysis, culture-agnostic utilities
│   │   ├── json_helpers.py        # Character sheet JSON utilities, validation
│   │   ├── math_helpers.py        # Statistical calculations, power level math
│   │   ├── balance_calculator.py  # Power level scoring, balance metrics
│   │   ├── content_utils.py       # Content analysis, theme extraction
│   │   ├── naming_validator.py    # Name validation, authenticity checking
│   │   ├── mechanical_parser.py   # Extract mechanical elements from text
│   │   ├── rule_checker.py        # D&D rule validation utilities
│   │   ├── cultures/              # 🆕 Dynamic culture generation system
│   │   │   ├── __init__.py
│   │   │   ├── base_culture.py    # ✅ Base culture template and interfaces
│   │   │   ├── culture_generator.py # 🆕 Core culture generation logic (LLM-independent)
│   │   │   ├── prompt_templates.py # 🆕 Prompt engineering templates for culture generation
│   │   │   ├── culture_parser.py  # 🆕 Parse LLM responses into BaseCulture structures
│   │   │   └── available_cultures/ # ✅ Pre-built culture implementations
│   │   │       ├── __init__.py
│   │   │       ├── ancient/       # Ancient civilizations
│   │   │       ├── medieval/      # Medieval cultures  
│   │   │       ├── asian/         # Asian cultures
│   │   │       ├── fantasy/       # Fantasy cultures
│   │   │       ├── modern/        # Modern cultures
│   │   │       └── other/         # Specialized cultures
│   │   └── validation/            # 🆕 Culture validation utilities
│   │       ├── __init__.py
│   │       └── culture_validator.py # 🆕 Validate generated cultures against authenticity standards
│   ├── abstractions/              # Interface contracts
│   │   ├── __init__.py
│   │   ├── llm_provider.py        # LLM interface for content generation
│   │   ├── content_generator.py   # Content creation interface (species, classes)
│   │   ├── balance_analyzer.py    # Balance checking interface
│   │   ├── character_validator.py # Character validation interface
│   │   ├── character_repository.py # Character storage interface
│   │   ├── conversation_handler.py # Interactive session interface
│   │   ├── export_service.py      # VTT export interface
│   │   └── culture_llm_provider.py # 🆕 LLM interface contract for culture generation
│   └── exceptions/                # Base exception types
│       ├── __init__.py            # Centralized exception registry
│       ├── base.py                # Base exception classes, ValidationResult
│       ├── generation.py          # Content generation errors, LLM failures
│       ├── balance.py             # Balance validation errors, rule violations
│       ├── workflow.py            # Use case errors, workflow state errors
│       ├── export.py              # Export/conversion errors, VTT format issues
│       ├── persistence.py         # Database errors, repository failures
│       ├── integration.py         # External service errors, API failures
│       └── culture.py             # 🆕 Culture generation errors, authenticity violations
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
│   │   ├── lore_generator.py      # Generate history/lore for custom content
│   │   └── dynamic_culture_service.py # 🆕 Culture generation business logic
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
│   │   │   ├── export_requests.py # Export format requests
│   │   │   └── culture_generation_requests.py # 🆕 Culture generation request DTOs
│   │   └── responses/             # Response DTOs
│   │       ├── __init__.py
│   │       ├── character_response.py # Character data responses
│   │       ├── generation_response.py # Generation status responses
│   │       ├── validation_response.py # Validation results
│   │       ├── conversation_response.py # Interactive session responses
│   │       ├── export_response.py # Export results
│   │       └── culture_generation_responses.py # 🆕 Culture generation response DTOs
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
│   │   │   ├── validate_balance.py # Balance validation pipeline
│   │   │   ├── generate_custom_culture.py # 🆕 Culture generation business logic orchestration
│   │   │   └── analyze_character_request.py # 🆕 Parse user intent for cultural elements
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
│       ├── workflow_coordinator.py # Overall workflow management
│       └── culture_orchestrator.py # 🆕 Culture generation coordination
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
    │   ├── prompt_manager.py      # Prompt template management
    │   ├── culture_llm_service.py # 🆕 LLM provider implementation for culture generation
    │   ├── openai_culture_client.py # 🆕 OpenAI implementation for culture generation
    │   └── claude_culture_client.py # 🆕 Claude implementation for culture generation
    ├── repositories/              # Data access implementations
    │   ├── __init__.py
    │   ├── character_repository.py # Character storage (JSON files, database)
    │   ├── conversation_repository.py # Conversation state storage
    │   ├── content_repository.py  # Custom content storage and retrieval
    │   ├── template_repository.py # Character sheet templates
    │   ├── cache_repository.py    # Caching layer for expensive operations
    │   └── culture_repository.py  # 🆕 Culture storage and retrieval
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
    ├── cache/                     # 🆕 Caching implementations
    │   ├── __init__.py
    │   └── culture_cache.py       # 🆕 Cache generated cultures
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

## Culture Generation System Integration

### 🆕 **New Files Added for Culture Generation**

#### Core Layer (`/core/`)
- **`culture_types.py`** - Culture generation type definitions and authenticity levels
- **`culture_prompts.py`** - Culture generation prompt templates and research guidelines  
- **`cultures/culture_generator.py`** - Core culture generation logic (LLM-independent)
- **`cultures/prompt_templates.py`** - Prompt engineering templates for culture generation
- **`cultures/culture_parser.py`** - Parse LLM responses into BaseCulture structures
- **`validation/culture_validator.py`** - Validate generated cultures against authenticity standards
- **`abstractions/culture_llm_provider.py`** - LLM interface contract for culture generation
- **`exceptions/culture.py`** - Culture generation errors and authenticity violations

#### Domain Layer (`/domain/`)
- **`services/dynamic_culture_service.py`** - Culture generation business logic

#### Application Layer (`/application/`)
- **`dtos/requests/culture_generation_requests.py`** - Culture generation request DTOs
- **`dtos/responses/culture_generation_responses.py`** - Culture generation response DTOs  
- **`use_cases/generation/generate_custom_culture.py`** - Culture generation orchestration
- **`use_cases/generation/analyze_character_request.py`** - Parse user intent for cultural elements
- **`services/culture_orchestrator.py`** - Culture generation coordination

#### Infrastructure Layer (`/infrastructure/`)
- **`llm/culture_llm_service.py`** - LLM provider implementation for culture generation
- **`llm/openai_culture_client.py`** - OpenAI implementation for culture generation
- **`llm/claude_culture_client.py`** - Claude implementation for culture generation
- **`repositories/culture_repository.py`** - Culture storage and retrieval
- **`cache/culture_cache.py`** - Cache generated cultures

### ✅ **Enhanced Existing Files**

#### Core Layer
- **`text_processing.py`** - Enhanced with culture-agnostic utilities for name generation and validation

#### Application Layer
- **LLM workflow integration** - Culture generation integrates with existing character creation pipeline

### 🎯 **Architecture Compliance**

All culture generation additions follow your established Clean Architecture patterns:

- **Layer Separation**: Core defines interfaces, Infrastructure implements them
- **Dependency Inversion**: No inward dependencies
- **Single Responsibility**: Each file has one clear purpose  
- **Infrastructure Independence**: Core/Domain layers remain pure
- **Testability**: Each component can be tested independently

This architecture enhancement maintains your existing structure while adding the powerful capability of AI-generated cultures that can create any cultural naming system on-demand from user prompts.