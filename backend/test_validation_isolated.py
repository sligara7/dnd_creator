#!/usr/bin/env python3
"""
Simple test to verify validation works in isolation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database_models import SessionLocal, init_database, CharacterDB
from src.services.unified_catalog_service import UnifiedCatalogService
from src.core.config import settings

# Initialize database
database_url = settings.effective_database_url
init_database(database_url)

from src.models.database_models import SessionLocal
session = SessionLocal()

print("Creating test character and testing validation...")

try:
    # Create a character using CharacterDB
    character_data = {
        "name": "Test Fighter",
        "species": "Human",
        "background": "Soldier",
        "character_classes": {"Fighter": 3},
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 8
    }
    
    character = CharacterDB.create_character(session, character_data)
    character_id = str(character.id)
    session.commit()  # Commit the transaction
    print(f"✅ Created character: {character_id}")
    
    # Verify character exists
    from src.models.database_models import Character
    import uuid
    found_char = session.query(Character).filter(Character.id == uuid.UUID(character_id)).first()
    print(f"Character verification: {found_char.name if found_char else 'NOT FOUND'}")
    
    # Create unified catalog service
    catalog = UnifiedCatalogService(session)
    
    # Find a wizard spell
    print("Searching for spells...")
    all_spells = catalog.search_items(item_type="spell", limit=5)
    print(f"Found {len(all_spells)} total spells")
    
    wizard_spells = [s for s in all_spells if "wizard" in [cls.lower() for cls in s.get("class_restrictions", [])]]
    print(f"Found {len(wizard_spells)} wizard spells")
    
    if not wizard_spells:
        print("❌ No wizard spells found")
    else:
        wizard_spell = wizard_spells[0]
        print(f"✅ Found wizard spell: {wizard_spell['name']}")
        
        # Try to allocate wizard spell to fighter (should fail)
        try:
            access_id = catalog.grant_item_access(
                character_id=character_id,
                item_id=wizard_spell["id"],
                access_type="spells_known",
                acquired_method="Test",
                skip_validation=False
            )
            print(f"❌ Validation failed - Fighter was allowed to learn wizard spell!")
        except ValueError as e:
            print(f"✅ Validation worked correctly: {e}")
            
        # Try with skip_validation=True (should succeed)
        try:
            access_id = catalog.grant_item_access(
                character_id=character_id,
                item_id=wizard_spell["id"],
                access_type="spells_known",
                acquired_method="Test (skipped validation)",
                skip_validation=True
            )
            print(f"✅ Skipped validation worked: {access_id}")
        except Exception as e:
            print(f"❌ Unexpected error with skipped validation: {e}")

finally:
    session.close()

print("Test completed!")
