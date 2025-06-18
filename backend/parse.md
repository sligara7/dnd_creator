<!-- Looking at this massive script, I'll break it down using clean architecture principles. Here's how to separate it into modular, maintainable components: -->

## **1. `core_models.py`**
**Domain entities and core business logic**
- **Classes**: `ProficiencyLevel`, `AbilityScoreSource`, `AbilityScore`, `ASIManager`, `CharacterLevelManager`, `MagicItemManager`
- **Purpose**: Core D&D mechanics, ability scores, ASI management, leveling systems
- **Dependencies**: None (pure domain logic)

## **2. `custom_content_models.py`**
**Custom D&D content domain models**
- **Classes**: `CustomSpecies`, `CustomClass`, `CustomItem`, `CustomSpell`, `CustomWeapon`, `CustomArmor`, `CustomFeat`, `FeatManager`, `ContentRegistry`
- **Purpose**: All custom content creation and management for species, classes, items, spells, weapons, armor, and feats
- **Dependencies**: `core_models.py`

## **3. `character_models.py`**
**Character sheet and data models**
- **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`, `CharacterIterationCache`
- **Purpose**: Character data structures, hit points, equipment, calculated statistics
- **Dependencies**: `core_models.py`

## **4. `ability_management.py`**
**Advanced ability score progression system**
- **Classes**: `AbilityScoreManager`, `LevelUpManager`, `CustomSpeciesAbilityManager`, `CustomClassAbilityManager`, `EnhancedAbilityScore`, `EnhancedCharacterCore`
- **Functions**: `enhance_character_data_with_ability_details`, `create_leveling_interface`, `example_character_leveling`
- **Purpose**: Enhanced ability score tracking, ASI progression, multiclassing effects, custom content ability interactions
- **Dependencies**: `core_models.py`, `custom_content_models.py`, `character_models.py`

## **5. `llm_services.py`**
**Infrastructure layer for AI services**
- **Classes**: `LLMService` (abstract), `OllamaLLMService`
- **Functions**: `create_character_service`, `check_ollama_setup`
- **Purpose**: AI service abstraction, Ollama integration, connection management
- **Dependencies**: None (infrastructure layer)

## **6. `generators.py`**
**Application services for content generation**
- **Classes**: `BackstoryGenerator`, `CustomContentGenerator`, `EnhancedCustomContentGenerator`
- **Purpose**: AI-powered generation of backstories, custom species/classes/items/spells
- **Dependencies**: `llm_services.py`, `custom_content_models.py`

## **7. `character_creation.py`**
**Application services for character creation workflow**
- **Classes**: `CreationConfig`, `CreationResult`, `CharacterValidator`, `CharacterDataGenerator`, `AsyncContentGenerator`, `CharacterIterationManager`, `CharacterModifier`, `CharacterCreator`, `EnhancedCharacterCreator`
- **Purpose**: Complete character creation process, iteration management, user interaction workflow
- **Dependencies**: All previous modules

## **8. `validation.py`**
**Data validation and business rules**
- **Functions**: `validate_character_data`, `get_character_stats_summary`, `check_armor_proficiency`, `calculate_character_ac`
- **Purpose**: Character data validation, consistency checking, rule compliance
- **Dependencies**: `character_models.py`

## **9. `formatting.py`**
**Presentation layer for display and output**
- **Functions**: All `format_*` functions including:
  - `format_character_summary`, `format_backstory_only`
  - `format_ability_scores_detailed`, `format_asi_progression`, `format_multiclass_progression`
  - `format_equipment_section`, `format_armor_details`, `format_weapon_details`
  - `format_species_features`, `format_class_features`, `format_feat_opportunities`
  - `format_rest_mechanics_summary`, `enhanced_format_character_summary`
- **Purpose**: All text formatting, display utilities, character sheet presentation
- **Dependencies**: `character_models.py`, `custom_content_models.py`

## **10. `file_operations.py`**
**Infrastructure layer for persistence**
- **Functions**: `save_character`, `load_character`, `save_backstory_as_text`, `export_character_sheet`
- **Purpose**: Saving/loading characters, file management, data persistence
- **Dependencies**: `formatting.py`

## **11. `utilities.py`**
**Shared utilities and helpers**
- **Functions**: `determine_level_from_description`, `get_mastery_description`, utility helper functions
- **Purpose**: Common utilities, helper functions, data processing
- **Dependencies**: None

## **12. `user_interface.py`**
**Presentation layer for user interaction**
- **Functions**: `interactive_character_creation`, user input/output functions
- **Purpose**: User interface, menu system, user interaction
- **Dependencies**: `character_creation.py`, `formatting.py`, `file_operations.py`

## **13. `main.py`**
**Application entry point**
- **Functions**: `main`
- **Purpose**: Application orchestration, dependency injection
- **Dependencies**: `user_interface.py`

## **Clean Architecture Benefits:**

### **Domain Layer** (Inner):
- `core_models.py`, `custom_content_models.py`, `character_models.py`
- Pure business logic, no external dependencies

### **Application Layer** (Middle):
- `ability_management.py`, `generators.py`, `character_creation.py`, `validation.py`
- Use cases and application services

### **Infrastructure Layer** (Outer):
- `llm_services.py`, `file_operations.py`, `formatting.py`, `user_interface.py`
- External concerns like AI services, file I/O, presentation

### **Dependency Flow:**
- Infrastructure → Application → Domain
- No circular dependencies
- Easy to test and modify individual components

### **Import Structure Example:**
```python
# main.py
from user_interface import interactive_character_creation

# user_interface.py  
from character_creation import CharacterCreator
from formatting import format_character_summary

# character_creation.py
from generators import BackstoryGenerator
from character_models import CharacterSheet

# generators.py
from llm_services import LLMService
from custom_content_models import CustomSpecies
```

This structure makes the codebase:
- **Testable**: Each layer can be tested independently
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features or change implementations
- **Readable**: Each file has a single, clear responsibility