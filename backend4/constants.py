class RuleConstants:
    """Centralized constants for D&D 2024 rules."""
    
    # Ability Score Rules
    ABILITY_SCORE_MIN = 3
    ABILITY_SCORE_MAX = 30
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    
    # Character Level Rules
    MIN_LEVEL = 1
    MAX_LEVEL = 20
    
    # XP thresholds, proficiency bonuses, etc.
    XP_BY_LEVEL = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Base content sets
    BASE_CLASSES = {
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    }
    
    # Class data
    HIT_DIE_BY_CLASS = {
        "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
        "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
        "Artificer": 8, "Wizard": 6, "Sorcerer": 6
    }
    
    MULTICLASS_REQUIREMENTS = {
        "Artificer": {"intelligence": 13},
        "Barbarian": {"strength": 13},
        "Bard": {"charisma": 13},
        "Cleric": {"wisdom": 13},
        "Druid": {"wisdom": 13},
        "Fighter": {"strength": 13, "dexterity": 13},  # Either
        "Monk": {"dexterity": 13, "wisdom": 13},
        "Paladin": {"strength": 13, "charisma": 13},
        "Ranger": {"dexterity": 13, "wisdom": 13},
        "Rogue": {"dexterity": 13},
        "Sorcerer": {"charisma": 13},
        "Warlock": {"charisma": 13},
        "Wizard": {"intelligence": 13}
    }

    # remember new classes can be created, so the multiclass_requirements need to be flexible to allow for new classes