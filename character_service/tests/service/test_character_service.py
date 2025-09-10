"""Tests for the character service."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository
from character_service.services.character import (
    CharacterCreationError,
    CharacterService,
    CharacterValidationError,
    ResourceType,
)
from tests.service.utils import create_test_ability_scores


@pytest.mark.asyncio
async def test_create_character_basic(db_session: AsyncSession):
    """Test basic character creation with valid inputs."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Act
    character = await service.create_character(
        name="Test Character",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    
    # Assert
    assert character.id is not None
    assert character.name == "Test Character"
    assert character.level == 1
    assert character.strength == ability_scores["strength"]
    assert character.race == "Human"
    assert character.character_class == "Fighter"
    # Fighter HP at level 1: Hit Die (10) + CON mod (1) = 11
    assert character.max_hit_points == 11
    assert character.current_hit_points == 11


@pytest.mark.asyncio
async def test_create_character_invalid_ability_scores(db_session: AsyncSession):
    """Test character creation with invalid ability scores."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    
    # Test scores too low
    invalid_scores = create_test_ability_scores(strength=2)
    with pytest.raises(CharacterValidationError, match=r"strength score must be between.*"):
        await service.create_character(
            name="Test Character",
            ability_scores=invalid_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        )
    
    # Test scores too high
    invalid_scores = create_test_ability_scores(dexterity=19)
    with pytest.raises(CharacterValidationError, match=r"dexterity score must be between.*"):
        await service.create_character(
            name="Test Character",
            ability_scores=invalid_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        )


@pytest.mark.asyncio
async def test_create_character_invalid_class(db_session: AsyncSession):
    """Test character creation with invalid class."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Act & Assert
    with pytest.raises(CharacterValidationError, match=r"Invalid character class.*"):
        await service.create_character(
            name="Test Character",
            ability_scores=ability_scores,
            race="Human",
            character_class="InvalidClass",
            background="Soldier"
        )


@pytest.mark.asyncio
async def test_create_character_invalid_level(db_session: AsyncSession):
    """Test character creation with invalid level."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Test level too low
    with pytest.raises(CharacterCreationError, match=r"Level must be between.*"):
        await service.create_character(
            name="Test Character",
            ability_scores=ability_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier",
            level=0
        )
    
    # Test level too high
    with pytest.raises(CharacterCreationError, match=r"Level must be between.*"):
        await service.create_character(
            name="Test Character",
            ability_scores=ability_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier",
            level=21
        )


@pytest.mark.asyncio
async def test_create_character_hp_calculation(db_session: AsyncSession):
    """Test HP calculation for different classes and levels."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Test Fighter HP calculation
    fighter = await service.create_character(
        name="Fighter Test",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=3
    )
    # Level 1: 10 (hit die) + 1 (con mod) = 11
    # Level 2-3: 2 * (6 (avg) + 1 (con mod)) = 14
    # Total: 25
    assert fighter.max_hit_points == 25
    
    # Test Wizard HP calculation
    wizard = await service.create_character(
        name="Wizard Test",
        ability_scores=ability_scores,
        race="Human",
        character_class="Wizard",
        background="Sage",
        level=3
    )
    # Level 1: 6 (hit die) + 1 (con mod) = 7
    # Level 2-3: 2 * (4 (avg) + 1 (con mod)) = 10
    # Total: 17
    assert wizard.max_hit_points == 17


@pytest.mark.asyncio
async def test_level_up_increases_hp(db_session: AsyncSession):
    """Test that leveling up increases max and current HP appropriately."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores(constitution=14)  # CON mod +2
    
    # Create a level 1 Fighter (d10)
    character = await service.create_character(
        name="Level Up Test",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=1
    )
    
    # Sanity check level 1 HP: 10 + 2 = 12
    assert character.max_hit_points == 12
    
    # Act: level up to 2
    leveled = await service.level_up(character.id)
    
# Assert: average HP gain at level up: average (10/2 + 1) + 2 = 6 + 2 = 8
    assert leveled.level == 2
    assert leveled.max_hit_points == 20  # 12 + 8
    assert leveled.current_hit_points == 20


@pytest.mark.asyncio
async def test_level_cap_enforced(db_session: AsyncSession):
    """Test that leveling beyond max level is prevented."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Create a level 20 Wizard
    character = await service.create_character(
        name="Max Level Wizard",
        ability_scores=ability_scores,
        race="Human",
        character_class="Wizard",
        background="Sage",
        level=CharacterService.MAX_LEVEL
    )
    
    # Act & Assert
    with pytest.raises(CharacterValidationError, match=r"maximum level"):
        await service.level_up(character.id)


@pytest.mark.asyncio
async def test_hp_recalculates_with_con_change(db_session: AsyncSession):
    """Test that HP recalculates appropriately when CON changes at higher levels."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    
    # Start with CON 12 (mod +1), Fighter level 5
    ability_scores = create_test_ability_scores(constitution=12)
    character = await service.create_character(
        name="CON Change",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=5
    )
    original_max_hp = character.max_hit_points
    original_current_hp = character.current_hit_points
    
    # Increase CON to 14 (mod +2)
    updated_scores = create_test_ability_scores(constitution=14)
    updated = await service.update_ability_scores(character.id, updated_scores)
    
    # Assert: max HP should increase; current HP adjusts proportionally
    assert updated.max_hit_points > original_max_hp
    # Ratio of current to max should remain approximately the same (integer rounding)
    assert abs((updated.current_hit_points / updated.max_hit_points) - (original_current_hp / original_max_hp)) < 0.05


@pytest.mark.asyncio
async def test_add_fighter_features_by_level(db_session: AsyncSession):
    """Test adding Fighter features at specific levels."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Create a Fighter
    fighter = await service.create_character(
        name="Fighter Features",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=1
    )
    
    # Act: add level 1 features
    features_lvl1 = await service.add_class_features(fighter.id, 1)
    
    # Assert
    assert any(f.name == "Fighting Style" for f in features_lvl1)
    assert any(f.name == "Second Wind" for f in features_lvl1)
    
    # Act: add level 2 features
    features_lvl2 = await service.add_class_features(fighter.id, 2)
    assert any(f.name == "Action Surge" for f in features_lvl2)
    
    # Verify features persisted on character
    stored = await repo.get(fighter.id)
    assert stored is not None
    names = [f.name for f in stored.features]
    assert "Fighting Style" in names
    assert "Second Wind" in names
    assert "Action Surge" in names


@pytest.mark.asyncio
async def test_reset_features_on_rest(db_session: AsyncSession):
    """Test resetting feature uses on rests."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    wizard = await service.create_character(
        name="Wizard Features",
        ability_scores=ability_scores,
        race="Human",
        character_class="Wizard",
        background="Sage",
        level=1
    )
    
    # Add level 1 features (Spellcasting, Arcane Recovery)
    features = await service.add_class_features(wizard.id, 1)
    arcane_recovery = next(f for f in features if f.name == "Arcane Recovery")
    
    # Simulate use
    arcane_recovery.uses_remaining = 0
    await repo.update(wizard)
    
    # Short rest should reset Arcane Recovery
    reset_short = await service.reset_features(wizard.id, rest_type=ResourceType.SHORT_REST)
    
    # Get updated character
    updated = await repo.get(wizard.id)
    arcane_recovery = next(f for f in updated.features if f.name == "Arcane Recovery")
    assert arcane_recovery.uses_remaining == arcane_recovery.uses_max
    assert any(f.name == "Arcane Recovery" for f in reset_short)
    
    # Set uses to 0 again and test long rest also resets
    arcane_recovery.uses_remaining = 0
    await repo.update(wizard)
    reset_long = await service.reset_features(wizard.id, rest_type=ResourceType.LONG_REST)
    assert any(f.name == "Arcane Recovery" for f in reset_long)


@pytest.mark.asyncio
async def test_multiclass_adds_new_class_and_features(db_session: AsyncSession):
    """Test adding a new class to a character and gaining level 1 features."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    # High INT to meet Wizard multiclass prereq (13)
    ability_scores = create_test_ability_scores(intelligence=14)
    fighter = await service.create_character(
        name="MC Fighter",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=3
    )

    # Act: add Wizard class
    updated = await service.add_class(fighter.id, "Wizard")

    # Assert: classes includes both Fighter and Wizard
    assert updated.classes is not None
    class_names = [c["class"] for c in updated.classes]
    assert "Fighter" in class_names and "Wizard" in class_names

    # Wizard level 1 features added
    names = [f.name for f in updated.features]
    assert "Spellcasting" in names
    assert "Arcane Recovery" in names


@pytest.mark.asyncio
async def test_multiclass_prereq_validation(db_session: AsyncSession):
    """Test that multiclassing enforces ability score prerequisites."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    # INT too low for Wizard multiclass
    ability_scores = create_test_ability_scores(intelligence=12)
    fighter = await service.create_character(
        name="MC Prereq",
        ability_scores=ability_scores,
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=3
    )

    # Act & Assert: adding Wizard should fail
    with pytest.raises(CharacterValidationError, match="prerequisites"):
        await service.add_class(fighter.id, "Wizard")
