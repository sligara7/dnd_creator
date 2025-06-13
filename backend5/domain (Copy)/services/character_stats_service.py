from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

from ...core.entities.character import Character
from ..rules.combat_rules import CombatRules
from ..rules.equipment_rules import EquipmentRules

logger = logging.getLogger(__name__)

@dataclass
class CharacterStatistics:
    """Data class containing comprehensive character statistics."""
    
    # Combat Statistics
    armor_class: int
    hit_points: int
    initiative: int
    speed: int
    
    # Attack Statistics
    melee_attack_bonus: int
    ranged_attack_bonus: int
    spell_attack_bonus: int
    spell_save_dc: int
    
    # Defensive Statistics
    saving_throws: Dict[str, int]
    passive_scores: Dict[str, int]
    
    # Skill Statistics
    skill_modifiers: Dict[str, int]
    
    # Proficiency Summary
    proficiencies: Dict[str, List[str]]
    
    # Resource Summary
    spell_slots: Dict[int, int]
    class_resources: Dict[str, Any]

class CharacterStatsService:
    """
    Domain service for calculating comprehensive character statistics.
    
    This service handles complex statistical calculations that require
    business logic and rule interactions.
    """
    
    def __init__(self):
        self.combat_rules = CombatRules()
        self.equipment_rules = EquipmentRules()
    
    def calculate_comprehensive_stats(self, character: Character) -> CharacterStatistics:
        """
        Calculate all character statistics.
        
        Args:
            character: Character to analyze
            
        Returns:
            CharacterStatistics: Complete statistical analysis
        """
        return CharacterStatistics(
            # Combat stats
            armor_class=self._calculate_armor_class(character),
            hit_points=self._calculate_hit_points(character),
            initiative=character.initiative_modifier,
            speed=self._calculate_speed(character),
            
            # Attack stats
            melee_attack_bonus=self._calculate_melee_attack_bonus(character),
            ranged_attack_bonus=self._calculate_ranged_attack_bonus(character),
            spell_attack_bonus=character.get_spell_attack_bonus(),
            spell_save_dc=character.get_spell_save_dc(),
            
            # Defensive stats
            saving_throws=self._calculate_all_saving_throws(character),
            passive_scores=self._calculate_passive_scores(character),
            
            # Skills
            skill_modifiers=self._calculate_all_skill_modifiers(character),
            
            # Proficiencies
            proficiencies=self._summarize_proficiencies(character),
            
            # Resources
            spell_slots=character.spell_slots.copy(),
            class_resources=self._calculate_class_resources(character)
        )
    
    def calculate_combat_statistics(self, character: Character) -> Dict[str, Any]:
        """Calculate combat-focused statistics."""
        return {
            "armor_class": self._calculate_armor_class(character),
            "hit_points": {
                "current": character.current_hit_points,
                "maximum": self._calculate_hit_points(character),
                "temporary": character.temporary_hit_points
            },
            "initiative": character.initiative_modifier,
            "speed": self._calculate_speed(character),
            "attacks": self._calculate_attack_options(character),
            "saving_throws": self._calculate_all_saving_throws(character),
            "defenses": self._calculate_damage_resistances(character)
        }
    
    def calculate_skill_analysis(self, character: Character) -> Dict[str, Any]:
        """Analyze character's skill capabilities."""
        skill_mods = self._calculate_all_skill_modifiers(character)
        
        return {
            "skill_modifiers": skill_mods,
            "passive_scores": self._calculate_passive_scores(character),
            "expertise_skills": self._get_expertise_skills(character),
            "proficient_skills": self._get_proficient_skills(character),
            "skill_rankings": self._rank_skills_by_modifier(skill_mods),
            "strongest_abilities": self._get_strongest_abilities(character)
        }
    
    def calculate_spellcasting_analysis(self, character: Character) -> Dict[str, Any]:
        """Analyze character's spellcasting capabilities."""
        if not character.is_spellcaster:
            return {"is_spellcaster": False}
        
        return {
            "is_spellcaster": True,
            "spellcasting_ability": character.spellcasting_ability,
            "spell_attack_bonus": character.get_spell_attack_bonus(),
            "spell_save_dc": character.get_spell_save_dc(),
            "spell_slots": character.spell_slots.copy(),
            "spells_known": character.spells_known.copy(),
            "ritual_casting": character.ritual_casting_classes.copy(),
            "caster_level": self._calculate_caster_level(character),
            "spell_schools": self._analyze_spell_schools(character)
        }
    
    def compare_characters(self, char1: Character, char2: Character) -> Dict[str, Any]:
        """Compare two characters statistically."""
        stats1 = self.calculate_comprehensive_stats(char1)
        stats2 = self.calculate_comprehensive_stats(char2)
        
        return {
            "character_1": {"name": char1.name, "stats": stats1},
            "character_2": {"name": char2.name, "stats": stats2},
            "comparisons": {
                "combat": self._compare_combat_stats(stats1, stats2),
                "skills": self._compare_skill_stats(stats1, stats2),
                "spellcasting": self._compare_spellcasting_stats(char1, char2)
            }
        }
    
    # === Private Helper Methods ===
    
    def _calculate_armor_class(self, character: Character) -> int:
        """Calculate comprehensive armor class including equipment."""
        # Start with base AC
        base_ac = character.armor_class_base
        
        # Apply armor bonuses
        armor_bonus = self._get_armor_ac_bonus(character)
        shield_bonus = self._get_shield_ac_bonus(character)
        
        # Apply magical bonuses
        magic_bonus = self._get_magical_ac_bonus(character)
        
        # Apply class features (e.g., Unarmored Defense)
        class_bonus = self._get_class_ac_bonus(character)
        
        return max(base_ac + armor_bonus + shield_bonus + magic_bonus, class_bonus)
    
    def _calculate_hit_points(self, character: Character) -> int:
        """Calculate maximum hit points."""
        total_hp = 0
        con_mod = character.get_ability_modifier("constitution")
        
        for class_name, level in character.character_classes.items():
            hit_die = self._get_class_hit_die(class_name)
            
            if class_name == character.primary_class:
                # First level gets max hit die
                total_hp += hit_die + con_mod
                # Remaining levels get average
                total_hp += (level - 1) * ((hit_die // 2) + 1 + con_mod)
            else:
                # Multiclass levels get average
                total_hp += level * ((hit_die // 2) + 1 + con_mod)
        
        # Apply feats and other bonuses
        total_hp += self._get_hp_bonuses(character)
        
        return max(1, total_hp)
    
    def _calculate_all_saving_throws(self, character: Character) -> Dict[str, int]:
        """Calculate all saving throw modifiers."""
        saving_throws = {}
        
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            saving_throws[ability] = character.get_saving_throw_modifier(ability)
        
        return saving_throws
    
    def _calculate_all_skill_modifiers(self, character: Character) -> Dict[str, int]:
        """Calculate all skill modifiers."""
        skills = [
            "acrobatics", "animal_handling", "arcana", "athletics", "deception",
            "history", "insight", "intimidation", "investigation", "medicine",
            "nature", "perception", "performance", "persuasion", "religion",
            "sleight_of_hand", "stealth", "survival"
        ]
        
        return {skill: character.get_skill_modifier(skill) for skill in skills}
    
    def _calculate_passive_scores(self, character: Character) -> Dict[str, int]:
        """Calculate passive skill scores."""
        return {
            "perception": character.passive_perception,
            "investigation": character.passive_investigation,
            "insight": character.passive_insight
        }
    
    def _calculate_attack_options(self, character: Character) -> List[Dict[str, Any]]:
        """Calculate available attack options."""
        attacks = []
        
        # Weapon attacks
        for weapon in self._get_equipped_weapons(character):
            attacks.append(self._calculate_weapon_attack(character, weapon))
        
        # Spell attacks
        if character.is_spellcaster:
            attacks.extend(self._calculate_spell_attacks(character))
        
        return attacks
    
    def _rank_skills_by_modifier(self, skill_mods: Dict[str, int]) -> List[tuple]:
        """Rank skills by modifier value."""
        return sorted(skill_mods.items(), key=lambda x: x[1], reverse=True)
    
    def _get_strongest_abilities(self, character: Character) -> List[tuple]:
        """Get abilities ranked by score."""
        abilities = []
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            abilities.append((ability, score))
        
        return sorted(abilities, key=lambda x: x[1], reverse=True)