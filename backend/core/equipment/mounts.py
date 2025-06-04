# mounts.py
# Description: Handles mount equipment for transportation and companion animals

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class MountType(Enum):
    """Types of mounts"""
    HORSE = "horse"         # Standard horses of various breeds
    PONY = "pony"           # Smaller equines
    CAMEL = "camel"         # Desert-adapted mounts
    ELEPHANT = "elephant"   # Large, powerful mounts
    GRIFFON = "griffon"     # Magical flying mounts
    WYVERN = "wyvern"       # Dragon-like flying mounts
    GIANT = "giant"         # Giant versions of normal animals
    AQUATIC = "aquatic"     # Water-based mounts
    EXOTIC = "exotic"       # Unusual or rare mounts
    MAGICAL = "magical"     # Inherently magical mounts

class TerrainAdaptation(Enum):
    """Terrain types mounts are adapted to"""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    ARCTIC = "arctic"
    SWAMP = "swamp"
    UNDERGROUND = "underground"
    URBAN = "urban"
    AQUATIC = "aquatic"
    AERIAL = "aerial"

class MountProperty(Enum):
    """Special properties that mounts can have"""
    TRAINED_WAR = "trained_war"      # Trained for combat
    TRAINED_RACING = "trained_racing"  # Trained for speed
    TRAINED_DRAFT = "trained_draft"    # Trained to pull vehicles
    ARMORED = "armored"           # Has armor protection
    FLYING = "flying"             # Can fly
    SWIMMING = "swimming"         # Can swim well
    CLIMBING = "climbing"         # Good at climbing
    INTELLIGENT = "intelligent"   # Higher than normal intelligence
    LOYAL = "loyal"              # Exceptionally loyal
    MAGICAL_ABILITY = "magical_ability"  # Has magical abilities
    TELEPATHIC = "telepathic"     # Can communicate telepathically
    BEAST_OF_BURDEN = "beast_of_burden"  # Can carry heavy loads
    SWIFT = "swift"              # Faster than typical
    ENDURING = "enduring"        # Has exceptional stamina
    MAGICAL_RESISTANCE = "magical_resistance"  # Resistant to magic

class Mounts(Equipment):
    """
    Class for handling mount equipment for transportation and companion animals.
    
    Extends the Equipment class with mount-specific functionality for creating,
    customizing, and analyzing mounts for character transportation and companionship.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the mounts manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional mount configuration
        self.terrain_mount_mapping = {
            "plains": ["horse", "pony", "elk"],
            "forest": ["elk", "wolf", "giant_boar"],
            "mountain": ["mule", "mountain_pony", "giant_goat"],
            "desert": ["camel", "giant_lizard", "axe_beak"],
            "arctic": ["polar_bear", "winter_wolf", "mammoth"],
            "swamp": ["giant_lizard", "giant_toad", "alligator"],
            "underground": ["giant_lizard", "giant_bat", "subterranean_lizard"],
            "urban": ["horse", "mule", "donkey"],
            "aquatic": ["giant_seahorse", "giant_octopus", "giant_turtle"],
            "aerial": ["griffon", "hippogriff", "pegasus"]
        }
        
        # Speed ranges by mount type
        self.typical_speed_ranges = {
            MountType.HORSE: (50, 60),
            MountType.PONY: (35, 45),
            MountType.CAMEL: (45, 55),
            MountType.ELEPHANT: (35, 45),
            MountType.GRIFFON: (60, 80),
            MountType.WYVERN: (70, 90),
            MountType.GIANT: (40, 50),
            MountType.AQUATIC: (30, 50),
            MountType.EXOTIC: (40, 60),
            MountType.MAGICAL: (60, 80)
        }
        
        # Carrying capacity multipliers by mount type
        self.carrying_capacity_multipliers = {
            MountType.HORSE: 2.0,
            MountType.PONY: 1.5,
            MountType.CAMEL: 2.2,
            MountType.ELEPHANT: 4.0,
            MountType.GRIFFON: 1.8,
            MountType.WYVERN: 2.0,
            MountType.GIANT: 3.0,
            MountType.AQUATIC: 1.5,
            MountType.EXOTIC: 2.0,
            MountType.MAGICAL: 2.5
        }
    
    def get_mounts_by_type(self, mount_type: Union[MountType, str]) -> List[Dict[str, Any]]:
        """
        Get mounts filtered by type.
        
        Args:
            mount_type: Type to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of mounts of the type
        """
        if isinstance(mount_type, str):
            # Try to convert string to enum
            try:
                mount_type = MountType(mount_type.lower())
            except ValueError:
                # If not a valid type, return empty list
                return []
        
        return [
            m for m in self.mounts.values() 
            if "mount_type" in m and m["mount_type"] == mount_type
        ]
    
    def get_mounts_by_property(self, property_name: Union[MountProperty, str]) -> List[Dict[str, Any]]:
        """
        Get mounts that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of mounts with the property
        """
        property_str = property_name.value if isinstance(property_name, MountProperty) else str(property_name).lower()
        
        return [
            m for m in self.mounts.values() 
            if "properties" in m and any(property_str in prop.lower() for prop in m["properties"])
        ]
    
    def get_mounts_by_terrain(self, terrain: Union[TerrainAdaptation, str]) -> List[Dict[str, Any]]:
        """
        Get mounts suitable for a specific terrain type.
        
        Args:
            terrain: Target terrain (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of mounts suitable for the terrain
        """
        terrain_str = terrain.value if isinstance(terrain, TerrainAdaptation) else str(terrain).lower()
        
        # Check if terrain is in our mapping
        if terrain_str not in self.terrain_mount_mapping:
            return []
        
        relevant_mounts = self.terrain_mount_mapping[terrain_str]
        
        # Find mounts that match the terrain
        matched_mounts = []
        
        for mount_id, mount_data in self.mounts.items():
            # Check if the mount is explicitly in the terrain list
            if mount_id in relevant_mounts:
                matched_mounts.append(mount_data)
                continue
            
            # Check if name contains terrain-specific mounts
            if any(rm in mount_data.get("name", "").lower() for rm in relevant_mounts):
                matched_mounts.append(mount_data)
                continue
                
            # Check adapted_terrains if present
            if "adapted_terrains" in mount_data:
                terrains = mount_data["adapted_terrains"]
                if isinstance(terrains, list) and any(t == terrain_str for t in terrains):
                    matched_mounts.append(mount_data)
        
        return matched_mounts
    
    def calculate_mount_carrying_capacity(self, 
                                       mount_id: str, 
                                       include_equipment: bool = True) -> Dict[str, Any]:
        """
        Calculate the carrying capacity of a mount.
        
        Args:
            mount_id: ID of the mount
            include_equipment: Whether to include equipment in capacity calculation
            
        Returns:
            Dict[str, Any]: Carrying capacity details
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return {"error": "Mount not found"}
        
        # Get mount's strength score
        strength = mount_data.get("strength", 14)  # Default to 14 if not specified
        
        # Base carrying capacity (like a character)
        base_capacity = strength * 15  # pounds
        
        # Apply mount type multiplier
        mount_type = mount_data.get("mount_type")
        multiplier = 1.0
        
        if isinstance(mount_type, MountType):
            multiplier = self.carrying_capacity_multipliers.get(mount_type, 1.0)
        elif isinstance(mount_type, str):
            try:
                enum_type = MountType(mount_type)
                multiplier = self.carrying_capacity_multipliers.get(enum_type, 1.0)
            except ValueError:
                pass
        
        # Check if the mount has the beast of burden property
        if "properties" in mount_data:
            if any("beast_of_burden" in p.lower() for p in mount_data["properties"]):
                multiplier *= 1.5
        
        total_capacity = base_capacity * multiplier
        
        # Calculate equipment weight if included
        equipment_weight = 0
        if include_equipment and "equipment" in mount_data:
            for item in mount_data["equipment"]:
                item_id = item.get("id")
                quantity = item.get("quantity", 1)
                
                item_data = self._find_item_by_id(item_id)
                if item_data and "weight" in item_data:
                    equipment_weight += item_data["weight"] * quantity
        
        # Calculate remaining capacity
        remaining_capacity = total_capacity - equipment_weight
        
        # Determine encumbrance thresholds
        encumbered_threshold = total_capacity / 3
        heavily_encumbered_threshold = total_capacity * 2 / 3
        
        return {
            "mount_name": mount_data.get("name"),
            "strength_score": strength,
            "base_capacity": base_capacity,
            "mount_type_multiplier": multiplier,
            "total_capacity": total_capacity,
            "equipment_weight": equipment_weight,
            "remaining_capacity": remaining_capacity,
            "encumbered_threshold": encumbered_threshold,
            "heavily_encumbered_threshold": heavily_encumbered_threshold
        }
    
    def calculate_mount_travel_speed(self, 
                                  mount_id: str, 
                                  encumbrance_level: str = "normal",
                                  terrain_difficulty: str = "normal",
                                  travel_pace: str = "normal") -> Dict[str, Any]:
        """
        Calculate travel speed for a mount in different conditions.
        
        Args:
            mount_id: ID of the mount
            encumbrance_level: Level of encumbrance (light, normal, heavy)
            terrain_difficulty: Difficulty of terrain (easy, normal, difficult)
            travel_pace: Pace of travel (fast, normal, slow)
            
        Returns:
            Dict[str, Any]: Travel speed calculations
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return {"error": "Mount not found"}
        
        # Get base speed
        base_speed = mount_data.get("speed", 50)  # Default to 50 feet per round
        
        # Convert combat speed (feet per round) to travel speed (miles per hour)
        # Approximately: combat_speed * 0.1 = mph
        base_mph = base_speed * 0.1
        
        # Apply encumbrance modifications
        encumbrance_multipliers = {
            "light": 1.0,
            "normal": 0.9,
            "heavy": 0.7
        }
        
        encumbrance_mult = encumbrance_multipliers.get(encumbrance_level.lower(), 1.0)
        
        # Apply terrain difficulty modifications
        terrain_multipliers = {
            "easy": 1.2,
            "normal": 1.0,
            "difficult": 0.7,
            "very_difficult": 0.5
        }
        
        terrain_mult = terrain_multipliers.get(terrain_difficulty.lower(), 1.0)
        
        # Apply travel pace modifications
        pace_multipliers = {
            "fast": 1.3,
            "normal": 1.0,
            "slow": 0.7
        }
        
        pace_mult = pace_multipliers.get(travel_pace.lower(), 1.0)
        
        # Calculate final travel speed
        adjusted_mph = base_mph * encumbrance_mult * terrain_mult * pace_mult
        miles_per_day = adjusted_mph * 8  # Assuming 8 hours of travel per day
        
        # Check for special terrain adaptations
        terrain_adapted = False
        terrain_bonus = 1.0
        
        if "adapted_terrains" in mount_data and terrain_difficulty != "normal":
            terrains = mount_data["adapted_terrains"]
            if terrain_difficulty == "difficult" and any(t in ["mountain", "desert", "arctic", "swamp"] for t in terrains):
                terrain_adapted = True
                terrain_bonus = 1.3
                miles_per_day *= terrain_bonus
            elif terrain_difficulty == "very_difficult" and any(t in ["mountain", "desert", "arctic", "swamp", "underground"] for t in terrains):
                terrain_adapted = True
                terrain_bonus = 1.5
                miles_per_day *= terrain_bonus
        
        return {
            "mount_name": mount_data.get("name"),
            "base_speed_feet": base_speed,
            "base_speed_mph": round(base_mph, 2),
            "encumbrance_factor": encumbrance_mult,
            "terrain_factor": terrain_mult,
            "pace_factor": pace_mult,
            "terrain_adaptation_bonus": terrain_bonus if terrain_adapted else "None",
            "adjusted_speed_mph": round(adjusted_mph, 2),
            "miles_per_day": round(miles_per_day, 1),
            "travel_conditions": f"{encumbrance_level} encumbrance, {terrain_difficulty} terrain, {travel_pace} pace"
        }
    
    def create_custom_mount(self, 
                         name: str,
                         mount_type: MountType,
                         speed: int = 50,
                         strength: int = 16,
                         properties: List[str] = None,
                         adapted_terrains: List[str] = None,
                         description: str = None,
                         cost: Dict[str, int] = None,
                         is_magical: bool = False,
                         rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom mount with specified attributes.
        
        Args:
            name: Name of the mount
            mount_type: Type of mount
            speed: Speed in feet per round
            strength: Strength score (affects carrying capacity)
            properties: List of mount properties
            adapted_terrains: List of terrains the mount is adapted to
            description: Description of the mount
            cost: Cost in currency values
            is_magical: Whether the mount is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created mount data
        """
        # Generate a description if none provided
        if description is None:
            description = f"A {mount_type.value} mount suitable for transportation and adventuring."
        
        # Set default properties if none provided
        if properties is None:
            if mount_type == MountType.HORSE:
                properties = [MountProperty.SWIFT.value]
            elif mount_type == MountType.ELEPHANT:
                properties = [MountProperty.BEAST_OF_BURDEN.value]
            elif mount_type == MountType.GRIFFON:
                properties = [MountProperty.FLYING.value]
            else:
                properties = []
                
        # Set default adapted terrains if none provided
        if adapted_terrains is None:
            if mount_type == MountType.HORSE:
                adapted_terrains = [TerrainAdaptation.PLAINS.value]
            elif mount_type == MountType.CAMEL:
                adapted_terrains = [TerrainAdaptation.DESERT.value]
            elif mount_type == MountType.ELEPHANT:
                adapted_terrains = [TerrainAdaptation.PLAINS.value, TerrainAdaptation.FOREST.value]
            elif mount_type == MountType.GRIFFON:
                adapted_terrains = [TerrainAdaptation.MOUNTAIN.value, TerrainAdaptation.AERIAL.value]
            else:
                adapted_terrains = [TerrainAdaptation.PLAINS.value]
        
        # Set default cost if none provided
        if cost is None:
            if mount_type == MountType.HORSE:
                cost = {"gp": 75}
            elif mount_type == MountType.PONY:
                cost = {"gp": 30}
            elif mount_type == MountType.CAMEL:
                cost = {"gp": 50}
            elif mount_type == MountType.ELEPHANT:
                cost = {"gp": 200}
            elif mount_type == MountType.GRIFFON or mount_type == MountType.WYVERN:
                cost = {"gp": 3000}
            elif mount_type == MountType.MAGICAL:
                cost = {"gp": 5000}
            else:
                cost = {"gp": 100}
        
        # Create the mount data
        mount_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": EquipmentCategory.MOUNT,
            "mount_type": mount_type,
            "speed": speed,
            "strength": strength,
            "properties": properties,
            "adapted_terrains": adapted_terrains,
            "cost": cost,
            "description": description,
            "is_magical": is_magical,
            "equipment": []  # Empty equipment list by default
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            mount_data["rarity"] = rarity
        
        # Add to mounts collection
        self.mounts[mount_data["id"]] = mount_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[mount_data["id"]] = mount_data
        
        return mount_data
    
    def enhance_mount_with_llm(self, 
                            mount_id: str, 
                            enhancement_type: str = "personality",
                            character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance mount with LLM-generated content.
        
        Args:
            mount_id: ID of the mount to enhance
            enhancement_type: Type of enhancement (personality, narrative, companion)
            character_data: Optional character data for contextual enhancements
            
        Returns:
            Dict[str, Any]: Enhanced mount data
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return {"error": "Mount not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_mount = mount_data.copy()
        
        if enhancement_type.lower() == "personality":
            # Generate mount personality
            prompt = self.llm_advisor._create_prompt(
                "create mount personality",
                f"Mount: {mount_data.get('name')}\n"
                f"Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
                f"Description: {mount_data.get('description', '')}\n\n"
                "Create a detailed personality profile for this mount, including temperament, "
                "notable behaviors, likes and dislikes, and how it typically interacts with its rider. "
                "The description should help players roleplay interactions with this mount."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_mount["personality"] = clean_response.strip()
            except Exception as e:
                print(f"Error generating mount personality: {e}")
                enhanced_mount["personality"] = "A mount with a typical temperament for its kind."
                
        elif enhancement_type.lower() == "narrative":
            # Generate narrative description
            if character_data:
                character_context = f"Character: {character_data.get('name')}, "
                character_context += f"a {character_data.get('race')} {character_data.get('class')}"
            else:
                character_context = "An adventurer"
                
            prompt = self.llm_advisor._create_prompt(
                "generate mount backstory",
                f"Mount: {mount_data.get('name')}\n"
                f"Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
                f"Description: {mount_data.get('description', '')}\n"
                f"Owner: {character_context}\n\n"
                "Create a rich backstory for how this mount was acquired by its owner, "
                "its history before joining the character, and notable experiences they have shared. "
                "The narrative should add depth to the mount-rider relationship."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_mount["narrative"] = response
            except Exception as e:
                print(f"Error generating mount narrative: {e}")
                enhanced_mount["narrative"] = f"A {mount_data.get('name')} with a typical background."
            
        elif enhancement_type.lower() == "companion":
            # Generate companion features
            prompt = self.llm_advisor._create_prompt(
                "develop mount as companion",
                f"Mount: {mount_data.get('name')}\n"
                f"Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
                f"Properties: {', '.join(mount_data.get('properties', []))}\n\n"
                "Develop this mount as a companion character rather than just transportation. "
                "Include special abilities it might develop with training, ways it might help in "
                "different adventuring situations, and how the bond between mount and rider "
                "might grow over time. Focus on narrative possibilities that don't break game balance."
                "Return as JSON with 'special_abilities', 'adventuring_uses', 'bond_development', and 'roleplay_opportunities' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                companion_data = self.llm_advisor._extract_json(response)
                
                if companion_data:
                    enhanced_mount["companion_features"] = companion_data
                else:
                    enhanced_mount["companion_features"] = {
                        "special_abilities": ["Basic training", "Loyalty to rider"],
                        "adventuring_uses": ["Transportation", "Carrying equipment"]
                    }
            except Exception as e:
                print(f"Error generating companion features: {e}")
                enhanced_mount["companion_features"] = {
                    "special_abilities": ["Basic training", "Loyalty to rider"],
                    "adventuring_uses": ["Transportation", "Carrying equipment"]
                }
            
        return enhanced_mount
    
    def suggest_mount_equipment(self, mount_id: str) -> Dict[str, Any]:
        """
        Suggest appropriate equipment for a mount.
        
        Args:
            mount_id: ID of the mount
            
        Returns:
            Dict[str, Any]: Suggested equipment
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return {"error": "Mount not found"}
            
        # Use LLM to suggest equipment based on mount type
        prompt = self.llm_advisor._create_prompt(
            "suggest mount equipment",
            f"Mount: {mount_data.get('name')}\n"
            f"Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
            f"Properties: {', '.join(mount_data.get('properties', []))}\n"
            f"Adapted Terrains: {', '.join(mount_data.get('adapted_terrains', []))}\n\n"
            "Suggest appropriate equipment for this mount, including saddles, barding, bags, "
            "and other accessories. For each item, explain its purpose, benefits, and approximate cost. "
            "Return as JSON with 'essential_equipment', 'recommended_accessories', 'specialty_gear', and 'total_cost_estimate' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            equipment_suggestions = self.llm_advisor._extract_json(response)
            
            if equipment_suggestions:
                return {
                    "mount_name": mount_data.get("name"),
                    "equipment_suggestions": equipment_suggestions
                }
        except Exception as e:
            print(f"Error suggesting mount equipment: {e}")
        
        # Fallback response
        mount_type = mount_data.get("mount_type")
        
        return {
            "mount_name": mount_data.get("name"),
            "equipment_suggestions": {
                "essential_equipment": [
                    {"name": "Saddle", "purpose": "For riding", "cost": "10 gp"},
                    {"name": "Bit and bridle", "purpose": "For control", "cost": "2 gp"},
                    {"name": "Saddlebags", "purpose": "For storage", "cost": "4 gp"}
                ],
                "recommended_accessories": [
                    {"name": "Feed bag", "purpose": "For keeping mount fed", "cost": "5 sp"}
                ],
                "specialty_gear": [],
                "total_cost_estimate": "17 gp"
            }
        }
    
    def analyze_mount_character_compatibility(self, 
                                          mount_id: str, 
                                          character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compatibility between a mount and character.
        
        Args:
            mount_id: ID of the mount
            character_data: Character data
            
        Returns:
            Dict[str, Any]: Compatibility analysis
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return {"error": "Mount not found"}
            
        # Extract relevant character information
        size = character_data.get("size", "medium")
        strength = character_data.get("ability_scores", {}).get("strength", 10)
        dexterity = character_data.get("ability_scores", {}).get("dexterity", 10)
        race = character_data.get("race", "")
        background = character_data.get("background", "")
        classes = character_data.get("class", {}).get("name", "")
        proficiencies = character_data.get("proficiencies", {})
        
        # Check if character has animal handling proficiency
        has_animal_handling = False
        if "skills" in proficiencies:
            has_animal_handling = "animal handling" in [s.lower() for s in proficiencies["skills"]]
        
        # Check size compatibility
        size_compatibility = self._check_size_compatibility(mount_data, size)
        
        # Use LLM for more detailed compatibility analysis
        prompt = self.llm_advisor._create_prompt(
            "analyze mount-character compatibility",
            f"Mount: {mount_data.get('name')}\n"
            f"Mount Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
            f"Character: {race} {classes}\n"
            f"Character Size: {size}\n"
            f"Strength: {strength}\n"
            f"Dexterity: {dexterity}\n"
            f"Has Animal Handling: {has_animal_handling}\n"
            f"Background: {background}\n\n"
            "Analyze the compatibility between this character and mount from both mechanical and thematic perspectives. "
            "Consider size appropriateness, skill synergies, cultural factors, and narrative fit. "
            "Return as JSON with 'compatibility_rating', 'mechanical_synergies', 'cultural_fit', 'challenges', and 'recommendations' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            compatibility = self.llm_advisor._extract_json(response)
            
            if compatibility:
                compatibility["mount_name"] = mount_data.get("name")
                compatibility["size_compatibility"] = size_compatibility
                return compatibility
        except Exception as e:
            print(f"Error analyzing mount compatibility: {e}")
        
        # Fallback response
        return {
            "mount_name": mount_data.get("name"),
            "compatibility_rating": "Medium",
            "size_compatibility": size_compatibility,
            "mechanical_synergies": ["Basic transportation"],
            "challenges": ["No special synergies noted"],
            "recommendations": ["Consider your character's needs when selecting a mount"]
        }
    
    def generate_mount_appearance(self, mount_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of a mount.
        
        Args:
            mount_id: ID of the mount
            style: Optional style direction (e.g., "majestic", "battle-worn", "exotic")
            
        Returns:
            str: Detailed appearance description
        """
        mount_data = self._find_item_by_id(mount_id)
        if not mount_data:
            return "Mount not found"
        
        context = f"Mount: {mount_data.get('name')}\n"
        context += f"Type: {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'unknown'}\n"
        context += f"Properties: {', '.join(mount_data.get('properties', []))}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this mount",
            context + "\n"
            "Create a vivid, detailed description of this mount's physical appearance. "
            "Include details about its coloration, size, distinctive features, mannerisms, "
            "movements, sounds, and overall aesthetic. The description should help a player "
            "visualize their mount and feel a connection to it as more than just a mode of transportation."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating mount appearance: {e}")
            
        # Fallback description
        return f"A typical {mount_data.get('mount_type').value if isinstance(mount_data.get('mount_type'), MountType) else 'mount'} with no particularly distinguishing features."
    
    # === HELPER METHODS ===
    
    def _check_size_compatibility(self, mount_data: Dict[str, Any], character_size: str) -> str:
        """Check if mount and character sizes are compatible."""
        character_size = character_size.lower()
        mount_type = mount_data.get("mount_type")
        
        # Size category estimates
        mount_size_categories = {
            MountType.PONY: "medium",
            MountType.HORSE: "large",
            MountType.CAMEL: "large",
            MountType.ELEPHANT: "huge",
            MountType.GRIFFON: "large",
            MountType.WYVERN: "large",
            MountType.GIANT: "huge",
            MountType.AQUATIC: "large",
            MountType.EXOTIC: "large",
            MountType.MAGICAL: "large"
        }
        
        # Override with specific mount size if available
        mount_size = mount_data.get("size", None)
        if mount_size is None and isinstance(mount_type, MountType):
            mount_size = mount_size_categories.get(mount_type, "large")
        elif mount_size is None:
            mount_size = "large"  # Default
        
        # Compatibility rules:
        # Tiny creatures can't usually ride mounts
        if character_size == "tiny":
            return "incompatible"
            
        # Small creatures can ride medium+ mounts
        elif character_size == "small":
            if mount_size in ["medium", "large", "huge", "gargantuan"]:
                return "compatible"
            else:
                return "incompatible"
                
        # Medium creatures can ride large+ mounts
        elif character_size == "medium":
            if mount_size in ["large", "huge", "gargantuan"]:
                return "compatible"
            else:
                return "incompatible"
                
        # Large creatures can ride huge+ mounts
        elif character_size == "large":
            if mount_size in ["huge", "gargantuan"]:
                return "compatible"
            else:
                return "incompatible"
                
        # Huge creatures can only ride gargantuan mounts
        elif character_size == "huge":
            if mount_size == "gargantuan":
                return "compatible"
            else:
                return "incompatible"
                
        # Gargantuan creatures typically don't ride mounts
        else:
            return "incompatible"