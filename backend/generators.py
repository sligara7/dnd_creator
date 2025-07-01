# ## **6. `generators.py`**
# **Application services for content generation**
# - **Classes**: `BackstoryGenerator`, `CustomContentGenerator`
# - **Purpose**: AI-powered generation of backstories, custom species/classes/items/spells
# - **Dependencies**: `llm_services.py`, `custom_content_models.py`

from typing import Dict, Any, List, Optional
import json
import logging
from llm_service import LLMService
from custom_content_models import (
    ContentRegistry, CustomSpecies, CustomClass, CustomSpell, 
    CustomWeapon, CustomArmor, CustomFeat, CustomItem
)
from core_models import SpellcastingManager

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
        
        json_str = response[start:end+1]
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        json_str = ' '.join(json_str.split())
        
        return json_str
    
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

# ============================================================================
# ITEM GENERATOR
# ============================================================================

class ItemGenerator:
    """LLM-powered generator for custom items (optional for DM use)."""
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.base_timeout = 15

    async def generate_item(self, item_type: str, name: str = "", description: str = "", extra_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a custom item using LLM. Returns a dict with item fields.
        item_type: 'weapon', 'armor', 'spell', 'equipment', etc.
        """
        prompt = f"""Create a D&D {item_type} for DM use. Return ONLY JSON.\nName: {name}\nDescription: {description}\nInclude all relevant fields for a {item_type}."""
        if extra_fields:
            prompt += f"\nExtra: {extra_fields}"
        try:
            response = await self.llm_service.generate_content(prompt)
            cleaned = self._clean_json_response(response)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Item LLM generation failed: {e}")
            return {"name": name, "item_type": item_type, "description": description, **(extra_fields or {})}

    def _clean_json_response(self, response: str) -> str:
        if not response:
            raise ValueError("Empty response")
        response = response.strip().replace('```json', '').replace('```', '')
        start = response.find('{')
        end = response.rfind('}')
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        return response[start:end+1]

# ============================================================================
# CHARACTER GENERATOR
# ============================================================================

class CharacterGenerator:
    """Comprehensive generator for full D&D characters (PCs)."""
    def __init__(self, llm_service: LLMService, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
        self.custom_content_generator = CustomContentGenerator(llm_service, content_registry)
        self.backstory_generator = BackstoryGenerator(llm_service)

    def generate_character(self, character_concept: Dict[str, Any], user_description: str) -> Dict[str, Any]:
        """
        Generate a complete character including stats, levels, class, species, equipment, spells, and backstory.
        Returns a dictionary representing the full character.
        """
        # 1. Generate ability scores (using standard array for now)
        ability_scores = self._generate_ability_scores()

        # 2. Assign level (default to 1 if not provided)
        level = character_concept.get('level', 1)

        # 3. Generate custom content (species, class, spells, etc.)
        custom_content = self.custom_content_generator.generate_custom_content_for_character(
            character_concept, user_description
        )

        # 4. Assign species and class (use custom if generated, else fallback to concept)
        species = custom_content['species'][0] if custom_content['species'] else character_concept.get('species', 'Human')
        classes = custom_content['classes'] if custom_content['classes'] else list(character_concept.get('classes', {}).keys() or ['Fighter'])

        # 5. Assign spells (if any)
        spells = custom_content['spells']

        # 6. Assign equipment (basic package + custom weapons/armor)
        equipment = self._generate_equipment(level, custom_content, character_concept)

        # 7. Generate backstory
        backstory = self.backstory_generator.generate_backstory({
            'name': character_concept.get('name', 'Unknown'),
            'species': species,
            'classes': {cls: level for cls in classes},
            'level': level
        }, user_description)

        # 8. Assemble character
        character = {
            'name': character_concept.get('name', 'Unknown'),
            'species': species,
            'classes': {cls: level for cls in classes},
            'level': level,
            'ability_scores': ability_scores,
            'equipment': equipment,
            'spells': spells,
            'backstory': backstory,
            'custom_content': custom_content
        }
        return character

    def _generate_ability_scores(self) -> Dict[str, int]:
        # Standard array for D&D 5e
        return {
            'Strength': 15,
            'Dexterity': 14,
            'Constitution': 13,
            'Intelligence': 12,
            'Wisdom': 10,
            'Charisma': 8
        }

    def _generate_equipment(self, level: int, custom_content: Dict[str, List[str]], character_concept: Dict[str, Any]) -> List[str]:
        # Basic equipment package + custom weapons/armor
        equipment = []
        # Add custom weapons
        equipment.extend(custom_content.get('weapons', []))
        # Add custom armor
        equipment.extend(custom_content.get('armor', []))
        # Add basic adventuring gear (placeholder)
        if level <= 4:
            equipment.append('Backpack')
            equipment.append('Rations (5 days)')
            equipment.append('Waterskin')
        else:
            equipment.append('Explorer\'s Pack')
        # Add any concept-specified items
        equipment.extend(character_concept.get('equipment', []))
        return equipment

    def update_character(self, existing_character: Dict[str, Any], user_description: str = "", update_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Hybrid workflow: Supplement or update an existing character with new generated content.
        Only generates/updates fields specified in update_fields (if provided), otherwise fills any missing fields.
        """
        character = existing_character.copy()
        update_fields = update_fields or []

        # Update or fill ability scores
        if ('ability_scores' in update_fields or ('ability_scores' not in character)):
            character['ability_scores'] = self._generate_ability_scores()

        # Update or fill level
        if ('level' in update_fields or ('level' not in character)):
            character['level'] = character.get('level', 1)
        level = character['level']

        # Update or supplement custom content
        if ('custom_content' in update_fields or ('custom_content' not in character)):
            custom_content = self.custom_content_generator.generate_custom_content_for_character(character, user_description)
            character['custom_content'] = custom_content
        else:
            custom_content = character.get('custom_content', {})

        # Update or fill species
        if ('species' in update_fields or ('species' not in character or not character['species'])):
            species = custom_content['species'][0] if custom_content.get('species') else character.get('species', 'Human')
            character['species'] = species

        # Update or fill classes
        if ('classes' in update_fields or ('classes' not in character or not character['classes'])):
            classes = custom_content['classes'] if custom_content.get('classes') else list(character.get('classes', {}).keys() or ['Fighter'])
            character['classes'] = {cls: level for cls in classes}

        # Update or fill spells
        if ('spells' in update_fields or ('spells' not in character)):
            character['spells'] = custom_content.get('spells', [])

        # Update or fill equipment
        if ('equipment' in update_fields or ('equipment' not in character)):
            character['equipment'] = self._generate_equipment(level, custom_content, character)

        # Update or fill backstory
        if ('backstory' in update_fields or ('backstory' not in character or not character['backstory'])):
            character['backstory'] = self.backstory_generator.generate_backstory({
                'name': character.get('name', 'Unknown'),
                'species': character.get('species', 'Human'),
                'classes': character.get('classes', {}),
                'level': level
            }, user_description)

        return character

    def update_backstory(self, existing_character: Dict[str, Any], user_description: str = "") -> Dict[str, Any]:
        """
        Use the generator pipeline to update an existing character's backstory only.
        """
        character = existing_character.copy()
        level = character.get('level', 1)
        character['backstory'] = self.backstory_generator.generate_backstory({
            'name': character.get('name', 'Unknown'),
            'species': character.get('species', 'Human'),
            'classes': character.get('classes', {}),
            'level': level
        }, user_description)
        return character

class NPCGenerator:
    """Generator for non-player characters (NPCs) with appropriate gear and spells."""
    def __init__(self, llm_service: LLMService, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry
        self.custom_content_generator = CustomContentGenerator(llm_service, content_registry)

    def generate_npc(self, npc_role: str, user_description: str = "") -> Dict[str, Any]:
        """
        Generate an NPC for a specific role (e.g., merchant, guard, villain), with gear and spells.
        Returns a dictionary representing the NPC.
        """
        # 1. Generate base stats (simplified for NPCs)
        stats = self._generate_npc_stats(npc_role)
        # 2. Generate custom content if needed
        custom_content = self.custom_content_generator.generate_custom_content_for_character({'name': npc_role, 'classes': {npc_role: 1}}, user_description)
        # 3. Assign equipment and spells
        equipment = self._generate_npc_equipment(npc_role, custom_content)
        spells = custom_content.get('spells', [])
        # 4. Assemble NPC
        npc = {
            'role': npc_role,
            'stats': stats,
            'equipment': equipment,
            'spells': spells,
            'custom_content': custom_content
        }
        return npc

    def _generate_npc_stats(self, npc_role: str) -> Dict[str, int]:
        # Simple stat block by role
        base_stats = {
            'Strength': 10,
            'Dexterity': 10,
            'Constitution': 10,
            'Intelligence': 10,
            'Wisdom': 10,
            'Charisma': 10
        }
        if npc_role.lower() in ['guard', 'soldier', 'warrior']:
            base_stats['Strength'] += 2
            base_stats['Constitution'] += 2
        elif npc_role.lower() in ['mage', 'wizard', 'sorcerer']:
            base_stats['Intelligence'] += 3
        elif npc_role.lower() in ['priest', 'cleric']:
            base_stats['Wisdom'] += 3
        elif npc_role.lower() in ['merchant', 'noble']:
            base_stats['Charisma'] += 3
        return base_stats

    def _generate_npc_equipment(self, npc_role: str, custom_content: Dict[str, List[str]]) -> List[str]:
        equipment = []
        equipment.extend(custom_content.get('weapons', []))
        equipment.extend(custom_content.get('armor', []))
        if npc_role.lower() in ['merchant']:
            equipment.append('Trade Goods')
        elif npc_role.lower() in ['guard', 'soldier', 'warrior']:
            equipment.append('Shield')
        elif npc_role.lower() in ['mage', 'wizard', 'sorcerer']:
            equipment.append('Spellbook')
        return equipment

class CreatureGenerator:
    """Generator for monsters, beasts, and other non-PC creatures."""
    def __init__(self, llm_service: LLMService, content_registry: ContentRegistry):
        self.llm_service = llm_service
        self.content_registry = content_registry

    def generate_creature(self, creature_type: str, user_description: str = "") -> Dict[str, Any]:
        """
        Generate a creature (monster, beast, etc.) with stats, abilities, and traits.
        Returns a dictionary representing the creature.
        """
        # 1. Generate base stats by type
        stats = self._generate_creature_stats(creature_type)
        # 2. Generate abilities/traits (placeholder, could use LLM)
        abilities = self._generate_creature_abilities(creature_type, user_description)
        # 3. Assemble creature
        creature = {
            'type': creature_type,
            'stats': stats,
            'abilities': abilities,
            'description': user_description
        }
        return creature

    def _generate_creature_stats(self, creature_type: str) -> Dict[str, int]:
        # Simple stat block by type
        base_stats = {
            'Strength': 12,
            'Dexterity': 12,
            'Constitution': 12,
            'Intelligence': 2,
            'Wisdom': 10,
            'Charisma': 6
        }
        if creature_type.lower() in ['dragon']:
            base_stats['Strength'] = 20
            base_stats['Constitution'] = 18
            base_stats['Intelligence'] = 14
            base_stats['Charisma'] = 16
        elif creature_type.lower() in ['beast', 'animal']:
            base_stats['Intelligence'] = 2
            base_stats['Wisdom'] = 12
        elif creature_type.lower() in ['undead']:
            base_stats['Constitution'] = 16
            base_stats['Charisma'] = 12
        return base_stats

    def _generate_creature_abilities(self, creature_type: str, user_description: str) -> List[str]:
        # Placeholder: could use LLM for richer abilities
        abilities = []
        if creature_type.lower() == 'dragon':
            abilities.append('Breath Weapon')
            abilities.append('Flight')
        elif creature_type.lower() == 'undead':
            abilities.append('Undead Fortitude')
        elif creature_type.lower() == 'beast':
            abilities.append('Keen Senses')
        if user_description:
            abilities.append(f"Special: {user_description}")
        return abilities

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

    def _determine_custom_spellcasting_type(self, custom_class: Optional[Any], user_description: str) -> Dict[str, Any]:
        """Determine spellcasting type and mechanics for a custom class."""
        spellcasting_type = detect_spellcasting_type(custom_class, user_description)
        
        return {
            "type": spellcasting_type,
            "ability": self._get_spellcasting_ability(spellcasting_type, user_description),
            "progression": self._get_spell_progression_type(spellcasting_type),
            "ritual_casting": spellcasting_type in ["full"],
            "spell_focus": self._get_spell_focus_type(spellcasting_type, user_description)
        }
    
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
def detect_spellcasting_type(custom_class: Optional[Any], user_description: str = "") -> str:
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