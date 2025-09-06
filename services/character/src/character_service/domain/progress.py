"""Progress tracking service module."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from character_service.core.exceptions import (CharacterNotFoundError,
                                          StateError,
                                          ValidationError)
from character_service.domain.models import Character, CharacterProgress
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.event import (
    CampaignEventRepository, EventImpactRepository)
from character_service.domain.state_version import VersionManager


class XP_LEVELS:
    """Experience points required for each level."""

    THRESHOLDS = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000,
        11: 85000,
        12: 100000,
        13: 120000,
        14: 140000,
        15: 165000,
        16: 195000,
        17: 225000,
        18: 265000,
        19: 305000,
        20: 355000,
    }

    @classmethod
    def get_level(cls, xp: int) -> int:
        """Get the level for a given amount of XP."""
        for level in range(20, 0, -1):
            if xp >= cls.THRESHOLDS[level]:
                return level
        return 1


class ProgressTrackingService:
    """Service for tracking character progression and milestones."""

    def __init__(
        self,
        char_repository: CharacterRepository,
        event_repository: CampaignEventRepository,
        impact_repository: EventImpactRepository,
        version_manager: VersionManager,
    ) -> None:
        """Initialize service."""
        self._char_repo = char_repository
        self._event_repo = event_repository
        self._impact_repo = impact_repository
        self._version_manager = version_manager

    async def get_character_progress(self, character_id: UUID) -> CharacterProgress:
        """Get progress for a character."""
        # Get character first to validate existence
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Create default progress if not exists
        progress = await self._get_or_create_progress(character)
        return progress

    async def add_experience(
        self,
        character_id: UUID,
        amount: int,
        source: str,
        reason: str,
    ) -> Tuple[int, bool, Optional[Dict]]:
        """Add experience points to a character.

        Returns:
            Tuple containing:
            - New total XP
            - Whether level changed
            - Level up data if level changed
        """
        if amount <= 0:
            raise ValidationError("Experience amount must be positive")

        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        progress = await self._get_or_create_progress(character)
        
        # Update XP
        old_level = progress.current_level
        progress.experience_points += amount
        new_level = XP_LEVELS.get_level(progress.experience_points)

        level_up_data = None
        if new_level > old_level:
            progress.previous_level = old_level
            progress.current_level = new_level
            progress.level_updated_at = datetime.utcnow()
            level_up_data = await self._handle_level_up(character, old_level, new_level)

        # Update progress
        await self._char_repo.update(character.id, character)
        # Create version after progress change
        await self._version_manager.create_version(character, parent_version=None)
        return progress.experience_points, new_level > old_level, level_up_data

    async def add_milestone(
        self,
        character_id: UUID,
        title: str,
        description: str,
        milestone_type: str,
        data: Optional[Dict] = None,
    ) -> CharacterProgress:
        """Add a milestone to a character's progress."""
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        progress = await self._get_or_create_progress(character)

        # Add milestone
        milestone = {
            "id": str(uuid4()),
            "title": title,
            "description": description,
            "type": milestone_type,
            "achieved_at": datetime.utcnow().isoformat(),
            "data": data or {},
        }
        progress.milestones.append(milestone)

        # Handle milestone-specific effects
        if milestone_type == "level":
            await self._handle_level_milestone(character, milestone)
        elif milestone_type == "story":
            await self._handle_story_milestone(character, milestone)
        elif milestone_type == "achievement":
            await self._handle_achievement_milestone(character, milestone)

        # Update progress
        await self._char_repo.update(character.id, character)
        await self._version_manager.create_version(character, parent_version=None)
        return progress

    async def add_achievement(
        self,
        character_id: UUID,
        title: str,
        description: str,
        achievement_type: str,
        data: Optional[Dict] = None,
    ) -> CharacterProgress:
        """Add an achievement to a character's progress."""
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        progress = await self._get_or_create_progress(character)

        # Check if achievement already exists
        existing = next(
            (a for a in progress.achievements if a["title"] == title),
            None
        )
        if existing:
            raise ValidationError(f"Achievement '{title}' already exists")

        # Add achievement
        achievement = {
            "id": str(uuid4()),
            "title": title,
            "description": description,
            "type": achievement_type,
            "achieved_at": datetime.utcnow().isoformat(),
            "data": data or {},
        }
        progress.achievements.append(achievement)

        # Update progress
        await self._char_repo.update(character.id, character)
        await self._version_manager.create_version(character, parent_version=None)
        return progress

    async def _get_or_create_progress(self, character: Character) -> CharacterProgress:
        """Get or create progress tracking for a character."""
        # Initialize with defaults based on character data
        current_xp = character.character_data.get("experience_points", 0)
        current_level = character.character_data.get("level", 1)

        progress = CharacterProgress(
            id=uuid4(),
            character_id=character.id,
            experience_points=current_xp,
            current_level=current_level,
            previous_level=current_level,
            milestones=[],
            achievements=[],
        )

        return progress

    async def _handle_level_up(
        self,
        character: Character,
        old_level: int,
        new_level: int,
    ) -> Dict:
        """Handle level up effects and return level up data."""
        level_data = {
            "previous_level": old_level,
            "new_level": new_level,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Update character level
        character.character_data["level"] = new_level
        
        # Add level-specific updates (class features, etc)
        level_data.update(self._calculate_level_benefits(character, new_level))

        return level_data

    def _calculate_level_benefits(self, character: Character, level: int) -> Dict:
        """Calculate benefits gained at a specific level."""
        benefits = {
            "class_features": [],
            "proficiency_bonus": 2 + ((level - 1) // 4),
            "ability_score_improvement": level in [4, 8, 12, 16, 19],
        }

        # Add class-specific features
        char_class = character.character_data.get("character_class", "")
        if char_class == "fighter":
            if level >= 5:
                benefits["class_features"].append("Extra Attack")
            if level >= 9:
                benefits["class_features"].append("Indomitable")
        # Add more class features as needed

        return benefits

    async def _handle_level_milestone(
        self,
        character: Character,
        milestone: Dict,
    ) -> None:
        """Handle effects of a level-based milestone."""
        # Example: Award bonus XP, items, or other rewards
        pass

    async def _handle_story_milestone(
        self,
        character: Character,
        milestone: Dict,
    ) -> None:
        """Handle effects of a story-based milestone."""
        # Example: Update reputation, relationships, or story state
        pass

    async def _handle_achievement_milestone(
        self,
        character: Character,
        milestone: Dict,
    ) -> None:
        """Handle effects of an achievement-based milestone."""
        # Example: Award titles, special abilities, or cosmetic rewards
        pass
