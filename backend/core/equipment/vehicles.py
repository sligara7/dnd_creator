# vehicles.py
# Description: Handles vehicles for land, water and air transportation

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class VehicleType(Enum):
    """Types of vehicles"""
    LAND = "land"           # Carts, wagons, carriages, etc.
    WATER = "water"         # Boats, ships, etc.
    AIR = "air"             # Airships, flying carpets, etc.
    HYBRID = "hybrid"       # Vehicles that can travel on multiple terrains
    MAGICAL = "magical"     # Vehicles powered by magic
    MECHANICAL = "mechanical"  # Advanced mechanical vehicles
    SIEGE = "siege"         # War machines and siege engines
    SUBMERSIBLE = "submersible"  # Underwater vehicles

class VehicleSize(Enum):
    """Size categories for vehicles"""
    TINY = "tiny"           # Personal transport devices
    SMALL = "small"         # Small carts, rowboats
    MEDIUM = "medium"       # Wagons, small sailing boats
    LARGE = "large"         # Carriages, sailing ships
    HUGE = "huge"           # War galleons, large merchant ships
    GARGANTUAN = "gargantuan"  # Massive ships, airships

class VehicleProperty(Enum):
    """Special properties that vehicles can have"""
    FAST = "fast"             # Faster than typical for its type
    STURDY = "sturdy"         # More durable than normal
    SPACIOUS = "spacious"     # More cargo/passenger capacity
    MANEUVERABLE = "maneuverable"  # Easier to handle/steer
    ARMED = "armed"           # Has weapons or defenses
    AMPHIBIOUS = "amphibious"   # Can travel on land and water
    ARMORED = "armored"       # Has protective plating/reinforcement
    MAGICAL_PROPULSION = "magical_propulsion"  # Powered by magic
    CONCEALED = "concealed"   # Has hidden compartments/features
    LUXURY = "luxury"         # Opulent features and comforts
    REPAIRABLE = "repairable"   # Easy to repair in the field
    COLLAPSIBLE = "collapsible"  # Can be disassembled for transport
    ADAPTABLE = "adaptable"   # Can be modified for different terrain
    SELF_PROPELLED = "self_propelled"  # Requires no animal power

class Vehicles(Equipment):
    """
    Class for handling vehicle equipment for transportation over land, water and air.
    
    Extends the Equipment class with vehicle-specific functionality for creating,
    customizing, and analyzing vehicles for character transportation and travel.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the vehicles manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional vehicle configuration
        self.terrain_vehicle_mapping = {
            "plains": ["cart", "wagon", "carriage"],
            "forest": ["sled", "light_cart"],
            "mountain": ["mountain_sled", "mule_cart"],
            "desert": ["sand_skiff", "desert_wagon"],
            "arctic": ["ice_sledge", "snow_runner"],
            "swamp": ["reed_boat", "mud_skimmer"],
            "water": ["rowboat", "keelboat", "sailing_ship", "galley"],
            "underwater": ["submersible", "diving_bell"],
            "air": ["airship", "flying_carpet", "flying_vessel"],
            "urban": ["carriage", "palanquin", "rickshaw"]
        }
        
        # Speed ranges by vehicle type
        self.typical_speed_ranges = {
            VehicleType.LAND: (2, 5),  # mph
            VehicleType.WATER: (1, 10),  # mph
            VehicleType.AIR: (8, 20),  # mph
            VehicleType.HYBRID: (3, 8),  # mph
            VehicleType.MAGICAL: (5, 15),  # mph
            VehicleType.MECHANICAL: (4, 12),  # mph
            VehicleType.SIEGE: (1, 3),  # mph
            VehicleType.SUBMERSIBLE: (1, 5)  # mph
        }
        
        # Crew requirements by vehicle size
        self.typical_crew_requirements = {
            VehicleSize.TINY: 1,
            VehicleSize.SMALL: 1,
            VehicleSize.MEDIUM: 2,
            VehicleSize.LARGE: 4,
            VehicleSize.HUGE: 10,
            VehicleSize.GARGANTUAN: 20
        }
    
    def get_vehicles_by_type(self, vehicle_type: Union[VehicleType, str]) -> List[Dict[str, Any]]:
        """
        Get vehicles filtered by type.
        
        Args:
            vehicle_type: Type to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of vehicles of the type
        """
        if isinstance(vehicle_type, str):
            # Try to convert string to enum
            try:
                vehicle_type = VehicleType(vehicle_type.lower())
            except ValueError:
                # If not a valid type, return empty list
                return []
        
        return [
            v for v in self.vehicles.values() 
            if "vehicle_type" in v and v["vehicle_type"] == vehicle_type
        ]
    
    def get_vehicles_by_size(self, vehicle_size: Union[VehicleSize, str]) -> List[Dict[str, Any]]:
        """
        Get vehicles filtered by size.
        
        Args:
            vehicle_size: Size to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of vehicles of the size
        """
        if isinstance(vehicle_size, str):
            # Try to convert string to enum
            try:
                vehicle_size = VehicleSize(vehicle_size.lower())
            except ValueError:
                # If not a valid size, return empty list
                return []
        
        return [
            v for v in self.vehicles.values() 
            if "vehicle_size" in v and v["vehicle_size"] == vehicle_size
        ]
    
    def get_vehicles_by_property(self, property_name: Union[VehicleProperty, str]) -> List[Dict[str, Any]]:
        """
        Get vehicles that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of vehicles with the property
        """
        property_str = property_name.value if isinstance(property_name, VehicleProperty) else str(property_name).lower()
        
        return [
            v for v in self.vehicles.values() 
            if "properties" in v and any(property_str in prop.lower() for prop in v["properties"])
        ]
    
    def get_vehicles_by_terrain(self, terrain: str) -> List[Dict[str, Any]]:
        """
        Get vehicles suitable for a specific terrain type.
        
        Args:
            terrain: Target terrain (plains, forest, water, etc.)
            
        Returns:
            List[Dict[str, Any]]: List of vehicles suitable for the terrain
        """
        terrain = terrain.lower()
        
        # Check if terrain is in our mapping
        if terrain not in self.terrain_vehicle_mapping:
            return []
        
        relevant_vehicles = self.terrain_vehicle_mapping[terrain]
        
        # Find vehicles that match the terrain
        matched_vehicles = []
        
        for vehicle_id, vehicle_data in self.vehicles.items():
            # Check if the vehicle is explicitly in the terrain list
            if vehicle_id in relevant_vehicles:
                matched_vehicles.append(vehicle_data)
                continue
            
            # Check if name contains terrain-specific vehicles
            if any(rv in vehicle_data.get("name", "").lower() for rv in relevant_vehicles):
                matched_vehicles.append(vehicle_data)
                continue
                
            # Check suitable_terrains if present
            if "suitable_terrains" in vehicle_data:
                terrains = vehicle_data["suitable_terrains"]
                if isinstance(terrains, list) and any(t == terrain for t in terrains):
                    matched_vehicles.append(vehicle_data)
        
        return matched_vehicles
    
    def calculate_vehicle_travel_speed(self, 
                                    vehicle_id: str, 
                                    terrain_difficulty: str = "normal",
                                    weather_conditions: str = "normal",
                                    cargo_load: str = "normal") -> Dict[str, Any]:
        """
        Calculate travel speed for a vehicle in different conditions.
        
        Args:
            vehicle_id: ID of the vehicle
            terrain_difficulty: Difficulty of terrain (easy, normal, difficult)
            weather_conditions: Weather impact (favorable, normal, adverse)
            cargo_load: Level of cargo load (light, normal, heavy)
            
        Returns:
            Dict[str, Any]: Travel speed calculations
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
        
        # Get base speed
        base_speed = vehicle_data.get("speed", 3)  # Default to 3 mph if not specified
        
        # Apply terrain difficulty modifications
        terrain_multipliers = {
            "easy": 1.2,
            "normal": 1.0,
            "difficult": 0.7,
            "very_difficult": 0.5
        }
        
        terrain_mult = terrain_multipliers.get(terrain_difficulty.lower(), 1.0)
        
        # Apply weather condition modifications
        weather_multipliers = {
            "favorable": 1.3,
            "normal": 1.0,
            "adverse": 0.7,
            "severe": 0.4
        }
        
        weather_mult = weather_multipliers.get(weather_conditions.lower(), 1.0)
        
        # Apply cargo load modifications
        cargo_multipliers = {
            "light": 1.1,
            "normal": 1.0,
            "heavy": 0.8,
            "overloaded": 0.6
        }
        
        cargo_mult = cargo_multipliers.get(cargo_load.lower(), 1.0)
        
        # Check if vehicle has special properties that affect speed
        properties = vehicle_data.get("properties", [])
        property_modifier = 1.0
        
        if any("fast" in p.lower() for p in properties):
            property_modifier *= 1.3
            
        if any("maneuverable" in p.lower() for p in properties):
            # Maneuverability helps in difficult terrain
            if terrain_difficulty.lower() in ["difficult", "very_difficult"]:
                property_modifier *= 1.1
                
        if any("magical_propulsion" in p.lower() for p in properties):
            # Magical propulsion is less affected by weather
            if weather_conditions.lower() in ["adverse", "severe"]:
                weather_mult = min(0.8, weather_mult * 1.3)
        
        # Calculate final travel speed
        adjusted_speed = base_speed * terrain_mult * weather_mult * cargo_mult * property_modifier
        
        # Calculate daily travel distance (8 hours of travel)
        miles_per_day = adjusted_speed * 8
        
        # Apply vehicle type specific adjustments
        vehicle_type = vehicle_data.get("vehicle_type")
        
        if isinstance(vehicle_type, VehicleType):
            if vehicle_type == VehicleType.WATER and weather_conditions.lower() == "favorable":
                # Water vehicles benefit more from favorable winds
                miles_per_day *= 1.2
            elif vehicle_type == VehicleType.AIR and weather_conditions.lower() == "adverse":
                # Air vehicles suffer more from adverse weather
                miles_per_day *= 0.8
        
        return {
            "vehicle_name": vehicle_data.get("name"),
            "base_speed_mph": base_speed,
            "terrain_factor": terrain_mult,
            "weather_factor": weather_mult,
            "cargo_factor": cargo_mult,
            "property_modifier": property_modifier,
            "adjusted_speed_mph": round(adjusted_speed, 2),
            "miles_per_day": round(miles_per_day, 1),
            "travel_conditions": f"{terrain_difficulty} terrain, {weather_conditions} weather, {cargo_load} cargo load"
        }
    
    def calculate_vehicle_capacity(self, 
                                vehicle_id: str,
                                include_creatures: bool = True) -> Dict[str, Any]:
        """
        Calculate the carrying capacity of a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            include_creatures: Whether to include crew and passenger capacity
            
        Returns:
            Dict[str, Any]: Carrying capacity details
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
        
        # Get vehicle size for base capacity
        vehicle_size = vehicle_data.get("vehicle_size")
        
        # Base capacity in pounds
        base_capacity = 0
        
        if isinstance(vehicle_size, VehicleSize):
            if vehicle_size == VehicleSize.TINY:
                base_capacity = 300
            elif vehicle_size == VehicleSize.SMALL:
                base_capacity = 1000
            elif vehicle_size == VehicleSize.MEDIUM:
                base_capacity = 4000
            elif vehicle_size == VehicleSize.LARGE:
                base_capacity = 10000
            elif vehicle_size == VehicleSize.HUGE:
                base_capacity = 25000
            elif vehicle_size == VehicleSize.GARGANTUAN:
                base_capacity = 50000
        else:
            # Default to medium if size is not specified
            base_capacity = 4000
        
        # Check if the vehicle has capacity-enhancing properties
        properties = vehicle_data.get("properties", [])
        capacity_modifier = 1.0
        
        if any("spacious" in p.lower() for p in properties):
            capacity_modifier *= 1.5
            
        if any("sturdy" in p.lower() for p in properties):
            capacity_modifier *= 1.2
        
        total_capacity = base_capacity * capacity_modifier
        
        # Calculate creature capacity if requested
        crew_capacity = vehicle_data.get("crew_required", self._get_default_crew_requirement(vehicle_size))
        passenger_capacity = vehicle_data.get("passenger_capacity", self._get_default_passenger_capacity(vehicle_size))
        
        # Calculate cargo capacity (total capacity minus space for creatures)
        creature_weight = 0
        if include_creatures:
            # Assume average weight per creature (200 pounds including gear)
            creature_weight = (crew_capacity + passenger_capacity) * 200
        
        cargo_capacity = total_capacity - creature_weight
        
        return {
            "vehicle_name": vehicle_data.get("name"),
            "vehicle_size": str(vehicle_size.value if isinstance(vehicle_size, VehicleSize) else "unknown"),
            "base_capacity_pounds": base_capacity,
            "capacity_modifier": capacity_modifier,
            "total_capacity_pounds": total_capacity,
            "crew_capacity": crew_capacity,
            "passenger_capacity": passenger_capacity,
            "cargo_capacity_pounds": max(0, cargo_capacity),
            "cargo_capacity_tons": max(0, cargo_capacity / 2000)  # Convert to tons
        }
    
    def create_custom_vehicle(self, 
                           name: str,
                           vehicle_type: VehicleType,
                           vehicle_size: VehicleSize,
                           speed: float = None,
                           properties: List[str] = None,
                           suitable_terrains: List[str] = None,
                           crew_required: int = None,
                           passenger_capacity: int = None,
                           description: str = None,
                           cost: Dict[str, int] = None,
                           is_magical: bool = False,
                           rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom vehicle with specified attributes.
        
        Args:
            name: Name of the vehicle
            vehicle_type: Type of vehicle
            vehicle_size: Size of vehicle
            speed: Speed in miles per hour
            properties: List of vehicle properties
            suitable_terrains: List of terrains the vehicle can navigate
            crew_required: Number of crew members required
            passenger_capacity: Number of passengers (beyond crew)
            description: Description of the vehicle
            cost: Cost in currency values
            is_magical: Whether the vehicle is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created vehicle data
        """
        # Set default speed if none provided
        if speed is None:
            speed_range = self.typical_speed_ranges.get(vehicle_type, (3, 6))
            speed = (speed_range[0] + speed_range[1]) / 2
        
        # Set default crew required if none provided
        if crew_required is None:
            crew_required = self._get_default_crew_requirement(vehicle_size)
        
        # Set default passenger capacity if none provided
        if passenger_capacity is None:
            passenger_capacity = self._get_default_passenger_capacity(vehicle_size)
        
        # Set default properties if none provided
        if properties is None:
            if vehicle_type == VehicleType.LAND:
                properties = []
            elif vehicle_type == VehicleType.WATER:
                properties = []
            elif vehicle_type == VehicleType.AIR:
                properties = [VehicleProperty.MAGICAL_PROPULSION.value]
            elif vehicle_type == VehicleType.MAGICAL:
                properties = [VehicleProperty.MAGICAL_PROPULSION.value]
            else:
                properties = []
                
        # Set default suitable terrains if none provided
        if suitable_terrains is None:
            if vehicle_type == VehicleType.LAND:
                suitable_terrains = ["plains", "urban"]
            elif vehicle_type == VehicleType.WATER:
                suitable_terrains = ["water"]
            elif vehicle_type == VehicleType.AIR:
                suitable_terrains = ["air"]
            elif vehicle_type == VehicleType.SUBMERSIBLE:
                suitable_terrains = ["underwater"]
            elif vehicle_type == VehicleType.HYBRID:
                suitable_terrains = ["land", "water"]
            else:
                suitable_terrains = ["plains"]
        
        # Generate a description if none provided
        if description is None:
            description = f"A {vehicle_size.value} {vehicle_type.value} vehicle designed for transportation."
        
        # Set default cost based on size and type
        if cost is None:
            base_cost = 0
            if vehicle_size == VehicleSize.TINY:
                base_cost = 50
            elif vehicle_size == VehicleSize.SMALL:
                base_cost = 100
            elif vehicle_size == VehicleSize.MEDIUM:
                base_cost = 250
            elif vehicle_size == VehicleSize.LARGE:
                base_cost = 5000
            elif vehicle_size == VehicleSize.HUGE:
                base_cost = 10000
            elif vehicle_size == VehicleSize.GARGANTUAN:
                base_cost = 25000
                
            # Adjust for vehicle type
            type_multiplier = 1.0
            if vehicle_type == VehicleType.AIR:
                type_multiplier = 3.0
            elif vehicle_type == VehicleType.MAGICAL:
                type_multiplier = 4.0
            elif vehicle_type == VehicleType.SUBMERSIBLE:
                type_multiplier = 2.5
                
            cost = {"gp": int(base_cost * type_multiplier)}
        
        # Create the vehicle data
        vehicle_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": EquipmentCategory.VEHICLE,
            "vehicle_type": vehicle_type,
            "vehicle_size": vehicle_size,
            "speed": speed,
            "properties": properties,
            "suitable_terrains": suitable_terrains,
            "crew_required": crew_required,
            "passenger_capacity": passenger_capacity,
            "cost": cost,
            "description": description,
            "is_magical": is_magical
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            vehicle_data["rarity"] = rarity
        
        # Add to vehicles collection
        self.vehicles[vehicle_data["id"]] = vehicle_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[vehicle_data["id"]] = vehicle_data
        
        return vehicle_data
    
    def enhance_vehicle_with_llm(self, 
                              vehicle_id: str, 
                              enhancement_type: str = "description",
                              adventure_context: str = None) -> Dict[str, Any]:
        """
        Enhance vehicle with LLM-generated content.
        
        Args:
            vehicle_id: ID of the vehicle to enhance
            enhancement_type: Type of enhancement (description, travel, history)
            adventure_context: Optional adventure context
            
        Returns:
            Dict[str, Any]: Enhanced vehicle data
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_vehicle = vehicle_data.copy()
        
        if enhancement_type.lower() == "description":
            # Generate detailed vehicle description
            prompt = self.llm_advisor._create_prompt(
                "create detailed vehicle description",
                f"Vehicle: {vehicle_data.get('name')}\n"
                f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
                f"Size: {vehicle_data.get('vehicle_size').value if isinstance(vehicle_data.get('vehicle_size'), VehicleSize) else 'unknown'}\n"
                f"Properties: {', '.join(vehicle_data.get('properties', []))}\n\n"
                "Create a detailed description of this vehicle, including its appearance, "
                "construction, notable features, and general atmosphere. The description should "
                "help players visualize the vehicle and understand its role in the world."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_vehicle["detailed_description"] = clean_response.strip()
            except Exception as e:
                print(f"Error generating vehicle description: {e}")
                enhanced_vehicle["detailed_description"] = "A standard vehicle of its type."
                
        elif enhancement_type.lower() == "travel":
            # Generate travel narrative and complications
            context = ""
            if adventure_context:
                context = f"Adventure Context: {adventure_context}\n\n"
                
            prompt = self.llm_advisor._create_prompt(
                "generate travel narrative and complications",
                f"Vehicle: {vehicle_data.get('name')}\n"
                f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
                f"{context}"
                "Create a narrative description of traveling with this vehicle, including "
                "the general experience, potential complications that might arise, and "
                "interesting encounters or events that could happen during travel. "
                "Return as JSON with 'travel_experience', 'common_complications', 'rare_complications', and 'notable_encounters' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                travel_data = self.llm_advisor._extract_json(response)
                
                if travel_data:
                    enhanced_vehicle["travel_narrative"] = travel_data
                else:
                    enhanced_vehicle["travel_narrative"] = {
                        "travel_experience": "Standard travel for this type of vehicle.",
                        "common_complications": ["Routine maintenance required", "Weather delays"],
                        "rare_complications": ["Mechanical failure"],
                        "notable_encounters": ["Passing travelers"]
                    }
            except Exception as e:
                print(f"Error generating travel narrative: {e}")
                enhanced_vehicle["travel_narrative"] = {
                    "travel_experience": "Standard travel for this type of vehicle.",
                    "common_complications": ["Routine maintenance required", "Weather delays"],
                    "rare_complications": ["Mechanical failure"],
                    "notable_encounters": ["Passing travelers"]
                }
            
        elif enhancement_type.lower() == "history":
            # Generate vehicle history
            prompt = self.llm_advisor._create_prompt(
                "create vehicle history",
                f"Vehicle: {vehicle_data.get('name')}\n"
                f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
                f"Size: {vehicle_data.get('vehicle_size').value if isinstance(vehicle_data.get('vehicle_size'), VehicleSize) else 'unknown'}\n\n"
                "Create an interesting history for this vehicle, including who built it, "
                "notable previous owners or uses, significant journeys or events it has been part of, "
                "and any legends or stories associated with it. The history should add depth and "
                "narrative hooks for the vehicle."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_vehicle["history"] = response
            except Exception as e:
                print(f"Error generating vehicle history: {e}")
                enhanced_vehicle["history"] = f"A {vehicle_data.get('name')} with a typical history."
            
        return enhanced_vehicle
    
    def analyze_vehicle_requirements(self, 
                                  vehicle_id: str,
                                  journey_length: str = "medium",
                                  crew_skill: str = "average") -> Dict[str, Any]:
        """
        Analyze crew, maintenance, and resource requirements for a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            journey_length: Length of journey (short, medium, long)
            crew_skill: Skill level of the crew (novice, average, expert)
            
        Returns:
            Dict[str, Any]: Requirement analysis
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
            
        # Use LLM to analyze requirements
        prompt = self.llm_advisor._create_prompt(
            "analyze vehicle requirements",
            f"Vehicle: {vehicle_data.get('name')}\n"
            f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
            f"Size: {vehicle_data.get('vehicle_size').value if isinstance(vehicle_data.get('vehicle_size'), VehicleSize) else 'unknown'}\n"
            f"Crew Required: {vehicle_data.get('crew_required', 'Unknown')}\n"
            f"Journey Length: {journey_length}\n"
            f"Crew Skill Level: {crew_skill}\n\n"
            "Analyze the requirements for operating this vehicle effectively on a journey of the specified length. "
            "Include crew requirements (specific roles and skills needed), maintenance needs (frequency and type), "
            "resources needed (supplies, fuel, etc.), and costs associated with upkeep. "
            "Return as JSON with 'crew_details', 'maintenance_needs', 'resource_requirements', 'upkeep_costs', and 'special_considerations' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            requirements = self.llm_advisor._extract_json(response)
            
            if requirements:
                return {
                    "vehicle_name": vehicle_data.get("name"),
                    "journey_length": journey_length,
                    "crew_skill": crew_skill,
                    "requirements": requirements
                }
        except Exception as e:
            print(f"Error analyzing vehicle requirements: {e}")
        
        # Fallback response
        return {
            "vehicle_name": vehicle_data.get("name"),
            "journey_length": journey_length,
            "crew_skill": crew_skill,
            "requirements": {
                "crew_details": [{"role": "Operator", "skills": ["Vehicle handling"]}],
                "maintenance_needs": ["Regular inspection"],
                "resource_requirements": ["Standard supplies"],
                "upkeep_costs": f"Variable based on {journey_length} journey",
                "special_considerations": ["None noted"]
            }
        }
    
    def calculate_vehicle_journey(self, 
                               vehicle_id: str, 
                               distance_miles: float,
                               terrain_type: str = "normal",
                               rest_hours_per_day: int = 16) -> Dict[str, Any]:
        """
        Calculate journey details for a specific distance.
        
        Args:
            vehicle_id: ID of the vehicle
            distance_miles: Distance in miles
            terrain_type: Type of terrain to traverse
            rest_hours_per_day: Hours spent resting (not traveling) per day
            
        Returns:
            Dict[str, Any]: Journey calculation results
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
        
        # Get vehicle speed
        base_speed = vehicle_data.get("speed", 3)  # mph
        
        # Adjust for terrain
        terrain_multipliers = {
            "easy": 1.2,
            "normal": 1.0,
            "difficult": 0.7,
            "mixed": 0.9
        }
        
        terrain_mult = terrain_multipliers.get(terrain_type.lower(), 1.0)
        adjusted_speed = base_speed * terrain_mult
        
        # Calculate travel time
        travel_hours_per_day = 24 - rest_hours_per_day
        distance_per_day = adjusted_speed * travel_hours_per_day
        
        days_required = math.ceil(distance_miles / distance_per_day)
        total_hours = (distance_miles / adjusted_speed)
        
        # Check if the vehicle has properties that affect journey calculation
        properties = vehicle_data.get("properties", [])
        
        # Calculate supply needs
        crew_size = vehicle_data.get("crew_required", self._get_default_crew_requirement(vehicle_data.get("vehicle_size")))
        passenger_capacity = vehicle_data.get("passenger_capacity", 0)
        total_people = crew_size + passenger_capacity
        
        # Basic supplies calculation (food and water)
        food_per_person_per_day = 1  # pound
        water_per_person_per_day = 1  # gallon
        
        total_food_needed = total_people * days_required * food_per_person_per_day
        total_water_needed = total_people * days_required * water_per_person_per_day
        
        # Calculate fuel/resources needed for the vehicle
        fuel_needed = "None"
        
        vehicle_type = vehicle_data.get("vehicle_type")
        if isinstance(vehicle_type, VehicleType):
            if vehicle_type == VehicleType.LAND:
                # Animal-drawn vehicles need feed
                if not any("self_propelled" in p.lower() for p in properties):
                    fuel_needed = f"{days_required * 10} pounds of animal feed"
            elif vehicle_type == VehicleType.MECHANICAL:
                fuel_needed = f"{days_required * 5} gallons of fuel"
            elif vehicle_type == VehicleType.MAGICAL:
                fuel_needed = f"{days_required} charges of magical energy"
        
        return {
            "vehicle_name": vehicle_data.get("name"),
            "journey_distance": distance_miles,
            "terrain_type": terrain_type,
            "adjusted_speed_mph": adjusted_speed,
            "travel_hours_per_day": travel_hours_per_day,
            "distance_per_day": round(distance_per_day, 1),
            "days_required": days_required,
            "total_travel_hours": round(total_hours, 1),
            "supplies_needed": {
                "food_pounds": total_food_needed,
                "water_gallons": total_water_needed,
                "fuel": fuel_needed
            }
        }
    
    def generate_vehicle_appearance(self, vehicle_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            style: Optional style direction (e.g., "opulent", "utilitarian", "battle-scarred")
            
        Returns:
            str: Detailed appearance description
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return "Vehicle not found"
        
        context = f"Vehicle: {vehicle_data.get('name')}\n"
        context += f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
        context += f"Size: {vehicle_data.get('vehicle_size').value if isinstance(vehicle_data.get('vehicle_size'), VehicleSize) else 'unknown'}\n"
        context += f"Properties: {', '.join(vehicle_data.get('properties', []))}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this vehicle",
            context + "\n"
            "Create a vivid, detailed description of this vehicle's physical appearance. "
            "Include details about its construction, materials, distinctive features, "
            "decorations, unique mechanisms, and overall aesthetic. The description should help "
            "players visualize the vehicle clearly and understand its character and function."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating vehicle appearance: {e}")
            
        # Fallback description
        vehicle_type_str = vehicle_data.get("vehicle_type").value if isinstance(vehicle_data.get("vehicle_type"), VehicleType) else "vehicle"
        return f"A standard {vehicle_type_str} with typical construction and appearance."
    
    def suggest_vehicle_upgrades(self, 
                              vehicle_id: str,
                              budget: int = 1000,
                              upgrade_focus: str = "speed") -> Dict[str, Any]:
        """
        Suggest possible upgrades for a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            budget: Budget in gold pieces
            upgrade_focus: Focus area for upgrades (speed, capacity, comfort, etc.)
            
        Returns:
            Dict[str, Any]: Suggested upgrades
        """
        vehicle_data = self._find_item_by_id(vehicle_id)
        if not vehicle_data:
            return {"error": "Vehicle not found"}
            
        # Use LLM to suggest upgrades
        prompt = self.llm_advisor._create_prompt(
            "suggest vehicle upgrades",
            f"Vehicle: {vehicle_data.get('name')}\n"
            f"Type: {vehicle_data.get('vehicle_type').value if isinstance(vehicle_data.get('vehicle_type'), VehicleType) else 'unknown'}\n"
            f"Size: {vehicle_data.get('vehicle_size').value if isinstance(vehicle_data.get('vehicle_size'), VehicleSize) else 'unknown'}\n"
            f"Properties: {', '.join(vehicle_data.get('properties', []))}\n"
            f"Budget: {budget} gold pieces\n"
            f"Upgrade Focus: {upgrade_focus}\n\n"
            "Suggest possible upgrades for this vehicle within the specified budget and focus area. "
            "For each upgrade, include a name, description, benefits, cost, and any requirements or drawbacks. "
            "Ensure the upgrades are appropriate for the vehicle type and size. "
            "Return as JSON with 'recommended_upgrades' as an array of objects with 'name', 'description', 'benefits', 'cost', and 'requirements' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            upgrades = self.llm_advisor._extract_json(response)
            
            if upgrades and "recommended_upgrades" in upgrades:
                return {
                    "vehicle_name": vehicle_data.get("name"),
                    "budget": budget,
                    "upgrade_focus": upgrade_focus,
                    "suggested_upgrades": upgrades["recommended_upgrades"]
                }
        except Exception as e:
            print(f"Error suggesting vehicle upgrades: {e}")
        
        # Fallback response
        return {
            "vehicle_name": vehicle_data.get("name"),
            "budget": budget,
            "upgrade_focus": upgrade_focus,
            "suggested_upgrades": [
                {
                    "name": "Basic Improvement",
                    "description": "Standard upgrade for this vehicle type",
                    "benefits": ["Slightly improved performance"],
                    "cost": budget // 2,
                    "requirements": ["Standard materials"]
                }
            ]
        }
    
    # === HELPER METHODS ===
    
    def _get_default_crew_requirement(self, vehicle_size: VehicleSize) -> int:
        """Get default crew requirement based on vehicle size."""
        if isinstance(vehicle_size, VehicleSize):
            return self.typical_crew_requirements.get(vehicle_size, 1)
        return 1
    
    def _get_default_passenger_capacity(self, vehicle_size: VehicleSize) -> int:
        """Get default passenger capacity based on vehicle size."""
        if isinstance(vehicle_size, VehicleSize):
            if vehicle_size == VehicleSize.TINY:
                return 0
            elif vehicle_size == VehicleSize.SMALL:
                return 2
            elif vehicle_size == VehicleSize.MEDIUM:
                return 4
            elif vehicle_size == VehicleSize.LARGE:
                return 8
            elif vehicle_size == VehicleSize.HUGE:
                return 20
            elif vehicle_size == VehicleSize.GARGANTUAN:
                return 40
        return 2  # Default to 2 passengers