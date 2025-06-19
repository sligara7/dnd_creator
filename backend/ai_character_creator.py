#!/usr/bin/env python3
"""
AI-Driven Character Creator - Creative Character Generation

This script uses the LLM service to create unique, non-traditional D&D characters
based on your prompts and descriptions. It can generate:
- Custom species and subspecies
- Unique character classes and subclasses  
- Custom feats, weapons, armor, and spells
- Rich backstories and personality traits

Usage:
    python ai_character_creator.py
    
Or in iPython:
    %run ai_character_creator.py
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from character_models import CharacterCore, DnDCondition
    from core_models import ProficiencyLevel
    from custom_content_models import ContentRegistry, CustomSpecies, CustomClass
    from llm_service_new import create_llm_service, create_ollama_service
    print("✅ Character, custom content, and LLM services imported successfully")
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class AICharacterCreator:
    """AI-driven character creation using LLM services with enhanced custom content."""
    
    def __init__(self):
        self.character = None
        self.llm_service = None
        self.content_registry = ContentRegistry()  # Enhanced registry with database and LLM
        self.character_concept = ""
        self.generated_content = {
            "species": None,
            "classes": {},
            "background": None,
            "personality": {},
            "equipment": [],
            "abilities": {},
            "custom_content": {
                "feats": [],
                "spells": [],
                "items": []
            }
        }
        
    def initialize_llm(self):
        """Initialize the LLM service and content registry."""
        print("🤖 Initializing AI service...")
        try:
            # Try Ollama first (local), fallback to others
            self.llm_service = create_ollama_service()
            print("✅ Connected to Ollama LLM service")
            
            # Set up the content registry with LLM integration
            self.content_registry.set_llm_service(self.llm_service)
            print("✅ Content registry initialized with LLM integration")
            
            return True
        except Exception as e:
            print(f"⚠️  Ollama not available: {e}")
            try:
                self.llm_service = create_llm_service()
                print("✅ Connected to default LLM service")
                
                # Set up the content registry with LLM integration
                self.content_registry.set_llm_service(self.llm_service)
                print("✅ Content registry initialized with LLM integration")
                
                return True
            except Exception as e2:
                print(f"❌ No LLM service available: {e2}")
                return False
    
    async def start_creation(self):
        """Start the AI-driven character creation process."""
        print("🎭 AI-Driven D&D Character Creator")
        print("=" * 50)
        print("Describe your character concept and I'll bring it to life!")
        print("I can create non-traditional species, classes, and abilities.\n")
        
        if not self.initialize_llm():
            print("❌ Cannot proceed without LLM service.")
            return
        
        # Get character concept from user
        concept = self.get_character_concept()
        if not concept:
            return
            
        self.character_concept = concept
        
        # Generate character using AI
        print(f"\n🔮 Creating character based on: '{concept}'")
        print("=" * 50)
        
        try:
            await self.generate_basic_info()
            await self.generate_species_and_classes()
            await self.generate_abilities()
            await self.generate_skills_and_background()
            await self.generate_equipment()
            await self.generate_custom_content()
            await self.generate_personality()
            
            self.create_character_object()
            self.display_final_character()
            
        except Exception as e:
            print(f"❌ Error during character generation: {e}")
            import traceback
            traceback.print_exc()
    
    def get_character_concept(self) -> str:
        """Get the character concept from the user."""
        print("Examples of character concepts:")
        print("• A crystal-powered artificer from a steampunk sky city")
        print("• A time-traveling druid who speaks with extinct creatures")
        print("• A shadow dancer who weaves darkness into magical weapons")
        print("• A dragon-touched healer with scales that change with emotions")
        print("• A void monk who fights by erasing parts of reality\n")
        
        concept = input("Describe your character concept: ").strip()
        
        if not concept:
            print("No concept provided. Goodbye!")
            return ""
        
        if concept.lower() in ['quit', 'exit']:
            return ""
            
        return concept
    
    async def generate_basic_info(self):
        """Generate basic character information."""
        print("📝 Generating basic character info...")
        
        prompt = f"""
        Based on this character concept: "{self.character_concept}"
        
        Generate a unique D&D character with the following JSON format:
        {{
            "name": "Character Name",
            "alignment": ["Ethical", "Moral"],
            "age": 25,
            "height": "5'8\"",
            "weight": "150 lbs",
            "appearance": "Detailed physical description",
            "voice": "How they speak and sound"
        }}
        
        Make the character interesting and unique. The alignment should be two words like ["Chaotic", "Good"].
        """
        
        try:
            response = await self.llm_service.generate_text(prompt)
            basic_info = self.parse_json_response(response)
            
            if basic_info:
                self.generated_content.update(basic_info)
                print(f"✅ Generated: {basic_info.get('name', 'Unknown')}")
                print(f"   Alignment: {' '.join(basic_info.get('alignment', ['True', 'Neutral']))}")
            else:
                print("⚠️  Using fallback basic info")
                self.generated_content.update({
                    "name": "Mysterious Wanderer",
                    "alignment": ["True", "Neutral"],
                    "age": 25,
                    "appearance": "An enigmatic figure with unique features"
                })
        except Exception as e:
            print(f"⚠️  Error generating basic info: {e}")
            self.generated_content.update({
                "name": "AI-Generated Hero",
                "alignment": ["Chaotic", "Good"]
            })
    
    async def generate_species_and_classes(self):
        """Generate unique species and class combinations using enhanced ContentRegistry."""
        print("🧬 Generating species and classes with rich descriptions...")
        
        # Parse the character concept to extract species and class hints
        species_hint, class_hint = self.extract_species_class_hints(self.character_concept)
        
        try:
            # Generate custom species with rich LLM description
            if species_hint:
                print(f"🌟 Creating custom species: {species_hint}")
                custom_species = await self.content_registry.create_species_with_llm(
                    species_hint, self.character_concept
                )
                self.generated_content["species"] = {
                    "name": custom_species.name,
                    "description": custom_species.description,
                    "traits": custom_species.innate_traits,
                    "creature_type": custom_species.creature_type,
                    "size": custom_species.size,
                    "speed": custom_species.speed
                }
                print(f"✅ Species: {custom_species.name}")
                print(f"   Description: {custom_species.description[:100]}...")
            
            # Generate custom class with rich LLM description
            if class_hint:
                print(f"⚔️ Creating custom class: {class_hint}")
                custom_class = await self.content_registry.create_class_with_llm(
                    class_hint, self.character_concept
                )
                self.generated_content["primary_class"] = {
                    "name": custom_class.name,
                    "description": custom_class.description,
                    "hit_die": custom_class.hit_die,
                    "level": 3,
                    "primary_ability": custom_class.primary_ability
                }
                print(f"✅ Class: {custom_class.name}")
                print(f"   Description: {custom_class.description[:100]}...")
            
            # Generate balanced ability scores
            self.generate_balanced_abilities()
            
        except Exception as e:
            print(f"⚠️  Error generating species/class: {e}")
            await self.use_fallback_species_class()
    
    def extract_species_class_hints(self, concept: str) -> Tuple[str, str]:
        """Extract species and class hints from the character concept."""
        concept_lower = concept.lower()
        
        # Common species patterns
        species_patterns = {
            "crystal": "Crystalkin",
            "shadow": "Shadowborn", 
            "void": "Voidtouched",
            "dragon": "Dragonkin",
            "time": "Chronarch",
            "star": "Starborn",
            "dream": "Dreamwalker",
            "storm": "Stormcaller",
            "flame": "Flameborn",
            "ice": "Frostkin"
        }
        
        # Common class patterns
        class_patterns = {
            "artificer": "Artificer",
            "dancer": "Shadow Dancer",
            "monk": "Monk",
            "healer": "Divine Healer", 
            "druid": "Druid",
            "time": "Chronomancer",
            "void": "Void Walker",
            "crystal": "Crystal Mage",
            "shadow": "Shadowblade",
            "dragon": "Dragon Knight"
        }
        
        species_hint = None
        class_hint = None
        
        # Find species hint
        for pattern, species in species_patterns.items():
            if pattern in concept_lower:
                species_hint = species
                break
        
        # Find class hint
        for pattern, class_name in class_patterns.items():
            if pattern in concept_lower:
                class_hint = class_name
                break
        
        # Generate defaults if no hints found
        if not species_hint:
            species_hint = "Mystical Being"
        if not class_hint:
            class_hint = "Arcane Warrior"
        
        return species_hint, class_hint
    
    async def use_fallback_species_class(self):
        """Use fallback species and class generation."""
        print("🎲 Using fallback species and class generation...")
        
        # Create simple custom species
        try:
            fallback_species = await self.content_registry.create_species_with_llm(
                "Wanderer", "A mysterious traveler with unknown origins"
            )
            self.generated_content["species"] = {
                "name": fallback_species.name,
                "description": fallback_species.description
            }
        except Exception:
            self.generated_content["species"] = {
                "name": "Human",
                "description": "A versatile and adaptable species."
            }
        
        # Create simple custom class
        try:
            fallback_class = await self.content_registry.create_class_with_llm(
                "Adventurer", "A versatile hero skilled in many arts"
            )
            self.generated_content["primary_class"] = {
                "name": fallback_class.name,
                "description": fallback_class.description,
                "level": 3
            }
        except Exception:
            self.generated_content["primary_class"] = {
                "name": "Fighter",
                "description": "A master of martial combat.",
                "level": 3
            }
    
    def generate_balanced_abilities(self):
        """Generate balanced ability scores."""
        # Create a balanced spread that totals around 75-80
        abilities = {
            "strength": 13,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 14
        }
        
        # Adjust based on class
        class_name = self.generated_content.get("primary_class", {}).get("name", "").lower()
        
        if any(word in class_name for word in ["mage", "wizard", "scholar"]):
            abilities["intelligence"] = 16
            abilities["strength"] = 10
        elif any(word in class_name for word in ["dancer", "rogue", "ranger"]):
            abilities["dexterity"] = 16
            abilities["strength"] = 10
        elif any(word in class_name for word in ["healer", "priest", "druid"]):
            abilities["wisdom"] = 16
            abilities["intelligence"] = 10
        elif any(word in class_name for word in ["warrior", "knight", "fighter"]):
            abilities["strength"] = 16
            abilities["intelligence"] = 10
        
        self.generated_content["abilities"] = abilities
    
    async def generate_abilities(self):
        """Generate ability scores based on character concept."""
        print("💪 Generating ability scores...")
        
        species_abilities = self.generated_content.get("species", {}).get("abilities", {})
        if species_abilities:
            self.generated_content["abilities"] = species_abilities
            print("✅ Ability scores set from species")
        else:
            # Generate balanced ability scores
            self.generated_content["abilities"] = {
                "strength": 13,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 16
            }
            print("✅ Generated balanced ability scores")
    
    async def generate_skills_and_background(self):
        """Generate skills and background."""
        print("🎯 Generating skills and background...")
        
        prompt = f"""
        For this character: "{self.character_concept}"
        With species: {self.generated_content.get("species", {}).get("name", "Unknown")}
        And class: {self.generated_content.get("primary_class", {}).get("name", "Unknown")}
        
        Generate skills and background in JSON format:
        {{
            "background": {{
                "name": "Background Name",
                "description": "What they did before adventuring"
            }},
            "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"],
            "languages": ["Common", "Language 2", "Language 3"],
            "proficiencies": ["Tool 1", "Tool 2"]
        }}
        
        Choose skills that make sense for the character concept.
        """
        
        try:
            response = await self.llm_service.generate_text(prompt)
            skills_bg = self.parse_json_response(response)
            
            if skills_bg:
                self.generated_content["background"] = skills_bg.get("background")
                self.generated_content["skills"] = skills_bg.get("skills", [])
                self.generated_content["languages"] = skills_bg.get("languages", ["Common"])
                print(f"✅ Background: {skills_bg.get('background', {}).get('name', 'Unknown')}")
                print(f"✅ Skills: {', '.join(skills_bg.get('skills', []))}")
            else:
                self.use_fallback_skills_background()
        except Exception as e:
            print(f"⚠️  Error generating skills/background: {e}")
            self.use_fallback_skills_background()
    
    async def generate_equipment(self):
        """Generate starting equipment."""
        print("⚔️ Generating equipment...")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        
        Generate starting equipment in JSON format:
        {{
            "weapons": ["Weapon 1", "Weapon 2"],
            "armor": "Armor type",
            "tools": ["Tool 1", "Tool 2"],
            "items": ["Item 1", "Item 2", "Item 3"],
            "magical_items": ["Magic Item 1"]
        }}
        
        Be creative with equipment that matches the character concept.
        Include both practical and unique items.
        """
        
        try:
            response = await self.llm_service.generate_text(prompt)
            equipment = self.parse_json_response(response)
            
            if equipment:
                self.generated_content["equipment"] = equipment
                print(f"✅ Equipment generated")
            else:
                self.use_fallback_equipment()
        except Exception as e:
            print(f"⚠️  Error generating equipment: {e}")
            self.use_fallback_equipment()
    
    async def generate_custom_content(self):
        """Generate custom feats, spells, and items."""
        print("✨ Generating custom content...")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        
        Create custom D&D content in JSON format:
        {{
            "custom_feats": [
                {{
                    "name": "Feat Name",
                    "description": "What the feat does",
                    "prerequisites": "Any requirements"
                }}
            ],
            "custom_spells": [
                {{
                    "name": "Spell Name", 
                    "level": 1,
                    "school": "Magic School",
                    "description": "Spell effect"
                }}
            ],
            "custom_items": [
                {{
                    "name": "Item Name",
                    "type": "Item type",
                    "description": "What makes it special"
                }}
            ]
        }}
        
        Create 1-2 items for each category that perfectly match the character concept.
        """
        
        try:
            response = await self.llm_service.generate_text(prompt)
            custom_content = self.parse_json_response(response)
            
            if custom_content:
                self.generated_content["custom_content"] = custom_content
                print("✅ Custom content created")
                
                # Show what was created
                if custom_content.get("custom_feats"):
                    print(f"   • {len(custom_content['custom_feats'])} custom feats")
                if custom_content.get("custom_spells"):
                    print(f"   • {len(custom_content['custom_spells'])} custom spells")
                if custom_content.get("custom_items"):
                    print(f"   • {len(custom_content['custom_items'])} custom items")
        except Exception as e:
            print(f"⚠️  Error generating custom content: {e}")
    
    async def generate_personality(self):
        """Generate personality traits and backstory."""
        print("🎭 Generating personality and backstory...")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        With name: {self.generated_content.get("name", "Unknown")}
        
        Generate personality in JSON format:
        {{
            "personality_traits": ["Trait 1", "Trait 2"],
            "ideals": ["Ideal 1"],
            "bonds": ["Bond 1"],
            "flaws": ["Flaw 1"],
            "backstory": "A rich backstory of 2-3 paragraphs explaining their origin, motivations, and how they became who they are."
        }}
        
        Make the personality complex and interesting, with internal conflicts and clear motivations.
        """
        
        try:
            response = await self.llm_service.generate_text(prompt)
            personality = self.parse_json_response(response)
            
            if personality:
                self.generated_content["personality"] = personality
                print("✅ Personality and backstory generated")
            else:
                self.use_fallback_personality()
        except Exception as e:
            print(f"⚠️  Error generating personality: {e}")
            self.use_fallback_personality()
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        try:
            # Try to find JSON in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                print("⚠️  No JSON found in response")
                return None
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            return None
    
    def create_character_object(self):
        """Create the CharacterCore object from generated content with custom content linking."""
        print("\n🏗️ Building character object...")
        
        name = self.generated_content.get("name", "AI Hero")
        self.character = CharacterCore(name=name)
        
        # Set basic info
        if "alignment" in self.generated_content:
            self.character.alignment = self.generated_content["alignment"]
        
        # Set species
        species_info = self.generated_content.get("species", {})
        species_name = species_info.get("name", "Custom Species")
        self.character.species = species_name
        
        # Set background
        background_info = self.generated_content.get("background", {})
        self.character.background = background_info.get("name", "Unique Background")
        
        # Set classes
        primary_class = self.generated_content.get("primary_class", {})
        if primary_class:
            class_name = primary_class.get("name", "Custom Class")
            class_level = primary_class.get("level", 1)
            self.character.character_classes[class_name] = class_level
        
        secondary_class = self.generated_content.get("secondary_class", {})
        if secondary_class and secondary_class.get("name"):
            class_name = secondary_class.get("name", "Second Class")
            class_level = secondary_class.get("level", 1)
            self.character.character_classes[class_name] = class_level
        
        # Set ability scores
        abilities = self.generated_content.get("abilities", {})
        for ability, score in abilities.items():
            self.character.set_ability_score(ability, score)
        
        # Set skills
        skills = self.generated_content.get("skills", [])
        for skill in skills:
            skill_key = skill.lower().replace(" ", "_")
            self.character.skill_proficiencies[skill_key] = ProficiencyLevel.PROFICIENT
        
        # Set personality
        personality = self.generated_content.get("personality", {})
        self.character.personality_traits = personality.get("personality_traits", [])
        self.character.ideals = personality.get("ideals", [])
        self.character.bonds = personality.get("bonds", [])
        self.character.flaws = personality.get("flaws", [])
        self.character.backstory = personality.get("backstory", "")
        
        # Link custom content to character
        custom_content_names = []
        if species_info.get("name") and species_info["name"] not in ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"]:
            custom_content_names.append(f"Species: {species_info['name']}")
        
        if primary_class.get("name") and primary_class["name"] not in ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Paladin", "Barbarian", "Bard", "Druid", "Monk", "Sorcerer", "Warlock"]:
            custom_content_names.append(f"Class: {primary_class['name']}")
        
        if secondary_class.get("name"):
            custom_content_names.append(f"Multiclass: {secondary_class['name']}")
        
        # Link to content registry
        if custom_content_names:
            character_id = f"{name}_{hash(name) % 10000}"  # Simple character ID
            self.content_registry.link_content_to_character(character_id, custom_content_names)
            print(f"🔗 Linked {len(custom_content_names)} custom content items to character")
        
        print("✅ Character object created with custom content links!")
    
    def display_final_character(self):
        """Display the complete AI-generated character."""
        print("\n" + "=" * 80)
        print("🎭 AI-GENERATED CHARACTER SHEET")
        print("=" * 80)
        
        # Basic Info
        print(f"Name: {self.character.name}")
        print(f"Species: {self.character.species}")
        print(f"Background: {self.character.background}")
        print(f"Alignment: {' '.join(self.character.alignment)}")
        
        # Physical Description
        if "appearance" in self.generated_content:
            print(f"Appearance: {self.generated_content['appearance']}")
        
        # Classes
        if self.character.character_classes:
            classes_str = ", ".join([f"{cls} {lvl}" for cls, lvl in self.character.character_classes.items()])
            total_level = sum(self.character.character_classes.values())
            print(f"Class(es): {classes_str} (Total Level: {total_level})")
        
        # Ability Scores
        print("\nAbility Scores:")
        modifiers = self.character.get_ability_modifiers()
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            ability_score_obj = self.character.get_ability_score(ability)
            score = ability_score_obj.total_score if hasattr(ability_score_obj, 'total_score') else 10
            modifier = modifiers.get(ability, 0)
            sign = "+" if modifier >= 0 else ""
            print(f"  {ability.title():13}: {score:2d} ({sign}{modifier})")
        
        # Skills
        if self.character.skill_proficiencies:
            skills = [skill.replace("_", " ").title() for skill in self.character.skill_proficiencies.keys()]
            print(f"\nSkill Proficiencies: {', '.join(skills)}")
        
        # Equipment
        equipment = self.generated_content.get("equipment", {})
        if equipment:
            print(f"\nEquipment:")
            if equipment.get("weapons"):
                print(f"  Weapons: {', '.join(equipment['weapons'])}")
            if equipment.get("armor"):
                print(f"  Armor: {equipment['armor']}")
            if equipment.get("tools"):
                print(f"  Tools: {', '.join(equipment['tools'])}")
            if equipment.get("magical_items"):
                print(f"  Magic Items: {', '.join(equipment['magical_items'])}")
        
        # Custom Content
        custom = self.generated_content.get("custom_content", {})
        if custom:
            print(f"\nCustom Content:")
            
            if custom.get("custom_feats"):
                print("  Custom Feats:")
                for feat in custom["custom_feats"]:
                    print(f"    • {feat['name']}: {feat['description']}")
            
            if custom.get("custom_spells"):
                print("  Custom Spells:")
                for spell in custom["custom_spells"]:
                    print(f"    • {spell['name']} (Level {spell['level']}): {spell['description']}")
            
            if custom.get("custom_items"):
                print("  Custom Items:")
                for item in custom["custom_items"]:
                    print(f"    • {item['name']}: {item['description']}")
        
        # Personality
        print(f"\nPersonality:")
        if self.character.personality_traits:
            print(f"  Traits: {', '.join(self.character.personality_traits)}")
        if self.character.ideals:
            print(f"  Ideals: {', '.join(self.character.ideals)}")
        if self.character.bonds:
            print(f"  Bonds: {', '.join(self.character.bonds)}")
        if self.character.flaws:
            print(f"  Flaws: {', '.join(self.character.flaws)}")
        
        # Backstory
        if self.character.backstory:
            print(f"\nBackstory:")
            print(f"  {self.character.backstory}")
        
        print("\n" + "=" * 80)
        print("🎉 Your AI-generated character is complete!")
        print("How does this match your creative vision?")
        print("=" * 80)
    
    # Fallback methods for when AI generation fails
    def use_fallback_skills_background(self):
        self.generated_content["background"] = {"name": "Wanderer"}
        self.generated_content["skills"] = ["Perception", "Insight", "Athletics", "Investigation"]
    
    def use_fallback_equipment(self):
        self.generated_content["equipment"] = {
            "weapons": ["Longsword", "Shortbow"],
            "armor": "Studded Leather",
            "items": ["Explorer's Pack", "Rope", "Torches"]
        }
    
    def use_fallback_personality(self):
        self.generated_content["personality"] = {
            "personality_traits": ["Curious about the unknown"],
            "ideals": ["Adventure calls to me"],
            "bonds": ["I seek my true purpose"],
            "flaws": ["I act before thinking"],
            "backstory": "A mysterious figure with an unknown past, driven by curiosity and wanderlust."
        }


async def main():
    """Main function for AI character creation."""
    try:
        creator = AICharacterCreator()
        await creator.start_creation()
    except KeyboardInterrupt:
        print("\n\nCharacter creation cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
