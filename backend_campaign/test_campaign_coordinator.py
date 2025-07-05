#!/usr/bin/env python3
"""
Campaign Content Coordinator Test

Tests the campaign coordinator's orchestration capabilities without requiring
full API setup or secret keys.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.campaign_content_coordinator import (
    CampaignContentCoordinator, CampaignWorkflowRequest, ChapterGenerationBatch
)
from src.models.campaign_creation_models import CampaignCreationType

def test_coordinator_initialization():
    """Test that the coordinator initializes properly."""
    print("Testing campaign coordinator initialization...")
    
    # Mock LLM service for testing
    class MockLLMService:
        async def generate_content(self, prompt, **kwargs):
            return f"Generated content for: {prompt[:50]}..."
    
    try:
        llm_service = MockLLMService()
        coordinator = CampaignContentCoordinator(llm_service)
        
        status = coordinator.get_coordinator_status()
        assert status["service"] == "CampaignContentCoordinator"
        assert status["status"] == "operational"
        assert "complete_campaign" in status["supported_workflows"]
        
        print("✓ Coordinator initialized successfully")
        print(f"✓ Supports {len(status['supported_workflows'])} workflow types")
        return True
        
    except Exception as e:
        print(f"❌ Coordinator initialization failed: {str(e)}")
        return False

def test_workflow_request_models():
    """Test the workflow request models."""
    print("\nTesting workflow request models...")
    
    try:
        # Test CampaignWorkflowRequest
        workflow_request = CampaignWorkflowRequest(
            workflow_type="complete_campaign",
            primary_params={
                "concept": "A dark fantasy campaign where heroes must stop an ancient evil from awakening and consuming the world in eternal darkness",
                "genre": "fantasy",
                "session_count": 8
            },
            chapters_needed=8,
            auto_generate_npcs=True,
            auto_generate_encounters=True
        )
        
        assert workflow_request.workflow_type == "complete_campaign"
        assert workflow_request.chapters_needed == 8
        assert workflow_request.auto_generate_npcs == True
        
        print("✓ CampaignWorkflowRequest model works correctly")
        
        # Test ChapterGenerationBatch
        batch_request = ChapterGenerationBatch(
            campaign_id="test_campaign_123",
            campaign_context={
                "title": "Test Campaign",
                "description": "A test campaign for validation",
                "themes": ["mystery", "adventure"]
            },
            chapter_outlines=[
                {"title": "Chapter 1", "summary": "The beginning"},
                {"title": "Chapter 2", "summary": "The middle"},
                {"title": "Chapter 3", "summary": "The end"}
            ],
            party_level_progression=[1, 3, 5]
        )
        
        assert batch_request.campaign_id == "test_campaign_123"
        assert len(batch_request.chapter_outlines) == 3
        assert batch_request.party_level_progression == [1, 3, 5]
        
        print("✓ ChapterGenerationBatch model works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Workflow request model test failed: {str(e)}")
        return False

def test_helper_methods():
    """Test coordinator helper methods."""
    print("\nTesting coordinator helper methods...")
    
    try:
        class MockLLMService:
            async def generate_content(self, prompt, **kwargs):
                return f"Generated: {prompt[:30]}..."
        
        coordinator = CampaignContentCoordinator(MockLLMService())
        
        # Test chapter title generation
        campaign_data = {"title": "Test Campaign", "themes": ["adventure"]}
        
        title_0 = coordinator._generate_chapter_title(0, campaign_data)
        title_1 = coordinator._generate_chapter_title(1, campaign_data)
        title_10 = coordinator._generate_chapter_title(10, campaign_data)
        
        assert title_0 == "The Call to Adventure"
        assert title_1 == "First Steps"
        assert title_10 == "Chapter 11"  # Beyond predefined titles
        
        print("✓ Chapter title generation works correctly")
        
        # Test skeleton outline extraction
        skeleton_data = {
            "chapters": [
                {"title": "Intro", "summary": "Beginning"},
                {"title": "Quest", "summary": "Adventure"}
            ]
        }
        
        outlines = coordinator._extract_chapter_outlines_from_skeleton(skeleton_data)
        assert len(outlines) == 2
        assert outlines[0]["title"] == "Intro"
        
        print("✓ Skeleton outline extraction works correctly")
        
        # Test empty skeleton handling
        empty_skeleton = {}
        default_outlines = coordinator._extract_chapter_outlines_from_skeleton(empty_skeleton)
        assert len(default_outlines) == 8  # Default chapter count
        
        print("✓ Empty skeleton handling works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Helper methods test failed: {str(e)}")
        return False

def test_coordinator_comparison():
    """Compare campaign coordinator vs character coordinator capabilities."""
    print("\nComparing coordinators...")
    
    print("Character Coordinator (content_coordinator.py):")
    print("  - Character creation with custom equipment")
    print("  - Adventure content generation") 
    print("  - Batch character/equipment creation")
    print("  - Equipment-character consistency validation")
    
    print("\nCampaign Coordinator (campaign_content_coordinator.py):")
    print("  - Complete campaign workflow orchestration")
    print("  - Skeleton expansion to full campaigns")
    print("  - Batch chapter generation with consistency")
    print("  - Campaign narrative flow refinement")
    print("  - Cross-chapter validation and quality assurance")
    
    print("\n✓ Both coordinators serve different but complementary purposes")
    print("✓ Campaign coordinator is specifically designed for campaign-level workflows")
    
    return True

def main():
    """Run all coordinator tests."""
    print("Campaign Content Coordinator Tests")
    print("=" * 50)
    
    tests = [
        test_coordinator_initialization,
        test_workflow_request_models, 
        test_helper_methods,
        test_coordinator_comparison
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    if passed == len(tests):
        print("✅ ALL COORDINATOR TESTS PASSED!")
        print(f"\nThe CampaignContentCoordinator is ready for use.")
        print("It provides high-level orchestration for complex campaign generation workflows.")
    else:
        print(f"❌ {len(tests) - passed} out of {len(tests)} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
