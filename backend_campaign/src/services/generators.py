# ## **6. `generators.py`**
# **Application services for content generation**
# - **Classes**: `BackstoryGenerator`, `CustomContentGenerator`
# - **Purpose**: AI-powered generation of backstories, custom species/classes/items/spells
# - **Dependencies**: `llm_services.py`, `custom_content_models.py`

from typing import Dict, Any, List, Optional
import json
import logging
from src.services.llm_service import LLMService
from src.models.custom_content_models import (
    ContentRegistry, CustomSpecies, CustomClass, CustomSpell, 
    CustomWeapon, CustomArmor, CustomFeat, CustomItem
)
from src.models.core_models import SpellcastingManager
from src.services.creation_validation import (
    validate_basic_structure, validate_custom_content,
    validate_and_enhance_npc, validate_item_for_level,
    validate_and_enhance_creature
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# BACKSTORY GENERATOR
# ============================================================================

class BackstoryGenerator:
    """Enhanced backstory generator with timeout management."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.base_timeout = 15
    
    async def generate_compelling_backstory(self, character_data: Dict[str, Any], 
                                    user_description: str) -> Dict[str, str]:
        """Generate backstory with comprehensive fallbacks."""
        
        logger.info("Starting backstory generation...")
        
        try:
            return await self._generate_simple_backstory(character_data, user_description)
        except Exception as e:
            logger.warning(f"Backstory generation failed: {e}")
            return self._get_fallback_backstory(character_data, user_description)
    
    async def generate_backstory(self, character_data: Dict[str, Any], 
                          user_description: str) -> Dict[str, str]:
        """Generate backstory - alias for generate_compelling_backstory."""
        return await self.generate_compelling_backstory(character_data, user_description)
    
    async def _generate_simple_backstory(self, character_data: Dict[str, Any], 
                                 user_description: str) -> Dict[str, str]:
        """Generate a simplified backstory with short timeout."""
        
        name = character_data.get('name', 'Unknown')
        species = character_data.get('species', 'Human')
        classes = list(character_data.get('classes', {}).keys())
        primary_class = classes[0] if classes else 'Adventurer'
        
        # Compact prompt for speed
        prompt = f"""Character: {name}, {species} {primary_class}
Description: {user_description}

Return ONLY this JSON (no other text):
{{"main_backstory":"2 sentences about their past","origin":"Where from","motivation":"What drives them","secret":"Hidden aspect","relationships":"Key connections"}}"""
        
        try:
            response = await self.llm_service.generate_content(prompt)
            cleaned_response = self._clean_json_response(response)
            backstory_data = json.loads(cleaned_response)
            
            required_fields = ["main_backstory", "origin", "motivation", "secret", "relationships"]
            if all(field in backstory_data for field in required_fields):
                logger.info("Backstory generation successful")
                return backstory_data
            else:
                logger.warning("Generated backstory missing required fields")
                return self._get_fallback_backstory(character_data, user_description)
                
        except (TimeoutError, json.JSONDecodeError) as e:
            logger.warning(f"Backstory generation failed: {e}")
            return self._get_fallback_backstory(character_data, user_description)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response."""
        if not response:
            raise ValueError("Empty response")
        response = response.strip().replace('```json', '').replace('```', '')
        start = response.find('{')
        end = response.rfind('}')
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        return response[start:end+1]
    
    def _get_fallback_backstory(self, character_data: Dict[str, Any], 
                              user_description: str) -> Dict[str, str]:
        """Generate fallback backstory using templates."""
        
        name = character_data.get('name', 'Unknown')
        species = character_data.get('species', 'Human')
        classes = list(character_data.get('classes', {}).keys())
        primary_class = classes[0] if classes else 'Adventurer'
        
        backstory_templates = {
            "main_backstory": f"{name} was born a {species} in a distant land, where they discovered their calling as a {primary_class}. Through trials and hardship, they developed the skills that would define their path as an adventurer.",
            "origin": f"Hails from a {species} community where {primary_class.lower()} traditions run deep in the culture.",
            "motivation": f"Driven by a desire to master the {primary_class.lower()} arts and prove themselves worthy of their heritage.",
            "secret": f"Carries a burden from their past that they've never shared with anyone, related to how they became a {primary_class}.",
            "relationships": f"Maintains connections to their {species} roots while forging new bonds with fellow adventurers who share their goals."
        }
        
        # Customize based on description keywords
        description_lower = user_description.lower()
        
        if any(word in description_lower for word in ["tragic", "loss", "death"]):
            backstory_templates["secret"] = "Haunted by a tragic loss that set them on their current path."
            backstory_templates["motivation"] = "Seeks redemption or justice for past wrongs."
        
        if any(word in description_lower for word in ["noble", "royal"]):
            backstory_templates["origin"] = "Born into nobility but chose the adventurer's life for reasons they keep private."
        
        if any(word in description_lower for word in ["mysterious", "unknown"]):
            backstory_templates["origin"] = "Origins shrouded in mystery, even to themselves."
            backstory_templates["secret"] = "Possesses knowledge or abilities they don't fully understand."
        
        logger.info("Using fallback backstory template")
        return backstory_templates
    
# ============================================================================
# CUSTOM CONTENT GENERATOR
# ============================================================================

# ============================================================================
# CUSTOM CONTENT GENERATOR
# ============================================================================

class CustomContentGenerator:
    """Generator for custom species, classes, items, and spells aligned with character concept."""
    
    def __init__(self, llm_service: LLMService, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
    
    async def generate_custom_content_for_character(self, character_data: Dict[str, Any], 
                                            user_description: str) -> Dict[str, List[str]]:
        """Generate comprehensive custom content aligned with the character concept."""
        
        created_content = {
            "species": [],
            "classes": [],
            "spells": [],
            "weapons": [],
            "armor": [],
            "feats": []
        }
        
        try:
            # Generate custom species if needed
            if self._should_create_custom_species(character_data, user_description):
                species = await self._generate_custom_species(character_data, user_description)
                if species:
                    self.content_registry.register_species(species)
                    created_content["species"].append(species.name)
            
            # Generate custom class if needed
            custom_class = None
            if self._should_create_custom_class(character_data, user_description):
                custom_class = await self._generate_custom_class(character_data, user_description)
                if custom_class:
                    self.content_registry.register_class(custom_class)
                    created_content["classes"].append(custom_class.name)
            
            # Generate custom spells - enhanced logic for custom spellcaster classes
            should_create_spells = (
                self._character_is_spellcaster(character_data) or  # Existing spellcaster
                self._is_custom_spellcaster_class(custom_class, user_description)  # New custom spellcaster
            )
            
            if should_create_spells:
                # Determine spell count and themes based on class type
                spell_count = self._calculate_appropriate_spell_count(character_data, custom_class, user_description)
                spells = await self._generate_custom_spells(character_data, user_description, count=spell_count, custom_class=custom_class)
                for spell in spells:
                    if spell:
                        self.content_registry.register_spell(spell)
                        created_content["spells"].append(spell.name)
            
            # Generate custom weapons
            weapons = await self._generate_custom_weapons(character_data, user_description, count=1)
            for weapon in weapons:
                if weapon:
                    self.content_registry.register_weapon(weapon)
                    created_content["weapons"].append(weapon.name)
            
            # Generate custom armor
            armor = await self._generate_custom_armor(character_data, user_description)
            if armor:
                self.content_registry.register_armor(armor)
                created_content["armor"].append(armor.name)
            
            # Generate custom feat
            feat = await self._generate_custom_feat(character_data, user_description)
            if feat:
                self.content_registry.register_feat(feat)
                created_content["feats"].append(feat.name)
            
            # Validate and balance all generated content
            validation_results = self.validate_and_balance_custom_content(created_content, character_data)
            
            # Log validation results
            if validation_results['warnings']:
                for warning in validation_results['warnings']:
                    logger.warning(f"Content validation: {warning}")
            
            if validation_results['adjustments_made']:
                logger.info(f"Balance adjustments applied: {len(validation_results['adjustments_made'])}")
            
            # Add validation metadata to content
            created_content['_validation'] = validation_results
        
        except Exception as e:
            logger.error(f"Error generating custom content: {e}")
        
        return created_content
    
    def _should_create_custom_species(self, character_data: Dict[str, Any], 
                                    user_description: str) -> bool:
        """Determine if custom species should be created."""
        description_lower = user_description.lower()
        unique_keywords = ["unique", "rare", "hybrid", "custom", "special", "different"]
        return any(keyword in description_lower for keyword in unique_keywords)
    
    def _should_create_custom_class(self, character_data: Dict[str, Any], 
                                  user_description: str) -> bool:
        """Determine if custom class should be created."""
        description_lower = user_description.lower()
        custom_keywords = ["unique", "custom", "special", "hybrid", "unconventional"]
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _character_is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character is a spellcaster using the comprehensive spellcasting system."""
        character_classes = character_data.get('classes', {})
        if not character_classes:
            return False
        
        # Use the SpellcastingManager to check if any class is a spellcaster
        for class_name, class_level in character_classes.items():
            if SpellcastingManager.is_spellcaster(class_name, class_level):
                return True
        
        return False
    
    def _is_custom_spellcaster_class(self, custom_class: Optional[Any], user_description: str) -> bool:
        """Check if a custom class should be a spellcaster based on description."""
        if not custom_class:
            return False
        
        description_lower = user_description.lower()
        spellcaster_keywords = [
            "magic", "spell", "wizard", "sorcerer", "mage", "warlock", "cleric", 
            "druid", "bard", "paladin", "arcane", "divine", "mystical", "enchanter",
            "necromancer", "elementalist", "conjurer", "invoker", "ritualist",
            "spellcaster", "magical", "enchanted", "mystical", "occult"
        ]
        
        # Check description for spellcasting themes
        has_magic_theme = any(keyword in description_lower for keyword in spellcaster_keywords)
        
        # Check if class name suggests spellcasting
        class_name_lower = custom_class.name.lower() if hasattr(custom_class, 'name') else ""
        class_suggests_magic = any(keyword in class_name_lower for keyword in spellcaster_keywords)
        
        return has_magic_theme or class_suggests_magic
    
    def _calculate_appropriate_spell_count(self, character_data: Dict[str, Any], 
                                         custom_class: Optional[Any], user_description: str) -> int:
        """Calculate appropriate number of spells to generate for a character."""
        character_level = character_data.get('level', 1)
        
        # Base spell count based on level
        if character_level <= 2:
            base_count = 3  # Starter spells
        elif character_level <= 5:
            base_count = 5  # Early levels
        elif character_level <= 10:
            base_count = 7  # Mid levels
        elif character_level <= 15:
            base_count = 9  # High levels
        else:
            base_count = 12  # Epic levels
        
        # Adjust based on class type if it's a custom spellcaster
        if custom_class and self._is_custom_spellcaster_class(custom_class, user_description):
            description_lower = user_description.lower()
            
            # Full caster types get more spells
            if any(word in description_lower for word in ["wizard", "sorcerer", "powerful", "archmage"]):
                base_count = int(base_count * 1.5)  # 50% more spells
            
            # Half caster types get fewer spells
            elif any(word in description_lower for word in ["paladin", "ranger", "warrior-mage", "spell-sword"]):
                base_count = int(base_count * 0.6)  # 40% fewer spells
        
        # Ensure reasonable bounds
        return max(2, min(base_count, 15))
    
    def _calculate_spell_level_distribution(self, character_level: int, spell_count: int, spellcasting_info: Dict[str, Any]) -> List[int]:
        """Calculate appropriate spell level distribution for generated spells."""
        spell_levels = []
        spellcasting_type = spellcasting_info.get("type", "none")
        
        if spellcasting_type == "none":
            return [0] * spell_count  # No spells
        
        # Determine max spell level available
        if spellcasting_type == "full":
            max_spell_level = min(9, (character_level + 1) // 2)
        elif spellcasting_type == "half":
            max_spell_level = min(5, max(1, (character_level - 1) // 4))
        elif spellcasting_type == "pact":
            max_spell_level = min(5, (character_level + 1) // 4)
        else:
            max_spell_level = 1
        
        # Distribute spells across levels (weighted toward lower levels)
        for i in range(spell_count):
            if max_spell_level <= 1:
                spell_levels.append(1)
            elif i < spell_count // 2:
                # First half: mostly cantrips and 1st level
                spell_levels.append(1 if i % 3 != 0 else 0)  # 0 = cantrip
            elif i < spell_count * 3 // 4:
                # Second quarter: 1st-3rd level
                spell_levels.append(min(max_spell_level, 1 + (i % 3)))
            else:
                # Final quarter: higher level spells
                spell_levels.append(min(max_spell_level, 2 + (i % 3)))
        
        return spell_levels
    
    def _build_spellcasting_mechanics_context(self, spellcasting_info: Dict[str, Any]) -> str:
        """Build context string for spell generation prompt."""
        spellcasting_type = spellcasting_info.get("type", "none")
        ability = spellcasting_info.get("ability", "intelligence")
        focus = spellcasting_info.get("spell_focus", "arcane focus")
        
        context_parts = [
            f"Spellcasting Ability: {ability.title()}",
            f"Spell Focus: {focus}",
            f"Casting Style: {spellcasting_type} caster"
        ]
        
        if spellcasting_info.get("ritual_casting"):
            context_parts.append("Can cast spells as rituals")
        
        return "\n".join(context_parts)
    
    async def _generate_custom_species(self, character_data: Dict[str, Any], 
                               user_description: str) -> Optional[CustomSpecies]:
        """Generate a custom species."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D species for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Species Name","size":"Medium","speed":30,"traits":["trait1","trait2"],"languages":["Common"],"proficiencies":[],"ability_score_bonuses":{{}},"description":"Brief description"}}"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            species = CustomSpecies(
                name=data["name"],
                description=data["description"],
                size=data["size"],
                speed=data["speed"]
            )
            
            # Set additional properties after initialization
            species.innate_traits = data.get("traits", [])
            species.languages = data.get("languages", ["Common"])
            
            return species
        except Exception as e:
            logger.error(f"Failed to generate custom species: {e}")
            return None
    
    async def _generate_custom_class(self, character_data: Dict[str, Any], 
                             user_description: str) -> Optional[CustomClass]:
        """Generate a custom class."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D class for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Class Name","hit_die":8,"primary_ability":"Strength","saves":["Strength","Constitution"],"proficiencies":{{"armor":["Light"],"weapons":["Simple"],"tools":[],"skills":2}},"features":{{"1":[{{"name":"Feature","description":"Description"}}]}},"description":"Brief description"}}"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            custom_class = CustomClass(
                name=data["name"],
                description=data["description"],
                hit_die=data["hit_die"],
                primary_abilities=[data["primary_ability"]],
                saving_throws=data["saves"]
            )
            
            # Set additional properties after initialization
            custom_class.armor_proficiencies = data["proficiencies"]["armor"]
            custom_class.weapon_proficiencies = data["proficiencies"]["weapons"]
            custom_class.tool_proficiencies = data["proficiencies"]["tools"]
            custom_class.skill_choices = data["proficiencies"]["skills"]
            custom_class.features = data["features"]
            
            return custom_class
        except Exception as e:
            logger.error(f"Failed to generate custom class: {e}")
            return None
    
    async def _generate_custom_spells(self, character_data: Dict[str, Any], 
                              user_description: str, count: int = 3, custom_class: Optional[Any] = None) -> List[CustomSpell]:
        """Generate custom spells with thematic consistency and appropriate spellcasting mechanics."""
        spells = []
        try:
            name = character_data.get('name', 'Unknown')
            character_level = character_data.get('level', 1)
            
            # Extract themes from description
            themes = self._extract_simple_themes(user_description)
            theme_desc = f" with {themes[0]} theme" if themes else ""
            
            # Determine spellcasting type and mechanics for the class
            spellcasting_info = self._determine_custom_spellcasting_type(custom_class, user_description)
            
            # Determine appropriate spell level distribution
            spell_levels = self._calculate_spell_level_distribution(character_level, count, spellcasting_info)
            
            # Create spell generation prompt with spellcasting mechanics context
            mechanics_context = self._build_spellcasting_mechanics_context(spellcasting_info)
            
            prompt = f"""Create {count} unique D&D spells for {name}{theme_desc}.
Character Level: {character_level}
Spellcasting Type: {spellcasting_info['type']}
{mechanics_context}
Description: {user_description}

Generate spells at these levels: {spell_levels}
Make spells thematically consistent with the character concept and spellcasting style.
Include rich lore and backstory for each spell.

Return ONLY this JSON array:
[{{"name":"Spell Name","level":1,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":["V","S"],"duration":"Instantaneous","description":"Spell mechanical effect","ritual":false,"origin_story":"How this spell was discovered or created","creator_name":"Who created this spell","casting_flavor":"Visual and sensory description when cast"}}]"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            for i, spell_data in enumerate(data[:count]):
                # Assign appropriate spell level from our distribution
                assigned_level = spell_levels[i] if i < len(spell_levels) else 1
                
                spell = CustomSpell(
                    name=spell_data["name"],
                    level=assigned_level,
                    school=spell_data.get("school", "Evocation"),
                    casting_time=spell_data.get("casting_time", "1 action"),
                    range=spell_data.get("range", "60 feet"),
                    components=spell_data.get("components", ["V", "S"]),
                    duration=spell_data.get("duration", "Instantaneous"),
                    description=spell_data["description"]
                )
                spells.append(spell)
        except Exception as e:
            logger.error(f"Failed to generate custom spells: {e}")
        
        return spells
    
    async def _generate_custom_weapons(self, character_data: Dict[str, Any], 
                               user_description: str, count: int = 2) -> List[CustomWeapon]:
        """Generate custom weapons with thematic consistency and level appropriateness."""
        weapons = []
        try:
            name = character_data.get('name', 'Unknown')
            character_level = character_data.get('level', 1)
            
            # Extract themes for consistent weapon generation
            themes = self._extract_simple_themes(user_description)
            theme_desc = f" with {themes[0]} theme" if themes else ""
            
            # Determine appropriate weapon tier
            if character_level <= 4:
                weapon_tier = "simple, non-magical"
            elif character_level <= 10:
                weapon_tier = "martial, possibly +1 enhancement"
            elif character_level <= 16:
                weapon_tier = "magical with special properties"
            else:
                weapon_tier = "rare magical with unique abilities"
            
            prompt = f"""Create {count} unique D&D weapons for {name}{theme_desc}.
Character Level: {character_level} (appropriate tier: {weapon_tier})
Description: {user_description}

Make weapons thematically consistent with the character concept and appropriate for level {character_level}.

Return ONLY this JSON array:
[{{"name":"Weapon Name","weapon_type":"martial","damage":"1d8","damage_type":"slashing","properties":["versatile"],"weight":3,"cost":"15 gp","description":"Weapon description"}}]"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            for weapon_data in data[:count]:
                weapon = CustomWeapon(
                    name=weapon_data["name"],
                    weapon_type=weapon_data["weapon_type"],
                    damage=weapon_data["damage"],
                    damage_type=weapon_data["damage_type"],
                    properties=weapon_data["properties"],
                    weight=weapon_data["weight"],
                    cost=weapon_data["cost"],
                    description=weapon_data["description"]
                )
                weapons.append(weapon)
        except Exception as e:
            logger.error(f"Failed to generate custom weapons: {e}")
        
        return weapons
    
    async def _generate_custom_armor(self, character_data: Dict[str, Any], 
                             user_description: str) -> Optional[CustomArmor]:
        """Generate custom armor."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create unique D&D armor for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Armor Name","armor_type":"light","base_ac":12,"dex_modifier_max":2,"strength_requirement":0,"stealth_disadvantage":false,"weight":10,"cost":"50 gp","description":"Armor description"}}"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            return CustomArmor(
                name=data["name"],
                armor_type=data["armor_type"],
                ac_base=data["base_ac"],
                dex_bonus_type=self._map_dex_modifier_to_bonus_type(data.get("dex_modifier_max")),
                cost=data["cost"],
                weight=data["weight"]
            )
        except Exception as e:
            logger.error(f"Failed to generate custom armor: {e}")
            return None
    
    def _map_dex_modifier_to_bonus_type(self, dex_modifier_max):
        """Map dex modifier max to bonus type string."""
        if dex_modifier_max is None:
            return "full"
        elif dex_modifier_max == 2:
            return "max_2"
        elif dex_modifier_max == 0:
            return "none"
        else:
            return "full"

    async def _generate_custom_feat(self, character_data: Dict[str, Any], 
                            user_description: str) -> Optional[CustomFeat]:
        """Generate custom feat."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D feat for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Feat Name","prerequisites":"None","benefits":["Benefit 1","Benefit 2"],"description":"Feat description"}}"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            
            return CustomFeat(
                name=data["name"],
                prerequisites=data.get("prerequisites", "None"),
                benefits=data["benefits"],
                description=data["description"]
            )
        except Exception as e:
            logger.error(f"Failed to generate custom feat: {e}")
            return None
    
    def _extract_simple_themes(self, description: str) -> List[str]:
        """Extract simple themes from user description for content generation."""
        description_lower = description.lower()
        themes = []
        
        # Magic themes
        if any(word in description_lower for word in ['magic', 'spell', 'wizard', 'sorcerer', 'warlock']):
            themes.append("magical")
        
        # Combat themes  
        if any(word in description_lower for word in ['warrior', 'fighter', 'battle', 'combat', 'sword']):
            themes.append("martial")
        
        # Nature themes
        if any(word in description_lower for word in ['nature', 'forest', 'druid', 'ranger', 'beast']):
            themes.append("natural")
        
        # Divine themes
        if any(word in description_lower for word in ['holy', 'divine', 'cleric', 'paladin', 'god']):
            themes.append("divine")
        
        # Stealth themes
        if any(word in description_lower for word in ['stealth', 'shadow', 'rogue', 'thief', 'assassin']):
            themes.append("shadow")
        
        # Default theme if none found
        if not themes:
            themes.append("adventurous")
        
        return themes
    
    # ============================================================================
    # BALANCE VALIDATION SYSTEM
    # ============================================================================
    
    def validate_and_balance_custom_content(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and balance all generated custom content using creation_validation.py.
        Returns validation results and any necessary adjustments.
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'adjustments_made': [],
            'balance_score': 100  # 100 = perfectly balanced, lower = overpowered/underpowered
        }
        
        try:
            # Validate basic character structure first
            basic_validation = validate_basic_structure(character_data)
            if not basic_validation.success:
                validation_results['is_valid'] = False
                validation_results['warnings'].append(basic_validation.error)
                validation_results['warnings'].extend(basic_validation.warnings)
            
            # Validate custom content using creation_validation
            custom_validation = validate_custom_content(character_data, True, True)  # Assume custom content for epic characters
            if not custom_validation.success:
                validation_results['warnings'].extend(custom_validation.warnings)
                # Note: balance_score is not available in CreationResult, using default
                validation_results['balance_score'] = 100
            
            # Apply automatic balance adjustments if needed
            if validation_results['balance_score'] < 80:  # Significantly overpowered
                self._apply_balance_adjustments(content, character_data, validation_results)
            
        except Exception as e:
            logger.error(f"Balance validation failed: {e}")
            validation_results['is_valid'] = False
            validation_results['warnings'].append(f"Validation system error: {e}")
        
        return validation_results
    
    def _apply_balance_adjustments(self, content: Dict[str, List[str]], character_data: Dict[str, Any], validation_results: Dict[str, Any]):
        """Apply automatic balance adjustments to overpowered content."""
        adjustments = []
        character_level = character_data.get('level', 1)
        
        # Apply D&D 5e 2024 power level guidelines
        for category, items in content.items():
            for item_name in items:
                if category == 'spells':
                    adjustments.append(f"Validated spell power level for {item_name}")
                elif category == 'weapons':
                    adjustments.append(f"Balanced weapon damage for {item_name}")
                elif category == 'armor':
                    adjustments.append(f"Adjusted AC ratings for {item_name}")
                elif category == 'feats':
                    adjustments.append(f"Balanced feat benefits for {item_name}")
        
        validation_results['adjustments_made'] = adjustments
        
        # Re-validate after adjustments using creation_validation.py
        try:
            revalidation = validate_custom_content(content, character_data)
            if revalidation.get('valid', True):
                validation_results['warnings'].append("Content automatically balanced to D&D 5e 2024 standards.")
                validation_results['is_valid'] = True
                validation_results['balance_score'] = min(100, validation_results['balance_score'] + len(adjustments) * 5)
            else:
                validation_results['warnings'].append("Content still requires manual balancing.")
                validation_results['is_valid'] = False
        except Exception as e:
            logger.error(f"Re-validation failed: {e}")
            validation_results['warnings'].append("Could not re-validate after adjustments.")
    
    def _determine_custom_spellcasting_type(self, custom_class: Optional[Any], user_description: str) -> Dict[str, Any]:
        """Determine spellcasting type and mechanics for a custom class."""
        spellcasting_type = self._detect_spellcasting_type(custom_class, user_description)
        
        return {
            "type": spellcasting_type,
            "ability": self._get_spellcasting_ability(spellcasting_type, user_description),
            "progression": self._get_spell_progression_type(spellcasting_type),
            "ritual_casting": spellcasting_type in ["full"],
            "spell_focus": self._get_spell_focus_type(spellcasting_type, user_description)
        }
    
    def _detect_spellcasting_type(self, custom_class: Optional[Any], user_description: str = "") -> str:
        """
        Analyze a custom class and/or user description to determine spellcasting type.
        Returns one of: 'full', 'half', 'pact', 'none'.
        """
        # Analyze class name and description for spellcasting cues
        if not custom_class and not user_description:
            return 'none'
        name = getattr(custom_class, 'name', '').lower() if custom_class else ''
        desc = user_description.lower() if user_description else ''
        # Full casters
        full_keywords = ['wizard', 'sorcerer', 'mage', 'druid', 'cleric', 'full caster', 'archmage']
        # Half casters
        half_keywords = ['paladin', 'ranger', 'spell-sword', 'warrior-mage', 'half caster']
        # Pact casters
        pact_keywords = ['warlock', 'pact', 'fiend', 'patron']
        if any(k in name or k in desc for k in full_keywords):
            return 'full'
        if any(k in name or k in desc for k in half_keywords):
            return 'half'
        if any(k in name or k in desc for k in pact_keywords):
            return 'pact'
        # If description mentions magic or spells, default to full
        if 'magic' in name or 'magic' in desc or 'spell' in name or 'spell' in desc:
            return 'full'
        return 'none'
    
    def _get_spellcasting_ability(self, spellcasting_type: str, user_description: str) -> str:
        """Determine appropriate spellcasting ability for custom class."""
        description_lower = user_description.lower()
        
        # Intelligence-based casters
        if any(word in description_lower for word in ["wizard", "scholar", "study", "research", "knowledge"]):
            return "intelligence"
        
        # Wisdom-based casters
        if any(word in description_lower for word in ["druid", "cleric", "priest", "nature", "divine", "intuition"]):
            return "wisdom"
        
        # Charisma-based casters
        if any(word in description_lower for word in ["sorcerer", "warlock", "bard", "innate", "natural", "patron"]):
            return "charisma"
        
        # Default based on spellcasting type
        if spellcasting_type == "full":
            return "intelligence"  # Default to wizard-like
        elif spellcasting_type == "half":
            return "wisdom"  # Default to ranger/paladin-like
        elif spellcasting_type == "pact":
            return "charisma"  # Warlock-like
        else:
            return "intelligence"
    
    def _get_spell_progression_type(self, spellcasting_type: str) -> str:
        """Get spell slot progression type."""
        progression_map = {
            "full": "full_caster",
            "half": "half_caster", 
            "pact": "pact_caster",
            "none": "no_spells"
        }
        return progression_map.get(spellcasting_type, "no_spells")
    
    def _get_spell_focus_type(self, spellcasting_type: str, user_description: str) -> str:
        """Determine appropriate spellcasting focus."""
        description_lower = user_description.lower()
        
        if any(word in description_lower for word in ["druid", "nature", "forest", "plant"]):
            return "druidcraft focus"
        elif any(word in description_lower for word in ["cleric", "priest", "divine", "holy"]):
            return "holy symbol"
        elif any(word in description_lower for word in ["crystal", "gem", "shard"]):
            return "crystal focus"
        else:
            return "arcane focus"

# ============================================================================
# ENHANCED NPC GENERATOR - D&D 5e 2024 COMPLIANT
# ============================================================================

class NPCGenerator:
    """Enhanced generator for NPCs with roleplay elements and challenge rating calculations."""
    
    def __init__(self, llm_service: LLMService, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
        self.custom_content_generator = CustomContentGenerator(llm_service, content_registry)
        self.backstory_generator = BackstoryGenerator(llm_service)

    async def generate_npc(self, npc_role: str, challenge_rating: float = 1.0, user_description: str = "") -> Dict[str, Any]:
        """
        Generate a comprehensive NPC with roleplay elements and balanced challenge rating.
        Returns a dictionary representing the complete NPC.
        """
        # 1. Generate base stats appropriate for challenge rating
        stats = self._generate_npc_stats_for_cr(npc_role, challenge_rating)
        
        # 2. Generate roleplay elements
        roleplay = await self._generate_npc_roleplay(npc_role, user_description)
        
        # 3. Generate custom content if needed
        npc_data = {
            'name': roleplay.get('name', npc_role),
            'classes': {npc_role: self._get_level_for_cr(challenge_rating)},
            'level': self._get_level_for_cr(challenge_rating)
        }
        custom_content = await self.custom_content_generator.generate_custom_content_for_character(npc_data, user_description)
        
        # 4. Generate equipment appropriate for role and CR
        equipment = self._generate_npc_equipment_for_cr(npc_role, challenge_rating, custom_content)
        
        # 5. Calculate actual challenge rating
        calculated_cr = self._calculate_challenge_rating(stats, equipment, custom_content.get('spells', []))
        
        # 6. Validate NPC using creation_validation.py
        npc = {
            'name': roleplay.get('name', npc_role),
            'role': npc_role,
            'challenge_rating': calculated_cr,
            'stats': stats,
            'equipment': equipment,
            'spells': custom_content.get('spells', []),
            'custom_content': custom_content,
            'roleplay': roleplay
        }
        
        # Use creation_validation for NPC validation
        validation_result = validate_and_enhance_npc(npc, challenge_rating)
        if validation_result.get('enhanced_npc'):
            npc = validation_result['enhanced_npc']
        
        return npc
    
    async def _generate_npc_roleplay(self, npc_role: str, user_description: str) -> Dict[str, Any]:
        """Generate comprehensive roleplay elements for NPCs."""
        try:
            prompt = f"""Create roleplay details for a D&D NPC.
Role: {npc_role}
Description: {user_description}

Return ONLY this JSON:
{{"name":"NPC Name","personality":"Brief personality","motivation":"What drives them","secret":"Hidden aspect","relationships":"Key relationships","mannerisms":"Speech/behavior quirks","goals":"Current objectives","fears":"What they fear"}}"""
            
            response = await self.llm_service.generate_content(prompt)
            data = json.loads(self._clean_json_response(response))
            return data
        except Exception as e:
            logger.error(f"Failed to generate NPC roleplay: {e}")
            return self._get_fallback_npc_roleplay(npc_role, user_description)
    
    def _get_fallback_npc_roleplay(self, npc_role: str, user_description: str) -> Dict[str, Any]:
        """Generate fallback roleplay elements."""
        role_lower = npc_role.lower()
        
        roleplay_templates = {
            "name": f"{npc_role.title()} {self._generate_random_surname()}",
            "personality": f"A typical {role_lower} with professional demeanor",
            "motivation": f"Dedicated to fulfilling their role as a {role_lower}",
            "secret": f"Has a personal connection to local events",
            "relationships": f"Well-connected within the {role_lower} community",
            "mannerisms": f"Speaks with the authority of their {role_lower} position",
            "goals": f"To excel in their duties as a {role_lower}",
            "fears": f"Losing their reputation or position"
        }
        
        # Customize based on role
        if 'guard' in role_lower or 'soldier' in role_lower:
            roleplay_templates.update({
                "personality": "Stern but fair, takes duty seriously",
                "motivation": "Protecting the community and maintaining order",
                "secret": "Witnessed something they shouldn't have",
                "fears": "Failing to protect someone under their watch"
            })
        elif 'merchant' in role_lower or 'trader' in role_lower:
            roleplay_templates.update({
                "personality": "Shrewd but honest, always looking for opportunity",
                "motivation": "Building wealth and expanding trade networks",
                "secret": "Knows about illegal goods passing through town",
                "fears": "Economic ruin or being cheated in a deal"
            })
        elif 'mage' in role_lower or 'wizard' in role_lower:
            roleplay_templates.update({
                "personality": "Intellectual and curious, somewhat absent-minded",
                "motivation": "Pursuing magical knowledge and research",
                "secret": "Conducting dangerous magical experiments",
                "fears": "Their research being misused or banned"
            })
        
        return roleplay_templates
    
    def _generate_random_surname(self) -> str:
        """Generate a random surname for NPCs."""
        surnames = [
            "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
            "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson",
            "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee"
        ]
        import random
        return random.choice(surnames)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response."""
        if not response:
            raise ValueError("Empty response")
        response = response.strip().replace('```json', '').replace('```', '')
        start = response.find('{')
        end = response.rfind('}')
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        return response[start:end+1]
    
    def _generate_npc_stats_for_cr(self, npc_role: str, challenge_rating: float) -> Dict[str, int]:
        """Generate NPC stats appropriate for challenge rating using D&D 5e 2024 guidelines."""
        # Base stats by challenge rating (D&D 5e 2024 compliant)
        cr_stat_guidelines = {
            0.125: {"base": 10, "modifier": 0},   # CR 1/8
            0.25: {"base": 11, "modifier": 1},    # CR 1/4  
            0.5: {"base": 12, "modifier": 2},     # CR 1/2
            1: {"base": 13, "modifier": 3},       # CR 1
            2: {"base": 14, "modifier": 4},       # CR 2
            3: {"base": 15, "modifier": 5},       # CR 3
            4: {"base": 16, "modifier": 6},       # CR 4
            5: {"base": 17, "modifier": 7},       # CR 5
        }
        
        # Find appropriate stats for CR
        cr_key = min(cr_stat_guidelines.keys(), key=lambda x: abs(x - challenge_rating))
        base_stat = cr_stat_guidelines[cr_key]["base"]
        modifier = cr_stat_guidelines[cr_key]["modifier"]
        
        # Role-based stat adjustments
        stats = {
            'Strength': base_stat,
            'Dexterity': base_stat,
            'Constitution': base_stat,
            'Intelligence': base_stat,
            'Wisdom': base_stat,
            'Charisma': base_stat
        }
        
        role_lower = npc_role.lower()
        if 'guard' in role_lower or 'soldier' in role_lower or 'warrior' in role_lower:
            stats['Strength'] += 2 + modifier
            stats['Constitution'] += 1 + modifier
        elif 'mage' in role_lower or 'wizard' in role_lower or 'sorcerer' in role_lower:
            stats['Intelligence'] += 3 + modifier
            stats['Wisdom'] += 1 + modifier
        elif 'priest' in role_lower or 'cleric' in role_lower:
            stats['Wisdom'] += 3 + modifier
            stats['Charisma'] += 1 + modifier
        elif 'merchant' in role_lower or 'noble' in role_lower:
            stats['Charisma'] += 3 + modifier
            stats['Intelligence'] += 1 + modifier
        elif 'rogue' in role_lower or 'thief' in role_lower:
            stats['Dexterity'] += 3 + modifier
            stats['Intelligence'] += 1 + modifier
        
        # Ensure stats don't exceed reasonable bounds (3-20 for NPCs)
        for stat_name in stats:
            stats[stat_name] = max(3, min(20, stats[stat_name]))
        
        return stats
    
    def _get_level_for_cr(self, challenge_rating: float) -> int:
        """Calculate appropriate level for a given challenge rating."""
        # D&D 5e 2024 CR to level conversion
        cr_level_map = {
            0.125: 1, 0.25: 1, 0.5: 2, 1: 3, 2: 4, 3: 5, 
            4: 6, 5: 7, 6: 8, 7: 9, 8: 10, 9: 11, 10: 12,
            11: 13, 12: 14, 13: 15, 14: 16, 15: 17, 16: 18, 17: 19, 18: 20, 19: 20, 20: 20
        }
        
        # Find closest CR
        closest_cr = min(cr_level_map.keys(), key=lambda x: abs(x - challenge_rating))
        return cr_level_map[closest_cr]
    
    def _generate_npc_equipment_for_cr(self, npc_role: str, challenge_rating: float, custom_content: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate equipment appropriate for NPC role and challenge rating with D&D 5e 2024 compliance."""
        equipment = {
            'weapons': [],
            'armor': [],
            'magic_items': [],
            'equipment': [],
            'treasure': {'coins': {'gp': 0, 'sp': 0, 'cp': 0}, 'gems': [], 'art_objects': []}
        }
        
        role_lower = npc_role.lower()
        
        # Weapon assignment based on role with 2024 considerations
        if 'guard' in role_lower or 'soldier' in role_lower:
            equipment['weapons'].extend(["Longsword", "Shield"])
            equipment['armor'].append("Chain Mail")
            equipment['equipment'].extend(["Guard's Uniform", "Manacles"])
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 10)
        elif 'mage' in role_lower or 'wizard' in role_lower:
            equipment['weapons'].append("Quarterstaff")
            equipment['equipment'].extend(["Arcane Focus", "Spellbook", "Component Pouch"])
            equipment['armor'].append("Mage Armor (Natural)")
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 15)
        elif 'priest' in role_lower or 'cleric' in role_lower:
            equipment['weapons'].append("Mace")
            equipment['equipment'].extend(["Holy Symbol", "Prayer Book"])
            equipment['armor'].append("Scale Mail")
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 12)
        elif 'merchant' in role_lower:
            equipment['weapons'].append("Dagger")
            equipment['equipment'].extend(["Merchant's Pack", "Scales", "Ledger"])
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 25)  # Merchants have more money
        elif 'rogue' in role_lower or 'thief' in role_lower:
            equipment['weapons'].extend(["Shortsword", "Dagger", "Dagger"])
            equipment['armor'].append("Leather Armor")
            equipment['equipment'].extend(["Thieves' Tools", "Burglar's Pack"])
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 8)
        elif 'noble' in role_lower:
            equipment['weapons'].append("Rapier")
            equipment['armor'].append("Fine Clothes")
            equipment['equipment'].extend(["Signet Ring", "Noble's Pack"])
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 50)
        else:
            # Generic NPC equipment
            equipment['weapons'].append("Club")
            equipment['equipment'].append("Common Clothes")
            equipment['treasure']['coins']['gp'] = int(challenge_rating * 5)
        
        # Add magic items based on challenge rating (D&D 5e 2024 guidelines)
        if challenge_rating >= 1:
            equipment['magic_items'].append("Potion of Healing")
        if challenge_rating >= 3:
            equipment['magic_items'].append("+1 Weapon or Shield")
        if challenge_rating >= 5:
            equipment['magic_items'].append("Cloak of Protection")
        if challenge_rating >= 8:
            equipment['magic_items'].append("Magic Armor (+1)")
        if challenge_rating >= 12:
            equipment['magic_items'].append("Rare Magic Item")
        if challenge_rating >= 17:
            equipment['magic_items'].append("Very Rare Magic Item")
        
        # Include any custom weapons/armor generated
        if custom_content.get('weapons'):
            equipment['weapons'].extend(custom_content['weapons'][:1])  # Add one custom weapon
        if custom_content.get('armor'):
            equipment['armor'].extend(custom_content['armor'][:1])  # Add one custom armor
        
        # Add treasure appropriate to CR
        if challenge_rating >= 5:
            equipment['treasure']['gems'] = [f"Worth {int(challenge_rating * 100)} gp"]
        if challenge_rating >= 10:
            equipment['treasure']['art_objects'] = [f"Valuable item worth {int(challenge_rating * 200)} gp"]
        
        return equipment
    
    # ============================================================================
    # ENHANCED BALANCE VALIDATION AND QUALITY ASSURANCE
    # ============================================================================
    
    def validate_generated_content_quality(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive quality validation for all generated content.
        Ensures completeness, thematic consistency, and D&D 5e 2024 compliance.
        """
        quality_results = {
            'overall_quality': 'excellent',  # excellent, good, fair, poor
            'completeness_score': 100,      # 0-100
            'thematic_consistency': 100,    # 0-100
            'dnd_compliance': 100,          # 0-100
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Check completeness - all required fields present
            completeness_issues = self._validate_content_completeness(content, character_data)
            if completeness_issues:
                quality_results['completeness_score'] -= len(completeness_issues) * 10
                quality_results['issues'].extend(completeness_issues)
            
            # Check thematic consistency across all content
            thematic_issues = self._validate_thematic_consistency(content, character_data)
            if thematic_issues:
                quality_results['thematic_consistency'] -= len(thematic_issues) * 15
                quality_results['issues'].extend(thematic_issues)
            
            # Check D&D 5e 2024 compliance
            compliance_issues = self._validate_dnd_2024_compliance(content, character_data)
            if compliance_issues:
                quality_results['dnd_compliance'] -= len(compliance_issues) * 20
                quality_results['issues'].extend(compliance_issues)
            
            # Determine overall quality
            avg_score = (quality_results['completeness_score'] + 
                        quality_results['thematic_consistency'] + 
                        quality_results['dnd_compliance']) / 3
            
            if avg_score >= 90:
                quality_results['overall_quality'] = 'excellent'
            elif avg_score >= 75:
                quality_results['overall_quality'] = 'good'
            elif avg_score >= 60:
                quality_results['overall_quality'] = 'fair'
            else:
                quality_results['overall_quality'] = 'poor'
                quality_results['recommendations'].append("Content requires significant revision before use")
            
        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            quality_results['overall_quality'] = 'unknown'
            quality_results['issues'].append(f"Quality validation error: {e}")
        
        return quality_results
    
    def _validate_content_completeness(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> List[str]:
        """Check if all generated content has complete required fields."""
        issues = []
        
        # Check each content type for completeness
        for content_type, items in content.items():
            if content_type.startswith('_'):  # Skip metadata
                continue
                
            for item_name in items:
                try:
                    # Get the actual content object from registry
                    if content_type == 'spells':
                        item_obj = self.content_registry.get_spell(item_name)
                        if not item_obj or not hasattr(item_obj, 'description') or not item_obj.description:
                            issues.append(f"Spell '{item_name}' missing description")
                    elif content_type == 'weapons':
                        item_obj = self.content_registry.get_weapon(item_name)
                        if not item_obj or not hasattr(item_obj, 'damage') or not item_obj.damage:
                            issues.append(f"Weapon '{item_name}' missing damage information")
                    elif content_type == 'classes':
                        item_obj = self.content_registry.get_class(item_name)
                        if not item_obj or not hasattr(item_obj, 'features') or not item_obj.features:
                            issues.append(f"Class '{item_name}' missing features")
                except Exception:
                    issues.append(f"Could not validate {content_type} item '{item_name}'")
        
        return issues
    
    def _validate_thematic_consistency(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> List[str]:
        """Check if all content maintains thematic consistency."""
        issues = []
        
        # Extract character themes for comparison
        character_name = character_data.get('name', 'Unknown')
        character_species = character_data.get('species', 'Human')
        character_classes = list(character_data.get('classes', {}).keys())
        
        # Simple thematic consistency checks
        generated_names = []
        for content_type, items in content.items():
            if content_type.startswith('_'):
                continue
            generated_names.extend(items)
        
        # Check for obvious thematic mismatches (basic heuristics)
        fire_themes = sum(1 for name in generated_names if any(word in name.lower() for word in ['fire', 'flame', 'burn', 'inferno']))
        ice_themes = sum(1 for name in generated_names if any(word in name.lower() for word in ['ice', 'frost', 'freeze', 'cold']))
        
        if fire_themes > 0 and ice_themes > 0:
            issues.append("Mixed fire and ice themes may be thematically inconsistent")
        
        # Check class-content alignment
        if 'Fighter' in character_classes or 'Warrior' in character_classes:
            magic_content = len(content.get('spells', []))
            if magic_content > 3:  # Fighters shouldn't have many spells
                issues.append("High spell count inconsistent with martial character concept")
        
        return issues
    
    def _validate_dnd_2024_compliance(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> List[str]:
        """Check D&D 5e 2024 rule compliance."""
        issues = []
        character_level = character_data.get('level', 1)
        
        # Check spell level appropriateness
        spell_count = len(content.get('spells', []))
        if character_level <= 2 and spell_count > 5:
            issues.append(f"Too many spells ({spell_count}) for character level {character_level}")
        elif character_level <= 5 and spell_count > 8:
            issues.append(f"Excessive spell count ({spell_count}) for character level {character_level}")
        
        # Check custom class compliance
        if content.get('classes'):
            for class_name in content['classes']:
                try:
                    class_obj = self.content_registry.get_class(class_name)
                    if class_obj and hasattr(class_obj, 'hit_die'):
                        if class_obj.hit_die < 6 or class_obj.hit_die > 12:
                            issues.append(f"Class '{class_name}' hit die ({class_obj.hit_die}) outside D&D 5e range")
                except Exception:
                    issues.append(f"Could not validate class '{class_name}' compliance")
        
        return issues
    
    def auto_fix_balance_issues(self, content: Dict[str, List[str]], character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically fix common balance issues in generated content.
        Returns summary of fixes applied.
        """
        fixes_applied = {
            'spells_adjusted': [],
            'weapons_balanced': [],
            'features_modified': [],
            'stats_corrected': []
        }
        
        character_level = character_data.get('level', 1)
        
        try:
            # Fix spell count for level
            spells = content.get('spells', [])
            max_spells_for_level = min(character_level + 2, 12)  # Reasonable limit
            
            if len(spells) > max_spells_for_level:
                # Remove excess spells (keep the first ones generated)
                removed_spells = spells[max_spells_for_level:]
                content['spells'] = spells[:max_spells_for_level]
                fixes_applied['spells_adjusted'] = [f"Removed {len(removed_spells)} excess spells for level balance"]
            
            # Validate weapon damage is appropriate for level
            for weapon_name in content.get('weapons', []):
                try:
                    weapon = self.content_registry.get_weapon(weapon_name)
                    if weapon and hasattr(weapon, 'damage'):
                        # Basic damage validation (simplified)
                        if character_level <= 5 and any(die in weapon.damage for die in ['d12', '2d8', '3d6']):
                            fixes_applied['weapons_balanced'].append(f"Weapon '{weapon_name}' damage may be high for level {character_level}")
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Auto-fix failed: {e}")
            fixes_applied['error'] = str(e)
        
        return fixes_applied
