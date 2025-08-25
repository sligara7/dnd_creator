"""
Character creation service.

This service handles all aspects of character creation including:
- Core character data management
- Character validation and creation rules
- Character templates and presets
- Multi-step character creation
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.core_models import AbilityScore, CharacterCore
from src.models.database_models import Character as CharacterDB
from src.services.character.ability import AbilityService
from src.services.character.equipment import EquipmentService
from src.services.character.validation import validate_character_data
from src.services.character.theme_manager import ThemeManager
from src.services.character.cr_calculator import CRCalculator
from src.services.data.rules import (
    get_appropriate_weapons_for_character,
    get_appropriate_spells_for_character,
    get_appropriate_equipment_for_character,
    get_appropriate_feats_for_character
)

logger = logging.getLogger(__name__)

class CharacterCreationService:
    """Service for managing character creation."""
    
    def __init__(self, db: Session, ability_service: Optional[AbilityService] = None,
                 equipment_service: Optional[EquipmentService] = None,
                 theme_manager: Optional[ThemeManager] = None,
                 cr_calculator: Optional[CRCalculator] = None):
        self.db = db
        self.ability_service = ability_service or AbilityService()
        self.equipment_service = equipment_service or EquipmentService(db)
        self.theme_manager = theme_manager or ThemeManager()
        self.cr_calculator = cr_calculator or CRCalculator()
        
    async def create_character(self, character_data: Dict[str, Any]) -> CharacterDB:
        """Create a new character from provided data."""
        # Validate character data
        validation_result = validate_character_data(character_data)
        if not validation_result.success:
            logger.error("Character validation failed", 
                        error=validation_result.error,
                        warnings=validation_result.warnings)
            raise ValueError(validation_result.error)
        
            # Calculate CR (useful for encounter balancing)
            cr = self.cr_calculator.calculate_cr(character_data)
            character_data["challenge_rating"] = cr
            character_data["effective_cr_factors"] = self.cr_calculator._extract_cr_factors(character_data)
            
            # Create character in database
            try:
            character = CharacterDB(
                id=str(uuid.uuid4()),
                name=character_data["name"],
                player_name=character_data["player_name"],
                species=character_data["species"],
                background=character_data["background"],
                level=1,
                character_classes=character_data.get("character_classes", {}),
                ability_scores=character_data.get("ability_scores", {}),
                created_at=datetime.utcnow()
            )
            
            self.db.add(character)
            self.db.commit()
            self.db.refresh(character)
            
            # Set up initial ability scores
            await self._setup_ability_scores(character, character_data)
            
            # Set up initial equipment
            await self._setup_initial_equipment(character, character_data)
            
            # Set up spells if applicable
            await self._setup_initial_spells(character, character_data)
            
            logger.info("Character created successfully", character_id=character.id)
            return character
            
        except Exception as e:
            self.db.rollback()
            logger.error("Character creation failed", error=str(e))
            raise
            
    async def _setup_ability_scores(self, character: CharacterDB, 
                                  character_data: Dict[str, Any]) -> None:
        """Set up initial ability scores for new character."""
        ability_scores = character_data.get("ability_scores", {})
        if not ability_scores:
            # Use standard array if no scores provided
            ability_scores = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        
        # Create ability scores through ability service
        for ability, score in ability_scores.items():
            base_score = AbilityScore(score)
            
            # Apply racial bonuses if any
            racial_bonus = character_data.get("racial_bonuses", {}).get(ability, 0)
            if racial_bonus:
                base_score.add_bonus(racial_bonus, "RACE", f"{character.species} Racial Bonus")
            
            setattr(character, ability, base_score)
        
        self.db.commit()
            
    async def _setup_initial_equipment(self, character: CharacterDB,
                                     character_data: Dict[str, Any]) -> None:
        """Set up initial equipment for new character."""
        # Get appropriate weapons based on class
        weapons = get_appropriate_weapons_for_character(character_data)
        
        # Assign starting equipment
        await self.equipment_service.assign_equipment(
            character_id=character.id,
            equipment_list=weapons,
            access_type="equipped"
        )
        
    async def _setup_initial_spells(self, character: CharacterDB,
                                  character_data: Dict[str, Any]) -> None:
        """Set up initial spells for spellcasting classes."""
        # Check if character has spellcasting classes
        spellcasting_classes = {"Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard"}
        character_classes = character_data.get("character_classes", {})
        
        if any(cls in spellcasting_classes for cls in character_classes):
            spells = get_appropriate_spells_for_character(character_data)
            
            # Store spells in character data
            character.spells_known = spells.get("known", [])
            character.spells_prepared = spells.get("prepared", [])
            
            self.db.commit()
            
    async def create_character_from_concept(self, concept: str, theme: Optional[str] = None,
                                          preferences: Optional[Dict[str, Any]] = None) -> CharacterDB:
        """Create a character from a concept description with optional theme."""
        try:
            # Generate character data from concept
            character_data = await self._generate_character_from_concept(concept, theme, preferences)
            
            # Create character using generated data
            character = await self.create_character(character_data)
            
            # Apply theme if provided
            if theme:
                character = await self.apply_theme(character.id, theme)
            
            return character
            
        except Exception as e:
            logger.error(f"Character creation from concept failed: {e}")
            raise

    async def _generate_character_from_concept(self, concept: str, theme: Optional[str],
                                             preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete character data from concept description."""
        # Build theme-aware prompt
        prompt = self._build_character_prompt(concept, theme, preferences)
        
        # Generate initial character data using LLM
        character_data = await self.theme_manager.generate_character_data(prompt)
        
        # Enhance with appropriate game elements
        character_data.update(await self._generate_ability_scores(character_data, concept))
        character_data.update(await self._generate_class_features(character_data, concept))
        character_data.update(await self._generate_equipment(character_data, concept, theme))
        
        if self._is_spellcaster(character_data):
            character_data.update(await self._generate_spells(character_data, concept, theme))
        
        return character_data

    def _build_character_prompt(self, concept: str, theme: Optional[str],
                              preferences: Optional[Dict[str, Any]]) -> str:
        """Build comprehensive prompt for character creation."""
        prompt_parts = [
            f"Create a D&D 5e character based on this concept: {concept}\n",
            "Ensure all components work together to support the concept."
        ]

        if theme:
            prompt_parts.append(f"\nTheme: {theme}")
            prompt_parts.append("All components should fit this theme while following D&D 5e rules.")

        if preferences:
            prompt_parts.append("\nPreferences:")
            for key, value in preferences.items():
                prompt_parts.append(f"- {key}: {value}")

        return "\n".join(prompt_parts)

    async def _generate_ability_scores(self, character_data: Dict[str, Any],
                                     concept: str) -> Dict[str, Any]:
        """Generate thematically appropriate ability scores."""
        prompt = f"""Generate D&D 5e ability scores for this character. Return ONLY JSON:

        CHARACTER CONCEPT:
        {concept}

        CURRENT CHARACTER:
        {character_data}

        Generate ability scores that:
        1. Support the character concept
        2. Follow D&D 5e rules
        3. Prioritize scores needed for class features

        Return JSON with ability scores."""

        scores = await self.theme_manager.generate_with_llm(prompt)
        return scores

    async def _generate_class_features(self, character_data: Dict[str, Any],
                                     concept: str) -> Dict[str, Any]:
        """Generate appropriate class features."""
        prompt = f"""Generate D&D 5e class features for this character. Return ONLY JSON:

        CHARACTER CONCEPT:
        {concept}

        CURRENT CHARACTER:
        {character_data}

        Generate class features that:
        1. Match the character concept
        2. Follow D&D 5e rules
        3. Work together cohesively

        Return JSON with class features."""

        features = await self.theme_manager.generate_with_llm(prompt)
        return features

    async def _generate_equipment(self, character_data: Dict[str, Any],
                               concept: str, theme: Optional[str]) -> Dict[str, Any]:
        """Generate thematically appropriate equipment."""
        prompt = f"""Generate D&D 5e equipment for this character. Return ONLY JSON:

        CHARACTER CONCEPT:
        {concept}

        CURRENT CHARACTER:
        {character_data}

        THEME: {theme if theme else 'Standard D&D'}

        Generate equipment that:
        1. Fits the character concept
        2. Matches the theme
        3. Follows D&D 5e rules
        4. Is appropriate for the character's abilities

        Return JSON with equipment."""

        equipment = await self.theme_manager.generate_with_llm(prompt)
        return equipment

    async def _generate_spells(self, character_data: Dict[str, Any],
                            concept: str, theme: Optional[str]) -> Dict[str, Any]:
        """Generate thematically appropriate spells."""
        prompt = f"""Generate D&D 5e spells for this character. Return ONLY JSON:

        CHARACTER CONCEPT:
        {concept}

        CURRENT CHARACTER:
        {character_data}

        THEME: {theme if theme else 'Standard D&D'}

        Generate spells that:
        1. Match the character concept
        2. Fit the theme
        3. Follow D&D 5e rules
        4. Are appropriate for the character's level and class

        Return JSON with spells."""

        spells = await self.theme_manager.generate_with_llm(prompt)
        return spells

    async def apply_theme(self, character_id: str, theme: str) -> CharacterDB:
        """Apply a theme to an existing character."""
        character = self.db.query(CharacterDB).filter(CharacterDB.id == character_id).first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        # Get current theme if any
        current_theme = character.theme

        try:
            # Generate theme mapping
            theme_mapping = await self.theme_manager.generate_theme_mapping(
                current_theme, theme, character.to_dict())

            # Apply theme mapping
            themed_data = await self.theme_manager.apply_theme_mapping(
                character.to_dict(), theme_mapping)

            # Update character with themed data
            for key, value in themed_data.items():
                if hasattr(character, key):
                    setattr(character, key, value)

            character.theme = theme
            self.db.commit()

            return character

        except Exception as e:
            self.db.rollback()
            logger.error(f"Theme application failed: {e}")
            raise

    async def suggest_alternatives(self, character_id: str, aspect: str,
                                 count: int = 3) -> List[Dict[str, Any]]:
        """Suggest alternatives for a character aspect."""
        character = self.db.query(CharacterDB).filter(CharacterDB.id == character_id).first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        return await self.theme_manager.generate_alternatives(
            character.to_dict(), aspect, character.theme, count)

    def get_creation_templates(self) -> List[Dict[str, Any]]:
        """Get available character creation templates."""
        return [
            {
                "name": "Quick Build Fighter",
                "description": "Pre-configured Fighter optimized for new players",
                "class": "Fighter",
                "ability_scores": {
                    "strength": 15,
                    "constitution": 14,
                    "dexterity": 13,
                    "wisdom": 12,
                    "intelligence": 10,
                    "charisma": 8
                },
                "equipment": ["Longsword", "Chain Mail", "Shield"],
                "background": "Soldier"
            },
            {
                "name": "Quick Build Wizard",
                "description": "Pre-configured Wizard optimized for new players",
                "class": "Wizard",
                "ability_scores": {
                    "intelligence": 15,
                    "constitution": 14,
                    "dexterity": 13,
                    "wisdom": 12,
                    "strength": 10,
                    "charisma": 8
                },
                "equipment": ["Quarterstaff", "Spellbook", "Component Pouch"],
                "background": "Sage"
            }
        ]
        
    def get_creation_progress(self, character_id: str) -> Dict[str, Any]:
        """Get character creation progress."""
        character = self.db.query(CharacterDB).filter(CharacterDB.id == character_id).first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")
            
        # Check completion of different sections
        core_complete = all([
            character.name,
            character.species,
            character.background,
            character.character_classes
        ])
        
        ability_scores_complete = all([
            getattr(character, ability, None) is not None
            for ability in ["strength", "dexterity", "constitution", 
                          "intelligence", "wisdom", "charisma"]
        ])
        
        equipment_complete = len(character.equipment or []) > 0
        
        return {
            "character_id": character_id,
            "progress": {
                "core_details": core_complete,
                "ability_scores": ability_scores_complete,
                "equipment": equipment_complete,
                "spells": bool(character.spells_known or character.spells_prepared)
            },
            "completion_percentage": sum([
                core_complete,
                ability_scores_complete,
                equipment_complete,
                bool(character.spells_known or character.spells_prepared)
            }) * 25  # Each section is worth 25%
        }

    async def update_character_aspect(self, character_id: str,
                                    aspect: str,
                                    new_value: Any,
                                    maintain_theme: bool = True) -> CharacterDB:
        """Update a specific aspect of a character while maintaining theme consistency."""
        character = self.db.query(CharacterDB).filter(CharacterDB.id == character_id).first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        try:
            # Apply theme to new value if needed
            if maintain_theme and character.theme:
                if aspect in ["weapons", "armor", "equipment"]:
                    new_value = await self.theme_manager.theme_item(new_value, character.theme)
                elif aspect == "spells":
                    new_value = await self.theme_manager.theme_spell(new_value, character.theme)

            # Update the aspect
            if hasattr(character, aspect):
                setattr(character, aspect, new_value)
            else:
                raise ValueError(f"Invalid aspect: {aspect}")

            # Recalculate dependent attributes
            await self._recalculate_dependent_attributes(character)

            self.db.commit()
            return character

        except Exception as e:
            self.db.rollback()
            logger.error(f"Character aspect update failed: {e}")
            raise

    async def level_up_character(self, character_id: str) -> CharacterDB:
        """Level up a character while maintaining theme consistency."""
        character = self.db.query(CharacterDB).filter(CharacterDB.id == character_id).first()
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        try:
            # Generate level-up options
            options = await self._generate_level_up_options(character)

            # Apply level up
            character.level += 1
            
            # Update class levels
            primary_class = next(iter(character.character_classes))
            character.character_classes[primary_class] = character.level

            # Add new features
            if options.get("new_features"):
                character.features.extend(options["new_features"])

            # Add new spells if applicable
            if self._is_spellcaster({"character_classes": character.character_classes}):
                new_spells = await self._generate_spells(
                    character.to_dict(),
                    f"Level {character.level} {primary_class}",
                    character.theme
                )
                character.spells_known.extend(new_spells.get("spells", []))

            # Add equipment upgrades
            if options.get("equipment_upgrades"):
                await self.equipment_service.add_equipment(
                    character_id,
                    options["equipment_upgrades"]
                )

            self.db.commit()
            return character

        except Exception as e:
            self.db.rollback()
            logger.error(f"Character level up failed: {e}")
            raise

    async def _generate_level_up_options(self, character: CharacterDB) -> Dict[str, Any]:
        """Generate appropriate options for character level up."""
        prompt = f"""Generate D&D 5e level up options for this character. Return ONLY JSON:

        CURRENT CHARACTER:
        {character.to_dict()}

        NEXT LEVEL: {character.level + 1}

        Generate level up options that:
        1. Follow D&D 5e rules
        2. Are appropriate for the character's class and level
        3. Maintain theme consistency
        4. Include new features, spells, and equipment as appropriate

        Return JSON with level up options."""

        options = await self.theme_manager.generate_with_llm(prompt)
        return options

    async def _recalculate_dependent_attributes(self, character: CharacterDB) -> None:
        """Recalculate attributes that depend on other character aspects."""
        # Recalculate ability score modifiers
        for ability in ["strength", "dexterity", "constitution",
                      "intelligence", "wisdom", "charisma"]:
            if hasattr(character, ability):
                score = getattr(character, ability)
                if isinstance(score, AbilityScore):
                    score.recalculate_modifier()

        # Recalculate derived statistics
        self._recalculate_armor_class(character)
        self._recalculate_hit_points(character)
        self._recalculate_proficiency_bonus(character)
        self._recalculate_save_dc(character)

    def _recalculate_armor_class(self, character: CharacterDB) -> None:
        """Recalculate character's armor class."""
        base_ac = 10
        dex_mod = getattr(character, "dexterity", AbilityScore(10)).modifier

        # Factor in armor
        if character.equipment and any(item.get("type") == "armor" for item in character.equipment):
            armor = next(item for item in character.equipment if item.get("type") == "armor")
            base_ac = armor.get("armor_class", base_ac)

        character.armor_class = base_ac + dex_mod

    def _recalculate_hit_points(self, character: CharacterDB) -> None:
        """Recalculate character's hit points."""
        con_mod = getattr(character, "constitution", AbilityScore(10)).modifier
        level = character.level or 1

        # Get hit die from class
        primary_class = next(iter(character.character_classes), "Fighter")
        hit_die = {
            "Barbarian": 12,
            "Fighter": 10,
            "Paladin": 10,
            "Ranger": 10,
            "Cleric": 8,
            "Druid": 8,
            "Monk": 8,
            "Rogue": 8,
            "Warlock": 8,
            "Bard": 8,
            "Sorcerer": 6,
            "Wizard": 6
        }.get(primary_class, 8)

        # Calculate HP
        character.hit_points = hit_die + (con_mod * level)

    def _recalculate_proficiency_bonus(self, character: CharacterDB) -> None:
        """Recalculate character's proficiency bonus."""
        level = character.level or 1
        character.proficiency_bonus = 2 + ((level - 1) // 4)

    def _recalculate_save_dc(self, character: CharacterDB) -> None:
        """Recalculate spell save DC for spellcasters."""
        if not self._is_spellcaster({"character_classes": character.character_classes}):
            return

        # Get spellcasting ability
        primary_class = next(iter(character.character_classes), "")
        spellcasting_abilities = {
            "Wizard": "intelligence",
            "Cleric": "wisdom",
            "Druid": "wisdom",
            "Sorcerer": "charisma",
            "Warlock": "charisma",
            "Bard": "charisma",
            "Paladin": "charisma",
            "Ranger": "wisdom"
        }
        ability = spellcasting_abilities.get(primary_class, "intelligence")

        # Calculate save DC
        ability_mod = getattr(character, ability, AbilityScore(10)).modifier
        character.spell_save_dc = 8 + character.proficiency_bonus + ability_mod
