from abc import ABC, abstractmethod
import math
import json
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from enum import Enum, auto

class CreatureType(Enum):
    """Types of creatures in D&D"""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class CreatureSize(Enum):
    """Size categories for creatures in D&D"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class CreatureTag(Enum):
    """Common tags for creatures in D&D"""
    AMPHIBIOUS = auto()
    AQUATIC = auto()
    AIRBORNE = auto()
    PACK_TACTICS = auto()
    SHAPECHANGER = auto()
    SWARM = auto()
    MAGICAL = auto()
    VENOMOUS = auto()
    LEGENDARY = auto()
    MYTHIC = auto()
    SPELLCASTER = auto()

class AbstractCreature(ABC):
    """
    Abstract base class for D&D creatures following the 2024 revised rules.
    
    Key characteristics and attributes of a creature in D&D:
    1. Creature Type: The fundamental nature of the creature (beast, humanoid, etc.)
    2. Ability Scores: STR, DEX, CON, INT, WIS, CHA
    3. Armor Class (AC): Defense rating, often from natural armor
    4. Hit Points (HP): Durability before being incapacitated
    5. Speed: Movement capabilities (walk, climb, swim, fly)
    6. Skills: Proficiencies like Perception or Stealth
    7. Senses: Darkvision, Blindsight, Tremorsense, etc.
    8. Languages: Communication capabilities
    9. Challenge Rating (CR): Difficulty/threat level
    10. Traits: Passive special abilities
    11. Actions: Combat abilities and attacks
    """
    
    # Common creature skills
    COMMON_SKILLS = [
        "Perception", "Stealth", "Athletics", "Survival", "Intimidation"
    ]
    
    # Saving throws correspond to ability scores
    SAVING_THROWS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    def __init__(self, name: str, creature_type: Union[str, CreatureType], challenge_rating: float, 
                 size: Union[str, CreatureSize] = CreatureSize.MEDIUM, 
                 ability_scores: Dict[str, int] = None,
                 creature_tags: List[Union[str, CreatureTag]] = None):
        """
        Initialize a new creature.
        
        Args:
            name: Creature name
            creature_type: Type of creature
            challenge_rating: Threat level (CR)
            size: Size category
            ability_scores: Dictionary with ability scores
            creature_tags: Additional descriptive tags for the creature
        """
        self.name = name
        
        # Convert creature_type string to enum if needed
        if isinstance(creature_type, str):
            try:
                self.creature_type = CreatureType(creature_type.lower())
            except ValueError:
                raise ValueError(f"Invalid creature type: {creature_type}")
        else:
            self.creature_type = creature_type
            
        self.challenge_rating = challenge_rating
        
        # Convert size string to enum if needed
        if isinstance(size, str):
            try:
                self.size = CreatureSize(size.lower())
            except ValueError:
                raise ValueError(f"Invalid creature size: {size}")
        else:
            self.size = size
            
        # Process tags
        self.tags = []
        if creature_tags:
            for tag in creature_tags:
                if isinstance(tag, str):
                    self.tags.append(tag)
                else:
                    self.tags.append(tag.name)
        
        # Set ability scores (default to average scores if not provided)
        if ability_scores:
            self.ability_scores = ability_scores
        else:
            # Default ability scores (somewhat average)
            self.ability_scores = {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        
        # Initialize other creature attributes
        self.hit_points = 0
        self.hit_dice = "1d8"  # Default, will be overridden by specific creatures
        self.armor_class = 10  # Base AC
        self.natural_armor_bonus = 0
        
        # Movement
        self.speed = {
            "walk": 30,
            "climb": 0,
            "swim": 0,
            "fly": 0,
            "burrow": 0
        }
        
        # Calculate proficiency bonus based on CR
        self.proficiency_bonus = self._calculate_proficiency_bonus()
        
        # Skills and senses
        self.skill_proficiencies = []
        self.saving_throw_proficiencies = []
        self.senses = {
            "darkvision": 0,
            "blindsight": 0,
            "tremorsense": 0,
            "truesight": 0,
            "passive_perception": 10 + self._calculate_ability_modifier(self.ability_scores["wisdom"])
        }
        
        # Combat-related attributes
        self.damage_immunities = []
        self.damage_resistances = []
        self.damage_vulnerabilities = []
        self.condition_immunities = []
        
        # Creature-specific attributes
        self.languages = []
        self.traits = {}     # Special traits/abilities
        self.actions = {}    # Attack and special actions
        self.reactions = {}  # Reaction abilities
        self.legendary_actions = {} # For legendary creatures
        self.lair_actions = {} # For creatures with lairs
        
        # Spellcasting (if applicable)
        self.spellcaster = False
        self.spellcasting_ability = None
        self.spell_save_dc = 0
        self.spell_attack_bonus = 0
        self.spells = {}  # Dict with spell levels as keys, lists of spells as values
        
        # Calculate initial hit points
        self._calculate_hit_points()
        
        # Calculate armor class
        self._calculate_armor_class()
    
    def _calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on Challenge Rating."""
        if self.challenge_rating < 1:
            return 2
        elif self.challenge_rating < 5:
            return 2
        elif self.challenge_rating < 9:
            return 3
        elif self.challenge_rating < 13:
            return 4
        elif self.challenge_rating < 17:
            return 5
        else:
            return 6
    
    def _calculate_ability_modifier(self, score: int) -> int:
        """Calculate ability modifier from score."""
        return math.floor((score - 10) / 2)
    
    def _calculate_hit_points(self):
        """Calculate hit points based on hit dice and Constitution."""
        # Parse hit dice (e.g., "3d8" -> 3 dice of d8)
        try:
            num_dice, die_type = self.hit_dice.split('d')
            num_dice = int(num_dice)
            die_type = int(die_type)
        except ValueError:
            num_dice = 1
            die_type = 8
        
        # Calculate average HP: num_dice * (average roll on die) + (CON mod * num_dice)
        con_mod = self._calculate_ability_modifier(self.ability_scores["constitution"])
        average_roll = (die_type + 1) / 2  # Average roll on a die is (max + min) / 2
        self.hit_points = int(num_dice * average_roll + (con_mod * num_dice))
    
    def _calculate_armor_class(self):
        """Calculate armor class based on Dexterity and natural armor."""
        dex_mod = self._calculate_ability_modifier(self.ability_scores["dexterity"])
        self.armor_class = 10 + dex_mod + self.natural_armor_bonus
    
    def get_ability_modifier(self, ability: str) -> int:
        """
        Get the modifier for a specific ability.
        
        Args:
            ability: The ability to get the modifier for
            
        Returns:
            int: The ability modifier
        """
        score = self.ability_scores.get(ability.lower(), 10)
        return self._calculate_ability_modifier(score)
    
    def get_saving_throw_modifier(self, ability: str) -> int:
        """
        Get the modifier for a specific saving throw.
        
        Args:
            ability: The ability for the saving throw
            
        Returns:
            int: The saving throw modifier
        """
        modifier = self.get_ability_modifier(ability)
        
        # Add proficiency bonus if proficient
        if ability.capitalize() in self.saving_throw_proficiencies:
            modifier += self.proficiency_bonus
            
        return modifier
    
    def get_skill_modifier(self, skill: str) -> int:
        """
        Get the modifier for a specific skill.
        
        Args:
            skill: The skill to get the modifier for
            
        Returns:
            int: The skill modifier
        """
        # Map skills to their primary abilities
        skill_to_ability = {
            "Acrobatics": "dexterity",
            "Animal Handling": "wisdom",
            "Arcana": "intelligence",
            "Athletics": "strength",
            "Deception": "charisma",
            "History": "intelligence",
            "Insight": "wisdom",
            "Intimidation": "charisma",
            "Investigation": "intelligence",
            "Medicine": "wisdom",
            "Nature": "intelligence",
            "Perception": "wisdom",
            "Performance": "charisma",
            "Persuasion": "charisma",
            "Religion": "intelligence",
            "Sleight of Hand": "dexterity",
            "Stealth": "dexterity",
            "Survival": "wisdom"
        }
        
        ability = skill_to_ability.get(skill, "dexterity")
        modifier = self.get_ability_modifier(ability)
        
        # Add proficiency bonus if proficient
        if skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
            
        return modifier
    
    def take_damage(self, damage: int, damage_type: str = "bludgeoning") -> int:
        """
        Apply damage to the creature.
        
        Args:
            damage: Amount of damage to take
            damage_type: Type of damage being dealt
            
        Returns:
            int: Remaining hit points
        """
        # Check for immunities, resistances, and vulnerabilities
        if damage_type in self.damage_immunities:
            return self.hit_points  # No damage taken
        
        if damage_type in self.damage_resistances:
            damage = damage // 2  # Half damage from resistances
            
        if damage_type in self.damage_vulnerabilities:
            damage = damage * 2  # Double damage from vulnerabilities
        
        # Apply to hit points
        self.hit_points = max(0, self.hit_points - damage)
        return self.hit_points
    
    def heal(self, amount: int) -> int:
        """
        Heal the creature.
        
        Args:
            amount: Amount of healing to receive
            
        Returns:
            int: New hit point total
        """
        # Calculate max hit points
        max_hp = self._calculate_hit_points()
        
        # You cannot heal beyond your maximum hit points
        self.hit_points = min(max_hp, self.hit_points + amount)
        return self.hit_points
    
    def add_trait(self, name: str, description: str):
        """
        Add a special trait to the creature.
        
        Args:
            name: Name of the trait
            description: Description of what the trait does
            
        Returns:
            dict: Updated traits dictionary
        """
        self.traits[name] = description
        return self.traits
    
    def add_action(self, name: str, description: str, attack_bonus: int = None, damage: str = None):
        """
        Add an action the creature can take.
        
        Args:
            name: Name of the action
            description: Description of what the action does
            attack_bonus: Bonus to attack rolls
            damage: Damage formula (e.g., "2d6+3 slashing")
            
        Returns:
            dict: Updated actions dictionary
        """
        self.actions[name] = {
            "description": description,
            "attack_bonus": attack_bonus,
            "damage": damage
        }
        return self.actions
    
    def add_reaction(self, name: str, description: str):
        """
        Add a reaction the creature can take.
        
        Args:
            name: Name of the reaction
            description: Description of what the reaction does
            
        Returns:
            dict: Updated reactions dictionary
        """
        self.reactions[name] = description
        return self.reactions
    
    def add_legendary_action(self, name: str, description: str, cost: int = 1):
        """
        Add a legendary action the creature can take.
        
        Args:
            name: Name of the legendary action
            description: Description of what the action does
            cost: Action point cost (usually 1-3)
            
        Returns:
            dict: Updated legendary actions dictionary
        """
        self.legendary_actions[name] = {
            "description": description,
            "cost": cost
        }
        return self.legendary_actions
    
    def add_lair_action(self, name: str, description: str):
        """
        Add a lair action the creature can take.
        
        Args:
            name: Name of the lair action
            description: Description of what the action does
            
        Returns:
            dict: Updated lair actions dictionary
        """
        self.lair_actions[name] = description
        return self.lair_actions
    
    def setup_spellcasting(self, ability: str, spells_by_level: Dict[int, List[str]]):
        """
        Set up the creature as a spellcaster.
        
        Args:
            ability: The spellcasting ability ("intelligence", "wisdom", or "charisma")
            spells_by_level: Dictionary with spell levels as keys and lists of spell names as values
            
        Returns:
            bool: True if successful
        """
        ability_mod = self.get_ability_modifier(ability)
        
        self.spellcaster = True
        self.spellcasting_ability = ability
        self.spell_save_dc = 8 + self.proficiency_bonus + ability_mod
        self.spell_attack_bonus = self.proficiency_bonus + ability_mod
        self.spells = spells_by_level
        
        return True
    
    def set_speed(self, movement_type: str, speed: int):
        """
        Set a movement speed for the creature.
        
        Args:
            movement_type: Type of movement (walk, swim, fly, climb, burrow)
            speed: Speed in feet
            
        Returns:
            dict: Updated speed dictionary
        """
        if movement_type.lower() in self.speed:
            self.speed[movement_type.lower()] = speed
        return self.speed
    
    def add_sense(self, sense_type: str, range_feet: int):
        """
        Add or modify a sense.
        
        Args:
            sense_type: Type of sense (darkvision, blindsight, etc.)
            range_feet: Range in feet
            
        Returns:
            dict: Updated senses dictionary
        """
        if sense_type.lower() in self.senses:
            self.senses[sense_type.lower()] = range_feet
            
            # Update passive perception if needed
            if sense_type.lower() == "perception":
                self.senses["passive_perception"] = 10 + range_feet
                
        return self.senses
    
    def set_hit_dice(self, hit_dice: str):
        """
        Set the hit dice for the creature.
        
        Args:
            hit_dice: Hit dice formula (e.g., "3d8")
            
        Returns:
            str: Updated hit dice
        """
        self.hit_dice = hit_dice
        self._calculate_hit_points()
        return self.hit_dice
    
    def add_skill_proficiency(self, skill: str):
        """
        Add a skill proficiency.
        
        Args:
            skill: The skill to add proficiency in
            
        Returns:
            bool: True if added successfully
        """
        if skill not in self.skill_proficiencies:
            self.skill_proficiencies.append(skill)
            
            # Update passive perception if adding Perception
            if skill == "Perception":
                self.senses["passive_perception"] = 10 + self.get_skill_modifier("Perception")
                
            return True
        return False
    
    def add_language(self, language: str):
        """
        Add a language the creature can understand or speak.
        
        Args:
            language: The language to add
            
        Returns:
            list: Updated languages list
        """
        if language not in self.languages:
            self.languages.append(language)
        return self.languages
    
    def _get_xp_for_cr(self, cr: float) -> int:
        """Get XP value for a challenge rating."""
        cr_to_xp = {
            0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450,
            3: 700, 4: 1100, 5: 1800, 6: 2300, 7: 2900, 8: 3900,
            9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000,
            14: 11500, 15: 13000, 16: 15000, 17: 18000, 18: 20000,
            19: 22000, 20: 25000, 21: 33000, 22: 41000, 23: 50000,
            24: 62000, 25: 75000, 26: 90000, 27: 105000, 28: 120000,
            29: 135000, 30: 155000
        }
        return cr_to_xp.get(cr, 0)
    
    def to_stat_block(self) -> Dict[str, Any]:
        """
        Convert creature to a D&D stat block format.
        
        Returns:
            dict: Dictionary representation of the creature's stat block
        """
        # Format size and type
        tags_str = f" ({', '.join(self.tags)})" if self.tags else ""
        size_type = f"{self.size.value.capitalize()} {self.creature_type.value}{tags_str}"
        
        # Format ability scores
        abilities = {}
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = self.ability_scores[ability]
            modifier = self.get_ability_modifier(ability)
            mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            abilities[ability.capitalize()] = f"{score} ({mod_str})"
        
        # Format senses
        senses_list = []
        for sense, range_val in self.senses.items():
            if range_val > 0 and sense != "passive_perception":
                senses_list.append(f"{sense.capitalize()} {range_val} ft.")
        senses_list.append(f"passive Perception {self.senses['passive_perception']}")
        
        # Format speeds
        speeds_list = []
        for move_type, speed_val in self.speed.items():
            if speed_val > 0:
                if move_type == "walk":
                    speeds_list.append(f"{speed_val} ft.")
                else:
                    speeds_list.append(f"{move_type} {speed_val} ft.")
        
        # Format skills
        skills_list = []
        for skill in self.skill_proficiencies:
            modifier = self.get_skill_modifier(skill)
            mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            skills_list.append(f"{skill} {mod_str}")
            
        # Format saving throws
        saves_list = []
        for save in self.saving_throw_proficiencies:
            modifier = self.get_saving_throw_modifier(save.lower())
            mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            saves_list.append(f"{save} {mod_str}")
        
        # Create the stat block
        stat_block = {
            "name": self.name,
            "size_type": size_type,
            "armor_class": self.armor_class,
            "hit_points": f"{self.hit_points} ({self.hit_dice})",
            "speed": ", ".join(speeds_list),
            "ability_scores": abilities,
            "saving_throws": saves_list,
            "skills": skills_list,
            "damage_resistances": self.damage_resistances,
            "damage_immunities": self.damage_immunities,
            "damage_vulnerabilities": self.damage_vulnerabilities,
            "condition_immunities": self.condition_immunities,
            "senses": ", ".join(senses_list),
            "languages": ", ".join(self.languages) if self.languages else "—",
            "challenge": f"{self.challenge_rating} ({self._get_xp_for_cr(self.challenge_rating)} XP)",
            "traits": self.traits,
            "actions": self.actions,
            "reactions": self.reactions
        }
        
        # Add legendary actions if applicable
        if self.legendary_actions:
            stat_block["legendary_actions"] = self.legendary_actions
            
        # Add lair actions if applicable
        if self.lair_actions:
            stat_block["lair_actions"] = self.lair_actions
        
        # Add spellcasting if applicable
        if self.spellcaster:
            stat_block["spellcasting"] = {
                "ability": self.spellcasting_ability,
                "spell_save_dc": self.spell_save_dc,
                "spell_attack_bonus": f"+{self.spell_attack_bonus}",
                "spells_by_level": self.spells
            }
        
        return stat_block
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save creature to a JSON file.
        
        Args:
            filename: The filename to save to
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_stat_block(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving creature: {e}")
            return False
    
    @classmethod
    @abstractmethod
    def load_from_file(cls, filename: str):
        """
        Load creature from a JSON file.
        
        Args:
            filename: The filename to load from
            
        Returns:
            AbstractCreature: A new creature instance
        """
        pass
        
    def __str__(self) -> str:
        """String representation of the creature."""
        return f"{self.name} ({self.size.value} {self.creature_type.value})"


class AbstractCreatures(ABC):
    """
    Abstract base class for managing creatures in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the creature system, including:
    - Retrieving information about creatures
    - Filtering creatures based on various criteria
    - Creating and managing creatures
    - Handling creature encounters and combat
    """
    
    @abstractmethod
    def get_all_creatures(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available creatures.
        
        Returns:
            List[Dict[str, Any]]: List of creature summary information
        """
        pass
    
    @abstractmethod
    def get_creature_details(self, creature_id: str) -> Optional[AbstractCreature]:
        """
        Get detailed information about a creature.
        
        Args:
            creature_id: Unique identifier for the creature
            
        Returns:
            Optional[AbstractCreature]: The creature object or None if not found
        """
        pass
    
    @abstractmethod
    def filter_creatures(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter creatures based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[Dict[str, Any]]: List of filtered creature summaries
        """
        pass
    
    @abstractmethod
    def create_creature(self, creature_data: Dict[str, Any]) -> AbstractCreature:
        """
        Create a new creature.
        
        Args:
            creature_data: Creature definition data
            
        Returns:
            AbstractCreature: New creature instance
        """
        pass
    
    @abstractmethod
    def get_creatures_by_type(self, creature_type: Union[str, CreatureType]) -> List[Dict[str, Any]]:
        """
        Get creatures by their type.
        
        Args:
            creature_type: Type to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching creature summaries
        """
        pass
    
    @abstractmethod
    def get_creatures_by_cr_range(self, min_cr: float, max_cr: float) -> List[Dict[str, Any]]:
        """
        Get creatures within a challenge rating range.
        
        Args:
            min_cr: Minimum challenge rating
            max_cr: Maximum challenge rating
            
        Returns:
            List[Dict[str, Any]]: List of matching creature summaries
        """
        pass
    
    @abstractmethod
    def get_creatures_by_environment(self, environment: str) -> List[Dict[str, Any]]:
        """
        Get creatures commonly found in a specific environment.
        
        Args:
            environment: Environment type (forest, desert, mountain, etc.)
            
        Returns:
            List[Dict[str, Any]]: List of matching creature summaries
        """
        pass
    
    @abstractmethod
    def get_creature_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available creature templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping template names to their definitions
        """
        pass
    
    @abstractmethod
    def create_creature_from_template(self, template_id: str, 
                                   customizations: Dict[str, Any] = None) -> AbstractCreature:
        """
        Create a creature from a template with optional customizations.
        
        Args:
            template_id: Template identifier
            customizations: Custom overrides for the template
            
        Returns:
            AbstractCreature: New creature instance based on template
        """
        pass
    
    @abstractmethod
    def update_creature(self, creature_id: str, updates: Dict[str, Any]) -> Optional[AbstractCreature]:
        """
        Update an existing creature.
        
        Args:
            creature_id: Creature identifier
            updates: Changes to apply
            
        Returns:
            Optional[AbstractCreature]: Updated creature or None if not found
        """
        pass
    
    @abstractmethod
    def generate_random_encounter(self, party_level: int, difficulty: str = "medium", 
                               environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate a random encounter appropriate for a party.
        
        Args:
            party_level: Average party level
            difficulty: Encounter difficulty (easy, medium, hard, deadly)
            environment: Optional environment to filter creatures
            
        Returns:
            List[Dict[str, Any]]: List of creatures for the encounter
        """
        pass
    
    @abstractmethod
    def calculate_encounter_xp(self, creatures: List[Union[str, AbstractCreature]], 
                            num_players: int) -> Dict[str, Any]:
        """
        Calculate encounter difficulty and XP value.
        
        Args:
            creatures: List of creatures or creature IDs
            num_players: Number of players in the party
            
        Returns:
            Dict[str, Any]: Encounter XP information and difficulty assessment
        """
        pass
    
    def creature_exists(self, creature_id: str) -> bool:
        """
        Check if a creature exists.
        
        Args:
            creature_id: Creature identifier
            
        Returns:
            bool: True if creature exists, False otherwise
        """
        return self.get_creature_details(creature_id) is not None