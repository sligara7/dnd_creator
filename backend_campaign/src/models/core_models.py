"""
Core D&D Models for Campaign Creation

This module provides fundamental D&D mechanics and data structures needed for campaign creation,
including ability scores, challenge ratings, encounter balancing, and character statistics.

Dependencies: Minimal (pure domain logic for campaign creation)
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CORE D&D ENUMS
# ============================================================================

class AbilityScore(str, Enum):
    """D&D 5e ability scores."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

class Skill(str, Enum):
    """D&D 5e skills."""
    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal_handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    RELIGION = "religion"
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"

class DamageType(str, Enum):
    """D&D 5e damage types."""
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"

class CreatureSize(str, Enum):
    """D&D 5e creature sizes."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class CreatureType(str, Enum):
    """D&D 5e creature types."""
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

class Environment(str, Enum):
    """D&D 5e environments for encounter generation."""
    ARCTIC = "arctic"
    COASTAL = "coastal"
    DESERT = "desert"
    FOREST = "forest"
    GRASSLAND = "grassland"
    HILL = "hill"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    UNDERDARK = "underdark"
    UNDERWATER = "underwater"
    URBAN = "urban"
    DUNGEON = "dungeon"
    PLANAR = "planar"

class EncounterDifficulty(str, Enum):
    """D&D 5e encounter difficulty levels."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"
    LEGENDARY = "legendary"

# ============================================================================
# CHALLENGE RATING SYSTEM
# ============================================================================

@dataclass
class ChallengeRating:
    """D&D 5e Challenge Rating system for monsters and NPCs."""
    
    # CR to XP mapping (official D&D 5e values)
    CR_TO_XP = {
        0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
        1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
        6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
        11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000,
        16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
        21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000,
        26: 90000, 27: 105000, 28: 120000, 29: 135000, 30: 155000
    }
    
    # XP thresholds per character level (easy, medium, hard, deadly)
    XP_THRESHOLDS = {
        1: (25, 50, 75, 100), 2: (50, 100, 150, 200), 3: (75, 150, 225, 400),
        4: (125, 250, 375, 500), 5: (250, 500, 750, 1100), 6: (300, 600, 900, 1400),
        7: (350, 750, 1100, 1700), 8: (450, 900, 1400, 2100), 9: (550, 1100, 1600, 2400),
        10: (600, 1200, 1900, 2800), 11: (800, 1600, 2400, 3600), 12: (1000, 2000, 3000, 4500),
        13: (1100, 2200, 3400, 5100), 14: (1250, 2500, 3800, 5700), 15: (1400, 2800, 4300, 6400),
        16: (1600, 3200, 4800, 7200), 17: (2000, 3900, 5900, 8800), 18: (2100, 4200, 6300, 9500),
        19: (2400, 4900, 7300, 10900), 20: (2800, 5700, 8500, 12700)
    }
    
    value: Union[int, float]
    
    def __post_init__(self):
        """Validate CR value."""
        valid_crs = list(self.CR_TO_XP.keys())
        if self.value not in valid_crs:
            raise ValueError(f"Invalid CR {self.value}. Must be one of {valid_crs}")
    
    @property
    def xp_value(self) -> int:
        """Get XP value for this CR."""
        return self.CR_TO_XP[self.value]
    
    @classmethod
    def from_xp(cls, xp: int) -> 'ChallengeRating':
        """Create CR from XP value (finds closest match)."""
        closest_cr = min(cls.CR_TO_XP.keys(), 
                        key=lambda cr: abs(cls.CR_TO_XP[cr] - xp))
        return cls(closest_cr)
    
    @classmethod
    def for_party_level(cls, party_level: int, difficulty: EncounterDifficulty, 
                       party_size: int = 4) -> List['ChallengeRating']:
        """Calculate appropriate CR range for a party."""
        if party_level not in cls.XP_THRESHOLDS:
            raise ValueError(f"Invalid party level {party_level}")
        
        thresholds = cls.XP_THRESHOLDS[party_level]
        difficulty_index = {
            EncounterDifficulty.EASY: 0,
            EncounterDifficulty.MEDIUM: 1, 
            EncounterDifficulty.HARD: 2,
            EncounterDifficulty.DEADLY: 3
        }[difficulty]
        
        target_xp = thresholds[difficulty_index] * party_size
        
        # Find CR range that produces encounters around target XP
        suitable_crs = []
        for cr, xp in cls.CR_TO_XP.items():
            if target_xp * 0.5 <= xp <= target_xp * 2.0:
                suitable_crs.append(cls(cr))
        
        return suitable_crs or [cls.from_xp(target_xp)]

# ============================================================================
# ABILITY SCORE UTILITIES
# ============================================================================

class AbilityScoreUtils:
    """Utilities for ability score calculations."""
    
    @staticmethod
    def calculate_modifier(score: int) -> int:
        """Calculate ability modifier from score."""
        return (score - 10) // 2
    
    @staticmethod
    def generate_standard_array() -> Dict[AbilityScore, int]:
        """Generate standard D&D ability score array."""
        scores = [15, 14, 13, 12, 10, 8]
        abilities = list(AbilityScore)
        return {ability: scores[i] for i, ability in enumerate(abilities)}
    
    @staticmethod
    def generate_point_buy_array(points_spent: Dict[AbilityScore, int]) -> Dict[AbilityScore, int]:
        """Generate point-buy ability scores."""
        base_scores = {ability: 8 for ability in AbilityScore}
        
        # Point buy costs: 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9
        point_costs = {9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        
        for ability, final_score in points_spent.items():
            if final_score < 8 or final_score > 15:
                raise ValueError(f"Point buy scores must be 8-15, got {final_score}")
            base_scores[ability] = final_score
        
        return base_scores

# ============================================================================
# ENCOUNTER BUILDING
# ============================================================================

@dataclass
class EncounterBuilder:
    """Utility class for building balanced D&D encounters."""
    
    party_level: int
    party_size: int = 4
    target_difficulty: EncounterDifficulty = EncounterDifficulty.MEDIUM
    
    def calculate_encounter_budget(self) -> int:
        """Calculate XP budget for the encounter."""
        if self.party_level not in ChallengeRating.XP_THRESHOLDS:
            raise ValueError(f"Invalid party level {self.party_level}")
        
        thresholds = ChallengeRating.XP_THRESHOLDS[self.party_level]
        difficulty_index = {
            EncounterDifficulty.TRIVIAL: -1,  # Below easy
            EncounterDifficulty.EASY: 0,
            EncounterDifficulty.MEDIUM: 1,
            EncounterDifficulty.HARD: 2,
            EncounterDifficulty.DEADLY: 3,
            EncounterDifficulty.LEGENDARY: 4  # Above deadly
        }[self.target_difficulty]
        
        if difficulty_index == -1:
            budget = thresholds[0] * 0.5  # Half of easy
        elif difficulty_index == 4:
            budget = thresholds[3] * 1.5  # 150% of deadly
        else:
            budget = thresholds[difficulty_index]
        
        return int(budget * self.party_size)
    
    def suggest_single_monster(self) -> List[ChallengeRating]:
        """Suggest CR for a single monster encounter."""
        budget = self.calculate_encounter_budget()
        return [ChallengeRating.from_xp(budget)]
    
    def suggest_monster_group(self, group_size: int) -> List[ChallengeRating]:
        """Suggest CR for a group of monsters."""
        budget = self.calculate_encounter_budget()
        
        # Encounter multipliers from DMG
        multipliers = {1: 1, 2: 1.5, 3: 2, 4: 2, 5: 2.5, 6: 2.5, 7: 3, 8: 3}
        multiplier = multipliers.get(min(group_size, 8), 4)
        
        # Adjust for multiplier
        individual_budget = budget / (group_size * multiplier)
        
        return [ChallengeRating.from_xp(int(individual_budget))] * group_size
    
    def validate_encounter(self, monster_crs: List[ChallengeRating]) -> Dict[str, Any]:
        """Validate an encounter against party capabilities."""
        total_xp = sum(cr.xp_value for cr in monster_crs)
        
        # Apply encounter multiplier
        count = len(monster_crs)
        multipliers = {1: 1, 2: 1.5, 3: 2, 4: 2, 5: 2.5, 6: 2.5, 7: 3, 8: 3}
        multiplier = multipliers.get(min(count, 8), 4)
        
        adjusted_xp = total_xp * multiplier
        thresholds = ChallengeRating.XP_THRESHOLDS[self.party_level]
        party_thresholds = tuple(t * self.party_size for t in thresholds)
        
        # Determine actual difficulty
        if adjusted_xp < party_thresholds[0]:
            actual_difficulty = EncounterDifficulty.TRIVIAL
        elif adjusted_xp < party_thresholds[1]:
            actual_difficulty = EncounterDifficulty.EASY
        elif adjusted_xp < party_thresholds[2]:
            actual_difficulty = EncounterDifficulty.MEDIUM
        elif adjusted_xp < party_thresholds[3]:
            actual_difficulty = EncounterDifficulty.HARD
        else:
            actual_difficulty = EncounterDifficulty.DEADLY
        
        return {
            "total_base_xp": total_xp,
            "adjusted_xp": adjusted_xp,
            "multiplier": multiplier,
            "target_difficulty": self.target_difficulty,
            "actual_difficulty": actual_difficulty,
            "is_balanced": actual_difficulty == self.target_difficulty,
            "party_thresholds": {
                "easy": party_thresholds[0],
                "medium": party_thresholds[1], 
                "hard": party_thresholds[2],
                "deadly": party_thresholds[3]
            }
        }

# ============================================================================
# CHARACTER STATISTICS
# ============================================================================

@dataclass
class CharacterStatistics:
    """Statistical representation of character capabilities."""
    
    level: int
    ability_scores: Dict[AbilityScore, int]
    proficiency_bonus: int
    hit_points: int
    armor_class: int
    saving_throw_proficiencies: List[AbilityScore] = field(default_factory=list)
    skill_proficiencies: List[Skill] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived statistics."""
        if self.proficiency_bonus == 0:
            self.proficiency_bonus = self.calculate_proficiency_bonus()
    
    def calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus for character level."""
        return 2 + ((self.level - 1) // 4)
    
    def get_ability_modifier(self, ability: AbilityScore) -> int:
        """Get ability modifier for given ability."""
        return AbilityScoreUtils.calculate_modifier(self.ability_scores[ability])
    
    def get_saving_throw_bonus(self, ability: AbilityScore) -> int:
        """Calculate saving throw bonus."""
        modifier = self.get_ability_modifier(ability)
        if ability in self.saving_throw_proficiencies:
            modifier += self.proficiency_bonus
        return modifier
    
    def get_skill_bonus(self, skill: Skill) -> int:
        """Calculate skill check bonus."""
        # Map skills to abilities (simplified mapping)
        skill_abilities = {
            Skill.ATHLETICS: AbilityScore.STRENGTH,
            Skill.ACROBATICS: AbilityScore.DEXTERITY,
            Skill.STEALTH: AbilityScore.DEXTERITY,
            Skill.SLEIGHT_OF_HAND: AbilityScore.DEXTERITY,
            Skill.ARCANA: AbilityScore.INTELLIGENCE,
            Skill.HISTORY: AbilityScore.INTELLIGENCE,
            Skill.INVESTIGATION: AbilityScore.INTELLIGENCE,
            Skill.NATURE: AbilityScore.INTELLIGENCE,
            Skill.RELIGION: AbilityScore.INTELLIGENCE,
            Skill.ANIMAL_HANDLING: AbilityScore.WISDOM,
            Skill.INSIGHT: AbilityScore.WISDOM,
            Skill.MEDICINE: AbilityScore.WISDOM,
            Skill.PERCEPTION: AbilityScore.WISDOM,
            Skill.SURVIVAL: AbilityScore.WISDOM,
            Skill.DECEPTION: AbilityScore.CHARISMA,
            Skill.INTIMIDATION: AbilityScore.CHARISMA,
            Skill.PERFORMANCE: AbilityScore.CHARISMA,
            Skill.PERSUASION: AbilityScore.CHARISMA
        }
        
        ability = skill_abilities.get(skill, AbilityScore.INTELLIGENCE)
        modifier = self.get_ability_modifier(ability)
        
        if skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
            
        return modifier
    
    def calculate_combat_effectiveness(self) -> Dict[str, float]:
        """Calculate relative combat effectiveness metrics."""
        # Offensive capability
        str_mod = self.get_ability_modifier(AbilityScore.STRENGTH)
        dex_mod = self.get_ability_modifier(AbilityScore.DEXTERITY)
        offensive_score = max(str_mod, dex_mod) + self.proficiency_bonus
        
        # Defensive capability  
        defensive_score = self.armor_class + (self.hit_points / 10)
        
        # Utility capability
        int_mod = self.get_ability_modifier(AbilityScore.INTELLIGENCE)
        wis_mod = self.get_ability_modifier(AbilityScore.WISDOM)
        cha_mod = self.get_ability_modifier(AbilityScore.CHARISMA)
        utility_score = (int_mod + wis_mod + cha_mod) / 3
        
        return {
            "offensive": offensive_score,
            "defensive": defensive_score,
            "utility": utility_score,
            "overall": (offensive_score + defensive_score + utility_score) / 3
        }

# ============================================================================
# CAMPAIGN UTILITIES
# ============================================================================

class CampaignBalanceUtils:
    """Utilities for maintaining campaign balance and progression."""
    
    @staticmethod
    def calculate_session_xp_budget(party_level: int, party_size: int, 
                                   session_length_hours: float = 4.0) -> int:
        """Calculate recommended XP budget for a session."""
        # Base XP per level (rough guideline)
        base_xp_per_level = {
            1: 300, 2: 600, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        
        # XP needed for next level
        next_level_xp = base_xp_per_level.get(party_level, 50000)
        
        # Assume 6-8 sessions per level, adjust for session length
        sessions_per_level = 6 * (4.0 / session_length_hours)
        session_xp = next_level_xp / sessions_per_level
        
        return int(session_xp)
    
    @staticmethod
    def suggest_encounter_mix(total_xp_budget: int, party_level: int, 
                            party_size: int) -> List[Dict[str, Any]]:
        """Suggest a mix of encounters for a session."""
        builder = EncounterBuilder(party_level, party_size)
        
        encounters = []
        remaining_budget = total_xp_budget
        
        # Major encounter (30-40% of budget)
        major_budget = int(total_xp_budget * 0.35)
        major_builder = EncounterBuilder(party_level, party_size, EncounterDifficulty.HARD)
        encounters.append({
            "type": "major_combat",
            "difficulty": EncounterDifficulty.HARD,
            "xp_budget": major_budget,
            "suggested_cr": major_builder.suggest_single_monster()[0].value
        })
        remaining_budget -= major_budget
        
        # Medium encounters (40-50% of budget)
        medium_count = 2
        medium_budget_each = remaining_budget // 3
        medium_builder = EncounterBuilder(party_level, party_size, EncounterDifficulty.MEDIUM)
        for i in range(medium_count):
            encounters.append({
                "type": "standard_combat",
                "difficulty": EncounterDifficulty.MEDIUM,
                "xp_budget": medium_budget_each,
                "suggested_cr": medium_builder.suggest_single_monster()[0].value
            })
        remaining_budget -= medium_budget_each * medium_count
        
        # Easy/exploration encounters (remaining budget)
        if remaining_budget > 0:
            easy_builder = EncounterBuilder(party_level, party_size, EncounterDifficulty.EASY)
            encounters.append({
                "type": "exploration_or_social",
                "difficulty": EncounterDifficulty.EASY,
                "xp_budget": remaining_budget,
                "suggested_cr": easy_builder.suggest_single_monster()[0].value
            })
        
        return encounters

# ============================================================================
# EXPORT SUMMARY
# ============================================================================

__all__ = [
    # Enums
    'AbilityScore', 'Skill', 'DamageType', 'CreatureSize', 'CreatureType',
    'Environment', 'EncounterDifficulty',
    
    # Classes
    'ChallengeRating', 'AbilityScoreUtils', 'EncounterBuilder', 
    'CharacterStatistics', 'CampaignBalanceUtils'
]

# Module documentation
"""
CAMPAIGN CORE MODELS - REFACTORED FOR CAMPAIGN CREATION

This module provides essential D&D mechanics for campaign creation:

KEY FEATURES:
- Challenge Rating system with encounter balancing
- Ability score utilities for character generation
- Encounter building and validation tools
- Campaign balance utilities for session planning
- Character statistics for NPC/monster generation

USAGE:
- Import specific classes/enums as needed
- Use EncounterBuilder for balanced encounters
- Use ChallengeRating for appropriate monster selection
- Use CampaignBalanceUtils for session planning

INTEGRATION:
- Works with campaign_creation_models.py for API requests
- Supports generators.py for content generation
- Compatible with database_models.py for persistence
"""
