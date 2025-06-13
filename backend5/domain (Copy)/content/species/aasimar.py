from typing import Dict, List, Optional, Any, Tuple
from ....core.abstractions.species import AbstractSpecies, SpeciesSize

class Human(AbstractSpecies):
    """
    Concrete implementation of the Human species from D&D 2024 Player's Handbook.
    
    Humans are versatile and adaptable, known for their:
    - Medium size and 30 ft speed
    - Flexible ability score improvements
    - Extra skill proficiency and feat at 1st level
    - Adaptable nature allowing for diverse builds
    """
    
    def get_name(self) -> str:
        """Get the name of the species."""
        return "Human"
    
    def get_size(self) -> SpeciesSize:
        """Humans are Medium creatures."""
        return SpeciesSize.MEDIUM
    
    def get_base_speed(self) -> int:
        """Humans have 30 feet base walking speed."""
        return 30
    
    def get_movement_types(self) -> Dict[str, int]:
        """Humans have only walking speed."""
        return {"walking": 30}
    
    def get_ability_score_increases(self) -> Dict[str, int]:
        """
        Per D&D 2024 rules, Humans get flexible ability score increases.
        This returns the default pattern, but can be customized during character creation.
        """
        return {
            "strength": 1,
            "dexterity": 1,
            "constitution": 1,
            "intelligence": 1,
            "wisdom": 1,
            "charisma": 1
        }
    
    def get_vision_types(self) -> Dict[str, int]:
        """Humans have normal vision only."""
        return {}
    
    def get_languages(self) -> List[str]:
        """Humans know Common plus one additional language of choice."""
        return ["Common", "Choice"]  # "Choice" indicates player can choose
    
    def get_damage_resistances(self) -> List[str]:
        """Humans have no inherent damage resistances."""
        return []
    
    def get_damage_immunities(self) -> List[str]:
        """Humans have no inherent damage immunities."""
        return []
    
    def get_condition_immunities(self) -> List[str]:
        """Humans have no inherent condition immunities."""
        return []
    
    def get_traits(self) -> Dict[str, Any]:
        """
        Get Human species traits per D&D 2024 rules.
        """
        return {
            "Resourceful": {
                "description": "You gain Heroic Inspiration whenever you finish a Long Rest.",
                "type": "passive",
                "mechanics": "heroic_inspiration_on_long_rest"
            },
            "Skillful": {
                "description": "You gain proficiency in one skill of your choice.",
                "type": "choice",
                "mechanics": "skill_proficiency_choice"
            },
            "Versatile": {
                "description": "You gain a 1st-level Feat of your choice.",
                "type": "choice", 
                "mechanics": "feat_choice_level_1"
            }
        }
    
    def get_proficiencies(self) -> Dict[str, List[str]]:
        """
        Humans get one skill proficiency of choice.
        """
        return {
            "skills": ["Choice"],  # Player chooses one skill
            "tools": [],
            "weapons": []
        }
    
    def get_lineages(self) -> List[str]:
        """
        Humans don't have official lineages in D&D 2024, but could support variants.
        """
        return ["Standard", "Variant Human"]  # Variant could be optional rule
    
    def get_lineage_details(self, lineage: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific human lineage."""
        lineages = {
            "Standard": {
                "description": "Standard Human with flexible ability increases",
                "modifications": {}
            },
            "Variant Human": {
                "description": "Variant Human with different trait distribution",
                "modifications": {
                    "ability_increases": {"choice_1": 1, "choice_2": 1},  # Choose 2 different abilities
                    "additional_traits": ["Extra Feat"]
                }
            }
        }
        return lineages.get(lineage)
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if humans have a specific feature."""
        features = ["Resourceful", "Skillful", "Versatile"]
        return feature_name in features
    
    def get_age_range(self) -> Tuple[int, int]:
        """Humans reach adulthood around 18 and live less than 100 years."""
        return (18, 80)
    
    def get_size_dimensions(self) -> Dict[str, Tuple[float, float]]:
        """Get typical human height and weight ranges."""
        return {
            "height": (4.5, 6.5),  # 4'6" to 6'6" in feet
            "weight": (100, 300)   # 100 to 300 pounds
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert human species to dictionary format."""
        return {
            "name": self.get_name(),
            "size": self.get_size().name,
            "speed": self.get_base_speed(),
            "movement_types": self.get_movement_types(),
            "ability_increases": self.get_ability_score_increases(),
            "vision": self.get_vision_types(),
            "languages": self.get_languages(),
            "damage_resistances": self.get_damage_resistances(),
            "traits": self.get_traits(),
            "proficiencies": self.get_proficiencies(),
            "lineages": self.get_lineages(),
            "age_range": self.get_age_range(),
            "size_dimensions": self.get_size_dimensions()
        }
    
    def validate(self) -> Tuple[bool, str]:
        """Validate the human species definition."""
        # Check required traits
        if self.get_base_speed() != 30:
            return False, "Human speed should be 30 feet"
        
        if self.get_size() != SpeciesSize.MEDIUM:
            return False, "Humans should be Medium size"
        
        required_traits = ["Resourceful", "Skillful", "Versatile"]
        current_traits = list(self.get_traits().keys())
        
        for trait in required_traits:
            if trait not in current_traits:
                return False, f"Missing required trait: {trait}"
        
        return True, "Human species validation passed"
    
    def apply_to_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply human traits to a character."""
        updated_character = character_data.copy()
        
        # Apply size and speed
        updated_character["size"] = self.get_size().name
        updated_character["speed"] = self.get_movement_types()
        
        # Apply ability score increases (flexible - player chooses)
        if "ability_scores" not in updated_character:
            updated_character["ability_scores"] = {}
        
        # Note: In actual implementation, this would handle the flexible nature
        # For now, apply the standard +1 to all abilities
        for ability, increase in self.get_ability_score_increases().items():
            current = updated_character["ability_scores"].get(ability, 10)
            updated_character["ability_scores"][ability] = current + increase
        
        # Apply languages
        if "languages" not in updated_character:
            updated_character["languages"] = []
        
        for language in self.get_languages():
            if language != "Choice" and language not in updated_character["languages"]:
                updated_character["languages"].append(language)
        
        # Apply traits
        if "species_traits" not in updated_character:
            updated_character["species_traits"] = {}
        
        updated_character["species_traits"].update(self.get_traits())
        
        # Apply proficiencies (player choice handled elsewhere)
        if "proficiencies" not in updated_character:
            updated_character["proficiencies"] = {"skills": [], "tools": [], "weapons": []}
        
        # Note: Skill choice handled during character creation
        
        return updated_character
    
    def get_character_creation_choices(self) -> Dict[str, Any]:
        """
        Get choices that need to be made during character creation.
        
        Returns:
            Dict describing choices to be made
        """
        return {
            "ability_score_distribution": {
                "type": "flexible",
                "description": "Choose how to distribute +6 total ability score increases",
                "options": "Any combination adding to +6, max +2 per ability"
            },
            "skill_proficiency": {
                "type": "choice",
                "description": "Choose one skill proficiency",
                "options": [
                    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                    "History", "Insight", "Intimidation", "Investigation", "Medicine",
                    "Nature", "Perception", "Performance", "Persuasion", "Religion",
                    "Sleight of Hand", "Stealth", "Survival"
                ]
            },
            "language": {
                "type": "choice", 
                "description": "Choose one additional language",
                "options": "Any standard language"
            },
            "feat": {
                "type": "choice",
                "description": "Choose a 1st-level feat",
                "options": "Any 1st-level feat"
            }
        }