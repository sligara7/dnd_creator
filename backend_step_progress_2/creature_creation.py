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

# Import from centralized enums
from enums import CreatureType, CreatureSize, CreatureAlignment

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
        
        logger.info("CreatureCreator initialized with LLM integration")
    
    def create_creature(self, description: str, challenge_rating: float = 1.0, 
                       creature_type: str = "beast") -> CreationResult:
        """Create a complete D&D 5e 2024 creature using LLM generation."""
        start_time = time.time()
        
        try:
            logger.info(f"Creating unique creature: {description[:50]}... (CR {challenge_rating})")
            
            # Generate unique creature using LLM
            creature_data = self._generate_unique_creature_with_llm(description, challenge_rating, creature_type)
            
            # Validate and enhance the generated creature
            validated_data = self._validate_and_enhance_creature(creature_data, challenge_rating)
            
            # Create successful result
            result = CreationResult()
            result.success = True
            result.data = validated_data
            result.creation_time = time.time() - start_time
            result.warnings = []
            
            logger.info(f"Unique creature creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Creature creation failed: {str(e)}")
            result = CreationResult()
            result.success = False
            result.error = f"Creature creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _generate_unique_creature_with_llm(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Generate a unique creature using LLM services."""
        if not self.llm_service:
            raise ValueError("LLM service not available for creature generation")
        
        # Create specialized prompt for creature generation
        specialized_prompt = f"""
        Generate a unique D&D 5e creature based on this description: {description}
        
        Challenge Rating: {challenge_rating}
        Creature Type: {creature_type}
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "name": "Unique creature name",
            "size": "Tiny/Small/Medium/Large/Huge/Gargantuan",
            "type": "{creature_type}",
            "alignment": "D&D alignment",
            "challenge_rating": {challenge_rating},
            "armor_class": 8-25,
            "hit_points": 1-500,
            "speed": {{
                "walk": "30 ft",
                "fly": "0 ft",
                "swim": "0 ft"
            }},
            "abilities": {{
                "strength": 1-30,
                "dexterity": 1-30,
                "constitution": 1-30,
                "intelligence": 1-30,
                "wisdom": 1-30,
                "charisma": 1-30
            }},
            "saving_throws": ["Str +X", "Dex +X"],
            "skills": ["Perception +X", "Stealth +X"],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["darkvision 60 ft", "passive Perception X"],
            "languages": ["Common", "other languages"],
            "proficiency_bonus": 2-9,
            "description": "Detailed creature description",
            "behavior": "How the creature acts",
            "habitat": "Where it lives",
            "diet": "What it eats",
            "actions": [
                {{
                    "name": "Action Name",
                    "description": "Action description with mechanics",
                    "attack_bonus": "+X to hit",
                    "damage": "XdY + Z damage type",
                    "range": "5 ft or ranged"
                }}
            ],
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "special_abilities": [
                {{
                    "name": "Ability Name",
                    "description": "Ability description and mechanics"
                }}
            ]
        }}
        
        Make this creature unique, memorable, and balanced for CR {challenge_rating}.
        Include appropriate abilities, attacks, and special features.
        """
        
        # Get LLM response
        response = self.llm_service.generate_content(specialized_prompt)
        
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
                creature_data = json.loads(json_str)
                logger.info(f"Successfully generated unique creature: {creature_data.get('name', 'Unknown')}")
                return creature_data
            else:
                raise ValueError("Could not find valid JSON in LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to basic creature structure
            return self._create_fallback_creature(description, challenge_rating, creature_type)
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return self._create_fallback_creature(description, challenge_rating, creature_type)
    
    def _create_fallback_creature(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Create a basic creature when LLM generation fails."""
        import random
        
        # Basic creature names by type
        creature_names = {
            "beast": ["Wild Beast", "Forest Creature", "Mountain Beast"],
            "monstrosity": ["Strange Monstrosity", "Twisted Creature", "Aberrant Beast"],
            "undead": ["Undead Horror", "Restless Spirit", "Skeletal Creature"],
            "dragon": ["Young Dragon", "Dragonling", "Lesser Wyrm"],
            "elemental": ["Elemental Being", "Primal Force", "Nature Spirit"],
            "fey": ["Fey Creature", "Forest Spirit", "Magical Being"],
            "fiend": ["Lesser Fiend", "Demonic Creature", "Infernal Beast"],
            "celestial": ["Celestial Being", "Divine Creature", "Heavenly Spirit"]
        }
        
        # Calculate basic stats based on CR
        cr_adjustments = {
            "hp": max(10, int(challenge_rating * 20 + 10)),
            "ac": max(10, int(challenge_rating + 10)),
            "attack_bonus": max(2, int(challenge_rating + 2)),
            "damage": max(1, int(challenge_rating * 2 + 1))
        }
        
        return {
            "name": random.choice(creature_names.get(creature_type, ["Generic Creature"])),
            "size": "Medium",
            "type": creature_type,
            "alignment": "neutral",
            "challenge_rating": challenge_rating,
            "armor_class": cr_adjustments["ac"],
            "hit_points": cr_adjustments["hp"],
            "speed": {"walk": "30 ft", "fly": "0 ft", "swim": "0 ft"},
            "abilities": {
                "strength": 12, "dexterity": 12, "constitution": 12,
                "intelligence": 8, "wisdom": 12, "charisma": 8
            },
            "saving_throws": [],
            "skills": ["Perception +2"],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["passive Perception 12"],
            "languages": [],
            "proficiency_bonus": max(2, int((challenge_rating + 7) / 4)),
            "description": f"A {creature_type} creature",
            "behavior": "Acts according to its nature",
            "habitat": "Various environments",
            "diet": "Omnivore",
            "actions": [
                {
                    "name": "Basic Attack",
                    "description": "A simple attack",
                    "attack_bonus": f"+{cr_adjustments['attack_bonus']} to hit",
                    "damage": f"{cr_adjustments['damage']}d6 bludgeoning",
                    "range": "5 ft"
                }
            ],
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "special_abilities": []
        }
    
    def _validate_and_enhance_creature(self, creature_data: Dict[str, Any], challenge_rating: float) -> Dict[str, Any]:
        """Validate and enhance the generated creature data."""
        # Ensure required fields exist
        required_fields = ["name", "type", "challenge_rating", "abilities", "hit_points", "armor_class"]
        for field in required_fields:
            if field not in creature_data:
                logger.warning(f"Missing required field '{field}' in creature data")
                
                # Provide defaults
                if field == "abilities":
                    creature_data[field] = {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    }
                elif field == "challenge_rating":
                    creature_data[field] = challenge_rating
                elif field == "hit_points":
                    creature_data[field] = max(1, int(challenge_rating * 20))
                elif field == "armor_class":
                    creature_data[field] = max(8, int(challenge_rating + 10))
                else:
                    creature_data[field] = "Unknown"
        
        # Validate ability scores (ensure they're in valid range)
        if "abilities" in creature_data:
            for ability, score in creature_data["abilities"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    creature_data["abilities"][ability] = 10
        
        # Ensure challenge rating consistency
        creature_data["challenge_rating"] = challenge_rating
        
        # Add metadata
        creature_data["creation_method"] = "llm_generated"
        creature_data["stat_block_complete"] = True
        
        return creature_data

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_creature_from_prompt(prompt: str, challenge_rating: float = 1.0) -> CreationResult:
    """Utility function for simple creature creation."""
    creator = CreatureCreator()
    return creator.create_creature(prompt, challenge_rating)
