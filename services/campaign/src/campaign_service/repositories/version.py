"""Version control repositories."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from campaign_service.models.version import Branch, BranchType, StateTransition, Version
from campaign_service.repositories.base import BaseRepository


class VersionRepository(BaseRepository[Version]):
    """Repository for version management."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Version)

    async def get_by_hash(self, version_hash: str) -> Optional[Version]:
        """Get version by its hash.

        Args:
            version_hash (str): Version hash

        Returns:
            Optional[Version]: Version if found
        """
        query = select(Version).where(
            Version.version_hash == version_hash,
            Version.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_campaign_versions(
        self,
        campaign_id: UUID,
        branch_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Version]:
        """Get versions for a campaign.

        Args:
            campaign_id (UUID): Campaign ID
            branch_id (Optional[UUID], optional): Branch ID. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[Version]: List of versions
        """
        query = select(Version).where(
            Version.campaign_id == campaign_id,
            Version.is_deleted == False,  # noqa: E712
        )

        if branch_id:
            query = query.where(Version.branch_id == branch_id)

        query = (
            query.order_by(Version.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())


class BranchRepository(BaseRepository[Branch]):
    """Repository for branch management."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Branch)

    async def get_campaign_branches(
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
        query = select(Branch).where(
            Branch.campaign_id == campaign_id,
            Branch.is_deleted == False,  # noqa: E712
        )

        if branch_type:
            query = query.where(Branch.branch_type == branch_type)

        query = (
            query.order_by(Branch.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_parent(self, branch_id: UUID) -> Optional[Branch]:
        """Get branch with parent branch.

        Args:
            branch_id (UUID): Branch ID

        Returns:
            Optional[Branch]: Branch with parent
        """
        query = (
            select(Branch)
            .options(joinedload(Branch.parent_branch))
            .where(
                Branch.id == branch_id,
                Branch.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_main_branch(self, campaign_id: UUID) -> Optional[Branch]:
        """Get main branch for a campaign.

        Args:
            campaign_id (UUID): Campaign ID

        Returns:
            Optional[Branch]: Main branch if found
        """
        query = select(Branch).where(
            Branch.campaign_id == campaign_id,
            Branch.branch_type == BranchType.MAIN,
            Branch.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class StateTransitionRepository(BaseRepository[StateTransition]):
    """Repository for state transition management."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, StateTransition)

    async def get_version_transitions(
        self,
        version_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StateTransition]:
        """Get state transitions for a version.

        Args:
            version_id (UUID): Version ID
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[StateTransition]: List of state transitions
        """
        query = (
            select(StateTransition)
            .where(StateTransition.version_id == version_id)
            .order_by(StateTransition.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
