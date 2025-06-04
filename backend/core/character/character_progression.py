"""
Character Progression Module

Manages character advancement, level-ups, and progression tracking.
Provides methods for tracking character development over time.
"""

# future work: should be able to anticipate how you'd like your character to evolve (or multi-class) and mold character to fit that trajectory


from typing import Dict, List, Any, Optional, Union
import json
from pathlib import Path
import datetime

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object


class CharacterProgression(AbstractCharacterClass):
    """
    Handles character advancement, level-ups, and progression tracking.
    
    This class manages the level-up process including selecting new features, 
    managing ability score improvements, and spell selection. It also supports 
    multi-classing and experience point tracking for character advancement.
    """

    def __init__(self, rules_data_path: str = None):
        """
        Initialize the character progression manager.
        
        Args:
            rules_data_path: Optional path to rules data directory
        """
        # Set up data path for rules
        self.data_dir = Path(rules_data_path) if rules_data_path else Path("backend/data/rules")
        self._load_rules_data()
        
        # Experience point thresholds by level
        self.xp_thresholds = {
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500,
            6: 14000,
            7: 23000,
            8: 34000,
            9: 48000,
            10: 64000,
            11: 85000,
            12: 100000,
            13: 120000,
            14: 140000,
            15: 165000,
            16: 195000,
            17: 225000,
            18: 265000,
            19: 305000,
            20: 355000
        }
    
    def _load_rules_data(self):
        """Load rules data from JSON files."""
        try:
            # Load class data for level-up features
            with open(self.data_dir / "classes.json", "r") as f:
                self.class_data = json.load(f)
                
            # Load spells data for spell selection
            with open(self.data_dir / "spells.json", "r") as f:
                self.spells_data = json.load(f)
                
        except FileNotFoundError as e:
            print(f"Warning: Could not load rules data: {e}")
            # Initialize with empty data as fallback
            self.class_data = {}
            self.spells_data = {}
    
    def process_level_up(self, character_data: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """
        Handle level advancement process.
        
        Args:
            character_data: Character data dictionary
            new_level: New character level to advance to
            
        Returns:
            Dict[str, Any]: Result with level-up options and status
        """
        # Validate level-up request
        current_level = character_data.get("class", {}).get("level", 1)
        
        if new_level <= current_level:
            return {
                "success": False,
                "error": f"New level ({new_level}) must be greater than current level ({current_level})",
                "character": character_data
            }
        
        if new_level > 20:
            return {
                "success": False,
                "error": "Cannot level up beyond level 20",
                "character": character_data
            }
        
        # Check if character has enough XP for the level
        if "experience_points" in character_data:
            required_xp = self.xp_thresholds.get(new_level, 0)
            if character_data["experience_points"] < required_xp:
                return {
                    "success": False,
                    "error": f"Insufficient XP for level {new_level}. Need {required_xp} XP.",
                    "character": character_data
                }
        
        # Get level-up options
        level_options = self.get_level_up_options(character_data, new_level)
        
        # Return result with options
        return {
            "success": True,
            "message": f"Ready to level up from {current_level} to {new_level}",
            "character": character_data,
            "level_options": level_options
        }
    
    def get_level_up_options(self, character_data: Dict[str, Any], new_level: int) -> Dict[str, Any]:
        """
        Get available choices for level up.
        
        Args:
            character_data: Character data dictionary
            new_level: New character level
            
        Returns:
            Dict[str, Any]: Available options for the level-up
        """
        options = {
            "features": [],
            "hit_dice": None,
            "ability_score_improvement": False,
            "spells": {
                "new_cantrips": 0,
                "new_spells": 0,
                "spell_slots": {}
            },
            "multi_class": {
                "available": True,
                "options": []
            }
        }
        
        # Get class info
        class_name = character_data.get("class", {}).get("name", "")
        if not class_name:
            return options
            
        class_key = class_name.lower().replace(" ", "_")
        class_info = self.class_data.get(class_key, {})
        
        # Get hit dice
        options["hit_dice"] = class_info.get("hit_dice", "d8")
        
        # Check for features at this level
        level_features = class_info.get("features", {}).get(str(new_level), [])
        options["features"] = level_features
        
        # Check for ASI levels (typically 4, 8, 12, 16, 19)
        asi_levels = class_info.get("ability_score_improvement_levels", [4, 8, 12, 16, 19])
        options["ability_score_improvement"] = new_level in asi_levels
        
        # Check for spellcasting changes
        if "spellcasting" in class_info:
            spellcasting = class_info["spellcasting"]
            
            # Check for new cantrips
            cantrips_by_level = spellcasting.get("cantrips_known", {})
            prev_cantrips = cantrips_by_level.get(str(new_level - 1), 0)
            new_cantrips = cantrips_by_level.get(str(new_level), 0)
            options["spells"]["new_cantrips"] = max(0, new_cantrips - prev_cantrips)
            
            # Check for new spells for known-spell casters
            if "spells_known" in spellcasting:
                spells_by_level = spellcasting.get("spells_known", {})
                prev_spells = spells_by_level.get(str(new_level - 1), 0)
                new_spells = spells_by_level.get(str(new_level), 0) 
                options["spells"]["new_spells"] = max(0, new_spells - prev_spells)
            
            # Get spell slot changes
            slots_by_level = spellcasting.get("spell_slots", {})
            if str(new_level) in slots_by_level:
                options["spells"]["spell_slots"] = slots_by_level[str(new_level)]
        
        # Check for subclass selection
        subclass_level = class_info.get("subclass_level", 3)
        if new_level == subclass_level and not character_data.get("class", {}).get("subclass"):
            subclasses = class_info.get("subclasses", {})
            options["subclass_options"] = list(subclasses.keys())
            options["subclass_selection_required"] = True
        
        # Get multi-class options
        multi_class_options = []
        for class_key, class_data in self.class_data.items():
            if class_key != class_name.lower().replace(" ", "_"):
                # Check if character meets requirements for the class
                if self._check_multiclass_requirements(character_data, class_key):
                    multi_class_options.append({
                        "name": class_data.get("name", class_key),
                        "key": class_key,
                        "description": class_data.get("description", "")
                    })
        
        options["multi_class"]["options"] = multi_class_options
        options["multi_class"]["available"] = len(multi_class_options) > 0
        
        return options
    
    def apply_level_benefits(self, character_data: Dict[str, Any], 
                           new_level: int, 
                           choices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply level benefits based on selected choices.
        
        Args:
            character_data: Character data dictionary
            new_level: New character level
            choices: Dictionary of selected choices for the level-up
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Create a copy of the character data to work with
        updated_character = character_data.copy()
        
        # Check if this is a multi-class level up
        is_multiclass = choices.get("multi_class", {}).get("selected", False)
        
        if is_multiclass:
            # Handle multi-class level up
            return self._apply_multiclass_level(updated_character, choices.get("multi_class", {}))
        else:
            # Update level in primary class
            current_class = updated_character.get("class", {})
            current_class["level"] = new_level
            updated_character["class"] = current_class
        
        # Apply hit dice and HP increase
        hit_dice_type = updated_character.get("class", {}).get("hit_dice", "d8")
        hit_dice_size = int(hit_dice_type.replace("d", ""))
        
        # Default HP increase is based on average roll (half hit die size + 1)
        hp_increase = (hit_dice_size // 2) + 1
        
        # If user selected to roll, use their provided roll
        if choices.get("hit_points", {}).get("method") == "roll":
            hp_roll = choices.get("hit_points", {}).get("roll")
            if hp_roll and isinstance(hp_roll, int) and 1 <= hp_roll <= hit_dice_size:
                hp_increase = hp_roll
        
        # Add Constitution modifier to HP increase
        con_mod = updated_character.get("ability_modifiers", {}).get("constitution", 0)
        hp_increase += con_mod
        
        # Ensure minimum of 1 HP gained per level
        hp_increase = max(1, hp_increase)
        
        # Update max HP
        updated_character["max_hp"] = updated_character.get("max_hp", 0) + hp_increase
        
        # Update hit dice count
        if "hit_dice" not in updated_character:
            updated_character["hit_dice"] = {}
        
        if hit_dice_type not in updated_character["hit_dice"]:
            updated_character["hit_dice"][hit_dice_type] = 0
        
        updated_character["hit_dice"][hit_dice_type] += 1
        
        # Apply ability score improvements if applicable and selected
        if choices.get("ability_score_improvement"):
            asi_choices = choices.get("ability_score_improvement", {})
            updated_character = self.apply_ability_score_improvement(updated_character, asi_choices)
        
        # Apply subclass if selected
        if choices.get("subclass"):
            subclass = choices.get("subclass")
            updated_character["class"]["subclass"] = subclass
            
            # Add subclass features
            class_key = updated_character["class"]["name"].lower().replace(" ", "_")
            class_info = self.class_data.get(class_key, {})
            subclasses = class_info.get("subclasses", {})
            
            if subclass in subclasses:
                subclass_info = subclasses[subclass]
                subclass_features = subclass_info.get("features", {}).get(str(new_level), [])
                
                if "features" not in updated_character["class"]:
                    updated_character["class"]["features"] = []
                
                updated_character["class"]["features"].extend(subclass_features)
        
        # Apply selected class features
        if "feature_choices" in choices:
            updated_character = self.select_new_features(updated_character, choices.get("feature_choices", {}))
        
        # Apply spell choices for spellcasting classes
        if "spell_choices" in choices:
            updated_character = self.learn_new_spells(updated_character, choices.get("spell_choices", {}))
        
        # Update proficiency bonus
        updated_character["proficiency_bonus"] = self._calculate_proficiency_bonus(new_level)
        
        # Update spellcasting DCs and attack bonuses if applicable
        if updated_character.get("spellcasting", {}).get("ability"):
            ability = updated_character["spellcasting"]["ability"].lower()
            ability_mod = updated_character.get("ability_modifiers", {}).get(ability, 0)
            
            updated_character["spellcasting"]["spell_save_dc"] = 8 + updated_character["proficiency_bonus"] + ability_mod
            updated_character["spellcasting"]["spell_attack_bonus"] = updated_character["proficiency_bonus"] + ability_mod
        
        # Add progression entry to character history
        if "history" not in updated_character:
            updated_character["history"] = []
        
        progression_entry = {
            "type": "level_up",
            "date": datetime.datetime.now().isoformat(),
            "previous_level": new_level - 1,
            "new_level": new_level,
            "choices": choices
        }
        
        updated_character["history"].append(progression_entry)
        
        return updated_character
    
    def calculate_experience_points(self, character_data: Dict[str, Any], 
                                  milestone: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate or update experience points.
        
        Args:
            character_data: Character data dictionary
            milestone: Optional milestone completion information
            
        Returns:
            Dict[str, Any]: Updated character data with XP
        """
        updated_character = character_data.copy()
        
        # Initialize XP if not present
        if "experience_points" not in updated_character:
            updated_character["experience_points"] = 0
        
        # Handle milestone-based advancement
        if milestone:
            milestone_type = milestone.get("type", "")
            milestone_tier = milestone.get("tier", "minor")
            
            # XP rewards based on tier
            xp_rewards = {
                "minor": 100,
                "moderate": 250,
                "major": 500,
                "quest": 1000
            }
            
            # Award XP based on milestone tier
            xp_reward = xp_rewards.get(milestone_tier, 100)
            updated_character["experience_points"] += xp_reward
            
            # Add milestone to character history
            if "history" not in updated_character:
                updated_character["history"] = []
            
            milestone_entry = {
                "type": "milestone",
                "date": datetime.datetime.now().isoformat(),
                "description": milestone.get("description", ""),
                "xp_earned": xp_reward
            }
            
            updated_character["history"].append(milestone_entry)
        
        # Check if character has enough XP to level up
        current_level = updated_character.get("class", {}).get("level", 1)
        if current_level < 20:
            next_level = current_level + 1
            required_xp = self.xp_thresholds.get(next_level, 0)
            
            if updated_character["experience_points"] >= required_xp:
                updated_character["can_level_up"] = True
                updated_character["next_level"] = next_level
            else:
                updated_character["can_level_up"] = False
                updated_character["xp_to_next_level"] = required_xp - updated_character["experience_points"]
        
        return updated_character
    
    def apply_ability_score_improvement(self, character_data: Dict[str, Any],
                                      improvements: Dict[str, int]) -> Dict[str, Any]:
        """
        Apply Ability Score Improvements (ASIs) to character.
        
        Args:
            character_data: Character data dictionary
            improvements: Dictionary of ability improvements
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        updated_character = character_data.copy()
        
        # Ensure ability scores exist
        if "ability_scores" not in updated_character:
            updated_character["ability_scores"] = {}
        
        # Apply improvements
        for ability, increase in improvements.items():
            if ability in updated_character["ability_scores"]:
                # Increase the ability score
                updated_character["ability_scores"][ability] += increase
                
                # Enforce the maximum of 20
                updated_character["ability_scores"][ability] = min(20, updated_character["ability_scores"][ability])
        
        # Recalculate ability modifiers
        modifiers = {}
        for ability, score in updated_character["ability_scores"].items():
            modifiers[ability] = (score - 10) // 2
        
        updated_character["ability_modifiers"] = modifiers
        
        # Update derived stats that depend on ability modifiers
        
        # Update max HP if constitution changed
        if "constitution" in improvements and "max_hp" in updated_character:
            # Calculate HP adjustment based on constitution change
            con_mod = updated_character["ability_modifiers"]["constitution"]
            previous_con_mod = character_data.get("ability_modifiers", {}).get("constitution", 0)
            con_mod_difference = con_mod - previous_con_mod
            
            # Adjust max HP for all levels
            level = updated_character.get("class", {}).get("level", 1)
            hp_adjustment = con_mod_difference * level
            updated_character["max_hp"] += hp_adjustment
        
        # Update spell save DC and attack bonus if spellcasting ability changed
        spellcasting_ability = updated_character.get("spellcasting", {}).get("ability", "").lower()
        if spellcasting_ability in improvements and spellcasting_ability:
            ability_mod = updated_character["ability_modifiers"][spellcasting_ability]
            proficiency = updated_character.get("proficiency_bonus", 2)
            
            updated_character["spellcasting"]["spell_save_dc"] = 8 + proficiency + ability_mod
            updated_character["spellcasting"]["spell_attack_bonus"] = proficiency + ability_mod
        
        return updated_character
    
    def select_new_features(self, character_data: Dict[str, Any], 
                          feature_choices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply new features based on selections.
        
        Args:
            character_data: Character data dictionary
            feature_choices: Dictionary of selected features and options
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        updated_character = character_data.copy()
        
        # Ensure features list exists
        if "class" not in updated_character:
            updated_character["class"] = {}
        if "features" not in updated_character["class"]:
            updated_character["class"]["features"] = []
        
        # Add selected features
        for feature_name, choice_details in feature_choices.items():
            feature = {
                "name": feature_name,
                "source": "class",  # or 'subclass', 'feat', etc.
                "level_gained": updated_character["class"].get("level", 1)
            }
            
            # Add selection details if present
            if isinstance(choice_details, dict) and choice_details:
                feature["selections"] = choice_details
            
            # Add feature to character
            updated_character["class"]["features"].append(feature)
            
            # Handle special features with additional effects
            if feature_name.lower() == "fighting style":
                style = choice_details.get("style")
                if style:
                    self._apply_fighting_style(updated_character, style)
            elif feature_name.lower() == "expertise":
                skills = choice_details.get("skills", [])
                if skills:
                    if "skills" not in updated_character:
                        updated_character["skills"] = {}
                    if "expertise" not in updated_character["skills"]:
                        updated_character["skills"]["expertise"] = []
                    
                    for skill in skills:
                        if skill not in updated_character["skills"]["expertise"]:
                            updated_character["skills"]["expertise"].append(skill)
        
        return updated_character
    
    def learn_new_spells(self, character_data: Dict[str, Any], 
                       spell_choices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn new spells based on selections.
        
        Args:
            character_data: Character data dictionary
            spell_choices: Dictionary with new cantrips and spells
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        updated_character = character_data.copy()
        
        # Ensure spellcasting data exists
        if "spellcasting" not in updated_character:
            return updated_character
        
        spellcasting = updated_character["spellcasting"]
        
        # Add new cantrips
        new_cantrips = spell_choices.get("cantrips", [])
        if new_cantrips:
            if "cantrips_known" not in spellcasting:
                spellcasting["cantrips_known"] = []
            
            for cantrip in new_cantrips:
                if cantrip not in spellcasting["cantrips_known"]:
                    spellcasting["cantrips_known"].append(cantrip)
        
        # Add new spells for "known spells" casters (like Bard, Sorcerer)
        new_spells = spell_choices.get("spells", [])
        if new_spells:
            if "spells_known" not in spellcasting:
                spellcasting["spells_known"] = []
            
            for spell in new_spells:
                if spell not in spellcasting["spells_known"]:
                    spellcasting["spells_known"].append(spell)
        
        # Update prepared spells for "prepared spells" casters (like Cleric, Wizard)
        prepared_spells = spell_choices.get("prepared", [])
        if prepared_spells:
            spellcasting["spells_prepared"] = prepared_spells
        
        # Update spell slots
        spell_slots = spell_choices.get("spell_slots", {})
        if spell_slots:
            spellcasting["spell_slots"] = spell_slots
        
        # Handle special cases for specific classes
        class_name = updated_character.get("class", {}).get("name", "").lower()
        
        if class_name == "wizard":
            # Wizards can add spells to their spellbook beyond their prepared spells
            new_spellbook_spells = spell_choices.get("spellbook", [])
            if new_spellbook_spells:
                if "spellbook" not in spellcasting:
                    spellcasting["spellbook"] = []
                
                for spell in new_spellbook_spells:
                    if spell not in spellcasting["spellbook"]:
                        spellcasting["spellbook"].append(spell)
        
        # Update the spellcasting in the character data
        updated_character["spellcasting"] = spellcasting
        
        return updated_character
    
    def track_character_development(self, character_id: str, 
                                 milestone_description: Optional[str] = None, 
                                 character_goals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track character growth and development over time.
        
        Args:
            character_id: Character identifier
            milestone_description: Optional narrative milestone description
            character_goals: Optional character goals and progress
            
        Returns:
            Dict[str, Any]: Updated character development data
        """
        # This method would typically load character data from storage,
        # update it with development information, and save it back.
        # For this implementation, we'll assume the character data is passed directly.
        
        # Placeholder for character repository functionality
        character_data = {"id": character_id}  # In a real implementation, load from repository
        
        if "development" not in character_data:
            character_data["development"] = {
                "milestones": [],
                "goals": {},
                "notes": []
            }
        
        # Add milestone if provided
        if milestone_description:
            milestone = {
                "date": datetime.datetime.now().isoformat(),
                "description": milestone_description
            }
            character_data["development"]["milestones"].append(milestone)
        
        # Update character goals if provided
        if character_goals:
            # Merge with existing goals
            character_data["development"]["goals"].update(character_goals)
        
        # In a real implementation, save back to repository
        
        return character_data["development"]
    
    def _calculate_proficiency_bonus(self, level: int) -> int:
        """Calculate proficiency bonus based on character level."""
        return 2 + ((level - 1) // 4)
    
    def _check_multiclass_requirements(self, character_data: Dict[str, Any], 
                                     class_key: str) -> bool:
        """Check if character meets requirements for multiclassing into a class."""
        class_info = self.class_data.get(class_key, {})
        multiclass_requirements = class_info.get("multiclass_requirements", {})
        
        if not multiclass_requirements:
            return True  # No requirements specified
        
        # Check if character meets ability score requirements
        ability_scores = character_data.get("ability_scores", {})
        for ability, min_score in multiclass_requirements.get("ability_scores", {}).items():
            if ability in ability_scores:
                if ability_scores[ability] < min_score:
                    return False
            else:
                return False
        
        return True
    
    def _apply_multiclass_level(self, character_data: Dict[str, Any], 
                              multiclass_choice: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a level in a new class when multiclassing."""
        # Get the selected class
        new_class_key = multiclass_choice.get("class")
        if not new_class_key:
            return character_data
        
        new_class_info = self.class_data.get(new_class_key, {})
        if not new_class_info:
            return character_data
        
        # Set up multiclass structure if not present
        if "multiclass" not in character_data:
            character_data["multiclass"] = {}
        
        # Add the new class
        if new_class_key not in character_data["multiclass"]:
            character_data["multiclass"][new_class_key] = {
                "name": new_class_info.get("name", new_class_key),
                "level": 1,
                "hit_dice": new_class_info.get("hit_dice", "d8"),
                "features": []
            }
        else:
            # Increase level in existing multiclass
            character_data["multiclass"][new_class_key]["level"] += 1
        
        # Calculate total character level
        primary_level = character_data.get("class", {}).get("level", 1)
        multi_levels = sum(c.get("level", 0) for c in character_data.get("multiclass", {}).values())
        total_level = primary_level + multi_levels
        
        character_data["total_level"] = total_level
        
        # Add 1st level class features if this is the first level in the class
        if character_data["multiclass"][new_class_key]["level"] == 1:
            level_1_features = new_class_info.get("features", {}).get("1", [])
            character_data["multiclass"][new_class_key]["features"].extend(level_1_features)
        
        # Update hit dice
        hit_dice_type = new_class_info.get("hit_dice", "d8")
        if "hit_dice" not in character_data:
            character_data["hit_dice"] = {}
        
        if hit_dice_type not in character_data["hit_dice"]:
            character_data["hit_dice"][hit_dice_type] = 0
        
        character_data["hit_dice"][hit_dice_type] += 1
        
        # Update HP
        hit_dice_size = int(hit_dice_type.replace("d", ""))
        hp_increase = (hit_dice_size // 2) + 1  # Average roll
        con_mod = character_data.get("ability_modifiers", {}).get("constitution", 0)
        hp_increase += con_mod
        
        # Ensure minimum of 1 HP gained
        hp_increase = max(1, hp_increase)
        
        # Update max HP
        character_data["max_hp"] = character_data.get("max_hp", 0) + hp_increase
        
        # Update proficiency bonus based on total level
        character_data["proficiency_bonus"] = self._calculate_proficiency_bonus(total_level)
        
        # Handle spellcasting for multiclass spellcasters
        self._update_multiclass_spellcasting(character_data, new_class_key)
        
        return character_data
    
    def _apply_fighting_style(self, character_data: Dict[str, Any], style: str) -> None:
        """Apply effects of a fighting style."""
        # Different fighting styles have different mechanical effects
        if style.lower() == "defense":
            # +1 to AC when wearing armor
            if "bonuses" not in character_data:
                character_data["bonuses"] = {}
            if "ac" not in character_data["bonuses"]:
                character_data["bonuses"]["ac"] = {}
                
            character_data["bonuses"]["ac"]["armor"] = character_data["bonuses"]["ac"].get("armor", 0) + 1
        
        elif style.lower() == "dueling":
            # +2 to damage when wielding a one-handed melee weapon
            if "bonuses" not in character_data:
                character_data["bonuses"] = {}
            if "damage" not in character_data["bonuses"]:
                character_data["bonuses"]["damage"] = {}
                
            character_data["bonuses"]["damage"]["dueling"] = 2
    
    def _update_multiclass_spellcasting(self, character_data: Dict[str, Any], 
                                      new_class_key: str) -> None:
        """Update spellcasting for multiclass characters."""
        # This is a complex area of the rules - this implementation is simplified
        
        new_class_info = self.class_data.get(new_class_key, {})
        
        # If the new class has spellcasting
        if "spellcasting" in new_class_info:
            # Initialize spellcasting if not present
            if "spellcasting" not in character_data:
                character_data["spellcasting"] = {
                    "ability": new_class_info["spellcasting"].get("ability"),
                    "spell_save_dc": 0,
                    "spell_attack_bonus": 0,
                    "cantrips_known": [],
                    "spells_known": [],
                    "spell_slots": {}
                }
            
            # Add the class to multiclass spellcasting tracking
            if "multiclass_spellcasting" not in character_data["spellcasting"]:
                character_data["spellcasting"]["multiclass_spellcasting"] = {}
                
            if new_class_key not in character_data["spellcasting"]["multiclass_spellcasting"]:
                character_data["spellcasting"]["multiclass_spellcasting"][new_class_key] = {
                    "ability": new_class_info["spellcasting"].get("ability"),
                    "level": 1
                }
            else:
                character_data["spellcasting"]["multiclass_spellcasting"][new_class_key]["level"] += 1
            
            # Recalculate total caster level and spell slots using the multiclass spellcasting rules
            self._recalculate_multiclass_slots(character_data)