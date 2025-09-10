"""Character service with business logic and validation rules."""
from datetime import UTC, datetime
from typing import Dict, List, Optional, TypedDict, cast, Any
from uuid import UUID

from character_service.models.character import Character
from character_service.models.features import Feature, FeatureType, ResourceType, Proficiency
from character_service.repositories.character import CharacterRepository


class AbilityScores(TypedDict):
    """Type for ability scores."""
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class CharacterCreationError(Exception):
    """Error raised when character creation validation fails."""
    pass


class CharacterValidationError(Exception):
    """Error raised when character validation fails."""
    pass


class CharacterService:
    """Service for character-related business logic."""

    # Constants for validation
    MIN_ABILITY_SCORE = 3
    MAX_ABILITY_SCORE = 18
    MIN_LEVEL = 1
    MAX_LEVEL = 20

    # Class features by level
    CLASS_FEATURES = {
        "Fighter": {
            1: [
                ("Fighting Style", "Choose a fighting style", ResourceType.PERMANENT),
                ("Second Wind", "Regain 1d10 + level HP", ResourceType.SHORT_REST)
            ],
            2: [("Action Surge", "Take an additional action", ResourceType.SHORT_REST)],
            3: [("Martial Archetype", "Choose a fighter archetype", ResourceType.PERMANENT)],
            5: [("Extra Attack", "Attack twice when taking Attack action", ResourceType.PERMANENT)],
            9: [("Indomitable", "Reroll a failed saving throw", ResourceType.LONG_REST)]
        },
        "Wizard": {
            1: [
                ("Spellcasting", "Cast wizard spells", ResourceType.PERMANENT),
                ("Arcane Recovery", "Recover spell slots on short rest", ResourceType.SHORT_REST)
            ],
            2: [("Arcane Tradition", "Choose a wizard school", ResourceType.PERMANENT)],
            3: [("Cantrip Formulas", "Swap cantrips on long rest", ResourceType.PERMANENT)],
            4: [("Ability Score Improvement", "+2 to one ability score", ResourceType.PERMANENT)]
        }
    }

    # Hit die by class
    HIT_DIE = {
        "Barbarian": 12,
        "Fighter": 10,
        "Paladin": 10,
        "Ranger": 10,
        "Cleric": 8,
        "Druid": 8,
        "Monk": 8,
        "Rogue": 8,
        "Warlock": 8,
        "Bard": 8,
        "Sorcerer": 6,
        "Wizard": 6
    }

    # Multiclass prerequisites (simplified): ability score minimums
    MULTICLASS_PREREQS: Dict[str, Dict[str, int]] = {
        "Fighter": {"strength": 13},
        "Wizard": {"intelligence": 13},
        # Add other classes as needed
    }

    def __init__(self, repository: CharacterRepository):
        """Initialize the service.
        
        Args:
            repository: Character repository instance
        """
        self.repository = repository

    def _validate_ability_scores(self, scores: AbilityScores) -> None:
        """Validate ability scores.
        
        Args:
            scores: Dictionary of ability scores
            
        Raises:
            CharacterValidationError: If scores are invalid
        """
        for ability, score in scores.items():
            if not isinstance(score, int):
                raise CharacterValidationError(f"{ability} score must be an integer")
            if score < self.MIN_ABILITY_SCORE or score > self.MAX_ABILITY_SCORE:
                raise CharacterValidationError(
                    f"{ability} score must be between {self.MIN_ABILITY_SCORE} "
                    f"and {self.MAX_ABILITY_SCORE}"
                )

    def _validate_class(self, character_class: str) -> None:
        """Validate character class.
        
        Args:
            character_class: Character's class
            
        Raises:
            CharacterValidationError: If class is invalid
        """
        if character_class not in self.HIT_DIE:
            raise CharacterValidationError(
                f"Invalid character class: {character_class}. "
                f"Must be one of {list(self.HIT_DIE.keys())}"
            )

    def _calculate_max_hp(self, character_class: str, constitution: int, level: int) -> int:
        """Calculate maximum hit points.
        
        Args:
            character_class: Character's class
            constitution: Constitution score
            level: Character level
            
        Returns:
            Maximum hit points
        """
        con_mod = (constitution - 10) // 2
        hit_die = self.HIT_DIE[character_class]
        
        # First level gets maximum HP
        max_hp = hit_die + con_mod
        
        # Additional levels get average HP
        if level > 1:
            average_hp = (hit_die / 2 + 1 + con_mod) * (level - 1)
            max_hp += int(average_hp)
        
        return max_hp

    async def create_character(
        self,
        name: str,
        ability_scores: AbilityScores,
        race: str,
        character_class: str,
        background: str,
        level: int = 1
    ) -> Character:
        """Create a new character with validation.
        
        Args:
            name: Character name
            ability_scores: Dictionary of ability scores
            race: Character race
            character_class: Character class
            background: Character background
            level: Starting level (default: 1)
            
        Returns:
            Created character
            
        Raises:
            CharacterCreationError: If validation fails
        """
        # Validate inputs
        if not name:
            raise CharacterCreationError("Character name is required")

        if level < self.MIN_LEVEL or level > self.MAX_LEVEL:
            raise CharacterCreationError(
                f"Level must be between {self.MIN_LEVEL} and {self.MAX_LEVEL}"
            )

        self._validate_ability_scores(ability_scores)
        self._validate_class(character_class)

        # Calculate derived stats
        max_hp = self._calculate_max_hp(
            character_class,
            ability_scores["constitution"],
            level
        )

        # Create character
        character = Character(
            name=name,
            level=level,
            strength=ability_scores["strength"],
            dexterity=ability_scores["dexterity"],
            constitution=ability_scores["constitution"],
            intelligence=ability_scores["intelligence"],
            wisdom=ability_scores["wisdom"],
            charisma=ability_scores["charisma"],
            max_hit_points=max_hp,
            current_hit_points=max_hp,
            temporary_hit_points=0,
            race=race,
            character_class=character_class,
            background=background,
            classes=[{"class": character_class, "level": level}]
        )

        return await self.repository.create(character)

    async def update_ability_scores(
        self,
        character_id: UUID,
        ability_scores: AbilityScores
    ) -> Character:
        """Update character ability scores with validation.
        
        Args:
            character_id: Character ID
            ability_scores: New ability scores
            
        Returns:
            Updated character
            
        Raises:
            CharacterValidationError: If validation fails
        """
        # Validate scores
        self._validate_ability_scores(ability_scores)

        # Get current character
        character = await self.repository.get(character_id)
        if not character:
            raise CharacterValidationError("Character not found")

        # Update scores
        character.strength = ability_scores["strength"]
        character.dexterity = ability_scores["dexterity"]
        character.constitution = ability_scores["constitution"]
        character.intelligence = ability_scores["intelligence"]
        character.wisdom = ability_scores["wisdom"]
        character.charisma = ability_scores["charisma"]

        # Recalculate max HP if constitution changed
        new_max_hp = self._calculate_max_hp(
            character.character_class,
            ability_scores["constitution"],
            character.level
        )
        
        # Adjust current HP proportionally if max HP changed
        if new_max_hp != character.max_hit_points:
            hp_ratio = character.current_hit_points / character.max_hit_points
            character.max_hit_points = new_max_hp
            character.current_hit_points = int(new_max_hp * hp_ratio)

        return await self.repository.update(character)

    async def level_up(self, character_id: UUID) -> Character:
        """Level up a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            Updated character
            
        Raises:
            CharacterValidationError: If validation fails
        """
        character = await self.repository.get(character_id)
        if not character:
            raise CharacterValidationError("Character not found")

        if character.level >= self.MAX_LEVEL:
            raise CharacterValidationError(f"Character is already at maximum level ({self.MAX_LEVEL})")

        # Calculate new max HP
        old_max_hp = character.max_hit_points
        character.level += 1
        new_max_hp = self._calculate_max_hp(
            character.character_class,
            character.constitution,
            character.level
        )
        
        # Update HP
        hp_increase = new_max_hp - old_max_hp
        character.max_hit_points = new_max_hp
        character.current_hit_points += hp_increase

        return await self.repository.update(character)

    def validate_combat_stats(self, character: Character) -> None:
        """Validate combat-related statistics.
        
        Args:
            character: Character to validate
            
        Raises:
            CharacterValidationError: If validation fails
        """
        if character.max_hit_points < 1:
            raise CharacterValidationError("Maximum hit points must be at least 1")
        
        if character.current_hit_points > character.max_hit_points + character.temporary_hit_points:
            raise CharacterValidationError(
                "Current HP cannot exceed max HP plus temporary HP"
            )
        
        if character.temporary_hit_points < 0:
            raise CharacterValidationError("Temporary HP cannot be negative")

    def validate_resource_usage(self, character: Character) -> None:
        """Validate resource usage and limits.
        
        Args:
            character: Character to validate
            
        Raises:
            CharacterValidationError: If validation fails
        """
        for feature in character.features:
            if feature.uses_max is not None:
                if feature.uses_remaining is None:
                    raise CharacterValidationError(
                        f"Feature {feature.name} must track remaining uses"
                    )
                if feature.uses_remaining < 0:
                    raise CharacterValidationError(
                        f"Feature {feature.name} cannot have negative uses"
                    )
                if feature.uses_remaining > feature.uses_max:
                    raise CharacterValidationError(
                        f"Feature {feature.name} cannot exceed maximum uses"
                    )

    def validate_character_state(self, character: Character) -> None:
        """Validate overall character state.
        
        Args:
            character: Character to validate
            
        Raises:
            CharacterValidationError: If validation fails
        """
        # Basic validation
        if not character.name:
            raise CharacterValidationError("Character name is required")
        
        if character.level < self.MIN_LEVEL or character.level > self.MAX_LEVEL:
            raise CharacterValidationError(
                f"Level must be between {self.MIN_LEVEL} and {self.MAX_LEVEL}"
            )
        
        # Validate that multiclass levels sum to total level
        if character.classes:
            total_levels = sum(c["level"] for c in character.classes)
            if total_levels != character.level:
                raise CharacterValidationError(
                    f"Sum of class levels ({total_levels}) must equal character level ({character.level})"
                )
        
        # Combat stats validation
        self.validate_combat_stats(character)
        
        # Resource usage validation
        self.validate_resource_usage(character)

    def _meets_prereqs(self, ability_scores: AbilityScores, new_class: str) -> bool:
        prereqs = self.MULTICLASS_PREREQS.get(new_class, {})
        return all(ability_scores.get(ability, 0) >= min_score for ability, min_score in prereqs.items())

    async def add_class(self, character_id: UUID, new_class: str) -> Character:
        """Add a new class at level 1 to the character (multiclass).
        
        Args:
            character_id: Character ID
            new_class: New class to add
        
        Returns:
            Updated character
        
        Raises:
            CharacterValidationError: If validation fails
        """
        character = await self.repository.get(character_id)
        if not character:
            raise CharacterValidationError("Character not found")
        
        # Already has this class?
        if any(c["class"] == new_class for c in (character.classes or [])):
            raise CharacterValidationError("Character already has this class")
        
        # Validate class and prerequisites
        self._validate_class(new_class)
        scores: AbilityScores = {
            "strength": character.strength,
            "dexterity": character.dexterity,
            "constitution": character.constitution,
            "intelligence": character.intelligence,
            "wisdom": character.wisdom,
            "charisma": character.charisma,
        }
        if not self._meets_prereqs(scores, new_class):
            raise CharacterValidationError("Ability scores do not meet multiclass prerequisites")
        
        # Add class entry
        character.classes = (character.classes or []) + [{"class": new_class, "level": 1}]
        
        # Add level 1 features for the new class
        new_features = self._get_class_features(new_class, 1)
        for f in new_features:
            f.character_id = character.id
            character.features.append(f)
        
        return await self.repository.update(character)

    def _get_class_features(self, char_class: str, level: int) -> List[Feature]:
        """Get class features for a given level.
        
        Args:
            char_class: Character's class
            level: Level to get features for
            
        Returns:
            List of features for that level
        """
        features = []
        if level in self.CLASS_FEATURES.get(char_class, {}):
            for name, desc, resource_type in self.CLASS_FEATURES[char_class][level]:
                feature = Feature(
                    name=name,
                    description=desc,
                    feature_type=FeatureType.CLASS.name,
                    level_gained=level,
                    source=char_class,
                    resource_type=resource_type.name if resource_type else None
                )
                if resource_type and resource_type != ResourceType.PERMANENT:
                    feature.uses_max = 1  # Default to 1 use
                    feature.uses_remaining = 1
                features.append(feature)
        return features

    async def add_class_features(self, character_id: UUID, level: int) -> List[Feature]:
        """Add class features for a specific level.
        
        Args:
            character_id: Character ID
            level: Level to add features for
            
        Returns:
            List of added features
            
        Raises:
            CharacterValidationError: If character not found
        """
        character = await self.repository.get(character_id)
        if not character:
            raise CharacterValidationError("Character not found")

        # Get features for this level
        features = self._get_class_features(character.character_class, level)
        
        # Add features to character
        for feature in features:
            feature.character_id = character.id
            character.features.append(feature)
        
        await self.repository.update(character)
        return features

    async def reset_features(self, character_id: UUID, rest_type: ResourceType) -> List[Feature]:
        """Reset features based on rest type.
        
        Args:
            character_id: Character ID
            rest_type: Type of rest (short or long)
            
        Returns:
            List of reset features
            
        Raises:
            CharacterValidationError: If character not found
        """
        character = await self.repository.get(character_id)
        if not character:
            raise CharacterValidationError("Character not found")

        reset_features = []
        for feature in character.features:
            if feature.resource_type == rest_type.name:
                feature.uses_remaining = feature.uses_max
                reset_features.append(feature)
            elif rest_type == ResourceType.LONG_REST and feature.resource_type == ResourceType.SHORT_REST.name:
                # Long rest also resets short rest resources
                feature.uses_remaining = feature.uses_max
                reset_features.append(feature)
        
        await self.repository.update(character)
        return reset_features
