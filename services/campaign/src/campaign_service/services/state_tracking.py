"""State tracking service implementation."""
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import StateError, ValidationError
from campaign_service.core.logging import get_logger
from campaign_service.models.version import StateTransition
from campaign_service.repositories.campaign import CampaignRepository
from campaign_service.repositories.version import (
    StateTransitionRepository,
    VersionRepository,
)
from campaign_service.services.version_control import VersionControlService

logger = get_logger(__name__)


class StateTrackingService:
    """Service for managing campaign state tracking."""

    def __init__(
        self,
        db: AsyncSession,
        campaign_repo: CampaignRepository,
        version_repo: VersionRepository,
        state_repo: StateTransitionRepository,
        version_control: VersionControlService,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize service.

        Args:
            db (AsyncSession): Database session
            campaign_repo (CampaignRepository): Campaign repository
            version_repo (VersionRepository): Version repository
            state_repo (StateTransitionRepository): State transition repository
            version_control (VersionControlService): Version control service
            message_hub_client (Any): Message hub client
        """
        self.db = db
        self.campaign_repo = campaign_repo
        self.version_repo = version_repo
        self.state_repo = state_repo
        self.version_control = version_control
        self.message_hub = message_hub_client

    async def validate_state_change(
        self,
        campaign_id: UUID,
        current_state: Dict,
        new_state: Dict,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Validate a proposed state change.

        Args:
            campaign_id (UUID): Campaign ID
            current_state (Dict): Current state
            new_state (Dict): Proposed new state
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If state change is invalid
        """
        try:
            # Get campaign and settings
            campaign = await self.campaign_repo.get(campaign_id)
            if not campaign:
                raise ValidationError(f"Campaign not found: {campaign_id}")

            # Basic validation
            required_keys = {"theme", "chapters", "npcs", "locations"}
            if not all(key in new_state for key in required_keys):
                raise ValidationError("New state missing required fields")

            # Theme validation
            if "theme" in current_state:
                # Theme transitions must be explicit
                if new_state["theme"] != current_state["theme"]:
                    raise ValidationError("Theme changes require explicit transition")

            # Chapter validation
            current_chapters = {c["id"] for c in current_state.get("chapters", [])}
            new_chapters = {c["id"] for c in new_state.get("chapters", [])}
            removed_chapters = current_chapters - new_chapters

            # Ensure no chapters with dependencies are removed
            for chapter_id in removed_chapters:
                if await self._has_dependent_chapters(campaign_id, chapter_id):
                    raise ValidationError(f"Chapter {chapter_id} has dependencies")

            # Resource validation
            if not await self._validate_resources(new_state):
                raise ValidationError("Invalid resource state")

            return True

        except ValidationError:
            raise
        except Exception as e:
            logger.error("State validation failed", error=str(e))
            raise ValidationError(f"Failed to validate state: {e}")

    async def _has_dependent_chapters(
        self,
        campaign_id: UUID,
        chapter_id: UUID,
    ) -> bool:
        """Check if any chapters depend on the given chapter.

        Args:
            campaign_id (UUID): Campaign ID
            chapter_id (UUID): Chapter ID

        Returns:
            bool: True if dependencies exist
        """
        # Get all chapters
        campaign = await self.campaign_repo.get_with_chapters(campaign_id)
        if not campaign:
            return False

        # Check for dependencies
        for chapter in campaign.chapters:
            if chapter.id != chapter_id and chapter_id in chapter.prerequisites:
                return True

        return False

    async def _validate_resources(self, state: Dict) -> bool:
        """Validate resource states.

        Args:
            state (Dict): State to validate

        Returns:
            bool: True if valid
        """
        try:
            # Validate NPCs
            if "npcs" in state:
                for npc in state["npcs"]:
                    if not all(key in npc for key in ["id", "name", "role"]):
                        return False

            # Validate locations
            if "locations" in state:
                for location in state["locations"]:
                    if not all(key in location for key in ["id", "name", "type"]):
                        return False

            # All validations passed
            return True

        except Exception as e:
            logger.error("Resource validation failed", error=str(e))
            return False

    async def create_state_transition(
        self,
        campaign_id: UUID,
        version_id: UUID,
        from_state: Dict,
        to_state: Dict,
        transition_type: str,
        reason: str,
        metadata: Optional[Dict] = None,
    ) -> StateTransition:
        """Create a new state transition.

        Args:
            campaign_id (UUID): Campaign ID
            version_id (UUID): Version ID
            from_state (Dict): Previous state
            to_state (Dict): New state
            transition_type (str): Type of transition
            reason (str): Reason for transition
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            StateTransition: Created transition

        Raises:
            StateError: If transition creation fails
        """
        try:
            # Validate state change
            await self.validate_state_change(campaign_id, from_state, to_state, metadata)

            # Create transition
            transition = await self.state_repo.create({
                "campaign_id": campaign_id,
                "version_id": version_id,
                "from_state": from_state,
                "to_state": to_state,
                "transition_type": transition_type,
                "reason": reason,
                "metadata": metadata or {},
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.state_transition",
                {
                    "campaign_id": str(campaign_id),
                    "version_id": str(version_id),
                    "transition_id": str(transition.id),
                    "type": transition_type,
                },
            )

            return transition

        except ValidationError as e:
            raise StateError(f"Invalid state transition: {e}")
        except Exception as e:
            logger.error("Failed to create state transition", error=str(e))
            raise StateError(f"Failed to create state transition: {e}")

    async def get_state_history(
        self,
        campaign_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StateTransition]:
        """Get state transition history.

        Args:
            campaign_id (UUID): Campaign ID
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[StateTransition]: List of transitions
        """
        try:
            transitions = await self.state_repo.get_multi(
                campaign_id=campaign_id,
                skip=skip,
                limit=limit,
            )
            return transitions

        except Exception as e:
            logger.error("Failed to get state history", error=str(e))
            raise StateError(f"Failed to get state history: {e}")

    async def get_state_at_version(
        self,
        campaign_id: UUID,
        version_id: UUID,
    ) -> Dict:
        """Get campaign state at a specific version.

        Args:
            campaign_id (UUID): Campaign ID
            version_id (UUID): Version ID

        Returns:
            Dict: Campaign state

        Raises:
            StateError: If state retrieval fails
        """
        try:
            version = await self.version_repo.get(version_id)
            if not version:
                raise StateError(f"Version not found: {version_id}")

            return version.content

        except Exception as e:
            logger.error("Failed to get state at version", error=str(e))
            raise StateError(f"Failed to get state at version: {e}")

    async def track_resource_versions(
        self,
        campaign_id: UUID,
        resource_type: str,
        resource_id: UUID,
        version_id: UUID,
    ) -> None:
        """Track resource version dependencies.

        Args:
            campaign_id (UUID): Campaign ID
            resource_type (str): Type of resource
            resource_id (UUID): Resource ID
            version_id (UUID): Version ID using the resource

        Raises:
            StateError: If tracking fails
        """
        try:
            # Track in version metadata
            version = await self.version_repo.get(version_id)
            if not version:
                raise StateError(f"Version not found: {version_id}")

            # Update version metadata with resource tracking
            metadata = version.metadata or {}
            resource_versions = metadata.get("resource_versions", {})
            resource_versions.setdefault(resource_type, {})[str(resource_id)] = {
                "tracked_at": datetime.utcnow().isoformat(),
            }
            metadata["resource_versions"] = resource_versions

            await self.version_repo.update(
                version_id,
                {"metadata": metadata},
            )

        except Exception as e:
            logger.error("Failed to track resource version", error=str(e))
            raise StateError(f"Failed to track resource version: {e}")

    async def validate_dependencies(
        self,
        campaign_id: UUID,
        state: Dict,
    ) -> bool:
        """Validate state dependencies.

        Args:
            campaign_id (UUID): Campaign ID
            state (Dict): State to validate

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If dependencies are invalid
        """
        try:
            # Track seen IDs to detect duplicates
            seen_ids: Set[str] = set()

            # Validate chapters
            if "chapters" in state:
                for chapter in state["chapters"]:
                    # Check for duplicate IDs
                    if chapter["id"] in seen_ids:
                        raise ValidationError(f"Duplicate chapter ID: {chapter['id']}")
                    seen_ids.add(chapter["id"])

                    # Validate prerequisites
                    for prereq_id in chapter.get("prerequisites", []):
                        if prereq_id not in seen_ids:
                            raise ValidationError(
                                f"Prerequisite chapter {prereq_id} not found"
                            )

            # Validate NPCs
            if "npcs" in state:
                for npc in state["npcs"]:
                    if npc["id"] in seen_ids:
                        raise ValidationError(f"Duplicate NPC ID: {npc['id']}")
                    seen_ids.add(npc["id"])

            # Validate locations
            if "locations" in state:
                for location in state["locations"]:
                    if location["id"] in seen_ids:
                        raise ValidationError(f"Duplicate location ID: {location['id']}")
                    seen_ids.add(location["id"])

            return True

        except Exception as e:
            logger.error("Dependency validation failed", error=str(e))
            raise ValidationError(f"Failed to validate dependencies: {e}")

    async def track_state_changes(
        self,
        campaign_id: UUID,
        old_state: Dict,
        new_state: Dict,
    ) -> Dict:
        """Track changes between states.

        Args:
            campaign_id (UUID): Campaign ID
            old_state (Dict): Previous state
            new_state (Dict): New state

        Returns:
            Dict: Change summary
        """
        try:
            changes = {
                "added": [],
                "modified": [],
                "removed": [],
            }

            # Helper function to detect changes
            def compare_states(
                old_items: List[Dict],
                new_items: List[Dict],
                item_type: str,
            ) -> None:
                old_ids = {item["id"] for item in old_items}
                new_ids = {item["id"] for item in new_items}

                # Track additions
                for item in new_items:
                    if item["id"] not in old_ids:
                        changes["added"].append({
                            "type": item_type,
                            "id": item["id"],
                            "name": item.get("name", "Unknown"),
                        })

                # Track removals
                for item in old_items:
                    if item["id"] not in new_ids:
                        changes["removed"].append({
                            "type": item_type,
                            "id": item["id"],
                            "name": item.get("name", "Unknown"),
                        })

                # Track modifications
                for old_item in old_items:
                    for new_item in new_items:
                        if old_item["id"] == new_item["id"]:
                            if old_item != new_item:
                                changes["modified"].append({
                                    "type": item_type,
                                    "id": old_item["id"],
                                    "name": old_item.get("name", "Unknown"),
                                    "fields": [
                                        k for k in new_item
                                        if k in old_item and new_item[k] != old_item[k]
                                    ],
                                })

            # Compare different content types
            compare_states(
                old_state.get("chapters", []),
                new_state.get("chapters", []),
                "chapter",
            )
            compare_states(
                old_state.get("npcs", []),
                new_state.get("npcs", []),
                "npc",
            )
            compare_states(
                old_state.get("locations", []),
                new_state.get("locations", []),
                "location",
            )

            return changes

        except Exception as e:
            logger.error("Failed to track state changes", error=str(e))
            raise StateError(f"Failed to track state changes: {e}")
