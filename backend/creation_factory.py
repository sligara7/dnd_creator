"""
D&D 5e Creation Factory

This module coordinates the creation of different D&D 5e objects by mapping
creation types to their required models, generators, and validators.

Acts as a single entry point for creating all D&D 5e objects with the appropriate
subsets of functionality for each creation type.

Hierarchical Design:
- CHARACTER: Includes all sub-components (weapons, armor, spells, items) + umbrella validation
- MONSTER: Includes equipment/abilities + challenge rating validation  
- NPC: Hybrid of character/creature components + social validation
- Individual items (WEAPON, ARMOR, SPELL) for standalone creation

Two Main Workflows:
1. CREATE FROM SCRATCH: Generate entirely new objects using LLM based on text prompts
2. EVOLVE EXISTING: Update existing objects using their history/journal + new prompts
   - For characters: PRESERVES existing backstory, adds new experiences
   - Uses journal entries as context for evolution decisions
   - Equipment/spell changes should be story-driven

Examples:
    # Create new character from scratch (includes all equipment)
    character = await create_character_from_scratch("brave paladin seeking redemption")
    
    # Level up existing character (preserves backstory, uses journal context)
    leveled_char = await level_up_character(existing_char_data, {
        "new_level": 5, 
        "multiclass": "Warlock",
        "story_reason": "Made a pact after nearly dying in battle"
    })
    
    # Evolve character based on story events (additive, not replacement)
    evolved_char = await evolve_character(existing_char_data, 
        "gained fire immunity after dragon encounter, learned draconic language")
"""

from typing import Dict, Any, Optional, Type, List
from dataclasses import dataclass

from backend.enums import CreationOptions
from backend.character_models import CharacterCore
from backend.creation import CharacterCreator
from backend.generators import CustomContentGenerator

# For now, we'll use Dict for missing sheet types until they're implemented
CreatureSheet = Dict[str, Any]  # Placeholder for future CreatureSheet class
ItemSheet = Dict[str, Any]      # Placeholder for future ItemSheet class


@dataclass
class CreationConfig:
    """Configuration for creating a specific type of D&D object."""
    models: List[Type]
    generators: List[Type]
    validators: List[Type]
    formatters: List[Type]
    schemas: Dict[str, Any]


class CreationFactory:
    """
    Factory class that coordinates the creation of different D&D 5e objects.
    
    Maps creation types to their required components and provides a unified
    interface for creating characters, monsters, NPCs, items, etc.
    """
    
    def __init__(self, llm_service=None, database=None):
        self.llm_service = llm_service
        self.database = database
        self._configs = self._build_creation_configs()
        self.last_verbose_logs = []  # Store verbose logs from last creation
    
    def _build_creation_configs(self) -> Dict[CreationOptions, CreationConfig]:
        """Build mapping of creation types to their required components.
        
        Simplified version that only supports character creation for now.
        Other creation types are disabled until missing creator classes are implemented.
        """
        return {
            CreationOptions.CHARACTER: CreationConfig(
                models=[CharacterCore],
                generators=[CharacterCreator, CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            )
            # TODO: Add other creation types when creator classes are implemented:
            # CreationOptions.MONSTER: CreationConfig(...),
            # CreationOptions.NPC: CreationConfig(...),
            # CreationOptions.WEAPON: CreationConfig(...),
            # CreationOptions.ARMOR: CreationConfig(...),
            # CreationOptions.SPELL: CreationConfig(...),
            # CreationOptions.OTHER_ITEM: CreationConfig(...)
        }
    
    def get_config(self, creation_type: CreationOptions) -> CreationConfig:
        """Get the configuration for a specific creation type."""
        return self._configs.get(creation_type)
    
    async def create_from_scratch(self, creation_type: CreationOptions, prompt: str, **kwargs) -> Any:
        """
        Create a D&D object from scratch using LLM generation.
        
        Args:
            creation_type: The type of object to create
            prompt: Text description for LLM generation
            **kwargs: Additional parameters specific to the creation type
        
        Returns:
            The created D&D object
        """
        config = self.get_config(creation_type)
        if not config:
            raise ValueError(f"Unknown creation type: {creation_type}")
        
        # Route to appropriate creation method
        if creation_type == CreationOptions.CHARACTER:
            return await self._create_character_from_scratch(prompt, **kwargs)
        elif creation_type == CreationOptions.MONSTER:
            return await self._create_monster_from_scratch(prompt, **kwargs)
        elif creation_type == CreationOptions.NPC:
            return await self._create_npc_from_scratch(prompt, **kwargs)
        elif creation_type in [CreationOptions.WEAPON, CreationOptions.ARMOR, 
                               CreationOptions.SPELL, CreationOptions.OTHER_ITEM]:
            return await self._create_item_from_scratch(creation_type, prompt, **kwargs)
        else:
            raise ValueError(f"Creation not implemented for: {creation_type}")
    
    async def evolve_existing(self, creation_type: CreationOptions, existing_data: Dict[str, Any], 
                             evolution_prompt: str, **kwargs) -> Any:
        """
        Evolve an existing D&D object using its history and journal entries.
        
        Args:
            creation_type: The type of object to evolve
            existing_data: Current object data from database
            evolution_prompt: Description of how to evolve the object
            **kwargs: Additional parameters specific to the evolution
        
        Returns:
            The evolved D&D object
        """
        config = self.get_config(creation_type)
        if not config:
            raise ValueError(f"Unknown creation type: {creation_type}")
        
        # Route to appropriate evolution method
        if creation_type == CreationOptions.CHARACTER:
            return await self._evolve_character(existing_data, evolution_prompt, **kwargs)
        elif creation_type == CreationOptions.MONSTER:
            return await self._evolve_monster(existing_data, evolution_prompt, **kwargs)
        elif creation_type == CreationOptions.NPC:
            return await self._evolve_npc(existing_data, evolution_prompt, **kwargs)
        else:
            raise ValueError(f"Evolution not supported for: {creation_type}")
    
    # Legacy method for backward compatibility
    def create(self, creation_type: CreationOptions, **kwargs) -> Any:
        """
        Legacy creation method. Use create_from_scratch or evolve_existing instead.
        """
        import asyncio
        return asyncio.run(self.create_from_scratch(creation_type, **kwargs))
    
    async def _create_character_from_scratch(self, prompt: str, **kwargs) -> CharacterCore:
        """
        Create a new character from scratch using LLM generation.
        
        This includes generating the character's core stats, equipment (weapons, armor),
        spells (if applicable), and other items as a complete package.
        """
        creator = CharacterCreator(self.llm_service)
        result = await creator.create_character(prompt, kwargs.get('user_preferences'))
        if result.success:
            # Store verbose logs for later retrieval
            if hasattr(result, 'verbose_logs'):
                self.last_verbose_logs = result.verbose_logs
            return result.data
        else:
            # Store verbose logs even on failure
            if hasattr(result, 'verbose_logs'):
                self.last_verbose_logs = result.verbose_logs
            raise Exception(f"Character creation failed: {result.error}")
    
    async def _evolve_character(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> CharacterCore:
        """
        Evolve an existing character using journal and new prompt.
        
        Key principles for character evolution:
        1. PRESERVE existing backstory - only append new experiences
        2. Use journal entries as context for evolution decisions
        3. Respect character's established personality and goals
        4. Equipment/spell changes should be story-driven
        """
        creator = CharacterCreator(self.llm_service)
        
        # Determine evolution type
        evolution_type = kwargs.get('evolution_type', 'enhance')
        
        if evolution_type == 'refine':
            # Iterative refinement
            result = await creator.refine_character(
                existing_data, 
                evolution_prompt, 
                kwargs.get('user_preferences')
            )
        elif evolution_type == 'level_up':
            # Level up using journal
            journal_entries = kwargs.get('journal_entries', [])
            new_level = kwargs.get('new_level', existing_data.get('level', 1) + 1)
            multiclass = kwargs.get('multiclass_option')
            result = await creator.level_up_character_with_journal(
                existing_data, journal_entries, new_level, multiclass
            )
        else:
            # General enhancement
            preserve_backstory = kwargs.get('preserve_backstory', True)
            result = await creator.enhance_existing_character(
                existing_data, evolution_prompt, preserve_backstory
            )
        
        if result.success:
            # Store verbose logs for later retrieval
            if hasattr(result, 'verbose_logs'):
                self.last_verbose_logs = result.verbose_logs
            return result.data
        else:
            # Store verbose logs even on failure
            if hasattr(result, 'verbose_logs'):
                self.last_verbose_logs = result.verbose_logs
            raise Exception(f"Character evolution failed: {result.error}")
    
    async def _create_monster_from_scratch(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Create a new monster from scratch using LLM generation.
        
        TODO: Implement CreatureCreator class. For now, returns a placeholder.
        """
        return {
            "error": "Monster creation not yet implemented",
            "message": "CreatureCreator class needs to be implemented",
            "type": "monster",
            "prompt": prompt
        }
    
    async def _evolve_monster(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve an existing monster (e.g., power up, new abilities).
        
        TODO: Implement monster evolution logic.
        """
        return {
            "error": "Monster evolution not yet implemented",
            "message": "Monster evolution logic needs to be implemented",
            "type": "monster_evolution"
        }
    
    async def _create_npc_from_scratch(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Create a new NPC from scratch using hybrid logic.
        
        TODO: Implement NPCCreator class. For now, returns a placeholder.
        """
        return {
            "error": "NPC creation not yet implemented", 
            "message": "NPCCreator class needs to be implemented",
            "type": "npc",
            "prompt": prompt
        }
    
    async def _evolve_npc(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve an existing NPC (level up, story changes, etc.).
        
        TODO: Implement NPC evolution logic.
        """
        return {
            "error": "NPC evolution not yet implemented",
            "message": "NPC evolution logic needs to be implemented", 
            "type": "npc_evolution"
        }
    
    async def _create_item_from_scratch(self, item_type: CreationOptions, prompt: str, **kwargs) -> Dict[str, Any]:
        """Create a new item from scratch using LLM generation.
        
        TODO: Implement ItemCreator class. For now, returns a placeholder.
        """
        return {
            "error": "Item creation not yet implemented",
            "message": "ItemCreator class needs to be implemented", 
            "type": "item",
            "item_type": item_type.value if hasattr(item_type, 'value') else str(item_type),
            "prompt": prompt
        }
    
    def validate(self, creation_type: CreationOptions, obj: Any) -> bool:
        """Validate a created object using the appropriate validators."""
        config = self.get_config(creation_type)
        # Run all validators for this creation type
        return True
    
    def format(self, creation_type: CreationOptions, obj: Any, format_type: str) -> str:
        """Format a created object using the appropriate formatters."""
        config = self.get_config(creation_type)
        # Run the appropriate formatter for this creation type and format
        return str(obj)


# Convenience functions for common creation patterns
async def create_character_from_scratch(prompt: str, llm_service=None, **kwargs) -> CharacterCore:
    """Convenience function to create a character from scratch."""
    factory = CreationFactory(llm_service)
    return await factory.create_from_scratch(CreationOptions.CHARACTER, prompt, **kwargs)


async def evolve_character(existing_data: Dict[str, Any], evolution_prompt: str, llm_service=None, **kwargs) -> CharacterCore:
    """
    Convenience function to evolve an existing character.
    
    Preserves existing backstory and uses journal entries for context.
    Evolution should be additive, not replacement.
    """
    factory = CreationFactory(llm_service)
    return await factory.evolve_existing(CreationOptions.CHARACTER, existing_data, evolution_prompt, **kwargs)


async def refine_character(existing_data: Dict[str, Any], refinement_prompt: str, llm_service=None, **kwargs) -> CharacterCore:
    """
    Convenience function for iterative character refinement.
    
    Applies user feedback while maintaining character consistency.
    """
    kwargs['evolution_type'] = 'refine'
    factory = CreationFactory(llm_service)
    return await factory.evolve_existing(CreationOptions.CHARACTER, existing_data, refinement_prompt, **kwargs)


async def level_up_character(existing_data: Dict[str, Any], level_info: Dict[str, Any], llm_service=None, **kwargs) -> CharacterCore:
    """
    Convenience function specifically for leveling up a character.
    
    Uses journal entries and level info to make appropriate advancement choices.
    Preserves character's established personality and story.
    """
    evolution_prompt = f"Level up to level {level_info.get('new_level', 'next')}. "
    if level_info.get('multiclass'):
        evolution_prompt += f"Multiclass into {level_info['multiclass']}. "
    if level_info.get('context'):
        evolution_prompt += level_info['context']
    if level_info.get('story_reason'):
        evolution_prompt += f" Story context: {level_info['story_reason']}"
    
    # Always preserve backstory when leveling up
    kwargs['preserve_backstory'] = True
    kwargs['evolution_type'] = 'level_up'
    kwargs['new_level'] = level_info.get('new_level')
    kwargs['multiclass_option'] = level_info.get('multiclass')
    kwargs['journal_entries'] = level_info.get('journal_entries', [])
    
    factory = CreationFactory(llm_service)
    return await factory.evolve_existing(CreationOptions.CHARACTER, existing_data, evolution_prompt, **kwargs)


async def apply_character_feedback(existing_data: Dict[str, Any], feedback: Dict[str, Any], llm_service=None, **kwargs) -> CharacterCore:
    """
    Convenience function for applying structured user feedback.
    
    Feedback format:
    {
        "change_type": "modify_ability|change_class|add_feat|modify_equipment|change_spells",
        "target": "strength|wizard|Alert|Longsword|Fireball", 
        "new_value": "15|Sorcerer|Magic Initiate|Rapier|Lightning Bolt",
        "reason": "User explanation for change"
    }
    """
    creator = CharacterCreator(llm_service)
    result = await creator.apply_user_feedback(existing_data, feedback)
    if result.success:
        return result.data
    else:
        raise Exception(f"Failed to apply feedback: {result.error}")


async def create_monster_from_scratch(prompt: str, llm_service=None, **kwargs) -> CreatureSheet:
    """Convenience function to create a monster from scratch."""
    factory = CreationFactory(llm_service)
    return await factory.create_from_scratch(CreationOptions.MONSTER, prompt, **kwargs)


async def create_item_from_scratch(item_type: str, prompt: str, llm_service=None, **kwargs) -> ItemSheet:
    """Convenience function to create an item from scratch."""
    factory = CreationFactory(llm_service)
    # Map string to enum
    creation_type = CreationOptions(item_type)
    return await factory.create_from_scratch(creation_type, prompt, **kwargs)
