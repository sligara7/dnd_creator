#!/usr/bin/env python3
"""
Basic API Test - Test the implemented classes directly
"""

import sys
import tempfile
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_repository_manager():
    """Test CharacterRepositoryManager functionality."""
    print("🧪 Testing CharacterRepositoryManager...")
    
    try:
        from database_models_new import (
            CharacterRepositoryManager, Base, CharacterRepository, 
            CharacterBranch, CharacterCommit
        )
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create in-memory test database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test repository creation
        repo = CharacterRepositoryManager.create_repository(
            db=db,
            name="Test Character",
            description="Testing repository manager",
            player_name="Test Player",
            initial_character_data={
                "name": "Test Hero",
                "species": "Human",
                "level": 1,
                "character_classes": {"Fighter": 1}
            }
        )
        
        print(f"✅ Created repository: {repo.name} (ID: {repo.id})")
        
        # Test branch creation
        branch = CharacterRepositoryManager.create_branch(
            db=db,
            repository_id=repo.id,
            branch_name="test-branch",
            description="Test branch"
        )
        
        print(f"✅ Created branch: {branch.branch_name}")
        
        # Test commit creation
        commit = CharacterRepositoryManager.create_commit(
            db=db,
            repository_id=repo.id,
            branch_name="main",
            commit_message="Test commit",
            character_data={
                "name": "Test Hero",
                "species": "Human",
                "level": 2,
                "character_classes": {"Fighter": 2}
            },
            character_level=2
        )
        
        print(f"✅ Created commit: {commit.short_hash}")
        
        # Test getting character at commit
        character_data = CharacterRepositoryManager.get_character_at_commit(
            db=db,
            commit_hash=commit.commit_hash
        )
        
        print(f"✅ Retrieved character data: Level {character_data.get('level', 'Unknown')}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ CharacterRepositoryManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_versioning_api():
    """Test CharacterVersioningAPI functionality."""
    print("\n🧪 Testing CharacterVersioningAPI...")
    
    try:
        from database_models_new import (
            CharacterVersioningAPI, CharacterRepositoryManager, Base
        )
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create in-memory test database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create test repository with some commits
        repo = CharacterRepositoryManager.create_repository(
            db=db,
            name="API Test Character",
            description="Testing versioning API",
            initial_character_data={
                "name": "API Hero",
                "species": "Elf",
                "level": 1,
                "character_classes": {"Wizard": 1}
            }
        )
        
        # Add another commit
        CharacterRepositoryManager.create_commit(
            db=db,
            repository_id=repo.id,
            branch_name="main",
            commit_message="Level 2: Learned new spells",
            character_data={
                "name": "API Hero",
                "species": "Elf", 
                "level": 2,
                "character_classes": {"Wizard": 2}
            },
            character_level=2,
            commit_type="level_up"
        )
        
        # Test timeline data
        timeline = CharacterVersioningAPI.get_character_timeline_for_frontend(
            db=db,
            repository_id=repo.id
        )
        
        print(f"✅ Timeline data: {len(timeline['events'])} events")
        
        # Test visualization data
        viz_data = CharacterVersioningAPI.get_character_visualization_data(
            db=db,
            repository_id=repo.id
        )
        
        print(f"✅ Visualization data: {len(viz_data['nodes'])} nodes, {len(viz_data['edges'])} edges")
        
        # Test level up
        levelup_commit = CharacterVersioningAPI.level_up_character(
            db=db,
            repository_id=repo.id,
            branch_name="main",
            new_character_data={
                "name": "API Hero",
                "species": "Elf",
                "level": 3,
                "character_classes": {"Wizard": 3}
            },
            level_up_choices={
                "new_spells": ["Fireball", "Lightning Bolt"],
                "new_features": ["2nd Level Spell Slots"]
            }
        )
        
        print(f"✅ Level up commit: {levelup_commit.commit_message}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ CharacterVersioningAPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run API tests."""
    print("🚀 D&D Character Creator - API Implementation Test")
    print("=" * 50)
    
    tests = [
        ("CharacterRepositoryManager", test_repository_manager),
        ("CharacterVersioningAPI", test_versioning_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All API classes working perfectly!")
        print("✅ Your Git-like versioning system is ready!")
    else:
        print("⚠️  Some tests failed. Check output above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
