"""
D&D 5e 2024 Creature Creation Module with LLM Integration.
Comprehensive creature generation following D&D 5e 2024 stat block format.
Uses shared components to eliminate code duplication.
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
    CharacterValidator, create_specialized_prompt
)

# Import core D&D components
from core_models import AbilityScore, ProficiencyLevel
from character_models import DnDCondition
from llm_service import create_llm_service, LLMService
from database_models import CustomContent

logger = logging.getLogger(__name__)

# ============================================================================
# D&D 5E 2024 CREATURE DEFINITIONS
# ============================================================================

class CreatureType(Enum):
    """D&D 5e creature types."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class CreatureSize(Enum):
    """D&D 5e creature sizes."""
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"

class CreatureAlignment(Enum):
    """D&D 5e alignments."""
    LAWFUL_GOOD = "lawful good"
    NEUTRAL_GOOD = "neutral good"
    CHAOTIC_GOOD = "chaotic good"
    LAWFUL_NEUTRAL = "lawful neutral"
    TRUE_NEUTRAL = "true neutral"
    CHAOTIC_NEUTRAL = "chaotic neutral"
    LAWFUL_EVIL = "lawful evil"
    NEUTRAL_EVIL = "neutral evil"
    CHAOTIC_EVIL = "chaotic evil"
    UNALIGNED = "unaligned"

# ============================================================================
# CREATURE CORE CLASS
# ============================================================================

class CreatureCore:
    """
    D&D 5e 2024 Creature stat block implementation.
    Contains all attributes required for a complete creature definition.
    """
    
    def __init__(self, name: str):
        # Basic Information
        self.name = name
        self.size = CreatureSize.MEDIUM
        self.creature_type = CreatureType.HUMANOID
        self.alignment = CreatureAlignment.TRUE_NEUTRAL
        
        # Core Stats
        self.armor_class = 10
        self.hit_points = 10
        self.hit_dice = "2d8+2"
        self.speed = {"walk": 30}
        
        # Ability Scores
        self.strength = AbilityScore(10)
        self.dexterity = AbilityScore(10)
        self.constitution = AbilityScore(10)
        self.intelligence = AbilityScore(10)
        self.wisdom = AbilityScore(10)
        self.charisma = AbilityScore(10)
        
        # Combat Stats
        self.challenge_rating = 0.0
        self.proficiency_bonus = 2
        
        # Skills and Proficiencies
        self.saving_throws = {}
        self.skills = {}
        self.damage_vulnerabilities = []
        self.damage_resistances = []
        self.damage_immunities = []
        self.condition_immunities = []
        self.senses = {"passive_perception": 10}
        self.languages = ["Common"]
        
        # Abilities and Actions
        self.special_abilities = []
        self.actions = []
        self.bonus_actions = []
        self.reactions = []
        self.legendary_actions = []
        
        # Lore and Flavor
        self.description = ""
        self.tactics = ""
        self.habitat = ""
        self.treasure = ""

# ============================================================================
# CREATURE CREATOR CLASS
# ============================================================================

class CreatureCreator:
    """
    D&D 5e 2024 Creature Creation Service with LLM Integration.
    Generates complete stat blocks following D&D 5e 2024 format.
    Uses shared components to eliminate code duplication.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, 
                 config: Optional[CreationConfig] = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize shared components
        self.validator = CharacterValidator()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        
        logger.info("CreatureCreator initialized with shared components")
    
    def create_creature(self, description: str, challenge_rating: float = 1.0) -> CreationResult:
        """Create a complete D&D 5e 2024 creature from description."""
        start_time = time.time()
        
        try:
            logger.info(f"Creating creature: {description[:50]}... (CR {challenge_rating})")
            
            # Create creature-specific prompt
            creature_prompt = f"""
            Create a D&D 5e 2024 creature: {description}
            Challenge Rating: {challenge_rating}
            
            Include complete stat block with appropriate abilities for the CR.
            Follow D&D 5e 2024 stat block format.
            """
            
            # Use shared data generator
            creature_preferences = {
                "content_type": "creature",
                "challenge_rating": challenge_rating,
                "focus": "stat_block"
            }
            
            result = self.data_generator.generate_character_data(creature_prompt, creature_preferences)
            
            if result.success:
                # Build creature from generated data
                creature_core = self._build_creature_from_data(result.data, challenge_rating)
                
                # Update result with creature data
                result.data = {
                    "creature_core": creature_core,
                    "raw_data": result.data
                }
                
                result.creation_time = time.time() - start_time
                logger.info(f"Creature creation completed in {result.creation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Creature creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Creature creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _build_creature_from_data(self, creature_data: Dict[str, Any], 
                                 challenge_rating: float) -> CreatureCore:
        """Build CreatureCore from generated data."""
        name = creature_data.get("name", "Unknown Creature")
        creature = CreatureCore(name)
        
        # Set basic properties
        creature.challenge_rating = challenge_rating
        creature.description = creature_data.get("description", "")
        
        # Set ability scores if provided
        if "ability_scores" in creature_data:
            abilities = creature_data["ability_scores"]
            creature.strength = AbilityScore(abilities.get("strength", 10))
            creature.dexterity = AbilityScore(abilities.get("dexterity", 10))
            creature.constitution = AbilityScore(abilities.get("constitution", 10))
            creature.intelligence = AbilityScore(abilities.get("intelligence", 10))
            creature.wisdom = AbilityScore(abilities.get("wisdom", 10))
            creature.charisma = AbilityScore(abilities.get("charisma", 10))
        
        # Set combat stats
        creature.armor_class = creature_data.get("armor_class", 10)
        creature.hit_points = creature_data.get("hit_points", 10)
        creature.hit_dice = creature_data.get("hit_dice", "2d8+2")
        creature.speed = creature_data.get("speed", {"walk": 30})
        
        return creature

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_creature_from_prompt(prompt: str, challenge_rating: float = 1.0) -> CreationResult:
    """Utility function for simple creature creation."""
    creator = CreatureCreator()
    return creator.create_creature(prompt, challenge_rating)
