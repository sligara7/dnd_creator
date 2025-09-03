"""Version control service for campaign content."""
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ..core.logging import get_logger
from ..models.campaign import Campaign
from ..models.chapter import Chapter
from ..models.version import (
    Version,
    Branch,
    MergeRequest,
    Conflict,
)
from ..api.schemas.version import (
    VersionType,
    BranchType,
    MergeStrategy,
    MergeConflict,
)

logger = get_logger(__name__)


class VersionControlService:
    """Service for managing content versioning."""

    def __init__(self, db: Session, message_hub_client):
        """Initialize with required dependencies."""
        self.db = db
        self.message_hub = message_hub_client

    def create_version(
        self,
        campaign_id: UUID,
        content: Dict,
        title: str,
        message: str,
        author: str,
        version_type: VersionType,
        branch_name: str = "main",
        parent_hashes: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Version:
        """Create a new version."""
        try:
            # Generate version hash
            version_hash = self._generate_hash(content)

            # Check if hash already exists
            existing = self.db.query(Version).filter_by(hash=version_hash).first()
            if existing:
                raise ValueError("Version with this content already exists")

            # Create version
            version = Version(
                campaign_id=campaign_id,
                hash=version_hash,
                title=title,
                summary=message,
                content=content,
                parent_hashes=parent_hashes or [],
                branch_name=branch_name,
                version_type=version_type,
                commit_message=message,
                author=author,
                metadata=metadata or {}
            )
            self.db.add(version)

            # Update branch head
            branch = self.db.query(Branch).filter_by(
                campaign_id=campaign_id,
                name=branch_name
            ).first()

            if branch:
                branch.head = version_hash
            else:
                # Create new branch
                branch = Branch(
                    campaign_id=campaign_id,
                    name=branch_name,
                    head=version_hash,
                    type=BranchType.MAIN if branch_name == "main" else BranchType.ALTERNATE
                )
                self.db.add(branch)

            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.version_created",
                {
                    "campaign_id": str(campaign_id),
                    "version_hash": version_hash,
                    "branch": branch_name,
                    "type": version_type
                }
            )

            return version

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create version", error=str(e))
            raise ValueError(f"Failed to create version: {e}")

    def get_version(
        self,
        version_hash: str,
        with_content: bool = True
    ) -> Version:
        """Get a specific version."""
        version = self.db.query(Version).filter_by(hash=version_hash).first()
        if not version:
            raise ValueError("Version not found")
        return version

    def get_version_history(
        self,
        campaign_id: UUID,
        branch: Optional[str] = None,
        max_count: Optional[int] = None
    ) -> List[Version]:
        """Get version history."""
        query = self.db.query(Version).filter_by(campaign_id=campaign_id)
        if branch:
            query = query.filter_by(branch_name=branch)
        query = query.order_by(Version.created_at.desc())
        if max_count:
            query = query.limit(max_count)
        return query.all()

    def create_branch(
        self,
        campaign_id: UUID,
        name: str,
        start_point: str,
        branch_type: BranchType,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Branch:
        """Create a new branch."""
        try:
            # Check if branch already exists
            existing = self.db.query(Branch).filter_by(
                campaign_id=campaign_id,
                name=name
            ).first()
            if existing:
                raise ValueError("Branch already exists")

            # Validate start point
            start_version = self.db.query(Version).filter_by(
                hash=start_point
            ).first()
            if not start_version:
                raise ValueError("Invalid start point")

            # Create branch
            branch = Branch(
                campaign_id=campaign_id,
                name=name,
                head=start_point,
                type=branch_type,
                description=description,
                metadata=metadata or {}
            )
            self.db.add(branch)
            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.branch_created",
                {
                    "campaign_id": str(campaign_id),
                    "branch": name,
                    "type": branch_type,
                    "start_point": start_point
                }
            )

            return branch

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create branch", error=str(e))
            raise ValueError(f"Failed to create branch: {e}")

    def create_merge_request(
        self,
        campaign_id: UUID,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        author: str,
        reviewers: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> MergeRequest:
        """Create a merge request."""
        try:
            # Validate branches
            source = self.db.query(Branch).filter_by(
                campaign_id=campaign_id,
                name=source_branch
            ).first()
            target = self.db.query(Branch).filter_by(
                campaign_id=campaign_id,
                name=target_branch
            ).first()
            if not source or not target:
                raise ValueError("Invalid branch names")

            # Create merge request
            mr = MergeRequest(
                campaign_id=campaign_id,
                source_branch=source_branch,
                target_branch=target_branch,
                title=title,
                description=description,
                author=author,
                reviewers=reviewers or [],
                status="open",
                metadata=metadata or {}
            )
            self.db.add(mr)
            self.db.commit()

            # Check for conflicts
            conflicts = await self._detect_conflicts(
                campaign_id,
                source.head,
                target.head
            )
            if conflicts:
                await self._create_conflicts(mr.id, conflicts)
                mr.status = "conflicts"
                self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.merge_request_created",
                {
                    "campaign_id": str(campaign_id),
                    "merge_request_id": str(mr.id),
                    "source": source_branch,
                    "target": target_branch,
                    "has_conflicts": bool(conflicts)
                }
            )

            return mr

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create merge request", error=str(e))
            raise ValueError(f"Failed to create merge request: {e}")

    async def merge_branches(
        self,
        merge_request_id: UUID,
        strategy: MergeStrategy,
        message: str,
        author: str,
        resolution_data: Optional[Dict] = None
    ) -> Version:
        """Merge branches via merge request."""
        try:
            # Get merge request
            mr = self.db.query(MergeRequest).get(merge_request_id)
            if not mr:
                raise ValueError("Merge request not found")
            if mr.status not in ["open", "conflicts"]:
                raise ValueError("Invalid merge request status")

            # Get branches
            source = self.db.query(Branch).filter_by(
                campaign_id=mr.campaign_id,
                name=mr.source_branch
            ).first()
            target = self.db.query(Branch).filter_by(
                campaign_id=mr.campaign_id,
                name=mr.target_branch
            ).first()

            # Get versions
            source_version = self.db.query(Version).filter_by(
                hash=source.head
            ).first()
            target_version = self.db.query(Version).filter_by(
                hash=target.head
            ).first()

            # Perform merge
            merged_content = await self._merge_content(
                source_version.content,
                target_version.content,
                strategy,
                resolution_data
            )

            # Create merge commit
            merge_version = self.create_version(
                campaign_id=mr.campaign_id,
                content=merged_content,
                title=f"Merge {mr.source_branch} into {mr.target_branch}",
                message=message,
                author=author,
                version_type=VersionType.MERGE,
                branch_name=mr.target_branch,
                parent_hashes=[source.head, target.head],
                metadata={
                    "merge_request_id": str(merge_request_id),
                    "strategy": strategy,
                    "resolution_data": resolution_data
                }
            )

            # Update merge request
            mr.status = "merged"
            mr.merged_by = author
            mr.merged_at = datetime.utcnow()
            mr.merge_commit_hash = merge_version.hash

            # Update target branch
            target.head = merge_version.hash

            # Mark source branch as merged if needed
            if source.type != BranchType.MAIN:
                source.is_merged = True
                source.merged_at = datetime.utcnow()

            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.branches_merged",
                {
                    "campaign_id": str(mr.campaign_id),
                    "merge_request_id": str(mr.id),
                    "source": mr.source_branch,
                    "target": mr.target_branch,
                    "version": merge_version.hash
                }
            )

            return merge_version

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to merge branches", error=str(e))
            raise ValueError(f"Failed to merge branches: {e}")

    async def resolve_conflicts(
        self,
        merge_request_id: UUID,
        resolutions: Dict[str, Dict],
    ) -> List[Conflict]:
        """Resolve merge conflicts."""
        try:
            mr = self.db.query(MergeRequest).get(merge_request_id)
            if not mr:
                raise ValueError("Merge request not found")

            conflicts = self.db.query(Conflict).filter_by(
                merge_request_id=merge_request_id,
                resolution=None
            ).all()

            # Apply resolutions
            for conflict in conflicts:
                if str(conflict.id) in resolutions:
                    resolution = resolutions[str(conflict.id)]
                    conflict.resolution = resolution["resolution"]
                    conflict.resolved_by = resolution["resolved_by"]
                    conflict.resolved_at = datetime.utcnow()
                    conflict.resolution_data = resolution.get("data")

            # Check if all conflicts resolved
            unresolved = self.db.query(Conflict).filter_by(
                merge_request_id=merge_request_id,
                resolution=None
            ).count()

            if unresolved == 0:
                mr.status = "open"

            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.conflicts_resolved",
                {
                    "campaign_id": str(mr.campaign_id),
                    "merge_request_id": str(mr.id),
                    "resolved_count": len(resolutions),
                    "remaining_count": unresolved
                }
            )

            return conflicts

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to resolve conflicts", error=str(e))
            raise ValueError(f"Failed to resolve conflicts: {e}")

    async def _detect_conflicts(
        self,
        campaign_id: UUID,
        source_hash: str,
        target_hash: str
    ) -> List[MergeConflict]:
        """Detect conflicts between versions."""
        # Get versions
        source = self.db.query(Version).filter_by(hash=source_hash).first()
        target = self.db.query(Version).filter_by(hash=target_hash).first()

        conflicts = []

        # Compare content
        source_content = source.content
        target_content = target.content

        # Check for structural conflicts
        for key in set(source_content.keys()) | set(target_content.keys()):
            if key in source_content and key in target_content:
                if isinstance(source_content[key], dict):
                    # Recursively check nested structures
                    nested_conflicts = self._check_nested_conflicts(
                        key,
                        source_content[key],
                        target_content[key]
                    )
                    conflicts.extend(nested_conflicts)
                elif source_content[key] != target_content[key]:
                    conflicts.append(MergeConflict(
                        path=key,
                        field=key,
                        source_value=str(source_content[key]),
                        target_value=str(target_content[key]),
                        resolution_options=["take_source", "take_target", "merge"]
                    ))

        return conflicts

    def _check_nested_conflicts(
        self,
        path: str,
        source_dict: Dict,
        target_dict: Dict
    ) -> List[MergeConflict]:
        """Recursively check for conflicts in nested structures."""
        conflicts = []
        for key in set(source_dict.keys()) | set(target_dict.keys()):
            full_path = f"{path}.{key}"
            if key in source_dict and key in target_dict:
                if isinstance(source_dict[key], dict):
                    nested = self._check_nested_conflicts(
                        full_path,
                        source_dict[key],
                        target_dict[key]
                    )
                    conflicts.extend(nested)
                elif source_dict[key] != target_dict[key]:
                    conflicts.append(MergeConflict(
                        path=full_path,
                        field=key,
                        source_value=str(source_dict[key]),
                        target_value=str(target_dict[key]),
                        resolution_options=["take_source", "take_target", "merge"]
                    ))
            else:
                conflicts.append(MergeConflict(
                    path=full_path,
                    field=key,
                    source_value=str(source_dict.get(key, "missing")),
                    target_value=str(target_dict.get(key, "missing")),
                    resolution_options=["take_source", "take_target"]
                ))
        return conflicts

    async def _create_conflicts(
        self,
        merge_request_id: UUID,
        conflicts: List[MergeConflict]
    ) -> List[Conflict]:
        """Create conflict records."""
        conflict_records = []
        for conflict in conflicts:
            record = Conflict(
                merge_request_id=merge_request_id,
                entity_type="content",
                entity_id=conflict.path,
                conflict_type="content",
                source_version=conflict.source_value,
                target_version=conflict.target_value,
            )
            self.db.add(record)
            conflict_records.append(record)
        return conflict_records

    async def _merge_content(
        self,
        source_content: Dict,
        target_content: Dict,
        strategy: MergeStrategy,
        resolution_data: Optional[Dict] = None
    ) -> Dict:
        """Merge content based on strategy."""
        if strategy == MergeStrategy.MANUAL:
            if not resolution_data:
                raise ValueError("Resolution data required for manual merge")
            return await self._apply_manual_resolutions(
                source_content,
                target_content,
                resolution_data
            )
        elif strategy == MergeStrategy.AUTO:
            return await self._auto_merge(source_content, target_content)
        elif strategy == MergeStrategy.CHERRY_PICK:
            if not resolution_data:
                raise ValueError("Cherry-pick paths required")
            return await self._cherry_pick_changes(
                source_content,
                target_content,
                resolution_data["paths"]
            )
        else:
            raise ValueError(f"Unsupported merge strategy: {strategy}")

    async def _apply_manual_resolutions(
        self,
        source_content: Dict,
        target_content: Dict,
        resolution_data: Dict
    ) -> Dict:
        """Apply manual conflict resolutions."""
        merged = target_content.copy()
        for path, resolution in resolution_data.items():
            if resolution["choice"] == "take_source":
                self._set_nested_value(merged, path, self._get_nested_value(source_content, path))
            elif resolution["choice"] == "merge":
                source_value = self._get_nested_value(source_content, path)
                target_value = self._get_nested_value(target_content, path)
                merged_value = self._merge_values(source_value, target_value, resolution.get("merge_strategy"))
                self._set_nested_value(merged, path, merged_value)
        return merged

    async def _auto_merge(self, source_content: Dict, target_content: Dict) -> Dict:
        """Automatically merge content."""
        merged = target_content.copy()
        for key, value in source_content.items():
            if key not in target_content:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(target_content[key], dict):
                merged[key] = await self._auto_merge(value, target_content[key])
            elif value != target_content[key]:
                # For conflicts, prefer target content
                continue
        return merged

    async def _cherry_pick_changes(
        self,
        source_content: Dict,
        target_content: Dict,
        paths: List[str]
    ) -> Dict:
        """Cherry-pick specific changes."""
        merged = target_content.copy()
        for path in paths:
            value = self._get_nested_value(source_content, path)
            if value is not None:
                self._set_nested_value(merged, path, value)
        return merged

    def _generate_hash(self, content: Dict) -> str:
        """Generate a hash for version content."""
        # Sort dictionary to ensure consistent hashing
        sorted_content = json.dumps(content, sort_keys=True)
        return hashlib.sha1(sorted_content.encode()).hexdigest()

    def _get_nested_value(self, content: Dict, path: str) -> Any:
        """Get a nested dictionary value using dot notation."""
        current = content
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _set_nested_value(self, content: Dict, path: str, value: Any) -> None:
        """Set a nested dictionary value using dot notation."""
        parts = path.split(".")
        current = content
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
