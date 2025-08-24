"""
Git-Like Chapter Management System

Implements a version control system for D&D campaign chapters similar to git:
- Each chapter version is like a git commit with a unique hash
- Chapters can branch into multiple storylines
- Full lineage tracking and merging capabilities
- Visual git-like structure for campaign flow
- Skeleton chapters are the initial "commit" structure
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

# ============================================================================
# GIT-LIKE CHAPTER VERSION ENUMS
# ============================================================================

class ChapterVersionType(str, Enum):
    """Types of chapter versions in the git-like system."""
    SKELETON = "skeleton"          # Initial bare-bones chapter outline
    DRAFT = "draft"               # Work-in-progress chapter content
    PUBLISHED = "published"       # Finalized chapter ready for play
    PLAYED = "played"            # Chapter that has been played by players
    BRANCH = "branch"            # Alternative storyline branch
    MERGE = "merge"              # Merged multiple storylines

class BranchType(str, Enum):
    """Types of story branches."""
    MAIN = "main"                # Primary storyline (like git main/master)
    ALTERNATE = "alternate"      # Alternative story path
    PLAYER_CHOICE = "player_choice"  # Branch created by player decisions
    EXPERIMENTAL = "experimental"    # Testing new story ideas
    PARALLEL = "parallel"       # Concurrent storylines

# ============================================================================
# CHAPTER VERSION DATA STRUCTURES
# ============================================================================

@dataclass
class ChapterHash:
    """Git-like hash for chapter versions."""
    content_hash: str
    parent_hashes: List[str]
    timestamp: str
    author: str
    
    @classmethod
    def generate(cls, content: Dict[str, Any], parent_hashes: List[str] = None, author: str = "system") -> str:
        """Generate a git-like hash for chapter content."""
        parent_hashes = parent_hashes or []
        timestamp = datetime.utcnow().isoformat()
        
        # Create deterministic hash from content + metadata
        hash_data = {
            "content": content,
            "parents": sorted(parent_hashes),
            "timestamp": timestamp,
            "author": author
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(hash_string.encode()).hexdigest()[:12]  # Short hash like git

@dataclass  
class ChapterBranch:
    """Represents a story branch in the campaign."""
    name: str
    branch_type: BranchType
    head_commit: str  # Latest chapter version hash
    description: str
    created_at: datetime
    parent_branch: Optional[str] = None

@dataclass
class ChapterCommit:
    """Git-like commit for chapter versions."""
    hash: str
    parent_hashes: List[str]
    content: Dict[str, Any]
    message: str
    author: str
    timestamp: datetime
    branch_name: str
    version_type: ChapterVersionType
    player_choices: Optional[Dict[str, Any]] = None
    dm_notes: Optional[str] = None

# ============================================================================
# ENHANCED DATABASE MODELS FOR CHAPTER VERSIONING
# ============================================================================

# Note: These would extend the existing database_models.py

class ChapterVersion:
    """Extended Chapter model with git-like versioning."""
    
    # Additional fields for versioning (to be added to existing Chapter model)
    version_hash = Column(String(12), unique=True, nullable=False, index=True)
    parent_hashes = Column(JSON, default=list)  # List of parent version hashes
    branch_name = Column(String(100), default="main", nullable=False)
    version_type = Column(String(20), default=ChapterVersionType.DRAFT.value)
    commit_message = Column(Text)
    author = Column(String(100), default="system")
    player_choices = Column(JSON, default=dict)  # Choices that led to this version
    dm_notes = Column(Text)
    is_head = Column(Boolean, default=True)  # Is this the latest version in its branch?
    play_session_id = Column(String(36), nullable=True)  # Session when this was played

class CampaignBranch:
    """Story branches within a campaign."""
    
    # Additional model for tracking branches (new table)
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(100), nullable=False)
    branch_type = Column(String(20), default=BranchType.MAIN.value)
    head_commit = Column(String(12), nullable=False)  # Latest chapter version hash
    description = Column(Text)
    parent_branch = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChapterChoice:
    """Player choices that create new branches."""
    
    # New model for tracking player decisions (new table)
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    chapter_hash = Column(String(12), nullable=False)
    choice_description = Column(Text, nullable=False)
    consequences = Column(JSON, default=dict)
    players_involved = Column(JSON, default=list)
    session_date = Column(DateTime, default=datetime.utcnow)
    resulted_in_branch = Column(String(100), nullable=True)

# ============================================================================
# CHAPTER VERSION MANAGEMENT SERVICE
# ============================================================================

class ChapterVersionManager:
    """
    Manages git-like versioning for campaign chapters.
    
    Provides functionality similar to git for chapter content:
    - Commit new chapter versions
    - Branch storylines
    - Merge alternate paths
    - View commit history
    - Generate visual git graph
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # ========================================================================
    # CHAPTER COMMIT OPERATIONS
    # ========================================================================
    
    def commit_chapter(self, 
                      campaign_id: str,
                      chapter_content: Dict[str, Any],
                      branch_name: str = "main",
                      commit_message: str = "",
                      author: str = "system",
                      version_type: ChapterVersionType = ChapterVersionType.DRAFT,
                      parent_hashes: List[str] = None) -> ChapterCommit:
        """
        Commit a new chapter version (like git commit).
        
        Args:
            campaign_id: Campaign this chapter belongs to
            chapter_content: Full chapter data
            branch_name: Story branch name
            commit_message: Description of changes
            author: Who made this commit
            version_type: Type of chapter version
            parent_hashes: Parent chapter versions (for merges)
        
        Returns:
            ChapterCommit object with new version hash
        """
        # Generate version hash
        parent_hashes = parent_hashes or self._get_current_branch_head(campaign_id, branch_name)
        version_hash = ChapterHash.generate(chapter_content, parent_hashes, author)
        
        # Create commit record
        commit = ChapterCommit(
            hash=version_hash,
            parent_hashes=parent_hashes,
            content=chapter_content,
            message=commit_message,
            author=author,
            timestamp=datetime.utcnow(),
            branch_name=branch_name,
            version_type=version_type
        )
        
        # Save to database (implementation would use existing Chapter model + new fields)
        self._save_chapter_version(campaign_id, commit)
        
        # Update branch head
        self._update_branch_head(campaign_id, branch_name, version_hash)
        
        return commit
    
    def create_skeleton_commits(self,
                               campaign_id: str,
                               skeleton_chapters: List[Dict[str, Any]],
                               author: str = "system") -> List[ChapterCommit]:
        """
        Create initial skeleton chapter commits (like initial git repository).
        
        Args:
            campaign_id: Campaign ID
            skeleton_chapters: List of bare-bones chapter outlines
            author: Who created the skeleton
        
        Returns:
            List of skeleton chapter commits
        """
        commits = []
        previous_hash = None
        
        for i, chapter_outline in enumerate(skeleton_chapters):
            # Each skeleton chapter depends on the previous one
            parent_hashes = [previous_hash] if previous_hash else []
            
            commit = self.commit_chapter(
                campaign_id=campaign_id,
                chapter_content=chapter_outline,
                branch_name="main",
                commit_message=f"Initial skeleton: {chapter_outline.get('title', f'Chapter {i+1}')}",
                author=author,
                version_type=ChapterVersionType.SKELETON,
                parent_hashes=parent_hashes
            )
            
            commits.append(commit)
            previous_hash = commit.hash
        
        return commits
    
    # ========================================================================
    # BRANCHING OPERATIONS
    # ========================================================================
    
    def create_branch(self,
                     campaign_id: str,
                     branch_name: str,
                     from_hash: str,
                     branch_type: BranchType = BranchType.ALTERNATE,
                     description: str = "",
                     parent_branch: str = "main") -> ChapterBranch:
        """
        Create a new story branch (like git branch).
        
        Args:
            campaign_id: Campaign ID
            branch_name: Name of new branch
            from_hash: Chapter version hash to branch from
            branch_type: Type of branch being created
            description: Purpose of this branch
            parent_branch: Parent branch name
        
        Returns:
            ChapterBranch object
        """
        branch = ChapterBranch(
            name=branch_name,
            branch_type=branch_type,
            head_commit=from_hash,
            description=description,
            created_at=datetime.utcnow(),
            parent_branch=parent_branch
        )
        
        # Save branch to database
        self._save_branch(campaign_id, branch)
        
        return branch
    
    def branch_from_player_choice(self,
                                 campaign_id: str,
                                 current_chapter_hash: str,
                                 player_choice: Dict[str, Any],
                                 new_content: Dict[str, Any],
                                 author: str = "dm") -> Tuple[ChapterBranch, ChapterCommit]:
        """
        Create a new branch based on player choices during gameplay.
        
        Args:
            campaign_id: Campaign ID
            current_chapter_hash: Chapter where choice was made
            player_choice: Description of player decision
            new_content: Chapter content resulting from choice
            author: Who made this branch (usually DM)
        
        Returns:
            Tuple of (new branch, new chapter commit)
        """
        # Generate branch name based on choice
        choice_summary = player_choice.get("summary", "player_choice")
        branch_name = f"choice_{choice_summary}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
        
        # Create branch
        branch = self.create_branch(
            campaign_id=campaign_id,
            branch_name=branch_name,
            from_hash=current_chapter_hash,
            branch_type=BranchType.PLAYER_CHOICE,
            description=f"Player choice: {player_choice.get('description', 'Alternate path')}"
        )
        
        # Commit new content to the branch
        commit = self.commit_chapter(
            campaign_id=campaign_id,
            chapter_content=new_content,
            branch_name=branch_name,
            commit_message=f"Player choice result: {choice_summary}",
            author=author,
            version_type=ChapterVersionType.BRANCH,
            parent_hashes=[current_chapter_hash]
        )
        
        # Record the player choice
        self._record_player_choice(campaign_id, current_chapter_hash, player_choice, branch_name)
        
        return branch, commit
    
    # ========================================================================
    # HISTORY AND NAVIGATION
    # ========================================================================
    
    def get_chapter_history(self, campaign_id: str, chapter_hash: str) -> List[ChapterCommit]:
        """
        Get full history leading to a chapter version (like git log).
        
        Args:
            campaign_id: Campaign ID
            chapter_hash: Chapter version to trace back from
        
        Returns:
            List of commits in chronological order
        """
        history = []
        visited = set()
        
        def trace_parents(hash_val: str):
            if hash_val in visited:
                return
            visited.add(hash_val)
            
            commit = self._get_commit_by_hash(campaign_id, hash_val)
            if commit:
                history.append(commit)
                for parent_hash in commit.parent_hashes:
                    trace_parents(parent_hash)
        
        trace_parents(chapter_hash)
        return sorted(history, key=lambda c: c.timestamp)
    
    def get_campaign_branches(self, campaign_id: str) -> List[ChapterBranch]:
        """Get all story branches in a campaign."""
        return self._get_all_branches(campaign_id)
    
    def get_branch_commits(self, campaign_id: str, branch_name: str) -> List[ChapterCommit]:
        """Get all commits in a specific branch."""
        return self._get_commits_by_branch(campaign_id, branch_name)
    
    # ========================================================================
    # VISUAL GIT STRUCTURE GENERATION
    # ========================================================================
    
    def generate_campaign_graph(self, campaign_id: str) -> Dict[str, Any]:
        """
        Generate a git-like visual graph of the campaign structure.
        
        Returns:
            Graph data suitable for visualization (nodes, edges, branches)
        """
        branches = self.get_campaign_branches(campaign_id)
        all_commits = []
        
        # Collect all commits from all branches
        for branch in branches:
            commits = self.get_branch_commits(campaign_id, branch.name)
            all_commits.extend(commits)
        
        # Remove duplicates (commits can appear in multiple branches)
        unique_commits = {commit.hash: commit for commit in all_commits}
        
        # Build graph structure
        nodes = []
        edges = []
        
        for commit in unique_commits.values():
            # Create node for this commit
            node = {
                "id": commit.hash,
                "label": f"{commit.content.get('title', 'Untitled')} ({commit.hash[:7]})",
                "type": commit.version_type.value,
                "branch": commit.branch_name,
                "timestamp": commit.timestamp.isoformat(),
                "author": commit.author,
                "message": commit.message,
                "data": {
                    "chapter_content": commit.content,
                    "player_choices": commit.player_choices,
                    "dm_notes": commit.dm_notes
                }
            }
            nodes.append(node)
            
            # Create edges to parent commits
            for parent_hash in commit.parent_hashes:
                if parent_hash in unique_commits:
                    edge = {
                        "from": parent_hash,
                        "to": commit.hash,
                        "type": "parent_child"
                    }
                    edges.append(edge)
        
        # Add branch information
        branch_info = []
        for branch in branches:
            branch_info.append({
                "name": branch.name,
                "type": branch.branch_type.value,
                "head": branch.head_commit,
                "description": branch.description,
                "created_at": branch.created_at.isoformat(),
                "parent_branch": branch.parent_branch
            })
        
        return {
            "campaign_id": campaign_id,
            "nodes": nodes,
            "edges": edges,
            "branches": branch_info,
            "graph_metadata": {
                "total_commits": len(nodes),
                "total_branches": len(branches),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def generate_ascii_git_graph(self, campaign_id: str) -> str:
        """Generate ASCII art git graph like 'git log --graph'."""
        # Implementation would create ASCII visualization
        # This is a simplified version
        branches = self.get_campaign_branches(campaign_id)
        
        ascii_lines = []
        ascii_lines.append("Campaign Git Graph")
        ascii_lines.append("==================")
        
        for branch in branches:
            commits = self.get_branch_commits(campaign_id, branch.name)
            ascii_lines.append(f"\n* Branch: {branch.name} ({branch.branch_type.value})")
            
            for commit in commits[-5:]:  # Show last 5 commits
                ascii_lines.append(f"  {commit.hash[:7]} - {commit.content.get('title', 'Untitled')}")
                ascii_lines.append(f"    Author: {commit.author}")
                ascii_lines.append(f"    Message: {commit.message}")
        
        return "\n".join(ascii_lines)
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _get_current_branch_head(self, campaign_id: str, branch_name: str) -> List[str]:
        """Get the current head commit hash for a branch."""
        # Implementation would query database
        return []
    
    def _save_chapter_version(self, campaign_id: str, commit: ChapterCommit):
        """Save chapter version to database."""
        # Implementation would use existing Chapter model + new version fields
        pass
    
    def _update_branch_head(self, campaign_id: str, branch_name: str, new_hash: str):
        """Update the head commit for a branch."""
        # Implementation would update CampaignBranch table
        pass
    
    def _save_branch(self, campaign_id: str, branch: ChapterBranch):
        """Save branch information to database."""
        # Implementation would save to CampaignBranch table
        pass
    
    def _record_player_choice(self, campaign_id: str, chapter_hash: str, 
                             choice: Dict[str, Any], resulting_branch: str):
        """Record a player choice that created a branch."""
        # Implementation would save to ChapterChoice table
        pass
    
    def _get_commit_by_hash(self, campaign_id: str, commit_hash: str) -> Optional[ChapterCommit]:
        """Get a commit by its hash."""
        # Implementation would query database
        return None
    
    def _get_all_branches(self, campaign_id: str) -> List[ChapterBranch]:
        """Get all branches for a campaign."""
        # Implementation would query CampaignBranch table
        return []
    
    def _get_commits_by_branch(self, campaign_id: str, branch_name: str) -> List[ChapterCommit]:
        """Get all commits in a specific branch."""
        # Implementation would query Chapter table filtered by branch
        return []

# ============================================================================
# CHAPTER VERSION UTILITIES
# ============================================================================

class ChapterGitOperations:
    """High-level git-like operations for chapters."""
    
    def __init__(self, version_manager: ChapterVersionManager):
        self.vm = version_manager
    
    def checkout_branch(self, campaign_id: str, branch_name: str) -> List[ChapterCommit]:
        """Checkout a branch (get all chapters in that storyline)."""
        return self.vm.get_branch_commits(campaign_id, branch_name)
    
    def merge_branches(self, campaign_id: str, 
                      source_branch: str, target_branch: str,
                      merge_strategy: str = "manual") -> ChapterCommit:
        """Merge two story branches together."""
        # Implementation would handle merging logic
        pass
    
    def cherry_pick_chapter(self, campaign_id: str,
                           source_hash: str, target_branch: str) -> ChapterCommit:
        """Cherry-pick a chapter from one branch to another."""
        # Implementation would copy chapter to new branch
        pass
    
    def revert_to_commit(self, campaign_id: str, commit_hash: str) -> ChapterCommit:
        """Revert campaign to a previous chapter version."""
        # Implementation would create new commit that undoes changes
        pass

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ChapterVersionType',
    'BranchType', 
    'ChapterHash',
    'ChapterBranch',
    'ChapterCommit',
    'ChapterVersionManager',
    'ChapterGitOperations'
]
