"""Challenge Rating calculation service for all character types."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

@dataclass
class CRFactors:
    """Factors that influence Challenge Rating."""
    hp: int
    ac: int
    damage_per_round: float
    attack_bonus: int
    save_dc: Optional[int] = None
    saving_throw_bonuses: Dict[str, int] = None
    resistances: List[str] = None
    immunities: List[str] = None
    vulnerabilities: List[str] = None
    special_abilities: List[Dict[str, Any]] = None
    legendary_actions: List[Dict[str, Any]] = None

class CRCalculator:
    """Calculates Challenge Rating for characters, NPCs, and monsters."""

    # CR tables from DMG
    HP_CR_TABLE = {
        1: 0.125, 7: 0.25, 15: 0.5, 23: 1, 33: 2, 45: 3, 60: 4,
        75: 5, 90: 6, 105: 7, 120: 8, 135: 9, 150: 10, 165: 11,
        180: 12, 195: 13, 210: 14, 225: 15, 240: 16, 255: 17,
        270: 18, 285: 19, 300: 20, 315: 21, 330: 22, 345: 23,
        360: 24, 375: 25, 390: 26, 405: 27, 420: 28, 435: 29, 450: 30
    }

    DAMAGE_CR_TABLE = {
        1: 0.125, 3: 0.25, 6: 0.5, 9: 1, 15: 2, 21: 3, 27: 4,
        33: 5, 39: 6, 45: 7, 51: 8, 57: 9, 63: 10, 69: 11,
        75: 12, 81: 13, 87: 14, 93: 15, 99: 16, 105: 17,
        111: 18, 117: 19, 123: 20, 129: 21, 135: 22, 141: 23,
        147: 24, 153: 25, 159: 26, 165: 27, 171: 28, 177: 29, 183: 30
    }

    AC_MODIFIER = {
        # Difference from base AC 13
        -3: -2, -2: -1, -1: -0.5, 0: 0,
        1: 0.5, 2: 1, 3: 1.5, 4: 2, 5: 2.5
    }

    ATTACK_MODIFIER = {
        # Difference from expected attack bonus
        -3: -2, -2: -1, -1: -0.5, 0: 0,
        1: 0.5, 2: 1, 3: 1.5, 4: 2, 5: 2.5
    }

    def calculate_cr(self, character: Dict[str, Any]) -> float:
        """Calculate Challenge Rating for any character type."""
        # Extract CR factors from character data
        factors = self._extract_cr_factors(character)
        
        # Calculate defensive and offensive CRs
        defensive_cr = self._calculate_defensive_cr(factors)
        offensive_cr = self._calculate_offensive_cr(factors)
        
        # Calculate base CR as average
        base_cr = (defensive_cr + offensive_cr) / 2
        
        # Apply special ability adjustments
        final_cr = self._adjust_for_special_abilities(base_cr, factors)
        
        return final_cr

    def _extract_cr_factors(self, character: Dict[str, Any]) -> CRFactors:
        """Extract relevant factors for CR calculation from character data."""
        # Calculate base HP
        base_hp = self._calculate_base_hp(character)
        
        # Get AC
        ac = character.get("armor_class", 10)
        
        # Calculate average damage per round
        dpr = self._calculate_damage_per_round(character)
        
        # Get attack bonus
        attack_bonus = self._calculate_attack_bonus(character)
        
        # Get save DC if spellcaster
        save_dc = character.get("spell_save_dc") if self._is_spellcaster(character) else None
        
        # Get saving throw bonuses
        saving_throws = self._extract_saving_throws(character)
        
        # Get damage modifiers
        resistances = character.get("damage_resistances", [])
        immunities = character.get("damage_immunities", [])
        vulnerabilities = character.get("damage_vulnerabilities", [])
        
        # Get special abilities
        special_abilities = character.get("special_abilities", [])
        legendary_actions = character.get("legendary_actions", [])
        
        return CRFactors(
            hp=base_hp,
            ac=ac,
            damage_per_round=dpr,
            attack_bonus=attack_bonus,
            save_dc=save_dc,
            saving_throw_bonuses=saving_throws,
            resistances=resistances,
            immunities=immunities,
            vulnerabilities=vulnerabilities,
            special_abilities=special_abilities,
            legendary_actions=legendary_actions
        )

    def _calculate_base_hp(self, character: Dict[str, Any]) -> int:
        """Calculate base HP including Constitution modifier."""
        # Get hit dice from class or monster type
        hit_die = self._get_hit_die(character)
        level = character.get("level", 1)
        
        # Get Constitution modifier
        con_mod = self._get_ability_modifier(character.get("constitution", 10))
        
        # Calculate base HP
        base_hp = hit_die + ((hit_die + con_mod) * (level - 1))
        
        return base_hp

    def _calculate_damage_per_round(self, character: Dict[str, Any]) -> float:
        """Calculate average damage per round over 3 rounds."""
        total_damage = 0
        
        # Add weapon attack damage
        weapon_damage = self._calculate_weapon_damage(character)
        total_damage += weapon_damage * 3  # 3 rounds
        
        # Add spell damage if applicable
        if self._is_spellcaster(character):
            spell_damage = self._calculate_spell_damage(character)
            total_damage += spell_damage  # Already averaged over 3 rounds
        
        # Add special ability damage
        ability_damage = self._calculate_ability_damage(character)
        total_damage += ability_damage  # Already averaged over 3 rounds
        
        return total_damage / 3  # Average per round

    def _calculate_defensive_cr(self, factors: CRFactors) -> float:
        """Calculate defensive CR based on HP, AC, and defensive abilities."""
        effective_hp = factors.hp
        
        # Adjust HP based on AC
        ac_diff = factors.ac - 13  # Base AC is 13
        if ac_diff != 0:
            hp_modifier = self.AC_MODIFIER.get(ac_diff, 0)
            effective_hp = int(effective_hp * (1 + hp_modifier))
        
        # Adjust for resistances/immunities
        effective_hp = self._adjust_hp_for_defenses(
            effective_hp, factors.resistances,
            factors.immunities, factors.vulnerabilities
        )
        
        # Look up base defensive CR
        defensive_cr = self._lookup_hp_cr(effective_hp)
        
        # Adjust for saving throws
        if factors.saving_throw_bonuses:
            defensive_cr = self._adjust_cr_for_saves(
                defensive_cr, factors.saving_throw_bonuses
            )
        
        return defensive_cr

    def _calculate_offensive_cr(self, factors: CRFactors) -> float:
        """Calculate offensive CR based on damage and attack bonus."""
        # Look up base offensive CR from damage
        offensive_cr = self._lookup_damage_cr(factors.damage_per_round)
        
        # Adjust for attack bonus/save DC
        if factors.save_dc:
            expected_dc = 8 + self._get_cr_prof_bonus(offensive_cr) + 3
            dc_diff = factors.save_dc - expected_dc
            if dc_diff != 0:
                offensive_cr += self.ATTACK_MODIFIER.get(dc_diff, 0)
        else:
            expected_bonus = self._get_cr_prof_bonus(offensive_cr) + 3
            bonus_diff = factors.attack_bonus - expected_bonus
            if bonus_diff != 0:
                offensive_cr += self.ATTACK_MODIFIER.get(bonus_diff, 0)
        
        return offensive_cr

    def _adjust_for_special_abilities(self, base_cr: float,
                                    factors: CRFactors) -> float:
        """Adjust CR for special abilities and legendary actions."""
        cr = base_cr
        
        # Adjust for special abilities
        if factors.special_abilities:
            for ability in factors.special_abilities:
                cr = self._adjust_cr_for_ability(cr, ability)
        
        # Adjust for legendary actions
        if factors.legendary_actions:
            cr = self._adjust_cr_for_legendary(cr, factors.legendary_actions)
        
        return cr

    def _lookup_hp_cr(self, hp: int) -> float:
        """Look up CR based on HP from DMG table."""
        for threshold, cr in sorted(self.HP_CR_TABLE.items()):
            if hp <= threshold:
                return cr
        return 30  # Maximum CR

    def _lookup_damage_cr(self, damage: float) -> float:
        """Look up CR based on damage from DMG table."""
        for threshold, cr in sorted(self.DAMAGE_CR_TABLE.items()):
            if damage <= threshold:
                return cr
        return 30  # Maximum CR

    def _get_cr_prof_bonus(self, cr: float) -> int:
        """Get proficiency bonus for a given CR."""
        return math.ceil(cr / 4) + 1

    def _adjust_hp_for_defenses(self, hp: int, resistances: List[str],
                               immunities: List[str],
                               vulnerabilities: List[str]) -> int:
        """Adjust effective HP based on damage resistances/immunities."""
        multiplier = 1.0
        
        # Common damage types that affect HP calculation
        common_damage_types = {
            "bludgeoning", "piercing", "slashing",  # Physical
            "fire", "cold", "lightning", "acid", "poison",  # Elemental
            "necrotic", "radiant"  # Energy
        }
        
        # Calculate resistance/immunity impact
        resistance_count = sum(1 for r in resistances if r in common_damage_types)
        immunity_count = sum(1 for i in immunities if i in common_damage_types)
        vulnerability_count = sum(1 for v in vulnerabilities if v in common_damage_types)
        
        # Apply modifiers
        if resistance_count > 0:
            multiplier += 0.25 * min(resistance_count, 3)  # Cap at 3 resistances
        if immunity_count > 0:
            multiplier += 0.5 * min(immunity_count, 2)  # Cap at 2 immunities
        if vulnerability_count > 0:
            multiplier -= 0.25 * vulnerability_count
        
        return int(hp * max(multiplier, 0.5))  # Minimum 50% of original HP

    def _adjust_cr_for_saves(self, cr: float,
                            save_bonuses: Dict[str, int]) -> float:
        """Adjust CR based on saving throw bonuses."""
        # Calculate average save bonus
        avg_bonus = sum(save_bonuses.values()) / len(save_bonuses)
        expected_bonus = self._get_cr_prof_bonus(cr)
        
        # Adjust CR based on difference
        diff = avg_bonus - expected_bonus
        if diff > 0:
            cr += diff * 0.25  # Small boost for good saves
        
        return cr

    def _adjust_cr_for_ability(self, cr: float,
                             ability: Dict[str, Any]) -> float:
        """Adjust CR based on special ability impact."""
        ability_type = ability.get("type", "")
        
        # Common ability adjustments
        adjustments = {
            "magic_resistance": 0.5,
            "regeneration": 1,
            "damage_transfer": 1,
            "spellcasting": 0.5,
            "multiattack": 0.5
        }
        
        if ability_type in adjustments:
            cr += adjustments[ability_type]
        
        return cr

    def _adjust_cr_for_legendary(self, cr: float,
                                legendary_actions: List[Dict[str, Any]]) -> float:
        """Adjust CR for legendary actions."""
        # Base adjustment for having legendary actions
        cr += 1
        
        # Additional adjustment based on number and power
        action_count = len(legendary_actions)
        if action_count >= 3:
            cr += 1
        
        # Check for particularly powerful legendary actions
        for action in legendary_actions:
            if action.get("damage_per_round", 0) > self._get_cr_prof_bonus(cr) * 4:
                cr += 0.5
        
        return cr

    def _is_spellcaster(self, character: Dict[str, Any]) -> bool:
        """Check if character has spellcasting abilities."""
        spellcasting_classes = {
            "wizard", "sorcerer", "warlock", "cleric", "druid", "bard",
            "paladin", "ranger", "artificer"
        }
        return any(cls.lower() in spellcasting_classes
                  for cls in character.get("classes", {}).keys())

    def _get_ability_modifier(self, score: int) -> int:
        """Calculate ability score modifier."""
        return (score - 10) // 2

    def _get_hit_die(self, character: Dict[str, Any]) -> int:
        """Get hit die size based on class or monster type."""
        hit_die_by_class = {
            "barbarian": 12,
            "fighter": 10, "paladin": 10, "ranger": 10,
            "cleric": 8, "druid": 8, "monk": 8, "rogue": 8, "warlock": 8,
            "sorcerer": 6, "wizard": 6
        }
        
        # Check character classes first
        classes = character.get("classes", {})
        if classes:
            primary_class = next(iter(classes)).lower()
            return hit_die_by_class.get(primary_class, 8)
        
        # Default for monsters based on size
        size_hit_die = {
            "tiny": 4,
            "small": 6,
            "medium": 8,
            "large": 10,
            "huge": 12,
            "gargantuan": 20
        }
        return size_hit_die.get(character.get("size", "medium").lower(), 8)
