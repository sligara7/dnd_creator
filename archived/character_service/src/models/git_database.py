"""Git-like database models for D&D entities."""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import uuid
from enum import Enum

class EntityType(Enum):
    """Types of entities in the database."""
    CHARACTER_PC = "character_pc"
    CHARACTER_NPC = "character_npc"
    MONSTER = "monster"
    WEAPON = "weapon"
    ARMOR = "armor"
    SPELL = "spell"
    ITEM = "item"
    FEATURE = "feature"
    GROUP = "group"

class BranchType(Enum):
    """Types of branches."""
    MAIN = "main"  # Original entity
    LEVEL_UP = "level_up"  # Level-up progression
    VARIANT = "variant"  # Different version (e.g., themed variant)
    INSTANCE = "instance"  # Copy for specific use (e.g., henchmen)
    FORK = "fork"  # Major divergence

@dataclass
class GitCommit:
    """Represents a change to an entity."""
    commit_id: str  # UUID
    entity_id: str  # UUID of entity
    parent_commit_id: Optional[str]  # Previous commit's UUID
    branch_name: str
    branch_type: BranchType
    changes: Dict[str, Any]  # The actual changes
    metadata: Dict[str, Any]  # Additional info
    timestamp: datetime
    message: str

@dataclass
class GitBranch:
    """Represents a branch of an entity."""
    branch_id: str  # UUID
    entity_id: str  # UUID of entity
    name: str
    type: BranchType
    head_commit_id: str  # Latest commit UUID
    parent_branch_id: Optional[str]  # Branch this was created from
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class EntityRelation:
    """Represents a relationship between entities."""
    relation_id: str  # UUID
    source_id: str  # UUID of source entity
    target_id: str  # UUID of target entity
    relation_type: str  # e.g., "owns", "member_of", "variant_of"
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class EntityGroup:
    """Represents a group of related entities."""
    group_id: str  # UUID
    name: str
    type: str  # e.g., "party", "encounter", "inventory"
    member_ids: Set[str]  # UUIDs of members
    metadata: Dict[str, Any]
    created_at: datetime

class ThemeProgressionType(Enum):
    """How an entity progresses through themes."""
    STATELESS = "stateless"  # Items: always branch from root
    PROGRESSIVE = "progressive"  # Characters: branch from current state

class ThemeVariant:
    """Represents a themed variant of an entity."""
    def __init__(self, original_id: str, theme: str, progression_type: ThemeProgressionType):
        self.original_id = original_id  # Root entity ID
        self.theme = theme
        self.progression_type = progression_type
        self.variants: Dict[str, Dict[str, Any]] = {}  # branch_id -> themed data
        self.progression_chain: List[str] = []  # Ordered list of branch IDs showing theme progression
        self.original_id = original_id  # Root entity ID
        self.theme = theme
        self.variants: Dict[str, Dict[str, Any]] = {}  # branch_id -> themed data

class GitDatabase:
    """Git-like database for D&D entities."""

    def __init__(self):
        self.theme_variants: Dict[str, ThemeVariant] = {}  # entity_id -> ThemeVariant
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.commits: Dict[str, GitCommit] = {}
        self.branches: Dict[str, GitBranch] = {}
        self.relations: Dict[str, EntityRelation] = {}
        self.groups: Dict[str, EntityGroup] = {}

    async def create_entity(self, entity_type: EntityType,
                          data: Dict[str, Any]) -> str:
        """Create a new entity with initial commit."""
        entity_id = str(uuid.uuid4())
        commit_id = str(uuid.uuid4())
        branch_id = str(uuid.uuid4())

        # Create main branch
        branch = GitBranch(
            branch_id=branch_id,
            entity_id=entity_id,
            name="main",
            type=BranchType.MAIN,
            head_commit_id=commit_id,
            parent_branch_id=None,
            created_at=datetime.utcnow(),
            metadata={"entity_type": entity_type.value}
        )

        # Create initial commit
        commit = GitCommit(
            commit_id=commit_id,
            entity_id=entity_id,
            parent_commit_id=None,
            branch_name="main",
            branch_type=BranchType.MAIN,
            changes=data,
            metadata={"entity_type": entity_type.value},
            timestamp=datetime.utcnow(),
            message="Initial creation"
        )

        # Store everything
        self.entities[entity_id] = {
            "type": entity_type,
            "current_data": data,
            "main_branch_id": branch_id
        }
        self.commits[commit_id] = commit
        self.branches[branch_id] = branch

        return entity_id

    def _get_progression_type(self, entity_type: EntityType) -> ThemeProgressionType:
        """Determine how an entity type progresses through themes."""
        if entity_type in [EntityType.CHARACTER_PC, EntityType.CHARACTER_NPC, EntityType.MONSTER]:
            return ThemeProgressionType.PROGRESSIVE
        return ThemeProgressionType.STATELESS

    async def create_themed_variant(self, entity_id: str, theme: str) -> str:
        """Create a themed variant of an entity.
        
        For items (STATELESS): Always branch from root
        For characters (PROGRESSIVE): Branch from most recent themed state
        """
        entity_type = self.entities[entity_id]["type"]
        progression_type = self._get_progression_type(entity_type)

        # Get or create theme variant tracker
        if entity_id not in self.theme_variants:
            self.theme_variants[entity_id] = ThemeVariant(
                entity_id, theme, progression_type)

        variant = self.theme_variants[entity_id]

        # Determine parent branch based on progression type
        if progression_type == ThemeProgressionType.STATELESS:
            # Items always branch from main
            parent_branch_id = self.entities[entity_id]["main_branch_id"]
        else:
            # Characters branch from most recent theme or main if first theme
            parent_branch_id = (variant.progression_chain[-1]
                               if variant.progression_chain
                               else self.entities[entity_id]["main_branch_id"])

        # Create new branch
        branch_id = await self.create_branch(
            entity_id=entity_id,
            branch_type=BranchType.VARIANT,
            name=f"theme_{theme}",
            parent_branch_id=parent_branch_id
        )

        # Store reference to themed variant
        variant.variants[branch_id] = {
            "theme": theme,
            "created_at": datetime.utcnow(),
            "parent_branch_id": parent_branch_id
        }

        # Update progression chain for characters
        if progression_type == ThemeProgressionType.PROGRESSIVE:
            variant.progression_chain.append(branch_id)

        return branch_id
        """Create a themed variant of an entity.
        Always branches from the root entity to maintain theme consistency."""
        # Get or create theme variant tracker
        if entity_id not in self.theme_variants:
            self.theme_variants[entity_id] = ThemeVariant(entity_id, theme)
        
        # Create a new branch from the main branch
        branch_id = await self.create_branch(
            entity_id=entity_id,
            branch_type=BranchType.VARIANT,
            name=f"theme_{theme}",
            parent_branch_id=self.entities[entity_id]["main_branch_id"]
        )
        
        # Store reference to themed variant
        self.theme_variants[entity_id].variants[branch_id] = {
            "theme": theme,
            "created_at": datetime.utcnow()
        }
        
        return branch_id

    async def get_themed_variant(self, entity_id: str,
                               theme: str,
                               previous_theme: Optional[str] = None) -> Optional[str]:
        """Get branch ID for a specific theme variant.
        
        For characters, if previous_theme is provided, find the variant that
        follows that theme in the progression chain.
        """
        if entity_id not in self.theme_variants:
            return None

        variant = self.theme_variants[entity_id]
        
        if variant.progression_type == ThemeProgressionType.STATELESS:
            # Items: just find the variant for this theme
            for branch_id, data in variant.variants.items():
                if data["theme"] == theme:
                    return branch_id
        else:
            # Characters: find the right point in the progression
            if previous_theme:
                # Find the variant that follows the previous theme
                prev_branch = None
                for branch_id in variant.progression_chain:
                    data = variant.variants[branch_id]
                    if prev_branch and data["theme"] == theme:
                        return branch_id
                    if data["theme"] == previous_theme:
                        prev_branch = branch_id
            else:
                # No previous theme, find most recent variant for this theme
                for branch_id in reversed(variant.progression_chain):
                    if variant.variants[branch_id]["theme"] == theme:
                        return branch_id

        return None
                               theme: str) -> Optional[str]:
        """Get branch ID for a specific theme variant."""
        if entity_id in self.theme_variants:
            variant = self.theme_variants[entity_id]
            for branch_id, data in variant.variants.items():
                if data["theme"] == theme:
                    return branch_id
        return None

    async def create_branch(self,
                          branch_type: BranchType,
                          name: str,
                          parent_branch_id: Optional[str] = None) -> str:
        """Create a new branch for an entity."""
        if parent_branch_id is None:
            parent_branch_id = self.entities[entity_id]["main_branch_id"]

        parent_branch = self.branches[parent_branch_id]
        
        branch_id = str(uuid.uuid4())
        branch = GitBranch(
            branch_id=branch_id,
            entity_id=entity_id,
            name=name,
            type=branch_type,
            head_commit_id=parent_branch.head_commit_id,  # Start at parent's head
            parent_branch_id=parent_branch_id,
            created_at=datetime.utcnow(),
            metadata={"branch_type": branch_type.value}
        )

        self.branches[branch_id] = branch
        return branch_id

    async def commit_changes(self, entity_id: str,
                           branch_id: str,
                           changes: Dict[str, Any],
                           message: str) -> str:
        """Commit changes to a branch."""
        branch = self.branches[branch_id]
        
        commit_id = str(uuid.uuid4())
        commit = GitCommit(
            commit_id=commit_id,
            entity_id=entity_id,
            parent_commit_id=branch.head_commit_id,
            branch_name=branch.name,
            branch_type=branch.type,
            changes=changes,
            metadata={},
            timestamp=datetime.utcnow(),
            message=message
        )

        # Update branch head
        branch.head_commit_id = commit_id
        
        # Store commit
        self.commits[commit_id] = commit
        
        # Update entity's current data if on main branch
        if branch.name == "main":
            self.entities[entity_id]["current_data"].update(changes)

        return commit_id

    async def create_relation(self, source_id: str,
                            target_id: str,
                            relation_type: str,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a relationship between entities."""
        relation_id = str(uuid.uuid4())
        relation = EntityRelation(
            relation_id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )

        self.relations[relation_id] = relation
        return relation_id

    async def create_group(self, name: str,
                          group_type: str,
                          member_ids: Optional[Set[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a group of entities."""
        group_id = str(uuid.uuid4())
        group = EntityGroup(
            group_id=group_id,
            name=name,
            type=group_type,
            member_ids=member_ids or set(),
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )

        self.groups[group_id] = group
        return group_id

    async def add_to_group(self, group_id: str, entity_id: str) -> None:
        """Add an entity to a group."""
        group = self.groups[group_id]
        group.member_ids.add(entity_id)

    async def remove_from_group(self, group_id: str, entity_id: str) -> None:
        """Remove an entity from a group."""
        group = self.groups[group_id]
        group.member_ids.remove(entity_id)

    async def get_entity_history(self, entity_id: str,
                               branch_id: Optional[str] = None) -> List[GitCommit]:
        """Get commit history for an entity on a branch."""
        if branch_id is None:
            branch_id = self.entities[entity_id]["main_branch_id"]

        branch = self.branches[branch_id]
        history = []
        
        # Walk back through commit history
        current_commit_id = branch.head_commit_id
        while current_commit_id:
            commit = self.commits[current_commit_id]
            history.append(commit)
            current_commit_id = commit.parent_commit_id

        return history

    async def get_entity_state(self, entity_id: str,
                             commit_id: Optional[str] = None,
                             branch_id: Optional[str] = None) -> Dict[str, Any]:
        """Get entity state at a specific commit or branch head."""
        if commit_id is None:
            if branch_id is None:
                branch_id = self.entities[entity_id]["main_branch_id"]
            commit_id = self.branches[branch_id].head_commit_id

        # Start with initial state
        state = {}
        
        # Apply all commits up to the specified one
        history = await self.get_entity_history(entity_id)
        for commit in reversed(history):  # Go from oldest to newest
            if commit.commit_id == commit_id:
                state.update(commit.changes)
                break
            state.update(commit.changes)

        return state

    async def get_related_entities(self, entity_id: str,
                                 relation_type: Optional[str] = None) -> List[str]:
        """Get entities related to this one."""
        related = []
        
        for relation in self.relations.values():
            if relation.source_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    related.append(relation.target_id)
            elif relation.target_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    related.append(relation.source_id)

        return related

    async def get_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """Get all members of a group with their current states."""
        group = self.groups[group_id]
        members = []
        
        for member_id in group.member_ids:
            state = await self.get_entity_state(member_id)
            members.append({
                "id": member_id,
                "type": self.entities[member_id]["type"],
                "state": state
            })

        return members
