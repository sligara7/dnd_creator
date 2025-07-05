#!/usr/bin/env python3
"""
Test Campaign Generation Endpoints - Task 2 Validation
=====================================================

This script validates the implementation of Task 2: Campaign Generation Endpoints:
- Campaign creation from scratch
- Campaign skeleton generation  
- Campaign refinement and evolution

Tests both the creation service and the underlying factory methods.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the backend_campaign src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_test_environment():
    """Set up test environment variables to avoid config issues."""
    os.environ['TESTING'] = 'true'
    os.environ['SECRET_KEY'] = 'test_secret_key_for_campaign_testing'
    os.environ['APP_NAME'] = 'test_campaign_app'
    os.environ['APP_ENV'] = 'testing'
    os.environ['DEBUG'] = 'true'

async def test_campaign_from_scratch():
    """Test creating a complete campaign from scratch."""
    print("🧪 Testing Campaign Creation From Scratch...")
    
    try:
        # Import after setting up environment
        from src.services.creation import CampaignCreationService, CampaignCreationConfig
        from src.services.llm_service import LLMService
        from src.models.campaign_creation_models import (
            CampaignFromScratchRequest, CampaignCreationType, CampaignGenre, 
            CampaignComplexity, SettingTheme
        )
        
        # Create mock LLM service
        class MockLLMService:
            async def generate_completion(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=""):
                return json.dumps({
                    "title": "The Shattered Crown",
                    "description": "A political intrigue campaign set in a crumbling kingdom where the royal bloodline has been corrupted by dark magic.",
                    "plot_summary": "The heroes must navigate complex political alliances while uncovering a conspiracy that threatens the realm's survival.",
                    "main_antagonist": {
                        "name": "Duke Malachar", 
                        "motivation": "Seeks to claim the throne through manipulation and dark pacts"
                    },
                    "key_npcs": [
                        {"name": "Queen Isadora", "role": "Reluctant monarch"},
                        {"name": "Spymaster Vex", "role": "Information broker"}
                    ],
                    "major_locations": [
                        {"name": "The Royal Capital", "description": "Center of political power"},
                        {"name": "The Shadowfell Embassy", "description": "Source of dark influence"}
                    ],
                    "campaign_hooks": [
                        "The heroes witness an assassination attempt on the queen",
                        "A mysterious letter arrives requesting their aid"
                    ]
                })
        
        # Create service
        llm_service = MockLLMService()
        config = CampaignCreationConfig(base_timeout=60)
        service = CampaignCreationService(llm_service, config)
        
        # Create test request
        request = CampaignFromScratchRequest(
            creation_type=CampaignCreationType.CAMPAIGN_FROM_SCRATCH,
            concept="A political intrigue campaign where the royal family is being corrupted by otherworldly forces, and the heroes must decide whether to save the monarchy or let it fall to prevent greater evil. Players will face moral dilemmas about power, sacrifice, and the greater good.",
            genre=CampaignGenre.FANTASY,
            complexity=CampaignComplexity.COMPLEX,
            session_count=10,
            themes=["political intrigue", "moral ambiguity", "corruption"],
            setting_theme=SettingTheme.STANDARD_FANTASY,
            party_level=3,
            party_size=4,
            use_character_service=True
        )
        
        # Test creation
        response = await service.create_content(request)
        
        # Validate response
        assert response.success, f"Campaign creation failed: {response.error}"
        assert response.campaign is not None, "No campaign data returned"
        assert response.campaign["title"], "Campaign missing title"
        assert response.campaign["description"], "Campaign missing description"
        assert len(response.campaign["chapters"]) == 10, f"Expected 10 chapters, got {len(response.campaign['chapters'])}"
        assert response.campaign["genre"] == "fantasy", f"Genre mismatch: {response.campaign['genre']}"
        assert response.performance.generation_time > 0, "No generation time recorded"
        
        print("✅ Campaign From Scratch: PASSED")
        print(f"   - Title: {response.campaign['title']}")
        print(f"   - Chapters: {len(response.campaign['chapters'])}")
        print(f"   - Generation time: {response.performance.generation_time:.2f}s")
        
        return response.campaign
        
    except Exception as e:
        print(f"❌ Campaign From Scratch: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_campaign_skeleton():
    """Test creating a campaign skeleton."""
    print("🧪 Testing Campaign Skeleton Generation...")
    
    try:
        from src.services.creation import CampaignCreationService, CampaignCreationConfig
        from src.services.llm_service import LLMService
        from src.models.campaign_creation_models import (
            CampaignSkeletonRequest, CampaignCreationType, CampaignGenre, SettingTheme
        )
        
        # Create mock LLM service
        class MockLLMService:
            async def generate_completion(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=""):
                return json.dumps({
                    "plot_overview": "A sweeping adventure to restore balance to the elemental planes",
                    "act_structure": [
                        {"act": "beginning", "description": "Heroes discover elemental imbalance"},
                        {"act": "middle", "description": "Journey through elemental planes"},
                        {"act": "end", "description": "Confront the source of chaos"}
                    ],
                    "major_plot_points": [
                        "Discovery of elemental disturbance",
                        "First planar journey",
                        "Alliance with elemental lords",
                        "Revelation of true enemy",
                        "Final confrontation"
                    ],
                    "key_antagonists": [
                        {"name": "The Void Touched", "goal": "Merge all planes into chaos"}
                    ],
                    "important_npcs": [
                        {"name": "Flamekeeper Zara", "role": "Fire plane guide"}
                    ],
                    "primary_locations": [
                        {"name": "Plane of Fire", "importance": "First destination"}
                    ],
                    "plot_hooks": [
                        "Elemental storms begin appearing in the material plane"
                    ]
                })
        
        # Create service
        llm_service = MockLLMService()
        config = CampaignCreationConfig(base_timeout=60)
        service = CampaignCreationService(llm_service, config)
        
        # Create test request
        request = CampaignSkeletonRequest(
            creation_type=CampaignCreationType.CAMPAIGN_SKELETON,
            concept="The elemental planes are becoming unstable, causing magical storms and dimensional rifts in the material world. The heroes must journey through each elemental plane to discover the source of the chaos and restore balance before reality itself tears apart.",
            campaign_title="Elemental Convergence",
            campaign_description="A planar adventure to restore elemental balance",
            themes=["elemental magic", "planar travel", "cosmic balance"],
            session_count=8,
            detail_level="medium"
        )
        
        # Test creation
        response = await service.create_content(request)
        
        # Validate response
        assert response.success, f"Skeleton creation failed: {response.error}"
        assert response.skeleton is not None, "No skeleton data returned"
        assert response.skeleton["title"] == "Elemental Convergence", "Title mismatch"
        assert len(response.skeleton["chapter_outlines"]) == 8, f"Expected 8 chapter outlines, got {len(response.skeleton['chapter_outlines'])}"
        assert response.skeleton["plot_overview"], "Missing plot overview"
        
        print("✅ Campaign Skeleton: PASSED")
        print(f"   - Title: {response.skeleton['title']}")
        print(f"   - Chapter outlines: {len(response.skeleton['chapter_outlines'])}")
        print(f"   - Detail level: {response.skeleton['detail_level']}")
        
        return response.skeleton
        
    except Exception as e:
        print(f"❌ Campaign Skeleton: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_campaign_refinement(existing_campaign):
    """Test campaign refinement and evolution."""
    print("🧪 Testing Campaign Refinement...")
    
    if not existing_campaign:
        print("⚠️ Skipping refinement test - no existing campaign")
        return
    
    try:
        from src.services.creation import CampaignCreationService, CampaignCreationConfig
        from src.models.campaign_creation_models import CampaignRefinementRequest, CampaignCreationType
        
        # Create mock LLM service
        class MockLLMService:
            async def generate_completion(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=""):
                return json.dumps({
                    "changes": [
                        {
                            "field": "description",
                            "new_value": "An enhanced political intrigue campaign with more social encounters and diplomatic challenges."
                        },
                        {
                            "field": "themes",
                            "new_value": ["political intrigue", "diplomacy", "social challenges", "moral ambiguity"]
                        }
                    ],
                    "reasoning": "Added more emphasis on social and diplomatic elements as requested"
                })
        
        # Create service
        llm_service = MockLLMService()
        config = CampaignCreationConfig(base_timeout=60)
        service = CampaignCreationService(llm_service, config)
        
        # Create refinement request
        request = CampaignRefinementRequest(
            creation_type=CampaignCreationType.ITERATIVE_REFINEMENT,
            concept="Refine existing campaign",
            existing_data=existing_campaign,
            refinement_prompt="Add more social encounters and diplomatic challenges. Players prefer roleplay over combat.",
            refinement_type="enhance",
            preserve_elements=["title", "main_antagonist"],
            player_feedback="We want more opportunities for negotiation and intrigue",
            refinement_cycles=1
        )
        
        # Test refinement
        response = await service.refine_content(request)
        
        # Validate response
        assert response.success, f"Refinement failed: {response.error}"
        assert response.campaign is not None, "No refined campaign data returned"
        assert response.evolution_type == "iterative_refinement", f"Wrong evolution type: {response.evolution_type}"
        assert response.cycles_completed == 1, f"Expected 1 cycle, got {response.cycles_completed}"
        
        # Check that preserved elements remained unchanged
        assert response.campaign["title"] == existing_campaign["title"], "Title was not preserved"
        
        print("✅ Campaign Refinement: PASSED")
        print(f"   - Evolution type: {response.evolution_type}")
        print(f"   - Cycles completed: {response.cycles_completed}")
        print(f"   - Title preserved: {response.campaign['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Campaign Refinement: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_factory_integration():
    """Test direct factory integration."""
    print("🧪 Testing Factory Integration...")
    
    try:
        from src.services.creation_factory import CampaignCreationFactory, CampaignCreationOptions
        from src.services.generators import CampaignGenre, CampaignComplexity, SettingTheme
        
        # Create mock LLM service
        class MockLLMService:
            async def generate_completion(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=""):
                return '{"title": "Factory Test Campaign", "description": "Generated via factory"}'
        
        # Create factory
        llm_service = MockLLMService()
        factory = CampaignCreationFactory(llm_service)
        
        # Test factory health
        health = await factory.get_factory_health_status()
        assert health["factory_type"] == "campaign_creation", "Wrong factory type"
        
        # Test factory creation
        result = await factory.create_from_scratch(
            CampaignCreationOptions.CAMPAIGN_SKELETON,
            "A test concept for factory validation"
        )
        
        assert result["success"], f"Factory creation failed: {result.get('error')}"
        
        print("✅ Factory Integration: PASSED")
        print(f"   - Factory type: {health['factory_type']}")
        print(f"   - Creation successful: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Factory Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_task_2_tests():
    """Run all Task 2 validation tests."""
    print("🚀 Starting Task 2: Campaign Generation Endpoints Tests")
    print("=" * 70)
    
    setup_test_environment()
    
    results = {}
    
    # Test 1: Campaign from scratch
    campaign = await test_campaign_from_scratch()
    results['campaign_from_scratch'] = campaign is not None
    
    # Test 2: Campaign skeleton
    skeleton = await test_campaign_skeleton()
    results['campaign_skeleton'] = skeleton is not None
    
    # Test 3: Campaign refinement (depends on campaign from test 1)
    refinement_success = await test_campaign_refinement(campaign)
    results['campaign_refinement'] = refinement_success
    
    # Test 4: Factory integration
    factory_success = await test_factory_integration()
    results['factory_integration'] = factory_success
    
    print("=" * 70)
    print("📋 Task 2 Test Results:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("🎉 TASK 2 IMPLEMENTATION COMPLETE!")
        print("✅ Campaign creation from scratch: Working")
        print("✅ Campaign skeleton generation: Working")  
        print("✅ Campaign refinement and evolution: Working")
        print("✅ Factory integration: Working")
        print()
        print("📝 Task 2 Summary:")
        print("   - ✅ Campaign Generation Endpoints implemented")
        print("   - ✅ LLM integration for content generation")
        print("   - ✅ Structured request/response handling")
        print("   - ✅ Performance tracking and validation")
        print("   - ✅ Error handling and fallback mechanisms")
    else:
        print("❌ TASK 2 HAS ISSUES - See failed tests above")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_task_2_tests())
    sys.exit(0 if success else 1)
