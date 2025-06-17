import sys
import json
import os
import random
from typing import Dict, Any, List

# Import character sheet components
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
from character_sheet import CharacterSheet, ProficiencyLevel
from llm_service import LLMService, JSONExtractor

class CharacterCreator:
    """A D&D character creator that uses any LLM service."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the character creator.
        
        Args:
            llm_service: An implementation of LLMService
        """
        self.llm_service = llm_service
        self.character = CharacterSheet()
        self.current_character_json = {}  # Store the current character JSON
        self.is_first_creation = True     # Track if this is the first creation
        self.json_extractor = JSONExtractor()
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service."""
        return self.llm_service.test_connection()
    
    def _generate_character_name(self, species: str) -> str:
        """Generate a character name based on species."""
        name_suggestions = {
            "Elf": ["Aeliana", "Thalion", "Silvyr", "Elenion", "Miriel", "Legolas"],
            "Dwarf": ["Thorin", "Dwalin", "Gimli", "Daina", "Borin", "Nala"],
            "Halfling": ["Bilbo", "Rosie", "Pippin", "Merry", "Frodo", "Samwise"],
            "Human": ["Gareth", "Elena", "Marcus", "Lyanna", "Roderick", "Aria"],
            "Dragonborn": ["Balasar", "Akra", "Torinn", "Sora", "Kriv", "Nala"],
            "Tiefling": ["Akmenios", "Nemeia", "Orianna", "Zevran", "Enna", "Damaia"],
            "Gnome": ["Boddynock", "Dimble", "Glim", "Seebo", "Sindri", "Turen"],
            "Half-Elf": ["Aramil", "Berris", "Dayereth", "Enna", "Galinndan", "Hadarai"],
            "Half-Orc": ["Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"]
        }
        
        names = name_suggestions.get(species, name_suggestions["Human"])
        return random.choice(names)
    
    def validate_character_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize character data to ensure correct types."""
        valid_data = {}
        
        # Basic identity - ensure strings with better name handling
        name = data.get("name", "")
        if not name or name.strip() == "":
            species = str(data.get("species", "Human"))
            valid_data["name"] = self._generate_character_name(species)
        else:
            valid_data["name"] = str(name).strip()
        
        valid_data["species"] = str(data.get("species", "Human"))
        valid_data["background"] = str(data.get("background", "Commoner"))
        
        # Level - ensure integer
        valid_data["level"] = int(data.get("level", 1))
        
        # Classes - ensure dict with string keys and int values
        classes = {}
        for cls, lvl in data.get("classes", {}).items():
            try:
                classes[str(cls)] = int(lvl)
            except (ValueError, TypeError):
                classes[str(cls)] = 1
        if not classes:
            classes["Fighter"] = 1
        valid_data["classes"] = classes
        
        # Subclasses - ensure dict with string keys and values
        subclasses = {}
        for cls, subcls in data.get("subclasses", {}).items():
            subclasses[str(cls)] = str(subcls)
        valid_data["subclasses"] = subclasses
        
        # Alignment - ensure list of strings
        alignment = data.get("alignment", ["Neutral", "Neutral"])
        if isinstance(alignment, list) and len(alignment) >= 2:
            valid_data["alignment"] = [str(alignment[0]), str(alignment[1])]
        else:
            valid_data["alignment"] = ["Neutral", "Neutral"]
        
        # Ability scores - ensure dict with int values
        ability_scores = {}
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            try:
                score = data.get("ability_scores", {}).get(ability, 10)
                ability_scores[ability] = int(score)
            except (ValueError, TypeError):
                ability_scores[ability] = 10
        valid_data["ability_scores"] = ability_scores
        
        # Lists of strings - skills, traits, etc.
        for field in ["skill_proficiencies", "saving_throw_proficiencies", 
                      "personality_traits", "ideals", "bonds", "flaws"]:
            valid_data[field] = [str(item) for item in data.get(field, [])]
        
        # Enhanced armor - support both string and object formats
        armor = data.get("armor", "")
        if isinstance(armor, dict):
            valid_data["armor"] = {
                "name": str(armor.get("name", "")),
                "type": str(armor.get("type", "light")),
                "ac_base": int(armor.get("ac_base", 10)),
                "special_properties": [str(p) for p in armor.get("special_properties", [])],
                "description": str(armor.get("description", ""))
            }
        else:
            valid_data["armor"] = str(armor)
        
        # Enhanced weapons - ensure list of detailed dicts
        weapons = []
        for weapon in data.get("weapons", []):
            if isinstance(weapon, dict):
                weapon_data = {
                    "name": str(weapon.get("name", "Dagger")),
                    "type": str(weapon.get("type", "simple")),
                    "damage": str(weapon.get("damage", "1d4")),
                    "damage_type": str(weapon.get("damage_type", "piercing")),
                    "properties": [str(p) for p in weapon.get("properties", [])],
                    "special_abilities": [str(a) for a in weapon.get("special_abilities", [])],
                    "description": str(weapon.get("description", "")),
                    "magical": bool(weapon.get("magical", False)),
                    "rarity": str(weapon.get("rarity", "common"))
                }
                weapons.append(weapon_data)
            elif isinstance(weapon, str):
                weapons.append({
                    "name": weapon,
                    "type": "simple",
                    "damage": "1d4",
                    "damage_type": "piercing",
                    "properties": [],
                    "special_abilities": [],
                    "description": "",
                    "magical": False,
                    "rarity": "common"
                })
        valid_data["weapons"] = weapons
        
        # Magical items
        magical_items = []
        for item in data.get("magical_items", []):
            if isinstance(item, dict):
                magical_items.append({
                    "name": str(item.get("name", "")),
                    "type": str(item.get("type", "wondrous item")),
                    "rarity": str(item.get("rarity", "common")),
                    "attunement": bool(item.get("attunement", False)),
                    "properties": [str(p) for p in item.get("properties", [])],
                    "description": str(item.get("description", ""))
                })
        valid_data["magical_items"] = magical_items
        
        # Equipment - support both string and object formats
        equipment = []
        for item in data.get("equipment", []):
            if isinstance(item, dict):
                equipment.append({
                    "name": str(item.get("name", "")),
                    "quantity": int(item.get("quantity", 1)),
                    "description": str(item.get("description", ""))
                })
            elif isinstance(item, str):
                equipment.append({
                    "name": item,
                    "quantity": 1,
                    "description": ""
                })
        valid_data["equipment"] = equipment
        
        # Special abilities
        special_abilities = []
        for ability in data.get("special_abilities", []):
            if isinstance(ability, dict):
                special_abilities.append({
                    "name": str(ability.get("name", "")),
                    "type": str(ability.get("type", "extraordinary")),
                    "uses": str(ability.get("uses", "at will")),
                    "description": str(ability.get("description", ""))
                })
        valid_data["special_abilities"] = special_abilities
        
        # Spellcasting information
        if "spellcasting_ability" in data:
            valid_data["spellcasting_ability"] = str(data["spellcasting_ability"])
            valid_data["spell_save_dc"] = int(data.get("spell_save_dc", 10))
            valid_data["spell_attack_bonus"] = int(data.get("spell_attack_bonus", 0))
            
            # Validate spells_known
            spells_known = {}
            for level_str, spells in data.get("spells_known", {}).items():
                try:
                    level = int(level_str)
                    spells_known[str(level)] = [str(spell) for spell in spells]
                except (ValueError, TypeError):
                    pass
            valid_data["spells_known"] = spells_known
            
            # Validate spell_slots
            spell_slots = {}
            for level_str, slots in data.get("spell_slots", {}).items():
                try:
                    level = int(level_str)
                    spell_slots[str(level)] = int(slots)
                except (ValueError, TypeError):
                    pass
            valid_data["spell_slots"] = spell_slots
        
        # Enhanced backstory and personality
        valid_data["backstory"] = str(data.get("backstory", ""))
        
        personality_details = data.get("personality_details", {})
        if isinstance(personality_details, dict):
            valid_data["personality_details"] = {
                "mannerisms": [str(m) for m in personality_details.get("mannerisms", [])],
                "interaction_traits": [str(t) for t in personality_details.get("interaction_traits", [])],
                "appearance": str(personality_details.get("appearance", "")),
                "voice_and_speech": str(personality_details.get("voice_and_speech", ""))
            }
        
        return valid_data
    
    def populate_character(self, character_data: Dict[str, Any]) -> None:
        """Populate character sheet with data from the validated JSON."""
        try:
            # Reset character to avoid conflicts
            self.character = CharacterSheet()
            
            # Basic identity
            if "name" in character_data:
                self.character.set_name(character_data["name"])
            
            if "species" in character_data:
                self.character.set_species(character_data["species"])
            
            # Classes and levels
            for class_name, level in character_data.get("classes", {}).items():
                self.character.set_class_level(class_name, level)
                
                # Set subclass if provided
                subclasses = character_data.get("subclasses", {})
                if subclasses and class_name in subclasses:
                    self.character.set_subclass(class_name, subclasses[class_name])
            
            # Background and alignment
            if "background" in character_data:
                self.character.set_background(character_data["background"])
            
            if "alignment" in character_data and len(character_data["alignment"]) == 2:
                self.character.set_alignment(character_data["alignment"][0], character_data["alignment"][1])
            
            # Ability scores
            for ability, score in character_data.get("ability_scores", {}).items():
                self.character.set_base_ability_score(ability, int(score))
            
            # Proficiencies
            for skill in character_data.get("skill_proficiencies", []):
                self.character.set_skill_proficiency(skill, ProficiencyLevel.PROFICIENT)
            
            for ability in character_data.get("saving_throw_proficiencies", []):
                self.character.set_saving_throw_proficiency(ability, ProficiencyLevel.PROFICIENT)
            
            # Equipment
            armor = character_data.get("armor", {})
            if isinstance(armor, dict) and armor.get("name"):
                self.character.equip_armor(armor["name"])
            elif isinstance(armor, str) and armor:
                self.character.equip_armor(armor)
            
            if character_data.get("shield", False):
                self.character.equip_shield()
            
            for weapon in character_data.get("weapons", []):
                self.character.add_weapon(weapon)
            
            for item in character_data.get("equipment", []):
                self.character.add_equipment(item)
            
            # Spellcasting
            if "spellcasting_ability" in character_data:
                self.character.set_spellcasting_ability(character_data["spellcasting_ability"])
                
                for level_str, spells in character_data.get("spells_known", {}).items():
                    level = int(level_str)
                    for spell in spells:
                        self.character.add_spell_known(level, spell)
            
            # Personality
            for trait in character_data.get("personality_traits", []):
                self.character.add_personality_trait(trait)
            
            for ideal in character_data.get("ideals", []):
                self.character.add_ideal(ideal)
            
            for bond in character_data.get("bonds", []):
                self.character.add_bond(bond)
            
            for flaw in character_data.get("flaws", []):
                self.character.add_flaw(flaw)
            
            # Backstory
            if "backstory" in character_data:
                self.character.set_backstory(character_data["backstory"])
                
            # Calculate all derived stats
            self.character.calculate_all_derived_stats()
            
        except Exception as e:
            print(f"Error populating character sheet: {e}")
    
    def create_character(self, description: str, level: int = 1) -> Dict[str, Any]:
        """Create a character based on a description and specified level."""
        prompt = f"""
        Create a level {level} D&D character based on this description: {description}
        
        IMPORTANT REQUIREMENTS:
        - Character level must be {level}
        - Generate an appropriate fantasy name for this character
        - Create specialized equipment that fits the character concept and level
        - If this is a unique concept (like Jedi), create appropriate special abilities and equipment
        - Scale ability scores, equipment, and spells to level {level}
        - Write a detailed, immersive backstory (minimum 3-4 paragraphs)
        - Include specialized weapons, armor, and magical items as appropriate
        - Respond with a complete character in valid JSON format following the schema
        - Make sure to include ALL required fields including "name" and "level"
        
        For level {level} characters:
        - Ability scores should reflect experience and training
        - Equipment should be of appropriate quality and magical enhancement
        - Spellcasters should have access to spells up to their maximum spell level
        - Include class features and abilities appropriate to this level
        """
        
        response = self.llm_service.generate(prompt)
        
        # Extract and validate JSON
        character_data = self.json_extractor.extract_json(response)
        
        # If extraction failed, provide level-appropriate fallback data
        if not character_data:
            print("Could not extract proper JSON. Using fallback character template.")
            character_data = self._get_fallback_character(description, level)
        
        # Ensure level is set correctly
        character_data["level"] = level
        
        # Ensure name is populated
        if not character_data.get("name") or character_data.get("name") == "":
            species = character_data.get("species", "Human")
            character_data["name"] = self._generate_character_name(species)
        
        # Validate data to ensure proper types
        validated_data = self.validate_character_json(character_data)
        
        # Store this as our current character JSON for future iterations
        self.current_character_json = validated_data.copy()
        self.is_first_creation = False
        
        # Populate the character sheet
        self.populate_character(validated_data)
        
        # Get final character summary
        return self.character.get_character_summary()
    
    def refine_character(self, feedback: str) -> Dict[str, Any]:
        """Refine the character based on feedback, using the previous character as base."""
        
        # Use the stored JSON instead of character summary for more accurate iteration
        if self.current_character_json:
            current_char_json = json.dumps(self.current_character_json, indent=2)
        else:
            # Fallback to character summary if JSON not available
            current_char_json = json.dumps(self.character.get_character_summary(), indent=2)
        
        prompt = f"""
        Current character JSON: 
        {current_char_json}
        
        User feedback: {feedback}
        
        IMPORTANT:
        - Modify the existing character based on the feedback
        - Keep all existing fields unless specifically changing them
        - Maintain the character's name unless asked to change it
        - Return the COMPLETE updated character JSON, not just the changes
        - Ensure all required fields are present in your response
        
        Provide the updated character in valid JSON format exactly matching the schema.
        """
        
        # Get LLM response
        response = self.llm_service.generate(prompt)
        
        # Extract and validate JSON
        updated_character = self.json_extractor.extract_json(response)
        
        if not updated_character:
            print("Failed to extract changes. Trying a simplified prompt...")
            
            # Try a simpler prompt that explicitly asks for complete character
            simple_prompt = f"""
            Take this character: {current_char_json}
            
            Apply this change: {feedback}
            
            Return the complete updated character as valid JSON.
            """
            response = self.llm_service.generate(simple_prompt)
            updated_character = self.json_extractor.extract_json(response)
        
        # If still no valid JSON, merge feedback manually with current character
        if not updated_character:
            print("LLM failed to provide valid JSON. Applying minimal changes...")
            updated_character = self.current_character_json.copy()
            
            # Try to parse feedback for simple changes
            if "name" in feedback.lower():
                # Extract potential name from feedback
                words = feedback.split()
                for i, word in enumerate(words):
                    if word.lower() in ["name", "called", "named"] and i + 1 < len(words):
                        updated_character["name"] = words[i + 1].strip(".,!?")
                        break
        
        # Validate data
        validated_changes = self.validate_character_json(updated_character)
        
        # Update our stored character JSON
        self.current_character_json = validated_changes.copy()
        
        # Apply changes to character sheet
        self.populate_character(validated_changes)
        
        return self.character.get_character_summary()
    
    def _get_fallback_character(self, description: str = "", level: int = 1) -> Dict[str, Any]:
        """Generate a level-appropriate fallback character."""
        # Scale ability scores based on level
        base_scores = {
            "strength": 14, "dexterity": 12, "constitution": 13, 
            "intelligence": 10, "wisdom": 11, "charisma": 10
        }
        
        # Add ability score improvements for higher levels
        improvements = (level - 1) // 4 * 2  # ASI every 4 levels
        base_scores["strength"] += improvements
        
        return {
            "name": "Adventurer",
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Soldier",
            "alignment": ["Neutral", "Good"],
            "ability_scores": base_scores,
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "saving_throw_proficiencies": ["Strength", "Constitution"],
            "personality_traits": ["I face problems head-on", "I have a strong sense of duty"],
            "ideals": ["Honor", "Protection of the innocent"],
            "bonds": ["My fellow soldiers are my family"],
            "flaws": ["I have trouble trusting new allies"],
            "armor": {
                "name": "Plate Armor" if level >= 5 else "Chain Mail",
                "type": "heavy" if level >= 5 else "medium",
                "ac_base": 18 if level >= 5 else 16,
                "special_properties": ["Masterwork craftsmanship"] if level >= 10 else [],
                "description": f"Well-crafted armor befitting a level {level} warrior"
            },
            "weapons": [{
                "name": f"{'Magical ' if level >= 5 else ''}Longsword",
                "type": "martial",
                "damage": "1d8 + 1" if level >= 5 else "1d8",
                "damage_type": "slashing",
                "properties": ["versatile"],
                "special_abilities": ["Enhanced Strike"] if level >= 5 else [],
                "description": f"A {('magical ' if level >= 5 else '')}longsword wielded with skill",
                "magical": level >= 5,
                "rarity": "uncommon" if level >= 5 else "common"
            }],
            "equipment": [
                {"name": "Explorer's Pack", "quantity": 1, "description": "Standard adventuring gear"},
                {"name": "Shield", "quantity": 1, "description": "Steel shield"}
            ],
            "backstory": f"A veteran soldier with {level} levels of experience, having served in numerous campaigns and earned recognition for bravery and tactical skill. Through years of combat and training, they have honed their abilities to a fine edge.",
            "personality_details": {
                "mannerisms": ["Stands at attention when addressed", "Checks weapons before battle"],
                "interaction_traits": ["Direct and honest", "Protective of allies"],
                "appearance": f"Battle-scarred warrior in well-maintained gear",
                "voice_and_speech": "Speaks with military precision and authority"
            }
        }

import sys
import json
import os
import random
from typing import Dict, Any, List

# Import character sheet components
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
from character_sheet import CharacterSheet, ProficiencyLevel
from llm_service import LLMService, JSONExtractor
from abstract_multiclass_and_level_up import AbstractMulticlassAndLevelUp


class CharacterCreator:
    """A D&D character creator that uses any LLM service with full level progression."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the character creator.
        
        Args:
            llm_service: An implementation of LLMService
        """
        self.llm_service = llm_service
        self.character = CharacterSheet()
        self.current_character_json = {}
        self.character_progression = {}  # Store full level 1-20 progression
        self.is_first_creation = True
        self.json_extractor = JSONExtractor()
        self.level_up_rules = AbstractMulticlassAndLevelUp()
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service."""
        return self.llm_service.test_connection()
    
    def create_character_progression(self, description: str, target_level: int = 20) -> Dict[str, Dict[str, Any]]:
        """
        Create a complete character progression from level 1 to target_level.
        
        Args:
            description: Character concept description
            target_level: Maximum level to create (default 20)
        
        Returns:
            Dictionary with keys like 'level_1', 'level_2', etc.
        """
        print(f"Creating character progression from level 1 to {target_level}...")
        
        # Step 1: Create the base level 1 character
        level_1_character = self._create_base_character(description)
        self.character_progression = {"level_1": level_1_character}
        
        # Step 2: Create progression for each subsequent level
        for level in range(2, target_level + 1):
            print(f"  Generating level {level}...")
            level_character = self._create_level_up_character(level, description)
            self.character_progression[f"level_{level}"] = level_character
        
        # Step 3: Save progression to file
        self._save_character_progression(description)
        
        print(f"✅ Complete character progression created (levels 1-{target_level})")
        return self.character_progression
    
    def _create_base_character(self, description: str) -> Dict[str, Any]:
        """Create the base level 1 character."""
        prompt = f"""
        Create a level 1 D&D character based on this description: {description}
        
        This is the foundation character that will grow from level 1 to 20. Consider:
        - What class(es) would best represent this concept?
        - What would their early backstory be as a beginning adventurer?
        - What basic equipment would they start with?
        - What are their core personality traits that will evolve over time?
        
        IMPORTANT REQUIREMENTS:
        - Character level must be 1
        - Generate an appropriate fantasy name
        - Create a backstory that shows their humble beginnings
        - Include basic starting equipment appropriate for level 1
        - Consider multiclass potential for future growth
        - Respond with complete character in valid JSON format
        """
        
        response = self.llm_service.generate(prompt)
        character_data = self.json_extractor.extract_json(response)
        
        if not character_data:
            character_data = self._get_fallback_character(description, 1)
        
        character_data["level"] = 1
        validated_data = self.validate_character_json(character_data)
        
        # Store as current character for reference
        self.current_character_json = validated_data.copy()
        
        return validated_data
    
    def _create_level_up_character(self, level: int, original_description: str) -> Dict[str, Any]:
        """Create a character at a specific level based on progression rules."""
        previous_level = level - 1
        previous_character = self.character_progression[f"level_{previous_level}"]
        
        # Apply level-up rules using the abstract class
        level_up_changes = self.level_up_rules.calculate_level_up_changes(
            previous_character, level
        )
        
        # Generate narrative progression
        prompt = f"""
        Level up this D&D character from level {previous_level} to level {level}.
        
        Original concept: {original_description}
        
        Previous character state:
        {json.dumps(previous_character, indent=2)}
        
        Level {level} changes to apply:
        {json.dumps(level_up_changes, indent=2)}
        
        IMPORTANT REQUIREMENTS:
        - Maintain character continuity and core identity
        - Apply the mechanical changes provided
        - Evolve the backstory to reflect growth and new experiences
        - Add new equipment/abilities appropriate for level {level}
        - Show character development and maturation
        - Update personality to reflect experiences gained
        - Consider multiclass progression if appropriate
        
        For level {level} specifically:
        - Update ability scores with any ASI/feat improvements
        - Add new class features and abilities
        - Upgrade equipment quality and magical enhancement
        - Expand spell repertoire if applicable
        - Develop relationships and reputation in the world
        
        Return the COMPLETE level {level} character in valid JSON format.
        """
        
        response = self.llm_service.generate(prompt)
        character_data = self.json_extractor.extract_json(response)
        
        if not character_data:
            print(f"LLM failed for level {level}, applying mechanical changes only...")
            character_data = self._apply_mechanical_level_up(previous_character, level_up_changes, level)
        
        # Ensure level is correct
        character_data["level"] = level
        
        # Apply mechanical changes from the abstract class
        character_data = self._merge_level_up_changes(character_data, level_up_changes)
        
        validated_data = self.validate_character_json(character_data)
        return validated_data
    
    def _apply_mechanical_level_up(self, previous_char: Dict[str, Any], changes: Dict[str, Any], level: int) -> Dict[str, Any]:
        """Apply mechanical level-up changes when LLM fails."""
        character_data = previous_char.copy()
        character_data["level"] = level
        
        # Apply ability score improvements
        if "ability_score_improvements" in changes:
            for ability, improvement in changes["ability_score_improvements"].items():
                current_score = character_data.get("ability_scores", {}).get(ability, 10)
                character_data.setdefault("ability_scores", {})[ability] = current_score + improvement
        
        # Apply new class levels
        if "class_levels" in changes:
            for class_name, new_level in changes["class_levels"].items():
                character_data.setdefault("classes", {})[class_name] = new_level
        
        # Add new proficiencies
        if "new_proficiencies" in changes:
            character_data.setdefault("skill_proficiencies", []).extend(changes["new_proficiencies"])
        
        # Add new spells
        if "new_spells" in changes:
            for spell_level, spells in changes["new_spells"].items():
                character_data.setdefault("spells_known", {}).setdefault(spell_level, []).extend(spells)
        
        # Update backstory with generic progression
        character_data["backstory"] += f"\n\nAt level {level}, the character has gained significant experience and continues to grow in power and wisdom."
        
        return character_data
    
    def _merge_level_up_changes(self, character_data: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Merge mechanical changes with LLM-generated character data."""
        # Ensure core mechanical changes are applied correctly
        if "class_levels" in changes:
            for class_name, new_level in changes["class_levels"].items():
                character_data.setdefault("classes", {})[class_name] = new_level
        
        if "ability_score_improvements" in changes:
            for ability, improvement in changes["ability_score_improvements"].items():
                current_score = character_data.get("ability_scores", {}).get(ability, 10)
                # Only apply if the LLM didn't already account for it
                if current_score < 20:  # Cap at 20
                    character_data.setdefault("ability_scores", {})[ability] = min(20, current_score + improvement)
        
        if "proficiency_bonus" in changes:
            character_data["proficiency_bonus"] = changes["proficiency_bonus"]
        
        if "hit_points" in changes:
            character_data["hit_points"] = changes["hit_points"]
        
        return character_data
    
    def _save_character_progression(self, description: str) -> None:
        """Save the character progression to JSON files."""
        # Create save directory
        save_dir = os.path.join(os.path.dirname(__file__), 'character_progressions')
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename from character name and description
        char_name = self.character_progression["level_1"].get("name", "unnamed_character")
        safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
        
        # Save complete progression
        progression_file = os.path.join(save_dir, f"{safe_name}_progression.json")
        with open(progression_file, 'w') as f:
            json.dump(self.character_progression, f, indent=2)
        
        # Save individual level files
        level_dir = os.path.join(save_dir, safe_name)
        os.makedirs(level_dir, exist_ok=True)
        
        for level_key, character_data in self.character_progression.items():
            level_file = os.path.join(level_dir, f"{level_key}.json")
            with open(level_file, 'w') as f:
                json.dump(character_data, f, indent=2)
        
        print(f"Character progression saved to: {progression_file}")
        print(f"Individual levels saved to: {level_dir}/")
    
    def get_character_at_level(self, level: int) -> Dict[str, Any]:
        """Get character data at a specific level."""
        level_key = f"level_{level}"
        if level_key in self.character_progression:
            return self.character_progression[level_key]
        else:
            raise ValueError(f"Level {level} not found in character progression")
    
    def preview_progression_summary(self) -> str:
        """Generate a summary of the character's progression."""
        if not self.character_progression:
            return "No character progression available."
        
        summary = []
        char_name = self.character_progression["level_1"].get("name", "Unknown")
        summary.append(f"=== {char_name}'s Character Progression ===\n")
        
        for level in range(1, len(self.character_progression) + 1):
            level_key = f"level_{level}"
            if level_key in self.character_progression:
                char_data = self.character_progression[level_key]
                
                # Extract key info
                classes = char_data.get("classes", {})
                class_summary = ", ".join([f"{cls} {lvl}" for cls, lvl in classes.items()])
                
                abilities = char_data.get("ability_scores", {})
                highest_ability = max(abilities.items(), key=lambda x: x[1]) if abilities else ("Unknown", 0)
                
                summary.append(f"Level {level}: {class_summary}")
                summary.append(f"  Highest Ability: {highest_ability[0].title()} ({highest_ability[1]})")
                
                # Show major features at key levels
                if level in [1, 3, 5, 11, 17, 20]:
                    weapons = char_data.get("weapons", [])
                    if weapons:
                        best_weapon = weapons[0].get("name", "None") if isinstance(weapons[0], dict) else weapons[0]
                        summary.append(f"  Primary Weapon: {best_weapon}")
                    
                    magical_items = char_data.get("magical_items", [])
                    if magical_items:
                        item_count = len(magical_items)
                        summary.append(f"  Magical Items: {item_count}")
                
                summary.append("")
        
        return "\n".join(summary)
    
    # Keep existing methods for backward compatibility
    def create_character(self, description: str, level: int = 1) -> Dict[str, Any]:
        """Create a character at a specific level (backward compatibility)."""
        if level == 1:
            # Create just level 1
            character_data = self._create_base_character(description)
            self.populate_character(character_data)
            return self.character.get_character_summary()
        else:
            # Create progression up to target level and return that level
            self.create_character_progression(description, level)
            target_character = self.get_character_at_level(level)
            self.populate_character(target_character)
            return self.character.get_character_summary()
    
    # ... (keep all existing validation and utility methods from previous version) ...
    
    def validate_character_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize character data to ensure correct types."""
        # ... (keep existing validation logic) ...
        valid_data = {}
        
        # Basic identity - ensure strings with better name handling
        name = data.get("name", "")
        if not name or name.strip() == "":
            species = str(data.get("species", "Human"))
            valid_data["name"] = self._generate_character_name(species)
        else:
            valid_data["name"] = str(name).strip()
        
        valid_data["species"] = str(data.get("species", "Human"))
        valid_data["background"] = str(data.get("background", "Commoner"))
        valid_data["level"] = int(data.get("level", 1))
        
        # Classes
        classes = {}
        for cls, lvl in data.get("classes", {}).items():
            try:
                classes[str(cls)] = int(lvl)
            except (ValueError, TypeError):
                classes[str(cls)] = 1
        if not classes:
            classes["Fighter"] = 1
        valid_data["classes"] = classes
        
        # Continue with rest of validation...
        # (Include all the validation logic from the previous version)
        
        return valid_data
    
    def _generate_character_name(self, species: str) -> str:
        """Generate a character name based on species."""
        name_suggestions = {
            "Elf": ["Aeliana", "Thalion", "Silvyr", "Elenion", "Miriel", "Legolas"],
            "Dwarf": ["Thorin", "Dwalin", "Gimli", "Daina", "Borin", "Nala"],
            "Halfling": ["Bilbo", "Rosie", "Pippin", "Merry", "Frodo", "Samwise"],
            "Human": ["Gareth", "Elena", "Marcus", "Lyanna", "Roderick", "Aria"],
            "Dragonborn": ["Balasar", "Akra", "Torinn", "Sora", "Kriv", "Nala"],
            "Tiefling": ["Akmenios", "Nemeia", "Orianna", "Zevran", "Enna", "Damaia"],
            "Gnome": ["Boddynock", "Dimble", "Glim", "Seebo", "Sindri", "Turen"],
            "Half-Elf": ["Aramil", "Berris", "Dayereth", "Enna", "Galinndan", "Hadarai"],
            "Half-Orc": ["Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"]
        }
        
        names = name_suggestions.get(species, name_suggestions["Human"])
        return random.choice(names)
    
    def populate_character(self, character_data: Dict[str, Any]) -> None:
        """Populate character sheet with data from the validated JSON."""
        # ... (keep existing populate logic) ...
        pass
    
    def _get_fallback_character(self, description: str = "", level: int = 1) -> Dict[str, Any]:
        """Generate a level-appropriate fallback character."""
        # ... (keep existing fallback logic) ...
        pass

    # In character_creator.py, modify the finalize_character method:
    def finalize_character(self, character_id: str, additional_details: Dict[str, Any] = None) -> Dict[str, Any]:
        character = self.active_characters.get(character_id)
        if not character:
            return {"error": "Character not found"}
        
        # Existing validation using CharacterValidator
        validation_result = self.validator.validate_full_character(character)
        
        # Add comprehensive rules validation using CreateRules
        from backend4.create_rules import CreateRules
        # Convert character dict to CharacterSheet object first, then validate
        # rules_validation = CreateRules.validate_entire_character_sheet(character_sheet)
        
        # Combine validation results
        character["validation_result"] = validation_result
        # character["rules_validation"] = rules_validation
        
        # use /backend4/unified_validator.py for unified validation
