#!/usr/bin/env python3
"""
Test script to verify the extensible psychological experiment system.
Tests both predefined and custom psychological experiments.
"""

import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend_campaign')

try:
    from src.services.generators import (
        PsychologicalExperimentType, 
        PsychologicalExperimentGenerator,
        SettingThemeGenerator,
        AdaptiveCampaignGenerator,
        CampaignGenre,
        SettingTheme
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)

class MockLLMService:
    """Mock LLM service for testing without actual API calls."""
    
    async def generate_content(self, prompt: str, max_tokens: int = 500, temperature: float = 0.8) -> str:
        # Return a mock response based on the prompt type
        if "psychological experiment" in prompt.lower():
            return f"""
Mock Psychological Experiment Integration

This is a test response for psychological experiment integration.
The experiment would be naturally woven into D&D scenarios with:
- Clear setup and player choices
- Observable behavior patterns
- Educational value
- Maintained game immersion
- Ethical considerations

This demonstrates the extensible psychology system working correctly.
"""
        elif "custom theme" in prompt.lower():
            return f"""
Mock Custom Theme

This is a test response for custom theme generation.
The theme would include:
- Distinctive atmosphere and mood
- Unique mechanics and features
- Thematic locations and NPCs
- Adventure opportunities
- Visual and narrative elements

This demonstrates the theme extension system working correctly.
"""
        elif "player behavior" in prompt.lower():
            return f"""
Mock Player Analysis

This is a test response for player behavior analysis.
Analysis would include:
- Combat and social preferences
- Problem-solving approaches
- Group dynamics
- Story engagement patterns
- Recommended adaptations

This demonstrates the adaptive system working correctly.
"""
        else:
            return "Mock LLM response for testing purposes."

async def test_predefined_experiments():
    """Test predefined psychological experiments."""
    print("=== Testing Predefined Psychological Experiments ===")
    
    mock_llm = MockLLMService()
    generator = PsychologicalExperimentGenerator(mock_llm)
    
    # Test a few predefined experiments
    experiments_to_test = [
        PsychologicalExperimentType.PRISONERS_DILEMMA,
        PsychologicalExperimentType.CONFORMITY,
        PsychologicalExperimentType.TRUST_RECIPROCITY,
        PsychologicalExperimentType.FRAMING_EFFECTS
    ]
    
    for experiment in experiments_to_test:
        print(f"\nTesting: {experiment.value}")
        try:
            result = await generator.generate_experiment_integration(
                experiment, 
                campaign_context="Fantasy adventure campaign with political intrigue"
            )
            print(f"✓ Successfully generated integration for {experiment.value}")
            print(f"  Source: {result['metadata']['source']}")
            print(f"  Generated at: {result['metadata']['generated_at']}")
        except Exception as e:
            print(f"✗ Error with {experiment.value}: {e}")

async def test_custom_experiment():
    """Test custom psychological experiment generation."""
    print("\n=== Testing Custom Psychological Experiments ===")
    
    mock_llm = MockLLMService()
    generator = PsychologicalExperimentGenerator(mock_llm)
    
    custom_concepts = [
        "emotional contagion in group decision making",
        "moral licensing and subsequent behavior",
        "choice architecture and decision paralysis",
        "social identity and alliance formation"
    ]
    
    for concept in custom_concepts:
        print(f"\nTesting custom concept: {concept}")
        try:
            result = await generator.generate_experiment_integration(
                PsychologicalExperimentType.CUSTOM,
                campaign_context="Medieval fantasy with guild politics",
                custom_concept=concept
            )
            print(f"✓ Successfully generated custom experiment for: {concept}")
            print(f"  Source: {result['metadata']['source']}")
        except Exception as e:
            print(f"✗ Error with custom concept '{concept}': {e}")

async def test_experiment_series():
    """Test psychological experiment series generation."""
    print("\n=== Testing Experiment Series ===")
    
    mock_llm = MockLLMService()
    generator = PsychologicalExperimentGenerator(mock_llm)
    
    try:
        result = await generator.generate_experiment_series(
            theme="leadership and authority in crisis situations",
            experiment_count=4
        )
        print("✓ Successfully generated experiment series")
        print(f"  Theme: {result['theme']}")
        print(f"  Experiment count: {result['experiment_count']}")
        print(f"  Source: {result['metadata']['source']}")
    except Exception as e:
        print(f"✗ Error generating experiment series: {e}")

async def test_theme_generator():
    """Test the setting theme generator."""
    print("\n=== Testing Setting Theme Generator ===")
    
    mock_llm = MockLLMService()
    generator = SettingThemeGenerator(mock_llm)
    
    # Test custom theme generation
    try:
        result = await generator.generate_custom_theme(
            "biopunk genetic revolution",
            CampaignGenre.SCIENCE_FICTION
        )
        print("✓ Successfully generated custom theme")
        print(f"  Theme concept: {result['theme_concept']}")
        print(f"  Genre: {result['genre']}")
    except Exception as e:
        print(f"✗ Error generating custom theme: {e}")
    
    # Test theme enhancement
    try:
        result = await generator.enhance_existing_theme(
            SettingTheme.STEAMPUNK,
            "environmental catastrophe and resource scarcity"
        )
        print("✓ Successfully enhanced existing theme")
        print(f"  Base theme: {result['base_theme']}")
        print(f"  Enhancement: {result['enhancement_concept']}")
    except Exception as e:
        print(f"✗ Error enhancing theme: {e}")

async def test_adaptive_generator():
    """Test the adaptive campaign generator."""
    print("\n=== Testing Adaptive Campaign Generator ===")
    
    mock_llm = MockLLMService()
    generator = AdaptiveCampaignGenerator(mock_llm)
    
    # Mock session data
    session_data = [
        {
            "session_number": 1,
            "combat_actions": "Tactical and coordinated",
            "social_choices": "Diplomatic approach preferred",
            "exploration_behavior": "Methodical and thorough",
            "problem_solving": "Creative solutions sought"
        },
        {
            "session_number": 2,
            "combat_actions": "Ri positioning",
            "social_choices": "Information gathering focus",
            "exploration_behavior": "Cautious advancement",
            "problem_solving": "Collaborative decision making"
        }
    ]
    
    try:
        # Test behavior analysis
        analysis = await generator.analyze_player_behavior(session_data)
        print("✓ Successfully analyzed player behavior")
        print(f"  Sessions analyzed: {analysis['session_count']}")
        
        # Test content adaptation
        original_content = "A dangerous dungeon with traps and monsters awaits exploration."
        adaptation = await generator.generate_adaptive_content(original_content, analysis)
        print("✓ Successfully generated adaptive content")
        print(f"  Original length: {len(adaptation['original_content'])} chars")
        print(f"  Adapted length: {len(adaptation['adapted_content'])} chars")
        
        # Test campaign suggestions
        campaign_data = {"title": "Test Campaign", "description": "A sample campaign for testing"}
        feedback = ["More social encounters please", "Combat feels too easy"]
        suggestions = await generator.suggest_campaign_adjustments(campaign_data, feedback)
        print("✓ Successfully generated campaign suggestions")
        print(f"  Campaign: {suggestions['campaign_title']}")
        
    except Exception as e:
        print(f"✗ Error in adaptive generator: {e}")

def test_enum_extensibility():
    """Test that the psychological experiment enum is properly extensible."""
    print("\n=== Testing Enum Extensibility ===")
    
    print("Available psychological experiment types:")
    for exp_type in PsychologicalExperimentType:
        print(f"  - {exp_type.value}: {exp_type.name}")
    
    # Verify CUSTOM option is available
    assert PsychologicalExperimentType.CUSTOM in PsychologicalExperimentType
    print("✓ CUSTOM experiment type is available")
    
    # Verify new experiment types are available
    new_experiments = [
        PsychologicalExperimentType.PRISONERS_DILEMMA,
        PsychologicalExperimentType.LOSS_AVERSION,
        PsychologicalExperimentType.IN_GROUP_OUT_GROUP,
        PsychologicalExperimentType.CONFIRMATION_BIAS
    ]
    
    for exp in new_experiments:
        assert exp in PsychologicalExperimentType
        print(f"✓ {exp.value} is available")
    
    print(f"\nTotal experiment types available: {len(list(PsychologicalExperimentType))}")

async def main():
    """Run all tests."""
    print("Testing Extensible Psychological Experiment System")
    print("=" * 50)
    
    # Test enum extensibility (synchronous)
    test_enum_extensibility()
    
    # Test async functionality
    await test_predefined_experiments()
    await test_custom_experiment()
    await test_experiment_series()
    await test_theme_generator()
    await test_adaptive_generator()
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
