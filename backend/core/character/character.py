"""
Character Module

Main coordinator class that orchestrates all character-related functionality
by integrating specialized subclasses for different aspects of character creation
and management.
"""

from typing import Dict, List, Any, Optional, Union
import json
import uuid
from pathlib import Path
import datetime
import os

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
    from backend.core.character.ability_scores import AbilityScores
    from backend.core.character.character_validator import CharacterValidator
    from backend.core.character.character_progression import CharacterProgression
    from backend.core.services.data_exporter import CharacterExporter
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object
    AbilityScores = object
    CharacterValidator = object
    CharacterProgression = object
    CharacterExporter = object


class Character(AbstractCharacterClass):
    """
    Main coordinator class that orchestrates all character-related functionality.
    
    This class integrates specialized component classes to manage different aspects
    of D&D character creation, validation, and progression. It serves as the central
    point of interaction for character management.
    """

    def __init__(self, llm_service=None, rules_data_path: str = None, 
                 storage_path: str = None) -> None:
        """
        Initialize the Character manager with component services.
        
        Args:
            llm_service: Optional LLM service for AI-assisted character creation
            rules_data_path: Path to D&D rules data files
            storage_path: Path for character data storage
        """
        # Set up paths
        self.rules_data_path = Path(rules_data_path) if rules_data_path else Path("backend/data/rules")
        self.storage_path = Path(storage_path) if storage_path else Path("backend/data/characters")
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize component services
        self.ability_scores = AbilityScores(rules_data_path=str(self.rules_data_path))
        self.validator = CharacterValidator(rules_data_path=str(self.rules_data_path))
        self.progression = CharacterProgression(rules_data_path=str(self.rules_data_path))
        self.exporter = CharacterExporter()
        
        # Store LLM service if provided
        self.llm_service = llm_service
        
        # In-memory cache for active characters
        self.character_cache = {}

    def create_character(self, character_data: Dict[str, Any], 
                      concept_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new character with the provided data.
        
        Args:
            character_data: Base character data
            concept_description: Optional description to guide character creation
            
        Returns:
            Dict[str, Any]: Created character data with ID
        """
        # Generate character ID if not provided
        if "id" not in character_data:
            character_data["id"] = str(uuid.uuid4())
        
        # Add creation metadata
        character_data["created_at"] = datetime.datetime.now().isoformat()
        character_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Process concept description with LLM if available
        if concept_description and self.llm_service:
            character_data = self._enhance_character_with_llm(character_data, concept_description)
        
        # Ensure ability scores are set
        if "ability_scores" not in character_data and "class" in character_data:
            # Generate default ability scores optimized for class
            scores = self.ability_scores.generate_ability_scores(method='standard_array')
            character_data["ability_scores"] = self.ability_scores.assign_ability_scores(
                scores, 
                character_data["class"].get("name", ""),
                character_data.get("species", {}).get("name")
            )
        
        # Calculate ability modifiers
        if "ability_scores" in character_data and "ability_modifiers" not in character_data:
            character_data["ability_modifiers"] = self.ability_scores.calculate_ability_modifiers(
                character_data["ability_scores"]
            )
        
        # Calculate hit points if not set
        if "max_hp" not in character_data and "class" in character_data:
            class_type = character_data["class"].get("name", "")
            constitution = character_data.get("ability_scores", {}).get("constitution", 10)
            level = character_data["class"].get("level", 1)
            
            character_data["max_hp"] = self.calculate_hit_points(level, constitution, class_type)
        
        # Set proficiency bonus
        if "proficiency_bonus" not in character_data and "class" in character_data:
            level = character_data["class"].get("level", 1)
            character_data["proficiency_bonus"] = self.calculate_proficiency_bonus(level)
        
        # Validate the character
        validation_result = self.validator.validate_full_character(character_data)
        character_data["validation_result"] = {
            "valid": validation_result["valid"],
            "issues": validation_result.get("issues", []),
            "warnings": validation_result.get("warnings", [])
        }
        
        # Store the character
        self._save_character(character_data)
        
        # Add to cache
        self.character_cache[character_data["id"]] = character_data
        
        return character_data

    def validate_character(self, character_data: Dict[str, Any], 
                        include_narrative_feedback: bool = False) -> Dict[str, Any]:
        """
        Validate character against D&D rules.
        
        Args:
            character_data: Character data to validate
            include_narrative_feedback: Whether to include narrative feedback
            
        Returns:
            Dict[str, Any]: Validation results
        """
        # Use the validator to check the character
        if include_narrative_feedback:
            return self.validator.generate_validation_report(character_data, True)
        else:
            return self.validator.validate_full_character(character_data)

    def calculate_proficiency_bonus(self, level: int, 
                                  include_narrative_context: bool = False) -> Union[int, Dict[str, Any]]:
        """
        Calculate proficiency bonus based on character level.
        
        Args:
            level: Character level
            include_narrative_context: Whether to include narrative explanation
            
        Returns:
            Union[int, Dict[str, Any]]: Proficiency bonus or detailed result with context
        """
        # Calculate the standard proficiency bonus
        proficiency = 2 + ((level - 1) // 4)
        
        if not include_narrative_context:
            return proficiency
        
        # If narrative context requested, provide more details
        result = {
            "proficiency_bonus": proficiency,
            "formula": "2 + (level - 1) ÷ 4",
            "calculation": f"2 + ({level} - 1) ÷ 4 = {proficiency}",
            "level_thresholds": {
                "1-4": 2,
                "5-8": 3,
                "9-12": 4,
                "13-16": 5,
                "17-20": 6
            },
            "narrative_context": (
                f"At level {level}, your character has a +{proficiency} proficiency bonus. "
                f"This reflects your character's growing expertise and is added to ability checks, "
                f"saving throws, and attack rolls for things you're proficient with."
            )
        }
        
        return result

    def calculate_hit_points(self, level: int, constitution: int, class_type: str, 
                          include_tactical_guidance: bool = False) -> Union[int, Dict[str, Any]]:
        """
        Calculate character hit points.
        
        Args:
            level: Character level
            constitution: Constitution score
            class_type: Character class
            include_tactical_guidance: Whether to include tactical advice
            
        Returns:
            Union[int, Dict[str, Any]]: HP value or detailed result with guidance
        """
        # Get constitution modifier
        con_mod = (constitution - 10) // 2
        
        # Get hit die size based on class
        hit_die_sizes = {
            "barbarian": 12,
            "fighter": 10, "paladin": 10, "ranger": 10,
            "bard": 8, "cleric": 8, "druid": 8, "monk": 8, "rogue": 8, "warlock": 8,
            "sorcerer": 6, "wizard": 6
        }
        
        # Default to d8 if class not found
        hit_die = hit_die_sizes.get(class_type.lower(), 8)
        
        # First level gets maximum hit die
        first_level_hp = hit_die + con_mod
        
        # Subsequent levels get average hit die (hit_die/2 + 1) + con_mod
        if level > 1:
            avg_hp_per_level = (hit_die // 2) + 1 + con_mod
            additional_hp = avg_hp_per_level * (level - 1)
            total_hp = first_level_hp + additional_hp
        else:
            total_hp = first_level_hp
        
        # Ensure minimum HP of 1 per level
        total_hp = max(level, total_hp)
        
        if not include_tactical_guidance:
            return total_hp
        
        # If tactical guidance requested, provide more details
        result = {
            "hit_points": total_hp,
            "formula": "First level: max hit die + CON mod; Additional levels: (average hit die + CON mod) per level",
            "calculation": (
                f"Level 1: {hit_die} + {con_mod} = {first_level_hp}; " +
                f"Levels 2-{level}: ({hit_die}/2 + 1 + {con_mod}) × {level-1} = {total_hp - first_level_hp}"
            ),
            "hit_die": f"d{hit_die}",
            "class": class_type,
            "constitution_modifier": con_mod,
            "tactical_guidance": self._generate_hp_tactical_guidance(total_hp, level, class_type)
        }
        
        return result

    def level_up(self, character_id: str, level_up_choices: Dict[str, Any], 
              narrative_milestone: Optional[str] = None, 
              character_goals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle character level advancement.
        
        Args:
            character_id: Character identifier
            level_up_choices: Selected choices for level up
            narrative_milestone: Optional narrative milestone description
            character_goals: Optional character goals and progress
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Get the character
        character_data = self.get_character(character_id)
        if not character_data:
            return {"success": False, "error": f"Character not found: {character_id}"}
        
        # Get current level
        current_level = character_data.get("class", {}).get("level", 1)
        new_level = current_level + 1
        
        # Use the progression manager to handle level up
        level_up_result = self.progression.process_level_up(character_data, new_level)
        
        if not level_up_result.get("success", False):
            return level_up_result
        
        # Apply the selected level up choices
        updated_character = self.progression.apply_level_benefits(
            character_data, 
            new_level, 
            level_up_choices
        )
        
        # Add narrative milestone if provided
        if narrative_milestone:
            if "narrative" not in updated_character:
                updated_character["narrative"] = {}
            
            if "milestones" not in updated_character["narrative"]:
                updated_character["narrative"]["milestones"] = []
            
            updated_character["narrative"]["milestones"].append({
                "level": new_level,
                "description": narrative_milestone,
                "date": datetime.datetime.now().isoformat()
            })
        
        # Add character goals if provided
        if character_goals:
            if "goals" not in updated_character:
                updated_character["goals"] = {}
            
            for goal_key, goal_data in character_goals.items():
                updated_character["goals"][goal_key] = goal_data
        
        # Update last modified timestamp
        updated_character["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save the updated character
        self._save_character(updated_character)
        
        # Update cache
        self.character_cache[character_id] = updated_character
        
        return {
            "success": True,
            "message": f"Successfully leveled up to {new_level}",
            "character": updated_character
        }

    def get_available_options(self, character_id: str, option_type: str, 
                           character_focus: Optional[str] = None, 
                           narrative_direction: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available options for character customization.
        
        Args:
            character_id: Character identifier
            option_type: Type of options to retrieve (e.g., 'feats', 'spells', etc.)
            character_focus: Optional focus area for options
            narrative_direction: Optional narrative direction to guide options
            
        Returns:
            Dict[str, Any]: Available options for the character
        """
        # Get the character
        character_data = self.get_character(character_id)
        if not character_data:
            return {"success": False, "error": f"Character not found: {character_id}"}
        
        result = {
            "success": True,
            "options": [],
            "character_id": character_id,
            "option_type": option_type
        }
        
        # Get basic character info for context
        class_name = character_data.get("class", {}).get("name", "")
        level = character_data.get("class", {}).get("level", 1)
        ability_scores = character_data.get("ability_scores", {})
        
        # Handle different option types
        if option_type == "feats":
            # Get feats based on character's attributes
            result["options"] = self._get_available_feats(character_data, character_focus)
            
        elif option_type == "spells":
            # Get available spells for the character's class and level
            result["options"] = self._get_available_spells(character_data, character_focus)
            
        elif option_type == "skills":
            # Get skill options
            result["options"] = self._get_available_skills(character_data, character_focus)
            
        elif option_type == "equipment":
            # Get equipment options
            result["options"] = self._get_available_equipment(character_data, character_focus)
            
        elif option_type == "abilities":
            # Get class/race abilities
            result["options"] = self._get_available_abilities(character_data, character_focus)
            
        # If narrative direction provided and LLM available, use it to refine options
        if narrative_direction and self.llm_service and result["options"]:
            result["options"] = self._refine_options_with_llm(
                result["options"], 
                option_type, 
                narrative_direction, 
                character_data
            )
        
        return result

    def export_character_sheet(self, character_id: str, format: str = 'json',
                            include_narrative_elements: bool = False,
                            character_portrait_style: Optional[str] = None) -> Dict[str, Any]:
        """
        Export character sheet in requested format.
        
        Args:
            character_id: Character identifier
            format: Output format ('json', 'pdf', 'markdown')
            include_narrative_elements: Whether to include narrative elements
            character_portrait_style: Optional style for character portrait
            
        Returns:
            Dict[str, Any]: Export result with file path or data
        """
        # Get the character
        character_data = self.get_character(character_id)
        if not character_data:
            return {"success": False, "error": f"Character not found: {character_id}"}
        
        # For now, we'll only implement JSON export as per instructions
        if format.lower() == 'json':
            export_result = self.exporter.export_to_json(character_data)
            return export_result
        else:
            return {
                "success": False,
                "error": f"Export format '{format}' is not currently supported. Use 'json' instead."
            }

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve character data by ID.
        
        Args:
            character_id: Character identifier
            
        Returns:
            Optional[Dict[str, Any]]: Character data or None if not found
        """
        # Check cache first
        if character_id in self.character_cache:
            return self.character_cache[character_id]
        
        # Try to load from storage
        character_path = self.storage_path / f"{character_id}.json"
        
        if not character_path.exists():
            return None
        
        try:
            with open(character_path, 'r') as f:
                character_data = json.load(f)
                
            # Add to cache
            self.character_cache[character_id] = character_data
            return character_data
            
        except Exception as e:
            print(f"Error loading character {character_id}: {e}")
            return None

    def update_character(self, character_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply updates to character data.
        
        Args:
            character_id: Character identifier
            updates: Dictionary of updates to apply
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Get the character
        character_data = self.get_character(character_id)
        if not character_data:
            return {"success": False, "error": f"Character not found: {character_id}"}
        
        # Apply updates
        for key, value in updates.items():
            if isinstance(value, dict) and key in character_data and isinstance(character_data[key], dict):
                # Deep update for nested dictionaries
                character_data[key].update(value)
            else:
                # Direct update for other fields
                character_data[key] = value
        
        # Update last modified timestamp
        character_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save the updated character
        self._save_character(character_data)
        
        # Update cache
        self.character_cache[character_id] = character_data
        
        return {
            "success": True,
            "message": "Character updated successfully",
            "character": character_data
        }

    def refine_character_concept(self, character_id: str, concept_updates: Dict[str, Any], 
                              narrative_direction: Optional[str] = None) -> Dict[str, Any]:
        """
        Refine character concept with LLM assistance.
        
        Args:
            character_id: Character identifier
            concept_updates: Updates to the character concept
            narrative_direction: Optional narrative direction for refinement
            
        Returns:
            Dict[str, Any]: Updated character data with refined concept
        """
        # Check if LLM service is available
        if not self.llm_service:
            return {
                "success": False, 
                "error": "LLM service not available for character concept refinement"
            }
        
        # Get the character
        character_data = self.get_character(character_id)
        if not character_data:
            return {"success": False, "error": f"Character not found: {character_id}"}
        
        # Create a refined concept request for the LLM
        concept_prompt = self._create_concept_refinement_prompt(character_data, concept_updates, narrative_direction)
        
        # Get LLM response
        try:
            llm_response = self.llm_service.generate_response(concept_prompt)
            refined_concept = self._parse_llm_concept_response(llm_response)
            
            # Apply the refined concept to the character
            updated_character = character_data.copy()
            updated_character.update(refined_concept)
            
            # Update last modified timestamp
            updated_character["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save the updated character
            self._save_character(updated_character)
            
            # Update cache
            self.character_cache[character_id] = updated_character
            
            return {
                "success": True,
                "message": "Character concept refined successfully",
                "character": updated_character
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error refining character concept: {str(e)}"
            }

    def resolve_character_conflicts(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflicts in character data.
        
        Args:
            character_data: Character data with potential conflicts
            
        Returns:
            Dict[str, Any]: Character data with conflicts resolved
        """
        # Create a copy to avoid modifying the original
        resolved_data = character_data.copy()
        conflicts = []
        
        # Check for class-species conflicts (e.g., racial restrictions in some campaigns)
        class_name = resolved_data.get("class", {}).get("name", "").lower()
        species_name = resolved_data.get("species", {}).get("name", "").lower()
        
        # Add ability score conflicts
        if "ability_scores" in resolved_data:
            ability_scores = resolved_data["ability_scores"]
            class_name = resolved_data.get("class", {}).get("name", "")
            
            if class_name:
                # Check if primary ability is below 13
                primary_ability = self._get_class_primary_ability(class_name)
                if primary_ability and primary_ability in ability_scores:
                    if ability_scores[primary_ability] < 13:
                        conflicts.append(f"Low {primary_ability} score for {class_name}")
                        # Auto-fix by ensuring minimum 13
                        resolved_data["ability_scores"][primary_ability] = max(13, ability_scores[primary_ability])
        
        # Check for conflicts between background and class (just an example)
        background = resolved_data.get("background", {}).get("name", "").lower()
        if background == "acolyte" and class_name == "barbarian":
            conflicts.append("Unusual combination of religious acolyte background with barbarian class")
        
        # Check for equipment conflicts (e.g., wearing armor spellcasters can't use)
        if "equipment" in resolved_data and "class" in resolved_data:
            armor_items = resolved_data.get("equipment", {}).get("armor", [])
            if class_name in ["wizard", "sorcerer"] and any(item.get("type") == "heavy" for item in armor_items):
                conflicts.append(f"{class_name} cannot use heavy armor")
                # Auto-fix by removing heavy armor
                resolved_data["equipment"]["armor"] = [
                    item for item in armor_items if item.get("type") != "heavy"
                ]
        
        # Add resolution information
        if conflicts:
            if "conflicts" not in resolved_data:
                resolved_data["conflicts"] = {}
            
            resolved_data["conflicts"]["resolved"] = conflicts
            resolved_data["conflicts"]["resolution_date"] = datetime.datetime.now().isoformat()
        
        return resolved_data

    def _save_character(self, character_data: Dict[str, Any]) -> None:
        """Save character data to file."""
        character_id = character_data.get("id")
        if not character_id:
            raise ValueError("Character data missing ID")
        
        character_path = self.storage_path / f"{character_id}.json"
        
        with open(character_path, 'w') as f:
            json.dump(character_data, f, indent=2)

    def _enhance_character_with_llm(self, character_data: Dict[str, Any], 
                                 concept_description: str) -> Dict[str, Any]:
        """Use LLM to enhance character based on concept description."""
        if not self.llm_service:
            return character_data
        
        try:
            # Create a prompt for the LLM
            prompt = (
                f"Create a D&D character based on this concept: {concept_description}\n\n"
                f"Current character data: {json.dumps(character_data, indent=2)}\n\n"
                "Please enhance this character data while preserving existing selections. "
                "Provide personality traits, background details, and character motivation."
            )
            
            # Get LLM response
            response = self.llm_service.generate_response(prompt)
            
            # Parse the response - this would need to be implemented based on LLM output format
            enhanced_data = self._parse_llm_character_response(response, character_data)
            
            return enhanced_data
            
        except Exception as e:
            print(f"Error enhancing character with LLM: {e}")
            return character_data

    def _parse_llm_character_response(self, llm_response: str, 
                                   base_character: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into character data structure."""
        # This is a placeholder - actual implementation would depend on LLM response format
        # In a real implementation, this would parse structured data from the LLM response
        
        # For now, just return the base character with a note about the LLM enhancement
        enhanced_character = base_character.copy()
        
        if "notes" not in enhanced_character:
            enhanced_character["notes"] = []
        
        enhanced_character["notes"].append({
            "type": "llm_enhancement",
            "content": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
            "date": datetime.datetime.now().isoformat()
        })
        
        return enhanced_character

    def _get_available_feats(self, character_data: Dict[str, Any], 
                          focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get feats available to the character."""
        # This would be implemented to fetch feats from rules data
        # For now, return placeholder data
        return [
            {"id": "alert", "name": "Alert", "description": "You are never surprised"},
            {"id": "tough", "name": "Tough", "description": "Gain +2 hit points per level"}
        ]

    def _get_available_spells(self, character_data: Dict[str, Any], 
                           focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get spells available to the character."""
        # This would be implemented to fetch spells from rules data
        # For now, return placeholder data
        return [
            {"id": "fireball", "name": "Fireball", "level": 3, "school": "evocation"},
            {"id": "cure_wounds", "name": "Cure Wounds", "level": 1, "school": "evocation"}
        ]

    def _get_available_skills(self, character_data: Dict[str, Any], 
                           focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get skills available to the character."""
        # This would be implemented to fetch skills from rules data
        # For now, return placeholder data
        return [
            {"id": "acrobatics", "name": "Acrobatics", "ability": "dexterity"},
            {"id": "arcana", "name": "Arcana", "ability": "intelligence"}
        ]

    def _get_available_equipment(self, character_data: Dict[str, Any], 
                              focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get equipment available to the character."""
        # This would be implemented to fetch equipment from rules data
        # For now, return placeholder data
        return [
            {"id": "longsword", "name": "Longsword", "type": "weapon", "damage": "1d8"},
            {"id": "chain_mail", "name": "Chain Mail", "type": "armor", "ac": 16}
        ]

    def _get_available_abilities(self, character_data: Dict[str, Any], 
                              focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get class and race abilities available to the character."""
        # This would be implemented to fetch abilities from rules data
        # For now, return placeholder data
        return [
            {"id": "rage", "name": "Rage", "type": "class", "class": "barbarian"},
            {"id": "darkvision", "name": "Darkvision", "type": "species", "species": "elf"}
        ]

    def _refine_options_with_llm(self, options: List[Dict[str, Any]], option_type: str,
                              narrative: str, character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to refine options based on narrative direction."""
        if not self.llm_service:
            return options
        
        try:
            # Create a prompt for the LLM
            character_summary = self._create_character_summary(character_data)
            
            prompt = (
                f"Character summary: {character_summary}\n\n"
                f"Narrative direction: {narrative}\n\n"
                f"Available {option_type}:\n{json.dumps(options, indent=2)}\n\n"
                f"Please rank these {option_type} based on how well they fit the character concept "
                f"and narrative direction. Add a brief explanation for each option."
            )
            
            # Get LLM response
            response = self.llm_service.generate_response(prompt)
            
            # Parse the response - this would need to be implemented based on LLM output format
            refined_options = self._parse_llm_options_response(response, options)
            
            return refined_options
            
        except Exception as e:
            print(f"Error refining options with LLM: {e}")
            return options

    def _create_character_summary(self, character_data: Dict[str, Any]) -> str:
        """Create a brief summary of the character for LLM context."""
        name = character_data.get("name", "Unnamed character")
        species = character_data.get("species", {}).get("name", "Unknown species")
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        level = character_data.get("class", {}).get("level", 1)
        
        return f"{name}, a level {level} {species} {class_name}"

    def _parse_llm_options_response(self, llm_response: str, 
                                 original_options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse LLM response about options."""
        # This is a placeholder - actual implementation would depend on LLM response format
        # For now, just return the original options with a note
        
        enhanced_options = []
        
        for option in original_options:
            enhanced_option = option.copy()
            enhanced_option["llm_commentary"] = f"LLM suggests this may be appropriate for your character."
            enhanced_options.append(enhanced_option)
        
        return enhanced_options

    def _create_concept_refinement_prompt(self, character_data: Dict[str, Any], 
                                       concept_updates: Dict[str, Any],
                                       narrative_direction: Optional[str]) -> str:
        """Create prompt for LLM concept refinement."""
        character_summary = self._create_character_summary(character_data)
        
        prompt = (
            f"Character summary: {character_summary}\n\n"
            f"Current character details: {json.dumps(character_data, indent=2)}\n\n"
            f"Requested concept updates: {json.dumps(concept_updates, indent=2)}\n\n"
        )
        
        if narrative_direction:
            prompt += f"Narrative direction: {narrative_direction}\n\n"
        
        prompt += (
            "Please refine this character concept based on the requested updates, "
            "maintaining coherence with existing traits and abilities. "
            "Provide updated character data in structured format with personality, "
            "motivation, and background elements."
        )
        
        return prompt

    def _parse_llm_concept_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM concept refinement response."""
        # This is a placeholder - actual implementation would depend on LLM response format
        # In a real implementation, this would extract structured data from the response
        
        # For now, just create a simple structure with the response
        return {
            "concept": {
                "refinement": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
                "generated_at": datetime.datetime.now().isoformat()
            }
        }

    def _generate_hp_tactical_guidance(self, hp: int, level: int, class_type: str) -> str:
        """Generate tactical guidance based on character HP."""
        class_role = {
            "barbarian": "tank",
            "fighter": "frontliner",
            "paladin": "frontliner",
            "wizard": "backline",
            "sorcerer": "backline",
            "rogue": "skirmisher"
        }.get(class_type.lower(), "balanced")
        
        avg_hp_by_level = {
            "tank": level * 10,
            "frontliner": level * 8,
            "balanced": level * 7,
            "skirmisher": level * 6,
            "backline": level * 5
        }
        
        expected_hp = avg_hp_by_level.get(class_role, level * 7)
        
        if hp >= expected_hp * 1.2:
            return (
                f"With {hp} hit points, you're exceptionally durable for a level {level} {class_type}. "
                f"You can confidently take on frontline positions in combat and absorb significant damage."
            )
        elif hp >= expected_hp:
            return (
                f"With {hp} hit points, you have good durability for a level {level} {class_type}. "
                f"You can fulfill your expected role in combat without undue risk."
            )
        elif hp >= expected_hp * 0.8:
            return (
                f"With {hp} hit points, you're slightly below average durability for a level {level} {class_type}. "
                f"Consider playing a bit more cautiously, especially in your first few encounters."
            )
        else:
            return (
                f"With {hp} hit points, you're quite fragile for a level {level} {class_type}. "
                f"Prioritize positioning and avoid direct confrontation where possible. "
                f"Consider asking your party's healer to keep a close eye on you."
            )

    def _get_class_primary_ability(self, class_name: str) -> Optional[str]:
        """Get primary ability for a class."""
        primary_abilities = {
            "barbarian": "strength",
            "bard": "charisma",
            "cleric": "wisdom",
            "druid": "wisdom",
            "fighter": "strength",
            "monk": "dexterity",
            "paladin": "strength",
            "ranger": "dexterity",
            "rogue": "dexterity",
            "sorcerer": "charisma",
            "warlock": "charisma",
            "wizard": "intelligence"
        }
        
        return primary_abilities.get(class_name.lower())