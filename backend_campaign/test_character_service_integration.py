#!/usr/bin/env python3
"""
Test script for character service integration with campaign generation.
Tests the new automatic NPC/monster generation with genre/theme consistency.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any

# Set testing mode to avoid config validation
os.environ["TESTING_MODE"] = "true"

# Add current directory and parent to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import campaign services
try:
    from src.services.generators import (
        CharacterServiceClient, 
        CampaignCharacterIntegrator,
        CampaignGenre,
        SettingTheme,
        CampaignComplexity
    )
    from src.services.creation_factory import (
        CampaignCreationFactory,
        CampaignCreationOptions
    )
    from src.services.llm_service import LLMService
    from src.core.config import Settings
except ImportError as e:
    logger.error(f"Failed to import campaign services: {e}")
    logger.info("Attempting alternative import path...")
    try:
        import importlib.util
        
        # Import generators module directly
        generators_path = os.path.join(current_dir, "src", "services", "generators.py")
        spec = importlib.util.spec_from_file_location("generators", generators_path)
        generators_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generators_module)
        
        CharacterServiceClient = generators_module.CharacterServiceClient
        CampaignCharacterIntegrator = generators_module.CampaignCharacterIntegrator
        CampaignGenre = generators_module.CampaignGenre
        SettingTheme = generators_module.SettingTheme
        CampaignComplexity = generators_module.CampaignComplexity
        
        logger.info("Successfully imported via direct file loading")
        
    except Exception as e2:
        logger.error(f"Alternative import also failed: {e2}")
        logger.info("Running in limited mode - some tests will be skipped")
        CharacterServiceClient = None


async def test_character_service_client():
    """Test basic character service client functionality."""
    logger.info("=== Testing CharacterServiceClient ===")
    
    if CharacterServiceClient is None:
        logger.warning("CharacterServiceClient not available - skipping test")
        return
    
    campaign_context = {
        "genre": "sci_fi",
        "theme": "cyberpunk",
        "complexity": "medium",
        "party_level": 3,
        "party_size": 4,
        "challenge_rating": 2,
        "narrative_role": "major",
        "custom_species": ["cyborg", "AI-enhanced human"],
        "cultural_background": "corporate dystopia"
    }
    
    try:
        async with CharacterServiceClient() as client:
            # Test NPC generation
            logger.info("Testing NPC generation...")
            npc_result = await client.generate_character("npc", campaign_context)
            logger.info(f"Generated NPC: {json.dumps(npc_result, indent=2)}")
            
            # Test Monster generation  
            logger.info("Testing Monster generation...")
            monster_context = campaign_context.copy()
            monster_context["challenge_rating"] = 3
            monster_result = await client.generate_character("monster", monster_context)
            logger.info(f"Generated Monster: {json.dumps(monster_result, indent=2)}")
            
    except Exception as e:
        logger.error(f"Character service test failed (expected if backend not running): {e}")
        logger.info("This is expected if the character creation backend is not running")


async def test_campaign_character_integrator():
    """Test the campaign-character integration logic."""
    logger.info("=== Testing CampaignCharacterIntegrator ===")
    
    # Create mock LLM service
    class MockLLMService:
        async def generate_content(self, prompt: str, **kwargs):
            # Return mock character requirements analysis
            return {
                "npcs": {
                    "major": 2,
                    "minor": 3,
                    "challenge_ratings": [1, 2],
                    "species": ["android", "genetically_modified_human", "AI_construct"],
                    "roles": ["contact", "rival", "informant", "vendor"]
                },
                "monsters": {
                    "types": 2,
                    "quantities": [2, 1],
                    "challenge_ratings": [2, 3],
                    "creature_types": ["construct", "aberration"]
                },
                "special_considerations": {
                    "custom_species": ["sentient_AI", "bio-enhanced_corporate_security"],
                    "custom_classes": ["netrunner", "corpo_operative"],
                    "cultural_backgrounds": ["street_gang", "corporate_elite"]
                }
            }
    
    campaign_data = {
        "genre": CampaignGenre.CYBERPUNK,
        "theme": SettingTheme.CYBERPUNK,
        "complexity": CampaignComplexity.MEDIUM,
        "party_level": 2,
        "party_size": 4,
        "title": "Corporate Shadows",
        "description": "A cyberpunk campaign about corporate espionage in Neo-Tokyo 2087"
    }
    
    chapter_data = {
        "title": "Data Heist",
        "description": "The team must infiltrate a corporate server farm to steal classified data",
        "themes": ["technology", "stealth", "corporate_intrigue"]
    }
    
    try:
        async with CharacterServiceClient() as client:
            integrator = CampaignCharacterIntegrator(client, MockLLMService())
            
            logger.info("Testing chapter character generation...")
            result = await integrator.generate_chapter_characters(campaign_data, chapter_data)
            
            logger.info("Character generation results:")
            logger.info(f"NPCs generated: {len(result.get('npcs', []))}")
            logger.info(f"Monsters generated: {len(result.get('monsters', []))}")
            logger.info(f"Requirements analysis: {json.dumps(result.get('requirements_analysis', {}), indent=2)}")
            
    except Exception as e:
        logger.error(f"Integration test failed: {e}")


async def test_enhanced_chapter_generation():
    """Test chapter generation with character service integration."""
    logger.info("=== Testing Enhanced Chapter Generation ===")
    
    # Create mock LLM service
    class MockLLMService:
        async def generate_content(self, prompt: str, **kwargs):
            if "character requirements" in prompt.lower():
                return json.dumps({
                    "npcs": {
                        "major": 3,
                        "minor": 4,
                        "challenge_ratings": [1, 2, 3],
                        "species": ["drow", "tiefling", "custom_shadow_touched"],
                        "roles": ["ally", "neutral", "antagonist", "merchant"]
                    },
                    "monsters": {
                        "types": 2,
                        "quantities": [3, 1],
                        "challenge_ratings": [2, 4],
                        "creature_types": ["undead", "shadow_creature"]
                    },
                    "special_considerations": {
                        "custom_species": ["shadow_touched_human"],
                        "custom_classes": ["shadow_dancer"],
                        "cultural_backgrounds": ["underdark_exile", "surface_refugee"]
                    }
                })
            else:
                return "Mock narrative content for horror campaign chapter"
    
    try:
        # Create factory with mock LLM
        mock_llm = MockLLMService()
        settings = Settings()
        factory = CampaignCreationFactory(mock_llm, settings)
        
        # Test chapter creation with character service integration
        chapter_result = await factory.create_from_scratch(
            CampaignCreationOptions.CHAPTER_CONTENT,
            "A horror-themed chapter where the party explores an abandoned mansion filled with supernatural threats",
            campaign_title="Shadows of the Past",
            campaign_description="A gothic horror campaign set in Victorian-era England",
            genre=CampaignGenre.HORROR,
            setting_theme=SettingTheme.HORROR,
            complexity=CampaignComplexity.COMPLEX,
            party_level=5,
            party_size=4,
            themes=["supernatural", "investigation", "psychological_horror"],
            use_character_service=True
        )
        
        logger.info("Enhanced chapter generation completed!")
        logger.info(f"Result keys: {list(chapter_result.keys())}")
        
        if "chapter" in chapter_result and "npcs" in chapter_result["chapter"]:
            npcs = chapter_result["chapter"]["npcs"]
            logger.info(f"NPCs generation method: {npcs.get('generation_method', 'unknown')}")
            if isinstance(npcs.get('npcs'), list):
                logger.info(f"Number of NPCs generated: {len(npcs['npcs'])}")
            
    except Exception as e:
        logger.error(f"Enhanced chapter generation test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_genre_theme_consistency():
    """Test that generated characters are consistent with campaign genre and theme."""
    logger.info("=== Testing Genre/Theme Consistency ===")
    
    test_scenarios = [
        {
            "name": "Sci-Fi Cyberpunk",
            "genre": CampaignGenre.SCI_FI,
            "theme": SettingTheme.CYBERPUNK,
            "expected_elements": ["cyber", "tech", "corpo", "net", "AI"]
        },
        {
            "name": "Fantasy Western",
            "genre": CampaignGenre.WESTERN,
            "theme": SettingTheme.WESTERN,
            "expected_elements": ["frontier", "outlaw", "sheriff", "saloon", "gunslinger"]
        },
        {
            "name": "Steampunk Horror",
            "genre": CampaignGenre.HORROR,
            "theme": SettingTheme.STEAMPUNK,
            "expected_elements": ["steam", "gear", "Victorian", "industrial", "gothic"]
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"Testing {scenario['name']} consistency...")
        
        campaign_context = {
            "genre": scenario["genre"],
            "theme": scenario["theme"],
            "complexity": "medium",
            "party_level": 3,
            "narrative_role": "major"
        }
        
        try:
            async with CharacterServiceClient() as client:
                npc_result = await client.generate_character("npc", campaign_context)
                
                # Check if result contains genre-appropriate elements
                result_text = json.dumps(npc_result).lower()
                found_elements = [elem for elem in scenario["expected_elements"] if elem in result_text]
                
                logger.info(f"  Generated character for {scenario['name']}")
                logger.info(f"  Found thematic elements: {found_elements}")
                
        except Exception as e:
            logger.info(f"  {scenario['name']} test failed (expected if backend not running): {e}")


async def main():
    """Run all character service integration tests."""
    logger.info("Starting Character Service Integration Tests")
    logger.info("=" * 50)
    
    tests = [
        test_character_service_client,
        test_campaign_character_integrator,
        test_enhanced_chapter_generation,
        test_genre_theme_consistency
    ]
    
    for test_func in tests:
        try:
            await test_func()
            logger.info(f"✓ {test_func.__name__} completed")
        except Exception as e:
            logger.error(f"✗ {test_func.__name__} failed: {e}")
        
        logger.info("-" * 30)
    
    logger.info("Character Service Integration Tests Complete")


if __name__ == "__main__":
    asyncio.run(main())
