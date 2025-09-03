"""Base version control system for all campaign types."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

from ...core.ai import AIClient
from ...core.logging import get_logger
from ...models.version_control import (
    StoryCommit,
    StoryBranch,
    StoryMerge,
    StoryState,
    CampaignType
)

logger = get_logger(__name__)


class BaseCampaignVersionService(ABC):
    """Base version control service for all campaign types."""

    def __init__(
        self,
        ai_client: AIClient,
        campaign_id: UUID,
        campaign_type: CampaignType,
    ):
        self.ai_client = ai_client
        self.campaign_id = campaign_id
        self.campaign_type = campaign_type
        self._branches: Dict[str, StoryBranch] = {}
        self._commits: Dict[str, StoryCommit] = {}
        self._head: Optional[str] = None
        self._current_branch: str = "main"

    async def initialize_campaign(self) -> StoryCommit:
        """Initialize main campaign branch."""
        try:
            # Create initial state based on campaign type
            initial_state = await self._create_initial_state()

            # Create root commit
            root_commit = StoryCommit(
                id=str(UUID.uuid4()),
                message="Initial campaign state",
                state=initial_state,
                timestamp=datetime.utcnow(),
                parent_ids=[],
                branch="main",
                campaign_type=self.campaign_type
            )

            # Initialize main branch
            main_branch = StoryBranch(
                name="main",
                head=root_commit.id,
                created_at=datetime.utcnow()
            )

            self._commits[root_commit.id] = root_commit
            self._branches["main"] = main_branch
            self._head = root_commit.id
            
            return root_commit

        except Exception as e:
            logger.error("Failed to initialize campaign", error=str(e))
            raise

    @abstractmethod
    async def _create_initial_state(self) -> StoryState:
        """Create initial campaign state based on type."""
        pass

    @abstractmethod
    async def _calculate_new_state(
        self,
        current_state: StoryState,
        dm_notes: Dict[str, Any],
        party_actions: List[Dict]
    ) -> StoryState:
        """Calculate new state based on campaign type."""
        pass

    async def create_branch(
        self,
        name: str,
        start_point: Optional[str] = None,
        branch_notes: Optional[Dict] = None
    ) -> StoryBranch:
        """Create new campaign branch."""
        try:
            if name in self._branches:
                raise ValueError(f"Branch {name} already exists")

            # Use current HEAD if no start point specified
            commit_id = start_point or self._head
            if not commit_id:
                raise ValueError("No starting point available")

            branch = StoryBranch(
                name=name,
                head=commit_id,
                created_at=datetime.utcnow(),
                notes=branch_notes
            )

            self._branches[name] = branch
            return branch

        except Exception as e:
            logger.error(f"Failed to create branch {name}", error=str(e))
            raise

    async def commit_update(
        self,
        dm_notes: Dict[str, Any],
        party_actions: List[Dict],
        current_state: StoryState
    ) -> StoryCommit:
        """Create new campaign state commit."""
        try:
            # Calculate new state based on campaign type
            new_state = await self._calculate_new_state(
                current_state,
                dm_notes,
                party_actions
            )

            # Create commit
            commit = StoryCommit(
                id=str(UUID.uuid4()),
                message=f"Update: {dm_notes.get('summary', 'No summary')}",
                state=new_state,
                timestamp=datetime.utcnow(),
                parent_ids=[self._head] if self._head else [],
                branch=self._current_branch,
                dm_notes=dm_notes,
                party_actions=party_actions,
                campaign_type=self.campaign_type
            )

            # Update branch and HEAD
            self._commits[commit.id] = commit
            self._branches[self._current_branch].head = commit.id
            self._head = commit.id

            return commit

        except Exception as e:
            logger.error("Failed to commit update", error=str(e))
            raise

    async def switch_branch(self, branch_name: str) -> None:
        """Switch to different campaign branch."""
        if branch_name not in self._branches:
            raise ValueError(f"Branch {branch_name} does not exist")

        self._current_branch = branch_name
        self._head = self._branches[branch_name].head

    async def merge_branches(
        self,
        source: str,
        target: str,
        resolution_notes: Optional[Dict] = None
    ) -> StoryMerge:
        """Merge two campaign branches."""
        try:
            if source not in self._branches or target not in self._branches:
                raise ValueError("Invalid branch names")

            source_state = self._commits[self._branches[source].head].state
            target_state = self._commits[self._branches[target].head].state

            # Generate merged campaign state
            merged_state = await self.ai_client.merge_campaign_states({
                "source_state": source_state.dict(),
                "target_state": target_state.dict(),
                "campaign_type": self.campaign_type.value,
                "resolution_notes": resolution_notes
            })

            # Create merge commit
            merge_commit = StoryCommit(
                id=str(UUID.uuid4()),
                message=f"Merge branch '{source}' into '{target}'",
                state=StoryState(**merged_state),
                timestamp=datetime.utcnow(),
                parent_ids=[
                    self._branches[source].head,
                    self._branches[target].head
                ],
                branch=target,
                merge_info={
                    "source": source,
                    "target": target,
                    "resolution_notes": resolution_notes
                },
                campaign_type=self.campaign_type
            )

            # Update branch and HEAD if on target branch
            self._commits[merge_commit.id] = merge_commit
            self._branches[target].head = merge_commit.id
            if self._current_branch == target:
                self._head = merge_commit.id

            return StoryMerge(
                commit=merge_commit,
                source_branch=self._branches[source],
                target_branch=self._branches[target]
            )

        except Exception as e:
            logger.error("Failed to merge branches", error=str(e))
            raise

    async def get_commit(self, commit_id: str) -> Optional[StoryCommit]:
        """Get specific campaign commit."""
        return self._commits.get(commit_id)

    async def list_branches(self) -> List[StoryBranch]:
        """List all campaign branches."""
        return list(self._branches.values())

    async def get_commit_history(
        self,
        branch: Optional[str] = None,
        max_entries: Optional[int] = None
    ) -> List[StoryCommit]:
        """Get commit history for branch."""
        try:
            branch_name = branch or self._current_branch
            if branch_name not in self._branches:
                raise ValueError(f"Branch {branch_name} does not exist")

            history = []
            current = self._branches[branch_name].head
            seen: Set[str] = set()

            while current and (not max_entries or len(history) < max_entries):
                commit = self._commits[current]
                if commit.id in seen:
                    break

                history.append(commit)
                seen.add(commit.id)
                current = commit.parent_ids[0] if commit.parent_ids else None

            return history

        except Exception as e:
            logger.error("Failed to get commit history", error=str(e))
            raise

    async def replay_from_commit(
        self,
        commit_id: str,
        branch_name: str,
        replay_notes: Optional[Dict] = None
    ) -> StoryBranch:
        """Create new branch from historical commit."""
        try:
            if commit_id not in self._commits:
                raise ValueError(f"Commit {commit_id} not found")

            # Create new branch
            branch = await self.create_branch(
                name=branch_name,
                start_point=commit_id,
                branch_notes={
                    "replay_from": commit_id,
                    "replay_notes": replay_notes,
                    "original_branch": self._commits[commit_id].branch
                }
            )

            # Switch to new branch
            await self.switch_branch(branch_name)

            return branch

        except Exception as e:
            logger.error("Failed to replay from commit", error=str(e))
            raise
