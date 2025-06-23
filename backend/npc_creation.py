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
from llm_service_new import create_llm_service, LLMService
from database_models import CustomContent
from ability_management import AdvancedAbilityManager
from generators import BackstoryGenerator, CustomContentGenerator
from custom_content_models import ContentRegistry
from backend.generators import FeatManager  # Adjust path if needed
from backend.character_models import CharacterLevelManager  # Adjust path if needed

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

@dataclass
class NPCConfig:
    """Configuration for NPC creation process."""
    base_timeout: int = 30
    max_retries: int = 3
    include_backstory: bool = True
    include_secrets: bool = True
    include_gear: bool = True
    include_tactics: bool = True
    auto_determine_type: bool = True  # Let LLM decide minor vs major
    use_llm_generation: bool = True

@dataclass
class NPCResult:
    """Result container for NPC creation operations."""
    
    def __init__(self, success: bool = False, npc_data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.npc_data = npc_data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
        self.llm_generation_used: bool = False
        self.npc_type: NPCType = NPCType.MINOR
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)

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
        
        # NPC-specific managers
        self.ability_manager = AdvancedAbilityManager()
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.content_registry = ContentRegistry()
        
        logger.info("NPCCreator initialized with shared components")
    
    def create_npc(self, prompt: str, npc_type: NPCType = NPCType.MINOR, 
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
            
            # Create NPC-specific prompt
            npc_prompt = self._create_npc_prompt(prompt, npc_type, npc_role)
            
            # Use shared data generator with NPC preferences
            npc_preferences = {
                "npc_type": npc_type.value,
                "npc_role": npc_role.value,
                "focus": "roleplay" if npc_type == NPCType.MINOR else "combat_ready"
            }
            
            result = self.data_generator.generate_character_data(npc_prompt, npc_preferences)
            
            if result.success:
                # Add NPC-specific enhancements
                result.data = self._enhance_npc_data(result.data, npc_type, npc_role)
                result.creation_time = time.time() - start_time
                logger.info(f"NPC creation completed in {result.creation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"NPC creation failed: {str(e)}")
            result = CreationResult()
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

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_npc_from_prompt(prompt: str, npc_type: NPCType = NPCType.MINOR) -> CreationResult:
    """Utility function for simple NPC creation."""
    creator = NPCCreator()
    return creator.create_npc(prompt, npc_type)

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
