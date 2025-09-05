"""Version control service for managing character versions."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from deepdiff import DeepDiff
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.repositories.version_repository import VersionRepository
from character_service.domain.version import (
    CharacterVersion,
    CharacterChange,
    VersionMetadata,
    ChangeType,
    ChangeSource,
)


class VersionControlService:
    """Service for managing character versions."""

    def __init__(self, session: AsyncSession):
        """Initialize the service.

        Args:
            session: Database session
        """
        self.session = session
        self.repository = VersionRepository(session)

    async def create_version(
        self,
        character_id: UUID,
        current_state: Dict[str, Any],
        parent_version_id: Optional[UUID] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        source: ChangeSource = ChangeSource.SYSTEM,
        created_by: str = "system",
    ) -> CharacterVersion:
        """Create a new version of a character.

        Args:
            character_id: The character ID
            current_state: The current character state
            parent_version_id: Optional parent version ID
            label: Optional version label
            description: Optional version description
            source: Source of the changes
            created_by: Who/what created this version

        Returns:
            The created version
        """
        # Get parent version state if any
        parent_state = None
        if parent_version_id:
            parent_version = await self.repository.get_version(parent_version_id)
            if parent_version:
                parent_state = parent_version.state

        # Calculate changes from parent
        changes = self._calculate_changes(parent_state, current_state) if parent_state else []

        # Create version
        version = await self.repository.create_version(
            character_id=character_id,
            state=current_state,
            changes=changes,
            parent_version_id=parent_version_id,
            label=label,
            description=description,
            created_by=created_by,
        )

        # Record detailed changes
        if changes:
            await self.repository.record_changes(
                character_id=character_id,
                version_id=version.id,
                changes=changes,
                source=source,
                created_by=created_by,
            )

        # Update version metadata
        await self._update_version_metadata(version, current_state)

        return version

    async def get_version_history(
        self,
        character_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[CharacterVersion], int]:
        """Get version history for a character.

        Args:
            character_id: The character ID
            limit: Maximum number of versions to return
            offset: Offset for pagination

        Returns:
            Tuple of (versions, total_count)
        """
        return await self.repository.get_character_versions(
            character_id=character_id,
            limit=limit,
            offset=offset,
        )

    async def get_version_tree(
        self,
        character_id: UUID,
        root_version_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """Get the version tree for a character.

        Args:
            character_id: The character ID
            root_version_id: Optional root version ID

        Returns:
            List of version nodes with tree structure
        """
        # Get versions
        versions = await self.repository.get_version_tree(
            character_id=character_id,
            root_version_id=root_version_id,
        )

        # Build tree structure
        tree = []
        version_map = {v.id: self._version_to_dict(v) for v in versions}

        for version in versions:
            version_dict = version_map[version.id]
            if version.parent_version_id:
                parent = version_map.get(version.parent_version_id)
                if parent:
                    if "children" not in parent:
                        parent["children"] = []
                    parent["children"].append(version_dict)
            else:
                tree.append(version_dict)

        return tree

    async def compare_versions(
        self,
        version_a_id: UUID,
        version_b_id: UUID,
        character_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Compare two versions.

        Args:
            version_a_id: First version ID
            version_b_id: Second version ID
            character_id: Optional character ID for validation

        Returns:
            Dictionary containing differences
        """
        # Get versions
        version_a = await self.repository.get_version(version_a_id, character_id)
        version_b = await self.repository.get_version(version_b_id, character_id)

        if not version_a or not version_b:
            raise ValueError("One or both versions not found")

        # Calculate differences
        diff = DeepDiff(version_a.state, version_b.state)

        # Get changes between versions
        changes_a = await self.repository.get_version_changes(version_a_id, character_id)
        changes_b = await self.repository.get_version_changes(version_b_id, character_id)

        return {
            "diff": diff,
            "changes": {
                "version_a": [self._change_to_dict(c) for c in changes_a],
                "version_b": [self._change_to_dict(c) for c in changes_b],
            },
            "metadata": {
                "version_a": await self._get_metadata_dict(version_a_id, character_id),
                "version_b": await self._get_metadata_dict(version_b_id, character_id),
            },
        }

    async def mark_milestone(
        self,
        version_id: UUID,
        character_id: UUID,
        milestone_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[VersionMetadata]:
        """Mark a version as a milestone.

        Args:
            version_id: The version ID
            character_id: The character ID
            milestone_metadata: Optional milestone metadata

        Returns:
            The updated metadata entry
        """
        return await self.repository.mark_as_milestone(
            version_id=version_id,
            character_id=character_id,
            milestone_metadata=milestone_metadata,
        )

    async def get_milestones(
        self,
        character_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Get milestone versions for a character.

        Args:
            character_id: The character ID

        Returns:
            List of milestone versions with metadata
        """
        versions = await self.repository.get_milestone_versions(character_id)
        milestone_data = []

        for version in versions:
            metadata = await self.repository.get_version_metadata(version.id)
            milestone_data.append({
                "version": self._version_to_dict(version),
                "metadata": self._metadata_to_dict(metadata) if metadata else None,
            })

        return milestone_data

    def _calculate_changes(
        self,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Calculate changes between states.

        Args:
            old_state: Previous state
            new_state: Current state

        Returns:
            List of changes
        """
        diff = DeepDiff(old_state, new_state, ignore_order=True)
        changes = []

        # Handle value changes
        for path, change in diff.get("values_changed", {}).items():
            changes.append({
                "type": self._determine_change_type(path),
                "path": path,
                "old_value": change["old_value"],
                "new_value": change["new_value"],
            })

        # Handle dictionary changes
        for path, change in diff.get("dictionary_item_added", {}).items():
            changes.append({
                "type": self._determine_change_type(path),
                "path": path,
                "old_value": None,
                "new_value": change,
            })

        for path, change in diff.get("dictionary_item_removed", {}).items():
            changes.append({
                "type": self._determine_change_type(path),
                "path": path,
                "old_value": change,
                "new_value": None,
            })

        # Handle list changes
        for path, change in diff.get("iterable_item_added", {}).items():
            changes.append({
                "type": self._determine_change_type(path),
                "path": path,
                "old_value": None,
                "new_value": change,
            })

        for path, change in diff.get("iterable_item_removed", {}).items():
            changes.append({
                "type": self._determine_change_type(path),
                "path": path,
                "old_value": change,
                "new_value": None,
            })

        return changes

    def _determine_change_type(self, path: str) -> ChangeType:
        """Determine change type from path.

        Args:
            path: The change path

        Returns:
            Appropriate change type
        """
        path = path.lower()
        if "ability" in path or "score" in path:
            return ChangeType.ABILITY_SCORE
        elif "class" in path or "feature" in path:
            return ChangeType.CLASS_FEATURE
        elif "equipment" in path or "item" in path:
            return ChangeType.EQUIPMENT
        elif "level" in path:
            return ChangeType.LEVEL
        elif "proficiency" in path:
            return ChangeType.PROFICIENCY
        elif "resource" in path:
            return ChangeType.RESOURCE
        elif "spell" in path:
            return ChangeType.SPELL
        elif "theme" in path:
            return ChangeType.THEME
        else:
            return ChangeType.OTHER

    async def _update_version_metadata(
        self,
        version: CharacterVersion,
        state: Dict[str, Any],
    ) -> Optional[VersionMetadata]:
        """Update version metadata from state.

        Args:
            version: The version to update
            state: The character state

        Returns:
            The updated metadata entry
        """
        metadata = {
            "level": state.get("level", 1),
            "class_name": state.get("class_name", "Unknown"),
            "active_theme_id": state.get("active_theme_id"),
            "ability_scores": {
                "strength": state.get("strength_score", 10),
                "dexterity": state.get("dexterity_score", 10),
                "constitution": state.get("constitution_score", 10),
                "intelligence": state.get("intelligence_score", 10),
                "wisdom": state.get("wisdom_score", 10),
                "charisma": state.get("charisma_score", 10),
            },
            "campaign_id": state.get("campaign_id"),
            "updated_at": datetime.utcnow().isoformat(),
        }

        return await self.repository.update_version_metadata(
            version_id=version.id,
            character_id=version.character_id,
            metadata=metadata,
        )

    def _version_to_dict(self, version: CharacterVersion) -> Dict[str, Any]:
        """Convert version to dictionary.

        Args:
            version: The version to convert

        Returns:
            Dictionary representation
        """
        return {
            "id": str(version.id),
            "character_id": str(version.character_id),
            "parent_version_id": str(version.parent_version_id) if version.parent_version_id else None,
            "label": version.label,
            "description": version.description,
            "is_active": version.is_active,
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
        }

    def _change_to_dict(self, change: CharacterChange) -> Dict[str, Any]:
        """Convert change to dictionary.

        Args:
            change: The change to convert

        Returns:
            Dictionary representation
        """
        return {
            "id": str(change.id),
            "character_id": str(change.character_id),
            "version_id": str(change.version_id),
            "change_type": change.change_type,
            "source": change.source,
            "attribute_path": change.attribute_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "metadata": change.metadata,
            "created_at": change.created_at.isoformat(),
            "created_by": change.created_by,
        }

    def _metadata_to_dict(self, metadata: VersionMetadata) -> Dict[str, Any]:
        """Convert metadata to dictionary.

        Args:
            metadata: The metadata to convert

        Returns:
            Dictionary representation
        """
        return {
            "id": str(metadata.id),
            "version_id": str(metadata.version_id),
            "character_id": str(metadata.character_id),
            "level": metadata.level,
            "class_name": metadata.class_name,
            "active_theme_id": str(metadata.active_theme_id) if metadata.active_theme_id else None,
            "ability_scores": metadata.ability_scores,
            "campaign_id": str(metadata.campaign_id) if metadata.campaign_id else None,
            "branch_point": str(metadata.branch_point) if metadata.branch_point else None,
            "is_milestone": metadata.is_milestone,
            "metadata": metadata.metadata,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat(),
        }

    async def _get_metadata_dict(
        self,
        version_id: UUID,
        character_id: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get metadata as dictionary.

        Args:
            version_id: The version ID
            character_id: Optional character ID for validation

        Returns:
            Dictionary representation of metadata if found
        """
        metadata = await self.repository.get_version_metadata(version_id, character_id)
        return self._metadata_to_dict(metadata) if metadata else None
