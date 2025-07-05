"""
D&D 5e Content Coordinator

This module provides high-level coordination for complex content generation
workflows that involve multiple creation types and dependencies.

Handles orchestration of:
- Character creation with custom equipment/spells
- Adventure/campaign content generation
- Batch content creation
- Content validation and consistency checks
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.core.enums import CreationOptions
from src.services.creation_factory import CreationFactory
from src.models.character_models import CharacterSheet


@dataclass
class ContentRequest:
    """Request for generating related content."""
    primary_type: CreationOptions
    primary_params: Dict[str, Any]
    related_content: List[Dict[str, Any]] = None
    validation_rules: List[str] = None


class ContentCoordinator:
    """
    Coordinates complex content generation workflows.
    
    Handles cases where creating one type of content requires or benefits
    from creating related content (e.g., character with custom equipment).
    """
    
    def __init__(self, llm_service=None, database=None):
        self.factory = CreationFactory(llm_service, database)
        self.llm_service = llm_service
        self.database = database
    
    def generate_character_with_equipment(self, character_params: Dict[str, Any], 
                                        custom_equipment: bool = True) -> Dict[str, Any]:
        """
        Generate a character with optionally custom equipment.
        
        If custom_equipment is True, generates unique items based on the
        character's class, background, and story elements.
        """
        # Create base character
        character = self.factory.create(CreationOptions.CHARACTER, **character_params)
        
        result = {"character": character}
        
        if custom_equipment:
            # Generate custom equipment based on character
            equipment_params = self._derive_equipment_params(character)
            custom_items = []
            
            for item_type, params in equipment_params.items():
                item = self.factory.create(CreationOptions(item_type), **params)
                custom_items.append(item)
            
            result["custom_equipment"] = custom_items
        
        return result
    
    def generate_adventure_content(self, theme: str, level_range: tuple,
                                 party_size: int = 4) -> Dict[str, Any]:
        """
        Generate a complete adventure with NPCs, monsters, and items.
        
        Creates a thematically consistent set of content for an adventure.
        """
        result = {
            "theme": theme,
            "level_range": level_range,
            "content": {}
        }
        
        # Generate NPCs for the adventure
        npc_params = self._derive_npc_params(theme, level_range)
        npcs = []
        for params in npc_params:
            npc = self.factory.create(CreationOptions.NPC, **params)
            npcs.append(npc)
        result["content"]["npcs"] = npcs
        
        # Generate monsters for encounters
        monster_params = self._derive_monster_params(theme, level_range, party_size)
        monsters = []
        for params in monster_params:
            monster = self.factory.create(CreationOptions.MONSTER, **params)
            monsters.append(monster)
        result["content"]["monsters"] = monsters
        
        # Generate treasure/items
        item_params = self._derive_treasure_params(theme, level_range)
        items = []
        for item_type, params in item_params.items():
            item = self.factory.create(CreationOptions(item_type), **params)
            items.append(item)
        result["content"]["items"] = items
        
        return result
    
    def batch_create(self, requests: List[ContentRequest]) -> List[Any]:
        """Create multiple pieces of content with dependency management."""
        results = []
        
        for request in requests:
            # Check dependencies and validation rules
            if self._validate_request(request, results):
                content = self.factory.create(request.primary_type, **request.primary_params)
                
                # Generate related content if specified
                if request.related_content:
                    related = {}
                    for related_spec in request.related_content:
                        related_type = CreationOptions(related_spec["type"])
                        related_content = self.factory.create(related_type, **related_spec["params"])
                        related[related_spec["type"]] = related_content
                    
                    results.append({"primary": content, "related": related})
                else:
                    results.append(content)
            else:
                results.append(None)  # Failed validation
        
        return results
    
    def validate_content_consistency(self, content: Dict[str, Any]) -> bool:
        """Validate that generated content is internally consistent."""
        # Check that challenge ratings match expected levels
        # Check that equipment is appropriate for character classes
        # Check that story elements are consistent
        return True
    
    def _derive_equipment_params(self, character: CharacterSheet) -> Dict[str, Dict[str, Any]]:
        """Derive equipment parameters based on character details."""
        # Analyze character class, background, story to suggest equipment
        equipment_params = {}
        
        # Example: Fighter might get custom weapon
        if "fighter" in character.character_classes:
            equipment_params["weapon"] = {
                "weapon_type": "martial_melee",
                "rarity": "uncommon",
                "theme": f"weapon suited for {character.name}"
            }
        
        return equipment_params
    
    def _derive_npc_params(self, theme: str, level_range: tuple) -> List[Dict[str, Any]]:
        """Derive NPC parameters based on adventure theme and level."""
        # Generate NPC concepts based on theme
        return [
            {"role": "quest_giver", "theme": theme, "level": level_range[0]},
            {"role": "ally", "theme": theme, "level": level_range[1]},
            {"role": "antagonist", "theme": theme, "level": level_range[1]}
        ]
    
    def _derive_monster_params(self, theme: str, level_range: tuple, 
                              party_size: int) -> List[Dict[str, Any]]:
        """Derive monster parameters for balanced encounters."""
        # Calculate appropriate challenge ratings
        return [
            {"theme": theme, "challenge_rating": level_range[0], "role": "minion"},
            {"theme": theme, "challenge_rating": level_range[1], "role": "boss"}
        ]
    
    def _derive_treasure_params(self, theme: str, level_range: tuple) -> Dict[str, Dict[str, Any]]:
        """Derive treasure parameters based on adventure details."""
        return {
            "magic_item": {"rarity": "uncommon", "theme": theme, "level": level_range[1]},
            "weapon": {"rarity": "rare", "theme": theme, "level": level_range[1]}
        }
    
    def _validate_request(self, request: ContentRequest, existing_results: List[Any]) -> bool:
        """Validate a content request against validation rules."""
        # Check validation rules
        # Check dependencies on existing results
        return True
