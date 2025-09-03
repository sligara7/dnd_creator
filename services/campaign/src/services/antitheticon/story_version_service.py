"""Version control system for Antitheticon story paths."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

from ...core.ai import AIClient
from ...core.logging import get_logger
from ...models.version_control import (
    StoryCommit,
    StoryBranch,
    StoryMerge,
    StoryState
)

logger = get_logger(__name__)


class AntithericonStoryVersionService:
    """Git-like version control for Antitheticon story paths."""

    def __init__(
        self,
        ai_client: AIClient,
        campaign_id: UUID,
    ):
        self.ai_client = ai_client
        self.campaign_id = campaign_id
        self._branches: Dict[str, StoryBranch] = {}
        self._commits: Dict[str, StoryCommit] = {}
        self._head: Optional[str] = None
        self._current_branch: str = "main"

    async def initialize_story(self) -> StoryCommit:
        """Initialize main story branch."""
        try:
            # Create initial state
            initial_state = await self._create_initial_state()

            # Create root commit
            root_commit = StoryCommit(
                id=str(UUID.uuid4()),
                message="Initial story state",
                state=initial_state,
                timestamp=datetime.utcnow(),
                parent_ids=[],
                branch="main"
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
            logger.error("Failed to initialize story", error=str(e))
            raise

    async def create_branch(
        self,
        name: str,
        start_point: Optional[str] = None
    ) -> StoryBranch:
        """Create new story branch."""
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
                created_at=datetime.utcnow()
            )

            self._branches[name] = branch
            return branch

        except Exception as e:
            logger.error(f"Failed to create branch {name}", error=str(e))
            raise

    async def commit_story_update(
        self,
        dm_notes: Dict[str, Any],
        party_actions: List[Dict],
        current_state: StoryState
    ) -> StoryCommit:
        """Create new story commit from DM notes."""
        try:
            # Generate Antitheticon's response to party actions
            antitheticon_response = await self._generate_antitheticon_response(
                dm_notes,
                party_actions,
                current_state
            )

            # Calculate new story state
            new_state = await self._calculate_story_state(
                current_state,
                party_actions,
                antitheticon_response
            )

            # Create commit
            commit = StoryCommit(
                id=str(UUID.uuid4()),
                message=f"Story update: {dm_notes.get('summary', 'No summary')}",
                state=new_state,
                timestamp=datetime.utcnow(),
                parent_ids=[self._head] if self._head else [],
                branch=self._current_branch,
                dm_notes=dm_notes,
                party_actions=party_actions,
                antitheticon_response=antitheticon_response
            )

            # Update branch and HEAD
            self._commits[commit.id] = commit
            self._branches[self._current_branch].head = commit.id
            self._head = commit.id

            return commit

        except Exception as e:
            logger.error("Failed to commit story update", error=str(e))
            raise

    async def _generate_antitheticon_response(
        self,
        dm_notes: Dict,
        party_actions: List[Dict],
        current_state: StoryState
    ) -> Dict[str, Any]:
        """Generate Antitheticon's response to party actions."""
        try:
            # Analyze party actions
            analysis = await self.ai_client.analyze_party_actions({
                "dm_notes": dm_notes,
                "party_actions": party_actions,
                "current_state": current_state.dict()
            })

            # Generate immediate response
            immediate_response = await self.ai_client.generate_immediate_response({
                "analysis": analysis,
                "current_state": current_state.dict()
            })

            # Plan long-term consequences
            long_term_plan = await self.ai_client.plan_long_term_response({
                "analysis": analysis,
                "immediate_response": immediate_response,
                "current_state": current_state.dict()
            })

            # Even if party allies with Antitheticon, plan betrayal
            betrayal_plan = await self.ai_client.generate_betrayal_plan({
                "alliance_state": analysis.get("alliance_state"),
                "party_weaknesses": analysis.get("vulnerabilities"),
                "useful_duration": analysis.get("utility_period")
            })

            return {
                "immediate_response": immediate_response,
                "long_term_plan": long_term_plan,
                "betrayal_plan": betrayal_plan
            }

        except Exception as e:
            logger.error("Failed to generate Antitheticon response", error=str(e))
            raise

    async def _calculate_story_state(
        self,
        current_state: StoryState,
        party_actions: List[Dict],
        antitheticon_response: Dict
    ) -> StoryState:
        """Calculate new story state based on actions and responses."""
        try:
            # Apply party actions
            intermediate_state = await self.ai_client.apply_party_actions({
                "current_state": current_state.dict(),
                "party_actions": party_actions
            })

            # Apply Antitheticon's response
            new_state = await self.ai_client.apply_antitheticon_response({
                "intermediate_state": intermediate_state,
                "antitheticon_response": antitheticon_response
            })

            return StoryState(**new_state)

        except Exception as e:
            logger.error("Failed to calculate story state", error=str(e))
            raise

    async def switch_branch(self, branch_name: str) -> None:
        """Switch to different story branch."""
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
        """Merge two story branches."""
        try:
            if source not in self._branches or target not in self._branches:
                raise ValueError("Invalid branch names")

            source_state = self._commits[self._branches[source].head].state
            target_state = self._commits[self._branches[target].head].state

            # Generate merged story state
            merged_state = await self.ai_client.merge_story_states({
                "source_state": source_state.dict(),
                "target_state": target_state.dict(),
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
                }
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
        """Get specific story commit."""
        return self._commits.get(commit_id)

    async def list_branches(self) -> List[StoryBranch]:
        """List all story branches."""
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
        branch_name: str
    ) -> StoryBranch:
        """Create new branch from historical commit."""
        try:
            if commit_id not in self._commits:
                raise ValueError(f"Commit {commit_id} not found")

            # Create new branch
            branch = await self.create_branch(
                name=branch_name,
                start_point=commit_id
            )

            # Switch to new branch
            await self.switch_branch(branch_name)

            return branch

        except Exception as e:
            logger.error("Failed to replay from commit", error=str(e))
            raise

    async def _create_initial_state(self) -> StoryState:
        """Create initial story state."""
        try:
            # Generate initial story state
            initial_state = await self.ai_client.generate_initial_state({
                "campaign_id": str(self.campaign_id)
            })

            return StoryState(**initial_state)

        except Exception as e:
            logger.error("Failed to create initial state", error=str(e))
            raise
