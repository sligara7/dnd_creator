"""
Shared Character Generation Components

This module contains all the shared functionality used across character_creation.py,
npc_creation.py, creature_creation.py, and items_creation.py to eliminate code duplication.

Core Components:
- CreationConfig and CreationResult classes
- CharacterValidator for validation logic
- CharacterDataGenerator for LLM-based generation
- JournalBasedEvolution for character evolution
- Shared utility functions

All other modules should import from this module instead of duplicating code.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet, CharacterStats
from core_models import AbilityScore, ASIManager, MagicItemManager, CharacterLevelManager, ProficiencyLevel
from custom_content_models import ContentRegistry, FeatManager
from ability_management import AdvancedAbilityManager
from llm_service import create_llm_service, LLMService
from generators import BackstoryGenerator, CustomContentGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# SHARED CONFIGURATION AND RESULT CLASSES
# ============================================================================

@dataclass
class CreationConfig:
    """Configuration for character creation process."""
    base_timeout: int = 20
    backstory_timeout: int = 15
    custom_content_timeout: int = 30
    max_retries: int = 2
    enable_progress_feedback: bool = True
    auto_save: bool = False

class CreationResult:
    """Result container for character creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.data)

# ============================================================================
# SHARED CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Handles validation of character data."""
    
    @staticmethod
    def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
        """Validate basic character data structure."""
        result = CreationResult()
        
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        missing_fields = [field for field in required_fields if field not in character_data]
        
        if missing_fields:
            result.error = f"Missing required fields: {', '.join(missing_fields)}"
            return result
        
        # Validate ability scores
        abilities = character_data.get("ability_scores", {})
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in abilities:
                result.add_warning(f"Missing ability score: {ability}")
            else:
                score = abilities[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    result.add_warning(f"Invalid {ability} score: {score}")
        
        # Validate level
        level = character_data.get("level", 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            result.add_warning(f"Invalid character level: {level}")
        
        result.success = True
        result.data = character_data
        return result
    
    @staticmethod
    def validate_custom_content(character_data: Dict[str, Any], 
                              needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
        """Validate that custom content requirements are met."""
        result = CreationResult(success=True, data=character_data)
        
        # Check for custom species if needed
        if needs_custom_species:
            species = character_data.get("species", "").lower()
            standard_species = [
                "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
                "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
                "goliath", "tabaxi", "kenku", "lizardfolk", "tortle"
            ]
            
            if species in standard_species:
                result.add_warning(f"Used standard species '{species}' when custom was expected")
        
        # Check for custom class if needed
        if needs_custom_class:
            classes = character_data.get("classes", {})
            class_names = [name.lower() for name in classes.keys()]
            standard_classes = [
                "barbarian", "bard", "cleric", "druid", "fighter", "monk",
                "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
                "artificer", "blood hunter"
            ]
            
            for class_name in class_names:
                if class_name in standard_classes:
                    result.add_warning(f"Used standard class '{class_name}' when custom was expected")
                    break
        
        return result

# ============================================================================
# SHARED CHARACTER DATA GENERATOR
# ============================================================================

class CharacterDataGenerator:
    """Handles core character data generation using LLM services."""
    
    def __init__(self, llm_service: LLMService, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    async def generate_character_data(self, description: str, level: int) -> CreationResult:
        """Generate core character data with retry logic."""
        start_time = time.time()
        
        needs_custom_species = self._needs_custom_species(description)
        needs_custom_class = self._needs_custom_class(description)
        
        # Create targeted prompt
        prompt = self._create_character_prompt(description, level, needs_custom_species, needs_custom_class)
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Character generation attempt {attempt + 1}/{self.config.max_retries}")
                
                timeout = max(self.config.base_timeout - (attempt * 5), 10)
                response = await self.llm_service.generate_content(prompt)
                
                # Clean and parse response
                cleaned_response = self._clean_json_response(response)
                character_data = json.loads(cleaned_response)
                character_data["level"] = level
                
                # Validate basic structure
                validation_result = self.validator.validate_basic_structure(character_data)
                if not validation_result.success:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(f"Validation failed: {validation_result.error}, retrying...")
                        continue
                    else:
                        character_data = self._apply_fixes(character_data, description, level)
                
                # Validate custom content requirements
                custom_validation = self.validator.validate_custom_content(
                    character_data, needs_custom_species, needs_custom_class
                )
                
                result = CreationResult(success=True, data=character_data)
                result.warnings.extend(validation_result.warnings + custom_validation.warnings)
                result.creation_time = time.time() - start_time
                
                logger.info("Character generation successful")
                return result
                
            except (TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    prompt = self._get_simplified_prompt(description, level)
                    continue
                else:
                    logger.error("All attempts failed, using fallback")
                    return self._get_fallback_result(description, level, start_time)
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    return self._get_fallback_result(description, level, start_time)
        
        return self._get_fallback_result(description, level, start_time)
    
    def _needs_custom_species(self, description: str) -> bool:
        """Determine if description requires custom species."""
        custom_keywords = ["unique", "custom", "new species", "homebrew", "original", "invented"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _needs_custom_class(self, description: str) -> bool:
        """Determine if description requires custom class."""
        custom_keywords = ["custom class", "homebrew class", "new class", "unique class"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _create_character_prompt(self, description: str, level: int, 
                               needs_custom_species: bool, needs_custom_class: bool) -> str:
        """Create optimized character generation prompt."""
        
        custom_instructions = ""
        if needs_custom_species:
            custom_instructions += "CREATE custom species name matching description. "
        if needs_custom_class:
            custom_instructions += "CREATE custom class name matching description. "
        
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}
{custom_instructions}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Skill1","Skill2"],"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":[{{"name":"Item","quantity":1}}],"backstory":"Brief backstory"}}

Match description exactly. Return complete JSON only."""
    
    def _get_simplified_prompt(self, description: str, level: int) -> str:
        """Get simplified prompt for retry attempts."""
        return f"""Character: {description}, Level {level}
JSON: {{"name":"Name","species":"Human","level":{level},"classes":{{"Fighter":{level}}},"background":"Folk Hero","alignment":["Neutral","Good"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Athletics"],"personality_traits":["Brave"],"ideals":["Justice"],"bonds":["Community"],"flaws":["Stubborn"],"armor":"Leather","weapons":[{{"name":"Sword","damage":"1d8","properties":["versatile"]}}],"equipment":[{{"name":"Pack","quantity":1}}],"backstory":"A brave {description} warrior."}}"""
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response."""
        if not response:
            raise ValueError("Empty response")
        
        # Remove markdown and find JSON boundaries
        response = response.replace('```json', '').replace('```', '').strip()
        
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[first_brace:last_brace + 1]
        
        # Basic JSON repair
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json_str
    
    def _apply_fixes(self, character_data: Dict[str, Any], description: str, level: int) -> Dict[str, Any]:
        """Apply fixes for common character data issues."""
        
        # Fix missing fields with defaults
        defaults = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "classes": {"Fighter": level},
            "ability_scores": {
                "strength": 13, "dexterity": 12, "constitution": 14,
                "intelligence": 11, "wisdom": 10, "charisma": 8
            },
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "skill_proficiencies": ["Athletics"],
            "personality_traits": ["Determined"],
            "ideals": ["Justice"],
            "bonds": ["Hometown"],
            "flaws": ["Stubborn"],
            "armor": "Leather",
            "weapons": [{"name": "Sword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
            "backstory": f"A {description} seeking adventure."
        }
        
        for key, value in defaults.items():
            if key not in character_data or not character_data[key]:
                character_data[key] = value
        
        return character_data
    
    def _generate_name_from_description(self, description: str) -> str:
        """Generate a simple name from description."""
        words = description.split()
        if words:
            return words[0].capitalize() + " " + ("Adventurer" if len(words) == 1 else words[-1].capitalize())
        return "Unknown Adventurer"
    
    def _get_fallback_result(self, description: str, level: int, start_time: float) -> CreationResult:
        """Create a fallback character when generation fails."""
        fallback_data = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "ability_scores": {
                "strength": 15, "dexterity": 13, "constitution": 14,
                "intelligence": 12, "wisdom": 10, "charisma": 8
            },
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "personality_traits": ["Brave and determined"],
            "ideals": ["Justice for all"],
            "bonds": ["Protecting my community"],
            "flaws": ["Too trusting of others"],
            "armor": "Chain Mail",
            "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
            "backstory": f"A fallback character based on: {description}"
        }
        
        result = CreationResult(success=True, data=fallback_data)
        result.add_warning("Used fallback character due to generation failures")
        result.creation_time = time.time() - start_time
        
        return result

# ============================================================================
# SHARED JOURNAL-BASED EVOLUTION
# ============================================================================

class JournalBasedEvolution:
    """Handles character evolution based on journal entries and play history."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze_play_patterns(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze journal entries to determine character play patterns."""
        if not journal_entries:
            return {"themes": [], "suggested_evolution": [], "confidence": 0.0}
        
        # Extract text from all journal entries
        journal_text = " ".join([entry.get("entry", "") for entry in journal_entries])
        
        # Enhanced keyword analysis
        analysis_patterns = {
            "stealth_assassin": {
                "keywords": ["sneak", "hide", "assassin", "shadow", "stealth", "backstab", "ambush", "poison", "silent", "dagger"],
                "weight": 1.0
            },
            "social_diplomat": {
                "keywords": ["persuade", "negotiate", "charm", "diplomat", "talk", "convince", "deception", "insight", "court"],
                "weight": 1.0
            },
            "combat_warrior": {
                "keywords": ["fight", "battle", "attack", "combat", "weapon", "armor", "charge", "defend", "warrior", "sword"],
                "weight": 1.0
            },
            "magic_scholar": {
                "keywords": ["spell", "magic", "cast", "ritual", "arcane", "divine", "study", "research", "tome", "scroll"],
                "weight": 1.0
            },
            "explorer_ranger": {
                "keywords": ["explore", "track", "wilderness", "forest", "survival", "nature", "animal", "guide", "scout"],
                "weight": 1.0
            },
            "healer_support": {
                "keywords": ["heal", "cure", "medicine", "help", "support", "protect", "save", "rescue", "tend", "care"],
                "weight": 1.0
            },
            "leader_commander": {
                "keywords": ["lead", "command", "order", "strategy", "tactics", "rally", "inspire", "organize", "direct"],
                "weight": 1.0
            }
        }
        
        text_lower = journal_text.lower()
        detected_themes = {}
        
        for pattern_name, pattern_data in analysis_patterns.items():
            score = sum(text_lower.count(keyword) for keyword in pattern_data["keywords"])
            if score > 0:
                detected_themes[pattern_name] = {
                    "score": score,
                    "confidence": min(score / 10.0, 1.0)  # Cap at 1.0
                }
        
        # Sort themes by score
        sorted_themes = sorted(detected_themes.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "themes": [{"name": theme, "score": data["score"], "confidence": data["confidence"]} 
                      for theme, data in sorted_themes],
            "total_entries": len(journal_entries),
            "analysis_confidence": min(len(journal_entries) / 20.0, 1.0)  # Higher confidence with more entries
        }
    
    def suggest_character_evolution(self, current_character: Dict[str, Any], 
                                  play_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest character evolution based on play patterns."""
        suggestions = {
            "multiclass_recommendations": [],
            "feat_suggestions": [],
            "skill_focus": [],
            "equipment_changes": [],
            "roleplay_evolution": "",
            "mechanical_changes": []
        }
        
        current_classes = current_character.get("classes", {})
        primary_class = max(current_classes.items(), key=lambda x: x[1])[0] if current_classes else "Fighter"
        
        themes = play_analysis.get("themes", [])
        if not themes:
            return suggestions
        
        top_theme = themes[0]["name"] if themes else None
        
        # Multiclass suggestions based on play patterns
        class_suggestions = {
            "stealth_assassin": ["Rogue", "Ranger", "Shadow Monk"],
            "social_diplomat": ["Bard", "Paladin", "Warlock"],
            "combat_warrior": ["Fighter", "Barbarian", "Paladin"],
            "magic_scholar": ["Wizard", "Sorcerer", "Warlock"],
            "explorer_ranger": ["Ranger", "Druid", "Scout Rogue"],
            "healer_support": ["Cleric", "Druid", "Divine Soul Sorcerer"],
            "leader_commander": ["Paladin", "Bard", "War Cleric"]
        }
        
        if top_theme in class_suggestions:
            for suggested_class in class_suggestions[top_theme]:
                if suggested_class not in current_classes:
                    suggestions["multiclass_recommendations"].append({
                        "class": suggested_class,
                        "reason": f"Journal shows strong {top_theme.replace('_', ' ')} tendencies",
                        "confidence": themes[0]["confidence"]
                    })
        
        # Feat suggestions
        feat_suggestions = {
            "stealth_assassin": ["Skulker", "Alert", "Assassinate", "Shadow Touched"],
            "social_diplomat": ["Actor", "Fey Touched", "Skill Expert", "Inspiring Leader"],
            "combat_warrior": ["Great Weapon Master", "Polearm Master", "Sentinel", "Tough"],
            "magic_scholar": ["Ritual Caster", "Magic Initiate", "Fey Touched", "Telekinetic"],
            "explorer_ranger": ["Sharpshooter", "Mobile", "Observant", "Nature Adept"],
            "healer_support": ["Healer", "Inspiring Leader", "Tough", "Fey Touched"],
            "leader_commander": ["Inspiring Leader", "Rally", "Tactical Mind", "Command"]
        }
        
        if top_theme in feat_suggestions:
            suggestions["feat_suggestions"] = feat_suggestions[top_theme]
        
        # Roleplay evolution
        evolution_descriptions = {
            "stealth_assassin": f"Character has evolved from {primary_class} into a shadow operative, using stealth and precision over brute force.",
            "social_diplomat": f"Character has grown beyond {primary_class} combat focus into a skilled negotiator and social manipulator.",
            "combat_warrior": f"Character has embraced their {primary_class} nature, becoming an exceptional warrior and tactician.",
            "magic_scholar": f"Character has discovered magical aptitude beyond their {primary_class} training, seeking arcane knowledge.",
            "explorer_ranger": f"Character has developed strong wilderness skills, moving beyond typical {primary_class} boundaries.",
            "healer_support": f"Character has found their calling in protecting and healing others, expanding beyond {primary_class} limitations.",
            "leader_commander": f"Character has naturally evolved into a leadership role, inspiring others beyond typical {primary_class} expectations."
        }
        
        if top_theme in evolution_descriptions:
            suggestions["roleplay_evolution"] = evolution_descriptions[top_theme]
        
        return suggestions

# ============================================================================
# SHARED UTILITY FUNCTIONS
# ============================================================================

def build_character_core(character_data: Dict[str, Any]) -> CharacterCore:
    """Build a CharacterCore from character data."""
    
    character_core = CharacterCore(character_data["name"])
    character_core.species = character_data.get("species", "Human")
    character_core.background = character_data.get("background", "Folk Hero")
    character_core.character_classes = character_data.get("classes", {"Fighter": 1})
    character_core.alignment = character_data.get("alignment", ["Neutral", "Good"])
    
    # Set personality traits
    character_core.personality_traits = character_data.get("personality_traits", ["Brave"])
    character_core.ideals = character_data.get("ideals", ["Justice"])
    character_core.bonds = character_data.get("bonds", ["Community"])
    character_core.flaws = character_data.get("flaws", ["Stubborn"])
    
    # Set proficiencies
    skill_profs = character_data.get("skill_proficiencies", [])
    for skill in skill_profs:
        character_core.skill_proficiencies[skill] = ProficiencyLevel.PROFICIENT
    
    # Set ability scores
    ability_scores = character_data.get("ability_scores", {})
    for ability_name, score in ability_scores.items():
        if hasattr(character_core, ability_name):
            setattr(character_core, ability_name, AbilityScore(score))
    
    return character_core

def quick_character_sheet(name: str, species: str = "Human", character_class: str = "Fighter", 
                         level: int = 1, add_journal: bool = True) -> CharacterSheet:
    """Create a simple character sheet quickly without LLM generation."""
    
    character_sheet = CharacterSheet(name)
    character_sheet.core.species = species
    character_sheet.core.character_classes = {character_class: level}
    
    # Set default ability scores
    character_sheet.core.strength = AbilityScore(15)
    character_sheet.core.dexterity = AbilityScore(13)
    character_sheet.core.constitution = AbilityScore(14)
    character_sheet.core.intelligence = AbilityScore(12)
    character_sheet.core.wisdom = AbilityScore(10)
    character_sheet.core.charisma = AbilityScore(8)
    
    # Calculate derived stats
    character_sheet.calculate_all_derived_stats()
    
    # Add initial journal if requested
    if add_journal:
        character_sheet.add_journal_entry(
            f"{name} the {species} {character_class} begins their adventure with determination and hope.",
            tags=["character_creation", "quick_creation"]
        )
    
    return character_sheet

def create_specialized_prompt(content_type: str, description: str, level: int = None) -> str:
    """Create specialized prompts for different content types."""
    
    if content_type == "creature":
        cr_guidance = f"Challenge Rating appropriate for level {level} encounters" if level else "appropriate Challenge Rating"
        return f"""Create D&D 5e 2024 creature. Return ONLY JSON:

DESCRIPTION: {description}
{cr_guidance}

Include: name, size, type, challenge_rating, armor_class, hit_points, speed, ability_scores, saving_throws, skills, damage_resistances, damage_immunities, condition_immunities, senses, languages, special_abilities, actions, legendary_actions, lair_actions, regional_effects

Match description exactly. Return complete JSON only."""
    
    elif content_type == "item":
        rarity_guidance = f"Rarity appropriate for level {level} characters" if level else "appropriate rarity"
        return f"""Create D&D 5e 2024 magic item. Return ONLY JSON:

DESCRIPTION: {description}
{rarity_guidance}

Include: name, type, rarity, requires_attunement, description, properties, mechanics, cost, weight

Match description exactly. Return complete JSON only."""
    
    elif content_type == "spell":
        spell_level = min((level or 1) // 2, 9) if level else 1
        return f"""Create D&D 5e 2024 spell. Return ONLY JSON:

DESCRIPTION: {description}
Spell level: {spell_level} or lower

Include: name, level, school, casting_time, range, components, duration, description, at_higher_levels, classes

Match description exactly. Return complete JSON only."""
    
    elif content_type == "backstory":
        return f"""Generate a detailed D&D character backstory. Return ONLY JSON:

CHARACTER CONCEPT: {description}
LEVEL: {level or 1}

IMPORTANT: Return only valid JSON in this format:
{{
    "backstory": "A detailed backstory of 2-3 paragraphs...",
    "personality_traits": ["Trait 1", "Trait 2"],
    "ideals": ["Ideal 1"],
    "bonds": ["Bond 1"],
    "flaws": ["Flaw 1"]
}}

Match the character concept exactly. Return complete JSON only."""
    
    else:  # Default to character
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level or 1}

Match description exactly. Return complete JSON only."""
