#!/usr/bin/env python3
"""
Test script for TASK 1: Core Architecture and Enums
Tests the basic factory structure and configuration system.
"""

import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend_campaign')

try:
    from src.services.creation_factory import (
        CampaignCreationFactory,
        CampaignCreationOptions,
        CampaignCreationConfig,
        create_campaign_factory
    )
    from src.services.generators import CampaignGeneratorFactory
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)

class MockLLMService:
    """Mock LLM service for testing."""
    
    async def generate_content(self, prompt: str, max_tokens: int = 500, temperature: float = 0.8) -> str:
        return f"Mock response for: {prompt[:50]}..."

def test_enum_options():
    """Test that all required campaign creation options are available."""
    print("=== Testing CampaignCreationOptions Enum ===")
    
    expected_options = [
        "CAMPAIGN_FROM_SCRATCH",
        "CAMPAIGN_SKELETON", 
        "CHAPTER_CONTENT",
        "ITERATIVE_REFINEMENT",
        "ADAPTIVE_CONTENT",
        "PSYCHOLOGICAL_EXPERIMENT",
        "SETTING_THEME",
        "NPC_FOR_CAMPAIGN",
        "MONSTER_FOR_CAMPAIGN",
        "EQUIPMENT_FOR_CAMPAIGN"
    ]
    
    available_options = [opt.name for opt in CampaignCreationOptions]
    
    for expected in expected_options:
        if expected in available_options:
            print(f"✓ {expected}")
        else:
            print(f"✗ Missing: {expected}")
    
    print(f"\nTotal options available: {len(available_options)}")
    return len(expected_options) == len(set(expected_options).intersection(set(available_options)))

def test_factory_initialization():
    """Test factory initialization with and without LLM service."""
    print("\n=== Testing Factory Initialization ===")
    
    # Test without LLM service
    try:
        factory1 = CampaignCreationFactory()
        print("✓ Factory initialized without LLM service")
    except Exception as e:
        print(f"✗ Factory initialization failed without LLM: {e}")
        return False
    
    # Test with mock LLM service
    try:
        mock_llm = MockLLMService()
        factory2 = CampaignCreationFactory(mock_llm)
        print("✓ Factory initialized with LLM service")
    except Exception as e:
        print(f"✗ Factory initialization failed with LLM: {e}")
        return False
    
    # Test convenience function
    try:
        factory3 = create_campaign_factory(mock_llm)
        print("✓ Factory created via convenience function")
    except Exception as e:
        print(f"✗ Convenience function failed: {e}")
        return False
    
    return True

def test_configuration_system():
    """Test that all creation types have proper configurations."""
    print("\n=== Testing Configuration System ===")
    
    mock_llm = MockLLMService()
    factory = CampaignCreationFactory(mock_llm)
    
    success_count = 0
    total_count = 0
    
    for option in CampaignCreationOptions:
        total_count += 1
        try:
            config = factory.get_config(option)
            
            # Validate config structure
            assert hasattr(config, 'primary_generator')
            assert hasattr(config, 'secondary_generators')
            assert hasattr(config, 'backend_integrations')
            assert hasattr(config, 'performance_timeout')
            assert hasattr(config, 'requires_llm')
            assert hasattr(config, 'supports_refinement')
            
            print(f"✓ {option.value}: {config.primary_generator} (timeout: {config.performance_timeout}s)")
            success_count += 1
            
        except Exception as e:
            print(f"✗ {option.value}: {e}")
    
    print(f"\nConfigurations tested: {success_count}/{total_count}")
    return success_count == total_count

async def test_factory_methods():
    """Test factory methods for proper error handling."""
    print("\n=== Testing Factory Method Signatures ===")
    
    mock_llm = MockLLMService()
    factory = CampaignCreationFactory(mock_llm)
    
    # Test create_from_scratch method signature
    try:
        # This should fail with NotImplementedError since we haven't implemented the methods yet
        result = await factory.create_from_scratch(
            CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH,
            "A test concept for a fantasy campaign"
        )
        print("✗ create_from_scratch should have raised NotImplementedError")
        return False
    except NotImplementedError as e:
        print(f"✓ create_from_scratch raises NotImplementedError as expected: {str(e)[:50]}...")
    except Exception as e:
        print(f"✗ create_from_scratch raised unexpected error: {e}")
        return False
    
    # Test evolve_existing method signature
    try:
        result = await factory.evolve_existing(
            CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH,
            {"test": "data"},
            "Make it more exciting"
        )
        print("✗ evolve_existing should have raised NotImplementedError")
        return False
    except NotImplementedError as e:
        print(f"✓ evolve_existing raises NotImplementedError as expected: {str(e)[:50]}...")
    except Exception as e:
        print(f"✗ evolve_existing raised unexpected error: {e}")
        return False
    
    return True

async def test_health_status():
    """Test factory health status functionality."""
    print("\n=== Testing Health Status ===")
    
    mock_llm = MockLLMService()
    factory = CampaignCreationFactory(mock_llm)
    
    try:
        health = await factory.get_factory_health_status()
        
        # Validate health status structure
        expected_keys = ["factory_type", "performance_stats", "llm_service_status", "supported_creation_types"]
        for key in expected_keys:
            if key in health:
                print(f"✓ Health status includes {key}")
            else:
                print(f"✗ Health status missing {key}")
                return False
        
        print(f"✓ Factory type: {health['factory_type']}")
        print(f"✓ LLM status: {health['llm_service_status']}")
        print(f"✓ Supported types: {len(health['supported_creation_types'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Health status check failed: {e}")
        return False

async def main():
    """Run all TASK 1 tests."""
    print("Testing TASK 1: Core Architecture and Enums")
    print("=" * 50)
    
    results = []
    
    # Test enum options
    results.append(test_enum_options())
    
    # Test factory initialization
    results.append(test_factory_initialization())
    
    # Test configuration system
    results.append(test_configuration_system())
    
    # Test factory methods (async)
    results.append(await test_factory_methods())
    
    # Test health status (async)
    results.append(await test_health_status())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"TASK 1 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ TASK 1: Core Architecture and Enums - COMPLETE")
        print("\nReady to proceed to TASK 2: Campaign Generation from Scratch")
    else:
        print("✗ TASK 1: Some tests failed")
        print("Fix issues before proceeding to TASK 2")

if __name__ == "__main__":
    asyncio.run(main())
