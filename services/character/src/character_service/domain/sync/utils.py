"""Utilities for state synchronization."""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar, Union
from uuid import UUID

from jsonpath_ng import parse

from character_service.domain.sync.exceptions import (
    SyncConflictError,
    SyncRetryError,
    SyncTimeoutError,
)
from character_service.domain.sync.models import (
    FieldSyncMode,
    StateChange,
    SyncMessage,
)

logger = logging.getLogger(__name__)


T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
):
    """Decorator for retrying async functions with exponential backoff."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        raise SyncRetryError(
                            f"Max retries ({max_retries}) exceeded: {str(e)}"
                        )
                    delay = min(base_delay * (exponential_base ** (retries - 1)), max_delay)
                    logger.warning(
                        "Retry %d after %0.1fs: %s", retries, delay, str(e)
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


async def with_timeout(
    coro, timeout: float, message: Optional[str] = None
) -> Any:
    """Run coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise SyncTimeoutError(message or "Operation timed out")


def extract_value(data: Dict, field_path: str) -> Any:
    """Extract value from data using field path."""
    jsonpath_expr = parse(field_path)
    matches = jsonpath_expr.find(data)
    if matches:
        return matches[0].value
    return None


def set_value(data: Dict, field_path: str, value: Any) -> None:
    """Set value in data using field path."""
    parts = field_path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


def diff_values(old_value: Any, new_value: Any) -> Tuple[bool, List[str]]:
    """Compare values and return diff paths."""
    if old_value == new_value:
        return False, []

    if isinstance(old_value, dict) and isinstance(new_value, dict):
        paths = []
        for key in set(old_value.keys()) | set(new_value.keys()):
            old_sub = old_value.get(key)
            new_sub = new_value.get(key)
            if old_sub != new_sub:
                changed, sub_paths = diff_values(old_sub, new_sub)
                if changed:
                    paths.extend([f"{key}.{p}" for p in sub_paths] if sub_paths else [key])
        return bool(paths), paths

    if isinstance(old_value, list) and isinstance(new_value, list):
        return True, ["[]"]  # Treat lists as atomic for now

    return True, []


def merge_values(
    base: Dict,
    theirs: Dict,
    ours: Dict,
    field_path: str,
    mode: FieldSyncMode = FieldSyncMode.FULL,
) -> Tuple[Dict, bool]:
    """Three-way merge of values."""
    base_value = extract_value(base, field_path)
    their_value = extract_value(theirs, field_path)
    our_value = extract_value(ours, field_path)

    if mode == FieldSyncMode.FULL:
        # If they haven't changed it, keep our changes
        if their_value == base_value:
            if our_value != base_value:
                return our_value, True
            return base_value, False

        # If we haven't changed it, take their changes
        if our_value == base_value:
            return their_value, True

        # Both changed - conflict
        raise SyncConflictError(
            f"Conflict in {field_path}: "
            f"base={base_value}, theirs={their_value}, ours={our_value}"
        )

    if mode == FieldSyncMode.INCREMENTAL:
        # Assuming numeric values for incremental
        if not all(
            isinstance(v, (int, float))
            for v in (base_value, their_value, our_value)
            if v is not None
        ):
            raise ValueError(f"Non-numeric value for incremental field {field_path}")

        # Calculate deltas
        their_delta = their_value - base_value if their_value is not None else 0
        our_delta = our_value - base_value if our_value is not None else 0

        # Combine deltas
        new_value = base_value + their_delta + our_delta
        return new_value, their_delta != 0 or our_delta != 0

    if mode == FieldSyncMode.MERGE:
        if isinstance(base_value, dict):
            # Merge dictionaries
            result = base_value.copy()
            result.update(their_value or {})
            result.update(our_value or {})
            return result, their_value != base_value or our_value != base_value

        if isinstance(base_value, list):
            # Merge lists (unique values)
            combined = list(
                set(base_value) | set(their_value or []) | set(our_value or [])
            )
            return combined, their_value != base_value or our_value != base_value

    return their_value, their_value != base_value


def detect_changes(
    old_data: Dict,
    new_data: Dict,
    fields: Optional[List[str]] = None,
) -> List[Tuple[str, Any, Any]]:
    """Detect changes between states."""
    changes = []
    fields = fields or list(set(old_data.keys()) | set(new_data.keys()))

    for field in fields:
        old_value = extract_value(old_data, field)
        new_value = extract_value(new_data, field)
        if old_value != new_value:
            changes.append((field, old_value, new_value))

    return changes


def group_changes(changes: List[StateChange]) -> Dict[str, List[StateChange]]:
    """Group changes by field path for efficient processing."""
    grouped = {}
    for change in changes:
        base_field = change.field_path.split(".")[0]
        if base_field not in grouped:
            grouped[base_field] = []
        grouped[base_field].append(change)
    return grouped


def reconcile_changes(
    changes: List[StateChange],
    base_state: Dict,
    current_state: Dict,
) -> Tuple[Dict, List[StateChange]]:
    """Reconcile changes with current state."""
    reconciled_state = current_state.copy()
    applied_changes = []

    # Group changes by field
    grouped = group_changes(changes)

    for field, field_changes in grouped.items():
        # Sort changes by timestamp
        field_changes.sort(key=lambda c: c.timestamp)

        # Get current field values
        base_value = extract_value(base_state, field)
        current_value = extract_value(current_state, field)

        # Apply changes in sequence
        for change in field_changes:
            try:
                # Check if change is still valid
                if change.old_value is not None and change.old_value != current_value:
                    continue  # Skip invalid change

                # Apply change based on sync mode
                if change.sync_mode == FieldSyncMode.INCREMENTAL:
                    # Calculate and apply delta
                    delta = change.new_value - change.old_value
                    new_value = current_value + delta
                else:
                    new_value = change.new_value

                set_value(reconciled_state, field, new_value)
                current_value = new_value
                applied_changes.append(change)

            except Exception as e:
                logger.warning(
                    "Failed to apply change %s: %s",
                    change.field_path,
                    str(e),
                )

    return reconciled_state, applied_changes
