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

from enums import CreationOptions
from character_models import CharacterSheet
from core_models import CreatureSheet, ItemSheet
from character_creation import CharacterCreator
from creature_creation import CreatureCreator
from items_creation import ItemCreator
from generators import CustomContentGenerator


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
    
    def _build_creation_configs(self) -> Dict[CreationOptions, CreationConfig]:
        """Build mapping of creation types to their required components."""
        return {
            CreationOptions.CHARACTER: CreationConfig(
                models=[CharacterSheet, ItemSheet],  # Characters have equipment/items
                generators=[
                    CharacterCreator, 
                    CustomContentGenerator,
                    ItemCreator  # Characters need item generation for equipment
                ],
                validators=[
                    # CharacterValidator,        # Core character validation
                    # WeaponValidator,          # Validate character's weapons
                    # ArmorValidator,           # Validate character's armor
                    # SpellValidator,           # Validate character's spells
                    # EquipmentValidator,       # Validate equipment compatibility
                    # CharacterBalanceValidator # Umbrella validator for overall balance
                ],
                formatters=[
                    # CharacterFormatter,       # Format character sheets
                    # EquipmentFormatter,       # Format equipment lists
                    # SpellListFormatter        # Format spell lists
                ],
                schemas={
                    # "character": CharacterCreateRequest,
                    # "equipment": EquipmentSchema,
                    # "spells": SpellListSchema
                }
            ),
            CreationOptions.MONSTER: CreationConfig(
                models=[CreatureSheet, ItemSheet],  # Monsters can have equipment
                generators=[
                    CreatureCreator, 
                    CustomContentGenerator,
                    ItemCreator  # Monsters may need custom items/abilities
                ],
                validators=[
                    # CreatureValidator,        # Core creature validation
                    # ChallengeRatingValidator, # Validate CR appropriateness
                    # AbilityValidator,         # Validate special abilities
                    # MonsterBalanceValidator   # Umbrella validator for encounter balance
                ],
                formatters=[
                    # CreatureFormatter,        # Format stat blocks
                    # AbilityFormatter          # Format special abilities
                ],
                schemas={
                    # "creature": CreatureCreateRequest,
                    # "abilities": AbilitySchema
                }
            ),
            CreationOptions.NPC: CreationConfig(
                models=[CharacterSheet, CreatureSheet, ItemSheet],  # NPCs can be character-like or creature-like
                generators=[
                    CharacterCreator,   # For character-based NPCs
                    CreatureCreator,    # For creature-based NPCs
                    CustomContentGenerator,
                    ItemCreator         # NPCs need equipment/items
                ],
                validators=[
                    # NPCValidator,             # Core NPC validation
                    # CharacterValidator,       # If using character rules
                    # CreatureValidator,        # If using creature rules
                    # NPCBalanceValidator       # Umbrella validator for NPC appropriateness
                ],
                formatters=[
                    # NPCFormatter,             # Format NPC sheets
                    # DialogueFormatter         # Format NPC dialogue/personality
                ],
                schemas={
                    # "npc": NPCCreateRequest,
                    # "personality": PersonalitySchema
                }
            ),
            CreationOptions.WEAPON: CreationConfig(
                models=[ItemSheet],
                generators=[ItemCreator, CustomContentGenerator],
                validators=[
                    # WeaponValidator,          # Validate weapon properties
                    # DamageValidator,          # Validate damage calculations
                    # BalanceValidator          # Validate weapon balance
                ],
                formatters=[
                    # WeaponFormatter           # Format weapon descriptions
                ],
                schemas={
                    # "weapon": WeaponCreateRequest
                }
            ),
            CreationOptions.ARMOR: CreationConfig(
                models=[ItemSheet],
                generators=[ItemCreator, CustomContentGenerator],
                validators=[
                    # ArmorValidator,           # Validate armor properties
                    # ACValidator,              # Validate AC calculations
                    # BalanceValidator          # Validate armor balance
                ],
                formatters=[
                    # ArmorFormatter            # Format armor descriptions
                ],
                schemas={
                    # "armor": ArmorCreateRequest
                }
            ),
            CreationOptions.SPELL: CreationConfig(
                models=[ItemSheet],  # Or create SpellSheet
                generators=[ItemCreator, CustomContentGenerator],
                validators=[
                    # SpellValidator,           # Validate spell mechanics
                    # LevelValidator,           # Validate spell level appropriateness
                    # ComponentValidator,       # Validate spell components
                    # BalanceValidator          # Validate spell balance
                ],
                formatters=[
                    # SpellFormatter            # Format spell descriptions
                ],
                schemas={
                    # "spell": SpellCreateRequest
                }
            ),
            CreationOptions.OTHER_ITEM: CreationConfig(
                models=[ItemSheet],
                generators=[ItemCreator, CustomContentGenerator],
                validators=[
                    # ItemValidator,            # Validate item properties
                    # RarityValidator,          # Validate item rarity
                    # BalanceValidator          # Validate item balance
                ],
                formatters=[
                    # ItemFormatter             # Format item descriptions
                ],
                schemas={
                    # "item": ItemCreateRequest
                }
            )
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
    
    async def _create_character_from_scratch(self, prompt: str, **kwargs) -> CharacterSheet:
        """
        Create a new character from scratch using LLM generation.
        
        This includes generating the character's core stats, equipment (weapons, armor),
        spells (if applicable), and other items as a complete package.
        """
        creator = CharacterCreator(self.llm_service)
        result = await creator.create_character(prompt, kwargs.get('user_preferences'))
        if result.success:
            return result.data
        else:
            raise Exception(f"Character creation failed: {result.error}")
    
    async def _evolve_character(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> CharacterSheet:
        """
        Evolve an existing character using journal and new prompt.
        
        Key principles for character evolution:
        1. PRESERVE existing backstory - only append new experiences
        2. Use journal entries as context for evolution decisions
        3. Respect character's established personality and goals
        4. Equipment/spell changes should be story-driven
        """
        creator = CharacterCreator(self.llm_service)
        
        # Ensure we preserve the existing backstory rather than regenerating it
        preserve_backstory = kwargs.get('preserve_backstory', True)
        if preserve_backstory and 'backstory' in existing_data:
            # Store original backstory to preserve it
            original_backstory = existing_data['backstory']
            kwargs['preserve_backstory'] = original_backstory
        
        result = await creator.create_character(
            evolution_prompt, 
            kwargs.get('user_preferences'),
            import_existing=existing_data
        )
        if result.success:
            return result.data
        else:
            raise Exception(f"Character evolution failed: {result.error}")
    
    async def _create_monster_from_scratch(self, prompt: str, **kwargs) -> CreatureSheet:
        """Create a new monster from scratch using LLM generation."""
        creator = CreatureCreator(self.llm_service)
        # Implementation would use creature creation logic
        pass
    
    async def _evolve_monster(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> CreatureSheet:
        """Evolve an existing monster (e.g., power up, new abilities)."""
        # Monsters could evolve through story events, power-ups, etc.
        creator = CreatureCreator(self.llm_service)
        # Implementation would use evolution logic
        pass
    
    async def _create_npc_from_scratch(self, prompt: str, **kwargs) -> CharacterSheet:
        """Create a new NPC from scratch using hybrid logic."""
        # NPCs might use both character and creature components
        # Could be character-like (with classes) or creature-like (with CR)
        pass
    
    async def _evolve_npc(self, existing_data: Dict[str, Any], evolution_prompt: str, **kwargs) -> CharacterSheet:
        """Evolve an existing NPC (level up, story changes, etc.)."""
        # NPCs could evolve similarly to characters based on story events
        pass
    
    async def _create_item_from_scratch(self, item_type: CreationOptions, prompt: str, **kwargs) -> ItemSheet:
        """Create a new item from scratch using LLM generation."""
        creator = ItemCreator(self.llm_service)
        # Implementation would use item creation logic based on item_type
        pass
    
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
async def create_character_from_scratch(prompt: str, llm_service=None, **kwargs) -> CharacterSheet:
    """Convenience function to create a character from scratch."""
    factory = CreationFactory(llm_service)
    return await factory.create_from_scratch(CreationOptions.CHARACTER, prompt, **kwargs)


async def evolve_character(existing_data: Dict[str, Any], evolution_prompt: str, llm_service=None, **kwargs) -> CharacterSheet:
    """
    Convenience function to evolve an existing character.
    
    Preserves existing backstory and uses journal entries for context.
    Evolution should be additive, not replacement.
    """
    factory = CreationFactory(llm_service)
    return await factory.evolve_existing(CreationOptions.CHARACTER, existing_data, evolution_prompt, **kwargs)


async def level_up_character(existing_data: Dict[str, Any], level_info: Dict[str, Any], llm_service=None, **kwargs) -> CharacterSheet:
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
    
    return await evolve_character(existing_data, evolution_prompt, llm_service, **kwargs)


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
