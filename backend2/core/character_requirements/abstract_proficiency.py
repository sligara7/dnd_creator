from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ProficiencyType(Enum):
    """Enumeration of proficiency types in D&D 5e (2024 Edition)."""
    SKILL = auto()      # Skill proficiencies (Perception, Stealth, etc.)
    SAVING_THROW = auto()  # Saving throw proficiencies (CON, DEX, etc.)
    TOOL = auto()       # Tool proficiencies (thieves' tools, herbalism kit, etc.)
    WEAPON = auto()     # Weapon proficiencies (simple, martial, specific)
    ARMOR = auto()      # Armor proficiencies (light, medium, heavy, shields)
    LANGUAGE = auto()   # Language proficiencies (Common, Elvish, etc.)

class ProficiencyLevel(Enum):
    """Enumeration of proficiency levels in D&D 5e (2024 Edition)."""
    NONE = 0            # No proficiency (0× proficiency bonus)
    HALF = 0.5          # Half proficiency (0.5× proficiency bonus, rounded down)
    PROFICIENT = 1      # Proficient (1× proficiency bonus)
    EXPERT = 2          # Expertise (2× proficiency bonus)

class WeaponCategory(Enum):
    """Weapon categories in D&D 5e (2024 Edition)."""
    SIMPLE = auto()
    MARTIAL = auto()
    SPECIFIC = auto()   # For specific weapon proficiencies

class ArmorCategory(Enum):
    """Armor categories in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()

class AbstractProficiency(ABC):
    """
    Abstract base class defining the contract for proficiency systems in D&D 5e (2024 Edition).
    
    In D&D, proficiencies represent a character's training and expertise with:
    - Skills (e.g., Perception, Athletics)
    - Saving throws (e.g., Constitution saves, Dexterity saves)
    - Tools (e.g., thieves' tools, alchemist's supplies)
    - Weapons (simple, martial, or specific weapons)
    - Armor (light, medium, heavy, shields)
    - Languages (Common, Elvish, etc.)
    
    Proficiencies grant bonuses to relevant ability checks, attack rolls, or other actions.
    """
    
    # Proficiency bonus by character level as per D&D 2024 rules
    PROFICIENCY_BONUS = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Standard skill list as per D&D 2024 rules
    SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Standard ability scores
    ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    # Standard tool categories
    TOOL_CATEGORIES = ["Artisan's Tools", "Gaming Sets", "Musical Instruments", "Other Tools"]
    
    # Common languages in D&D 2024
    STANDARD_LANGUAGES = [
        "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", 
        "Halfling", "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", 
        "Infernal", "Primordial", "Sylvan", "Undercommon"
    ]
    
    @abstractmethod
    def calculate_proficiency_bonus(self, character_level: int) -> int:
        """
        Calculate proficiency bonus based on character level.
        
        Per D&D 2024 rules:
        - Levels 1-4: +2
        - Levels 5-8: +3
        - Levels 9-12: +4
        - Levels 13-16: +5
        - Levels 17-20: +6
        
        Args:
            character_level: Total character level (1-20)
            
        Returns:
            int: Proficiency bonus
        """
        pass
    
    @abstractmethod
    def get_proficiency_level(self, prof_type: ProficiencyType, specific_prof: str) -> ProficiencyLevel:
        """
        Get the proficiency level for a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            ProficiencyLevel: Level of proficiency
        """
        pass
    
    @abstractmethod
    def set_proficiency_level(self, prof_type: ProficiencyType, specific_prof: str, 
                           level: ProficiencyLevel) -> bool:
        """
        Set the proficiency level for a specific proficiency.
        
        Per D&D 2024 rules:
        - Proficiency levels generally don't stack
        - When multiple features grant proficiency, take the highest level
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            level: Level of proficiency
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def add_proficiency(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Add a proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def add_expertise(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Add expertise for a proficiency.
        
        Per D&D 2024 rules, expertise doubles the proficiency bonus
        for checks using that proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if expertise was successfully added
        """
        pass
    
    @abstractmethod
    def apply_jack_of_all_trades(self) -> bool:
        """
        Apply the Jack of All Trades feature.
        
        Per D&D 2024 rules, Jack of All Trades allows adding half the proficiency
        bonus (rounded down) to any ability check that doesn't already include
        the proficiency bonus.
        
        Returns:
            bool: True if successfully applied
        """
        pass
    
    @abstractmethod
    def has_jack_of_all_trades(self) -> bool:
        """
        Check if the character has Jack of All Trades.
        
        Returns:
            bool: True if the character has Jack of All Trades
        """
        pass
    
    @abstractmethod
    def calculate_modifier(self, prof_type: ProficiencyType, specific_prof: str, 
                        ability_scores: Dict[str, int], character_level: int) -> int:
        """
        Calculate the total modifier for a check using this proficiency.
        
        Per D&D 2024 rules:
        - Base modifier is the relevant ability score modifier
        - Add proficiency bonus if proficient
        - Add twice proficiency bonus if expertise
        - Add half proficiency bonus (rounded down) if Jack of All Trades applies
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            ability_scores: Character's ability scores
            character_level: Character's level
            
        Returns:
            int: Total modifier
        """
        pass
    
    @abstractmethod
    def get_all_proficiencies(self) -> Dict[ProficiencyType, List[str]]:
        """
        Get all proficiencies the character has.
        
        Returns:
            Dict[ProficiencyType, List[str]]: All proficiencies by type
        """
        pass
    
    @abstractmethod
    def get_all_expertise(self) -> Dict[ProficiencyType, List[str]]:
        """
        Get all proficiencies the character has expertise in.
        
        Returns:
            Dict[ProficiencyType, List[str]]: All expertise proficiencies
        """
        pass
    
    @abstractmethod
    def has_proficiency(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Check if the character is proficient in a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if proficient
        """
        pass
    
    @abstractmethod
    def has_expertise(self, prof_type: ProficiencyType, specific_prof: str) -> bool:
        """
        Check if the character has expertise in a specific proficiency.
        
        Args:
            prof_type: Type of proficiency
            specific_prof: Name of the specific proficiency
            
        Returns:
            bool: True if has expertise
        """
        pass
    
    @abstractmethod
    def get_proficiencies_by_source(self, source: str) -> Dict[ProficiencyType, List[str]]:
        """
        Get proficiencies from a specific source.
        
        Per D&D 2024 rules, proficiencies come from:
        - Character class
        - Background
        - Species
        - Feats
        
        Args:
            source: Source of proficiencies (class, background, species, feat)
            
        Returns:
            Dict[ProficiencyType, List[str]]: Proficiencies from that source
        """
        pass
    
    @abstractmethod
    def can_use_armor(self, armor_name: str) -> Tuple[bool, str]:
        """
        Check if character can use a specific armor.
        
        Per D&D 2024 rules:
        - Characters need proficiency to use armor effectively
        - Non-proficient use of armor imposes disadvantage on
          ability checks, saving throws, and attack rolls that use
          Strength or Dexterity, and prevents spellcasting
        
        Args:
            armor_name: Name of the armor
            
        Returns:
            Tuple[bool, str]: (Can use, explanation)
        """
        pass
    
    @abstractmethod
    def can_use_weapon(self, weapon_name: str) -> bool:
        """
        Check if character can use a specific weapon.
        
        Per D&D 2024 rules:
        - Characters can use any weapon, but only add proficiency bonus
          to attack rolls with weapons they're proficient with
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            bool: True if proficient with the weapon
        """
        pass
    
    @abstractmethod
    def can_use_tool(self, tool_name: str) -> bool:
        """
        Check if character can use a specific tool.
        
        Per D&D 2024 rules:
        - Characters can attempt to use any tool
        - Proficiency adds the proficiency bonus to the check
        - Some tool uses might require proficiency
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: True if proficient with the tool
        """
        pass
    
    @abstractmethod
    def can_speak_language(self, language: str) -> bool:
        """
        Check if character can speak a specific language.
        
        Args:
            language: Name of the language
            
        Returns:
            bool: True if character knows the language
        """
        pass
    
    @abstractmethod
    def add_saving_throw_proficiency(self, ability: str) -> bool:
        """
        Add proficiency in a saving throw.
        
        Per D&D 2024 rules:
        - Each class grants proficiency in specific saving throws
        - Some features can grant additional saving throw proficiencies
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def is_proficient_in_saving_throw(self, ability: str) -> bool:
        """
        Check if character is proficient in a saving throw.
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            
        Returns:
            bool: True if proficient in that saving throw
        """
        pass
    
    @abstractmethod
    def calculate_saving_throw_modifier(self, ability: str, ability_scores: Dict[str, int], 
                                      character_level: int) -> int:
        """
        Calculate modifier for a saving throw.
        
        Per D&D 2024 rules:
        - Base is the ability score modifier
        - Add proficiency bonus if proficient in that saving throw
        
        Args:
            ability: Ability score (Strength, Dexterity, etc.)
            ability_scores: Character's ability scores
            character_level: Character's level
            
        Returns:
            int: Total saving throw modifier
        """
        pass
    
    @abstractmethod
    def get_tool_categories(self) -> Dict[str, List[str]]:
        """
        Get all tool categories and their tools.
        
        Per D&D 2024 rules, tools include:
        - Artisan's tools (smith's tools, carpenter's tools, etc.)
        - Gaming sets (dice set, playing card set)
        - Musical instruments (drum, lute, etc.)
        - Other tools (thieves' tools, navigator's tools, etc.)
        
        Returns:
            Dict[str, List[str]]: Tool categories and tools
        """
        pass
    
    @abstractmethod
    def get_weapons_by_category(self) -> Dict[WeaponCategory, List[str]]:
        """
        Get weapons organized by category.
        
        Per D&D 2024 rules, weapons are categorized as:
        - Simple weapons
        - Martial weapons
        - Specific weapons (for special proficiencies)
        
        Returns:
            Dict[WeaponCategory, List[str]]: Weapons by category
        """
        pass
    
    @abstractmethod
    def get_armor_by_category(self) -> Dict[ArmorCategory, List[str]]:
        """
        Get armor organized by category.
        
        Per D&D 2024 rules, armor is categorized as:
        - Light armor
        - Medium armor
        - Heavy armor
        - Shields
        
        Returns:
            Dict[ArmorCategory, List[str]]: Armor by category
        """
        pass
    
    @abstractmethod
    def get_languages_by_rarity(self) -> Dict[str, List[str]]:
        """
        Get languages organized by rarity.
        
        Per D&D 2024 rules, languages are categorized as:
        - Common languages (Common, Dwarvish, Elvish, etc.)
        - Exotic languages (Abyssal, Celestial, etc.)
        
        Returns:
            Dict[str, List[str]]: Languages by rarity
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_class(self, class_name: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a character class.
        
        Per D&D 2024 rules, each class grants:
        - Saving throw proficiencies (2)
        - Skill proficiencies (2-4 from a class list)
        - Armor proficiencies (varies)
        - Weapon proficiencies (varies)
        - Tool proficiencies (some classes)
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_background(self, background: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a background.
        
        Per D&D 2024 rules, backgrounds typically grant:
        - Two skill proficiencies
        - Tool proficiency or language
        
        Args:
            background: Name of the background
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_proficiencies_from_species(self, species: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from a species.
        
        Per D&D 2024 rules, some species grant:
        - Skill proficiencies
        - Tool proficiencies
        - Weapon proficiencies
        - Languages
        
        Args:
            species: Name of the species
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def add_multiclass_proficiencies(self, new_class: str) -> Dict[ProficiencyType, List[str]]:
        """
        Add proficiencies from multiclassing.
        
        Per D&D 2024 rules, multiclassing grants:
        - Limited armor/weapon proficiencies
        - No saving throw proficiencies
        - Limited skill proficiencies (typically 1)
        
        Args:
            new_class: New class being added
            
        Returns:
            Dict[ProficiencyType, List[str]]: Added proficiencies
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert proficiency data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of proficiencies
        """
        pass