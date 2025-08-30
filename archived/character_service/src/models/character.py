"""Character models for D&D characters."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class AbilityScores:
    """D&D ability scores."""
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

class Character(BaseModel):
    """Core character data model.
    
    All characters (PCs, NPCs, and monsters) have a challenge rating (CR).
    CR may be hidden in display but is used for encounter balancing.
    """
    id: str
    name: str
    race: str
    class_name: str
    level: int
    ability_scores: AbilityScores
    background: Optional[str] = None
    alignment: Optional[str] = None
    description: Optional[str] = None
    proficiencies: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    spells: Optional[List[str]] = None
    features: Optional[List[str]] = None
    traits: Optional[Dict[str, str]] = None
    challenge_rating: float = 0.0  # Hidden for PCs but used for encounter balance
    effective_cr_factors: Optional[Dict[str, Any]] = None  # Stores CR calculation factors
    
    # NPC-specific fields
    is_npc: bool = False
    npc_role: Optional[str] = None
    is_friendly: Optional[bool] = None
    is_recurring: Optional[bool] = None
    social_traits: Optional[Dict[str, str]] = None
    
    # Monster-specific fields
    is_monster: bool = False
    monster_type: Optional[str] = None
    size: Optional[str] = None
    is_legendary: Optional[bool] = None
    lair_actions: Optional[List[Dict[str, Any]]] = None
    legendary_actions: Optional[List[Dict[str, Any]]] = None
    regional_effects: Optional[List[Dict[str, Any]]] = None
    
    # Combat-related fields
    armor_class: int = 10
    hit_points: int = 0
    hit_dice: str = "1d8"
    speed: Dict[str, int] = {"walk": 30}
    damage_resistances: List[str] = []
    damage_immunities: List[str] = []
    damage_vulnerabilities: List[str] = []
    condition_immunities: List[str] = []
    saving_throws: Dict[str, int] = {}
    skills: Dict[str, int] = {}
    senses: Dict[str, int] = {"passive_perception": 10}
    languages: List[str] = ["Common"]
    
    # Spellcasting
    spellcasting_ability: Optional[str] = None
    spell_save_dc: Optional[int] = None
    spell_attack_bonus: Optional[int] = None
    spells_known: List[Dict[str, Any]] = []
    spell_slots: Dict[str, int] = {}
    
    # Theme and customization
    theme: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "race": self.race,
            "class_name": self.class_name,
            "level": self.level,
            "ability_scores": {
                "strength": self.ability_scores.strength,
                "dexterity": self.ability_scores.dexterity,
                "constitution": self.ability_scores.constitution,
                "intelligence": self.ability_scores.intelligence,
                "wisdom": self.ability_scores.wisdom,
                "charisma": self.ability_scores.charisma
            },
            "background": self.background,
            "alignment": self.alignment,
            "description": self.description,
            "proficiencies": self.proficiencies,
            "equipment": self.equipment,
            "spells": self.spells,
            "features": self.features,
            "traits": self.traits,
            "challenge_rating": self.challenge_rating,
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "hit_dice": self.hit_dice,
            "speed": self.speed,
            "saving_throws": self.saving_throws,
            "skills": self.skills,
            "damage_resistances": self.damage_resistances,
            "damage_immunities": self.damage_immunities,
            "damage_vulnerabilities": self.damage_vulnerabilities,
            "condition_immunities": self.condition_immunities,
            "senses": self.senses,
            "languages": self.languages,
            "is_npc": self.is_npc,
            "is_monster": self.is_monster,
            "theme": self.theme
        }

    def get_display_sheet(self, include_cr: bool = False) -> Dict[str, Any]:
        """Get character sheet for display.
        
        Args:
            include_cr: Whether to include CR (shown for monsters/NPCs, hidden for PCs)
        """
        sheet = self.to_dict()
        
        # Remove CR unless specifically requested or monster/NPC
        if not include_cr and not (self.is_monster or self.is_npc):
            sheet.pop("challenge_rating", None)
            sheet.pop("effective_cr_factors", None)
        
        return sheet

@dataclass
class CharacterSheet:
    """Complete character sheet including calculated values."""
    character: Character
    ability_modifiers: Dict[str, int]
    proficiency_bonus: int
    initiative_bonus: int
    passive_perception: int
    spell_slots_by_level: Dict[int, int]
    carrying_capacity: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character sheet to dictionary format."""
        return {
            "character": self.character.to_dict(),
            "ability_modifiers": self.ability_modifiers,
            "proficiency_bonus": self.proficiency_bonus,
            "initiative_bonus": self.initiative_bonus,
            "passive_perception": self.passive_perception,
            "spell_slots_by_level": self.spell_slots_by_level,
            "carrying_capacity": self.carrying_capacity
        }
