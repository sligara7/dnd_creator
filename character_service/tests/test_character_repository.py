"""Tests for the character repository."""
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository, SortOrder

@pytest.mark.asyncio
async def test_create_character(db_session: AsyncSession):
    """Test creating a new character."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    
    # Act
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Assert
    assert created_character.id is not None
    assert created_character.name == "Test Character"
    assert created_character.level == 1
    assert created_character.strength == 15
    assert created_character.race == "Human"
    assert created_character.character_class == "Fighter"
    assert created_character.is_deleted == False
    assert created_character.created_at is not None
    assert created_character.updated_at is not None


@pytest.mark.asyncio
async def test_get_character(db_session: AsyncSession):
    """Test retrieving a character by ID."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Act
    retrieved_character = await repo.get(created_character.id)
    
    # Assert
    assert retrieved_character is not None
    assert retrieved_character.id == created_character.id
    assert retrieved_character.name == "Test Character"
    assert retrieved_character.level == 1
    assert retrieved_character.strength == 15
    assert retrieved_character.race == "Human"
    assert retrieved_character.character_class == "Fighter"
    assert retrieved_character.is_deleted == False


@pytest.mark.asyncio
async def test_get_non_existent_character(db_session: AsyncSession):
    """Test retrieving a non-existent character."""
    # Arrange
    repo = CharacterRepository(db_session)
    non_existent_id = UUID('00000000-0000-0000-0000-000000000000')
    
    # Act
    retrieved_character = await repo.get(non_existent_id)
    
    # Assert
    assert retrieved_character is None


@pytest.mark.asyncio
async def test_get_deleted_character(db_session: AsyncSession):
    """Test retrieving a soft-deleted character."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Soft delete the character
    await repo.delete(created_character.id)
    await db_session.flush()
    
    # Act
    retrieved_character = await repo.get(created_character.id)
    
    # Assert
    assert retrieved_character is None


@pytest.mark.asyncio
async def test_update_basic_fields(db_session: AsyncSession):
    """Test updating basic character fields."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Update basic fields
    created_character.name = "Updated Character"
    created_character.level = 2
    created_character.background = "Noble"
    
    # Act
    updated_character = await repo.update(created_character)
    await db_session.flush()
    
    # Verify the update
    retrieved_character = await repo.get(created_character.id)
    
    # Assert
    assert retrieved_character is not None
    assert retrieved_character.name == "Updated Character"
    assert retrieved_character.level == 2
    assert retrieved_character.background == "Noble"
    # Original fields should remain unchanged
    assert retrieved_character.strength == 15
    assert retrieved_character.race == "Human"
    assert retrieved_character.character_class == "Fighter"


@pytest.mark.asyncio
async def test_update_ability_scores(db_session: AsyncSession):
    """Test updating character ability scores."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Update ability scores
    created_character.strength = 16
    created_character.dexterity = 15
    created_character.constitution = 14
    created_character.intelligence = 13
    created_character.wisdom = 12
    created_character.charisma = 10
    
    # Act
    updated_character = await repo.update(created_character)
    await db_session.flush()
    
    # Verify the update
    retrieved_character = await repo.get(created_character.id)
    
    # Assert
    assert retrieved_character is not None
    assert retrieved_character.strength == 16
    assert retrieved_character.dexterity == 15
    assert retrieved_character.constitution == 14
    assert retrieved_character.intelligence == 13
    assert retrieved_character.wisdom == 12
    assert retrieved_character.charisma == 10
    # Other fields should remain unchanged
    assert retrieved_character.name == "Test Character"
    assert retrieved_character.level == 1


@pytest.mark.asyncio
async def test_update_combat_stats(db_session: AsyncSession):
    """Test updating character combat statistics."""
    # Arrange
    repo = CharacterRepository(db_session)
    new_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        temporary_hit_points=0,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    created_character = await repo.create(new_character)
    await db_session.flush()
    
    # Update combat stats
    created_character.max_hit_points = 15
    created_character.current_hit_points = 12
    created_character.temporary_hit_points = 5
    
    # Act
    updated_character = await repo.update(created_character)
    await db_session.flush()
    
    # Verify the update
    retrieved_character = await repo.get(created_character.id)
    
    # Assert
    assert retrieved_character is not None
    assert retrieved_character.max_hit_points == 15
    assert retrieved_character.current_hit_points == 12
    assert retrieved_character.temporary_hit_points == 5
    # Other fields should remain unchanged
    assert retrieved_character.name == "Test Character"
    assert retrieved_character.strength == 15
    assert retrieved_character.level == 1


@pytest.mark.asyncio
async def test_list_characters(db_session: AsyncSession):
    """Test retrieving all non-deleted characters."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create multiple characters
    characters = [
        Character(
            name=f"Test Character {i}",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for i in range(3)
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act
    retrieved_characters = await repo.get_all()
    
    # Assert
    assert len(retrieved_characters) == 3
    for i, character in enumerate(retrieved_characters):
        assert character.name == f"Test Character {i}"
        assert character.level == 1
        assert character.race == "Human"
        assert character.is_deleted == False


@pytest.mark.asyncio
async def test_list_empty_characters(db_session: AsyncSession):
    """Test listing characters when none exist."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Act
    characters = await repo.get_all()
    
    # Assert
    assert len(characters) == 0
    assert isinstance(characters, list)


@pytest.mark.asyncio
async def test_list_with_deleted_characters(db_session: AsyncSession):
    """Test that soft-deleted characters are excluded from list."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters
    characters = [
        Character(
            name=f"Test Character {i}",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for i in range(3)
    ]
    
    # Create and store characters
    stored_characters = []
    for character in characters:
        created = await repo.create(character)
        stored_characters.append(created)
    await db_session.flush()
    
    # Soft delete the second character
    await repo.delete(stored_characters[1].id)
    await db_session.flush()
    
    # Act
    active_characters = await repo.get_all()
    
    # Assert
    assert len(active_characters) == 2
    assert active_characters[0].name == "Test Character 0"
    assert active_characters[1].name == "Test Character 2"
    for character in active_characters:
        assert character.is_deleted == False


@pytest.mark.asyncio
async def test_filter_by_level(db_session: AsyncSession):
    """Test filtering characters by level range."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters of different levels
    levels = [1, 3, 5, 7, 10]
    characters = [
        Character(
            name=f"Level {level} Character",
            level=level,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for level in levels
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act & Assert
    # Test min level only
    filtered = await repo.filter_by_level(min_level=5)
    assert len(filtered) == 3  # Should get levels 5, 7, 10
    assert all(c.level >= 5 for c in filtered)
    
    # Test level range
    filtered = await repo.filter_by_level(min_level=3, max_level=7)
    assert len(filtered) == 3  # Should get levels 3, 5, 7
    assert all(3 <= c.level <= 7 for c in filtered)


@pytest.mark.asyncio
async def test_filter_by_class(db_session: AsyncSession):
    """Test filtering characters by character class."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters of different classes
    classes = ["Fighter", "Wizard", "Cleric", "Fighter", "Rogue"]
    characters = [
        Character(
            name=f"{class_name} Character",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class=class_name,
            background="Soldier"
        ) for class_name in classes
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act
    fighters = await repo.filter_by_class("Fighter")
    wizards = await repo.filter_by_class("Wizard")
    
    # Assert
    assert len(fighters) == 2
    assert all(c.character_class == "Fighter" for c in fighters)
    assert len(wizards) == 1
    assert wizards[0].character_class == "Wizard"


@pytest.mark.asyncio
async def test_filter_by_race(db_session: AsyncSession):
    """Test filtering characters by race."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters of different races
    races = ["Human", "Elf", "Dwarf", "Human", "Halfling"]
    characters = [
        Character(
            name=f"{race} Character",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race=race,
            character_class="Fighter",
            background="Soldier"
        ) for race in races
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act
    humans = await repo.filter_by_race("Human")
    elves = await repo.filter_by_race("Elf")
    
    # Assert
    assert len(humans) == 2
    assert all(c.race == "Human" for c in humans)
    assert len(elves) == 1
    assert elves[0].race == "Elf"


@pytest.mark.asyncio
async def test_filter_by_multiple_criteria(db_session: AsyncSession):
    """Test filtering characters by multiple criteria."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create various characters
    test_characters = [
        # Human Fighters
        Character(
            name="Human Fighter 1",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ),
        Character(
            name="Human Fighter 5",
            level=5,
            strength=16,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=45,
            current_hit_points=45,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ),
        # Elf Wizard
        Character(
            name="Elf Wizard 1",
            level=1,
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=16,
            wisdom=10,
            charisma=12,
            max_hit_points=6,
            current_hit_points=6,
            race="Elf",
            character_class="Wizard",
            background="Sage"
        )
    ]
    
    for character in test_characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act & Assert
    # Test filtering by race and class
    human_fighters = await repo.filter_by_criteria({
        "race": "Human",
        "character_class": "Fighter"
    })
    assert len(human_fighters) == 2
    assert all(c.race == "Human" and c.character_class == "Fighter" for c in human_fighters)
    
    # Test filtering by race, class, and level
    level_1_human_fighters = await repo.filter_by_criteria({
        "race": "Human",
        "character_class": "Fighter",
        "level": 1
    })
    assert len(level_1_human_fighters) == 1
    assert level_1_human_fighters[0].name == "Human Fighter 1"


@pytest.mark.asyncio
async def test_sort_by_level(db_session: AsyncSession):
    """Test sorting characters by level."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters of different levels
    levels = [5, 1, 10, 3, 7]
    characters = [
        Character(
            name=f"Level {level} Character",
            level=level,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for level in levels
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act & Assert
    # Test ascending order
    sorted_asc = await repo.get_sorted("level")
    assert len(sorted_asc) == 5
    assert [c.level for c in sorted_asc] == [1, 3, 5, 7, 10]
    
    # Test descending order
    sorted_desc = await repo.get_sorted("level", SortOrder.DESC)
    assert len(sorted_desc) == 5
    assert [c.level for c in sorted_desc] == [10, 7, 5, 3, 1]


@pytest.mark.asyncio
async def test_sort_by_name(db_session: AsyncSession):
    """Test sorting characters by name."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters with different names
    names = ["Zorro", "Aragorn", "Merlin", "Conan", "Bilbo"]
    characters = [
        Character(
            name=name,
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for name in names
    ]
    
    for character in characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act
    sorted_chars = await repo.get_sorted("name")
    
    # Assert
    assert len(sorted_chars) == 5
    assert [c.name for c in sorted_chars] == sorted(names)


@pytest.mark.asyncio
async def test_sort_by_multiple_fields(db_session: AsyncSession):
    """Test sorting characters by multiple fields."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters with various combinations
    test_characters = [
        Character(
            name="Fighter A",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ),
        Character(
            name="Fighter B",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ),
        Character(
            name="Wizard A",
            level=3,
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=16,
            wisdom=12,
            charisma=10,
            max_hit_points=16,
            current_hit_points=16,
            race="Elf",
            character_class="Wizard",
            background="Sage"
        ),
        Character(
            name="Wizard B",
            level=3,
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=16,
            wisdom=12,
            charisma=10,
            max_hit_points=16,
            current_hit_points=16,
            race="Elf",
            character_class="Wizard",
            background="Sage"
        )
    ]
    
    for character in test_characters:
        await repo.create(character)
    await db_session.flush()
    
    # Act
    # Sort by class ascending, then name ascending
    sorted_chars = await repo.get_sorted([
        ("character_class", SortOrder.ASC),
        ("name", SortOrder.ASC)
    ])
    
    # Assert
    assert len(sorted_chars) == 4
    assert [c.name for c in sorted_chars] == ["Fighter A", "Fighter B", "Wizard A", "Wizard B"]
    
    # Test different sort orders
    # Sort by class descending, then name descending
    sorted_chars_desc = await repo.get_sorted([
        ("character_class", SortOrder.DESC),
        ("name", SortOrder.DESC)
    ])
    
    assert len(sorted_chars_desc) == 4
    assert [c.name for c in sorted_chars_desc] == ["Wizard B", "Wizard A", "Fighter B", "Fighter A"]


@pytest.mark.asyncio
async def test_sort_invalid_field(db_session: AsyncSession):
    """Test sorting with invalid field raises error."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid sort field: invalid_field"):
        await repo.get_sorted("invalid_field")
    
    with pytest.raises(ValueError, match="Invalid sort field: invalid_field"):
        await repo.get_sorted([("invalid_field", SortOrder.ASC)])


@pytest.mark.asyncio
async def test_batch_create(db_session: AsyncSession):
    """Test creating multiple characters in a single operation."""
    # Arrange
    repo = CharacterRepository(db_session)
    characters = [
        Character(
            name=f"Character {i}",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for i in range(3)
    ]
    
    # Act
    created_characters = await repo.batch_create(characters)
    await db_session.flush()
    
    # Assert
    assert len(created_characters) == 3
    for i, character in enumerate(created_characters):
        assert character.id is not None
        assert character.name == f"Character {i}"
        assert character.is_deleted == False
        assert character.created_at is not None
        assert character.updated_at is not None


@pytest.mark.asyncio
async def test_batch_update(db_session: AsyncSession):
    """Test updating multiple characters in a single operation."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create initial characters
    characters = [
        Character(
            name=f"Character {i}",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for i in range(3)
    ]
    created_characters = await repo.batch_create(characters)
    await db_session.flush()
    
    # Update characters
    for char in created_characters:
        char.level = 2
        char.max_hit_points = 20
        char.current_hit_points = 20
    
    # Act
    updated_characters = await repo.batch_update(created_characters)
    await db_session.flush()
    
    # Verify updates
    for char_id in [c.id for c in updated_characters]:
        retrieved_char = await repo.get(char_id)
        assert retrieved_char is not None
        assert retrieved_char.level == 2
        assert retrieved_char.max_hit_points == 20
        assert retrieved_char.current_hit_points == 20


@pytest.mark.asyncio
async def test_batch_delete(db_session: AsyncSession):
    """Test deleting multiple characters in a single operation."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Create characters
    characters = [
        Character(
            name=f"Character {i}",
            level=1,
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
            max_hit_points=10,
            current_hit_points=10,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        ) for i in range(3)
    ]
    created_characters = await repo.batch_create(characters)
    await db_session.flush()
    
    # Act
    deleted_count = await repo.batch_delete([c.id for c in created_characters])
    await db_session.flush()
    
    # Assert
    assert deleted_count == 3
    
    # Verify all characters are soft deleted
    for char_id in [c.id for c in created_characters]:
        retrieved_char = await repo.get(char_id)
        assert retrieved_char is None


@pytest.mark.asyncio
async def test_batch_operations_validation(db_session: AsyncSession):
    """Test validation and error handling for batch operations."""
    # Arrange
    repo = CharacterRepository(db_session)
    
    # Test empty batch create
    with pytest.raises(ValueError, match="Cannot create empty list of characters"):
        await repo.batch_create([])
    
    # Test empty batch update
    with pytest.raises(ValueError, match="Cannot update empty list of characters"):
        await repo.batch_update([])
    
    # Test empty batch delete
    with pytest.raises(ValueError, match="Cannot delete empty list of characters"):
        await repo.batch_delete([])
    
    # Create a character for partial batch operations
    single_character = Character(
        name="Test Character",
        level=1,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        max_hit_points=10,
        current_hit_points=10,
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    await repo.create(single_character)
    await db_session.flush()
    
    # Test batch delete with mix of existing and non-existent IDs
    non_existent_id = UUID('00000000-0000-0000-0000-000000000000')
    deleted_count = await repo.batch_delete([single_character.id, non_existent_id])
    assert deleted_count == 1  # Only existing character should be deleted
