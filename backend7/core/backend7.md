# D&D Character Creator - Clean Architecture MVP

## Overview

A minimal viable D&D character creation system built with Clean Architecture principles, focusing on essential functionality while maintaining extensibility and proper separation of concerns.

## Architecture Philosophy

- **Character creation comes first** - All features support the core goal
- **Simple, supportive systems** - No bureaucratic complexity
- **Culture enhances, never restricts** - Optional cultural features for creativity
- **Clean Architecture principles** - Proper dependency inversion and separation

## Project Structure

````bash
# MINIMAL VIABLE D&D CHARACTER CREATOR WORKSPACE
dnd_char_creator/
├── backend7/
│   ├── core/                           # Core domain layer (essential only)
│   │   ├── constants/                  # Essential constants only
│   │   │   ├── __init__.py            # 150 lines - essential constants
│   │   │   ├── dnd_mechanics.py       # 200 lines - core D&D rules
│   │   │   └── character_limits.py    # 150 lines - character creation limits
│   │   ├── enums/                     # Simplified enums
│   │   │   ├── __init__.py           # 400 lines - SIMPLIFIED
│   │   │   ├── game_mechanics.py     # 300 lines - core D&D enums
│   │   │   ├── content_types.py      # 200 lines - content generation
│   │   │   ├── culture_types.py      # 100 lines - SIMPLE culture enums
│   │   │   ├── creativity_levels.py  # 150 lines - generation parameters
│   │   │   ├── balance_levels.py     # 150 lines - validation levels
│   │   │   ├── validation_types.py   # 200 lines - validation framework
│   │   │   ├── progression_types.py  # 150 lines - character progression
│   │   │   ├── export_formats.py     # 200 lines - VTT compatibility
│   │   │   ├── conversation_states.py # 400 lines - workflow states
│   │   │   └── text_types.py         # 150 lines - text processing
│   │   ├── exceptions/               # Simplified exceptions
│   │   │   ├── __init__.py          # 400 lines - SIMPLIFIED
│   │   │   ├── base.py              # 300 lines - base exceptions
│   │   │   ├── culture.py           # 150 lines - SIMPLE culture exceptions
│   │   │   ├── generation.py        # 400 lines - generation errors
│   │   │   ├── balance.py           # 350 lines - balance/validation errors
│   │   │   ├── workflow.py          # 400 lines - workflow errors
│   │   │   ├── export.py            # 300 lines - export errors
│   │   │   ├── persistence.py       # 300 lines - data errors
│   │   │   └── integration.py       # 350 lines - external service errors
│   │   ├── utils/                   # Simplified utilities
│   │   │   ├── __init__.py         # 400 lines - SIMPLIFIED
│   │   │   ├── balance_calculator.py # 300 lines - balance scoring
│   │   │   ├── content_utils.py     # 250 lines - content analysis
│   │   │   ├── naming_validator.py  # 200 lines - name validation
│   │   │   ├── mechanical_parser.py # 300 lines - mechanical elements
│   │   │   ├── rule_checker.py      # 250 lines - D&D rule validation
│   │   │   ├── culture_parser.py    # 200 lines - SIMPLE culture parsing
│   │   │   ├── culture_validator.py # 200 lines - SIMPLE culture validation
│   │   │   └── text_processing.py   # 150 lines - SIMPLE text formatting
│   │   └── __init__.py             # 400 lines - SIMPLIFIED
│   ├── domain/                      # Domain entities and services
│   │   ├── entities/
│   │   │   ├── __init__.py         # 100 lines - entity exports
│   │   │   ├── character.py        # 400 lines - core character entity
│   │   │   ├── ability_scores.py   # 200 lines - ability score value object
│   │   │   ├── background.py       # 150 lines - character background
│   │   │   ├── species.py          # 200 lines - character species
│   │   │   ├── character_class.py  # 300 lines - character class
│   │   │   └── progression.py      # 250 lines - level progression
│   │   ├── services/
│   │   │   ├── __init__.py         # 100 lines - service exports
│   │   │   ├── character_builder.py # 400 lines - character creation service
│   │   │   ├── validation_service.py # 350 lines - validation orchestration
│   │   │   └── level_progression_service.py # 300 lines - leveling service
│   │   └── validators/              # Domain validators using abstract classes
│   │       ├── __init__.py         # 100 lines - validator exports
│   │       ├── core_character_validator.py # 300 lines - core validation
│   │       ├── multiclass_validator.py # 250 lines - multiclassing rules
│   │       └── optimization_validator.py # 200 lines - build optimization
│   ├── application/                 # Use cases and application services
│   │   ├── use_cases/
│   │   │   ├── __init__.py         # 100 lines - use case exports
│   │   │   ├── create_character.py # 300 lines - character creation workflow
│   │   │   ├── create_progression.py # 250 lines - progression workflow
│   │   │   └── validate_character.py # 200 lines - validation workflow
│   │   └── services/
│   │       └── __init__.py         # 50 lines - application service exports
│   ├── infrastructure/              # External systems and adapters
│   │   ├── data/
│   │   │   ├── __init__.py         # 100 lines - data layer exports
│   │   │   ├── character_repository_impl.py # 300 lines - character persistence
│   │   │   └── character_storage.py # 200 lines - file storage
│   │   └── llm/
│   │       ├── __init__.py         # 100 lines - LLM service exports
│   │       └── ollama_llm_service.py # 400 lines - Ollama integration
│   ├── interfaces/                  # User interfaces and external APIs
│   │   ├── cli/
│   │   │   ├── __init__.py         # 50 lines - CLI exports
│   │   │   ├── character_creator_cli.py # 450 lines - main CLI interface
│   │   │   └── cli_utils.py        # 200 lines - CLI formatting utilities
│   │   └── api/                    # Future: REST API
│   │       └── __init__.py         # 50 lines - API placeholder
│   ├── container.py                # 250 lines - dependency injection
│   ├── main.py                     # 100 lines - application entry point
│   └── config.py                   # 150 lines - configuration management
├── tests/                          # Test suites
│   ├── unit/
│   │   ├── core/
│   │   │   ├── test_enums.py       # 300 lines - enum tests
│   │   │   ├── test_utils.py       # 400 lines - utility tests
│   │   │   └── test_exceptions.py  # 250 lines - exception tests
│   │   ├── domain/
│   │   │   ├── test_entities.py    # 400 lines - entity tests
│   │   │   ├── test_services.py    # 350 lines - service tests
│   │   │   └── test_validators.py  # 300 lines - validator tests
│   │   └── application/
│   │       └── test_use_cases.py   # 400 lines - use case tests
│   ├── integration/
│   │   ├── test_character_creation.py # 300 lines - end-to-end character creation
│   │   └── test_validation_flow.py # 250 lines - validation integration
│   └── conftest.py                 # 200 lines - test configuration
├── docs/                           # Documentation
│   ├── README.md                   # Project overview
│   ├── ARCHITECTURE.md             # Architecture decisions
│   ├── SETUP.md                    # Setup instructions
│   └── USAGE.md                    # Usage examples
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
└── .gitignore                      # Git ignore rules
````

## Key Architectural Decisions

### ✅ **Simplified Systems**
- **Single validation system** using domain validators with abstract classes
- **Essential constants only** - no complex validation thresholds
- **Simple culture features** - optional and supportive, never restrictive
- **Essential D&D mechanics** - core rules without bureaucratic overhead

### ✅ **Clean Architecture Layers**

#### **Core Layer** (`core/`)
- **Constants**: Essential D&D rules and character creation limits
- **Enums**: Type-safe enumeration values for all D&D concepts
- **Exceptions**: Hierarchical exception handling with graceful degradation
- **Utils**: Essential utilities for balance, validation, and text processing

#### **Domain Layer** (`domain/`)
- **Entities**: Core business objects (Character, AbilityScores, etc.)
- **Services**: Business logic orchestration
- **Validators**: Domain validation using abstract classes

#### **Application Layer** (`application/`)
- **Use Cases**: Application-specific workflows
- **Services**: Application service coordination

#### **Infrastructure Layer** (`infrastructure/`)
- **Data**: Persistence implementations
- **LLM**: External AI service integration

#### **Interface Layer** (`interfaces/`)
- **CLI**: Command-line interface
- **API**: Future REST API support

### ❌ **Removed Complexity**
- **Legacy validator adapter** - Technical debt with no value
- **Complex culture generation** - Replaced with simple, supportive features
- **Bureaucratic validation** - Replaced with essential rule checking
- **Over-abstraction** - Direct, clean implementations

## Validation Architecture

### **Clean Validation Flow**
```
Character Creation Request
    ↓
Use Case (create_character.py)
    ↓
Domain Service (validation_service.py)
    ↓
Domain Validators (core_character_validator.py)
    ↓
Core Utilities (rule_checker.py)
    ↓
Constants (dnd_mechanics.py)
```

### **Domain Validators** (Using Abstract Classes)
- `core_character_validator.py` - Core D&D rule validation
- `multiclass_validator.py` - Multiclassing requirements
- `optimization_validator.py` - Build optimization suggestions

## Module Size Guidelines

Each module is designed to be **400-500 lines maximum** for maintainability:

- **Large modules are split** into focused sub-modules
- **Related functionality is grouped** logically
- **Clear separation of concerns** between modules
- **Easy to locate and modify** specific functionality

## Core Features

### **Character Creation**
1. **Essential D&D 5e/2024 mechanics**
2. **All official classes and species**
3. **Proper ability score generation**
4. **Equipment and spell assignment**
5. **Level progression support**

### **Simple Culture Support**
1. **Optional cultural name suggestions**
2. **Basic cultural background text**
3. **Never restricts character creation**
4. **Enhances creativity without complexity**

### **Validation System**
1. **Core D&D rule compliance**
2. **Multiclass requirement checking**
3. **Character optimization suggestions**
4. **Graceful error handling**

### **LLM Integration**
1. **Ollama primary support**
2. **Extensible provider system**
3. **Error handling and fallbacks**
4. **Optional AI enhancement**

## Development Priorities

### **Phase 1: Core MVP**
1. Character entity and value objects
2. Basic character creation service
3. Essential D&D rule validation
4. CLI interface
5. File-based character storage

### **Phase 2: Enhanced MVP**
1. Level progression system
2. Multiclass validation
3. LLM integration for descriptions
4. Simple culture features
5. Character optimization suggestions

### **Phase 3: Full Feature Set**
1. Multiple export formats
2. VTT integration
3. REST API
4. Advanced culture generation
5. Campaign management features

## Benefits

### **Maintainability**
- **Clear module boundaries** and responsibilities
- **Consistent code organization** across all layers
- **Easy to locate and modify** specific functionality
- **Comprehensive test coverage** for all components

### **Extensibility**
- **Clean interfaces** for adding new features
- **Modular design** supports independent development
- **Provider pattern** for external services
- **Plugin architecture** for custom content

### **Reliability**
- **Graceful error handling** at all levels
- **Comprehensive validation** without being restrictive
- **Fallback systems** for external dependencies
- **Type safety** through enums and validation

### **Developer Experience**
- **Clear architecture documentation**
- **Consistent naming conventions**
- **Comprehensive type hints**
- **IDE-friendly structure**

This architecture provides a solid foundation for a D&D character creation system that can grow from MVP to full-featured application while maintaining clean code principles and developer productivity.
