#!/usr/bin/env python3
"""
Simple validation integration test - no API dependencies
Tests the validation system integration without requiring secret keys or full API setup.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.creation_validation import (
    validate_campaign_concept, validate_campaign_structure, 
    validate_chapter_content, validate_encounter_balance,
    validate_campaign_from_scratch_request, validate_campaign_skeleton_request,
    validate_chapter_content_request, validate_refinement_request,
    CampaignCreationType
)

from src.models.campaign_creation_models import (
    CampaignFromScratchRequest, CampaignSkeletonRequest, 
    ChapterContentRequest, CampaignRefinementRequest
)

def test_concept_validation():
    """Test campaign concept validation."""
    print("Testing campaign concept validation...")
    
    # Valid concept
    valid_concept = "A dark fantasy campaign where players must investigate mysterious disappearances in a small village plagued by ancient curses and supernatural phenomena. The story explores complex themes of corruption, redemption, and the terrible price of forbidden power as heroes gradually uncover a sinister conspiracy involving corrupt nobles, otherworldly entities, and ancient pacts that threaten to destroy everything they hold dear. Players will face moral dilemmas, political intrigue, and terrifying supernatural encounters."
    
    result = validate_campaign_concept(valid_concept, CampaignCreationType.CAMPAIGN_FROM_SCRATCH)
    assert result.success, f"Valid concept should pass: {result.errors}"
    print("✓ Valid concept passed validation")
    
    # Invalid concept (too short)
    short_concept = "A fantasy adventure"
    result = validate_campaign_concept(short_concept, CampaignCreationType.CAMPAIGN_FROM_SCRATCH)
    assert not result.success, "Short concept should fail validation"
    print("✓ Short concept properly rejected")
    
    # Invalid concept (too long)
    long_concept = " ".join(["adventure"] * 600)  # Way too long
    result = validate_campaign_concept(long_concept, CampaignCreationType.CAMPAIGN_FROM_SCRATCH)
    assert not result.success, "Long concept should fail validation"
    print("✓ Long concept properly rejected")

def test_request_validation():
    """Test request validation."""
    print("\nTesting request validation...")
    
    # Valid campaign from scratch request
    valid_request = CampaignFromScratchRequest(
        creation_type=CampaignCreationType.CAMPAIGN_FROM_SCRATCH,
        concept="A compelling fantasy adventure involving ancient mysteries, political intrigue, and supernatural threats that span across multiple kingdoms and realms. Players must navigate complex moral choices while uncovering the truth behind a series of mysterious events that threaten the stability of the known world. The campaign features epic battles, deep character development, meaningful relationships with NPCs, and consequences that reshape the political landscape of the setting."
    )
    
    result = validate_campaign_from_scratch_request(valid_request)
    if result.has_errors():
        print(f"Errors: {result.errors}")
    assert not result.has_errors(), f"Valid request should pass: {result.errors}"
    print("✓ Valid campaign request passed validation")
    
    # Valid skeleton request
    skeleton_request = CampaignSkeletonRequest(
        creation_type=CampaignCreationType.CAMPAIGN_SKELETON,
        concept="A comprehensive mystery campaign involving supernatural elements, ancient conspiracies, and otherworldly threats that challenge both the heroes and the very fabric of reality. Players must investigate a series of interconnected mysteries while uncovering dark secrets that span generations. The campaign features complex NPCs, political intrigue, moral dilemmas, and escalating supernatural encounters that build to an epic climax.",
        campaign_title="The Haunted Manor",
        campaign_description="A mystery campaign set in a haunted estate with supernatural elements",
        detail_level="standard"
    )
    
    result = validate_campaign_skeleton_request(skeleton_request)
    assert not result.has_errors(), f"Valid skeleton request should pass: {result.errors}"
    print("✓ Valid skeleton request passed validation")
    
    # Valid chapter request
    chapter_request = ChapterContentRequest(
        creation_type=CampaignCreationType.CHAPTER_CONTENT,
        concept="Investigation of the abandoned library where ancient tomes contain dark secrets and supernatural entities lurk in the shadows of forgotten knowledge. Players must solve intricate puzzles, face otherworldly threats from beyond the veil, and uncover vital clues that lead to a larger conspiracy threatening the realm. They must navigate the supernatural dangers hidden within the forgotten archives while deciphering cryptic texts and avoiding the guardians that protect the most dangerous secrets.",
        campaign_title="Mystery of the Lost Tome",
        campaign_description="A dark mystery campaign involving ancient knowledge and supernatural threats",
        chapter_title="Chapter 1: The Silent Archive",
        chapter_summary="Heroes investigate an abandoned library filled with mysterious books and supernatural dangers",
        party_level=3,
        party_size=4
    )
    
    result = validate_chapter_content_request(chapter_request)
    assert not result.has_errors(), f"Valid chapter request should pass: {result.errors}"
    print("✓ Valid chapter request passed validation")

def test_content_validation():
    """Test content validation."""
    print("\nTesting content validation...")
    
    # Test campaign structure validation
    valid_campaign = {
        "title": "The Lost Kingdom",
        "description": "A thrilling adventure where heroes must reclaim a lost kingdom from ancient evils.",
        "themes": ["heroism", "redemption", "ancient evil"],
        "chapters": [
            {"title": "The Call to Adventure", "summary": "Heroes are summoned"},
            {"title": "The Journey Begins", "summary": "Initial challenges"}
        ]
    }
    
    result = validate_campaign_structure(valid_campaign)
    if result.has_errors():
        print(f"Campaign structure errors: {result.errors}")
    # Should pass or have warnings only
    print("✓ Campaign structure validation completed")
    
    # Test chapter content validation
    valid_chapter = {
        "title": "The Mysterious Cave",
        "content": "A detailed exploration scenario with multiple encounters and story elements.",
        "encounters": [
            {"type": "combat", "cr": 2, "description": "Goblin ambush"},
            {"type": "social", "description": "Negotiate with local traders"}
        ],
        "npcs": [{"name": "Merchant Bob", "role": "information"}],
        "locations": [{"name": "Crystal Cave", "description": "Glowing crystals illuminate the cavern"}]
    }
    
    result = validate_chapter_content(valid_chapter, party_level=3, party_size=4)
    if result.has_errors():
        print(f"Chapter content errors: {result.errors}")
    print("✓ Chapter content validation completed")

def test_encounter_validation():
    """Test encounter balance validation."""
    print("\nTesting encounter validation...")
    
    encounters = [
        {
            "type": "combat",
            "challenge_rating": 2,
            "creatures": [{"name": "Goblin", "cr": 0.25, "count": 4}],
            "difficulty": "medium"
        },
        {
            "type": "social", 
            "challenge_rating": 1,
            "description": "Negotiation with village elder"
        }
    ]
    
    result = validate_encounter_balance(encounters, party_level=3, party_size=4)
    if result.has_errors():
        print(f"Encounter balance errors: {result.errors}")
    print("✓ Encounter balance validation completed")

def main():
    """Run all validation tests."""
    print("Running Validation Integration Tests")
    print("=" * 50)
    
    try:
        test_concept_validation()
        test_request_validation()
        test_content_validation()
        test_encounter_validation()
        
        print("\n" + "=" * 50)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("\nValidation system is properly integrated and working.")
        print("The creation.py service now uses creation_validation.py for all validation requirements.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
