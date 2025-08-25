"""
Smoke Tests for Character Service Catalog Integration

These tests verify that the catalog integration is working as expected at a high level.
"""

import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

# Import the services we want to test
from src.services.creation_factory import CreationFactory
from src.services.character_equipment import CharacterEquipmentService
from src.services.unified_catalog_service import UnifiedCatalogService

# Import our models and enums
from src.core.enums import CreationOptions
from src.models.database_models import Character, UnifiedItem, CharacterItemAccess

@pytest.fixture
def db_session():
    """Provide a database session for testing."""
    from src.models.database_models import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def factory(db_session):
    """Provide a CreationFactory instance."""
    return CreationFactory(llm_service=None, database=db_session)

@pytest.fixture
def equipment_service(db_session):
    """Provide a CharacterEquipmentService instance."""
    return CharacterEquipmentService(db=db_session)

@pytest.fixture
def catalog_service(db_session):
    """Provide a UnifiedCatalogService instance."""
    return UnifiedCatalogService(session=db_session)

@pytest.fixture
def test_character(db_session) -> Character:
    """Create a test character for use in tests."""
    character = Character(
        id=str(uuid.uuid4()),
        name="Test Character",
        character_classes={"Fighter": 1},
        created_at=datetime.now(timezone.utc),
        weapon_proficiencies=["simple", "martial"],
        armor_proficiencies=["light", "medium", "heavy", "shields"]
    )
    db_session.add(character)
    db_session.commit()
    return character

async def test_creation_factory_prefers_official_content(factory, test_character):
    """Verify that creation factory prioritizes official content."""
    # Try to create a longsword (which exists in official content)
    result = await factory.create_from_scratch(
        CreationOptions.WEAPON,
        "longsword",
        character_data={
            "name": "Longsword",
            "character_id": test_character.id,
            "classes": test_character.character_classes
        }
    )
    
    assert result is not None
    assert result.get("source_type") == "official"
    assert result.get("name") == "Longsword"

async def test_equipment_service_assigns_official_weapons(equipment_service, test_character):
    """Verify that equipment service correctly assigns official weapons."""
    weapons_to_assign = [
        {"name": "Longsword", "type": "weapon"},
        {"name": "Dagger", "type": "weapon"},
        {"name": "Custom Weapon", "type": "weapon"}  # Should be created as custom
    ]
    
    access_ids = await equipment_service.assign_equipment(
        character_id=test_character.id,
        equipment_list=weapons_to_assign
    )
    
    assert len(access_ids) == 3
    
    # Verify the assignments
    equipment = await equipment_service.get_character_equipment(test_character.id)
    assert len(equipment["equipped"]) == 3
    
    # Check that official weapons were properly sourced
    items = [item["item_details"] for item in equipment["equipped"]]
    official_items = [i for i in items if i["source_type"] == "official"]
    custom_items = [i for i in items if i["source_type"] == "custom"]
    
    assert len(official_items) == 2  # Longsword and Dagger should be official
    assert len(custom_items) == 1    # Custom Weapon should be custom

async def test_catalog_migration_state_tracking(catalog_service, db_session):
    """Verify that migration state is properly tracked."""
    from src.services.unified_catalog_migration import run_migration
    from src.models.database_models import SystemState
    
    # Run a migration
    results = await run_migration(catalog_service, db_session)
    
    # Check that items were migrated
    assert sum(results.values()) > 0
    
    # Verify system state was updated
    state = db_session.query(SystemState).filter(
        SystemState.component == "catalog_migration"
    ).first()
    
    assert state is not None
    assert state.status == "success"
    assert "last_successful_run" in state.details

@pytest.mark.parametrize("weapon_name", [
    "Longsword",  # Official weapon
    "Custom Blade"  # Custom weapon
])
async def test_character_weapon_assignment(
    equipment_service,
    test_character,
    weapon_name: str
):
    """Verify weapon assignment works for both official and custom weapons."""
    weapon = {"name": weapon_name, "type": "weapon"}
    
    # Assign the weapon
    access_ids = await equipment_service.assign_equipment(
        character_id=test_character.id,
        equipment_list=[weapon]
    )
    
    assert len(access_ids) == 1
    
    # Verify the assignment
    equipment = await equipment_service.get_character_equipment(test_character.id)
    assigned_weapon = next(
        (item for item in equipment["equipped"] if item["item_details"]["name"] == weapon_name),
        None
    )
    
    assert assigned_weapon is not None
    if weapon_name == "Longsword":
        assert assigned_weapon["item_details"]["source_type"] == "official"
    else:
        assert assigned_weapon["item_details"]["source_type"] == "custom"

def test_factory_logs_creation_events(factory, test_character, caplog):
    """Verify that the factory logs important creation events."""
    import logging
    caplog.set_level(logging.INFO)
    
    # Create a weapon
    factory.create_from_scratch(
        CreationOptions.WEAPON,
        "magical dagger",
        character_data={
            "name": "Magical Dagger",
            "character_id": test_character.id,
            "classes": test_character.character_classes
        }
    )
    
    # Check for expected log messages
    log_text = "\n".join(caplog.messages)
    assert "checking_official_content" in log_text
    assert "creation_type=weapon" in log_text

def test_equipment_service_logs_assignments(equipment_service, test_character, caplog):
    """Verify that equipment assignments are properly logged."""
    import logging
    caplog.set_level(logging.INFO)
    
    # Assign some equipment
    equipment_service.assign_equipment(
        character_id=test_character.id,
        equipment_list=[
            {"name": "Longsword", "type": "weapon"},
            {"name": "Custom Item", "type": "equipment"}
        ]
    )
    
    # Check for expected log messages
    log_text = "\n".join(caplog.messages)
    assert "assigning_equipment" in log_text
    assert "found_official_weapon" in log_text
    assert "creating_custom_item" in log_text
    assert "item_access_granted" in log_text
