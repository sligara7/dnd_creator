from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CharacterStats:
    """
    DEPENDENT VARIABLES - Calculated from other variables.
    
    These variables are computed based on core character data and current state.
    They should be recalculated whenever their dependencies change.
    """
    
    def __init__(self, core: 'CharacterCore', state: 'CharacterState'):
        self.core = core
        self.state = state
        
        # Cached calculated values
        self._proficiency_bonus: Optional[int] = None
        self._armor_class: Optional[int] = None
        self._max_hit_points: Optional[int] = None
        self._initiative: Optional[int] = None
        self._spell_save_dc: Optional[int] = None
        self._spell_attack_bonus: Optional[int] = None
        self._passive_perception: Optional[int] = None
        self._passive_investigation: Optional[int] = None
        self._passive_insight: Optional[int] = None
        
        # Available actions (computed based on class features, etc.)
        self._available_actions: Dict[str, Dict[str, Any]] = {}
        self._available_reactions: Dict[str, Dict[str, Any]] = {}
        
        # Dependencies tracking for cache invalidation
        self._last_core_hash: Optional[int] = None
        self._last_state_hash: Optional[int] = None
    
    def invalidate_cache(self) -> None:
        """Invalidate all cached calculations."""
        self._proficiency_bonus = None
        self._armor_class = None
        self._max_hit_points = None
        self._initiative = None
        self._spell_save_dc = None
        self._spell_attack_bonus = None
        self._passive_perception = None
        self._passive_investigation = None
        self._passive_insight = None
        self._available_actions = {}
        self._available_reactions = {}
    
    def _needs_recalculation(self) -> bool:
        """Check if recalculation is needed based on dependencies."""
        # Simple hash-based dependency tracking
        core_hash = hash(str(self.core.to_dict()))
        state_hash = hash(str(self.state.to_dict()))
        
        if (self._last_core_hash != core_hash or 
            self._last_state_hash != state_hash):
            self._last_core_hash = core_hash
            self._last_state_hash = state_hash
            return True
        return False
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        if self._proficiency_bonus is None or self._needs_recalculation():
            level = self.core.total_level
            self._proficiency_bonus = 2 + ((level - 1) // 4)
        return self._proficiency_bonus
    
    @property
    def armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        if self._armor_class is None or self._needs_recalculation():
            self._armor_class = self._calculate_armor_class()
        return self._armor_class
    
    @property
    def max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if self._max_hit_points is None or self._needs_recalculation():
            self._max_hit_points = self._calculate_max_hit_points()
        return self._max_hit_points
    
    @property
    def initiative(self) -> int:
        """Calculate initiative bonus."""
        if self._initiative is None or self._needs_recalculation():
            self._initiative = self._calculate_initiative()
        return self._initiative
    
    @property
    def spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if self._spell_save_dc is None or self._needs_recalculation():
            self._spell_save_dc = self._calculate_spell_save_dc()
        return self._spell_save_dc
    
    @property
    def spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if self._spell_attack_bonus is None or self._needs_recalculation():
            self._spell_attack_bonus = self._calculate_spell_attack_bonus()
        return self._spell_attack_bonus
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive Perception score."""
        if self._passive_perception is None or self._needs_recalculation():
            self._passive_perception = self._calculate_passive_perception()
        return self._passive_perception
    
    def _calculate_armor_class(self) -> int:
        """Internal method to calculate armor class."""
        base_ac = 10
        dex_mod = self.core.dexterity.modifier
        
        # Check for worn armor
        if self.state.armor:
            armor_type = self.state.armor.lower()
            
            # Light armor
            if any(a in armor_type for a in ["padded", "leather"]):
                if "studded" in armor_type:
                    base_ac = 12 + dex_mod
                else:
                    base_ac = 11 + dex_mod
            
            # Medium armor
            elif any(a in armor_type for a in ["chain shirt", "scale", "breastplate", "half plate"]):
                if "chain shirt" in armor_type:
                    base_ac = 13 + min(dex_mod, 2)
                elif "scale" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "breastplate" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "half plate" in armor_type:
                    base_ac = 15 + min(dex_mod, 2)
            
            # Heavy armor
            elif any(a in armor_type for a in ["ring mail", "chain mail", "splint", "plate"]):
                if "ring mail" in armor_type:
                    base_ac = 14
                elif "chain mail" in armor_type:
                    base_ac = 16
                elif "splint" in armor_type:
                    base_ac = 17
                elif "plate" in armor_type:
                    base_ac = 18
        else:
            # Unarmored Defense
            if "Barbarian" in self.core.character_classes:
                con_mod = self.core.constitution.modifier
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
            
            if "Monk" in self.core.character_classes:
                wis_mod = self.core.wisdom.modifier
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self.state.shield:
            base_ac += 2
        
        return base_ac
    
    def _calculate_max_hit_points(self) -> int:
        """Internal method to calculate maximum hit points."""
        if not self.core.character_classes:
            return 1
        
        con_mod = self.core.constitution.modifier
        total = 0
        
        hit_die_sizes = {
            "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
            "Wizard": 6, "Sorcerer": 6
        }
        
        for class_name, level in self.core.character_classes.items():
            if level <= 0:
                continue
                
            hit_die = hit_die_sizes.get(class_name, 8)
            
            # First level is max hit die + CON
            if class_name == self.core.primary_class:
                total += hit_die + con_mod
                remaining_levels = level - 1
            else:
                remaining_levels = level
            
            # Average for remaining levels
            total += remaining_levels * ((hit_die // 2) + 1 + con_mod)
        
        # Add modifiers from state
        total += self.state.hit_point_maximum_modifier
        
        return max(1, total)
    
    def _calculate_initiative(self) -> int:
        """Internal method to calculate initiative."""
        dex_mod = self.core.dexterity.modifier
        bonus = 0
        
        # Check for feats and features
        if "Alert" in self.core.feats:
            bonus += 5
        
        if "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:  # Jack of All Trades
                bonus += self.proficiency_bonus // 2
        
        return dex_mod + bonus
    
    def _calculate_spell_save_dc(self) -> int:
        """Internal method to calculate spell save DC."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return 8 + self.proficiency_bonus + ability_mod
    
    def _calculate_spell_attack_bonus(self) -> int:
        """Internal method to calculate spell attack bonus."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return self.proficiency_bonus + ability_mod
    
    def _calculate_passive_perception(self) -> int:
        """Internal method to calculate passive Perception."""
        wis_mod = self.core.wisdom.modifier
        prof_bonus = 0
        
        perception_prof = self.core.skill_proficiencies.get("Perception", ProficiencyLevel.NONE)
        if perception_prof == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif perception_prof == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        feat_bonus = 5 if "Observant" in self.core.feats else 0
        
        return 10 + wis_mod + prof_bonus + feat_bonus
    
    def calculate_skill_bonus(self, skill_name: str) -> int:
        """Calculate bonus for a specific skill check."""
        skill_abilities = {
            "Athletics": "strength", "Acrobatics": "dexterity",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity",
            "Arcana": "intelligence", "History": "intelligence",
            "Investigation": "intelligence", "Nature": "intelligence", "Religion": "intelligence",
            "Animal Handling": "wisdom", "Insight": "wisdom", "Medicine": "wisdom",
            "Perception": "wisdom", "Survival": "wisdom",
            "Deception": "charisma", "Intimidation": "charisma",
            "Performance": "charisma", "Persuasion": "charisma"
        }
        
        if skill_name not in skill_abilities:
            return 0
        
        ability = skill_abilities[skill_name]
        ability_mod = self.core.get_ability_score(ability).modifier
        
        # Check proficiency
        prof_level = self.core.skill_proficiencies.get(skill_name, ProficiencyLevel.NONE)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Jack of All Trades for non-proficient skills
        if prof_level == ProficiencyLevel.NONE and "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:
                prof_bonus = self.proficiency_bonus // 2
        
        return ability_mod + prof_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calculated stats to dictionary."""
        return {
            "proficiency_bonus": self.proficiency_bonus,
            "armor_class": self.armor_class,
            "max_hit_points": self.max_hit_points,
            "initiative": self.initiative,
            "spell_save_dc": self.spell_save_dc,
            "spell_attack_bonus": self.spell_attack_bonus,
            "passive_perception": self.passive_perception,
            "available_actions": self._available_actions,
            "available_reactions": self._available_reactions
        }