"""
Character Validator Module

Validates character data against D&D rules, ensuring consistency and compliance.
Provides validation methods for different aspects of character creation and development.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object


class CharacterValidator(AbstractCharacterClass):
    """
    Validates character data against D&D rules and requirements.
    
    This class provides validation methods for checking the correctness and rule 
    compliance of character data, from ability scores to spell selections.
    It can generate detailed validation reports and suggest fixes for issues.
    """

    def __init__(self, rules_data_path: str = None):
        """
        Initialize the character validator.
        
        Args:
            rules_data_path: Optional path to rules data directory
        """
        # Set up data path for rules
        self.data_dir = Path(rules_data_path) if rules_data_path else Path("backend/data/rules")
        self._load_rules_data()
        
        # Define ability score limits
        self.min_ability_score = 3
        self.max_ability_score = 20
        self.point_buy_min = 8
        self.point_buy_max = 15
        
        # Define standard ability score sets
        self.standard_array = [15, 14, 13, 12, 10, 8]
        
        # Point buy costs (D&D 5e uses a 27-point system)
        self.point_buy_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        self.point_buy_points = 27
    
    def _load_rules_data(self):
        """Load rules data from JSON files."""
        try:
            # Load class data
            with open(self.data_dir / "classes.json", "r") as f:
                self.class_data = json.load(f)
                
            # Load species data
            with open(self.data_dir / "species.json", "r") as f:
                self.species_data = json.load(f)
                
            # Load background data
            with open(self.data_dir / "backgrounds.json", "r") as f:
                self.background_data = json.load(f)
                
            # Load equipment data
            with open(self.data_dir / "equipment.json", "r") as f:
                self.equipment_data = json.load(f)
                
            # Load spells data
            with open(self.data_dir / "spells.json", "r") as f:
                self.spells_data = json.load(f)
                
            # Load skills data
            with open(self.data_dir / "skills.json", "r") as f:
                self.skills_data = json.load(f)
                
        except FileNotFoundError as e:
            print(f"Warning: Could not load rules data: {e}")
            # Initialize with empty data as fallback
            self.class_data = {}
            self.species_data = {}
            self.background_data = {}
            self.equipment_data = {}
            self.spells_data = {}
            self.skills_data = {}
    
    def validate_full_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a complete character against all applicable rules.
        
        Args:
            character_data: Complete character data dictionary
            
        Returns:
            Dict[str, Any]: Validation results with issues and status
        """
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = [
            "name", "class", "species", "ability_scores", "background"
        ]
        
        for field in required_fields:
            if field not in character_data:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Missing required field: {field}")
        
        # If basic structure is invalid, return early
        if not validation_result["valid"]:
            return validation_result
        
        # Validate character name
        if not character_data.get("name"):
            validation_result["warnings"].append("Character name is empty")
        
        # Validate class
        class_result = self._validate_class(character_data.get("class", {}))
        if not class_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(class_result["issues"])
        
        # Validate species
        species_result = self._validate_species(character_data.get("species", {}))
        if not species_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(species_result["issues"])
        
        # Validate background
        background_result = self._validate_background(character_data.get("background", {}))
        if not background_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(background_result["issues"])
        
        # Validate ability scores
        ability_result = self.validate_ability_scores(
            character_data.get("ability_scores", {}),
            character_data.get("species", {}).get("name"),
            character_data.get("class", {}).get("name")
        )
        if not ability_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(ability_result["issues"])
        
        # Validate skill selections
        skill_result = self.validate_skill_selections(
            character_data.get("skills", {}),
            character_data.get("class", {}).get("name"),
            character_data.get("background", {}).get("name")
        )
        if not skill_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(skill_result["issues"])
        
        # Validate equipment selections
        equipment_result = self.validate_equipment_selections(
            character_data.get("equipment", {}),
            character_data.get("class", {}).get("name"),
            character_data.get("background", {}).get("name")
        )
        if not equipment_result["valid"]:
            validation_result["valid"] = False
            validation_result["issues"].extend(equipment_result["issues"])
        
        # Validate spells if character is a spellcaster
        if character_data.get("spellcasting", {}).get("ability"):
            spell_result = self.validate_spell_selections(
                character_data.get("spellcasting", {}),
                character_data.get("class", {}).get("name"),
                character_data.get("class", {}).get("level", 1)
            )
            if not spell_result["valid"]:
                validation_result["valid"] = False
                validation_result["issues"].extend(spell_result["issues"])
        
        # Validate multiclassing if applicable
        if "multiclass" in character_data:
            for multiclass_name, multiclass_data in character_data["multiclass"].items():
                multiclass_result = self.validate_multiclass_requirements(
                    character_data.get("ability_scores", {}),
                    multiclass_name
                )
                if not multiclass_result["valid"]:
                    validation_result["valid"] = False
                    validation_result["issues"].extend(multiclass_result["issues"])
        
        # Check for common optimization issues (not rule violations, just suboptimal choices)
        optimization_warnings = self._check_optimization_issues(character_data)
        if optimization_warnings:
            validation_result["warnings"].extend(optimization_warnings)
        
        return validation_result
    
    def validate_ability_scores(self, ability_scores: Dict[str, int], 
                              species: str = None, class_type: str = None) -> Dict[str, Any]:
        """
        Check if ability scores are valid according to D&D rules.
        
        Args:
            ability_scores: Dictionary of ability scores
            species: Optional species/race name to check racial bonuses
            class_type: Optional class name to check class requirements
            
        Returns:
            Dict[str, Any]: Validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check if all abilities are present
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in required_abilities:
            if ability not in ability_scores:
                result["valid"] = False
                result["issues"].append(f"Missing required ability: {ability}")
        
        # If missing abilities, return early
        if not result["valid"]:
            return result
        
        # Validate ability score ranges
        for ability, score in ability_scores.items():
            if not isinstance(score, int):
                result["valid"] = False
                result["issues"].append(f"Ability {ability} score must be an integer")
                continue
                
            if score < self.min_ability_score or score > self.max_ability_score:
                result["valid"] = False
                result["issues"].append(
                    f"Invalid {ability} score: {score}. Must be between {self.min_ability_score} and {self.max_ability_score}"
                )
        
        # If scores are invalid, return early
        if not result["valid"]:
            return result
        
        # Check if scores follow standard array or point buy
        if self._is_standard_array(ability_scores.values()):
            result["generation_method"] = "standard_array"
        else:
            # Check if point buy is valid
            point_buy_valid, point_buy_message, points_used = self._validate_point_buy(ability_scores)
            if point_buy_valid:
                result["generation_method"] = "point_buy"
                result["points_used"] = points_used
            else:
                # Not standard array or valid point buy, could be rolled or custom
                result["generation_method"] = "custom"
                # Add a warning but don't invalidate
                result["warnings"].append(
                    "Ability scores don't match standard array or point buy. " +
                    "Ensure they were generated using a valid method."
                )
        
        # Check class specific recommendations
        if class_type:
            class_key = class_type.lower().replace(" ", "_") if class_type else ""
            if class_key in self.class_data:
                class_info = self.class_data[class_key]
                primary_ability = class_info.get("primary_ability", "").lower()
                secondary_ability = class_info.get("secondary_ability", "").lower()
                
                # Check if primary ability is one of the highest
                if primary_ability in ability_scores:
                    primary_score = ability_scores[primary_ability]
                    higher_scores = sum(1 for score in ability_scores.values() if score > primary_score)
                    if higher_scores > 0:
                        result["warnings"].append(
                            f"{primary_ability.capitalize()} is the primary ability for {class_type} " +
                            f"but it's not your highest score."
                        )
                
                # Check if constitution is too low (general warning)
                if ability_scores.get("constitution", 0) < 12:
                    result["warnings"].append(
                        "Constitution score is below 12, which may result in lower hit points."
                    )
        
        return result
    
    def validate_skill_selections(self, skills: Dict[str, List[str]], 
                               class_type: str = None, background: str = None) -> Dict[str, Any]:
        """
        Validate skill selections against class and background options.
        
        Args:
            skills: Dictionary with 'proficient' and optional 'expertise' skill lists
            class_type: Optional class name for validation
            background: Optional background name for validation
            
        Returns:
            Dict[str, Any]: Validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Get proficient skills
        proficient_skills = skills.get("proficient", [])
        expertise_skills = skills.get("expertise", [])
        
        # Check if skills actually exist in the system
        all_skills = list(self.skills_data.keys()) if self.skills_data else []
        for skill in proficient_skills:
            if all_skills and skill not in all_skills:
                result["valid"] = False
                result["issues"].append(f"Invalid skill: {skill}")
        
        # Check expertise skills - must be proficient first
        for skill in expertise_skills:
            if skill not in proficient_skills:
                result["valid"] = False
                result["issues"].append(f"Cannot have expertise in {skill} without proficiency")
            
            if all_skills and skill not in all_skills:
                result["valid"] = False
                result["issues"].append(f"Invalid skill for expertise: {skill}")
        
        # Validate against class and background if provided
        if class_type:
            class_key = class_type.lower().replace(" ", "_") if class_type else ""
            if class_key in self.class_data:
                class_info = self.class_data[class_key]
                
                # Check class skill count
                class_skill_count = class_info.get("skills", {}).get("count", 2)
                class_skills = class_info.get("skills", {}).get("choose_from", [])
                
                # Count skills from class (excluding background skills)
                background_skills = []
                if background:
                    background_key = background.lower().replace(" ", "_")
                    if background_key in self.background_data:
                        bg_info = self.background_data[background_key]
                        background_skills = bg_info.get("proficiencies", {}).get("skills", [])
                
                class_selected_skills = [skill for skill in proficient_skills if skill not in background_skills]
                
                # Check if selected too many class skills
                if len(class_selected_skills) > class_skill_count:
                    result["valid"] = False
                    result["issues"].append(
                        f"{class_type} can only choose {class_skill_count} skills, " +
                        f"but {len(class_selected_skills)} non-background skills are selected"
                    )
                
                # Check if skills are valid for class
                for skill in class_selected_skills:
                    if skill not in class_skills:
                        result["valid"] = False
                        result["issues"].append(f"Skill '{skill}' is not available for {class_type}")
        
        # Validate background skills
        if background:
            background_key = background.lower().replace(" ", "_")
            if background_key in self.background_data:
                bg_info = self.background_data[background_key]
                bg_skills = bg_info.get("proficiencies", {}).get("skills", [])
                
                # Check if all background skills are selected
                for skill in bg_skills:
                    if skill not in proficient_skills:
                        result["valid"] = False
                        result["issues"].append(f"Background skill '{skill}' is missing")
        
        return result
    
    def validate_equipment_selections(self, equipment: Dict[str, List[Dict[str, Any]]], 
                                   class_type: str = None, background: str = None) -> Dict[str, Any]:
        """
        Validate equipment selections against class and background options.
        
        Args:
            equipment: Dictionary with equipment categories and items
            class_type: Optional class name for validation
            background: Optional background name for validation
            
        Returns:
            Dict[str, Any]: Validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check if equipment is present
        if not equipment:
            result["warnings"].append("No equipment selected")
            return result
        
        # Get equipment by category
        weapons = equipment.get("weapons", [])
        armor = equipment.get("armor", [])
        gear = equipment.get("gear", [])
        
        # Validate weapons
        for weapon in weapons:
            weapon_id = weapon.get("id")
            if not self._validate_equipment_item("weapon", weapon_id):
                result["valid"] = False
                result["issues"].append(f"Invalid weapon: {weapon_id}")
            
            # Check proficiency
            if class_type:
                proficiencies = self._get_class_weapon_proficiencies(class_type)
                if weapon.get("type") not in proficiencies and "all" not in proficiencies:
                    result["warnings"].append(
                        f"Character may not be proficient with {weapon.get('name', weapon_id)}"
                    )
        
        # Validate armor
        for armor_item in armor:
            armor_id = armor_item.get("id")
            if not self._validate_equipment_item("armor", armor_id):
                result["valid"] = False
                result["issues"].append(f"Invalid armor: {armor_id}")
            
            # Check proficiency
            if class_type:
                proficiencies = self._get_class_armor_proficiencies(class_type)
                if armor_item.get("type") not in proficiencies and "all" not in proficiencies:
                    result["valid"] = False
                    result["issues"].append(
                        f"Character is not proficient with {armor_item.get('name', armor_id)}"
                    )
        
        # Validate basic gear
        for item in gear:
            gear_id = item.get("id")
            if not self._validate_equipment_item("gear", gear_id):
                result["valid"] = False
                result["issues"].append(f"Invalid gear item: {gear_id}")
        
        # Check for missing essential equipment
        if not weapons:
            result["warnings"].append("Character has no weapons")
        
        # Check for class-specific starting equipment requirements
        if class_type:
            class_key = class_type.lower().replace(" ", "_")
            if class_key in self.class_data:
                class_info = self.class_data[class_key]
                required_types = class_info.get("required_equipment_types", [])
                
                for req_type in required_types:
                    if req_type == "weapon" and not weapons:
                        result["warnings"].append(f"{class_type} typically starts with at least one weapon")
                    elif req_type == "spellcasting_focus":
                        has_focus = any(item.get("type") == "spellcasting_focus" for item in gear)
                        if not has_focus:
                            result["warnings"].append(f"{class_type} typically needs a spellcasting focus")
        
        return result
    
    def validate_spell_selections(self, spellcasting: Dict[str, Any], 
                                class_type: str = None, level: int = 1) -> Dict[str, Any]:
        """
        Validate spell selections against class spell lists and level restrictions.
        
        Args:
            spellcasting: Dictionary with spellcasting details
            class_type: Optional class name for validation
            level: Character level for validation
            
        Returns:
            Dict[str, Any]: Validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # If not a spellcaster, return valid
        if not spellcasting.get("ability"):
            return result
        
        # If no class specified, can't validate spell list
        if not class_type:
            result["warnings"].append("Class not specified, cannot validate spell selections")
            return result
        
        class_key = class_type.lower().replace(" ", "_")
        if class_key not in self.class_data:
            result["warnings"].append(f"Unknown class {class_type}, cannot validate spell selections")
            return result
        
        class_info = self.class_data[class_key]
        
        # Check if class has spellcasting
        if "spellcasting" not in class_info:
            result["valid"] = False
            result["issues"].append(f"{class_type} is not a spellcasting class")
            return result
        
        spellcasting_info = class_info["spellcasting"]
        
        # Get cantrips and spells
        cantrips = spellcasting.get("cantrips_known", [])
        spells_known = spellcasting.get("spells_known", [])
        spells_prepared = spellcasting.get("spells_prepared", [])
        
        # Check cantrip count
        cantrips_allowed = spellcasting_info.get("cantrips_known", {}).get(str(level), 0)
        if len(cantrips) > cantrips_allowed:
            result["valid"] = False
            result["issues"].append(
                f"Too many cantrips: has {len(cantrips)}, allowed {cantrips_allowed} at level {level}"
            )
        
        # Validate cantrips
        for cantrip in cantrips:
            if not self._validate_spell(cantrip, 0, class_key):
                result["valid"] = False
                result["issues"].append(f"Invalid cantrip for {class_type}: {cantrip}")
        
        # Check known spells for classes that learn specific spells
        if "spells_known" in spellcasting_info:
            spells_allowed = spellcasting_info.get("spells_known", {}).get(str(level), 0)
            if len(spells_known) > spells_allowed:
                result["valid"] = False
                result["issues"].append(
                    f"Too many known spells: has {len(spells_known)}, allowed {spells_allowed} at level {level}"
                )
            
            # Validate known spells
            for spell in spells_known:
                spell_info = self.spells_data.get(spell, {})
                spell_level = spell_info.get("level", 0)
                
                # Check spell level - character must be able to cast that level
                max_spell_level = (level + 1) // 2  # Approximate formula
                if spell_level > max_spell_level:
                    result["valid"] = False
                    result["issues"].append(
                        f"Cannot learn level {spell_level} spell '{spell}' at character level {level}"
                    )
                
                # Check if spell is in class spell list
                if not self._validate_spell(spell, spell_level, class_key):
                    result["valid"] = False
                    result["issues"].append(f"Spell '{spell}' is not on the {class_type} spell list")
        
        # Check prepared spells for prepared casters
        if "prepared" in spellcasting_info and spells_prepared:
            # Calculate how many spells can be prepared
            spellcasting_ability = spellcasting_info.get("ability", "").lower()
            ability_modifiers = {}  # This would come from character_data in a real validation
            
            # If we don't have the actual ability modifiers, just check the spell count approximately
            max_prepared = level + 1  # Approximate without ability modifier
            
            if len(spells_prepared) > max_prepared:
                result["warnings"].append(
                    f"Possibly too many prepared spells. Check if character has enough slots."
                )
            
            # Validate prepared spells
            for spell in spells_prepared:
                spell_info = self.spells_data.get(spell, {})
                spell_level = spell_info.get("level", 0)
                
                # Check spell level - character must be able to cast that level
                max_spell_level = (level + 1) // 2  # Approximate formula
                if spell_level > max_spell_level:
                    result["valid"] = False
                    result["issues"].append(
                        f"Cannot prepare level {spell_level} spell '{spell}' at character level {level}"
                    )
                
                # Check if spell is in class spell list
                if not self._validate_spell(spell, spell_level, class_key):
                    result["valid"] = False
                    result["issues"].append(f"Spell '{spell}' is not on the {class_type} spell list")
        
        return result
    
    def validate_multiclass_requirements(self, ability_scores: Dict[str, int], 
                                      new_class: str) -> Dict[str, Any]:
        """
        Check if character meets requirements for multiclassing.
        
        Args:
            ability_scores: Dictionary of character ability scores
            new_class: Class name to multiclass into
            
        Returns:
            Dict[str, Any]: Validation results
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Normalize class name
        class_key = new_class.lower().replace(" ", "_")
        if class_key not in self.class_data:
            result["valid"] = False
            result["issues"].append(f"Unknown class {new_class}")
            return result
        
        class_info = self.class_data[class_key]
        
        # Check multiclass requirements
        multiclass_reqs = class_info.get("multiclass_requirements", {})
        
        # If no specific requirements, check primary ability
        if not multiclass_reqs:
            primary_ability = class_info.get("primary_ability", "").lower()
            if primary_ability:
                if ability_scores.get(primary_ability, 0) < 13:
                    result["valid"] = False
                    result["issues"].append(
                        f"Need at least 13 {primary_ability} to multiclass into {new_class}"
                    )
            return result
        
        # Check specific ability requirements
        for ability, min_score in multiclass_reqs.get("ability_scores", {}).items():
            if ability_scores.get(ability, 0) < min_score:
                result["valid"] = False
                result["issues"].append(
                    f"Need at least {min_score} {ability} to multiclass into {new_class}"
                )
        
        return result
    
    def generate_validation_report(self, character_data: Dict[str, Any], 
                                include_narrative: bool = False) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report for a character.
        
        Args:
            character_data: Character data dictionary
            include_narrative: Whether to include narrative feedback
            
        Returns:
            Dict[str, Any]: Detailed validation report
        """
        # Validate the character
        validation_result = self.validate_full_character(character_data)
        
        # Build a comprehensive report
        report = {
            "valid": validation_result["valid"],
            "summary": self._generate_validation_summary(validation_result),
            "issues_by_category": self._categorize_validation_issues(validation_result),
            "optimization_suggestions": self._generate_optimization_suggestions(character_data),
            "character_strengths": self._identify_character_strengths(character_data)
        }
        
        # Add narrative elements if requested
        if include_narrative:
            report["narrative_feedback"] = self._generate_narrative_feedback(character_data, validation_result)
            report["character_concept_analysis"] = self._analyze_character_concept(character_data)
            report["roleplaying_suggestions"] = self._generate_roleplaying_suggestions(character_data)
        
        return report
    
    def suggest_fixes(self, validation_issues: List[str], 
                   character_concept: Optional[str] = None) -> Dict[str, Any]:
        """
        Suggest fixes for validation issues.
        
        Args:
            validation_issues: List of validation issues
            character_concept: Optional character concept for context
            
        Returns:
            Dict[str, Any]: Suggested fixes by category
        """
        suggestions = {
            "ability_scores": [],
            "skills": [],
            "equipment": [],
            "spells": [],
            "general": []
        }
        
        for issue in validation_issues:
            issue_lower = issue.lower()
            
            # Ability score issues
            if any(term in issue_lower for term in ["ability", "score", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]):
                if "missing" in issue_lower:
                    suggestions["ability_scores"].append("Add all six ability scores to your character")
                elif "invalid" in issue_lower:
                    suggestions["ability_scores"].append("Ensure all ability scores are between 3 and 20")
                elif "primary" in issue_lower:
                    # Extract class from issue if possible
                    class_match = issue_lower.split("primary ability for ")[1].split()[0] if "primary ability for " in issue_lower else None
                    if class_match:
                        primary_ability = self._get_class_primary_ability(class_match)
                        suggestions["ability_scores"].append(
                            f"Consider making {primary_ability} your highest ability score for optimal {class_match} performance"
                        )
            
            # Skill issues
            elif any(term in issue_lower for term in ["skill", "proficiency", "expertise"]):
                if "invalid skill" in issue_lower:
                    suggestions["skills"].append("Remove invalid skills and choose from the official skill list")
                elif "expertise" in issue_lower and "without proficiency" in issue_lower:
                    skill = issue_lower.split("expertise in ")[1].split()[0]
                    suggestions["skills"].append(f"Add proficiency in {skill} before selecting it for expertise")
                elif "background skill" in issue_lower and "missing" in issue_lower:
                    skill = issue_lower.split("background skill '")[1].split("'")[0]
                    suggestions["skills"].append(f"Add the skill proficiency in {skill} from your background")
            
            # Equipment issues
            elif any(term in issue_lower for term in ["weapon", "armor", "equipment", "gear", "proficient"]):
                if "invalid" in issue_lower:
                    item_type = "weapon" if "weapon" in issue_lower else "armor" if "armor" in issue_lower else "item"
                    suggestions["equipment"].append(f"Replace the invalid {item_type} with one from the equipment list")
                elif "not proficient" in issue_lower:
                    item = issue_lower.split("not proficient with ")[1]
                    suggestions["equipment"].append(f"Choose armor your class is proficient with instead of {item}")
            
            # Spell issues
            elif any(term in issue_lower for term in ["spell", "cantrip", "spellcasting"]):
                if "too many cantrips" in issue_lower:
                    suggestions["spells"].append("Remove excess cantrips to match your class limit")
                elif "too many known spells" in issue_lower:
                    suggestions["spells"].append("Remove excess spells to match your class limit")
                elif "not on" in issue_lower and "spell list" in issue_lower:
                    spell = issue_lower.split("spell '")[1].split("'")[0] if "spell '" in issue_lower else "unknown"
                    class_name = issue_lower.split("not on the ")[1].split()[0] if "not on the " in issue_lower else "your class"
                    suggestions["spells"].append(f"Replace {spell} with a spell from the {class_name} spell list")
            
            # General fallback
            else:
                suggestions["general"].append(f"Fix issue: {issue}")
        
        # Add concept-specific suggestions if concept provided
        if character_concept:
            concept_suggestions = self._generate_concept_based_suggestions(character_concept, validation_issues)
            suggestions["concept_specific"] = concept_suggestions
        
        return suggestions
    
    def _validate_class(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate class selection."""
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if class name is provided
        if not class_data.get("name"):
            result["valid"] = False
            result["issues"].append("No class selected")
            return result
        
        # Check if class exists
        class_key = class_data.get("name", "").lower().replace(" ", "_")
        if class_key not in self.class_data:
            result["valid"] = False
            result["issues"].append(f"Invalid class: {class_data.get('name')}")
            return result
        
        # Check level range
        level = class_data.get("level", 1)
        if not isinstance(level, int) or level < 1 or level > 20:
            result["valid"] = False
            result["issues"].append(f"Invalid level: {level}. Must be between 1 and 20.")
        
        # Check subclass if high enough level
        class_info = self.class_data[class_key]
        subclass_level = class_info.get("subclass_level", 3)
        
        if level >= subclass_level and not class_data.get("subclass"):
            result["valid"] = False
            result["issues"].append(f"Subclass required at level {level}")
        
        # If subclass provided, validate it
        if class_data.get("subclass"):
            subclass = class_data["subclass"]
            subclasses = class_info.get("subclasses", {})
            
            if subclass not in subclasses:
                result["valid"] = False
                result["issues"].append(f"Invalid subclass: {subclass}")
        
        return result
    
    def _validate_species(self, species_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate species/race selection."""
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if species name is provided
        if not species_data.get("name"):
            result["valid"] = False
            result["issues"].append("No species/race selected")
            return result
        
        # Check if species exists
        species_key = species_data.get("name", "").lower().replace(" ", "_")
        if species_key not in self.species_data:
            result["valid"] = False
            result["issues"].append(f"Invalid species/race: {species_data.get('name')}")
            return result
        
        # Check subrace if applicable
        species_info = self.species_data[species_key]
        
        if species_data.get("subrace"):
            subrace = species_data["subrace"]
            subraces = species_info.get("subraces", {})
            
            if not subraces:
                result["valid"] = False
                result["issues"].append(f"{species_data['name']} does not have subraces")
            elif subrace not in subraces:
                result["valid"] = False
                result["issues"].append(f"Invalid subrace: {subrace}")
        
        return result
    
    def _validate_background(self, background_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate background selection."""
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if background name is provided
        if not background_data.get("name"):
            result["valid"] = False
            result["issues"].append("No background selected")
            return result
        
        # Check if background exists
        background_key = background_data.get("name", "").lower().replace(" ", "_")
        if background_key not in self.background_data:
            result["valid"] = False
            result["issues"].append(f"Invalid background: {background_data.get('name')}")
        
        return result
    
    def _is_standard_array(self, scores: List[int]) -> bool:
        """Check if ability scores match the standard array."""
        # Convert to sorted list for comparison
        sorted_scores = sorted(list(scores), reverse=True)
        return sorted_scores == sorted(self.standard_array)
    
    def _validate_point_buy(self, scores: Dict[str, int]) -> Tuple[bool, str, int]:
        """Validate scores against point buy rules."""
        # Check if all scores are within allowed point buy range
        for ability, score in scores.items():
            if score < self.point_buy_min or score > self.point_buy_max:
                return (False, f"{ability.capitalize()} score {score} outside point buy range", 0)
        
        # Calculate total point cost
        points_used = 0
        for score in scores.values():
            if score in self.point_buy_costs:
                points_used += self.point_buy_costs[score]
            else:
                return (False, f"Score {score} not valid in point buy system", 0)
        
        # Check if within point budget
        if points_used > self.point_buy_points:
            return (False, f"Used {points_used} points, exceeding maximum of {self.point_buy_points}", points_used)
            
        return (True, f"Valid point buy using {points_used}/{self.point_buy_points} points", points_used)
    
    def _validate_equipment_item(self, item_type: str, item_id: str) -> bool:
        """Check if an equipment item exists in the data."""
        if not self.equipment_data or not item_id:
            return False
            
        item_collection = self.equipment_data.get(f"{item_type}s", {})
        return item_id in item_collection
    
    def _validate_spell(self, spell_id: str, level: int, class_id: str) -> bool:
        """Check if a spell exists and is available to the class."""
        if not self.spells_data or not spell_id:
            return False
            
        spell = self.spells_data.get(spell_id, {})
        if not spell:
            return False
            
        # Check spell level
        if spell.get("level", 0) != level:
            return False
            
        # Check if available to class
        classes = spell.get("classes", [])
        return class_id in classes
    
    def _get_class_weapon_proficiencies(self, class_name: str) -> List[str]:
        """Get weapon proficiencies for a class."""
        class_key = class_name.lower().replace(" ", "_")
        if class_key in self.class_data:
            return self.class_data[class_key].get("proficiencies", {}).get("weapons", [])
        return []
    
    def _get_class_armor_proficiencies(self, class_name: str) -> List[str]:
        """Get armor proficiencies for a class."""
        class_key = class_name.lower().replace(" ", "_")
        if class_key in self.class_data:
            return self.class_data[class_key].get("proficiencies", {}).get("armor", [])
        return []
    
    def _get_class_primary_ability(self, class_name: str) -> str:
        """Get primary ability for a class."""
        class_key = class_name.lower().replace(" ", "_")
        if class_key in self.class_data:
            return self.class_data[class_key].get("primary_ability", "").lower()
        return ""
    
    def _check_optimization_issues(self, character_data: Dict[str, Any]) -> List[str]:
        """Check for common optimization issues."""
        warnings = []
        
        # Check if primary ability score is optimized
        class_name = character_data.get("class", {}).get("name")
        if class_name:
            primary_ability = self._get_class_primary_ability(class_name)
            if primary_ability:
                primary_score = character_data.get("ability_scores", {}).get(primary_ability, 0)
                highest_score = max(character_data.get("ability_scores", {}).values()) if character_data.get("ability_scores") else 0
                
                if primary_score < highest_score:
                    warnings.append(f"{primary_ability.capitalize()} is the primary ability for {class_name} but it's not your highest score")
        
        # Check if Constitution is too low
        con_score = character_data.get("ability_scores", {}).get("constitution", 0)
        if con_score < 12:
            warnings.append("Constitution is below 12, which may result in lower hit points")
        
        # Check for dump stats that are too low
        for ability, score in character_data.get("ability_scores", {}).items():
            if score < 8:
                warnings.append(f"Very low {ability} score ({score}) may significantly impact related checks and saves")
        
        # Check armor class if available
        ac = character_data.get("armor_class", 0)
        level = character_data.get("class", {}).get("level", 1)
        
        # Rough guideline for AC by level
        if ac > 0:  # Only if AC is calculated
            expected_ac = 12 + min(8, level // 3)  # Simple formula for expected AC growth
            if ac < expected_ac - 2:
                warnings.append(f"Armor Class ({ac}) is below recommended value for level {level}")
        
        return warnings
    
    def _generate_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate a summary of validation results."""
        if validation_result["valid"]:
            return "Character is valid according to basic D&D rules."
        else:
            issue_count = len(validation_result["issues"])
            warning_count = len(validation_result.get("warnings", []))
            
            return (
                f"Character has {issue_count} rule violation{'s' if issue_count != 1 else ''} "
                f"and {warning_count} warning{'s' if warning_count != 1 else ''}."
            )
    
    def _categorize_validation_issues(self, validation_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize validation issues by type."""
        categories = {
            "ability_scores": [],
            "class": [],
            "species": [],
            "background": [],
            "skills": [],
            "equipment": [],
            "spells": [],
            "general": []
        }
        
        # Helper function to categorize an issue
        def categorize_issue(issue):
            issue_lower = issue.lower()
            
            if any(term in issue_lower for term in ["ability", "score", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]):
                categories["ability_scores"].append(issue)
            elif any(term in issue_lower for term in ["class", "subclass", "level"]):
                categories["class"].append(issue)
            elif any(term in issue_lower for term in ["species", "race", "subrace"]):
                categories["species"].append(issue)
            elif "background" in issue_lower:
                categories["background"].append(issue)
            elif any(term in issue_lower for term in ["skill", "expertise", "proficiency"]):
                categories["skills"].append(issue)
            elif any(term in issue_lower for term in ["equipment", "weapon", "armor", "gear"]):
                categories["equipment"].append(issue)
            elif any(term in issue_lower for term in ["spell", "cantrip", "spellcasting"]):
                categories["spells"].append(issue)
            else:
                categories["general"].append(issue)
        
        # Categorize issues
        for issue in validation_result.get("issues", []):
            categorize_issue(issue)
        
        # Categorize warnings
        for warning in validation_result.get("warnings", []):
            categorize_issue(warning)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_optimization_suggestions(self, character_data: Dict[str, Any]) -> List[str]:
        """Generate suggestions to optimize character build."""
        suggestions = []
        
        class_name = character_data.get("class", {}).get("name")
        level = character_data.get("class", {}).get("level", 1)
        primary_ability = None
        
        if class_name:
            class_key = class_name.lower().replace(" ", "_")
            if class_key in self.class_data:
                class_info = self.class_data[class_key]
                primary_ability = class_info.get("primary_ability", "").lower()
        
        # Check ability score distribution
        if primary_ability:
            primary_score = character_data.get("ability_scores", {}).get(primary_ability, 0)
            highest_score = max(character_data.get("ability_scores", {}).values()) if character_data.get("ability_scores") else 0
            
            if primary_score < highest_score:
                suggestions.append(
                    f"Consider making {primary_ability} your highest ability score for optimal {class_name} performance."
                )
        
        # Check for feats vs ASI
        # This would require more character data about feat selections
        
        # Check equipment optimization
        armor = character_data.get("equipment", {}).get("armor", [])
        if class_name and armor:
            # Check if using best armor available for class
            armor_proficiencies = self._get_class_armor_proficiencies(class_name)
            
            if "heavy" in armor_proficiencies:
                has_heavy = any(item.get("type") == "heavy" for item in armor)
                if not has_heavy:
                    suggestions.append(
                        f"Consider using heavy armor for better protection since {class_name} is proficient with it."
                    )
        
        # Check spellcasting optimization
        if character_data.get("spellcasting", {}).get("ability"):
            spells_known = character_data.get("spellcasting", {}).get("spells_known", [])
            
            # Check if character has enough damage spells
            damage_spells = sum(1 for spell_id in spells_known if "damage" in self.spells_data.get(spell_id, {}).get("tags", []))
            if damage_spells == 0:
                suggestions.append("Consider adding at least one damage-dealing spell to your repertoire.")
            
            # Check for utility spells
            utility_spells = sum(1 for spell_id in spells_known if "utility" in self.spells_data.get(spell_id, {}).get("tags", []))
            if utility_spells == 0:
                suggestions.append("Consider adding utility spells for versatility outside of combat.")
        
        return suggestions
    
    def _identify_character_strengths(self, character_data: Dict[str, Any]) -> List[str]:
        """Identify character's strengths based on build."""
        strengths = []
        
        # Get basic character info
        class_name = character_data.get("class", {}).get("name")
        ability_scores = character_data.get("ability_scores", {})
        
        # Check for high ability scores
        for ability, score in ability_scores.items():
            if score >= 16:
                strengths.append(f"High {ability.capitalize()} ({score})")
        
        # Class-specific strengths
        if class_name:
            class_key = class_name.lower().replace(" ", "_")
            
            if class_key == "fighter":
                strengths.append("Good combat capability")
            elif class_key == "wizard":
                int_score = ability_scores.get("intelligence", 0)
                if int_score >= 16:
                    strengths.append("Strong spellcasting with high Intelligence")
            elif class_key == "rogue":
                dex_score = ability_scores.get("dexterity", 0)
                if dex_score >= 16:
                    strengths.append("Excellent stealth and skill capability")
        
        # Check for skill expertise
        expertise = character_data.get("skills", {}).get("expertise", [])
        if expertise:
            for skill in expertise:
                strengths.append(f"Expertise in {skill}")
        
        # Check for good saving throws
        if class_name:
            class_key = class_name.lower().replace(" ", "_")
            if class_key in self.class_data:
                class_info = self.class_data[class_key]
                saving_throws = class_info.get("saving_throws", [])
                
                for save in saving_throws:
                    if ability_scores.get(save, 0) >= 14:
                        strengths.append(f"Strong {save.capitalize()} saves")
        
        return strengths
    
    def _generate_narrative_feedback(self, character_data: Dict[str, Any], 
                                   validation_result: Dict[str, Any]) -> str:
        """Generate narrative feedback about the character."""
        # This would typically connect to an LLM for more natural language feedback
        # Here we'll just generate a simple narrative
        
        class_name = character_data.get("class", {}).get("name", "adventurer")
        species = character_data.get("species", {}).get("name", "unknown species")
        background = character_data.get("background", {}).get("name", "mysterious past")
        char_name = character_data.get("name", "unnamed character")
        
        if validation_result["valid"]:
            return (
                f"{char_name}, the {species} {class_name} with a {background} background, "
                f"is well-constructed and ready for adventure. The character adheres to the "
                f"rules of D&D and should be effective in gameplay."
            )
        else:
            issue_count = len(validation_result.get("issues", []))
            return (
                f"{char_name}, the {species} {class_name} with a {background} background, "
                f"has {issue_count} issue{'s' if issue_count != 1 else ''} that need{'s' if issue_count == 1 else ''} "
                f"attention before the character is ready for adventure."
            )
    
    def _analyze_character_concept(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze character concept for thematic coherence."""
        # This would typically connect to an LLM for deeper concept analysis
        # Here we'll just do a basic analysis
        
        concept = {
            "thematic_coherence": "medium",
            "notes": []
        }
        
        class_name = character_data.get("class", {}).get("name")
        species = character_data.get("species", {}).get("name")
        background = character_data.get("background", {}).get("name")
        
        # Some basic class-race synergy checks
        if class_name and species:
            # These are very simplified examples
            if class_name == "barbarian" and species == "half-orc":
                concept["thematic_coherence"] = "high"
                concept["notes"].append("Half-orc barbarian is a classic, synergistic combination")
            elif class_name == "wizard" and species == "high-elf":
                concept["thematic_coherence"] = "high"
                concept["notes"].append("High-elf wizard is a classic, synergistic combination")
            elif class_name == "fighter" and species == "dwarf":
                concept["thematic_coherence"] = "high"
                concept["notes"].append("Dwarf fighter is a classic, synergistic combination")
        
        # Check if background aligns with class
        if class_name and background:
            if class_name == "rogue" and background == "criminal":
                concept["thematic_coherence"] = "high"
                concept["notes"].append("Criminal background complements the rogue class well")
            elif class_name == "cleric" and background == "acolyte":
                concept["thematic_coherence"] = "high"
                concept["notes"].append("Acolyte background naturally aligns with the cleric class")
        
        return concept
    
    def _generate_roleplaying_suggestions(self, character_data: Dict[str, Any]) -> List[str]:
        """Generate roleplaying suggestions based on character build."""
        # This would typically connect to an LLM for more creative suggestions
        # Here we'll just provide basic suggestions
        
        suggestions = []
        
        class_name = character_data.get("class", {}).get("name")
        background = character_data.get("background", {}).get("name")
        personality = character_data.get("personality", {})
        
        # Class-based suggestions
        if class_name == "barbarian":
            suggestions.append("Consider how your character manages their rage outside of combat")
        elif class_name == "bard":
            suggestions.append("Think about your character's preferred art form and performance style")
        elif class_name == "cleric":
            suggestions.append("Consider how your character expresses their devotion to their deity in daily life")
        
        # Background-based suggestions
        if background == "soldier":
            suggestions.append("Consider which military unit your character served in and how it shaped them")
        elif background == "sage":
            suggestions.append("Think about your character's area of academic expertise and how they apply it")
        elif background == "outlander":
            suggestions.append("Consider how your character adapts to civilized environments after living in the wild")
        
        # Add a general suggestion if we don't have specific ones
        if not suggestions:
            suggestions.append(
                "Consider how your character's class abilities and background experiences shape their personality and approach to challenges"
            )
        
        return suggestions
    
    def _generate_concept_based_suggestions(self, concept: str, issues: List[str]) -> List[str]:
        """Generate concept-specific suggestions based on validation issues."""
        # This would typically connect to an LLM for more tailored suggestions
        # Here we'll just use simple keyword matching
        
        suggestions = []
        concept_lower = concept.lower()
        
        # Check concept keywords
        if "tactician" in concept_lower or "strategic" in concept_lower:
            suggestions.append("For a tactician concept, consider prioritizing Intelligence and acquiring tactical skills")
        
        if "healer" in concept_lower or "medic" in concept_lower:
            suggestions.append("For a healer concept, ensure you have healing spells or the Medicine skill")
        
        if "tank" in concept_lower or "defender" in concept_lower:
            suggestions.append("For a defensive character, prioritize Constitution and consider heavy armor if proficient")
        
        # Add a default suggestion if none match
        if not suggestions:
            suggestions.append(f"Consider how your character's abilities and choices reflect their concept: '{concept}'")
        
        return suggestions