#!/usr/bin/env python3
"""
Test script for the git-like campaign system with chapters, characters, and maps.

This demonstrates the complete git-like versioning system where:
- Each chapter is a "commit" with a unique hash
- Characters and maps have UUIDs and are linked to specific chapters
- Branches represent alternate storylines
- Player choices create new branches
- Visual git-like structure for campaign flow
"""

import sys
import os
import json
import uuid
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models.database_models import (
        # Core campaign models
        Campaign, CampaignDB, CampaignStatusEnum,
        
        # Git-like versioning models
        ChapterVersion, CampaignBranch, ChapterChoice, PlaySession, ChapterMerge,
        ChapterVersionDB, ChapterVersionTypeEnum, BranchTypeEnum, PlaySessionStatusEnum,
        
        # Campaign content models
        CampaignCharacter, CampaignMap, CharacterChapterAppearance, MapChapterUsage,
        CampaignContentDB, CampaignCharacterTypeEnum, MapTypeEnum,
        
        # Database setup
        Base, init_database, get_db
    )
    print("✅ Successfully imported all database models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def generate_chapter_hash(content, parents=None):
    """Generate a simple hash for demonstration purposes."""
    import hashlib
    parents = parents or []
    data = f"{content}_{parents}_{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:12]

def demonstrate_git_like_campaign():
    """Demonstrate the git-like campaign system."""
    print("\n" + "="*70)
    print("🎲 D&D GIT-LIKE CAMPAIGN VERSIONING SYSTEM DEMONSTRATION")
    print("="*70)
    
    # Test data structures (without actual database)
    campaign_data = {
        "id": str(uuid.uuid4()),
        "title": "The Lost Kingdom Campaign",
        "description": "A high-fantasy adventure with political intrigue",
        "themes": ["political intrigue", "ancient magic", "redemption"],
        "current_branch": "main",
        "total_chapters": 0,
        "total_branches": 1
    }
    
    print(f"\n📚 Created Campaign: {campaign_data['title']}")
    print(f"   Campaign ID: {campaign_data['id']}")
    print(f"   Themes: {', '.join(campaign_data['themes'])}")
    
    # Demonstrate git-like chapter structure
    print(f"\n🌳 CHAPTER VERSION TREE (Git-like Structure)")
    print("-" * 50)
    
    # Create skeleton chapters (initial "commits")
    skeleton_chapters = []
    
    # Chapter 1: The Mysterious Letter
    chapter1_hash = generate_chapter_hash("Chapter 1: The Mysterious Letter")
    chapter1 = {
        "version_hash": chapter1_hash,
        "branch_name": "main",
        "title": "The Mysterious Letter",
        "summary": "The party receives a cryptic letter about a lost kingdom",
        "version_type": ChapterVersionTypeEnum.SKELETON.value,
        "parent_hashes": [],  # First chapter, no parents
        "commit_message": "Initial skeleton: Campaign opening"
    }
    skeleton_chapters.append(chapter1)
    print(f"📝 {chapter1_hash} (main) - {chapter1['title']} [SKELETON]")
    
    # Chapter 2: The Tavern Investigation
    chapter2_hash = generate_chapter_hash("Chapter 2: The Tavern Investigation", [chapter1_hash])
    chapter2 = {
        "version_hash": chapter2_hash,
        "branch_name": "main",
        "title": "The Tavern Investigation",
        "summary": "The party investigates rumors at the local tavern",
        "version_type": ChapterVersionTypeEnum.SKELETON.value,
        "parent_hashes": [chapter1_hash],
        "commit_message": "Skeleton: Tavern investigation scene"
    }
    skeleton_chapters.append(chapter2)
    print(f"📝 {chapter2_hash} (main) - {chapter2['title']} [SKELETON]")
    
    # Chapter 3: The Forest Encounter
    chapter3_hash = generate_chapter_hash("Chapter 3: The Forest Encounter", [chapter2_hash])
    chapter3 = {
        "version_hash": chapter3_hash,
        "branch_name": "main",
        "title": "The Forest Encounter",
        "summary": "The party encounters mysterious creatures in the forest",
        "version_type": ChapterVersionTypeEnum.SKELETON.value,
        "parent_hashes": [chapter2_hash],
        "commit_message": "Skeleton: Forest encounter setup"
    }
    skeleton_chapters.append(chapter3)
    print(f"📝 {chapter3_hash} (main) - {chapter3['title']} [SKELETON]")
    
    # Demonstrate campaign characters with UUIDs
    print(f"\n👥 CAMPAIGN CHARACTERS (UUID Tracking)")
    print("-" * 50)
    
    # Create NPCs and characters
    characters = []
    
    # The Mysterious Messenger (NPC)
    messenger_id = str(uuid.uuid4())
    messenger = {
        "id": messenger_id,
        "campaign_id": campaign_data["id"],
        "name": "Elara Moonwhisper",
        "character_type": CampaignCharacterTypeEnum.NPC.value,
        "species": "Elf",
        "description": "A mysterious hooded figure who delivers the initial letter",
        "role_in_campaign": "Quest initiator",
        "first_appearance_chapter": chapter1_hash,
        "chapters_appeared": [chapter1_hash],
        "stats": {"ac": 14, "hp": 27, "speed": 30},
        "backstory": "Former royal messenger with a dark secret"
    }
    characters.append(messenger)
    print(f"🧙‍♀️ {messenger_id[:8]}... - {messenger['name']} (NPC)")
    print(f"    Role: {messenger['role_in_campaign']}")
    print(f"    First appears: Chapter 1 ({chapter1_hash})")
    
    # The Tavern Keeper (NPC)
    tavern_keeper_id = str(uuid.uuid4())
    tavern_keeper = {
        "id": tavern_keeper_id,
        "campaign_id": campaign_data["id"],
        "name": "Brom Ironbeard",
        "character_type": CampaignCharacterTypeEnum.NPC.value,
        "species": "Dwarf",
        "description": "Gruff but kindhearted tavern keeper with useful information",
        "role_in_campaign": "Information source",
        "first_appearance_chapter": chapter2_hash,
        "chapters_appeared": [chapter2_hash],
        "stats": {"ac": 12, "hp": 34, "speed": 25},
        "backstory": "Retired adventurer who knows local legends"
    }
    characters.append(tavern_keeper)
    print(f"🍺 {tavern_keeper_id[:8]}... - {tavern_keeper['name']} (NPC)")
    print(f"    Role: {tavern_keeper['role_in_campaign']}")
    print(f"    First appears: Chapter 2 ({chapter2_hash})")
    
    # Forest Guardian (Monster)
    guardian_id = str(uuid.uuid4())
    guardian = {
        "id": guardian_id,
        "campaign_id": campaign_data["id"],
        "name": "Ancient Tree Shepherd",
        "character_type": CampaignCharacterTypeEnum.MONSTER.value,
        "species": "Awakened Tree",
        "description": "Massive sentient tree that guards the forest paths",
        "role_in_campaign": "Forest protector",
        "challenge_rating": "5",
        "first_appearance_chapter": chapter3_hash,
        "chapters_appeared": [chapter3_hash],
        "stats": {"ac": 16, "hp": 138, "speed": 20},
        "legendary_actions": ["Root Slam", "Entangle", "Call Wildlife"]
    }
    characters.append(guardian)
    print(f"🌳 {guardian_id[:8]}... - {guardian['name']} (MONSTER)")
    print(f"    Role: {guardian['role_in_campaign']}")
    print(f"    Challenge Rating: {guardian['challenge_rating']}")
    print(f"    First appears: Chapter 3 ({chapter3_hash})")
    
    # Demonstrate campaign maps with UUIDs
    print(f"\n🗺️  CAMPAIGN MAPS (UUID Tracking)")
    print("-" * 50)
    
    maps = []
    
    # Village Map
    village_map_id = str(uuid.uuid4())
    village_map = {
        "id": village_map_id,
        "campaign_id": campaign_data["id"],
        "name": "Millbrook Village",
        "map_type": MapTypeEnum.CITY.value,
        "description": "Small farming village where the adventure begins",
        "scale": "1 square = 10 feet",
        "first_used_chapter": chapter1_hash,
        "associated_chapters": [chapter1_hash, chapter2_hash],
        "points_of_interest": [
            {"name": "The Prancing Pony Tavern", "coordinates": {"x": 15, "y": 20}},
            {"name": "Village Square", "coordinates": {"x": 25, "y": 25}},
            {"name": "Mayor's House", "coordinates": {"x": 35, "y": 15}}
        ],
        "character_positions": {
            messenger_id: {"x": 25, "y": 25},  # Village square
            tavern_keeper_id: {"x": 15, "y": 20}  # Inside tavern
        }
    }
    maps.append(village_map)
    print(f"🏘️  {village_map_id[:8]}... - {village_map['name']} ({village_map['map_type']})")
    print(f"    Scale: {village_map['scale']}")
    print(f"    Used in: Chapters 1-2")
    print(f"    POIs: {len(village_map['points_of_interest'])} locations")
    
    # Forest Map
    forest_map_id = str(uuid.uuid4())
    forest_map = {
        "id": forest_map_id,
        "campaign_id": campaign_data["id"],
        "name": "Whispering Woods",
        "map_type": MapTypeEnum.REGION.value,
        "description": "Ancient forest with magical properties",
        "scale": "1 hex = 1 mile",
        "first_used_chapter": chapter3_hash,
        "associated_chapters": [chapter3_hash],
        "points_of_interest": [
            {"name": "Forest Path", "coordinates": {"x": 10, "y": 30}},
            {"name": "Guardian's Grove", "coordinates": {"x": 20, "y": 40}},
            {"name": "Hidden Spring", "coordinates": {"x": 30, "y": 35}}
        ],
        "character_positions": {
            guardian_id: {"x": 20, "y": 40}  # Guardian's Grove
        },
        "hidden_areas": [
            {"name": "Secret Druid Circle", "coordinates": {"x": 25, "y": 45}}
        ]
    }
    maps.append(forest_map)
    print(f"🌲 {forest_map_id[:8]}... - {forest_map['name']} ({forest_map['map_type']})")
    print(f"    Scale: {forest_map['scale']}")
    print(f"    Used in: Chapter 3")
    print(f"    POIs: {len(forest_map['points_of_interest'])} locations")
    print(f"    Hidden areas: {len(forest_map['hidden_areas'])} secret locations")
    
    # Demonstrate player choice creating a branch
    print(f"\n🎭 PLAYER CHOICE & BRANCHING")
    print("-" * 50)
    
    # Simulate a player choice in Chapter 3
    choice_data = {
        "campaign_id": campaign_data["id"],
        "chapter_version_id": chapter3_hash,
        "choice_description": "How to approach the Ancient Tree Shepherd",
        "options_presented": [
            "Attempt peaceful negotiation",
            "Attack immediately", 
            "Try to sneak past",
            "Offer a magical gift"
        ],
        "choice_made": {"option": "Attempt peaceful negotiation", "details": "Party decides to talk first"},
        "players_involved": ["Alice", "Bob", "Charlie", "Dana"],
        "immediate_consequences": {"tree_disposition": "cautiously friendly"},
        "resulted_in_branch": "peaceful-path"
    }
    
    print(f"🎯 Player Choice: {choice_data['choice_description']}")
    print(f"    Options: {len(choice_data['options_presented'])} choices available")
    print(f"    Chosen: {choice_data['choice_made']['option']}")
    print(f"    Result: New branch '{choice_data['resulted_in_branch']}'")
    
    # Create the new branch
    peaceful_branch_hash = generate_chapter_hash("Chapter 3: Peaceful Resolution", [chapter3_hash])
    peaceful_chapter = {
        "version_hash": peaceful_branch_hash,
        "branch_name": "peaceful-path",
        "title": "The Forest Encounter - Peaceful Resolution",
        "summary": "The party successfully negotiates with the Ancient Tree Shepherd",
        "version_type": ChapterVersionTypeEnum.DRAFT.value,
        "parent_hashes": [chapter3_hash],
        "commit_message": "Player choice: Peaceful negotiation with tree guardian",
        "player_choices": choice_data["choice_made"],
        "player_consequences": {"tree_ally": True, "forest_access": "granted"}
    }
    
    print(f"\n🌿 New Branch Created:")
    print(f"📝 {peaceful_branch_hash} (peaceful-path) - {peaceful_chapter['title']} [DRAFT]")
    print(f"    Parent: {chapter3_hash} (main)")
    print(f"    Consequence: Tree becomes ally, grants forest access")
    
    # Show the visual git-like structure
    print(f"\n🌳 UPDATED CAMPAIGN TREE STRUCTURE")
    print("-" * 50)
    print(f"📝 {chapter1_hash} (main) - Chapter 1: The Mysterious Letter [SKELETON]")
    print(f"│")
    print(f"📝 {chapter2_hash} (main) - Chapter 2: The Tavern Investigation [SKELETON]")
    print(f"│")
    print(f"📝 {chapter3_hash} (main) - Chapter 3: The Forest Encounter [SKELETON]")
    print(f"├── 🌿 {peaceful_branch_hash} (peaceful-path) - Peaceful Resolution [DRAFT]")
    print(f"│   └── 🎯 Player Choice: Negotiation successful")
    print(f"│")
    print(f"└── (Other branches could be: aggressive-path, stealth-path, gift-path)")
    
    # Demonstrate character tracking across chapters
    print(f"\n📊 CHARACTER CHAPTER APPEARANCES")
    print("-" * 50)
    
    for character in characters:
        print(f"👤 {character['name']} ({character['character_type'].upper()})")
        print(f"    UUID: {character['id']}")
        print(f"    Appears in: {len(character['chapters_appeared'])} chapter(s)")
        print(f"    First seen: {character['first_appearance_chapter']}")
        if character['name'] == "Ancient Tree Shepherd":
            print(f"    Branch variations:")
            print(f"      - Main branch: Hostile encounter")
            print(f"      - Peaceful branch: Becomes ally")
        print()
    
    # Demonstrate map usage tracking
    print(f"\n🗺️  MAP USAGE ACROSS CHAPTERS")
    print("-" * 50)
    
    for map_data in maps:
        print(f"🌍 {map_data['name']} ({map_data['map_type'].upper()})")
        print(f"    UUID: {map_data['id']}")
        print(f"    Used in: {len(map_data['associated_chapters'])} chapter(s)")
        print(f"    Characters present: {len(map_data['character_positions'])} character(s)")
        if 'hidden_areas' in map_data and map_data['hidden_areas']:
            print(f"    Hidden areas: {len(map_data['hidden_areas'])} secret location(s)")
        print()
    
    # Show campaign statistics
    print(f"\n📈 CAMPAIGN STATISTICS")
    print("-" * 50)
    print(f"🎲 Campaign: {campaign_data['title']}")
    print(f"📚 Total Chapters: {len(skeleton_chapters) + 1} (3 skeleton + 1 branch)")
    print(f"🌳 Total Branches: 2 (main + peaceful-path)")
    print(f"👥 Total Characters: {len(characters)} (1 NPC + 1 info source + 1 monster)")
    print(f"🗺️  Total Maps: {len(maps)} (1 village + 1 forest)")
    print(f"🎯 Player Choices: 1 (created peaceful-path branch)")
    print(f"🔗 Character-Chapter Links: {sum(len(c['chapters_appeared']) for c in characters)}")
    print(f"🔗 Map-Chapter Links: {sum(len(m['associated_chapters']) for m in maps)}")
    
    print(f"\n✅ Git-like campaign system demonstration complete!")
    print(f"📝 This system provides:")
    print(f"   • Each chapter as a git-like commit with unique hash")
    print(f"   • Characters and maps with UUIDs for tracking")
    print(f"   • Branching storylines based on player choices")
    print(f"   • Full lineage and relationship tracking")
    print(f"   • Visual git-like campaign structure")
    print(f"   • Flexible content management with JSON storage")

if __name__ == "__main__":
    try:
        demonstrate_git_like_campaign()
        print(f"\n🎉 Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
