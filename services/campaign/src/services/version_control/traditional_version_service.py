"""Version control system for traditional, single-theme campaigns."""
from typing import Dict, List, Optional, Any
from uuid import UUID

from ...core.ai import AIClient
from ...models.version_control import (
    StoryState,
    CampaignType
)
from .base_version_service import BaseCampaignVersionService


class TraditionalVersionService(BaseCampaignVersionService):
    """Version control for traditional single-theme campaigns."""

    def __init__(
        self,
        ai_client: AIClient,
        campaign_id: UUID,
        theme: str,
        setting: Dict[str, Any]
    ):
        super().__init__(
            ai_client=ai_client,
            campaign_id=campaign_id,
            campaign_type=CampaignType.TRADITIONAL
        )
        self.theme = theme
        self.setting = setting

    async def _create_initial_state(self) -> StoryState:
        """Create initial state for traditional campaign."""
        try:
            # Generate initial campaign state
            state_data = await self.ai_client.generate_traditional_state({
                "campaign_id": str(self.campaign_id),
                "theme": self.theme,
                "setting": self.setting
            })

            return StoryState(
                campaign_id=self.campaign_id,
                campaign_type=CampaignType.TRADITIONAL,
                theme=self.theme,
                setting=self.setting,
                state_data=state_data
            )

        except Exception as e:
            logger.error("Failed to create initial traditional state", error=str(e))
            raise

    async def _calculate_new_state(
        self,
        current_state: StoryState,
        dm_notes: Dict[str, Any],
        party_actions: List[Dict]
    ) -> StoryState:
        """Calculate new state for traditional campaign."""
        try:
            # Analyze party actions and DM notes
            analysis = await self.ai_client.analyze_traditional_update({
                "current_state": current_state.dict(),
                "dm_notes": dm_notes,
                "party_actions": party_actions,
                "theme": self.theme
            })

            # Calculate state changes
            changes = await self.ai_client.calculate_traditional_changes({
                "analysis": analysis,
                "theme_constraints": {
                    "theme": self.theme,
                    "setting": self.setting
                }
            })

            # Apply changes to create new state
            new_state_data = await self.ai_client.apply_traditional_changes({
                "current_state": current_state.dict(),
                "changes": changes
            })

            return StoryState(
                campaign_id=self.campaign_id,
                campaign_type=CampaignType.TRADITIONAL,
                theme=self.theme,
                setting=self.setting,
                state_data=new_state_data
            )

        except Exception as e:
            logger.error("Failed to calculate new traditional state", error=str(e))
            raise

    async def create_decision_branch(
        self,
        decision_point: str,
        alternative_choice: Dict[str, Any],
        branch_name: Optional[str] = None
    ) -> StoryBranch:
        """Create new branch for alternative decision."""
        try:
            # Generate appropriate branch name if not provided
            if not branch_name:
                branch_name = f"decision_{decision_point}_{alternative_choice['summary']}"

            # Create alternative state
            alternative_state = await self.ai_client.calculate_alternative_outcome({
                "current_state": self._commits[self._head].state.dict(),
                "decision_point": decision_point,
                "alternative_choice": alternative_choice,
                "theme_constraints": {
                    "theme": self.theme,
                    "setting": self.setting
                }
            })

            # Create branch commit
            commit = await self.commit_update(
                dm_notes={
                    "summary": f"Alternative choice at {decision_point}",
                    "alternative_choice": alternative_choice
                },
                party_actions=[{
                    "type": "alternative_decision",
                    "decision_point": decision_point,
                    "choice": alternative_choice
                }],
                current_state=self._commits[self._head].state
            )

            # Create and switch to new branch
            branch = await self.create_branch(
                name=branch_name,
                start_point=commit.id,
                branch_notes={
                    "decision_point": decision_point,
                    "alternative_choice": alternative_choice
                }
            )

            return branch

        except Exception as e:
            logger.error("Failed to create decision branch", error=str(e))
            raise

    async def analyze_branch_divergence(
        self,
        source_branch: str,
        target_branch: str
    ) -> Dict[str, Any]:
        """Analyze how two branches have diverged."""
        try:
            source_state = self._commits[self._branches[source_branch].head].state
            target_state = self._commits[self._branches[target_branch].head].state

            # Analyze differences between states
            analysis = await self.ai_client.analyze_traditional_divergence({
                "source_state": source_state.dict(),
                "target_state": target_state.dict(),
                "theme": self.theme,
                "setting": self.setting
            })

            return {
                "divergence_point": analysis["divergence_point"],
                "key_differences": analysis["differences"],
                "major_consequences": analysis["consequences"],
                "potential_merge_issues": analysis["merge_issues"]
            }

        except Exception as e:
            logger.error("Failed to analyze branch divergence", error=str(e))
            raise

    async def get_decision_points(
        self,
        branch: Optional[str] = None,
        include_alternatives: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all major decision points in a branch."""
        try:
            branch_name = branch or self._current_branch
            history = await self.get_commit_history(branch_name)

            # Extract decision points from history
            decision_points = []
            for commit in history:
                if "alternative_choice" in (commit.dm_notes or {}):
                    continue  # Skip alternative choices

                # Analyze commit for decision points
                points = await self.ai_client.identify_decision_points({
                    "commit": commit.dict(),
                    "theme": self.theme,
                    "include_alternatives": include_alternatives
                })

                for point in points:
                    if include_alternatives:
                        # Generate potential alternative choices
                        alternatives = await self.ai_client.generate_alternative_choices({
                            "decision_point": point,
                            "state": commit.state.dict(),
                            "theme_constraints": {
                                "theme": self.theme,
                                "setting": self.setting
                            }
                        })
                        point["alternative_choices"] = alternatives

                    decision_points.append(point)

            return decision_points

        except Exception as e:
            logger.error("Failed to get decision points", error=str(e))
            raise

    async def validate_branch_consistency(
        self,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate story consistency within a branch."""
        try:
            branch_name = branch or self._current_branch
            history = await self.get_commit_history(branch_name)

            # Analyze branch for consistency
            validation = await self.ai_client.validate_traditional_consistency({
                "commits": [c.dict() for c in history],
                "theme": self.theme,
                "setting": self.setting
            })

            return {
                "is_consistent": validation["is_consistent"],
                "consistency_score": validation["score"],
                "issues": validation.get("issues", []),
                "suggestions": validation.get("suggestions", [])
            }

        except Exception as e:
            logger.error("Failed to validate branch consistency", error=str(e))
            raise
