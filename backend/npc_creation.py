"""
D&D 5e 2024 NPC Creation Module with LLM Integration.
Comprehensive NPC generation for both minor roleplaying NPCs and major combat-ready NPCs.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import shared components to eliminate duplication
from shared_character_generation import (
    CreationConfig, CreationResult, CharacterDataGenerator, 
    CharacterValidator, JournalBasedEvolution, build_character_core, create_specialized_prompt
)

# Import core D&D components
from core_models import AbilityScore, ProficiencyLevel, ASIManager
from character_models import DnDCondition, CharacterCore, CharacterSheet, CharacterState, CharacterStats
from llm_service import create_llm_service, LLMService
from database_models import CustomContent
from ability_management import AdvancedAbilityManager
from generators import BackstoryGenerator, CustomContentGenerator
from custom_content_models import ContentRegistry

logger = logging.getLogger(__name__)

# ============================================================================
# D&D 5E 2024 NPC DEFINITIONS
# ============================================================================

class NPCType(Enum):
    """NPC complexity types."""
    MINOR = "minor"      # Roleplaying only, no stat block needed
    MAJOR = "major"      # Full stat block for combat/abilities

class NPCRole(Enum):
    """2024 role-based NPC categories."""
    CIVILIAN = "civilian"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"
    ARTISAN = "artisan"
    CRIMINAL = "criminal"
    SOLDIER = "soldier"
    SPELLCASTER = "spellcaster"
    LEADER = "leader"
    HEALER = "healer"
    SCOUT = "scout"

class NPCSpecies(Enum):
    """Common NPC species (expandable with LLM-generated custom species)."""
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    DRAGONBORN = "dragonborn"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    TIEFLING = "tiefling"
    CUSTOM = "custom"  # For LLM-generated species

class NPCClass(Enum):
    """Common NPC classes (expandable with LLM-generated custom classes)."""
    FIGHTER = "fighter"
    WIZARD = "wizard"
    ROGUE = "rogue"
    CLERIC = "cleric"
    RANGER = "ranger"
    BARD = "bard"
    PALADIN = "paladin"
    BARBARIAN = "barbarian"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    DRUID = "druid"
    MONK = "monk"
    ARTIFICER = "artificer"
    CUSTOM = "custom"  # For LLM-generated classes

# NPCConfig and NPCResult have been replaced with shared CreationConfig and CreationResult
# from shared_character_generation.py to eliminate code duplication

# ============================================================================
# CONFIGURATION AND RESULT CLASSES
# ============================================================================

# All shared classes (CreationConfig, CreationResult, CharacterValidator, 
# CharacterDataGenerator, JournalBasedEvolution) are imported from shared_character_generation
# to eliminate code duplication. Only NPC-specific classes remain below.

# ============================================================================
# NPC-SPECIFIC CLASSES
# ============================================================================

class MinorNPC:
    """
    D&D 5e 2024 Minor NPC - Roleplaying focused without stat block.
    Used for shopkeepers, background characters, informants, etc.
    """
    
    def __init__(self, name: str):
        # Basic Identity
        self.name = name
        self.species = NPCSpecies.HUMAN
        self.role = NPCRole.CIVILIAN
        self.alignment = "neutral"
        
        # Roleplaying Attributes
        self.appearance = ""
        self.personality = ""
        self.secret = ""
        self.backstory = ""
        self.motivations: List[str] = []
        self.mannerisms: List[str] = []
        
        # Location and Context
        self.location = ""
        self.occupation = ""
        self.relationships: Dict[str, str] = {}
        
        # Simple traits
        self.notable_features: List[str] = []
        self.languages: List[str] = ["Common"]
        
        # Metadata
        self.description = ""
        self.dm_notes = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert minor NPC to dictionary format."""
        return {
            "name": self.name,
            "type": "minor",
            "species": self.species.value,
            "role": self.role.value,
            "alignment": self.alignment,
            "appearance": self.appearance,
            "personality": self.personality,
            "secret": self.secret,
            "backstory": self.backstory,
            "motivations": self.motivations,
            "mannerisms": self.mannerisms,
            "location": self.location,
            "occupation": self.occupation,
            "relationships": self.relationships,
            "notable_features": self.notable_features,
            "languages": self.languages,
            "description": self.description,
            "dm_notes": self.dm_notes
        }


def create_major_npc(description: str, level: int = 1, generate_backstory: bool = True, 
                    include_custom_content: bool = False, add_initial_journal: bool = True, 
                    llm_service: LLMService = None) -> CreationResult:
    """Convenience function to create a major NPC (full stat block) with journal support."""
    creator = NPCCreator(llm_service)
    return creator.create_npc(description, NPCType.MAJOR, NPCRole.CIVILIAN)

class NPCCreator:
    """NPC Creation orchestrator using shared components for D&D 5e 2024 NPCs."""
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        """Initialize NPC creator with shared components."""
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Use shared components
        self.validator = CharacterValidator()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.journal_evolution = JournalBasedEvolution(self.llm_service)
        
        # NPC-specific managers (initialize without character_core for now)
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.content_registry = ContentRegistry()
        self.content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        
        logger.info("NPCCreator initialized with shared components and LLM integration")
    
    async def create_npc(self, prompt: str, npc_type: NPCType = NPCType.MINOR, 
                   npc_role: NPCRole = NPCRole.CIVILIAN) -> CreationResult:
        """
        Create an NPC using shared generation components.
        
        Args:
            prompt: Description of the desired NPC
            npc_type: Type of NPC (MINOR for roleplay, MAJOR for combat)
            npc_role: Role/occupation of the NPC
            
        Returns:
            CreationResult with NPC data
        """
        start_time = time.time()
        
        try:
            logger.info(f"Creating {npc_type.value} {npc_role.value} NPC: {prompt[:50]}...")
            
            # Create NPC-specific prompt for LLM generation
            npc_prompt = self._create_npc_prompt(prompt, npc_type, npc_role)
            
            # Generate unique NPC using LLM
            npc_data = await self._generate_unique_npc_with_llm(npc_prompt, npc_type, npc_role)
            
            # Validate and enhance the generated NPC
            validated_data = self._validate_and_enhance_npc(npc_data, npc_type, npc_role)
            
            # Create successful result
            result = CreationResult()
            result.success = True
            result.data = validated_data
            result.creation_time = time.time() - start_time
            result.warnings = []
            
            logger.info(f"Unique NPC creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"NPC creation failed: {str(e)}")
            result = CreationResult()
            result.success = False
            result.error = f"NPC creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _create_npc_prompt(self, base_prompt: str, npc_type: NPCType, npc_role: NPCRole) -> str:
        """Create NPC-specific prompt for generation."""
        type_guidance = {
            NPCType.MINOR: "Create a roleplay-focused NPC with personality and dialogue, minimal combat stats needed.",
            NPCType.MAJOR: "Create a combat-ready NPC with full stat block, abilities, and tactics."
        }
        
        role_guidance = {
            NPCRole.CIVILIAN: "ordinary townsperson with everyday concerns",
            NPCRole.MERCHANT: "trader with business interests and connections",
            NPCRole.GUARD: "law enforcement with authority and combat training",
            NPCRole.NOBLE: "aristocrat with social influence and resources",
            NPCRole.SCHOLAR: "learned individual with specialized knowledge",
            NPCRole.ARTISAN: "skilled craftsperson with professional expertise",
            NPCRole.CRIMINAL: "lawbreaker with underworld connections",
            NPCRole.SOLDIER: "military professional with combat experience"
        }
        
        enhanced_prompt = f"""
        {base_prompt}
        
        NPC Type: {type_guidance.get(npc_type, "")}
        NPC Role: This character is a {role_guidance.get(npc_role, npc_role.value)}.
        
        Focus on creating a memorable, three-dimensional character appropriate for D&D 5e 2024 rules.
        """
        
        return enhanced_prompt.strip()
    
    def _enhance_npc_data(self, npc_data: Dict[str, Any], npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Add NPC-specific enhancements to generated data."""
        # Add NPC metadata
        npc_data["npc_metadata"] = {
            "type": npc_type.value,
            "role": npc_role.value,
            "is_combat_ready": npc_type == NPCType.MAJOR,
            "created_at": time.time()
        }
        
        # Add role-specific traits
        if npc_role == NPCRole.MERCHANT:
            npc_data.setdefault("equipment", []).append("merchant's scales")
            npc_data.setdefault("proficiencies", []).append("Insight")
        elif npc_role == NPCRole.GUARD:
            npc_data.setdefault("equipment", []).extend(["chain mail", "spear", "light crossbow"])
            npc_data.setdefault("proficiencies", []).extend(["Perception", "Athletics"])
        elif npc_role == NPCRole.SCHOLAR:
            npc_data.setdefault("equipment", []).extend(["books", "ink and quill"])
            npc_data.setdefault("proficiencies", []).extend(["History", "Investigation"])
        
        return npc_data

    async def _generate_unique_npc_with_llm(self, prompt: str, npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Generate a unique NPC using LLM services."""
        if not self.llm_service:
            raise ValueError("LLM service not available for NPC generation")
        
        # Create specialized prompt for NPC generation
        specialized_prompt = f"""
        Generate a unique D&D 5e NPC based on this description: {prompt}
        
        NPC Type: {npc_type.value}
        NPC Role: {npc_role.value}
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "name": "Unique character name",
            "species": "D&D species/race",
            "class": "D&D class (if applicable)",
            "role": "{npc_role.value}",
            "level": 1-20,
            "alignment": "D&D alignment",
            "appearance": "Physical description",
            "personality": "Personality traits and mannerisms",
            "backstory": "Brief background story",
            "motivation": "What drives this character",
            "secret": "Hidden aspect or secret",
            "abilities": {{
                "strength": 8-18,
                "dexterity": 8-18,
                "constitution": 8-18,
                "intelligence": 8-18,
                "wisdom": 8-18,
                "charisma": 8-18
            }},
            "skills": ["skill1", "skill2", "skill3"],
            "equipment": ["item1", "item2", "item3"],
            "special_abilities": ["ability1", "ability2"],
            "challenge_rating": 0.125-30.0,
            "hit_points": 1-500,
            "armor_class": 8-25,
            "languages": ["Common", "other languages"],
            "location": "Where they might be found",
            "relationships": "Important connections",
            "quirks": ["unique trait 1", "unique trait 2"]
        }}
        
        Make this NPC unique and memorable. Focus on {"roleplay elements" if npc_type == NPCType.MINOR else "combat readiness and tactical abilities"}.
        """
        
        # Get LLM response
        response = await self.llm_service.generate_content(specialized_prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                npc_data = json.loads(json_str)
                logger.info(f"Successfully generated unique NPC: {npc_data.get('name', 'Unknown')}")
                return npc_data
            else:
                raise ValueError("Could not find valid JSON in LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to basic NPC structure
            return self._create_fallback_npc(prompt, npc_type, npc_role)
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return self._create_fallback_npc(prompt, npc_type, npc_role)
    
    def _create_fallback_npc(self, prompt: str, npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Create a basic NPC when LLM generation fails."""
        import random
        
        # Basic fallback names by role
        names_by_role = {
            NPCRole.CIVILIAN: ["Aldric", "Mira", "Tomás", "Elara"],
            NPCRole.MERCHANT: ["Goldwin", "Vera", "Marcus", "Lydia"],
            NPCRole.GUARD: ["Gareth", "Thane", "Kira", "Bron"],
            NPCRole.NOBLE: ["Lord Aldwin", "Lady Celeste", "Duke Raven", "Countess Vale"],
            NPCRole.SCHOLAR: ["Sage Oren", "Magister Lila", "Scholar Finn", "Archivest Naia"],
            NPCRole.ARTISAN: ["Smith Jorik", "Weaver Anya", "Mason Craig", "Baker Rosie"],
            NPCRole.CRIMINAL: ["Sly", "Raven", "Quick-finger Tom", "Shadow"],
            NPCRole.SOLDIER: ["Captain Rex", "Sergeant Maya", "Commander Zara", "Lieutenant Vale"]
        }
        
        return {
            "name": random.choice(names_by_role.get(npc_role, ["Generic NPC"])),
            "species": "Human",
            "class": "Commoner" if npc_type == NPCType.MINOR else "Fighter",
            "role": npc_role.value,
            "level": 1 if npc_type == NPCType.MINOR else random.randint(1, 5),
            "alignment": "Neutral",
            "appearance": f"A typical {npc_role.value}",
            "personality": "Straightforward and practical",
            "backstory": f"A {npc_role.value} with local connections",
            "motivation": "Maintaining their position",
            "secret": "Nothing significant",
            "abilities": {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10
            },
            "skills": ["Insight", "Perception"],
            "equipment": ["Simple clothes", "Belt pouch"],
            "special_abilities": [],
            "challenge_rating": 0.0 if npc_type == NPCType.MINOR else 0.25,
            "hit_points": 4 if npc_type == NPCType.MINOR else 11,
            "armor_class": 10,
            "languages": ["Common"],
            "location": "Local area",
            "relationships": "Local community",
            "quirks": ["Speaks quickly when nervous"]
        }
    
    def _validate_and_enhance_npc(self, npc_data: Dict[str, Any], npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Validate and enhance the generated NPC data."""
        # Ensure required fields exist
        required_fields = ["name", "species", "role", "alignment", "abilities"]
        for field in required_fields:
            if field not in npc_data:
                logger.warning(f"Missing required field '{field}' in NPC data")
                npc_data[field] = "Unknown" if field != "abilities" else {
                    "strength": 10, "dexterity": 10, "constitution": 10,
                    "intelligence": 10, "wisdom": 10, "charisma": 10
                }
        
        # Validate ability scores (ensure they're in valid range)
        if "abilities" in npc_data:
            for ability, score in npc_data["abilities"].items():
                if not isinstance(score, int) or score < 3 or score > 20:
                    npc_data["abilities"][ability] = 10
        
        # Add NPC type-specific enhancements
        if npc_type == NPCType.MINOR:
            # Focus on roleplay elements
            npc_data["focus"] = "roleplay"
            npc_data["combat_stats_minimal"] = True
        else:
            # Focus on combat readiness
            npc_data["focus"] = "combat"
            npc_data["combat_ready"] = True
            
            # Ensure combat stats are present
            if "challenge_rating" not in npc_data:
                npc_data["challenge_rating"] = 0.25
            if "hit_points" not in npc_data:
                npc_data["hit_points"] = 11
            if "armor_class" not in npc_data:
                npc_data["armor_class"] = 12
        
        # Add metadata
        npc_data["creation_method"] = "llm_generated"
        npc_data["npc_type"] = npc_type.value
        npc_data["npc_role"] = npc_role.value
        
        return npc_data

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def create_npc_from_prompt(prompt: str, npc_type: NPCType = NPCType.MINOR) -> CreationResult:
    """Utility function for simple NPC creation."""
    creator = NPCCreator()
    return await creator.create_npc(prompt, npc_type)

def quick_npc_creation(concept: str, role: str = "civilian") -> CreationResult:
    """Quick NPC creation utility."""
    creator = NPCCreator()
    npc_role = NPCRole.CIVILIAN
    
    # Map role string to enum
    role_mapping = {
        "merchant": NPCRole.MERCHANT,
        "guard": NPCRole.GUARD,
        "noble": NPCRole.NOBLE,
        "scholar": NPCRole.SCHOLAR,
        "artisan": NPCRole.ARTISAN,
        "criminal": NPCRole.CRIMINAL,
        "soldier": NPCRole.SOLDIER
    }
    
    npc_role = role_mapping.get(role.lower(), NPCRole.CIVILIAN)
    return creator.create_npc(concept, NPCType.MINOR, npc_role)
