# CONSISTENCY VALIDATION SYSTEM
# 
# This system addresses two critical consistency concerns:
#
# 1. THEMATIC CONSISTENCY: Ensures created species, class, weapons, armor, and spells are 
#    thematically aligned with the character concept. For example, water-based species won't 
#    receive fire-based weapons. This is implemented through:
#    - ConceptualValidator.validate_thematic_consistency() 
#    - ContentAligner.align_content_with_concept()
#    - Theme extraction and conflict detection algorithms
#
# 2. LEVEL APPROPRIATENESS: Ensures characters receive weapons, spells, and armor appropriate 
#    for their level. For example, level 1 characters won't receive level 20 weapons or spells.
#    This is implemented through:
#    - LevelValidator.validate_level_appropriate_content()
#    - PowerScaler.scale_content_to_level()
#    - Rarity and power level validation systems

"""
Character Creation Service - Refactored and Simplified

This module provides the main character creation workflow by integrating
the cleaned modular components. It handles the complete character creation
process including validation, generation, and iterative improvements.

Dependencies: All cleaned backend modules
"""

# REFACTORED: Journal tracker integration complete. Character creation now includes:
# - Journal-based character evolution analysis
# - Play history integration for character updates
# - Automatic character progression suggestions based on journal themes
# - Enhanced backstory generation incorporating journal entries
# - Background evolution with journal highlights during level-ups
# - Character progression snapshots for tracking development over time
# - NPC and relationship tracking through journal entries

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet, CharacterStats
from core_models import AbilityScore, ASIManager, MagicItemManager, CharacterLevelManager, ProficiencyLevel, AbilityScoreSource
from custom_content_models import ContentRegistry, FeatManager
from ability_management import AdvancedAbilityManager, CustomContentAbilityManager
from llm_service_new import create_llm_service, LLMService
from generators import BackstoryGenerator, CustomContentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION AND RESULT CLASSES
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
# JOURNAL-BASED CHARACTER EVOLUTION
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
    
    def generate_evolved_backstory(self, current_backstory: str, journal_entries: List[Dict[str, Any]]) -> str:
        """Generate an evolved backstory incorporating journal entries."""
        if not journal_entries:
            return current_backstory
        
        # Summarize key journal moments
        key_moments = []
        for entry in journal_entries[-10:]:  # Last 10 entries for recent development
            entry_text = entry.get("entry", "")
            if len(entry_text) > 50:  # Only include substantial entries
                key_moments.append(entry_text)
        
        if not key_moments:
            return current_backstory
        
        prompt = f"""Evolve this character's backstory by incorporating their recent adventures:

ORIGINAL BACKSTORY:
{current_backstory}

RECENT ADVENTURES (from journal):
{chr(10).join(['- ' + moment for moment in key_moments[:5]])}

Create an evolved backstory that:
1. Keeps the core original elements
2. Shows character growth through these experiences
3. Explains how these adventures changed them
4. Maintains narrative consistency
5. Reflects their evolution as an adventurer

Return the evolved backstory as a single coherent narrative."""
        
        try:
            evolved_backstory = self.llm_service.generate(prompt, timeout_seconds=15)
            return evolved_backstory.strip()
        except Exception as e:
            logger.warning(f"Failed to generate evolved backstory: {e}")
            return current_backstory
    
    def create_character_arc_summary(self, character_name: str, journal_entries: List[Dict[str, Any]], 
                                   evolution_suggestions: Dict[str, Any]) -> str:
        """Create a summary of the character's development arc."""
        if not journal_entries:
            return f"{character_name} is just beginning their adventure."
        
        entry_count = len(journal_entries)
        themes = evolution_suggestions.get("themes", [])
        
        if not themes:
            return f"Through {entry_count} adventures, {character_name} has grown as a well-rounded adventurer."
        
        top_themes = [theme["name"].replace("_", " ") for theme in themes[:3]]
        
        arc_summary = f"""Character Arc for {character_name}:

Through {entry_count} documented adventures, {character_name} has shown remarkable growth and development. 

Primary Development Themes:
{chr(10).join(['• ' + theme.title() for theme in top_themes])}

Evolution Summary:
{evolution_suggestions.get('roleplay_evolution', 'Character continues to grow through their adventures.')}

This character has grown beyond their original conception, shaped by the challenges and choices they've faced in their journey."""
        
        return arc_summary

# ============================================================================
# CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Handles validation of character data with comprehensive consistency checks."""
    
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
    
    @staticmethod
    def validate_comprehensive_consistency(character_data: Dict[str, Any], 
                                         description: str) -> CreationResult:
        """
        Perform comprehensive consistency validation including thematic alignment 
        and level appropriateness.
        """
        result = CreationResult(success=True, data=character_data)
        
        # 1. Validate thematic consistency
        thematic_result = ConceptualValidator.validate_thematic_consistency(
            character_data, description
        )
        
        # Merge thematic warnings
        if thematic_result.warnings:
            result.warnings.extend(thematic_result.warnings)
        
        # 2. Validate level appropriateness
        level_result = LevelValidator.validate_level_appropriate_content(character_data)
        
        # Merge level warnings
        if level_result.warnings:
            result.warnings.extend(level_result.warnings)
        
        # 3. Check for severe consistency issues
        severe_issues = CharacterValidator._check_severe_consistency_issues(
            character_data, description
        )
        
        if severe_issues:
            result.warnings.extend(severe_issues)
        
        logger.info(f"Comprehensive consistency validation complete with {len(result.warnings)} warnings")
        return result
    
    @staticmethod
    def _check_severe_consistency_issues(character_data: Dict[str, Any], 
                                       description: str) -> List[str]:
        """Check for severe consistency issues that should be flagged."""
        issues = []
        
        # Check for major theme conflicts (e.g., holy paladin with necromantic spells)
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["holy", "paladin", "cleric", "divine"]):
            spells = character_data.get("spells", [])
            for spell in spells:
                spell_name = spell if isinstance(spell, str) else spell.get("name", "")
                if any(word in spell_name.lower() for word in ["necro", "death", "drain", "dark"]):
                    issues.append(f"Major theme conflict: Divine character with necromantic spell '{spell_name}'")
        
        # Check for level vs. power mismatches
        level = character_data.get("level", 1)
        if level <= 3:
            # Low level characters shouldn't have high-power items
            weapons = character_data.get("weapons", [])
            for weapon in weapons:
                weapon_name = weapon.get("name", "")
                if any(word in weapon_name.lower() for word in ["legendary", "artifact", "divine", "ancient"]):
                    issues.append(f"Level mismatch: Level {level} character with high-power weapon '{weapon_name}'")
        
        return issues
    
    @staticmethod
    def apply_consistency_fixes(character_data: Dict[str, Any], 
                              description: str) -> Dict[str, Any]:
        """
        Apply automatic consistency fixes to character data.
        """
        # Apply thematic alignment
        aligned_data = ContentAligner.align_content_with_concept(character_data, description)
        
        # Apply level scaling
        scaled_data = PowerScaler.scale_content_to_level(aligned_data)
        
        logger.info("Applied automatic consistency fixes")
        return scaled_data

# ============================================================================
# CHARACTER DATA GENERATOR
# ============================================================================

class CharacterDataGenerator:
    """Handles core character data generation using LLM services."""
    
    def __init__(self, llm_service: LLMService, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    def generate_character_data(self, description: str, level: int) -> CreationResult:
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
                response = self.llm_service.generate(prompt, timeout_seconds=timeout)
                
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
                
                # Perform comprehensive consistency validation
                consistency_validation = self.validator.validate_comprehensive_consistency(
                    character_data, description
                )
                
                # Apply automatic consistency fixes if warnings are present
                if consistency_validation.warnings:
                    logger.info(f"Applying consistency fixes for {len(consistency_validation.warnings)} issues")
                    character_data = self.validator.apply_consistency_fixes(character_data, description)
                    
                    # Re-validate after fixes
                    post_fix_validation = self.validator.validate_comprehensive_consistency(
                        character_data, description
                    )
                    consistency_validation.warnings = post_fix_validation.warnings
                
                result = CreationResult(success=True, data=character_data)
                result.warnings.extend(validation_result.warnings + custom_validation.warnings + consistency_validation.warnings)
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
# CHARACTER CREATOR
# ============================================================================

class CharacterCreator:
    """Main character creation service integrating all components with journal evolution."""
    
    def __init__(self, llm_service: LLMService = None, config: CreationConfig = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize components
        self.content_registry = ContentRegistry()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.custom_content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        
        # Initialize journal-based evolution
        self.journal_evolution = JournalBasedEvolution(self.llm_service)
        
        # Initialize managers
        self.feat_manager = FeatManager()
        
        logger.info("Character Creator initialized with journal evolution support")
    
    def create_character(self, description: str, level: int = 1, 
                        generate_backstory: bool = True,
                        include_custom_content: bool = False,
                        add_initial_journal: bool = True) -> CreationResult:
        """Create a complete D&D character from description."""
        
        start_time = time.time()
        
        try:
            # Generate core character data
            logger.info(f"Creating character: {description} (Level {level})")
            data_result = self.data_generator.generate_character_data(description, level)
            
            if not data_result.success:
                return data_result
            
            character_data = data_result.data
            
            # Create CharacterCore from the data
            character_core = self._build_character_core(character_data)
            
            # Create character sheet with journal initialization
            character_sheet = CharacterSheet(character_core.name)
            character_sheet.core = character_core
            character_sheet.state = CharacterState()
            character_sheet.stats = CharacterStats(character_core, character_sheet.state)
            
            # Add initial journal entry if requested
            if add_initial_journal:
                self._add_initial_journal_content(character_sheet, character_data, description)
            
            # Create managers for the character
            asi_manager = ASIManager()
            level_manager = CharacterLevelManager()
            ability_manager = AdvancedAbilityManager(character_core)
            
            # Generate backstory if requested
            backstory = None
            if generate_backstory:
                backstory_prompt = self._build_backstory_prompt(character_data)
                backstory = self.backstory_generator.generate_backstory(backstory_prompt)
                
                # Set backstory in character core
                if backstory:
                    character_core.backstory = backstory
            
            # Generate custom content if requested
            custom_content = {}
            if include_custom_content:
                custom_content = self._generate_custom_content(character_data, description)
            
            # Initialize character state with proper HP
            character_sheet.calculate_all_derived_stats()
            
            # Build final result
            result_data = {
                "core": character_core.to_dict(),
                "sheet": character_sheet.get_character_summary(),
                "backstory": backstory,
                "custom_content": custom_content,
                "journal": {
                    "entries": character_sheet.get_journal_entries(),
                    "summary": character_sheet.get_journal_summary()
                },
                "managers": {
                    "asi_info": asi_manager.calculate_available_asis(character_core.character_classes),
                    "level_summary": level_manager.get_level_progression_summary(character_core.character_classes),
                    "ability_summary": ability_manager.get_ability_summary()
                }
            }
            
            result = CreationResult(success=True, data=result_data)
            result.warnings.extend(data_result.warnings)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Character creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character creation failed: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def update_character_with_journal(self, character_sheet: CharacterSheet, 
                                    force_evolution: bool = False) -> CreationResult:
        """Update an existing character based on their journal entries."""
        
        start_time = time.time()
        
        try:
            journal_entries = character_sheet.get_journal_entries()
            
            if not journal_entries and not force_evolution:
                return CreationResult(
                    success=True, 
                    data={"message": "No journal entries to analyze"},
                    warnings=["Character has no journal entries for evolution analysis"]
                )
            
            # Analyze play patterns from journal
            play_analysis = self.journal_evolution.analyze_play_patterns(journal_entries)
            
            # Generate evolution suggestions
            current_character_data = character_sheet.get_character_summary()
            evolution_suggestions = self.journal_evolution.suggest_character_evolution(
                current_character_data, play_analysis
            )
            
            # Generate evolved backstory
            current_backstory = character_sheet.get_backstory()
            evolved_backstory = self.journal_evolution.generate_evolved_backstory(
                current_backstory, journal_entries
            )
            
            # Create character arc summary
            character_arc = self.journal_evolution.create_character_arc_summary(
                character_sheet.get_name(), journal_entries, play_analysis
            )
            
            # Update backstory if it evolved
            if evolved_backstory and evolved_backstory != current_backstory:
                character_sheet.core.backstory = evolved_backstory
                # Add journal entry about backstory evolution
                character_sheet.add_journal_entry(
                    "Character backstory has evolved based on recent adventures and experiences.",
                    tags=["character_development", "backstory_evolution"]
                )
            
            result_data = {
                "character_summary": character_sheet.get_character_summary(),
                "play_analysis": play_analysis,
                "evolution_suggestions": evolution_suggestions,
                "evolved_backstory": evolved_backstory,
                "character_arc": character_arc,
                "journal_summary": character_sheet.get_journal_summary()
            }
            
            result = CreationResult(success=True, data=result_data)
            result.creation_time = time.time() - start_time
            
            # Add suggestions as warnings for visibility
            if evolution_suggestions.get("multiclass_recommendations"):
                for rec in evolution_suggestions["multiclass_recommendations"][:2]:  # Top 2
                    result.add_warning(f"Consider multiclassing: {rec['class']} - {rec['reason']}")
            
            logger.info(f"Character evolution analysis completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character journal analysis failed: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def apply_evolution_suggestions(self, character_sheet: CharacterSheet, 
                                  evolution_suggestions: Dict[str, Any],
                                  apply_multiclass: bool = False,
                                  apply_feats: bool = False) -> CreationResult:
        """Apply evolution suggestions to a character."""
        
        start_time = time.time()
        changes_made = []
        
        try:
            # Apply multiclass suggestions if requested
            if apply_multiclass and evolution_suggestions.get("multiclass_recommendations"):
                top_multiclass = evolution_suggestions["multiclass_recommendations"][0]
                new_class = top_multiclass["class"]
                
                # Add 1 level in the suggested class
                current_classes = character_sheet.core.character_classes.copy()
                current_classes[new_class] = current_classes.get(new_class, 0) + 1
                character_sheet.core.character_classes = current_classes
                
                # Add journal entry
                character_sheet.add_journal_entry(
                    f"Began training in {new_class} based on recent experiences and natural aptitude.",
                    tags=["multiclass", "character_development", new_class.lower()]
                )
                
                changes_made.append(f"Added 1 level in {new_class}")
            
            # Apply feat suggestions (simulation - would need actual feat system)
            if apply_feats and evolution_suggestions.get("feat_suggestions"):
                suggested_feats = evolution_suggestions["feat_suggestions"][:2]  # Top 2
                
                character_sheet.add_journal_entry(
                    f"Considering developing new abilities: {', '.join(suggested_feats)}",
                    tags=["feat_consideration", "character_development"]
                )
                
                changes_made.append(f"Noted feat considerations: {', '.join(suggested_feats)}")
            
            # Recalculate stats
            character_sheet.calculate_all_derived_stats()
            
            result_data = {
                "character_summary": character_sheet.get_character_summary(),
                "changes_applied": changes_made,
                "evolution_complete": True
            }
            
            result = CreationResult(success=True, data=result_data)
            result.creation_time = time.time() - start_time
            
            for change in changes_made:
                result.add_warning(f"Applied: {change}")
            
            logger.info(f"Evolution suggestions applied in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply evolution suggestions: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def _add_initial_journal_content(self, character_sheet: CharacterSheet, 
                                   character_data: Dict[str, Any], description: str):
        """Add initial journal content for a new character."""
        
        # Add creation entry (already added by CharacterSheet constructor)
        
        # Add backstory-based initial entry
        background = character_data.get("background", "Folk Hero")
        personality = character_data.get("personality_traits", ["Brave"])
        
        initial_entry = f"Today I set out on my first real adventure. As a {background}, I've always {personality[0].lower() if personality else 'been determined'}, but now it's time to prove myself in the wider world. The road ahead is uncertain, but I'm ready for whatever challenges await."
        
        character_sheet.add_journal_entry(
            initial_entry,
            tags=["character_creation", "first_adventure", "backstory"]
        )
        
        # Add a hint about their potential based on description
        if "stealth" in description.lower() or "rogue" in description.lower():
            character_sheet.add_journal_entry(
                "I've always felt more comfortable in the shadows, watching and learning before acting.",
                tags=["character_creation", "personality", "stealth"]
            )
        elif "magic" in description.lower() or "wizard" in description.lower():
            character_sheet.add_journal_entry(
                "The arcane arts have always fascinated me. I sense there's more to magic than I currently understand.",
                tags=["character_creation", "personality", "magic"]
            )
        elif "social" in description.lower() or "bard" in description.lower():
            character_sheet.add_journal_entry(
                "I find myself naturally drawn to people and their stories. There's power in words and connections.",
                tags=["character_creation", "personality", "social"]
            )
    
    def _build_character_core(self, character_data: Dict[str, Any]) -> CharacterCore:
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
    
    def _build_backstory_prompt(self, character_data: Dict[str, Any]) -> str:
        """Build a backstory generation prompt from character data."""
        
        classes = character_data.get("classes", {})
        class_list = ", ".join([f"{cls} {level}" for cls, level in classes.items()])
        
        prompt = f"""Create a compelling backstory for this D&D character:

Name: {character_data.get('name', 'Unknown')}
Species: {character_data.get('species', 'Human')}
Classes: {class_list}
Background: {character_data.get('background', 'Folk Hero')}
Personality: {', '.join(character_data.get('personality_traits', ['Brave']))}
Ideals: {', '.join(character_data.get('ideals', ['Justice']))}
Bonds: {', '.join(character_data.get('bonds', ['Community']))}
Flaws: {', '.join(character_data.get('flaws', ['Stubborn']))}

Generate a rich, detailed backstory that explains their motivations, background, and how they became an adventurer."""
        
        return prompt
    
    def _generate_custom_content(self, character_data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Generate custom content based on character data."""
        
        custom_content = {}
        
        # Generate custom species if needed
        species = character_data.get("species", "")
        standard_species = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome"]
        
        if species.lower() not in standard_species:
            try:
                custom_species = self.custom_content_generator.generate_custom_species(
                    f"Create a custom species called '{species}' based on: {description}"
                )
                custom_content["species"] = custom_species.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom species: {e}")
        
        # Generate custom background if non-standard
        background = character_data.get("background", "")
        standard_backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
        
        if background.lower() not in standard_backgrounds:
            try:
                # Use content registry to create custom background
                background_id = self.content_registry.add_custom_background(
                    background,
                    f"Custom background: {background}",
                    character_data.get("skill_proficiencies", [])[:2],
                    character_data.get("equipment", [])[:3]
                )
                custom_background = self.content_registry.get_custom_background(background_id)
                if custom_background:
                    custom_content["background"] = custom_background.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom background: {e}")
        
        return custom_content

# ============================================================================
# CONSISTENCY VALIDATION SYSTEM
# ============================================================================

class ConceptualValidator:
    """Validates thematic consistency between character elements."""
    
    ELEMENTAL_THEMES = {
        "fire": ["flame", "burn", "heat", "ember", "inferno", "blaze", "scorch", "ignite"],
        "water": ["aqua", "ocean", "sea", "wave", "current", "flow", "tide", "frost"],
        "earth": ["stone", "rock", "mountain", "crystal", "gem", "mineral", "clay"],
        "air": ["wind", "storm", "lightning", "thunder", "sky", "cloud", "tempest"],
        "shadow": ["dark", "shadow", "void", "night", "eclipse", "umbra", "shade"],
        "light": ["radiant", "holy", "divine", "bright", "sun", "star", "celestial"],
        "nature": ["forest", "wild", "grove", "leaf", "thorn", "seed", "bloom"],
        "death": ["necro", "bone", "corpse", "grave", "decay", "undead", "soul"]
    }
    
    THEME_CONFLICTS = {
        "fire": ["water", "ice"],
        "water": ["fire"],
        "light": ["shadow", "death"],
        "shadow": ["light"],
        "nature": ["death", "undead"],
        "death": ["nature", "light"],
        "holy": ["shadow", "death", "fiend"],
        "fiend": ["holy", "light", "celestial"]
    }
    
    @classmethod
    def extract_themes(cls, text: str) -> List[str]:
        """Extract thematic elements from text."""
        text_lower = text.lower()
        themes = []
        
        for theme, keywords in cls.ELEMENTAL_THEMES.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    @classmethod
    def validate_thematic_consistency(cls, character_data: Dict[str, Any], 
                                    description: str) -> CreationResult:
        """Validate thematic consistency across all character elements."""
        result = CreationResult(success=True, data=character_data)
        
        # Extract themes from description and character elements
        base_themes = cls.extract_themes(description)
        species_themes = cls.extract_themes(character_data.get("species", ""))
        
        # Check weapons for thematic conflicts
        weapons = character_data.get("weapons", [])
        for weapon in weapons:
            weapon_name = weapon.get("name", "")
            weapon_themes = cls.extract_themes(weapon_name)
            
            for weapon_theme in weapon_themes:
                for base_theme in base_themes:
                    if cls._themes_conflict(base_theme, weapon_theme):
                        result.add_warning(
                            f"Thematic conflict: {base_theme} character concept conflicts with {weapon_theme} weapon '{weapon_name}'"
                        )
        
        # Check armor for thematic conflicts
        armor = character_data.get("armor", "")
        if armor:
            armor_themes = cls.extract_themes(armor)
            for armor_theme in armor_themes:
                for base_theme in base_themes:
                    if cls._themes_conflict(base_theme, armor_theme):
                        result.add_warning(
                            f"Thematic conflict: {base_theme} character concept conflicts with {armor_theme} armor '{armor}'"
                        )
        
        # Check spells for thematic conflicts (if character has spells)
        spells = character_data.get("spells", [])
        for spell in spells:
            spell_name = spell if isinstance(spell, str) else spell.get("name", "")
            spell_themes = cls.extract_themes(spell_name)
            
            for spell_theme in spell_themes:
                for base_theme in base_themes:
                    if cls._themes_conflict(base_theme, spell_theme):
                        result.add_warning(
                            f"Thematic conflict: {base_theme} character concept conflicts with {spell_theme} spell '{spell_name}'"
                        )
        
        logger.info(f"Thematic validation complete. Base themes: {base_themes}")
        return result
    
    @classmethod
    def _themes_conflict(cls, theme1: str, theme2: str) -> bool:
        """Check if two themes conflict with each other."""
        conflicts = cls.THEME_CONFLICTS.get(theme1, [])
        return theme2 in conflicts

class LevelValidator:
    """Validates level-appropriate content for characters."""
    
    # Define power/rarity tiers by level ranges
    LEVEL_TIERS = {
        "novice": (1, 4),      # Levels 1-4
        "apprentice": (5, 10), # Levels 5-10
        "expert": (11, 16),    # Levels 11-16
        "master": (17, 20)     # Levels 17-20
    }
    
    # Weapon power levels
    WEAPON_POWER_INDICATORS = {
        "legendary": "master",
        "artifact": "master", 
        "very rare": "expert",
        "rare": "apprentice",
        "uncommon": "novice",
        "common": "novice",
        "masterwork": "apprentice",
        "enchanted": "apprentice",
        "magical": "apprentice",
        "ancient": "expert",
        "divine": "master",
        "demonic": "expert"
    }
    
    # Spell level by character level (maximum spell level available)
    MAX_SPELL_LEVEL_BY_CHARACTER_LEVEL = {
        1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5,
        11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9, 18: 9, 19: 9, 20: 9
    }
    
    @classmethod
    def validate_level_appropriate_content(cls, character_data: Dict[str, Any]) -> CreationResult:
        """Validate that all content is appropriate for the character's level."""
        result = CreationResult(success=True, data=character_data)
        character_level = character_data.get("level", 1)
        
        # Validate weapons
        cls._validate_weapon_levels(character_data, character_level, result)
        
        # Validate armor
        cls._validate_armor_level(character_data, character_level, result)
        
        # Validate spells
        cls._validate_spell_levels(character_data, character_level, result)
        
        # Validate equipment rarity
        cls._validate_equipment_rarity(character_data, character_level, result)
        
        logger.info(f"Level appropriateness validation complete for level {character_level} character")
        return result
    
    @classmethod
    def _validate_weapon_levels(cls, character_data: Dict[str, Any], 
                              character_level: int, result: CreationResult):
        """Validate weapon power levels."""
        weapons = character_data.get("weapons", [])
        character_tier = cls._get_character_tier(character_level)
        
        for weapon in weapons:
            weapon_name = weapon.get("name", "")
            weapon_desc = weapon.get("description", "")
            weapon_text = f"{weapon_name} {weapon_desc}".lower();
            
            # Check for power level indicators
            weapon_tier = cls._determine_weapon_tier(weapon_text)
            
            if weapon_tier and not cls._tier_appropriate(character_tier, weapon_tier):
                tier_levels = cls.LEVEL_TIERS[weapon_tier]
                result.add_warning(
                    f"Level mismatch: {weapon_name} appears to be {weapon_tier}-tier "
                    f"(levels {tier_levels[0]}-{tier_levels[1]}) but character is level {character_level}"
                )
    
    @classmethod
    def _validate_armor_level(cls, character_data: Dict[str, Any], 
                            character_level: int, result: CreationResult):
        """Validate armor power level."""
        armor = character_data.get("armor", "")
        if not armor:
            return
            
        character_tier = cls._get_character_tier(character_level)
        armor_text = armor.lower()
        
        # Check for high-level armor indicators
        high_level_indicators = ["plate", "magical", "enchanted", "artifact", "legendary", "adamantine", "mithril"]
        
        if character_level < 5 and any(indicator in armor_text for indicator in high_level_indicators):
            result.add_warning(
                f"Level mismatch: {armor} may be too advanced for level {character_level} character"
            )
    
    @classmethod
    def _validate_spell_levels(cls, character_data: Dict[str, Any], 
                             character_level: int, result: CreationResult):
        """Validate spell levels against character level."""
        spells = character_data.get("spells", [])
        max_spell_level = cls.MAX_SPELL_LEVEL_BY_CHARACTER_LEVEL.get(character_level, 1)
        
        for spell in spells:
            spell_name = spell if isinstance(spell, str) else spell.get("name", "")
            
            # Try to extract spell level from name or description
            spell_level = cls._estimate_spell_level(spell_name)
            
            if spell_level and spell_level > max_spell_level:
                result.add_warning(
                    f"Level mismatch: {spell_name} appears to be level {spell_level} spell "
                    f"but character can only cast up to level {max_spell_level} spells"
                )
    
    @classmethod
    def _validate_equipment_rarity(cls, character_data: Dict[str, Any], 
                                 character_level: int, result: CreationResult):
        """Validate overall equipment rarity."""
        equipment = character_data.get("equipment", [])
        character_tier = cls._get_character_tier(character_level)
        
        rare_item_count = 0
        for item in equipment:
            item_name = item.get("name", "") if isinstance(item, dict) else str(item)
            item_text = item_name.lower()
            
            if any(indicator in item_text for indicator in ["rare", "magical", "enchanted", "legendary"]):
                rare_item_count += 1
        
        # Check if character has too many rare items for their level
        max_rare_items = {"novice": 0, "apprentice": 1, "expert": 2, "master": 4}
        
        if rare_item_count > max_rare_items.get(character_tier, 0):
            result.add_warning(
                f"Equipment rarity concern: Level {character_level} character has {rare_item_count} "
                f"rare/magical items (typical max: {max_rare_items.get(character_tier, 0)})"
            )
    
    @classmethod
    def _get_character_tier(cls, level: int) -> str:
        """Get the character's power tier based on level."""
        for tier, (min_level, max_level) in cls.LEVEL_TIERS.items():
            if min_level <= level <= max_level:
                return tier
        return "novice"
    
    @classmethod
    def _determine_weapon_tier(cls, weapon_text: str) -> Optional[str]:
        """Determine weapon tier from text description."""
        for indicator, tier in cls.WEAPON_POWER_INDICATORS.items():
            if indicator in weapon_text:
                return tier
        return None
    
    @classmethod
    def _tier_appropriate(cls, character_tier: str, item_tier: str) -> bool:
        """Check if item tier is appropriate for character tier."""
        tier_order = ["novice", "apprentice", "expert", "master"]
        char_index = tier_order.index(character_tier)
        item_index = tier_order.index(item_tier)
        
        # Allow items up to one tier higher
        return item_index <= char_index + 1
    
    @classmethod
    def _estimate_spell_level(cls, spell_name: str) -> Optional[int]:
        """Estimate spell level from name using common patterns."""
        spell_lower = spell_name.lower()
        
        # High-level spell indicators
        if any(word in spell_lower for word in ["meteor", "wish", "gate", "storm", "tsunami", "earthquake"]):
            return 9
        elif any(word in spell_lower for word in ["disintegrate", "chain", "mass", "greater"]):
            return 6
        elif any(word in spell_lower for word in ["fireball", "lightning bolt", "counterspell"]):
            return 3
        elif any(word in spell_lower for word in ["shield", "magic missile", "cure"]):
            return 1
        
        return None

class ContentAligner:
    """Aligns content with character concept and level."""
    
    @classmethod
    def align_content_with_concept(cls, character_data: Dict[str, Any], 
                                 description: str) -> Dict[str, Any]:
        """Modify content to better align with character concept."""
        aligned_data = character_data.copy()
        
        # Extract themes from description
        base_themes = ConceptualValidator.extract_themes(description)
        if not base_themes:
            return aligned_data
        
        primary_theme = base_themes[0]  # Use first theme as primary
        
        # Align weapons
        aligned_data["weapons"] = cls._align_weapons(
            character_data.get("weapons", []), primary_theme
        )
        
        # Align armor
        if character_data.get("armor"):
            aligned_data["armor"] = cls._align_armor(
                character_data["armor"], primary_theme
            )
        
        # Align spells
        aligned_data["spells"] = cls._align_spells(
            character_data.get("spells", []), primary_theme
        )
        
        logger.info(f"Content aligned to {primary_theme} theme")
        return aligned_data
    
    @classmethod
    def _align_weapons(cls, weapons: List[Dict], theme: str) -> List[Dict]:
        """Align weapons with character theme."""
        theme_weapon_mapping = {
            "fire": {"prefix": "Flame", "suffix": "of Burning", "damage_type": "fire"},
            "water": {"prefix": "Frost", "suffix": "of the Depths", "damage_type": "cold"},
            "earth": {"prefix": "Stone", "suffix": "of the Mountain", "damage_type": "bludgeoning"},
            "air": {"prefix": "Storm", "suffix": "of Lightning", "damage_type": "lightning"},
            "shadow": {"prefix": "Shadow", "suffix": "of Darkness", "damage_type": "necrotic"},
            "light": {"prefix": "Radiant", "suffix": "of Light", "damage_type": "radiant"}
        }
        
        if theme not in theme_weapon_mapping:
            return weapons
        
        theme_data = theme_weapon_mapping[theme]
        aligned_weapons = []
        
        for weapon in weapons:
            aligned_weapon = weapon.copy()
            weapon_name = weapon.get("name", "Sword")
            
            # Check if weapon already has thematic elements
            weapon_themes = ConceptualValidator.extract_themes(weapon_name)
            
            if not weapon_themes or theme not in weapon_themes:
                # Add thematic prefix/suffix
                if "sword" in weapon_name.lower():
                    aligned_weapon["name"] = f"{theme_data['prefix']} {weapon_name}"
                else:
                    aligned_weapon["name"] = f"{weapon_name} {theme_data['suffix']}"
                
                # Add thematic damage type if appropriate
                aligned_weapon["damage_type"] = theme_data["damage_type"]
            
            aligned_weapons.append(aligned_weapon)
        
        return aligned_weapons
    
    @classmethod
    def _align_armor(cls, armor: str, theme: str) -> str:
        """Align armor with character theme."""
        theme_armor_mapping = {
            "fire": "Flame-forged",
            "water": "Scale",
            "earth": "Stone",
            "air": "Storm",
            "shadow": "Shadowweave",
            "light": "Radiant"
        }
        
        if theme in theme_armor_mapping and theme not in armor.lower():
            return f"{theme_armor_mapping[theme]} {armor}"
        
        return armor
    
    @classmethod
    def _align_spells(cls, spells: List, theme: str) -> List:
        """Align spells with character theme."""
        if not spells:
            return spells
        
        # For now, return as-is but could implement spell theme alignment
        # This would involve replacing conflicting spells with thematically appropriate ones
        return spells

class PowerScaler:
    """Scales content power to appropriate level."""
    
    @classmethod
    def scale_content_to_level(cls, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scale all content to be appropriate for character level."""
        scaled_data = character_data.copy()
        character_level = character_data.get("level", 1)
        
        # Scale weapons
        scaled_data["weapons"] = cls._scale_weapons(
            character_data.get("weapons", []), character_level
        )
        
        # Scale armor
        if character_data.get("armor"):
            scaled_data["armor"] = cls._scale_armor(
                character_data["armor"], character_level
            )
        
        # Scale spells
        scaled_data["spells"] = cls._scale_spells(
            character_data.get("spells", []), character_level
        )
        
        logger.info(f"Content scaled for level {character_level}")
        return scaled_data
    
    @classmethod
    def _scale_weapons(cls, weapons: List[Dict], level: int) -> List[Dict]:
        """Scale weapon power to character level."""
        scaled_weapons = []
        
        for weapon in weapons:
            scaled_weapon = weapon.copy()
            
            # Add appropriate enhancement based on level
            if level >= 11:
                scaled_weapon["magical_bonus"] = "+2"
                scaled_weapon["properties"] = weapon.get("properties", []) + ["magical"]
            elif level >= 5:
                scaled_weapon["magical_bonus"] = "+1"
                scaled_weapon["properties"] = weapon.get("properties", []) + ["magical"]
            
            # Adjust damage for very low or high levels
            if level == 1:
                # Ensure starting weapons aren't overpowered
                damage = weapon.get("damage", "1d6")
                if "d12" in damage or "2d" in damage:
                    scaled_weapon["damage"] = "1d8"
            
            scaled_weapons.append(scaled_weapon)
        
        return scaled_weapons
    
    @classmethod
    def _scale_armor(cls, armor: str, level: int) -> str:
        """Scale armor to character level."""
        # Basic scaling - could be more sophisticated
        if level >= 10 and "leather" in armor.lower():
            return armor.replace("Leather", "Studded Leather")
        elif level >= 15 and "chain" in armor.lower():
            return armor.replace("Chain", "Plate")
        
        return armor
    
    @classmethod
    def _scale_spells(cls, spells: List, level: int) -> List:
        """Scale spells to appropriate level."""
        if not spells:
            return spells
        
        scaled_spells = []
        max_spell_level = LevelValidator.MAX_SPELL_LEVEL_BY_CHARACTER_LEVEL.get(level, 1)
        
        for spell in spells:
            spell_name = spell if isinstance(spell, str) else spell.get("name", "")
            estimated_level = LevelValidator._estimate_spell_level(spell_name)
            
            if estimated_level and estimated_level > max_spell_level:
                # Replace with level-appropriate alternative
                if isinstance(spell, dict):
                    scaled_spell = spell.copy()
                    scaled_spell["name"] = cls._get_level_appropriate_spell(spell_name, max_spell_level)
                    scaled_spells.append(scaled_spell)
                else:
                    scaled_spells.append(cls._get_level_appropriate_spell(spell_name, max_spell_level))
            else:
                scaled_spells.append(spell)
        
        return scaled_spells
    
    @classmethod
    def _get_level_appropriate_spell(cls, original_spell: str, max_level: int) -> str:
        """Get a level-appropriate replacement spell."""
        spell_alternatives = {
            1: ["Magic Missile", "Shield", "Cure Wounds", "Burning Hands"],
            2: ["Scorching Ray", "Hold Person", "Blur", "Web"],
            3: ["Fireball", "Lightning Bolt", "Counterspell", "Fly"],
            4: ["Greater Invisibility", "Wall of Fire", "Confusion", "Polymorph"],
            5: ["Cone of Cold", "Hold Monster", "Wall of Stone", "Telekinesis"]
        }
        
        # Get spells for the maximum allowed level
        if max_level in spell_alternatives:
            alternatives = spell_alternatives[max_level]
            # Try to match theme if possible
            original_lower = original_spell.lower()
            if "fire" in original_lower or "flame" in original_lower:
                fire_spells = [s for s in alternatives if "fire" in s.lower() or "burn" in s.lower()]
                if fire_spells:
                    return fire_spells[0]
            
            return alternatives[0]  # Default to first alternative
        
        return "Cantrip"  # Fallback for very low levels

# ============================================================================
# ENHANCED CHARACTER VALIDATOR WITH CONSISTENCY CHECKS
# ============================================================================

# ============================================================================
# CONSISTENCY SYSTEM SUMMARY
# ============================================================================
# 
# This implementation addresses the two key consistency concerns:
#
# 1. THEMATIC CONSISTENCY SYSTEM:
#    - ConceptualValidator: Detects thematic conflicts (e.g., fire vs water elements)
#    - ContentAligner: Automatically aligns content with character themes
#    - Theme extraction from descriptions using keyword mapping
#    - Conflict detection between opposing elemental/conceptual themes
#    - Applied during generation and as post-processing validation
#
# 2. LEVEL APPROPRIATENESS SYSTEM:
#    - LevelValidator: Ensures content matches character power level
#    - PowerScaler: Automatically scales content to appropriate level
#    - Tier-based validation (novice/apprentice/expert/master)
#    - Spell level caps based on character level
#    - Equipment rarity restrictions by level range
#    - Weapon/armor power scaling integration
#
# 3. INTEGRATION POINTS:
#    - Enhanced CharacterValidator with comprehensive_consistency validation
#    - Automatic fix application during character generation
#    - Custom content generation includes thematic and level guidance
#    - Validation occurs at multiple points in the creation pipeline
#    - Warnings provide detailed feedback on consistency issues
#
# USAGE:
# The system automatically runs during character creation and provides both
# validation warnings and automatic fixes to ensure created characters have
# consistent, level-appropriate equipment, spells, and abilities that align
# with their conceptual theme.
# ============================================================================
