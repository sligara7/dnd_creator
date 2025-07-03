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
import json
import re
import logging

from src.core.enums import CreationOptions
from src.models.character_models import CharacterCore
from src.services.creation import CharacterCreator
from src.services.generators import CustomContentGenerator

logger = logging.getLogger(__name__)

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
        """Build mapping of creation types to their required components."""
        return {
            CreationOptions.CHARACTER: CreationConfig(
                models=[CharacterCore],
                generators=[CharacterCreator, CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.MONSTER: CreationConfig(
                models=[],  # Will use dict-based creation for now
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.NPC: CreationConfig(
                models=[],  # Will use dict-based creation for now
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.WEAPON: CreationConfig(
                models=[],
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.ARMOR: CreationConfig(
                models=[],
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.SPELL: CreationConfig(
                models=[],
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
            ),
            CreationOptions.OTHER_ITEM: CreationConfig(
                models=[],
                generators=[CustomContentGenerator],
                validators=[],
                formatters=[],
                schemas={}
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
    
    async def _create_character_from_scratch(self, prompt: str, **kwargs) -> CharacterCore:
        """
        Create a new character from scratch using LLM generation.
        
        This includes generating the character's core stats, equipment (weapons, armor),
        spells (if applicable), and other items as a complete package.
        """
        creator = CharacterCreator(self.llm_service)
        
        # Merge extra_fields into user_preferences for better parameter handling
        user_preferences = kwargs.get('user_preferences', {})
        extra_fields = kwargs.get('extra_fields', {})
        
        # Merge extra_fields into user_preferences (extra_fields takes precedence)
        merged_preferences = {**user_preferences, **extra_fields}
        
        result = await creator.create_character(prompt, merged_preferences)
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
        """Create a new monster from scratch using LLM generation."""
        try:
            challenge_rating = float(kwargs.get('challenge_rating', 1.0))
            creature_type = kwargs.get('creature_type', 'monstrosity')
            
            # Use LLM to generate monster based on prompt
            monster_prompt = f"""Create a D&D 5e monster based on this description: {prompt}

Challenge Rating: {challenge_rating}
Creature Type: {creature_type}

Generate a complete monster stat block in JSON format:
{{
    "name": "Monster Name",
    "type": "{creature_type}",
    "size": "Medium",
    "alignment": "neutral",
    "challenge_rating": {challenge_rating},
    "abilities": {{
        "strength": 14,
        "dexterity": 12,
        "constitution": 13,
        "intelligence": 10,
        "wisdom": 11,
        "charisma": 8
    }},
    "hit_points": 30,
    "armor_class": 14,
    "speed": 30,
    "skills": [],
    "damage_resistances": [],
    "damage_immunities": [],
    "condition_immunities": [],
    "senses": ["darkvision 60 ft"],
    "languages": [],
    "special_abilities": [
        {{
            "name": "Special Ability",
            "description": "Description of special ability"
        }}
    ],
    "actions": [
        {{
            "name": "Attack",
            "description": "Melee attack: +5 to hit, reach 5 ft., one target. Hit: 8 (1d8 + 4) damage."
        }}
    ],
    "description": "A brief description of the monster's appearance and behavior."
}}

Return only valid JSON."""

            # Use the LLM service if available
            if self.llm_service:
                try:
                    print(f"DEBUG: Using LLM service to generate monster: {type(self.llm_service)}")
                    response = await self.llm_service.generate_content(monster_prompt)
                    print(f"DEBUG: LLM response received: {response[:200]}...")
                    
                    # Try to parse the JSON response
                    import json
                    try:
                        monster_data = json.loads(response)
                        print(f"DEBUG: Successfully parsed JSON from LLM response")
                    except json.JSONDecodeError:
                        print(f"DEBUG: Failed to parse JSON directly, trying regex extraction")
                        # Try to extract JSON from response
                        import re
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            monster_data = json.loads(json_match.group())
                            print(f"DEBUG: Successfully extracted JSON from LLM response")
                        else:
                            print(f"DEBUG: Could not extract JSON from LLM response, using fallback")
                            raise ValueError("Could not parse JSON from LLM response")
                    
                    # Validate and enhance the monster using the existing validation system
                    from src.services.creation_validation import validate_and_enhance_creature
                    enhanced_monster = validate_and_enhance_creature(monster_data, challenge_rating)
                    print(f"DEBUG: Monster creation via LLM successful")
                    
                    return enhanced_monster
                    
                except Exception as llm_error:
                    print(f"DEBUG: LLM generation failed with error: {llm_error}")
                    # Fall through to basic template
                    return self._create_basic_monster_template(prompt, challenge_rating, creature_type)
            
            else:
                print(f"DEBUG: No LLM service available, using basic template")
                # Fallback: create a basic monster template
                return self._create_basic_monster_template(prompt, challenge_rating, creature_type)
                return self._create_basic_monster_template(prompt, challenge_rating, creature_type)
                
        except Exception as e:
            # Return a basic template if generation fails
            return self._create_basic_monster_template(prompt, kwargs.get('challenge_rating', 1.0), kwargs.get('creature_type', 'monstrosity'))
    
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
        """Create a new NPC from scratch using LLM generation and NPC generators."""
        try:
            npc_role = kwargs.get('npc_type', 'commoner')
            challenge_rating = float(kwargs.get('challenge_rating', 0.5))
            
            # Use LLM to generate NPC based on prompt
            npc_prompt = f"""Create a D&D 5e NPC based on this description: {prompt}

Role: {npc_role}
Challenge Rating: {challenge_rating}

Generate a complete NPC in JSON format:
{{
    "name": "NPC Name",
    "species": "human",
    "role": "{npc_role}",
    "alignment": "neutral",
    "challenge_rating": {challenge_rating},
    "level": {max(1, int(challenge_rating * 2))},
    "abilities": {{
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }},
    "hit_points": {max(1, int(challenge_rating * 8 + 4))},
    "armor_class": {max(10, int(10 + challenge_rating))},
    "speed": 30,
    "skills": [],
    "languages": ["Common"],
    "equipment": {{
        "weapons": [],
        "armor": [],
        "items": []
    }},
    "spells": [],
    "personality": {{
        "trait": "A defining personality trait",
        "ideal": "What drives this NPC",
        "bond": "Important connection or loyalty",
        "flaw": "A character weakness"
    }},
    "background": "Brief background and role in the world",
    "description": "Physical appearance and mannerisms",
    "profession": "What they do for a living",
    "location": "Where they can typically be found"
}}

Return only valid JSON."""

            # Use the LLM service if available
            if self.llm_service:
                try:
                    print(f"DEBUG: Using LLM service to generate NPC: {type(self.llm_service)}")
                    response = await self.llm_service.generate_content(npc_prompt)
                    print(f"DEBUG: LLM response received: {response[:200]}...")
                    
                    # Try to parse the JSON response
                    import json
                    try:
                        npc_data = json.loads(response)
                        print(f"DEBUG: Successfully parsed JSON from LLM response")
                    except json.JSONDecodeError:
                        print(f"DEBUG: Failed to parse JSON directly, trying regex extraction")
                        # Try to extract JSON from response
                        import re
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            npc_data = json.loads(json_match.group())
                            print(f"DEBUG: Successfully extracted JSON from LLM response")
                        else:
                            print(f"DEBUG: Could not extract JSON from LLM response, using fallback")
                            raise ValueError("Could not parse JSON from LLM response")
                    
                    # Validate and enhance the NPC using the existing validation system
                    from src.core.enums import NPCType, NPCRole
                    from src.services.creation_validation import validate_and_enhance_npc
                    
                    # Map role to enums (with fallbacks)
                    npc_type_enum = NPCType.MAJOR  # Default to major for generated NPCs
                    npc_role_enum = getattr(NPCRole, npc_role.upper(), NPCRole.CIVILIAN)
                    
                    enhanced_npc = validate_and_enhance_npc(npc_data, npc_type_enum, npc_role_enum)
                    print(f"DEBUG: NPC creation via LLM successful")
                    
                    return enhanced_npc
                    
                except Exception as llm_error:
                    print(f"DEBUG: LLM generation failed with error: {llm_error}")
                    # Fall through to basic template
                    return self._create_basic_npc_template(prompt, challenge_rating, npc_role)
            
            else:
                print(f"DEBUG: No LLM service available, using basic template")
                # Fallback: create a basic NPC template
                return self._create_basic_npc_template(prompt, challenge_rating, npc_role)
                
        except Exception as e:
            # Return a basic template if generation fails
            return self._create_basic_npc_template(prompt, kwargs.get('challenge_rating', 0.5), kwargs.get('npc_type', 'commoner'))
    
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
    
    def _create_basic_monster_template(self, prompt: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Create a basic monster template when LLM generation fails."""
        from src.services.creation_validation import validate_and_enhance_creature
        
        # Extract some keywords from the prompt for basic customization
        prompt_lower = prompt.lower()
        
        # Determine size based on prompt keywords
        size = "Medium"
        if any(word in prompt_lower for word in ["tiny", "small"]):
            size = "Small"
        elif any(word in prompt_lower for word in ["large", "giant", "huge"]):
            size = "Large"
        elif any(word in prompt_lower for word in ["gargantuan", "colossal"]):
            size = "Gargantuan"
        
        # Basic stat allocation based on CR
        base_stat = max(10, int(10 + challenge_rating * 2))
        
        basic_monster = {
            "name": f"Generated {creature_type.title()}",
            "type": creature_type,
            "size": size,
            "alignment": "neutral",
            "challenge_rating": challenge_rating,
            "abilities": {
                "strength": base_stat + 2,
                "dexterity": base_stat,
                "constitution": base_stat + 1,
                "intelligence": max(3, base_stat - 2),
                "wisdom": base_stat,
                "charisma": max(3, base_stat - 2)
            },
            "hit_points": max(1, int(challenge_rating * 15 + 10)),
            "armor_class": max(10, int(10 + challenge_rating)),
            "speed": 30,
            "skills": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["passive Perception 10"],
            "languages": [],
            "special_abilities": [],
            "actions": [
                {
                    "name": "Basic Attack",
                    "description": f"Melee attack: +{max(1, int(2 + challenge_rating))} to hit, reach 5 ft., one target. Hit: {max(1, int(4 + challenge_rating * 2))} damage."
                }
            ],
            "description": f"A basic {creature_type} created from the concept: {prompt[:100]}..."
        }
        
        # Use creation_validation to enhance and balance the monster
        enhanced_monster = validate_and_enhance_creature(basic_monster, challenge_rating)
        return enhanced_monster

    def _create_basic_npc_template(self, prompt: str, challenge_rating: float, npc_role: str) -> Dict[str, Any]:
        """Create a basic NPC template when LLM generation fails."""
        from src.core.enums import NPCType, NPCRole
        from src.services.creation_validation import validate_and_enhance_npc
        
        # Extract some keywords from the prompt for basic customization
        prompt_lower = prompt.lower()
        
        # Determine species based on prompt keywords
        species = "human"
        if any(word in prompt_lower for word in ["elf", "elven"]):
            species = "elf"
        elif any(word in prompt_lower for word in ["dwarf", "dwarven"]):
            species = "dwarf"
        elif any(word in prompt_lower for word in ["halfling", "small"]):
            species = "halfling"
        elif any(word in prompt_lower for word in ["orc", "orcish"]):
            species = "orc"
        
        # Basic stat allocation based on CR and role
        base_stat = max(8, int(10 + challenge_rating))
        level = max(1, int(challenge_rating * 2))
        
        # Role-based stat preferences
        if npc_role in ["guard", "soldier", "warrior"]:
            strength_bonus = 2
            dexterity_bonus = 1
            constitution_bonus = 1
        elif npc_role in ["scout", "rogue", "archer"]:
            strength_bonus = 0
            dexterity_bonus = 2
            constitution_bonus = 0
        elif npc_role in ["mage", "wizard", "scholar"]:
            strength_bonus = -1
            dexterity_bonus = 0
            constitution_bonus = 0
        else:  # commoner, civilian, etc.
            strength_bonus = 0
            dexterity_bonus = 0
            constitution_bonus = 0
        
        basic_npc = {
            "name": f"Generated {npc_role.title()}",
            "species": species,
            "role": npc_role,
            "alignment": "neutral",
            "challenge_rating": challenge_rating,
            "level": level,
            "abilities": {
                "strength": max(6, base_stat + strength_bonus),
                "dexterity": max(6, base_stat + dexterity_bonus),
                "constitution": max(6, base_stat + constitution_bonus),
                "intelligence": max(6, base_stat if npc_role in ["mage", "wizard", "scholar"] else base_stat - 1),
                "wisdom": max(6, base_stat if npc_role in ["cleric", "druid"] else base_stat - 1),
                "charisma": max(6, base_stat if npc_role in ["bard", "sorcerer"] else base_stat - 1)
            },
            "hit_points": max(1, int(challenge_rating * 8 + 4 + level * 2)),
            "armor_class": max(10, int(10 + challenge_rating)),
            "speed": 30,
            "skills": [],
            "languages": ["Common"],
            "equipment": {
                "weapons": [],
                "armor": [],
                "items": []
            },
            "spells": [],
            "personality": {
                "trait": f"A {npc_role} with a strong sense of duty",
                "ideal": "Serving their community",
                "bond": "Loyal to their station",
                "flaw": "Can be overly cautious"
            },
            "background": f"A {npc_role} created from the concept: {prompt[:100]}...",
            "description": f"A typical {species} {npc_role} with a practical demeanor",
            "profession": npc_role,
            "location": "In their place of work or community"
        }
        
        # Map role to enums (with fallbacks)
        npc_type_enum = NPCType.MAJOR  # Default to major for generated NPCs
        npc_role_enum = getattr(NPCRole, npc_role.upper(), NPCRole.CIVILIAN)
        
        # Use creation_validation to enhance and balance the NPC
        enhanced_npc = validate_and_enhance_npc(basic_npc, npc_type_enum, npc_role_enum)
        return enhanced_npc


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
