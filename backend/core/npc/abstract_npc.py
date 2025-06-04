from abc import ABC, abstractmethod
import math
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum, auto

# Import relevant modules
from backend.core.species.abstract_species import AbstractSpecies
from backend.core.alignment.abstract_alignment import Alignment
from backend.core.equipment.abstract_equipment import AbstractEquipment
from backend.core.spells.abstract_spells import AbstractSpell

class NPCRole(Enum):
    """Common NPC roles in a campaign"""
    ALLY = "ally"
    ANTAGONIST = "antagonist"
    NEUTRAL = "neutral"
    QUEST_GIVER = "quest_giver"
    MERCHANT = "merchant"
    INFORMANT = "informant"
    BACKGROUND = "background"
    VILLAIN = "villain"

class NPCCategory(Enum):
    """Categories of NPCs in D&D"""
    COMMONER = auto()       # Basic townspeople, peasants, etc.
    EXPERT = auto()         # Skilled professionals without combat focus
    WARRIOR = auto()        # Combat-focused NPCs
    SPELLCASTER = auto()    # Magic-using NPCs 
    HYBRID = auto()         # Mixture of combat and spellcasting
    NOBLE = auto()          # Political or social elites
    MONSTER_HUMANOID = auto() # Humanoid creatures with monster traits

class AbstractNPC(ABC):
    """
    Abstract base class for Non-Player Characters (NPCs) in D&D.
    
    In D&D 5th edition, Non-Player Characters (NPCs) are essentially creatures controlled by the Dungeon Master (DM) 
    to populate the world and interact with the players. They can range from simple shopkeepers to powerful villains, 
    and their complexity is determined by their role in the campaign.
    
    Key characteristics and attributes of an NPC:
    1. Name: Identity and flavor for memorable characters
    2. Creature Type and Tags: Humanoid type with profession/role tags
    3. Ability Scores: STR, DEX, CON, INT, WIS, CHA defining capabilities
    4. Armor Class (AC): Defense rating from armor, dexterity, and magic
    5. Hit Points (HP): Durability before defeat
    6. Speed: Movement capabilities (walk, fly, swim)
    7. Skills: Proficiencies with bonus added to rolls
    8. Senses: Perception abilities like Darkvision
    9. Languages: Communication capabilities
    10. Challenge Rating (CR): Threat level for combat encounters
    11. Traits: Passive special abilities
    12. Actions: Combat abilities and attacks
    13. Spellcasting: Magical abilities (if applicable)
    
    Beyond mechanics, NPCs have personality, goals, motivations, and a role in the world.
    """
    
    # Default skill list based on 2024 rules
    SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Saving throws correspond to ability scores
    SAVING_THROWS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    def __init__(self, name: str, species: AbstractSpecies, 
                challenge_rating: float = 0.125,
                role: Union[str, NPCRole] = NPCRole.BACKGROUND,
                category: NPCCategory = NPCCategory.COMMONER,
                alignment: Alignment = None,
                ability_scores: Dict[str, int] = None,
                tags: List[str] = None):
        """
        Initialize a new NPC.
        
        Args:
            name: NPC name
            species: NPC species (formerly race)
            challenge_rating: Threat level (CR) for this NPC
            role: Role in the campaign
            category: General category of NPC
            alignment: NPC alignment (if any)
            ability_scores: Dictionary with ability scores
            tags: Additional descriptive tags (like "guard", "noble", "merchant")
        """
        self.name = name
        self.species = species
        self.challenge_rating = challenge_rating
        self.alignment = alignment
        self.category = category
        
        # Set role (convert string to enum if needed)
        if isinstance(role, str):
            try:
                self.role = NPCRole(role.lower())
            except ValueError:
                self.role = NPCRole.BACKGROUND
        else:
            self.role = role
            
        # Set tags
        self.tags = tags or []
        
        # Set ability scores (default to 10s if not provided)
        if ability_scores:
            self.ability_scores = ability_scores
        else:
            # Most basic NPCs have average scores
            self.ability_scores = {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10, 
                "wisdom": 10,
                "charisma": 10
            }
        
        # Basic stats
        self.hit_points = 0
        self.hit_dice = "1d8"
        self.armor_class = 10  # Base AC
        self.proficiency_bonus = self._calculate_proficiency_bonus()
        
        # Set up NPC capabilities
        self.skill_proficiencies = []
        self.saving_throw_proficiencies = []
        self.equipment = []
        self.languages = []
        self.speed = {
            "walk": 30,
            "swim": 0,
            "fly": 0,
            "climb": 0,
            "burrow": 0
        }
        self.senses = {
            "darkvision": 0,
            "blindsight": 0,
            "tremorsense": 0,
            "truesight": 0,
            "passive_perception": 10 + self._calculate_ability_modifier(self.ability_scores["wisdom"])
        }
        
        # Combat-related attributes
        self.traits = {}  # Passive special abilities
        self.actions = {}  # Combat actions
        self.reactions = {}  # Reaction abilities
        self.legendary_actions = {}  # For special NPCs
        
        # Spellcasting (if applicable)
        self.spellcaster = False
        self.spellcasting_ability = None
        self.spell_save_dc = 0
        self.spell_attack_bonus = 0
        self.spells = {}  # Dict with spell levels as keys, lists of spells as values
        
        # Resistances, immunities, vulnerabilities
        self.damage_resistances = []
        self.damage_immunities = []
        self.damage_vulnerabilities = []
        self.condition_immunities = []
        
        # NPC personality and behavior
        self.personality_traits = []
        self.ideals = []
        self.bonds = []
        self.flaws = []
        self.mannerisms = []
        self.goals = []
        self.notes = ""
        
        # Apply species traits
        self._apply_species_traits()
        
        # Calculate hit points
        self._calculate_hit_points()
    
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
    
    def _apply_species_traits(self):
        """Apply species traits to the NPC."""
        # Apply species-specific bonuses
        self.species.apply_species_bonuses(self)
        
        # Set base speed
        if hasattr(self.species, 'speed'):
            self.speed["walk"] = self.species.speed
        
        # Set darkvision if applicable
        if hasattr(self.species, 'darkvision'):
            self.senses["darkvision"] = self.species.darkvision
        
        # Add languages
        if hasattr(self.species, 'languages'):
            self.languages = list(self.species.languages)
    
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
        con_mod = self.get_ability_modifier("constitution")
        average_roll = (die_type + 1) / 2  # Average roll on a die is (max + min) / 2
        self.hit_points = int(num_dice * average_roll + (con_mod * num_dice))
    
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
        Apply damage to the NPC.
        
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
        Heal the NPC.
        
        Args:
            amount: Amount of healing to receive
            
        Returns:
            int: New hit point total
        """
        # Calculate original max hit points
        max_hp = self._calculate_hit_points()
        
        # Cannot heal beyond maximum
        self.hit_points = min(max_hp, self.hit_points + amount)
        return self.hit_points
    
    def add_trait(self, name: str, description: str):
        """
        Add a special trait to the NPC.
        
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
        Add an action the NPC can take.
        
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
        Add a reaction the NPC can take.
        
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
        Add a legendary action the NPC can take.
        
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
    
    def setup_spellcasting(self, ability: str, spells_by_level: Dict[int, List[str]]):
        """
        Set up the NPC as a spellcaster.
        
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
    
    def add_skill_proficiency(self, skill: str):
        """
        Add a skill proficiency.
        
        Args:
            skill: The skill to add proficiency in
            
        Returns:
            bool: True if added successfully
        """
        if skill not in self.skill_proficiencies and skill in self.SKILLS:
            self.skill_proficiencies.append(skill)
            
            # Update passive perception if adding Perception
            if skill == "Perception":
                self.senses["passive_perception"] = 10 + self.get_skill_modifier("Perception")
                
            return True
        return False
    
    def add_language(self, language: str):
        """
        Add a language.
        
        Args:
            language: The language to add
            
        Returns:
            bool: True if added successfully
        """
        if language not in self.languages:
            self.languages.append(language)
            return True
        return False
    
    def set_speed(self, movement_type: str, speed: int):
        """
        Set a movement speed for the NPC.
        
        Args:
            movement_type: Type of movement (walk, swim, fly, climb, burrow)
            speed: Speed in feet
            
        Returns:
            dict: Updated speed dictionary
        """
        if movement_type.lower() in self.speed:
            self.speed[movement_type.lower()] = speed
        return self.speed
    
    def add_equipment(self, item: Union[str, AbstractEquipment]):
        """
        Add equipment to the NPC.
        
        Args:
            item: Equipment item to add
            
        Returns:
            list: Updated equipment list
        """
        self.equipment.append(item)
        return self.equipment
    
    def set_personality(self, traits=None, ideals=None, bonds=None, flaws=None, mannerisms=None, goals=None):
        """
        Set the NPC's personality elements.
        
        Args:
            traits: Personality traits
            ideals: Core ideals and beliefs
            bonds: Connections to people, places, or things
            flaws: Character weaknesses
            mannerisms: Distinctive habits and behaviors
            goals: Objectives and motivations
            
        Returns:
            dict: Updated personality information
        """
        if traits:
            self.personality_traits = traits if isinstance(traits, list) else [traits]
        if ideals:
            self.ideals = ideals if isinstance(ideals, list) else [ideals]
        if bonds:
            self.bonds = bonds if isinstance(bonds, list) else [bonds]
        if flaws:
            self.flaws = flaws if isinstance(flaws, list) else [flaws]
        if mannerisms:
            self.mannerisms = mannerisms if isinstance(mannerisms, list) else [mannerisms]
        if goals:
            self.goals = goals if isinstance(goals, list) else [goals]
        
        return {
            "traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "mannerisms": self.mannerisms,
            "goals": self.goals
        }
    
    def to_stat_block(self) -> Dict[str, Any]:
        """
        Convert NPC to a D&D stat block format.
        
        Returns:
            dict: Dictionary representation of the NPC's stat block
        """
        # Format size and type
        tags_str = f" ({', '.join(self.tags)})" if self.tags else ""
        size_type = f"{self.species.size.name.lower()} {self.species.name}{tags_str}, {self.alignment}" if self.alignment else f"{self.species.size.name.lower()} {self.species.name}{tags_str}"
        
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
            "size_type_alignment": size_type,
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
        
        # Add spellcasting if applicable
        if self.spellcaster:
            stat_block["spellcasting"] = {
                "ability": self.spellcasting_ability,
                "spell_save_dc": self.spell_save_dc,
                "spell_attack_bonus": f"+{self.spell_attack_bonus}",
                "spells_by_level": self.spells
            }
        
        return stat_block
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert NPC to a complete dictionary including both mechanics and personality.
        
        Returns:
            dict: Dictionary representation of the NPC
        """
        stat_block = self.to_stat_block()
        
        # Add personality elements
        personality = {
            "role": self.role.value if isinstance(self.role, NPCRole) else self.role,
            "category": self.category.name,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "mannerisms": self.mannerisms,
            "goals": self.goals,
            "notes": self.notes
        }
        
        return {**stat_block, **{"personality": personality}}
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save NPC to a JSON file.
        
        Args:
            filename: The filename to save to
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving NPC: {e}")
            return False
    
    @classmethod
    @abstractmethod
    def load_from_file(cls, filename: str):
        """
        Load NPC from a JSON file.
        
        Args:
            filename: The filename to load from
            
        Returns:
            AbstractNPC: A new NPC instance
        """
        pass


class AbstractNPCs(ABC):
    """
    Abstract base class for managing NPCs in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the NPC system, including:
    - Retrieving information about NPCs
    - Filtering NPCs based on various criteria
    - Creating and managing NPCs
    - Handling NPC interactions and behavior
    """
    
    @abstractmethod
    def get_all_npcs(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available NPCs.
        
        Returns:
            List[Dict[str, Any]]: List of NPC summary information
        """
        pass
    
    @abstractmethod
    def get_npc_details(self, npc_id: str) -> Optional[AbstractNPC]:
        """
        Get detailed information about an NPC.
        
        Args:
            npc_id: Unique identifier for the NPC
            
        Returns:
            Optional[AbstractNPC]: The NPC object or None if not found
        """
        pass
    
    @abstractmethod
    def filter_npcs(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter NPCs based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[Dict[str, Any]]: List of filtered NPC summaries
        """
        pass
    
    @abstractmethod
    def create_npc(self, npc_data: Dict[str, Any]) -> AbstractNPC:
        """
        Create a new NPC.
        
        Args:
            npc_data: NPC definition data
            
        Returns:
            AbstractNPC: New NPC instance
        """
        pass
    
    @abstractmethod
    def generate_random_npc(self, parameters: Dict[str, Any] = None) -> AbstractNPC:
        """
        Generate a random NPC based on optional parameters.
        
        Args:
            parameters: Optional parameters to guide generation
            
        Returns:
            AbstractNPC: Randomly generated NPC
        """
        pass
    
    @abstractmethod
    def get_npcs_by_role(self, role: Union[str, NPCRole]) -> List[Dict[str, Any]]:
        """
        Get NPCs by their role in the campaign.
        
        Args:
            role: Role to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching NPC summaries
        """
        pass
    
    @abstractmethod
    def get_npcs_by_category(self, category: Union[str, NPCCategory]) -> List[Dict[str, Any]]:
        """
        Get NPCs by their category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching NPC summaries
        """
        pass
    
    @abstractmethod
    def get_npcs_by_cr_range(self, min_cr: float, max_cr: float) -> List[Dict[str, Any]]:
        """
        Get NPCs within a challenge rating range.
        
        Args:
            min_cr: Minimum challenge rating
            max_cr: Maximum challenge rating
            
        Returns:
            List[Dict[str, Any]]: List of matching NPC summaries
        """
        pass
    
    @abstractmethod
    def get_npc_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available NPC templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping template names to their definitions
        """
        pass
    
    @abstractmethod
    def create_npc_from_template(self, template_id: str, customizations: Dict[str, Any] = None) -> AbstractNPC:
        """
        Create an NPC from a template with optional customizations.
        
        Args:
            template_id: Template identifier
            customizations: Custom overrides for the template
            
        Returns:
            AbstractNPC: New NPC instance based on template
        """
        pass
    
    @abstractmethod
    def update_npc(self, npc_id: str, updates: Dict[str, Any]) -> Optional[AbstractNPC]:
        """
        Update an existing NPC.
        
        Args:
            npc_id: NPC identifier
            updates: Changes to apply
            
        Returns:
            Optional[AbstractNPC]: Updated NPC or None if not found
        """
        pass
    
    @abstractmethod
    def generate_npc_interaction(self, npc_id: str, interaction_type: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate dialogue and behavior for an NPC interaction.
        
        Args:
            npc_id: NPC identifier
            interaction_type: Type of interaction (e.g., "greeting", "shop", "quest")
            context: Optional contextual information
            
        Returns:
            Dict[str, Any]: Interaction details
        """
        pass
    
    @abstractmethod
    def get_related_npcs(self, npc_id: str) -> List[Dict[str, Any]]:
        """
        Find NPCs related to a specific NPC.
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            List[Dict[str, Any]]: List of related NPCs with relationship information
        """
        pass
    
    def npc_exists(self, npc_id: str) -> bool:
        """
        Check if an NPC exists.
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            bool: True if NPC exists, False otherwise
        """
        return self.get_npc_details(npc_id) is not None