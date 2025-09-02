"""Character factory for testing."""
from typing import Dict, Any, Optional
from uuid import uuid4


def create_character_data(
    name: Optional[str] = None,
    species: Optional[str] = None,
    character_class: Optional[str] = None,
    level: int = 1,
    background: Optional[str] = None,
    ability_scores: Optional[Dict[str, int]] = None,
    theme: Optional[str] = None
) -> Dict[str, Any]:
    """Create test character data."""
    character_classes = {character_class or "Fighter": level}
    used_ability_scores = ability_scores or {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8
    }

    # Calculate derived values
    base_ac = 10 + (used_ability_scores["dexterity"] - 10) // 2  # 10 + DEX modifier
    
    # Fighter gets d10 hit dice, add CON modifier
    base_hp = 10 + (used_ability_scores["constitution"] - 10) // 2

    # Level 1-4: +2, Level 5-8: +3, Level 9-12: +4, Level 13-16: +5, Level 17-20: +6
    prof_bonus = 2 + (level - 1) // 4

    # Base character data
    character_json = {
        "species": species or "Human",
        "character_classes": character_classes,
        "background": background or "Soldier",
        "level": level,
        "ability_scores": used_ability_scores,
        "equipment": [],
        "spells_known": [],
        "spells_prepared": [],
        "features": [],
        "racial_bonuses": None,
        "warnings": None,
        "hit_points": base_hp,
        "armor_class": base_ac,
        "proficiency_bonus": prof_bonus,
        "spell_save_dc": None,
        "spellcasting_ability": None
    }

    return {
        "id": str(uuid4()),
        "name": name or "Test Character",
        "user_id": str(uuid4()),
        "campaign_id": str(uuid4()),
        "theme": theme or "traditional",
        "character_data": character_json,
        "is_active": True
    }
