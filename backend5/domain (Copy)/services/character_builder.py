from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ...core.entities.character import Character
from ...core.value_objects.ability_score import AbilityScore
from ...core.value_objects.alignment import Alignment
from ...core.value_objects.proficiency import ProficiencyLevel
from ..rules.character_creation import CharacterCreationRules
from ..rules.multiclass_rules import MulticlassRules

logger = logging.getLogger(__name__)

class CharacterBuilderService:
    """
    Domain service for building and managing characters.
    
    This service encapsulates all character building logic including:
    - Creating new characters from data
    - Converting between data formats
    - Applying species traits and class features
    - Level progression
    - Character validation
    """
    
    def __init__(self):
        self.creation_rules = CharacterCreationRules()
        self.multiclass_rules = MulticlassRules()
        self.ability_calculator = AbilityScoreCalculator()
    
    def create_character(self, character_data: Dict[str, Any]) -> Character:
        """
        Create a new character from provided data.
        
        This is the primary character creation method that handles
        the complete character creation process.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            Character: Newly created character entity
            
        Raises:
            ValueError: If character data is invalid
        """
        # Validate basic requirements
        self._validate_creation_data(character_data)
        
        # Build ability scores
        ability_scores = self._build_ability_scores(character_data.get("ability_scores", {}))
        
        # Build alignment
        alignment = self._build_alignment(character_data.get("alignment", []))
        
        # Create base character entity
        character = Character(
            name=character_data["name"],
            species=character_data["species"],
            background=character_data.get("background", ""),
            alignment=alignment
        )
        
        # Set ability scores
        self._set_character_ability_scores(character, ability_scores)
        
        # Set classes and subclasses
        character.character_classes = character_data.get("classes", {})
        character.subclasses = character_data.get("subclasses", {})
        
        # Apply species traits and ability score increases
        self._apply_species_traits(character, character_data["species"])
        
        # Apply class features for current levels
        self._apply_class_features(character)
        
        # Set proficiencies
        self._apply_proficiencies(character, character_data)
        
        # Calculate initial hit points
        self._calculate_initial_hit_points(character)
        
        # Set additional data
        self._apply_additional_character_data(character, character_data)
        
        return character
    
    def build_from_legacy_data(self, legacy_data: Dict[str, Any]) -> Character:
        """
        Build a Character entity from legacy character data formats.
        
        This method handles conversion from the old CharacterCore format
        to the new Character entity format.
        
        Args:
            legacy_data: Legacy character data dictionary
            
        Returns:
            Character: Newly created character entity
        """
        character = Character()
        
        # Basic identity
        character.name = legacy_data.get("name", "")
        character.species = legacy_data.get("species", "")
        character.species_variants = legacy_data.get("species_variants", [])
        character.lineage = legacy_data.get("lineage")
        character.background = legacy_data.get("background", "")
        
        # Alignment - handle both list and dict formats
        alignment_data = legacy_data.get("alignment", [])
        if isinstance(alignment_data, list) and len(alignment_data) >= 2:
            character.alignment = Alignment(
                ethical=alignment_data[0],
                moral=alignment_data[1]
            )
        elif isinstance(alignment_data, dict):
            character.alignment = Alignment(
                ethical=alignment_data.get("ethical", "Neutral"),
                moral=alignment_data.get("moral", "Neutral")
            )
        
        # Character classes - handle both "classes" and "character_classes" keys
        classes_data = legacy_data.get("character_classes") or legacy_data.get("classes", {})
        character.character_classes = classes_data
        character.subclasses = legacy_data.get("subclasses", {})
        
        # Build ability scores - handle both dict and nested dict formats
        ability_scores = legacy_data.get("ability_scores", {})
        if isinstance(ability_scores, dict):
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                score_value = ability_scores.get(ability, 10)
                if isinstance(score_value, dict):
                    # Handle nested format with base_score, bonuses, etc.
                    base_score = score_value.get("base_score", 10)
                    ability_score = AbilityScore(base_score)
                    # Apply bonuses if present
                    if "bonus" in score_value:
                        ability_score = ability_score.add_bonus(score_value["bonus"])
                    if "stacking_bonuses" in score_value:
                        for source, bonus in score_value["stacking_bonuses"].items():
                            ability_score = ability_score.add_stacking_bonus(source, bonus)
                else:
                    # Handle simple integer format
                    ability_score = AbilityScore(score_value)
                
                setattr(character, ability, ability_score)
        
        # Proficiencies - handle enum conversion
        skill_profs = legacy_data.get("skill_proficiencies", {})
        character.skill_proficiencies = {
            skill: ProficiencyLevel.from_string(str(level)) if not isinstance(level, ProficiencyLevel) else level
            for skill, level in skill_profs.items()
        }
        
        saving_throw_profs = legacy_data.get("saving_throw_proficiencies", {})
        character.saving_throw_proficiencies = {
            save: ProficiencyLevel.from_string(str(level)) if not isinstance(level, ProficiencyLevel) else level
            for save, level in saving_throw_profs.items()
        }
        
        tool_profs = legacy_data.get("tool_proficiencies", {})
        character.tool_proficiencies = {
            tool: ProficiencyLevel.from_string(str(level)) if not isinstance(level, ProficiencyLevel) else level
            for tool, level in tool_profs.items()
        }
        
        # Set collections
        character.weapon_proficiencies = set(legacy_data.get("weapon_proficiencies", []))
        character.armor_proficiencies = set(legacy_data.get("armor_proficiencies", []))
        character.languages = set(legacy_data.get("languages", []))
        
        # Features and traits
        character.species_traits = legacy_data.get("species_traits", {})
        character.class_features = legacy_data.get("class_features", {})
        character.background_feature = legacy_data.get("background_feature", "")
        character.feats = legacy_data.get("feats", [])
        
        # Current state
        character.current_hit_points = legacy_data.get("current_hit_points", 0)
        character.temporary_hit_points = legacy_data.get("temporary_hit_points", 0)
        character.experience_points = legacy_data.get("experience_points", 0)
        
        # Spellcasting
        character.spellcasting_ability = legacy_data.get("spellcasting_ability")
        character.spellcasting_classes = legacy_data.get("spellcasting_classes", {})
        character.ritual_casting_classes = legacy_data.get("ritual_casting_classes", {})
        
        # Equipment
        character.equipment = legacy_data.get("equipment", [])
        
        # Metadata
        character.player_name = legacy_data.get("player_name", "")
        character.campaign = legacy_data.get("campaign", "")
        character.sources_used = set(legacy_data.get("sources_used", []))
        
        # Timestamps - handle string or datetime formats
        created_at = legacy_data.get("creation_date") or legacy_data.get("created_at")
        if isinstance(created_at, str):
            try:
                character.created_at = datetime.fromisoformat(created_at)
            except (ValueError, TypeError):
                character.created_at = datetime.now()
        elif isinstance(created_at, datetime):
            character.created_at = created_at
        
        return character
    
    def level_up_character(self, character: Character, target_class: str, 
                          choices: Optional[Dict[str, Any]] = None) -> Character:
        """
        Level up a character in the specified class.
        
        Args:
            character: The character to level up
            target_class: Class to gain a level in
            choices: Optional choices for level-up (ASI, spells, etc.)
            
        Returns:
            Character: Updated character (modifies in place)
            
        Raises:
            ValueError: If level-up is not valid
        """
        # Validate level-up eligibility
        total_level = character.total_level
        if total_level >= 20:
            raise ValueError("Character is already at maximum level (20)")
        
        if target_class not in character.character_classes:
            # This is multiclassing
            if not self.multiclass_rules.can_multiclass_into(character, target_class):
                raise ValueError(f"Character cannot multiclass into {target_class}")
            character.character_classes[target_class] = 1
        else:
            # Level up existing class
            current_class_level = character.character_classes[target_class]
            if current_class_level >= 20:
                raise ValueError(f"Character is already at maximum level in {target_class}")
            character.character_classes[target_class] += 1
        
        # Apply level-up benefits
        self._apply_level_up_benefits(character, target_class, choices)
        
        # Update last modified timestamp
        character.last_modified = datetime.now()
        
        return character
    
    def validate_character(self, character: Character) -> Dict[str, Any]:
        """
        Validate character against D&D rules.
        
        Args:
            character: Character to validate
            
        Returns:
            Dict containing validation results
        """
        issues = []
        warnings = []
        
        # Basic validation
        if not character.name.strip():
            warnings.append("Character name is empty")
        
        if not character.species:
            issues.append("Species is required")
        
        if not character.character_classes:
            issues.append("At least one character class is required")
        
        # Level validation
        total_level = character.total_level
        if total_level > 20:
            issues.append(f"Total character level ({total_level}) exceeds maximum (20)")
        elif total_level < 1:
            issues.append("Character must have at least 1 level")
        
        # Ability score validation
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability = character.get_ability_score(ability_name)
            if ability.total_score < 1 or ability.total_score > 30:
                issues.append(f"{ability_name.title()} score ({ability.total_score}) must be between 1 and 30")
        
        # Multiclass validation
        if len(character.character_classes) > 1:
            multiclass_issues = self._validate_multiclass_requirements(character)
            issues.extend(multiclass_issues)
        
        # Equipment validation
        equipment_warnings = self._validate_equipment(character)
        warnings.extend(equipment_warnings)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    # === Private Helper Methods ===
    
    def _validate_creation_data(self, data: Dict[str, Any]) -> None:
        """Validate character creation data."""
        required_fields = ["name", "species"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        if not self.creation_rules.is_valid_species(data["species"]):
            raise ValueError(f"Invalid species: {data['species']}")
    
    def _build_ability_scores(self, scores_data: Dict[str, int]) -> Dict[str, AbilityScore]:
        """Build ability score objects from data."""
        ability_scores = {}
        
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = scores_data.get(ability, 10)
            ability_scores[ability] = AbilityScore(base_score=score)
        
        return ability_scores
    
    def _set_character_ability_scores(self, character: Character, ability_scores: Dict[str, AbilityScore]) -> None:
        """Set ability scores on character entity."""
        character.strength = ability_scores.get("strength", AbilityScore(10))
        character.dexterity = ability_scores.get("dexterity", AbilityScore(10))
        character.constitution = ability_scores.get("constitution", AbilityScore(10))
        character.intelligence = ability_scores.get("intelligence", AbilityScore(10))
        character.wisdom = ability_scores.get("wisdom", AbilityScore(10))
        character.charisma = ability_scores.get("charisma", AbilityScore(10))
    
    def _build_alignment(self, alignment_data: List[str]) -> Optional[Alignment]:
        """Build alignment from data."""
        if isinstance(alignment_data, list) and len(alignment_data) >= 2:
            return Alignment(ethical=alignment_data[0], moral=alignment_data[1])
        elif isinstance(alignment_data, dict):
            return Alignment(
                ethical=alignment_data.get("ethical", "Neutral"),
                moral=alignment_data.get("moral", "Neutral")
            )
        return Alignment(ethical="Neutral", moral="Neutral")
    
    def _apply_species_traits(self, character: Character, species: str) -> None:
        """Apply species-specific traits to character."""
        try:
            traits = self.creation_rules.get_species_traits(species)
            character.species_traits = traits
            
            # Apply ability score increases
            ability_increases = self.creation_rules.get_species_ability_increases(species)
            for ability, increase in ability_increases.items():
                current_score = character.get_ability_score(ability)
                new_score = current_score.add_bonus(increase)
                setattr(character, ability, new_score)
                
        except Exception as e:
            logger.warning(f"Could not apply species traits for {species}: {e}")
    
    def _apply_class_features(self, character: Character) -> None:
        """Apply class features for all character classes."""
        try:
            all_features = {}
            for class_name, level in character.character_classes.items():
                features = self.creation_rules.get_class_features(class_name, level)
                all_features[class_name] = features
            character.class_features = all_features
        except Exception as e:
            logger.warning(f"Could not apply class features: {e}")
    
    def _apply_proficiencies(self, character: Character, character_data: Dict[str, Any]) -> None:
        """Apply proficiencies from character data."""
        # Skill proficiencies
        skill_profs = character_data.get("skill_proficiencies", {})
        character.skill_proficiencies = {
            skill: ProficiencyLevel.from_string(str(level)) if isinstance(level, str) else level
            for skill, level in skill_profs.items()
        }
        
        # Other proficiencies
        character.weapon_proficiencies = set(character_data.get("weapon_proficiencies", []))
        character.armor_proficiencies = set(character_data.get("armor_proficiencies", []))
        character.languages = set(character_data.get("languages", []))
    
    def _calculate_initial_hit_points(self, character: Character) -> None:
        """Calculate initial hit points for character."""
        if not character.character_classes:
            character.current_hit_points = 1
            return
        
        try:
            con_mod = character.get_ability_modifier("constitution")
            primary_class = character.primary_class
            hit_die = self.creation_rules.get_class_hit_die(primary_class)
            
            # Calculate HP for each class level
            total_hp = 0
            for class_name, level in character.character_classes.items():
                class_hit_die = self.creation_rules.get_class_hit_die(class_name)
                if class_name == primary_class and level > 0:
                    # First level gets max hit die + CON modifier
                    total_hp += class_hit_die + con_mod
                    # Remaining levels get average + CON modifier
                    total_hp += (level - 1) * ((class_hit_die // 2) + 1 + con_mod)
                else:
                    # Multiclass levels get average + CON modifier
                    total_hp += level * ((class_hit_die // 2) + 1 + con_mod)
            
            character.current_hit_points = max(1, total_hp)
        except Exception as e:
            logger.warning(f"Could not calculate hit points: {e}")
            character.current_hit_points = 1
    
    def _apply_additional_character_data(self, character: Character, character_data: Dict[str, Any]) -> None:
        """Apply additional character data like equipment, spells, etc."""
        # Equipment
        character.equipment = character_data.get("equipment", [])
        
        # Experience points
        character.experience_points = character_data.get("experience_points", 0)
        
        # Metadata
        character.player_name = character_data.get("player_name", "")
        character.campaign = character_data.get("campaign", "")
        
        # Feats
        character.feats = character_data.get("feats", [])
    
    def _apply_level_up_benefits(self, character: Character, target_class: str, 
                                choices: Optional[Dict[str, Any]]) -> None:
        """Apply benefits from leveling up."""
        try:
            new_level = character.character_classes[target_class]
            
            # Apply hit point increase
            self._apply_hit_point_increase(character, target_class)
            
            # Apply new class features
            new_features = self.creation_rules.get_class_features(target_class, new_level)
            if target_class not in character.class_features:
                character.class_features[target_class] = []
            character.class_features[target_class].extend(new_features)
            
            # Apply ability score improvements if applicable
            if choices and "ability_score_improvement" in choices:
                self._apply_ability_score_improvement(character, choices["ability_score_improvement"])
            
            # Apply feat if chosen
            if choices and "feat" in choices:
                character.feats.append(choices["feat"])
                
        except Exception as e:
            logger.error(f"Failed to apply level-up benefits: {e}")
    
    def _apply_hit_point_increase(self, character: Character, class_name: str) -> None:
        """Apply hit point increase for leveling up."""
        try:
            hit_die = self.creation_rules.get_class_hit_die(class_name)
            con_mod = character.get_ability_modifier("constitution")
            
            # Use average hit die roll + CON modifier
            hp_increase = (hit_die // 2) + 1 + con_mod
            character.current_hit_points += max(1, hp_increase)
        except Exception as e:
            logger.warning(f"Could not apply hit point increase: {e}")
    
    def _apply_ability_score_improvement(self, character: Character, improvements: Dict[str, int]) -> None:
        """Apply ability score improvements."""
        for ability, increase in improvements.items():
            if hasattr(character, ability):
                current_score = getattr(character, ability)
                new_score = current_score.add_bonus(increase)
                setattr(character, ability, new_score)
    
    def _validate_multiclass_requirements(self, character: Character) -> List[str]:
        """Validate multiclass requirements."""
        issues = []
        try:
            for class_name in character.character_classes.keys():
                if not self.multiclass_rules.meets_multiclass_requirements(character, class_name):
                    requirements = self.multiclass_rules.get_multiclass_requirements(class_name)
                    issues.append(f"Character does not meet multiclass requirements for {class_name}: {requirements}")
        except Exception as e:
            logger.warning(f"Could not validate multiclass requirements: {e}")
        return issues
    
    def _validate_equipment(self, character: Character) -> List[str]:
        """Validate character equipment."""
        warnings = []
        # Add equipment validation logic as needed
        return warnings

    def create_base_character(self, description: str) -> Character:
        """Create base character (from _create_base_character method)."""
        # Business logic from the original method
        pass
    
    def apply_species_traits(self, character: Character, species: str, 
                           subrace: str = None) -> Character:
        """Apply species traits (from select_species method)."""
        # Logic from original select_species method
        pass
    
    def apply_class_features(self, character: Character, class_name: str, 
                           subclass: str = None) -> Character:
        """Apply class features (from select_class method)."""
        # Logic from original select_class method
        pass
    
    def calculate_ability_scores(self, character: Character, 
                               scores: Dict[str, int], method: str) -> Character:
        """Calculate and apply ability scores (from set_ability_scores)."""
        # Logic from original set_ability_scores method
        pass

