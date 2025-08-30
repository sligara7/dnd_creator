"""
Character ability score management service.

This service handles all ability score related operations including:
- Ability score calculation and tracking
- ASI (Ability Score Improvement) management 
- Temporary and permanent modifiers
- Validation and versioning
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging

from src.models.core_models import AbilityScore, AbilityScoreSource
from src.services.data.rules import validate_ability_score_ranges
from src.services.character.validation import CreationResult

logger = logging.getLogger(__name__)

class AbilityService:
    """Service for managing character ability scores."""
    
    def __init__(self, character_id: str = None):
        self.character_id = character_id or str(uuid.uuid4())
        self.version = 1
        self.ability_score_maximums = {}
        self.temporary_modifiers = {}
        self.ability_snapshots = {}
    
    def calculate_ability_score(self, base_score: int, 
                              bonuses: Dict[str, int] = None,
                              temp_modifiers: Dict[str, int] = None) -> int:
        """Calculate total ability score with all modifiers."""
        total = base_score
        
        # Add permanent bonuses
        if bonuses:
            total += sum(bonuses.values())
            
        # Add temporary modifiers
        if temp_modifiers:
            total += sum(temp_modifiers.values())
            
        # Enforce standard D&D ability score limits
        total = min(30, max(1, total))
        
        return total
    
    def add_temporary_modifier(self, ability: str, amount: int, 
                             source: str, duration: str = None) -> None:
        """Add a temporary modifier to an ability score."""
        if ability not in self.temporary_modifiers:
            self.temporary_modifiers[ability] = []
            
        modifier = {
            "amount": amount,
            "source": source,
            "duration": duration,
            "applied_at": datetime.utcnow().isoformat()
        }
        
        self.temporary_modifiers[ability].append(modifier)
        logger.info(f"Added temporary {amount:+d} to {ability} from {source}")
    
    def remove_temporary_modifier(self, ability: str, source: str) -> bool:
        """Remove a temporary modifier by source."""
        if ability not in self.temporary_modifiers:
            return False
            
        original_count = len(self.temporary_modifiers[ability])
        self.temporary_modifiers[ability] = [
            mod for mod in self.temporary_modifiers[ability]
            if mod["source"] != source
        ]
        
        removed = len(self.temporary_modifiers[ability]) < original_count
        if removed:
            logger.info(f"Removed temporary modifier from {ability} ({source})")
            
        return removed
    
    def set_ability_maximum(self, ability: str, maximum: int, 
                          source: str = "Class Feature") -> None:
        """Set a custom maximum for an ability score."""
        self.ability_score_maximums[ability] = {
            "value": maximum,
            "source": source
        }
        logger.info(f"Set {ability} maximum to {maximum} from {source}")
    
    def create_snapshot(self, ability_scores: Dict[str, Any], 
                       description: str = "") -> int:
        """Create a snapshot of current ability scores."""
        snapshot_id = self.version
        
        snapshot = {
            "id": snapshot_id,
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "ability_scores": ability_scores.copy(),
            "temporary_modifiers": self.temporary_modifiers.copy(),
            "maximums": self.ability_score_maximums.copy()
        }
        
        self.ability_snapshots[snapshot_id] = snapshot
        self.version += 1
        
        logger.info(f"Created ability score snapshot {snapshot_id}: {description}")
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        """Restore ability scores from a snapshot."""
        if snapshot_id not in self.ability_snapshots:
            return None
            
        snapshot = self.ability_snapshots[snapshot_id]
        self.temporary_modifiers = snapshot["temporary_modifiers"].copy()
        self.ability_score_maximums = snapshot["maximums"].copy()
        
        logger.info(f"Restored ability scores to snapshot {snapshot_id}")
        return snapshot["ability_scores"]
    
    def validate_ability_scores(self, ability_scores: Dict[str, Any]) -> CreationResult:
        """Validate ability scores against D&D 5e rules."""
        return validate_ability_score_ranges(ability_scores)
    
    def get_summary(self, ability_scores: Dict[str, AbilityScore]) -> Dict[str, Any]:
        """Get a summary of current ability scores and modifiers."""
        summary = {}
        
        for ability_name, ability_score in ability_scores.items():
            summary[ability_name] = {
                "base_score": ability_score.base_score,
                "current_score": self.calculate_ability_score(
                    ability_score.base_score,
                    ability_score.bonuses,
                    {mod["source"]: mod["amount"] 
                     for mod in self.temporary_modifiers.get(ability_name, [])}
                ),
                "modifier": (ability_score.total_score - 10) // 2,
                "temporary_modifiers": self.temporary_modifiers.get(ability_name, []),
                "maximum": self.ability_score_maximums.get(ability_name, {"value": 20})
            }
        
        return {
            "abilities": summary,
            "version": self.version,
            "snapshots": len(self.ability_snapshots)
        }
