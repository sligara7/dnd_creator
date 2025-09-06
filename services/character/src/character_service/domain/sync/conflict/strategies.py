"""State conflict resolution strategies."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

from character_service.domain.sync.exceptions import SyncConflictError
from character_service.domain.sync.models import (
    FieldSyncMode,
    StateChange,
    SyncDirection,
)
from character_service.domain.sync.utils import (
    detect_changes,
    diff_values,
    extract_value,
    set_value,
)


class ResolutionStrategy(ABC):
    """Base class for conflict resolution strategies."""

    @abstractmethod
    def resolve(
        self,
        field_path: str,
        base_value: Any,
        local_value: Any,
        remote_value: Any,
        sync_mode: FieldSyncMode = FieldSyncMode.FULL,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Any, Dict]:
        """Resolve conflict between values.

        Args:
            field_path: Path to conflicting field
            base_value: Original base value
            local_value: Local (character) value
            remote_value: Remote (campaign) value
            sync_mode: Sync mode for field
            timestamp: Optional timestamp for resolution
            metadata: Optional metadata for resolution

        Returns:
            Tuple of (resolved value, resolution metadata)
        """
        ...


class LastWriteWinsStrategy(ResolutionStrategy):
    """Last write wins resolution strategy."""

    def resolve(
        self,
        field_path: str,
        base_value: Any,
        local_value: Any,
        remote_value: Any,
        sync_mode: FieldSyncMode = FieldSyncMode.FULL,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Any, Dict]:
        """Resolve using last write wins strategy.

        The most recent change wins, based on timestamps.
        """
        meta = metadata or {}
        local_time = meta.get("local_timestamp")
        remote_time = meta.get("remote_timestamp")

        # If no timestamps, prefer remote value
        if not local_time or not remote_time:
            return remote_value, {
                "strategy": "last_write_wins",
                "reason": "no timestamps, using remote",
            }

        # Compare timestamps
        if local_time > remote_time:
            return local_value, {
                "strategy": "last_write_wins",
                "reason": "local more recent",
                "local_timestamp": local_time,
                "remote_timestamp": remote_time,
            }
        return remote_value, {
            "strategy": "last_write_wins",
            "reason": "remote more recent",
            "local_timestamp": local_time,
            "remote_timestamp": remote_time,
        }


class MergeStrategy(ResolutionStrategy):
    """Merge-based resolution strategy."""

    def resolve(
        self,
        field_path: str,
        base_value: Any,
        local_value: Any,
        remote_value: Any,
        sync_mode: FieldSyncMode = FieldSyncMode.FULL,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Any, Dict]:
        """Resolve using merge strategy.

        For lists: Union of values
        For dicts: Deep merge of values
        For scalars: Remote value wins
        """
        if isinstance(local_value, dict) and isinstance(remote_value, dict):
            # Deep merge dictionaries
            result = base_value.copy() if isinstance(base_value, dict) else {}
            result.update(local_value)  # Local changes
            result.update(remote_value)  # Remote changes win conflicts
            return result, {
                "strategy": "merge",
                "reason": "dictionary merge",
            }

        if isinstance(local_value, (list, set)) and isinstance(remote_value, (list, set)):
            # Union of lists/sets
            combined = list(set(local_value) | set(remote_value))
            return combined, {
                "strategy": "merge",
                "reason": "list/set union",
            }

        # Default to remote value for scalar values
        return remote_value, {
            "strategy": "merge",
            "reason": "scalar default to remote",
        }


class IncrementalStrategy(ResolutionStrategy):
    """Incremental value resolution strategy."""

    def resolve(
        self,
        field_path: str,
        base_value: Any,
        local_value: Any,
        remote_value: Any,
        sync_mode: FieldSyncMode = FieldSyncMode.FULL,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Any, Dict]:
        """Resolve using incremental strategy.

        For numeric values, combines deltas from both sides.
        """
        if not all(isinstance(v, (int, float)) for v in (base_value, local_value, remote_value)):
            raise SyncConflictError(
                f"Incremental strategy requires numeric values: {field_path}"
            )

        # Calculate and combine deltas
        local_delta = local_value - base_value
        remote_delta = remote_value - base_value
        result = base_value + local_delta + remote_delta

        return result, {
            "strategy": "incremental",
            "reason": "combined deltas",
            "local_delta": local_delta,
            "remote_delta": remote_delta,
        }


class RuleBasedStrategy(ResolutionStrategy):
    """Rule-based resolution strategy."""

    def __init__(self) -> None:
        """Initialize strategy."""
        self.rules = {
            # Combat state rules
            "hit_points": self._resolve_hit_points,
            "temporary_hit_points": self._resolve_temp_hp,
            "conditions": self._resolve_conditions,
            # Resource rules
            "spell_slots": self._resolve_spell_slots,
            "class_resources": self._resolve_class_resources,
            # Feature rules
            "features": self._resolve_features,
            "traits": self._resolve_traits,
            # Item rules
            "inventory": self._resolve_inventory,
            "equipment": self._resolve_equipment,
            # Progress rules
            "experience_points": self._resolve_xp,
            "milestones": self._resolve_milestones,
        }

    def resolve(
        self,
        field_path: str,
        base_value: Any,
        local_value: Any,
        remote_value: Any,
        sync_mode: FieldSyncMode = FieldSyncMode.FULL,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Any, Dict]:
        """Resolve using rule-based strategy.

        Applies specific rules based on field path.
        """
        # Find matching rule
        rule = None
        for pattern, handler in self.rules.items():
            if pattern in field_path:
                rule = handler
                break

        if not rule:
            # Default to merge strategy
            strategy = MergeStrategy()
            return strategy.resolve(
                field_path,
                base_value,
                local_value,
                remote_value,
                sync_mode,
                timestamp,
                metadata,
            )

        # Apply rule
        return rule(
            field_path,
            base_value,
            local_value,
            remote_value,
            sync_mode,
            timestamp,
            metadata,
        )

    def _resolve_hit_points(
        self,
        field_path: str,
        base_value: int,
        local_value: int,
        remote_value: int,
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve hit points conflict."""
        # Use lower value to be safe
        result = min(local_value, remote_value)
        return result, {
            "strategy": "rule_based",
            "rule": "hit_points",
            "reason": "using lower value",
        }

    def _resolve_temp_hp(
        self,
        field_path: str,
        base_value: int,
        local_value: int,
        remote_value: int,
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve temporary hit points conflict."""
        # Use higher value
        result = max(local_value, remote_value)
        return result, {
            "strategy": "rule_based",
            "rule": "temp_hp",
            "reason": "using higher value",
        }

    def _resolve_conditions(
        self,
        field_path: str,
        base_value: List[str],
        local_value: List[str],
        remote_value: List[str],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve conditions conflict."""
        # Union of conditions
        result = list(set(local_value) | set(remote_value))
        return result, {
            "strategy": "rule_based",
            "rule": "conditions",
            "reason": "combined conditions",
        }

    def _resolve_spell_slots(
        self,
        field_path: str,
        base_value: Dict[str, int],
        local_value: Dict[str, int],
        remote_value: Dict[str, int],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve spell slots conflict."""
        # Use lower values
        result = {}
        all_levels = set(local_value.keys()) | set(remote_value.keys())
        for level in all_levels:
            local_slots = local_value.get(level, 0)
            remote_slots = remote_value.get(level, 0)
            result[level] = min(local_slots, remote_slots)
        return result, {
            "strategy": "rule_based",
            "rule": "spell_slots",
            "reason": "using lower values",
        }

    def _resolve_class_resources(
        self,
        field_path: str,
        base_value: Dict[str, Any],
        local_value: Dict[str, Any],
        remote_value: Dict[str, Any],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve class resources conflict."""
        # Use lower values for numeric resources
        result = {}
        for resource, value in remote_value.items():
            if isinstance(value, (int, float)):
                local_val = local_value.get(resource, 0)
                result[resource] = min(value, local_val)
            else:
                # Use remote value for non-numeric
                result[resource] = value
        return result, {
            "strategy": "rule_based",
            "rule": "class_resources",
            "reason": "using lower values for numeric",
        }

    def _resolve_features(
        self,
        field_path: str,
        base_value: List[Dict],
        local_value: List[Dict],
        remote_value: List[Dict],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve features conflict."""
        # Merge by feature ID
        result = []
        seen = set()
        for feature in local_value + remote_value:
            if feature["id"] not in seen:
                seen.add(feature["id"])
                result.append(feature)
        return result, {
            "strategy": "rule_based",
            "rule": "features",
            "reason": "merged by ID",
        }

    def _resolve_traits(
        self,
        field_path: str,
        base_value: List[Dict],
        local_value: List[Dict],
        remote_value: List[Dict],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve traits conflict."""
        # Similar to features
        return self._resolve_features(
            field_path,
            base_value,
            local_value,
            remote_value,
            sync_mode,
            timestamp,
            metadata,
        )

    def _resolve_inventory(
        self,
        field_path: str,
        base_value: List[Dict],
        local_value: List[Dict],
        remote_value: List[Dict],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve inventory conflict."""
        # Merge items by ID, use higher quantity
        result = []
        item_map = {}
        for item in local_value + remote_value:
            if item["id"] not in item_map:
                item_map[item["id"]] = item
            else:
                # Use higher quantity
                existing = item_map[item["id"]]
                existing["quantity"] = max(
                    existing.get("quantity", 1),
                    item.get("quantity", 1),
                )
        result = list(item_map.values())
        return result, {
            "strategy": "rule_based",
            "rule": "inventory",
            "reason": "merged by ID with max quantity",
        }

    def _resolve_equipment(
        self,
        field_path: str,
        base_value: Dict[str, Dict],
        local_value: Dict[str, Dict],
        remote_value: Dict[str, Dict],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve equipment conflict."""
        # Use remote state for equipped items
        return remote_value, {
            "strategy": "rule_based",
            "rule": "equipment",
            "reason": "using remote state",
        }

    def _resolve_xp(
        self,
        field_path: str,
        base_value: int,
        local_value: int,
        remote_value: int,
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve experience points conflict."""
        strategy = IncrementalStrategy()
        return strategy.resolve(
            field_path,
            base_value,
            local_value,
            remote_value,
            sync_mode,
            timestamp,
            metadata,
        )

    def _resolve_milestones(
        self,
        field_path: str,
        base_value: List[Dict],
        local_value: List[Dict],
        remote_value: List[Dict],
        sync_mode: FieldSyncMode,
        timestamp: Optional[datetime],
        metadata: Optional[Dict],
    ) -> Tuple[Any, Dict]:
        """Resolve milestones conflict."""
        # Union of milestone IDs
        seen = set()
        result = []
        for milestone in local_value + remote_value:
            if milestone["id"] not in seen:
                seen.add(milestone["id"])
                result.append(milestone)
        return result, {
            "strategy": "rule_based",
            "rule": "milestones",
            "reason": "union of milestones",
        }


# Default strategy instances
LAST_WRITE_WINS = LastWriteWinsStrategy()
MERGE = MergeStrategy()
INCREMENTAL = IncrementalStrategy()
RULE_BASED = RuleBasedStrategy()

# Strategy mapping
STRATEGIES = {
    "last_write_wins": LAST_WRITE_WINS,
    "merge": MERGE,
    "incremental": INCREMENTAL,
    "rule_based": RULE_BASED,
}
