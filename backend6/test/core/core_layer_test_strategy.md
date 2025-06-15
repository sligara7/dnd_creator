# Core Layer Testing Approach

## Overview

The core layer (`/backend6/core/__init__.py`) provides comprehensive interfaces for testing all functionality independently from other layers. This document outlines a systematic approach to test all core layer features using the provided interfaces.

## Testing Architecture

### Primary Testing Interfaces

1. **`CoreLayerInterface`** - Main interface for domain integration testing
2. **`CoreTestingInterface`** - Specialized interface for comprehensive component testing
3. **Module validation functions** - Built-in integrity checking

## Testing Strategy by Component Category

### 1. Enum System Testing (`test_enums/`)

#### 1.1 Culture Generation Enums
```python
# Test all culture generation enums
from backend6.core import CoreTestingInterface

def test_culture_generation_enums():
    testable = CoreTestingInterface.get_testable_components()
    culture_enums = testable['enum_systems']['culture_generation']
    
    for enum_class in culture_enums:
        # Test enum completeness
        assert len(enum_class) > 0
        # Test enum values are unique
        values = [item.value for item in enum_class]
        assert len(values) == len(set(values))
        # Test string representation
        for item in enum_class:
            assert str(item) is not None
```

#### 1.2 Enum Utility Functions
```python
def test_enum_utility_functions():
    from backend6.core import (
        calculate_character_generation_score,
        suggest_creative_culture_enhancements,
        get_optimal_authenticity_for_characters
    )
    
    # Test character generation scoring
    score = calculate_character_generation_score(
        authenticity_level=CultureAuthenticityLevel.GAMING_OPTIMIZED,
        creativity_level=CultureCreativityLevel.MODERATE
    )
    assert isinstance(score, (int, float))
    assert 0 <= score <= 100
```

### 2. Culture Generation System Testing (`test_cultures/`)

#### 2.1 Enhanced Culture Generator Testing
```python
def test_enhanced_culture_generator():
    capabilities = CoreLayerInterface.get_culture_generation_capabilities()
    generator_class = capabilities['generators']['enhanced_creative']
    
    # Test generator instantiation
    generator = generator_class()
    assert generator is not None
    
    # Test spec creation
    from backend6.core import create_character_culture_spec_enhanced
    spec = create_character_culture_spec_enhanced(
        culture_type=CultureGenerationType.FANTASY_INSPIRED,
        authenticity_level=CultureAuthenticityLevel.MODERATE,
        character_count=3
    )
    assert spec is not None
    assert spec.character_count == 3
```

#### 2.2 Culture Parsing Testing
```python
def test_culture_parsing():
    capabilities = CoreLayerInterface.get_culture_generation_capabilities()
    parser_class = capabilities['parsers']['enhanced_creative']
    
    # Test parser with sample culture data
    parser = parser_class()
    sample_culture = """
    Culture: Sky Nomads
    Names: Aeliana (female), Theron (male), Zephyr (neutral)
    Traditions: Wind ceremonies, Cloud reading
    """
    
    from backend6.core import parse_for_characters_enhanced
    result = parse_for_characters_enhanced(sample_culture)
    
    assert result is not None
    assert len(result.character_names) > 0
    assert result.culture_name == "Sky Nomads"
```

### 3. Validation System Testing (`test_validation/`)

#### 3.1 Culture Validation Testing
```python
def test_culture_validation():
    validation_caps = CoreLayerInterface.get_validation_capabilities()
    
    # Test character culture validation
    from backend6.core import validate_culture_for_characters
    
    sample_culture = EnhancedCreativeCulture(
        name="Test Culture",
        character_names=["Alice", "Bob", "Charlie"],
        traditions=["Storytelling", "Crafting"],
        social_structure="Egalitarian"
    )
    
    result = validate_culture_for_characters(sample_culture)
    assert result is not None
    assert hasattr(result, 'is_valid')
    assert hasattr(result, 'issues')
```

#### 3.2 Enhancement Suggestion Testing
```python
def test_enhancement_suggestions():
    from backend6.core import get_culture_enhancement_suggestions_enhanced
    
    basic_culture = EnhancedCreativeCulture(
        name="Basic Culture",
        character_names=["Name1", "Name2"]
    )
    
    suggestions = get_culture_enhancement_suggestions_enhanced(
        basic_culture,
        target_categories=[CultureEnhancementCategory.CHARACTER_NAMES]
    )
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
```

### 4. LLM Provider Abstraction Testing (`test_providers/`)

#### 4.1 Provider Interface Testing
```python
def test_provider_interfaces():
    provider_abstractions = CoreLayerInterface.get_llm_provider_abstractions()
    
    # Test base provider interface
    base_provider = provider_abstractions['base_providers']['culture_llm']
    
    # Test interface compliance (abstract methods)
    import inspect
    abstract_methods = [
        name for name, method in inspect.getmembers(base_provider)
        if getattr(method, '__isabstractmethod__', False)
    ]
    
    expected_methods = ['generate_culture', 'validate_response']
    for method in expected_methods:
        assert method in [m for m in dir(base_provider) if not m.startswith('_')]
```

#### 4.2 Request/Response Structure Testing
```python
def test_request_response_structures():
    provider_abstractions = CoreLayerInterface.get_llm_provider_abstractions()
    
    # Test generation request
    request_class = provider_abstractions['request_structures']['generation_request']
    
    from backend6.core import create_character_focused_culture_request
    request = create_character_focused_culture_request(
        culture_type=CultureGenerationType.ORIGINAL,
        character_count=4,
        authenticity_level=CultureAuthenticityLevel.MODERATE
    )
    
    assert isinstance(request, request_class)
    assert request.character_count == 4
```

### 5. Text Processing Testing (`test_text_processing/`)

#### 5.1 Enhanced Text Analysis Testing
```python
def test_enhanced_text_analysis():
    text_capabilities = CoreLayerInterface.get_text_processing_capabilities()
    
    from backend6.core import analyze_text_content_enhanced
    
    sample_text = """
    The Sky Nomads are a proud people who ride the wind currents 
    between floating islands. Their names often reflect elements 
    of air and freedom: Aeliana, Theron, Zephyr.
    """
    
    analysis = analyze_text_content_enhanced(sample_text)
    
    assert analysis is not None
    assert hasattr(analysis, 'complexity_score')
    assert hasattr(analysis, 'cultural_references')
    assert hasattr(analysis, 'fantasy_terms')
```

#### 5.2 Cultural Reference Extraction Testing
```python
def test_cultural_reference_extraction():
    from backend6.core import extract_cultural_references_enhanced
    
    text_with_culture = """
    The Eldari maintain ancient libraries and practice meditation.
    Their naming convention follows celestial patterns.
    """
    
    references = extract_cultural_references_enhanced(text_with_culture)
    
    assert isinstance(references, list)
    # Should detect cultural elements like "ancient libraries", "meditation"
    assert len(references) > 0
```

### 6. Traditional Utility Testing (`test_utils/`)

#### 6.1 Balance Calculator Testing
```python
def test_balance_calculator():
    from backend6.core import (
        calculate_overall_balance_score,
        calculate_power_level_score,
        create_balance_metrics
    )
    
    # Test with sample D&D content
    sample_feature = {
        'damage_dice': '2d8',
        'usage': 'short_rest',
        'range': 60,
        'area_effect': 'line'
    }
    
    balance_score = calculate_overall_balance_score(sample_feature)
    assert isinstance(balance_score, (int, float))
    assert 0 <= balance_score <= 100
```

#### 6.2 Mechanical Parser Testing
```python
def test_mechanical_parser():
    from backend6.core import (
        extract_mechanical_elements,
        parse_damage_expression,
        MechanicalElement
    )
    
    spell_text = """
    Range: 120 feet
    Damage: 3d6 fire damage
    Duration: Instantaneous
    Components: V, S, M
    """
    
    elements = extract_mechanical_elements(spell_text)
    assert isinstance(elements, list)
    assert any(elem.category == 'damage' for elem in elements)
    
    damage_result = parse_damage_expression('3d6+2')
    assert damage_result is not None
```

### 7. Integration Testing (`test_integration/`)

#### 7.1 Culture System Workflow Testing
```python
def test_culture_generation_workflow():
    """Test complete culture generation workflow"""
    
    # 1. Create specification
    from backend6.core import create_character_culture_spec_enhanced
    spec = create_character_culture_spec_enhanced(
        culture_type=CultureGenerationType.FANTASY_INSPIRED,
        authenticity_level=CultureAuthenticityLevel.MODERATE,
        character_count=3
    )
    
    # 2. Generate culture (mock LLM response)
    mock_response = """
    Culture: Mountain Clans
    Character Names: Thorek (male), Daina (female), Kael (neutral)
    Traditions: Stone carving, Ancestor worship
    """
    
    # 3. Parse response
    from backend6.core import parse_for_characters_enhanced
    parsed = parse_for_characters_enhanced(mock_response)
    
    # 4. Validate result
    from backend6.core import validate_culture_for_characters
    validation = validate_culture_for_characters(parsed.culture)
    
    # 5. Get enhancement suggestions
    from backend6.core import get_culture_enhancement_suggestions_enhanced
    suggestions = get_culture_enhancement_suggestions_enhanced(parsed.culture)
    
    # Assert workflow completion
    assert spec is not None
    assert parsed is not None
    assert validation is not None
    assert suggestions is not None
```

#### 7.2 Enum-Utility Integration Testing
```python
def test_enum_utility_integration():
    """Test integration between enums and utility functions"""
    
    integration_points = CoreTestingInterface.get_integration_test_points()
    enum_integration = integration_points['enum_utility_integration']
    
    # Test culture generation scoring with enums
    scoring_func = enum_integration['culture_generation_scoring']
    score = scoring_func(
        authenticity_level=CultureAuthenticityLevel.GAMING_OPTIMIZED,
        creativity_level=CultureCreativityLevel.HIGH,
        complexity_level=CultureComplexityLevel.SIMPLE
    )
    
    assert isinstance(score, (int, float))
    
    # Test enhancement suggestions with enums
    suggestion_func = enum_integration['enhancement_suggestions']
    suggestions = suggestion_func(
        current_authenticity=CultureAuthenticityLevel.LOW,
        target_authenticity=CultureAuthenticityLevel.MODERATE
    )
    
    assert isinstance(suggestions, list)
```

## Test Organization Structure

```
test/core/
├── test_enums/
│   ├── test_culture_enums.py
│   ├── test_game_mechanic_enums.py
│   ├── test_validation_enums.py
│   └── test_enum_utilities.py
├── test_cultures/
│   ├── test_enhanced_generator.py
│   ├── test_enhanced_parser.py
│   ├── test_prompt_templates.py
│   └── test_culture_orchestrator.py
├── test_validation/
│   ├── test_enhanced_validator.py
│   ├── test_validation_functions.py
│   └── test_validation_presets.py
├── test_providers/
│   ├── test_provider_interfaces.py
│   ├── test_request_structures.py
│   └── test_provider_utilities.py
├── test_text_processing/
│   ├── test_enhanced_analysis.py
│   ├── test_cultural_extraction.py
│   └── test_text_utilities.py
├── test_utils/
│   ├── test_balance_calculator.py
│   ├── test_mechanical_parser.py
│   ├── test_content_utils.py
│   └── test_rule_checker.py
├── test_integration/
│   ├── test_culture_workflow.py
│   ├── test_enum_integration.py
│   └── test_provider_integration.py
└── test_core_integrity.py
```

## Test Execution Strategy

### 1. Unit Tests
- Test individual components in isolation
- Use mocking for external dependencies
- Focus on pure functions and data structures

### 2. Integration Tests
- Test component interactions
- Validate workflow completeness
- Test enum-utility integrations

### 3. Interface Compliance Tests
- Validate abstract interface implementations
- Test provider abstraction compliance
- Verify data structure contracts

### 4. Performance Tests
- Test enum lookup performance
- Validate memory usage for large datasets
- Test concurrent access safety

## Continuous Testing Approach

### 1. Core Integrity Validation
```python
def test_core_layer_integrity():
    from backend6.core import validate_core_layer_integrity
    
    integrity_report = validate_core_layer_integrity()
    
    assert integrity_report['overall_status'] in ['valid', 'valid_with_warnings']
    
    if integrity_report['overall_status'] == 'invalid':
        pytest.fail(f"Core layer integrity failed: {integrity_report['issues']}")
```

### 2. Interface Availability Testing
```python
def test_interface_availability():
    # Test CoreLayerInterface methods
    capabilities = CoreLayerInterface.get_culture_generation_capabilities()
    assert capabilities is not None
    
    # Test CoreTestingInterface methods
    testable = CoreTestingInterface.get_testable_components()
    assert testable is not None
    
    # Test all major functional areas
    required_areas = [
        'enum_systems', 'pure_functions', 
        'data_structures', 'abstract_interfaces'
    ]
    
    for area in required_areas:
        assert area in testable
```

### 3. Feature Completeness Testing
```python
def test_feature_completeness():
    from backend6.core import ENHANCED_FEATURE_MATRIX
    
    # Validate all features are marked as complete or enhanced
    for category, features in ENHANCED_FEATURE_MATRIX.items():
        for feature_name, feature_info in features.items():
            assert feature_info['status'] in ['complete', 'enhanced']
            assert 'coverage' in feature_info
```

## Testing Best Practices

1. **Use Core Interfaces**: Always use `CoreLayerInterface` and `CoreTestingInterface` for accessing core functionality
2. **Test Independence**: Ensure core layer tests run independently from domain/application layers
3. **Mock External Dependencies**: Use mocking for any external services (LLM providers, file systems)
4. **Validate Compliance**: Regularly test architectural compliance and feature completeness
5. **Performance Monitoring**: Include performance benchmarks for critical operations
6. **Integration Validation**: Test complete workflows to ensure component integration works correctly

This comprehensive testing approach ensures all core layer features are thoroughly validated while maintaining the independence and integrity of the core domain layer.