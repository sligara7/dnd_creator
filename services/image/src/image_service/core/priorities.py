"""Priority definitions for generation tasks."""

from dataclasses import dataclass
from typing import Dict, Optional

from image_service.core.constants import (
    QUEUE_PRIORITY_HIGH,
    QUEUE_PRIORITY_LOW,
    QUEUE_PRIORITY_NORMAL,
)


@dataclass
class TaskPriority:
    """Task priority configuration."""

    base: int
    character_boost: bool = False  # Boost for character-related tasks
    map_boost: bool = False  # Boost for map-related tasks
    session_boost: bool = False  # Boost for in-session tasks
    antitheticon_boost: bool = False  # Boost for Antitheticon tasks


# Base priority configurations
PORTRAIT_PRIORITY = TaskPriority(
    base=QUEUE_PRIORITY_NORMAL,
    character_boost=True,
)

MAP_TACTICAL_PRIORITY = TaskPriority(
    base=QUEUE_PRIORITY_NORMAL,
    map_boost=True,
    session_boost=True,
)

MAP_CAMPAIGN_PRIORITY = TaskPriority(
    base=QUEUE_PRIORITY_NORMAL,
    map_boost=True,
)

ITEM_PRIORITY = TaskPriority(
    base=QUEUE_PRIORITY_NORMAL,
    character_boost=True,
)

# Priority boost values
BOOST_VALUES = {
    "character": 10,  # Character-related tasks
    "map": 10,  # Map-related tasks
    "session": 20,  # In-session tasks
    "antitheticon": 15,  # Antitheticon campaign tasks
}

# Task type to priority mapping
TASK_PRIORITIES: Dict[str, TaskPriority] = {
    "portrait": PORTRAIT_PRIORITY,
    "map_tactical": MAP_TACTICAL_PRIORITY,
    "map_campaign": MAP_CAMPAIGN_PRIORITY,
    "item": ITEM_PRIORITY,
}


def calculate_priority(
    task_type: str,
    context: Optional[Dict[str, bool]] = None,
) -> int:
    """Calculate task priority based on type and context.
    
    Args:
        task_type: Type of generation task
        context: Task context flags:
            - in_session: Task is part of active session
            - is_character: Task is character-related
            - is_antitheticon: Task is for Antitheticon campaign
    
    Returns:
        Calculated priority value (higher is more important)
    """
    context = context or {}
    priority_config = TASK_PRIORITIES.get(task_type)
    
    if not priority_config:
        return QUEUE_PRIORITY_NORMAL

    # Start with base priority
    priority = priority_config.base

    # Add boosts based on context
    if priority_config.character_boost and context.get("is_character"):
        priority += BOOST_VALUES["character"]
    
    if priority_config.map_boost and context.get("is_map"):
        priority += BOOST_VALUES["map"]
    
    if priority_config.session_boost and context.get("in_session"):
        priority += BOOST_VALUES["session"]
    
    if priority_config.antitheticon_boost and context.get("is_antitheticon"):
        priority += BOOST_VALUES["antitheticon"]

    return min(priority, QUEUE_PRIORITY_HIGH)
