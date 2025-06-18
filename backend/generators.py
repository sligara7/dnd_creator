# ## **6. `generators.py`**
# **Application services for content generation**
# - **Classes**: `BackstoryGenerator`, `CustomContentGenerator`
# - **Purpose**: AI-powered generation of backstories, custom species/classes/items/spells
# - **Dependencies**: `llm_services.py`, `custom_content_models.py`

from typing import Dict, Any, List, Optional
import json
import logging
from llm_service_new import LLMService
from custom_content_models import (
    ContentRegistry, CustomSpecies, CustomClass, CustomSpell, 
    CustomWeapon, CustomArmor, CustomFeat, CustomItem
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
    
    def generate_compelling_backstory(self, character_data: Dict[str, Any], 
                                    user_description: str) -> Dict[str, str]:
        """Generate backstory with comprehensive fallbacks."""
        
        logger.info("Starting backstory generation...")
        
        try:
            return self._generate_simple_backstory(character_data, user_description)
        except Exception as e:
            logger.warning(f"Backstory generation failed: {e}")
            return self._get_fallback_backstory(character_data, user_description)
    
    def generate_backstory(self, character_data: Dict[str, Any], 
                          user_description: str) -> Dict[str, str]:
        """Generate backstory - alias for generate_compelling_backstory."""
        return self.generate_compelling_backstory(character_data, user_description)
    
    def _generate_simple_backstory(self, character_data: Dict[str, Any], 
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
            response = self.llm_service.generate(prompt, timeout_seconds=self.base_timeout)
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
    
    def generate_custom_content_for_character(self, character_data: Dict[str, Any], 
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
                species = self._generate_custom_species(character_data, user_description)
                if species:
                    self.content_registry.register_species(species)
                    created_content["species"].append(species.name)
            
            # Generate custom class if needed
            if self._should_create_custom_class(character_data, user_description):
                custom_class = self._generate_custom_class(character_data, user_description)
                if custom_class:
                    self.content_registry.register_class(custom_class)
                    created_content["classes"].append(custom_class.name)
            
            # Generate custom spells for spellcasters
            if self._character_is_spellcaster(character_data):
                spells = self._generate_custom_spells(character_data, user_description, count=2)
                for spell in spells:
                    if spell:
                        self.content_registry.register_spell(spell)
                        created_content["spells"].append(spell.name)
            
            # Generate custom weapons
            weapons = self._generate_custom_weapons(character_data, user_description, count=1)
            for weapon in weapons:
                if weapon:
                    self.content_registry.register_weapon(weapon)
                    created_content["weapons"].append(weapon.name)
            
            # Generate custom armor
            armor = self._generate_custom_armor(character_data, user_description)
            if armor:
                self.content_registry.register_armor(armor)
                created_content["armor"].append(armor.name)
            
            # Generate custom feat
            feat = self._generate_custom_feat(character_data, user_description)
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
        """Check if character is a spellcaster."""
        spellcasting_classes = ["wizard", "sorcerer", "warlock", "bard", "cleric", "druid", "ranger", "paladin"]
        classes = [cls.lower() for cls in character_data.get('classes', {}).keys()]
        return any(cls in spellcasting_classes for cls in classes)
    
    def _generate_custom_species(self, character_data: Dict[str, Any], 
                               user_description: str) -> Optional[CustomSpecies]:
        """Generate a custom species."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D species for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Species Name","size":"Medium","speed":30,"traits":["trait1","trait2"],"languages":["Common"],"proficiencies":[],"ability_score_bonuses":{{}},"description":"Brief description"}}"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=20)
            data = json.loads(self._clean_json_response(response))
            
            return CustomSpecies(
                name=data["name"],
                size=data["size"],
                speed=data["speed"],
                innate_traits=data["traits"],
                languages=data["languages"],
                proficiencies=data["proficiencies"],
                ability_score_bonuses=data.get("ability_score_bonuses", {}),
                description=data["description"]
            )
        except Exception as e:
            logger.error(f"Failed to generate custom species: {e}")
            return None
    
    def _generate_custom_class(self, character_data: Dict[str, Any], 
                             user_description: str) -> Optional[CustomClass]:
        """Generate a custom class."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D class for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Class Name","hit_die":8,"primary_ability":"Strength","saves":["Strength","Constitution"],"proficiencies":{{"armor":["Light"],"weapons":["Simple"],"tools":[],"skills":2}},"features":{{"1":[{{"name":"Feature","description":"Description"}}]}},"description":"Brief description"}}"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=20)
            data = json.loads(self._clean_json_response(response))
            
            return CustomClass(
                name=data["name"],
                hit_die=data["hit_die"],
                primary_ability=data["primary_ability"],
                saving_throw_proficiencies=data["saves"],
                armor_proficiencies=data["proficiencies"]["armor"],
                weapon_proficiencies=data["proficiencies"]["weapons"],
                tool_proficiencies=data["proficiencies"]["tools"],
                skill_choices=data["proficiencies"]["skills"],
                features=data["features"],
                description=data["description"]
            )
        except Exception as e:
            logger.error(f"Failed to generate custom class: {e}")
            return None
    
    def _generate_custom_spells(self, character_data: Dict[str, Any], 
                              user_description: str, count: int = 3) -> List[CustomSpell]:
        """Generate custom spells."""
        spells = []
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create {count} unique D&D spells for {name}.
Description: {user_description}

Return ONLY this JSON array:
[{{"name":"Spell Name","level":1,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","description":"Spell effect"}}]"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=25)
            data = json.loads(self._clean_json_response(response))
            
            for spell_data in data[:count]:
                spell = CustomSpell(
                    name=spell_data["name"],
                    level=spell_data["level"],
                    school=spell_data["school"],
                    casting_time=spell_data["casting_time"],
                    range=spell_data["range"],
                    components=spell_data["components"],
                    duration=spell_data["duration"],
                    description=spell_data["description"]
                )
                spells.append(spell)
        except Exception as e:
            logger.error(f"Failed to generate custom spells: {e}")
        
        return spells
    
    def _generate_custom_weapons(self, character_data: Dict[str, Any], 
                               user_description: str, count: int = 2) -> List[CustomWeapon]:
        """Generate custom weapons."""
        weapons = []
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create {count} unique D&D weapons for {name}.
Description: {user_description}

Return ONLY this JSON array:
[{{"name":"Weapon Name","weapon_type":"martial","damage":"1d8","damage_type":"slashing","properties":["versatile"],"weight":3,"cost":"15 gp","description":"Weapon description"}}]"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=25)
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
    
    def _generate_custom_armor(self, character_data: Dict[str, Any], 
                             user_description: str) -> Optional[CustomArmor]:
        """Generate custom armor."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create unique D&D armor for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Armor Name","armor_type":"light","base_ac":12,"dex_modifier_max":2,"strength_requirement":0,"stealth_disadvantage":false,"weight":10,"cost":"50 gp","description":"Armor description"}}"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=20)
            data = json.loads(self._clean_json_response(response))
            
            return CustomArmor(
                name=data["name"],
                armor_type=data["armor_type"],
                base_ac=data["base_ac"],
                dex_modifier_max=data.get("dex_modifier_max"),
                strength_requirement=data.get("strength_requirement", 0),
                stealth_disadvantage=data.get("stealth_disadvantage", False),
                weight=data["weight"],
                cost=data["cost"],
                description=data["description"]
            )
        except Exception as e:
            logger.error(f"Failed to generate custom armor: {e}")
            return None
    
    def _generate_custom_feat(self, character_data: Dict[str, Any], 
                            user_description: str) -> Optional[CustomFeat]:
        """Generate custom feat."""
        try:
            name = character_data.get('name', 'Unknown')
            
            prompt = f"""Create a unique D&D feat for {name}.
Description: {user_description}

Return ONLY this JSON:
{{"name":"Feat Name","prerequisites":"None","benefits":["Benefit 1","Benefit 2"],"description":"Feat description"}}"""
            
            response = self.llm_service.generate(prompt, timeout_seconds=20)
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
        start = response.find('{') if '{' in response else response.find('[')
        end = response.rfind('}') if '}' in response else response.rfind(']')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[start:end+1]
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        json_str = ' '.join(json_str.split())
        
        return json_str
    
    def generate_custom_species(self, character_data: Dict[str, Any], 
                               user_description: str) -> Optional[Any]:
        """Generate custom species - public interface."""
        return self._generate_custom_species(character_data, user_description)
