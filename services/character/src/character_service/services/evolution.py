"""Evolution service for character progression."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID
import json

from sqlalchemy import select, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from character_service.core.exceptions import (
    ValidationError,
    EvolutionError,
    StateError,
)
from character_service.domain.character import Character
from character_service.domain.evolution import (
    CharacterEvent,
    CharacterMilestone,
    CharacterProgress,
    ProgressSnapshot,
    CharacterAchievement,
    EventType,
    MilestoneType,
    ProgressType,
    AchievementCategory,
    Difficulty,
)


class EvolutionService:
    """Service for managing character evolution and progression."""

    def __init__(self, session: AsyncSession):
        """Initialize service.

        Args:
            session: Database session
        """
        self.session = session
        self._level_thresholds = {
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

    async def get_character_events(
        self,
        character_id: UUID,
        event_type: Optional[EventType] = None,
        processed: Optional[bool] = None,
    ) -> List[CharacterEvent]:
        """Get character events.

        Args:
            character_id: Character ID
            event_type: Optional event type filter
            processed: Optional processed state filter

        Returns:
            List of character events

        Raises:
            EvolutionError: If operation fails
        """
        try:
            query = select(CharacterEvent).where(
                CharacterEvent.character_id == character_id
            )

            if event_type:
                query = query.where(CharacterEvent.event_type == event_type)
            if processed is not None:
                query = query.where(CharacterEvent.is_processed == processed)

            query = query.order_by(CharacterEvent.created_at.desc())
            result = await self.session.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise EvolutionError(f"Failed to get character events: {str(e)}") from e

    async def create_event(
        self,
        character_id: UUID,
        event_type: EventType,
        title: str,
        description: Optional[str] = None,
        impact: Optional[Dict] = None,
        campaign_event_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> CharacterEvent:
        """Create a character event.

        Args:
            character_id: Character ID
            event_type: Event type
            title: Event title
            description: Optional event description
            impact: Optional impact data
            campaign_event_id: Optional linked campaign event
            metadata: Optional metadata

        Returns:
            Created character event

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            event = CharacterEvent(
                character_id=character_id,
                event_type=event_type,
                title=title,
                description=description,
                impact=impact,
                campaign_event_id=campaign_event_id,
                metadata=metadata,
            )
            self.session.add(event)
            await self.session.flush()

            # Create progress snapshot
            await self._create_state_snapshot(
                character_id=character_id,
                event_id=event.id,
                snapshot_type="event",
            )

            # Process event impact
            if impact:
                await self._process_event_impact(event)

            return event

        except Exception as e:
            raise EvolutionError(f"Failed to create event: {str(e)}") from e

    async def get_character_progress(
        self,
        character_id: UUID,
        progress_type: Optional[ProgressType] = None,
    ) -> CharacterProgress:
        """Get character progress.

        Args:
            character_id: Character ID
            progress_type: Optional progress type filter

        Returns:
            Character progress

        Raises:
            EvolutionError: If operation fails
        """
        try:
            query = select(CharacterProgress).where(
                CharacterProgress.character_id == character_id
            )

            if progress_type:
                query = query.where(CharacterProgress.progress_type == progress_type)

            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            raise EvolutionError(f"Failed to get character progress: {str(e)}") from e

    async def add_xp(
        self,
        character_id: UUID,
        amount: int,
        source: str,
        metadata: Optional[Dict] = None,
    ) -> CharacterProgress:
        """Add XP to character.

        Args:
            character_id: Character ID
            amount: XP amount
            source: XP source
            metadata: Optional metadata

        Returns:
            Updated character progress

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            if amount <= 0:
                raise ValidationError("XP amount must be positive")

            # Get or create progress
            progress = await self.get_character_progress(character_id)
            if not progress:
                progress = CharacterProgress(
                    character_id=character_id,
                    progress_type=ProgressType.XP,
                    level_progression=self._level_thresholds,
                )
                self.session.add(progress)

            # Calculate new values
            current_xp = progress.current_xp + amount
            total_xp = progress.total_xp + amount
            new_level = await self._calculate_level(total_xp)

            # Update progress
            progress.current_xp = current_xp
            progress.total_xp = total_xp
            progress.current_level = new_level
            progress.updated_at = datetime.utcnow()

            # Create event
            await self.create_event(
                character_id=character_id,
                event_type=EventType.LEVEL_UP if new_level > progress.current_level else None,
                title=f"Gained {amount} XP from {source}",
                impact={
                    "xp_gained": amount,
                    "current_xp": current_xp,
                    "total_xp": total_xp,
                    "level_before": progress.current_level,
                    "level_after": new_level,
                },
                metadata=metadata,
            )

            await self.session.flush()
            return progress

        except Exception as e:
            raise EvolutionError(f"Failed to add XP: {str(e)}") from e

    async def create_milestone(
        self,
        character_id: UUID,
        milestone_type: MilestoneType,
        title: str,
        description: Optional[str] = None,
        requirements: Optional[Dict] = None,
        rewards: Optional[Dict] = None,
        campaign_milestone_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> CharacterMilestone:
        """Create a character milestone.

        Args:
            character_id: Character ID
            milestone_type: Milestone type
            title: Milestone title
            description: Optional description
            requirements: Optional requirements
            rewards: Optional rewards
            campaign_milestone_id: Optional campaign milestone ID
            metadata: Optional metadata

        Returns:
            Created milestone

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            milestone = CharacterMilestone(
                character_id=character_id,
                milestone_type=milestone_type,
                title=title,
                description=description,
                requirements=requirements,
                rewards=rewards,
                campaign_milestone_id=campaign_milestone_id,
                metadata=metadata,
            )
            self.session.add(milestone)
            await self.session.flush()

            return milestone

        except Exception as e:
            raise EvolutionError(f"Failed to create milestone: {str(e)}") from e

    async def complete_milestone(
        self,
        character_id: UUID,
        milestone_id: UUID,
    ) -> CharacterMilestone:
        """Complete a character milestone.

        Args:
            character_id: Character ID
            milestone_id: Milestone ID

        Returns:
            Updated milestone

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            # Get milestone
            milestone = await self._get_milestone(milestone_id, character_id)
            if not milestone:
                raise ValidationError("Milestone not found")

            if milestone.completed:
                raise StateError("Milestone already completed")

            # Complete milestone
            milestone.completed = True
            milestone.completed_at = datetime.utcnow()

            # Create event
            await self.create_event(
                character_id=character_id,
                event_type=EventType.MILESTONE,
                title=f"Completed milestone: {milestone.title}",
                impact={
                    "milestone_id": str(milestone_id),
                    "milestone_type": milestone.milestone_type,
                    "rewards": milestone.rewards,
                },
                metadata=milestone.metadata,
            )

            # Update progress
            progress = await self.get_character_progress(character_id)
            if progress:
                progress.milestones_completed += 1

            await self.session.flush()
            return milestone

        except Exception as e:
            raise EvolutionError(f"Failed to complete milestone: {str(e)}") from e

    async def create_achievement(
        self,
        character_id: UUID,
        title: str,
        description: str,
        category: AchievementCategory,
        difficulty: Difficulty,
        requirements: Dict,
        rewards: Optional[Dict] = None,
        points: int = 0,
        campaign_achievement_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> CharacterAchievement:
        """Create a character achievement.

        Args:
            character_id: Character ID
            title: Achievement title
            description: Achievement description
            category: Achievement category
            difficulty: Achievement difficulty
            requirements: Achievement requirements
            rewards: Optional rewards
            points: Optional achievement points
            campaign_achievement_id: Optional campaign achievement ID
            metadata: Optional metadata

        Returns:
            Created achievement

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            achievement = CharacterAchievement(
                character_id=character_id,
                title=title,
                description=description,
                category=category,
                difficulty=difficulty,
                requirements=requirements,
                rewards=rewards,
                points=points,
                campaign_achievement_id=campaign_achievement_id,
                metadata=metadata,
            )
            self.session.add(achievement)
            await self.session.flush()

            return achievement

        except Exception as e:
            raise EvolutionError(f"Failed to create achievement: {str(e)}") from e

    async def complete_achievement(
        self,
        character_id: UUID,
        achievement_id: UUID,
    ) -> CharacterAchievement:
        """Complete a character achievement.

        Args:
            character_id: Character ID
            achievement_id: Achievement ID

        Returns:
            Updated achievement

        Raises:
            ValidationError: If validation fails
            EvolutionError: If operation fails
        """
        try:
            # Get achievement
            achievement = await self._get_achievement(achievement_id, character_id)
            if not achievement:
                raise ValidationError("Achievement not found")

            if achievement.completed:
                raise StateError("Achievement already completed")

            # Complete achievement
            achievement.completed = True
            achievement.completed_at = datetime.utcnow()

            # Create event
            await self.create_event(
                character_id=character_id,
                event_type=EventType.ACHIEVEMENT,
                title=f"Completed achievement: {achievement.title}",
                impact={
                    "achievement_id": str(achievement_id),
                    "category": achievement.category,
                    "difficulty": achievement.difficulty,
                    "points": achievement.points,
                    "rewards": achievement.rewards,
                },
                metadata=achievement.metadata,
            )

            await self.session.flush()
            return achievement

        except Exception as e:
            raise EvolutionError(f"Failed to complete achievement: {str(e)}") from e

    async def _create_state_snapshot(
        self,
        character_id: UUID,
        event_id: UUID,
        snapshot_type: str,
    ) -> ProgressSnapshot:
        """Create a state snapshot.

        Args:
            character_id: Character ID
            event_id: Event ID
            snapshot_type: Snapshot type

        Returns:
            Created snapshot

        Raises:
            EvolutionError: If operation fails
        """
        try:
            # Get current state
            state = await self._get_character_state(character_id)

            # Create snapshot
            snapshot = ProgressSnapshot(
                character_id=character_id,
                event_id=event_id,
                snapshot_type=snapshot_type,
                state_before=state,
            )
            self.session.add(snapshot)
            await self.session.flush()

            return snapshot

        except Exception as e:
            raise EvolutionError(f"Failed to create state snapshot: {str(e)}") from e

    async def _process_event_impact(
        self,
        event: CharacterEvent,
    ) -> None:
        """Process event impact.

        Args:
            event: Character event to process

        Raises:
            EvolutionError: If operation fails
        """
        try:
            if not event.impact:
                return

            # Get latest state snapshot
            snapshot = await self._get_latest_snapshot(event.character_id)
            if not snapshot:
                return

            # Process impact based on event type
            if event.event_type == EventType.LEVEL_UP:
                # Handle level up
                pass
            elif event.event_type == EventType.MILESTONE:
                # Handle milestone
                if rewards := event.impact.get("rewards"):
                    await self._apply_rewards(event.character_id, rewards)
            elif event.event_type == EventType.ACHIEVEMENT:
                # Handle achievement
                if rewards := event.impact.get("rewards"):
                    await self._apply_rewards(event.character_id, rewards)

            # Mark event as processed
            event.is_processed = True
            event.processed_at = datetime.utcnow()

            # Update snapshot
            snapshot.state_after = await self._get_character_state(event.character_id)
            snapshot.diff = await self._calculate_state_diff(
                snapshot.state_before,
                snapshot.state_after,
            )

            await self.session.flush()

        except Exception as e:
            raise EvolutionError(f"Failed to process event impact: {str(e)}") from e

    async def _calculate_level(self, total_xp: int) -> int:
        """Calculate level from total XP.

        Args:
            total_xp: Total XP

        Returns:
            Character level
        """
        level = 1
        for next_level, threshold in self._level_thresholds.items():
            if total_xp >= threshold:
                level = next_level
            else:
                break
        return level

    async def _get_milestone(
        self,
        milestone_id: UUID,
        character_id: UUID,
    ) -> Optional[CharacterMilestone]:
        """Get a character milestone.

        Args:
            milestone_id: Milestone ID
            character_id: Character ID for validation

        Returns:
            Character milestone if found
        """
        query = select(CharacterMilestone).where(
            and_(
                CharacterMilestone.id == milestone_id,
                CharacterMilestone.character_id == character_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_achievement(
        self,
        achievement_id: UUID,
        character_id: UUID,
    ) -> Optional[CharacterAchievement]:
        """Get a character achievement.

        Args:
            achievement_id: Achievement ID
            character_id: Character ID for validation

        Returns:
            Character achievement if found
        """
        query = select(CharacterAchievement).where(
            and_(
                CharacterAchievement.id == achievement_id,
                CharacterAchievement.character_id == character_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_latest_snapshot(
        self,
        character_id: UUID,
    ) -> Optional[ProgressSnapshot]:
        """Get latest state snapshot.

        Args:
            character_id: Character ID

        Returns:
            Latest snapshot if found
        """
        query = (
            select(ProgressSnapshot)
            .where(ProgressSnapshot.character_id == character_id)
            .order_by(ProgressSnapshot.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_character_state(self, character_id: UUID) -> Dict:
        """Get current character state.

        Args:
            character_id: Character ID

        Returns:
            Character state dictionary
        """
        # Get character progress
        progress = await self.get_character_progress(character_id)

        # Build state dictionary
        state = {
            "character_id": str(character_id),
            "timestamp": datetime.utcnow().isoformat(),
            "progress": {
                "xp": progress.current_xp if progress else 0,
                "total_xp": progress.total_xp if progress else 0,
                "level": progress.current_level if progress else 1,
                "milestones_completed": progress.milestones_completed if progress else 0,
            },
        }

        return state

    async def _calculate_state_diff(
        self,
        state_before: Dict,
        state_after: Dict,
    ) -> Dict:
        """Calculate state difference.

        Args:
            state_before: State before event
            state_after: State after event

        Returns:
            State difference dictionary
        """
        diff = {}

        # Compare progress
        if "progress" in state_before and "progress" in state_after:
            progress_diff = {}
            for key in state_before["progress"]:
                before = state_before["progress"][key]
                after = state_after["progress"][key]
                if before != after:
                    progress_diff[key] = {
                        "before": before,
                        "after": after,
                        "delta": after - before if isinstance(before, (int, float)) else None,
                    }
            if progress_diff:
                diff["progress"] = progress_diff

        return diff

    async def _apply_rewards(
        self,
        character_id: UUID,
        rewards: Dict,
    ) -> None:
        """Apply rewards to character.

        Args:
            character_id: Character ID
            rewards: Reward data

        Raises:
            EvolutionError: If operation fails
        """
        try:
            # Handle XP rewards
            if xp := rewards.get("xp"):
                await self.add_xp(
                    character_id=character_id,
                    amount=xp,
                    source="reward",
                    metadata={"reward_data": rewards},
                )

            # Handle other rewards
            # TODO: Implement other reward types
            pass

        except Exception as e:
            raise EvolutionError(f"Failed to apply rewards: {str(e)}") from e
