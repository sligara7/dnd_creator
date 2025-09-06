"""Version control service implementation."""
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import VersionControlError
from campaign_service.core.logging import get_logger
from campaign_service.models.version import Branch, BranchType, Version, VersionType
from campaign_service.repositories.campaign import CampaignRepository
from campaign_service.repositories.version import (
    BranchRepository,
    StateTransitionRepository,
    VersionRepository,
)

logger = get_logger(__name__)


class VersionControlService:
    """Service for managing campaign versioning."""

    def __init__(
        self,
        db: AsyncSession,
        campaign_repo: CampaignRepository,
        version_repo: VersionRepository,
        branch_repo: BranchRepository,
        state_repo: StateTransitionRepository,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize service.

        Args:
            db (AsyncSession): Database session
            campaign_repo (CampaignRepository): Campaign repository
            version_repo (VersionRepository): Version repository
            branch_repo (BranchRepository): Branch repository
            state_repo (StateTransitionRepository): State transition repository
            message_hub_client (Any): Message hub client
        """
        self.db = db
        self.campaign_repo = campaign_repo
        self.version_repo = version_repo
        self.branch_repo = branch_repo
        self.state_repo = state_repo
        self.message_hub = message_hub_client

    def _calculate_hash(self, content: Dict) -> str:
        """Calculate version hash from content.

        Args:
            content (Dict): Version content

        Returns:
            str: Version hash
        """
        # Sort keys for consistent hashing
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def initialize_campaign_versioning(
        self,
        campaign_id: UUID,
        initial_content: Dict,
        author: str,
    ) -> Tuple[Branch, Version]:
        """Initialize version control for a campaign.

        Args:
            campaign_id (UUID): Campaign ID
            initial_content (Dict): Initial campaign content
            author (str): Author of initial version

        Returns:
            Tuple[Branch, Version]: Created main branch and initial version

        Raises:
            VersionControlError: If initialization fails
        """
        try:
            # Create main branch
            main_branch = await self.branch_repo.create({
                "campaign_id": campaign_id,
                "name": "main",
                "branch_type": BranchType.MAIN,
                "description": "Main campaign timeline",
                "parent_branch_id": None,
                "base_version_hash": self._calculate_hash(initial_content),
                "metadata": {
                    "initialized_at": datetime.utcnow().isoformat(),
                    "initialized_by": author,
                },
            })

            # Create initial version
            initial_version = await self.version_repo.create({
                "campaign_id": campaign_id,
                "branch_id": main_branch.id,
                "version_hash": self._calculate_hash(initial_content),
                "parent_hashes": [],  # Initial version has no parents
                "version_type": VersionType.SKELETON,
                "title": "Initial campaign structure",
                "message": "Campaign initialization",
                "author": author,
                "content": initial_content,
                "metadata": {
                    "initialized_at": datetime.utcnow().isoformat(),
                },
            })

            # Record initial state
            await self.state_repo.create({
                "campaign_id": campaign_id,
                "version_id": initial_version.id,
                "from_state": None,  # Initial state
                "to_state": initial_content,
                "transition_type": "initialization",
                "reason": "Campaign initialization",
                "metadata": {
                    "initialized_at": datetime.utcnow().isoformat(),
                    "initialized_by": author,
                },
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.version_control_initialized",
                {
                    "campaign_id": str(campaign_id),
                    "branch_id": str(main_branch.id),
                    "version_id": str(initial_version.id),
                    "author": author,
                },
            )

            return main_branch, initial_version

        except Exception as e:
            logger.error("Failed to initialize version control", error=str(e))
            raise VersionControlError(f"Failed to initialize version control: {e}")

    async def create_version(
        self,
        campaign_id: UUID,
        branch_id: UUID,
        content: Dict,
        title: str,
        message: str,
        author: str,
        version_type: Optional[VersionType] = None,
        metadata: Optional[Dict] = None,
    ) -> Version:
        """Create a new version.

        Args:
            campaign_id (UUID): Campaign ID
            branch_id (UUID): Branch ID
            content (Dict): Version content
            title (str): Version title
            message (str): Commit message
            author (str): Version author
            version_type (Optional[VersionType], optional): Version type. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Version: Created version

        Raises:
            VersionControlError: If version creation fails
        """
        try:
            # Get parent version(s)
            parent_versions = await self.version_repo.get_campaign_versions(
                campaign_id=campaign_id,
                branch_id=branch_id,
                limit=1,
            )
            parent_hashes = [v.version_hash for v in parent_versions]

            # Create new version
            version = await self.version_repo.create({
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "version_hash": self._calculate_hash(content),
                "parent_hashes": parent_hashes,
                "version_type": version_type or VersionType.DRAFT,
                "title": title,
                "message": message,
                "author": author,
                "content": content,
                "metadata": metadata or {},
            })

            # Record state transition
            if parent_versions:
                await self.state_repo.create({
                    "campaign_id": campaign_id,
                    "version_id": version.id,
                    "from_state": parent_versions[0].content,
                    "to_state": content,
                    "transition_type": "update",
                    "reason": message,
                    "metadata": metadata or {},
                })

            # Publish event
            await self.message_hub.publish(
                "campaign.version_created",
                {
                    "campaign_id": str(campaign_id),
                    "version_id": str(version.id),
                    "branch_id": str(branch_id),
                    "type": version_type.value if version_type else VersionType.DRAFT.value,
                    "author": author,
                },
            )

            return version

        except Exception as e:
            logger.error("Failed to create version", error=str(e))
            raise VersionControlError(f"Failed to create version: {e}")

    async def create_branch(
        self,
        campaign_id: UUID,
        name: str,
        branch_type: BranchType,
        description: str,
        base_version_hash: str,
        parent_branch_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> Branch:
        """Create a new branch.

        Args:
            campaign_id (UUID): Campaign ID
            name (str): Branch name
            branch_type (BranchType): Branch type
            description (str): Branch description
            base_version_hash (str): Base version hash
            parent_branch_id (Optional[UUID], optional): Parent branch ID. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Branch: Created branch

        Raises:
            VersionControlError: If branch creation fails
        """
        try:
            # Verify base version exists
            base_version = await self.version_repo.get_by_hash(base_version_hash)
            if not base_version:
                raise VersionControlError(f"Base version not found: {base_version_hash}")

            # Create branch
            branch = await self.branch_repo.create({
                "campaign_id": campaign_id,
                "name": name,
                "branch_type": branch_type,
                "description": description,
                "parent_branch_id": parent_branch_id,
                "base_version_hash": base_version_hash,
                "metadata": metadata or {},
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.branch_created",
                {
                    "campaign_id": str(campaign_id),
                    "branch_id": str(branch.id),
                    "type": branch_type.value,
                    "parent_branch_id": str(parent_branch_id) if parent_branch_id else None,
                },
            )

            return branch

        except Exception as e:
            logger.error("Failed to create branch", error=str(e))
            raise VersionControlError(f"Failed to create branch: {e}")

    async def merge_branches(
        self,
        campaign_id: UUID,
        source_branch_id: UUID,
        target_branch_id: UUID,
        author: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> Version:
        """Merge two branches.

        Args:
            campaign_id (UUID): Campaign ID
            source_branch_id (UUID): Source branch ID
            target_branch_id (UUID): Target branch ID
            author (str): Merge author
            message (str): Merge message
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Version: Merge version

        Raises:
            VersionControlError: If merge fails
        """
        try:
            # Get latest versions from both branches
            source_versions = await self.version_repo.get_campaign_versions(
                campaign_id=campaign_id,
                branch_id=source_branch_id,
                limit=1,
            )
            target_versions = await self.version_repo.get_campaign_versions(
                campaign_id=campaign_id,
                branch_id=target_branch_id,
                limit=1,
            )

            if not source_versions or not target_versions:
                raise VersionControlError("Source or target branch has no versions")

            source_version = source_versions[0]
            target_version = target_versions[0]

            # Merge content (for now, just take source content)
            # TODO: Implement proper content merging strategy
            merged_content = source_version.content

            # Create merge version
            merge_version = await self.version_repo.create({
                "campaign_id": campaign_id,
                "branch_id": target_branch_id,
                "version_hash": self._calculate_hash(merged_content),
                "parent_hashes": [
                    target_version.version_hash,
                    source_version.version_hash,
                ],
                "version_type": VersionType.MERGE,
                "title": f"Merge branch '{source_version.branch.name}' into '{target_version.branch.name}'",
                "message": message,
                "author": author,
                "content": merged_content,
                "metadata": metadata or {},
            })

            # Record state transition
            await self.state_repo.create({
                "campaign_id": campaign_id,
                "version_id": merge_version.id,
                "from_state": target_version.content,
                "to_state": merged_content,
                "transition_type": "merge",
                "reason": message,
                "metadata": {
                    "source_branch": str(source_branch_id),
                    "target_branch": str(target_branch_id),
                    **(metadata or {}),
                },
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.branches_merged",
                {
                    "campaign_id": str(campaign_id),
                    "source_branch_id": str(source_branch_id),
                    "target_branch_id": str(target_branch_id),
                    "merge_version_id": str(merge_version.id),
                    "author": author,
                },
            )

            return merge_version

        except Exception as e:
            logger.error("Failed to merge branches", error=str(e))
            raise VersionControlError(f"Failed to merge branches: {e}")

    async def get_version_history(
        self,
        campaign_id: UUID,
        branch_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Version]:
        """Get version history for a campaign or branch.

        Args:
            campaign_id (UUID): Campaign ID
            branch_id (Optional[UUID], optional): Branch ID. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[Version]: List of versions
        """
        try:
            return await self.version_repo.get_campaign_versions(
                campaign_id=campaign_id,
                branch_id=branch_id,
                skip=skip,
                limit=limit,
            )

        except Exception as e:
            logger.error("Failed to get version history", error=str(e))
            raise VersionControlError(f"Failed to get version history: {e}")

    async def get_branches(
        self,
        campaign_id: UUID,
        branch_type: Optional[BranchType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Branch]:
        """Get branches for a campaign.

        Args:
            campaign_id (UUID): Campaign ID
            branch_type (Optional[BranchType], optional): Branch type. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[Branch]: List of branches
        """
        try:
            return await self.branch_repo.get_campaign_branches(
                campaign_id=campaign_id,
                branch_type=branch_type,
                skip=skip,
                limit=limit,
            )

        except Exception as e:
            logger.error("Failed to get branches", error=str(e))
            raise VersionControlError(f"Failed to get branches: {e}")

    async def get_state_transitions(
        self,
        version_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List["StateTransition"]:
        """Get state transitions for a version.

        Args:
            version_id (UUID): Version ID
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[StateTransition]: List of state transitions
        """
        try:
            return await self.state_repo.get_version_transitions(
                version_id=version_id,
                skip=skip,
                limit=limit,
            )

        except Exception as e:
            logger.error("Failed to get state transitions", error=str(e))
            raise VersionControlError(f"Failed to get state transitions: {e}")

    async def restore_version(
        self,
        campaign_id: UUID,
        version_hash: str,
        author: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> Version:
        """Restore a previous version.

        Args:
            campaign_id (UUID): Campaign ID
            version_hash (str): Version hash to restore
            author (str): Restore author
            message (str): Restore message
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Version: Restored version

        Raises:
            VersionControlError: If restore fails
        """
        try:
            # Get version to restore
            version_to_restore = await self.version_repo.get_by_hash(version_hash)
            if not version_to_restore:
                raise VersionControlError(f"Version not found: {version_hash}")

            # Create restoration version on the same branch
            restored_version = await self.version_repo.create({
                "campaign_id": campaign_id,
                "branch_id": version_to_restore.branch_id,
                "version_hash": version_hash,  # Same hash since it's the same content
                "parent_hashes": [version_hash],
                "version_type": version_to_restore.version_type,
                "title": f"Restore version: {version_to_restore.title}",
                "message": message,
                "author": author,
                "content": version_to_restore.content,
                "metadata": {
                    "restored_from": version_hash,
                    "restored_at": datetime.utcnow().isoformat(),
                    **(metadata or {}),
                },
            })

            # Record state transition
            await self.state_repo.create({
                "campaign_id": campaign_id,
                "version_id": restored_version.id,
                "from_state": version_to_restore.content,
                "to_state": version_to_restore.content,
                "transition_type": "restore",
                "reason": message,
                "metadata": {
                    "restored_from": version_hash,
                    "restored_at": datetime.utcnow().isoformat(),
                    **(metadata or {}),
                },
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.version_restored",
                {
                    "campaign_id": str(campaign_id),
                    "restored_version_id": str(restored_version.id),
                    "source_version_hash": version_hash,
                    "author": author,
                },
            )

            return restored_version

        except Exception as e:
            logger.error("Failed to restore version", error=str(e))
            raise VersionControlError(f"Failed to restore version: {e}")
