"""
Character Creator Module

Handles the step-by-step process of character creation, from concept to completed character sheet.
Coordinates with other character-related classes to create a complete D&D character.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import uuid
import json
import datetime
from pathlib import Path

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object

from backend.core.character.ability_scores import AbilityScores
from backend.core.character.character_validator import CharacterValidator
from backend.core.character.llm_character_advisor import LLMCharacterAdvisor
from backend.core.services.ollama_service import OllamaService
from backend.data.character_repository import CharacterRepository


class CharacterCreator(AbstractCharacterClass):
    """
    Handles the step-by-step character creation process for D&D characters.
    
    This class manages the workflow of character creation, from initial concept through
    all selections (species, class, background, abilities, skills, equipment, spells)
    to a finalized character sheet. It coordinates with other specialized classes
    to ensure all aspects of character creation are properly handled.
    """

    def __init__(self, llm_service=None, character_repository=None):
        """
        Initialize the character creator with optional services.
        
        Args:
            llm_service: Optional LLM service for AI assistance
            character_repository: Optional repository for character storage
        """
        self.llm_service = llm_service or OllamaService()
        self.character_repository = character_repository or CharacterRepository()
        
        # Initialize helper classes
        self.ability_scores_manager = AbilityScores()
        self.character_validator = CharacterValidator()
        self.llm_advisor = LLMCharacterAdvisor(self.llm_service)
        
        # Template for a new character
        self.character_template = {
            "id": None,
            "name": None,
            "concept": None,
            "created_at": None,
            "updated_at": None,
            "species": {
                "name": None,
                "subrace": None,
                "traits": [],
                "ability_bonuses": {}
            },
            "class": {
                "name": None,
                "subclass": None,
                "level": 1,
                "hit_dice": None,
                "features": []
            },
            "background": {
                "name": None,
                "traits": [],
                "proficiencies": [],
                "equipment": []
            },
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "ability_modifiers": {
                "strength": 0,
                "dexterity": 0,
                "constitution": 0,
                "intelligence": 0,
                "wisdom": 0,
                "charisma": 0
            },
            "proficiency_bonus": 2,
            "saving_throws": [],
            "skills": {
                "proficient": [],
                "expertise": []
            },
            "equipment": {
                "weapons": [],
                "armor": [],
                "gear": [],
                "treasure": {
                    "gp": 0,
                    "sp": 0,
                    "cp": 0
                }
            },
            "spellcasting": {
                "ability": None,
                "spell_save_dc": None,
                "spell_attack_bonus": None,
                "cantrips_known": [],
                "spells_known": [],
                "spell_slots": {}
            },
            "proficiencies": {
                "languages": [],
                "weapons": [],
                "armor": [],
                "tools": []
            },
            "personality": {
                "traits": [],
                "ideals": [],
                "bonds": [],
                "flaws": []
            },
            "backstory": None,
            "notes": "",
            "creation_status": "initialized"
        }
        
        # Rules data paths
        self.data_dir = Path("backend/data/rules")
        self._load_rules_data()
        
        # Cache for active characters being created
        self.active_characters = {}

    def _load_rules_data(self):
        """Load rules data from JSON files."""
        try:
            # Load species data
            with open(self.data_dir / "species.json", "r") as f:
                self.species_data = json.load(f)
                
            # Load class data
            with open(self.data_dir / "classes.json", "r") as f:
                self.class_data = json.load(f)
                
            # Load background data
            with open(self.data_dir / "backgrounds.json", "r") as f:
                self.background_data = json.load(f)
                
            # Load skills data
            with open(self.data_dir / "skills.json", "r") as f:
                self.skills_data = json.load(f)
                
            # Load equipment data
            with open(self.data_dir / "equipment.json", "r") as f:
                self.equipment_data = json.load(f)
                
            # Load spells data
            with open(self.data_dir / "spells.json", "r") as f:
                self.spells_data = json.load(f)
        
        except FileNotFoundError as e:
            print(f"Warning: Could not load rules data: {e}")
            # Initialize with empty data as fallback
            self.species_data = {}
            self.class_data = {}
            self.background_data = {}
            self.skills_data = {}
            self.equipment_data = {}
            self.spells_data = {}

    def initialize_character(self, name: str = None, concept_description: str = None) -> str:
        """
        Start the character creation process by initializing a new character.
        
        Args:
            name: Optional character name
            concept_description: Optional character concept description
            
        Returns:
            str: The newly generated character ID
        """
        # Generate a unique ID for the character
        character_id = str(uuid.uuid4())
        
        # Create a new character based on the template
        character = self.character_template.copy()
        character["id"] = character_id
        character["name"] = name
        character["concept"] = concept_description
        
        # Set creation timestamps
        current_time = datetime.datetime.now().isoformat()
        character["created_at"] = current_time
        character["updated_at"] = current_time
        
        # If a concept was provided, use the LLM to suggest character elements
        if concept_description:
            suggestions = self.llm_advisor.generate_character_concept(concept_description)
            
            # Add suggestions to the character data
            character["concept_suggestions"] = suggestions
        
        # Store the character in the active characters cache
        self.active_characters[character_id] = character
        
        # Save to repository
        self.character_repository.save_character(character)
        
        return character_id

    def select_species(self, character_id: str, species: str, subrace: str = None) -> Dict[str, Any]:
        """
        Select a character's species (race) and optional subrace.
        
        Args:
            character_id: The character's unique identifier
            species: The chosen species/race name
            subrace: Optional subrace name
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Normalize species name for lookup
        species_key = species.lower().replace(" ", "_")
        
        # Verify the species exists in the data
        if species_key not in self.species_data:
            return {"error": f"Species '{species}' not found in available data"}
        
        # Get species data
        species_info = self.species_data[species_key]
        
        # Update character data with species information
        character["species"]["name"] = species
        character["species"]["traits"] = species_info.get("traits", [])
        character["species"]["ability_bonuses"] = species_info.get("ability_bonuses", {})
        
        # Handle subrace if provided
        if subrace:
            subrace_key = subrace.lower().replace(" ", "_")
            subraces = species_info.get("subraces", {})
            
            if subrace_key not in subraces:
                return {"error": f"Subrace '{subrace}' not found for species '{species}'"}
            
            # Get subrace data
            subrace_info = subraces[subrace_key]
            
            # Update character with subrace information
            character["species"]["subrace"] = subrace
            
            # Add subrace traits
            character["species"]["traits"].extend(subrace_info.get("traits", []))
            
            # Add subrace ability bonuses (combine with species bonuses)
            subrace_bonuses = subrace_info.get("ability_bonuses", {})
            for ability, bonus in subrace_bonuses.items():
                if ability in character["species"]["ability_bonuses"]:
                    character["species"]["ability_bonuses"][ability] += bonus
                else:
                    character["species"]["ability_bonuses"][ability] = bonus
        
        # Update creation status
        character["creation_status"] = "species_selected"
        
        # Add species proficiencies
        for language in species_info.get("languages", []):
            if language not in character["proficiencies"]["languages"]:
                character["proficiencies"]["languages"].append(language)
        
        # Apply ability score bonuses
        for ability, bonus in character["species"]["ability_bonuses"].items():
            if ability in character["ability_scores"]:
                character["ability_scores"][ability] += bonus
        
        # Recalculate ability modifiers
        character["ability_modifiers"] = self.ability_scores_manager.calculate_ability_modifiers(
            character["ability_scores"]
        )
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def select_class(self, character_id: str, class_name: str, subclass: str = None) -> Dict[str, Any]:
        """
        Select a character's class and optional subclass.
        
        Args:
            character_id: The character's unique identifier
            class_name: The chosen class name
            subclass: Optional subclass name
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Normalize class name for lookup
        class_key = class_name.lower().replace(" ", "_")
        
        # Verify the class exists in the data
        if class_key not in self.class_data:
            return {"error": f"Class '{class_name}' not found in available data"}
        
        # Get class data
        class_info = self.class_data[class_key]
        
        # Update character data with class information
        character["class"]["name"] = class_name
        character["class"]["hit_dice"] = class_info.get("hit_dice", "d8")
        character["class"]["level"] = 1
        
        # Add 1st level class features
        level_1_features = class_info.get("features", {}).get("1", [])
        character["class"]["features"] = level_1_features
        
        # Handle subclass if provided and if valid for level 1
        subclass_level = class_info.get("subclass_level", 3)
        if subclass and subclass_level == 1:
            subclass_key = subclass.lower().replace(" ", "_")
            subclasses = class_info.get("subclasses", {})
            
            if subclass_key not in subclasses:
                return {"error": f"Subclass '{subclass}' not found for class '{class_name}'"}
            
            # Get subclass data
            subclass_info = subclasses[subclass_key]
            
            # Update character with subclass information
            character["class"]["subclass"] = subclass
            
            # Add subclass features
            subclass_features = subclass_info.get("features", {}).get("1", [])
            character["class"]["features"].extend(subclass_features)
        
        # Update proficiency information
        # Saving throws
        character["saving_throws"] = class_info.get("saving_throws", [])
        
        # Weapon proficiencies
        for weapon_prof in class_info.get("proficiencies", {}).get("weapons", []):
            if weapon_prof not in character["proficiencies"]["weapons"]:
                character["proficiencies"]["weapons"].append(weapon_prof)
        
        # Armor proficiencies
        for armor_prof in class_info.get("proficiencies", {}).get("armor", []):
            if armor_prof not in character["proficiencies"]["armor"]:
                character["proficiencies"]["armor"].append(armor_prof)
        
        # Tool proficiencies
        for tool_prof in class_info.get("proficiencies", {}).get("tools", []):
            if tool_prof not in character["proficiencies"]["tools"]:
                character["proficiencies"]["tools"].append(tool_prof)
        
        # Update spellcasting information if the class can cast spells
        if "spellcasting" in class_info:
            spellcasting_info = class_info["spellcasting"]
            character["spellcasting"]["ability"] = spellcasting_info.get("ability")
            
            # Calculate spell save DC and attack bonus
            if character["spellcasting"]["ability"]:
                ability = character["spellcasting"]["ability"].lower()
                ability_mod = character["ability_modifiers"].get(ability, 0)
                character["spellcasting"]["spell_save_dc"] = 8 + character["proficiency_bonus"] + ability_mod
                character["spellcasting"]["spell_attack_bonus"] = character["proficiency_bonus"] + ability_mod
            
            # Set up spell slots for level 1
            spell_slots = spellcasting_info.get("spell_slots", {}).get("1", {})
            character["spellcasting"]["spell_slots"] = spell_slots
        
        # Update creation status
        character["creation_status"] = "class_selected"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        # Calculate hit points (max at level 1)
        hit_dice = character["class"]["hit_dice"]
        hit_dice_value = int(hit_dice.replace("d", ""))
        con_mod = character["ability_modifiers"]["constitution"]
        character["max_hp"] = hit_dice_value + con_mod
        character["current_hp"] = character["max_hp"]
        
        return character

    def select_background(self, character_id: str, background: str) -> Dict[str, Any]:
        """
        Select a character's background.
        
        Args:
            character_id: The character's unique identifier
            background: The chosen background name
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Normalize background name for lookup
        background_key = background.lower().replace(" ", "_")
        
        # Verify the background exists in the data
        if background_key not in self.background_data:
            return {"error": f"Background '{background}' not found in available data"}
        
        # Get background data
        background_info = self.background_data[background_key]
        
        # Update character data with background information
        character["background"]["name"] = background
        character["background"]["traits"] = background_info.get("traits", [])
        
        # Add personality elements
        if "personality" in background_info:
            personality = background_info["personality"]
            
            # Select default options or first in list
            if personality.get("traits"):
                character["personality"]["traits"] = personality["traits"][:2]
            
            if personality.get("ideals"):
                character["personality"]["ideals"] = [personality["ideals"][0]]
            
            if personality.get("bonds"):
                character["personality"]["bonds"] = [personality["bonds"][0]]
            
            if personality.get("flaws"):
                character["personality"]["flaws"] = [personality["flaws"][0]]
        
        # Add background proficiencies
        # Skill proficiencies
        for skill in background_info.get("proficiencies", {}).get("skills", []):
            if skill not in character["skills"]["proficient"]:
                character["skills"]["proficient"].append(skill)
        
        # Tool proficiencies
        for tool in background_info.get("proficiencies", {}).get("tools", []):
            if tool not in character["proficiencies"]["tools"]:
                character["proficiencies"]["tools"].append(tool)
        
        # Language proficiencies
        for language in background_info.get("proficiencies", {}).get("languages", []):
            if language not in character["proficiencies"]["languages"]:
                character["proficiencies"]["languages"].append(language)
        
        # Add background equipment
        bg_equipment = background_info.get("equipment", [])
        for item in bg_equipment:
            if item.get("type") == "weapon":
                character["equipment"]["weapons"].append(item)
            elif item.get("type") == "armor":
                character["equipment"]["armor"].append(item)
            else:
                character["equipment"]["gear"].append(item)
        
        # Add starting gold
        if "starting_gold" in background_info:
            for coin, amount in background_info["starting_gold"].items():
                character["equipment"]["treasure"][coin] += amount
        
        # Update creation status
        character["creation_status"] = "background_selected"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def set_ability_scores(self, character_id: str, ability_scores: Dict[str, int], 
                         method: str = None) -> Dict[str, Any]:
        """
        Set a character's ability scores.
        
        Args:
            character_id: The character's unique identifier
            ability_scores: Dictionary of ability scores
            method: Method used to generate scores (standard_array, point_buy, rolled)
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Validate the ability scores
        valid_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in valid_abilities:
            if ability not in ability_scores:
                return {"error": f"Missing required ability score: {ability}"}
            
            if not isinstance(ability_scores[ability], int) or ability_scores[ability] < 3 or ability_scores[ability] > 20:
                return {"error": f"Invalid value for {ability}: must be an integer between 3-20"}
        
        # Store the generation method if provided
        if method:
            character["ability_scores_method"] = method
        
        # Backup original scores before race bonuses, if this is initial assignment
        if "base_ability_scores" not in character:
            character["base_ability_scores"] = ability_scores.copy()
            
            # Apply species bonuses to the actual scores
            for ability, bonus in character["species"].get("ability_bonuses", {}).items():
                if ability in ability_scores:
                    ability_scores[ability] += bonus
        
        # Update ability scores
        character["ability_scores"] = ability_scores
        
        # Calculate ability modifiers
        character["ability_modifiers"] = self.ability_scores_manager.calculate_ability_modifiers(ability_scores)
        
        # Update spellcasting DCs and attack bonuses if applicable
        if character["spellcasting"]["ability"]:
            ability = character["spellcasting"]["ability"].lower()
            ability_mod = character["ability_modifiers"].get(ability, 0)
            character["spellcasting"]["spell_save_dc"] = 8 + character["proficiency_bonus"] + ability_mod
            character["spellcasting"]["spell_attack_bonus"] = character["proficiency_bonus"] + ability_mod
        
        # Recalculate HP if constitution changed
        if "class" in character and character["class"]["name"]:
            hit_dice = character["class"]["hit_dice"]
            hit_dice_value = int(hit_dice.replace("d", ""))
            con_mod = character["ability_modifiers"]["constitution"]
            character["max_hp"] = hit_dice_value + con_mod
            character["current_hp"] = character["max_hp"]
        
        # Update creation status
        character["creation_status"] = "ability_scores_set"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def select_skills(self, character_id: str, skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Select a character's skills.
        
        Args:
            character_id: The character's unique identifier
            skills: Dictionary with 'proficient' and optional 'expertise' lists
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Get class data to verify available skill choices
        class_key = character["class"]["name"].lower().replace(" ", "_") if character["class"]["name"] else None
        if not class_key or class_key not in self.class_data:
            return {"error": "Class must be selected before choosing skills"}
        
        class_info = self.class_data[class_key]
        available_skills = class_info.get("skills", {}).get("choose_from", [])
        num_skills = class_info.get("skills", {}).get("count", 2)
        
        # Get background skills that were already added
        background_skills = []
        if character["background"]["name"]:
            bg_key = character["background"]["name"].lower().replace(" ", "_")
            if bg_key in self.background_data:
                bg_info = self.background_data[bg_key]
                background_skills = bg_info.get("proficiencies", {}).get("skills", [])
        
        # Validate skill selections
        proficient_skills = skills.get("proficient", [])
        expertise_skills = skills.get("expertise", [])
        
        # Check if the selected skills are valid for the class
        class_skill_count = 0
        for skill in proficient_skills:
            if skill in background_skills:
                continue  # Skip counting skills already granted by background
                
            if skill not in available_skills:
                return {"error": f"Skill '{skill}' is not available for {character['class']['name']}"}
                
            class_skill_count += 1
        
        # Check if the correct number of skills were selected
        if class_skill_count > num_skills:
            return {"error": f"{character['class']['name']} can only choose {num_skills} skills"}
        
        # Update skill proficiencies
        # First, keep background skills
        character["skills"]["proficient"] = background_skills.copy()
        
        # Add selected class skills (avoiding duplicates)
        for skill in proficient_skills:
            if skill not in character["skills"]["proficient"]:
                character["skills"]["proficient"].append(skill)
        
        # Update expertise if provided
        if expertise_skills:
            # Validate expertise (must be proficient first)
            for skill in expertise_skills:
                if skill not in character["skills"]["proficient"]:
                    return {"error": f"Cannot have expertise in '{skill}' without proficiency"}
            
            character["skills"]["expertise"] = expertise_skills
        
        # Update creation status
        character["creation_status"] = "skills_selected"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def select_equipment(self, character_id: str, equipment_choices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select a character's starting equipment.
        
        Args:
            character_id: The character's unique identifier
            equipment_choices: Dictionary of equipment choices
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Validate class is selected
        if not character["class"]["name"]:
            return {"error": "Class must be selected before choosing equipment"}
        
        # Get class equipment options
        class_key = character["class"]["name"].lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        
        # Process selected weapons
        if "weapons" in equipment_choices:
            for weapon in equipment_choices["weapons"]:
                # Validate weapon exists in data
                weapon_id = weapon.get("id")
                if not self._validate_equipment_item("weapon", weapon_id):
                    return {"error": f"Invalid weapon: {weapon_id}"}
                
                # Add weapon to character
                character["equipment"]["weapons"].append(weapon)
        
        # Process selected armor
        if "armor" in equipment_choices:
            for armor in equipment_choices["armor"]:
                # Validate armor exists in data
                armor_id = armor.get("id")
                if not self._validate_equipment_item("armor", armor_id):
                    return {"error": f"Invalid armor: {armor_id}"}
                
                # Add armor to character
                character["equipment"]["armor"].append(armor)
        
        # Process selected gear
        if "gear" in equipment_choices:
            for gear in equipment_choices["gear"]:
                # Validate gear exists in data
                gear_id = gear.get("id")
                if not self._validate_equipment_item("gear", gear_id):
                    return {"error": f"Invalid gear: {gear_id}"}
                
                # Add gear to character
                character["equipment"]["gear"].append(gear)
        
        # Process pack choices
        if "pack" in equipment_choices:
            pack_id = equipment_choices["pack"]
            pack_contents = self._get_pack_contents(pack_id)
            
            if not pack_contents:
                return {"error": f"Invalid equipment pack: {pack_id}"}
            
            # Add pack contents to gear
            for item in pack_contents:
                character["equipment"]["gear"].append(item)
        
        # Process additional gold
        if "gold" in equipment_choices:
            character["equipment"]["treasure"]["gp"] += equipment_choices["gold"]
        
        # Update creation status
        character["creation_status"] = "equipment_selected"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def select_spells(self, character_id: str, spell_choices: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Select a character's spells if they are a spellcaster.
        
        Args:
            character_id: The character's unique identifier
            spell_choices: Dictionary with 'cantrips' and 'spells' lists
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Check if the character is a spellcaster
        if not character["spellcasting"]["ability"]:
            return {"error": "This character cannot cast spells"}
        
        # Get class data for spell information
        class_key = character["class"]["name"].lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        spellcasting_info = class_info.get("spellcasting", {})
        
        # Get number of cantrips and spells allowed
        cantrips_allowed = spellcasting_info.get("cantrips_known", {}).get("1", 0)
        
        # For prepared spellcasters vs. known spellcasters
        spells_prepared = False
        if "prepared" in spellcasting_info:
            spellcasting_ability = character["spellcasting"]["ability"].lower()
            ability_mod = character["ability_modifiers"][spellcasting_ability]
            spells_allowed = ability_mod + character["class"]["level"]
            if spells_allowed < 1:
                spells_allowed = 1
            spells_prepared = True
        else:
            spells_allowed = spellcasting_info.get("spells_known", {}).get("1", 0)
        
        # Validate the spell selections
        cantrips_selected = spell_choices.get("cantrips", [])
        spells_selected = spell_choices.get("spells", [])
        
        # Check cantrip count
        if len(cantrips_selected) > cantrips_allowed:
            return {"error": f"Too many cantrips selected. Maximum allowed: {cantrips_allowed}"}
        
        # Check spell count
        if len(spells_selected) > spells_allowed:
            return {"error": f"Too many spells selected. Maximum allowed: {spells_allowed}"}
        
        # Validate each cantrip
        for cantrip in cantrips_selected:
            if not self._validate_spell(cantrip, 0, class_key):
                return {"error": f"Invalid cantrip: {cantrip}"}
        
        # Validate each spell
        for spell in spells_selected:
            if not self._validate_spell(spell, 1, class_key):
                return {"error": f"Invalid spell: {spell}"}
        
        # Update character's spells
        character["spellcasting"]["cantrips_known"] = cantrips_selected
        
        if spells_prepared:
            character["spellcasting"]["spells_prepared"] = spells_selected
        else:
            character["spellcasting"]["spells_known"] = spells_selected
        
        # Update creation status
        character["creation_status"] = "spells_selected"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        return character

    def finalize_character(self, character_id: str, additional_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete character creation with additional details and final validation.
        
        Args:
            character_id: The character's unique identifier
            additional_details: Optional additional character details
            
        Returns:
            Dict[str, Any]: Finalized character data
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Validate that required elements are selected
        if not character["species"]["name"]:
            return {"error": "Species must be selected to finalize character"}
        
        if not character["class"]["name"]:
            return {"error": "Class must be selected to finalize character"}
        
        if not character["background"]["name"]:
            return {"error": "Background must be selected to finalize character"}
        
        # Add additional details if provided
        if additional_details:
            # Character name
            if "name" in additional_details:
                character["name"] = additional_details["name"]
            
            # Physical characteristics
            if "appearance" in additional_details:
                character["appearance"] = additional_details["appearance"]
            
            # Character backstory
            if "backstory" in additional_details:
                character["backstory"] = additional_details["backstory"]
            
            # Personality
            if "personality" in additional_details:
                for trait_type, traits in additional_details["personality"].items():
                    if trait_type in character["personality"]:
                        character["personality"][trait_type] = traits
            
            # Additional notes
            if "notes" in additional_details:
                character["notes"] = additional_details["notes"]
        
        # Perform final validation
        validation_result = self.character_validator.validate_full_character(character)
        
        if not validation_result["valid"]:
            # Return validation errors but don't block finalization
            character["validation_issues"] = validation_result["issues"]
        
        # Update creation status
        character["creation_status"] = "complete"
        
        # Update the stored character data
        self.active_characters[character_id] = character
        self.character_repository.save_character(character)
        
        # Remove from active characters cache after finalization
        if character_id in self.active_characters:
            del self.active_characters[character_id]
        
        return character

    def get_available_species(self) -> Dict[str, Any]:
        """Get list of available species/races."""
        return {
            "species": [
                {
                    "name": species_data.get("name", key),
                    "id": key,
                    "description": species_data.get("description", ""),
                    "has_subraces": bool(species_data.get("subraces"))
                }
                for key, species_data in self.species_data.items()
            ]
        }
    
    def get_available_classes(self) -> Dict[str, Any]:
        """Get list of available classes."""
        return {
            "classes": [
                {
                    "name": class_data.get("name", key),
                    "id": key,
                    "description": class_data.get("description", ""),
                    "primary_ability": class_data.get("primary_ability", "")
                }
                for key, class_data in self.class_data.items()
            ]
        }
    
    def get_available_backgrounds(self) -> Dict[str, Any]:
        """Get list of available backgrounds."""
        return {
            "backgrounds": [
                {
                    "name": bg_data.get("name", key),
                    "id": key,
                    "description": bg_data.get("description", "")
                }
                for key, bg_data in self.background_data.items()
            ]
        }
    
    def get_class_skill_options(self, character_id: str) -> Dict[str, Any]:
        """
        Get available skill options for the character's class.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Dict[str, Any]: Available skills and how many can be selected
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Check if class is selected
        if not character["class"]["name"]:
            return {"error": "Class must be selected first"}
            
        # Get class data
        class_key = character["class"]["name"].lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        
        # Get skill options
        available_skills = class_info.get("skills", {}).get("choose_from", [])
        num_skills = class_info.get("skills", {}).get("count", 2)
        
        # Get background skills that were already added
        background_skills = []
        if character["background"]["name"]:
            bg_key = character["background"]["name"].lower().replace(" ", "_")
            if bg_key in self.background_data:
                bg_info = self.background_data[bg_key]
                background_skills = bg_info.get("proficiencies", {}).get("skills", [])
        
        return {
            "available_skills": available_skills,
            "skills_to_choose": num_skills,
            "background_skills": background_skills
        }
    
    def get_class_equipment_options(self, character_id: str) -> Dict[str, Any]:
        """
        Get available starting equipment options for the character's class.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Dict[str, Any]: Available equipment options
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Check if class is selected
        if not character["class"]["name"]:
            return {"error": "Class must be selected first"}
            
        # Get class data
        class_key = character["class"]["name"].lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        
        # Get equipment options
        equipment_options = class_info.get("equipment_options", [])
        
        # Get background equipment already added
        background_equipment = []
        if character["background"]["name"]:
            bg_key = character["background"]["name"].lower().replace(" ", "_")
            if bg_key in self.background_data:
                bg_info = self.background_data[bg_key]
                background_equipment = bg_info.get("equipment", [])
        
        return {
            "equipment_options": equipment_options,
            "background_equipment": background_equipment
        }
    
    def get_class_spell_options(self, character_id: str) -> Dict[str, Any]:
        """
        Get available spell options for the character's class.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Dict[str, Any]: Available spell options
        """
        # Retrieve character data
        character = self._get_character_data(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Check if class is selected
        if not character["class"]["name"]:
            return {"error": "Class must be selected first"}
            
        # Get class data
        class_key = character["class"]["name"].lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        
        # Check if spellcaster
        spellcasting_info = class_info.get("spellcasting", {})
        if not spellcasting_info:
            return {"error": "This class cannot cast spells"}
        
        # Get spellcasting details
        spellcasting_ability = spellcasting_info.get("ability", "")
        cantrips_known = spellcasting_info.get("cantrips_known", {}).get("1", 0)
        
        # Calculate spells known/prepared
        if "prepared" in spellcasting_info:
            # Prepared caster (Cleric, Druid, etc.)
            ability = spellcasting_ability.lower()
            ability_mod = character["ability_modifiers"].get(ability, 0)
            spells_prepared = ability_mod + character["class"]["level"]
            if spells_prepared < 1:
                spells_prepared = 1
            
            spell_formula = f"{ability.capitalize()} modifier ({ability_mod}) + {class_info.get('name')} level ({character['class']['level']})"
            
            spells_info = {
                "spells_prepared": spells_prepared,
                "preparation_formula": spell_formula,
                "preparation_type": "prepared"
            }
        else:
            # Known caster (Bard, Sorcerer, etc.)
            spells_known = spellcasting_info.get("spells_known", {}).get("1", 0)
            
            spells_info = {
                "spells_known": spells_known,
                "preparation_type": "known"
            }
        
        # Get available spell lists
        available_cantrips = self._get_class_spell_list(class_key, 0)
        available_level1_spells = self._get_class_spell_list(class_key, 1)
        
        return {
            "spellcasting_ability": spellcasting_ability,
            "cantrips_known": cantrips_known,
            "available_cantrips": available_cantrips,
            "available_spells": available_level1_spells,
            "spells_info": spells_info
        }
        
    def _get_character_data(self, character_id: str) -> Dict[str, Any]:
        """
        Get character data from active cache or repository.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Dict[str, Any]: Character data or None if not found
        """
        # First check the active characters cache
        if character_id in self.active_characters:
            return self.active_characters[character_id]
        
        # If not in cache, try the repository
        character = self.character_repository.get_character(character_id)
        
        # If found, add to active cache
        if character:
            self.active_characters[character_id] = character
            
        return character
    
    def _validate_equipment_item(self, item_type: str, item_id: str) -> bool:
        """
        Validate that an equipment item exists in the data.
        
        Args:
            item_type: Type of equipment (weapon, armor, gear)
            item_id: Item identifier
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not item_id:
            return False
            
        # Check equipment data for the item
        item_collection = self.equipment_data.get(f"{item_type}s", {})
        return item_id in item_collection
    
    def _get_pack_contents(self, pack_id: str) -> List[Dict[str, Any]]:
        """
        Get contents of an equipment pack.
        
        Args:
            pack_id: Pack identifier
            
        Returns:
            List[Dict[str, Any]]: Pack contents or empty list if invalid
        """
        packs = self.equipment_data.get("packs", {})
        pack = packs.get(pack_id, {})
        
        return pack.get("contents", [])
    
    def _validate_spell(self, spell_id: str, level: int, class_id: str) -> bool:
        """
        Validate that a spell exists and is available to the class.
        
        Args:
            spell_id: Spell identifier
            level: Spell level (0 for cantrips)
            class_id: Class identifier
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not spell_id:
            return False
            
        # Get spell data
        spell = self.spells_data.get(spell_id, {})
        if not spell:
            return False
            
        # Check spell level
        if spell.get("level", 0) != level:
            return False
            
        # Check if available to class
        classes = spell.get("classes", [])
        return class_id in classes
    
    def _get_class_spell_list(self, class_id: str, level: int) -> List[Dict[str, Any]]:
        """
        Get list of spells available to a class at a certain level.
        
        Args:
            class_id: Class identifier
            level: Spell level (0 for cantrips)
            
        Returns:
            List[Dict[str, Any]]: List of available spells
        """
        available_spells = []
        
        for spell_id, spell_data in self.spells_data.items():
            if spell_data.get("level") == level and class_id in spell_data.get("classes", []):
                spell_info = {
                    "id": spell_id,
                    "name": spell_data.get("name", spell_id),
                    "school": spell_data.get("school", ""),
                    "casting_time": spell_data.get("casting_time", ""),
                    "components": spell_data.get("components", ""),
                }
                available_spells.append(spell_info)
                
        return available_spells