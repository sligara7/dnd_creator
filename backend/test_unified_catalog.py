#!/usr/bin/env python3
"""
Test script for unified catalog functionality.
Tests the unified catalog API and services without starting the full FastAPI server.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Set PYTHONPATH for imports
os.environ['PYTHONPATH'] = str(backend_path)

import logging
from src.core.config import settings
from src.models.database_models import init_database, CharacterDB
from src.services.unified_catalog_service import UnifiedCatalogService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_catalog_functionality():
    """Test the unified catalog functionality."""
    print("=== UNIFIED CATALOG FUNCTIONALITY TEST ===\n")
    
    try:
        # Initialize database
        database_url = settings.effective_database_url
        print(f"Database URL: {database_url}")
        init_database(database_url)
        
        # Import SessionLocal after database initialization
        from src.models.database_models import SessionLocal
        
        # Create catalog service with session
        session = SessionLocal()
        catalog_service = UnifiedCatalogService(session)
        
        # Test 1: Get catalog stats
        print("Test 1: Getting catalog statistics...")
        stats = catalog_service.get_catalog_stats()
        print(f"Catalog Stats: {stats}")
        
        # Test 2: Search for spells
        print("\nTest 2: Searching for spells...")
        spells = catalog_service.search_items(
            item_type="spell",
            limit=10
        )
        print(f"Found {len(spells)} spells")
        if spells:
            print(f"Sample spell: {spells[0]['name']} (Level {spells[0].get('spell_level', 'Unknown')})")
        
        # Test 3: Search for weapons
        print("\nTest 3: Searching for weapons...")
        weapons = catalog_service.search_items(
            item_type="weapon",
            limit=10
        )
        print(f"Found {len(weapons)} weapons")
        if weapons:
            print(f"Sample weapon: {weapons[0]['name']} ({weapons[0].get('item_subtype', 'Unknown type')})")
        
        # Test 4: Search for armor
        print("\nTest 4: Searching for armor...")
        armor = catalog_service.search_items(
            item_type="armor",
            limit=5
        )
        print(f"Found {len(armor)} armor items")
        if armor:
            print(f"Sample armor: {armor[0]['name']} ({armor[0].get('item_subtype', 'Unknown type')})")
        
        # Test 5: Search by name filter
        print("\nTest 5: Searching by name filter (fireball)...")
        fireball_results = catalog_service.search_items(
            name_filter="fireball",
            limit=5
        )
        print(f"Found {len(fireball_results)} items matching 'fireball'")
        for item in fireball_results:
            print(f"  - {item['name']} ({item['item_type']})")
        
        # Test 6: Test character allocation (if possible)
        print("\nTest 6: Testing character allocation...")
        # Re-import SessionLocal for the allocation test
        from src.models.database_models import SessionLocal
        allocation_session = SessionLocal()
        try:
            # Get first character if any exist
            characters = CharacterDB.list_characters(allocation_session)
            if characters:
                character_id = characters[0].id
                print(f"Testing allocation for character: {characters[0].name} ({character_id})")
                
                # Try to allocate a spell
                if spells:
                    spell_id = spells[0]['id']
                    result = catalog_service.grant_item_access(
                        character_id=character_id,
                        item_id=spell_id,
                        access_type="spells_known",
                        quantity=1,
                        acquired_method="test"
                    )
                    print(f"Spell allocation result: {result}")
                    
                    # Check character allocations
                    allocations = catalog_service.get_character_allocations(character_id)
                    print(f"Character allocations: {len(allocations)} items")
                else:
                    print("No spells available for allocation test")
            else:
                print("No characters found for allocation test")
        finally:
            allocation_session.close()
        
        print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n=== TEST FAILED: {e} ===")
        return False

if __name__ == "__main__":
    success = test_catalog_functionality()
    sys.exit(0 if success else 1)
