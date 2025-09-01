"""Character service module."""
from typing import Dict, List, Optional, Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character


class CharacterService:
    """Service for managing characters."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.spellcasting_classes = {
            "Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Paladin", "Ranger"
        }

    async def create_character(self, character_data: Dict[str, Any]) -> Character:
        """Create a new character."""
        # Validate data
        self._validate_character_data(character_data)

        # Check for duplicate names
        duplicate_name = await self._check_duplicate_name(character_data["name"])

        # Create character instance
        character = Character(
            id=character_data.get("id", str(uuid4())),
            name=character_data["name"],
            user_id=character_data["user_id"],
            campaign_id=character_data["campaign_id"],
            species=character_data["species"],
            background=character_data["background"],
            level=character_data.get("level", 1),
            character_classes=character_data["character_classes"],
            ability_scores=character_data["ability_scores"],
            equipment=character_data.get("equipment", []),
            spells_known=character_data.get("spells_known", []),
            spells_prepared=character_data.get("spells_prepared", []),
            features=character_data.get("features", []),
            warnings=["duplicate_name"] if duplicate_name else None
        )

        # Apply racial bonuses
        if racial_bonuses := character_data.get("racial_bonuses"):
            self._apply_racial_bonuses(character, racial_bonuses)

        # Calculate derived attributes
        self._calculate_hit_points(character)
        self._calculate_armor_class(character)
        self._calculate_proficiency_bonus(character)
        
        # Handle spellcasting
        if self._is_spellcaster(character):
            self._setup_spellcasting(character)

        # Save to database
        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)

        return character

    def _validate_character_data(self, data: Dict[str, Any]) -> None:
        """Validate character data."""
        required_fields = ["name", "species", "background", "character_classes", "ability_scores", "user_id", "campaign_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate ability scores
        for ability, score in data["ability_scores"].items():
            if not 1 <= score <= 20:
                raise ValueError(f"Invalid ability score for {ability}: {score}")

    async def _check_duplicate_name(self, name: str) -> bool:
        """Check if character name already exists."""
        query = select(Character).where(Character.name == name)
        result = await self.db.execute(query)
        return result.first() is not None

    def _apply_racial_bonuses(self, character: Character, bonuses: Dict[str, int]) -> None:
        """Apply racial ability score bonuses."""
        character.racial_bonuses = bonuses
        for ability, bonus in bonuses.items():
            current_score = character.ability_scores[ability]
            character.ability_scores[ability] = min(20, current_score + bonus)

    def _calculate_hit_points(self, character: Character) -> None:
        """Calculate character's hit points."""
        # Get primary class and its hit die
        primary_class = next(iter(character.character_classes))
        hit_die_sizes = {
            "Barbarian": 12,
            "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Cleric": 8, "Druid": 8, "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8,
            "Sorcerer": 6, "Wizard": 6
        }
        hit_die = hit_die_sizes.get(primary_class, 8)

        # Calculate HP: max hit die + Constitution modifier for first level
        con_mod = character.get_ability_modifier("constitution")
        hp = hit_die + con_mod  # First level

        # Add average HP for remaining levels
        for class_name, level in character.character_classes.items():
            if level > 1:
                class_hit_die = hit_die_sizes.get(class_name, 8)
                # Use average roll (half of hit die + 1) for remaining levels
                hp += (class_hit_die // 2 + 1 + con_mod) * (level - 1)

        character.hit_points = hp

    def _calculate_armor_class(self, character: Character) -> None:
        """Calculate character's armor class."""
        # Base AC 10 + Dexterity modifier (unarmored)
        dex_mod = character.get_ability_modifier("dexterity")
        character.armor_class = 10 + dex_mod

    def _calculate_proficiency_bonus(self, character: Character) -> None:
        """Calculate character's proficiency bonus based on level."""
        character.proficiency_bonus = 2 + ((character.level - 1) // 4)

    def _is_spellcaster(self, character: Character) -> bool:
        """Check if character is a spellcaster."""
        return any(
            class_name in self.spellcasting_classes
            for class_name in character.character_classes
        )

    def _setup_spellcasting(self, character: Character) -> None:
        """Setup spellcasting attributes for spellcasting classes."""
        # Get primary spellcasting class
        spellcasting_abilities = {
            "Wizard": "intelligence",
            "Cleric": "wisdom", "Druid": "wisdom", "Ranger": "wisdom",
            "Sorcerer": "charisma", "Warlock": "charisma", 
            "Bard": "charisma", "Paladin": "charisma"
        }

        # Find the highest level spellcasting class
        primary_class = None
        highest_level = 0
        for class_name, level in character.character_classes.items():
            if class_name in spellcasting_abilities:
                if level > highest_level:
                    primary_class = class_name
                    highest_level = level

        # Set spellcasting ability for highest level spellcasting class
        character.spellcasting_ability = spellcasting_abilities.get(primary_class)

        # Calculate spell save DC if applicable
        if character.spellcasting_ability:
            ability_mod = character.get_ability_modifier(character.spellcasting_ability)
            character.spell_save_dc = 8 + character.proficiency_bonus + ability_mod

    async def get_character(self, character_id: str) -> Character:
        """Get a character by ID."""
        query = select(Character).where(Character.id == character_id)
        result = await self.db.execute(query)
        character = result.scalars().first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")
        return character

    async def level_up(self, character_id: str, level_up_data: Dict[str, Any]) -> Character:
        """Level up a character."""
        character = await self.get_character(character_id)

        # Validate level up data
        self._validate_level_up(character, level_up_data)

        # Update basic attributes
        character.level = level_up_data["level"]
        character.character_classes = level_up_data["character_classes"]

        # Handle hit points
        new_hp = self._calculate_level_up_hp(character, level_up_data)
        character.hit_points = new_hp

        # Handle spellcasting
        self._setup_spellcasting(character)

        # Handle spells known if applicable
        if spells_added := level_up_data.get("spells_added"):
            current_spells = character.spells_known or []
            character.spells_known = current_spells + spells_added

        # Save changes
        await self.db.commit()
        await self.db.refresh(character)

        return character

    def _validate_level_up(self, character: Character, level_up_data: Dict[str, Any]) -> None:
        """Validate level up data."""
        # Check level progression
        if level_up_data["level"] != character.level + 1:
            raise ValueError("Cannot skip levels")

        # Validate new class levels
        if sum(level_up_data["character_classes"].values()) != level_up_data["level"]:
            raise ValueError("Total class levels must equal character level")

        # Check if all classes exist in current classes or meet multiclass requirements
        for class_name, level in level_up_data["character_classes"].items():
            if class_name not in character.character_classes:
                self._validate_multiclass_requirements(character, class_name)

    def _validate_multiclass_requirements(self, character: Character, new_class: str) -> None:
        """Validate multiclass requirements."""
        requirements = {
            "Barbarian": {"strength": 13},
            "Bard": {"charisma": 13},
            "Cleric": {"wisdom": 13},
            "Druid": {"wisdom": 13},
            "Fighter": {"strength": 13, "dexterity": 13},
            "Monk": {"dexterity": 13, "wisdom": 13},
            "Paladin": {"strength": 13, "charisma": 13},
            "Ranger": {"dexterity": 13, "wisdom": 13},
            "Rogue": {"dexterity": 13},
            "Sorcerer": {"charisma": 13},
            "Warlock": {"charisma": 13},
            "Wizard": {"intelligence": 13}
        }

        if new_class in requirements:
            for ability, min_score in requirements[new_class].items():
                if character.ability_scores[ability] < min_score:
                    raise ValueError(f"Does not meet requirements for {new_class} multiclass")

    def _calculate_level_up_hp(self, character: Character, level_up_data: Dict[str, Any]) -> int:
        """Calculate new hit points after level up."""
        # Get hit die size for the new class level
        new_class = None
        for class_name, level in level_up_data["character_classes"].items():
            if level > character.character_classes.get(class_name, 0):
                new_class = class_name
                break

        hit_die_sizes = {
            "Barbarian": 12,
            "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Cleric": 8, "Druid": 8, "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8,
            "Sorcerer": 6, "Wizard": 6
        }
        hit_die = hit_die_sizes.get(new_class, 8)

        # Add Constitution modifier and rolled value
        con_mod = character.get_ability_modifier("constitution")
        return character.hit_points + level_up_data["hp_roll"] + con_mod
