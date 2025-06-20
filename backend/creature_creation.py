"""
Simple creature creation module for D&D Character Creator.
Production-ready minimal implementation.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class CreatureConfig:
    """Configuration for creature creation process."""
    base_timeout: int = 15
    max_retries: int = 2
    include_tactics: bool = True
    include_lore: bool = False
    auto_calculate_cr: bool = True

@dataclass
class CreatureResult:
    """Result container for creature creation operations."""
    
    def __init__(self, success: bool = False, creature_data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.creature_data = creature_data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)

class CreatureCreator:
    """Simple creature creation service."""
    
    def __init__(self, config: Optional[CreatureConfig] = None):
        self.config = config or CreatureConfig()
    
    def create_creature(self, name: str, creature_type: str, 
                       challenge_rating: float = 1.0,
                       description: str = "") -> CreatureResult:
        """Create a basic creature."""
        start_time = time.time()
        
        try:
            creature_data = {
                "name": name,
                "type": creature_type,
                "challenge_rating": challenge_rating,
                "description": description,
                "hit_points": max(1, int(challenge_rating * 10)),
                "armor_class": max(10, int(10 + challenge_rating)),
                "stats": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "created_at": time.time()
            }
            
            result = CreatureResult(success=True, creature_data=creature_data)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Created creature '{name}' in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create creature '{name}': {e}")
            result = CreatureResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def get_creature_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get basic creature templates."""
        return {
            "goblin": {
                "type": "humanoid",
                "challenge_rating": 0.25,
                "hit_points": 7,
                "armor_class": 15
            },
            "orc": {
                "type": "humanoid", 
                "challenge_rating": 1.0,
                "hit_points": 15,
                "armor_class": 13
            },
            "dragon": {
                "type": "dragon",
                "challenge_rating": 10.0,
                "hit_points": 200,
                "armor_class": 18
            }
        }
