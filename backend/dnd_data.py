"""
D&D 5e 2024 Official Data

This module contains all official D&D 5e 2024 data including spells, weapons, armor,
equipment, and other game content. This data is used to prioritize official content
over custom content during character creation.

Data Sources:
- D&D 5e 2024 Player's Handbook
- D&D 5e 2024 Rules Updates
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# D&D 5e SPELL DATABASE - PRIORITIZE EXISTING SPELLS
# ============================================================================

# Comprehensive D&D 5e spell list organized by level and school
# Updated with complete spell list from D&D 5e 2024
DND_SPELL_DATABASE = {
    "cantrips": {
        "evocation": ["Acid Splash", "Fire Bolt", "Ray of Frost", "Sacred Flame", "Shocking Grasp", 
                     "Eldritch Blast", "Sorcerous Burst", "Starry Wisp", "True Strike"],
        "conjuration": ["Mage Hand", "Poison Spray", "Produce Flame"],
        "transmutation": ["Druidcraft", "Mending", "Prestidigitation", "Thaumaturgy", "Shillelagh"],
        "illusion": ["Minor Illusion", "Dancing Lights"],
        "necromancy": ["Chill Touch", "Spare the Dying"],
        "enchantment": ["Vicious Mockery"],
        "divination": ["Guidance"],
        "abjuration": ["Resistance"]
    },
    "level_1": {
        "abjuration": ["Alarm", "Mage Armor", "Protection from Evil and Good", "Sanctuary", "Shield", "Shield of Faith"],
        "conjuration": ["Find Familiar", "Floating Disk", "Grease", "Unseen Servant", "Goodberry"],
        "divination": ["Comprehend Languages", "Detect Evil and Good", "Detect Magic", "Detect Poison and Disease", "Identify"],
        "enchantment": ["Bane", "Bless", "Charm Person", "Command", "Dissonant Whispers", "Heroism", "Sleep", "Animal Friendship"],
        "evocation": ["Burning Hands", "Cure Wounds", "Divine Favor", "Guiding Bolt", "Healing Word", "Magic Missile", "Thunderwave", "Divine Smite"],
        "illusion": ["Color Spray", "Disguise Self", "Illusory Script", "Silent Image"],
        "necromancy": ["False Life", "Inflict Wounds", "Ray of Sickness"],
        "transmutation": ["Expeditious Retreat", "Feather Fall", "Jump", "Longstrider", "Speak with Animals", "Ensnaring Strike"]
    },
    "level_2": {
        "abjuration": ["Arcane Lock", "Lesser Restoration", "Protection from Poison"],
        "conjuration": ["Cloud of Daggers", "Find Steed", "Misty Step", "Spiritual Weapon", "Web", "Fog Cloud"],
        "divination": ["Augury", "Detect Thoughts", "Find Traps", "Locate Animals or Plants", "Locate Object", "See Invisibility"],
        "enchantment": ["Calm Emotions", "Enthrall", "Hold Person", "Suggestion"],
        "evocation": ["Acid Arrow", "Continual Flame", "Darkness", "Flaming Sphere", "Gust of Wind", "Heat Metal", "Magic Weapon", "Prayer of Healing", "Scorching Ray", "Shatter", "Moonbeam"],
        "illusion": ["Blur", "Invisibility", "Magic Mouth", "Mirror Image", "Pass without Trace"],
        "necromancy": ["Blindness Deafness", "Gentle Repose", "Ray of Enfeeblement"],
        "transmutation": ["Aid", "Alter Self", "Barkskin", "Darkvision", "Enhance Ability", "Enlarge Reduce", "Knock", "Levitate", "Rope Trick", "Spider Climb"]
    },
    "level_3": {
        "abjuration": ["Counterspell", "Dispel Magic", "Magic Circle", "Nondetection", "Protection from Energy", "Remove Curse"],
        "conjuration": ["Conjure Animals", "Create Food and Water", "Sleet Storm", "Spirit Guardians", "Stinking Cloud", "Conjure Woodland Beings"],
        "divination": ["Clairvoyance", "Speak with Dead", "Tongues"],
        "enchantment": ["Bestow Curse", "Fear", "Hypnotic Pattern"],
        "evocation": ["Call Lightning", "Daylight", "Fireball", "Lightning Bolt", "Mass Healing Word", "Flame Strike"],
        "illusion": ["Major Image"],
        "necromancy": ["Animate Dead", "Vampiric Touch"],
        "transmutation": ["Fly", "Gaseous Form", "Haste", "Meld into Stone", "Plant Growth", "Slow", "Water Breathing", "Water Walk"]
    },
    "level_4": {
        "abjuration": ["Banishment", "Death Ward", "Freedom of Movement", "Stoneskin"],
        "conjuration": ["Conjure Minor Elementals", "Dimension Door", "Faithful Hound", "Wall of Fire"],
        "divination": ["Arcane Eye", "Divination", "Locate Creature"],
        "enchantment": ["Charm Monster", "Compulsion", "Confusion", "Dominate Beast"],
        "evocation": ["Fire Shield", "Guardian of Faith", "Ice Storm"],
        "illusion": ["Greater Invisibility", "Hallucinatory Terrain", "Phantasmal Killer"],
        "necromancy": ["Blight"],
        "transmutation": ["Control Water", "Fabricate", "Giant Insect", "Polymorph", "Stone Shape"]
    },
    "level_5": {
        "abjuration": ["Antilife Shell", "Dispel Evil and Good", "Greater Restoration"],
        "conjuration": ["Cloudkill", "Conjure Elemental", "Teleportation Circle", "Wall of Stone"],
        "divination": ["Commune", "Contact Other Plane", "Legend Lore", "Scrying", "Commune with Nature"],
        "enchantment": ["Dominate Person", "Geas", "Hold Monster", "Mass Suggestion", "Modify Memory"],
        "evocation": ["Cone of Cold", "Flame Strike", "Insect Plague", "Mass Cure Wounds"],
        "illusion": ["Dream", "Mislead", "Seeming"],
        "necromancy": ["Contagion", "Raise Dead"],
        "transmutation": ["Animate Objects", "Awaken", "Passwall", "Reincarnate", "Telekinesis"]
    },
    "level_6": {
        "abjuration": ["Forbiddance", "Globe of Invulnerability", "Guards and Wards"],
        "conjuration": ["Conjure Fey", "Planar Ally", "Wall of Ice", "Wall of Thorns"],
        "divination": ["Find the Path", "True Seeing"],
        "enchantment": ["Irresistible Dance"],
        "evocation": ["Chain Lightning", "Disintegrate", "Freezing Sphere", "Harm", "Heal", "Sunbeam"],
        "illusion": ["Programmed Illusion"],
        "necromancy": ["Circle of Death", "Create Undead", "Eyebite"],
        "transmutation": ["Flesh to Stone", "Move Earth", "Wind Walk"]
    },
    "level_7": {
        "abjuration": ["Forcecage"],
        "conjuration": ["Magnificent Mansion", "Plane Shift"],
        "divination": [],
        "enchantment": [],
        "evocation": ["Delayed Blast Fireball", "Fire Storm", "Prismatic Spray"],
        "illusion": ["Mirage Arcane", "Project Image"],
        "necromancy": ["Finger of Death"],
        "transmutation": ["Etherealness", "Regenerate", "Reverse Gravity"]
    },
    "level_8": {
        "abjuration": ["Antimagic Field", "Mind Blank"],
        "conjuration": ["Incendiary Cloud", "Maze"],
        "divination": [],
        "enchantment": ["Dominate Monster", "Power Word Stun"],
        "evocation": ["Earthquake", "Sunburst"],
        "illusion": [],
        "necromancy": ["Clone"],
        "transmutation": ["Animal Shapes", "Control Weather"]
    },
    "level_9": {
        "abjuration": ["Imprisonment", "Prismatic Wall"],
        "conjuration": ["Gate", "Storm of Vengeance"],
        "divination": ["Foresight"],
        "enchantment": ["Power Word Kill", "Weird"],
        "evocation": ["Mass Heal", "Meteor Swarm"],
        "illusion": [],
        "necromancy": ["Astral Projection", "True Resurrection"],
        "transmutation": ["Shapechange", "Time Stop", "True Polymorph", "Wish"]
    }
}

# Class to spell list mapping for D&D 5e 2024
CLASS_SPELL_LISTS = {
    "Wizard": {
        "schools": ["abjuration", "conjuration", "divination", "enchantment", "evocation", "illusion", "necromancy", "transmutation"],
        "restrictions": None
    },
    "Sorcerer": {
        "schools": ["evocation", "transmutation", "enchantment", "illusion"],
        "restrictions": "Prefers damage and utility spells"
    },
    "Warlock": {
        "schools": ["enchantment", "evocation", "illusion", "necromancy"],
        "restrictions": "Eldritch-themed spells"
    },
    "Cleric": {
        "schools": ["abjuration", "divination", "evocation", "necromancy"],
        "restrictions": "Divine magic focused on healing and protection"
    },
    "Druid": {
        "schools": ["conjuration", "transmutation", "evocation", "divination"],
        "restrictions": "Nature-themed spells only"
    },
    "Bard": {
        "schools": ["enchantment", "illusion", "divination", "transmutation"],
        "restrictions": "Social and utility spells"
    },
    "Paladin": {
        "schools": ["abjuration", "evocation", "divination"],
        "restrictions": "Divine smites and protective magic"
    },
    "Ranger": {
        "schools": ["conjuration", "divination", "transmutation"],
        "restrictions": "Nature and tracking magic"
    },
    "Artificer": {
        "schools": ["abjuration", "transmutation", "conjuration"],
        "restrictions": "Magical item and construct themes"
    }
}

# Complete list of D&D 5e spells for lookup purposes
COMPLETE_SPELL_LIST = [
    # Cantrips
    "Acid Splash", "Fire Bolt", "Ray of Frost", "Sacred Flame", "Shocking Grasp", 
    "Eldritch Blast", "Sorcerous Burst", "Starry Wisp", "True Strike",
    "Mage Hand", "Poison Spray", "Produce Flame",
    "Druidcraft", "Mending", "Prestidigitation", "Thaumaturgy", "Shillelagh",
    "Minor Illusion", "Dancing Lights",
    "Chill Touch", "Spare the Dying",
    "Vicious Mockery",
    "Guidance",
    "Resistance",
    
    # Level 1
    "Alarm", "Mage Armor", "Protection from Evil and Good", "Sanctuary", "Shield", "Shield of Faith",
    "Find Familiar", "Floating Disk", "Grease", "Unseen Servant", "Goodberry",
    "Comprehend Languages", "Detect Evil and Good", "Detect Magic", "Detect Poison and Disease", "Identify",
    "Bane", "Bless", "Charm Person", "Command", "Dissonant Whispers", "Heroism", "Sleep", "Animal Friendship",
    "Burning Hands", "Cure Wounds", "Divine Favor", "Guiding Bolt", "Healing Word", "Magic Missile", "Thunderwave", "Divine Smite",
    "Color Spray", "Disguise Self", "Illusory Script", "Silent Image",
    "False Life", "Inflict Wounds", "Ray of Sickness",
    "Expeditious Retreat", "Feather Fall", "Jump", "Longstrider", "Speak with Animals", "Ensnaring Strike",
    
    # Level 2
    "Arcane Lock", "Lesser Restoration", "Protection from Poison",
    "Cloud of Daggers", "Find Steed", "Misty Step", "Spiritual Weapon", "Web", "Fog Cloud",
    "Augury", "Detect Thoughts", "Find Traps", "Locate Animals or Plants", "Locate Object", "See Invisibility",
    "Calm Emotions", "Enthrall", "Hold Person", "Suggestion",
    "Acid Arrow", "Continual Flame", "Darkness", "Flaming Sphere", "Gust of Wind", "Heat Metal", "Magic Weapon", "Prayer of Healing", "Scorching Ray", "Shatter", "Moonbeam",
    "Blur", "Invisibility", "Magic Mouth", "Mirror Image", "Pass without Trace",
    "Blindness Deafness", "Gentle Repose", "Ray of Enfeeblement",
    "Aid", "Alter Self", "Barkskin", "Darkvision", "Enhance Ability", "Enlarge Reduce", "Knock", "Levitate", "Rope Trick", "Spider Climb",
    
    # Level 3
    "Counterspell", "Dispel Magic", "Magic Circle", "Nondetection", "Protection from Energy", "Remove Curse",
    "Conjure Animals", "Create Food and Water", "Sleet Storm", "Spirit Guardians", "Stinking Cloud", "Conjure Woodland Beings",
    "Clairvoyance", "Speak with Dead", "Tongues",
    "Bestow Curse", "Fear", "Hypnotic Pattern",
    "Call Lightning", "Daylight", "Fireball", "Lightning Bolt", "Mass Healing Word", "Flame Strike",
    "Major Image",
    "Animate Dead", "Vampiric Touch",
    "Fly", "Gaseous Form", "Haste", "Meld into Stone", "Plant Growth", "Slow", "Water Breathing", "Water Walk",
    
    # Level 4
    "Banishment", "Death Ward", "Freedom of Movement", "Stoneskin",
    "Conjure Minor Elementals", "Dimension Door", "Faithful Hound", "Wall of Fire",
    "Arcane Eye", "Divination", "Locate Creature",
    "Charm Monster", "Compulsion", "Confusion", "Dominate Beast",
    "Fire Shield", "Guardian of Faith", "Ice Storm",
    "Greater Invisibility", "Hallucinatory Terrain", "Phantasmal Killer",
    "Blight",
    "Control Water", "Fabricate", "Giant Insect", "Polymorph", "Stone Shape",
    
    # Level 5
    "Antilife Shell", "Dispel Evil and Good", "Greater Restoration",
    "Cloudkill", "Conjure Elemental", "Teleportation Circle", "Wall of Stone",
    "Commune", "Contact Other Plane", "Legend Lore", "Scrying", "Commune with Nature",
    "Dominate Person", "Geas", "Hold Monster", "Mass Suggestion", "Modify Memory",
    "Cone of Cold", "Flame Strike", "Insect Plague", "Mass Cure Wounds",
    "Dream", "Mislead", "Seeming",
    "Contagion", "Raise Dead",
    "Animate Objects", "Awaken", "Passwall", "Reincarnate", "Telekinesis",
    
    # Level 6
    "Forbiddance", "Globe of Invulnerability", "Guards and Wards",
    "Conjure Fey", "Planar Ally", "Wall of Ice", "Wall of Thorns",
    "Find the Path", "True Seeing",
    "Irresistible Dance",
    "Chain Lightning", "Disintegrate", "Freezing Sphere", "Harm", "Heal", "Sunbeam",
    "Programmed Illusion",
    "Circle of Death", "Create Undead", "Eyebite",
    "Flesh to Stone", "Move Earth", "Wind Walk",
    
    # Level 7
    "Forcecage",
    "Magnificent Mansion", "Plane Shift",
    "Delayed Blast Fireball", "Fire Storm", "Prismatic Spray",
    "Mirage Arcane", "Project Image",
    "Finger of Death",
    "Etherealness", "Regenerate", "Reverse Gravity",
    
    # Level 8
    "Antimagic Field", "Mind Blank",
    "Incendiary Cloud", "Maze",
    "Dominate Monster", "Power Word Stun",
    "Earthquake", "Sunburst",
    "Animal Shapes", "Control Weather",
    
    # Level 9
    "Imprisonment", "Prismatic Wall",
    "Gate", "Storm of Vengeance",
    "Foresight",
    "Power Word Kill", "Weird",
    "Mass Heal", "Meteor Swarm",
    "Astral Projection", "True Resurrection",
    "Shapechange", "Time Stop", "True Polymorph", "Wish"
]

# Create a quick lookup for spell names (case-insensitive)
SPELL_LOOKUP = {spell.lower(): spell for spell in COMPLETE_SPELL_LIST}

# ============================================================================
# D&D 5e WEAPON DATABASE - PRIORITIZE EXISTING WEAPONS
# ============================================================================

# Complete D&D 5e 2024 weapon database with all properties, mastery, costs, and weights
DND_WEAPON_DATABASE = {
    "simple_melee": {
        "Club": {
            "damage": "1d4",
            "damage_type": "bludgeoning",
            "properties": ["Light"],
            "mastery": "Slow",
            "weight": 2.0,
            "cost": "1 SP",
            "category": "Simple",
            "type": "Melee"
        },
        "Dagger": {
            "damage": "1d4",
            "damage_type": "piercing",
            "properties": ["Finesse", "Light", "Thrown (Range 20/60)"],
            "mastery": "Nick",
            "weight": 1.0,
            "cost": "2 GP",
            "category": "Simple",
            "type": "Melee"
        },
        "Greatclub": {
            "damage": "1d8",
            "damage_type": "bludgeoning",
            "properties": ["Two-Handed"],
            "mastery": "Push",
            "weight": 10.0,
            "cost": "2 SP",
            "category": "Simple",
            "type": "Melee"
        },
        "Handaxe": {
            "damage": "1d6",
            "damage_type": "slashing",
            "properties": ["Light", "Thrown (Range 20/60)"],
            "mastery": "Vex",
            "weight": 2.0,
            "cost": "5 GP",
            "category": "Simple",
            "type": "Melee"
        },
        "Javelin": {
            "damage": "1d6",
            "damage_type": "piercing",
            "properties": ["Thrown (Range 30/120)"],
            "mastery": "Slow",
            "weight": 2.0,
            "cost": "5 SP",
            "category": "Simple",
            "type": "Melee"
        },
        "Light Hammer": {
            "damage": "1d4",
            "damage_type": "bludgeoning",
            "properties": ["Light", "Thrown (Range 20/60)"],
            "mastery": "Nick",
            "weight": 2.0,
            "cost": "2 GP",
            "category": "Simple",
            "type": "Melee"
        },
        "Mace": {
            "damage": "1d6",
            "damage_type": "bludgeoning",
            "properties": [],
            "mastery": "Sap",
            "weight": 4.0,
            "cost": "5 GP",
            "category": "Simple",
            "type": "Melee"
        },
        "Quarterstaff": {
            "damage": "1d6",
            "damage_type": "bludgeoning",
            "properties": ["Versatile (1d8)"],
            "mastery": "Topple",
            "weight": 4.0,
            "cost": "2 SP",
            "category": "Simple",
            "type": "Melee"
        },
        "Sickle": {
            "damage": "1d4",
            "damage_type": "slashing",
            "properties": ["Light"],
            "mastery": "Nick",
            "weight": 2.0,
            "cost": "1 GP",
            "category": "Simple",
            "type": "Melee"
        },
        "Spear": {
            "damage": "1d6",
            "damage_type": "piercing",
            "properties": ["Thrown (Range 20/60)", "Versatile (1d8)"],
            "mastery": "Sap",
            "weight": 3.0,
            "cost": "1 GP",
            "category": "Simple",
            "type": "Melee"
        }
    },
    "simple_ranged": {
        "Dart": {
            "damage": "1d4",
            "damage_type": "piercing",
            "properties": ["Finesse", "Thrown (Range 20/60)"],
            "mastery": "Vex",
            "weight": 0.25,
            "cost": "5 CP",
            "category": "Simple",
            "type": "Ranged"
        },
        "Light Crossbow": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 80/320; Bolt)", "Loading", "Two-Handed"],
            "mastery": "Slow",
            "weight": 5.0,
            "cost": "25 GP",
            "category": "Simple",
            "type": "Ranged"
        },
        "Shortbow": {
            "damage": "1d6",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 80/320; Arrow)", "Two-Handed"],
            "mastery": "Vex",
            "weight": 2.0,
            "cost": "25 GP",
            "category": "Simple",
            "type": "Ranged"
        },
        "Sling": {
            "damage": "1d4",
            "damage_type": "bludgeoning",
            "properties": ["Ammunition (Range 30/120; Bullet)"],
            "mastery": "Slow",
            "weight": 0,
            "cost": "1 SP",
            "category": "Simple",
            "type": "Ranged"
        }
    },
    "martial_melee": {
        "Battleaxe": {
            "damage": "1d8",
            "damage_type": "slashing",
            "properties": ["Versatile (1d10)"],
            "mastery": "Topple",
            "weight": 4.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Flail": {
            "damage": "1d8",
            "damage_type": "bludgeoning",
            "properties": [],
            "mastery": "Sap",
            "weight": 2.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Glaive": {
            "damage": "1d10",
            "damage_type": "slashing",
            "properties": ["Heavy", "Reach", "Two-Handed"],
            "mastery": "Graze",
            "weight": 6.0,
            "cost": "20 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Greataxe": {
            "damage": "1d12",
            "damage_type": "slashing",
            "properties": ["Heavy", "Two-Handed"],
            "mastery": "Cleave",
            "weight": 7.0,
            "cost": "30 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Greatsword": {
            "damage": "2d6",
            "damage_type": "slashing",
            "properties": ["Heavy", "Two-Handed"],
            "mastery": "Graze",
            "weight": 6.0,
            "cost": "50 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Halberd": {
            "damage": "1d10",
            "damage_type": "slashing",
            "properties": ["Heavy", "Reach", "Two-Handed"],
            "mastery": "Cleave",
            "weight": 6.0,
            "cost": "20 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Lance": {
            "damage": "1d10",
            "damage_type": "piercing",
            "properties": ["Heavy", "Reach", "Two-Handed (unless mounted)"],
            "mastery": "Topple",
            "weight": 6.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Longsword": {
            "damage": "1d8",
            "damage_type": "slashing",
            "properties": ["Versatile (1d10)"],
            "mastery": "Sap",
            "weight": 3.0,
            "cost": "15 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Maul": {
            "damage": "2d6",
            "damage_type": "bludgeoning",
            "properties": ["Heavy", "Two-Handed"],
            "mastery": "Topple",
            "weight": 10.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Morningstar": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": [],
            "mastery": "Sap",
            "weight": 4.0,
            "cost": "15 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Pike": {
            "damage": "1d10",
            "damage_type": "piercing",
            "properties": ["Heavy", "Reach", "Two-Handed"],
            "mastery": "Push",
            "weight": 18.0,
            "cost": "5 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Rapier": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": ["Finesse"],
            "mastery": "Vex",
            "weight": 2.0,
            "cost": "25 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Scimitar": {
            "damage": "1d6",
            "damage_type": "slashing",
            "properties": ["Finesse", "Light"],
            "mastery": "Nick",
            "weight": 3.0,
            "cost": "25 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Shortsword": {
            "damage": "1d6",
            "damage_type": "piercing",
            "properties": ["Finesse", "Light"],
            "mastery": "Vex",
            "weight": 2.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Trident": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": ["Thrown (Range 20/60)", "Versatile (1d10)"],
            "mastery": "Topple",
            "weight": 4.0,
            "cost": "5 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Warhammer": {
            "damage": "1d8",
            "damage_type": "bludgeoning",
            "properties": ["Versatile (1d10)"],
            "mastery": "Push",
            "weight": 5.0,
            "cost": "15 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "War Pick": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": ["Versatile (1d10)"],
            "mastery": "Sap",
            "weight": 2.0,
            "cost": "5 GP",
            "category": "Martial",
            "type": "Melee"
        },
        "Whip": {
            "damage": "1d4",
            "damage_type": "slashing",
            "properties": ["Finesse", "Reach"],
            "mastery": "Slow",
            "weight": 3.0,
            "cost": "2 GP",
            "category": "Martial",
            "type": "Melee"
        }
    },
    "martial_ranged": {
        "Blowgun": {
            "damage": "1d4",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 25/100; Needle)", "Loading"],
            "mastery": "Vex",
            "weight": 1.0,
            "cost": "10 GP",
            "category": "Martial",
            "type": "Ranged"
        },
        "Hand Crossbow": {
            "damage": "1d6",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 30/120; Bolt)", "Light", "Loading"],
            "mastery": "Vex",
            "weight": 3.0,
            "cost": "75 GP",
            "category": "Martial",
            "type": "Ranged"
        },
        "Heavy Crossbow": {
            "damage": "1d10",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 100/400; Bolt)", "Heavy", "Loading", "Two-Handed"],
            "mastery": "Push",
            "weight": 18.0,
            "cost": "50 GP",
            "category": "Martial",
            "type": "Ranged"
        },
        "Longbow": {
            "damage": "1d8",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 150/600; Arrow)", "Heavy", "Two-Handed"],
            "mastery": "Slow",
            "weight": 2.0,
            "cost": "50 GP",
            "category": "Martial",
            "type": "Ranged"
        },
        "Musket": {
            "damage": "1d12",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 40/120; Bullet)", "Loading", "Two-Handed"],
            "mastery": "Slow",
            "weight": 10.0,
            "cost": "500 GP",
            "category": "Martial",
            "type": "Ranged"
        },
        "Pistol": {
            "damage": "1d10",
            "damage_type": "piercing",
            "properties": ["Ammunition (Range 30/90; Bullet)", "Loading"],
            "mastery": "Vex",
            "weight": 3.0,
            "cost": "250 GP",
            "category": "Martial",
            "type": "Ranged"
        }
    }
}

# Flatten weapon database for easy lookup
ALL_WEAPONS = {}
for category_weapons in DND_WEAPON_DATABASE.values():
    ALL_WEAPONS.update(category_weapons)

# Create a quick lookup for weapon names (case-insensitive)
WEAPON_LOOKUP = {weapon.lower(): weapon for weapon in ALL_WEAPONS.keys()}

# Weapon proficiency mappings
CLASS_WEAPON_PROFICIENCIES = {
    "Barbarian": {
        "simple": True,
        "martial": True,
        "shields": True
    },
    "Bard": {
        "simple": True,
        "martial": False,
        "specific": ["Hand Crossbow", "Longsword", "Rapier", "Shortsword"],
        "shields": False
    },
    "Cleric": {
        "simple": True,
        "martial": False,
        "shields": True
    },
    "Druid": {
        "simple": True,
        "martial": False,
        "specific": ["Scimitar", "Shortsword"],
        "shields": True,
        "restrictions": ["No metal armor or shields"]
    },
    "Fighter": {
        "simple": True,
        "martial": True,
        "shields": True
    },
    "Monk": {
        "simple": True,
        "martial": False,
        "specific": ["Shortsword"],
        "shields": False
    },
    "Paladin": {
        "simple": True,
        "martial": True,
        "shields": True
    },
    "Ranger": {
        "simple": True,
        "martial": True,
        "shields": True
    },
    "Rogue": {
        "simple": True,
        "martial": False,
        "specific": ["Hand Crossbow", "Longsword", "Rapier", "Shortsword"],
        "shields": False
    },
    "Sorcerer": {
        "simple": False,
        "martial": False,
        "specific": ["Dagger", "Dart", "Sling", "Quarterstaff", "Light Crossbow"],
        "shields": False
    },
    "Warlock": {
        "simple": True,
        "martial": False,
        "shields": False
    },
    "Wizard": {
        "simple": False,
        "martial": False,
        "specific": ["Dagger", "Dart", "Sling", "Quarterstaff", "Light Crossbow"],
        "shields": False
    }
}

# ============================================================================
# D&D 5e FEAT DATABASE - PRIORITIZE EXISTING FEATS
# ============================================================================

# Complete D&D 5e 2024 feat database organized by category
DND_FEAT_DATABASE = {
    "origin_feats": {
        "Alert": {
            "description": "Always on the lookout for danger, you gain the following benefits:",
            "benefits": [
                "You gain a +5 bonus to initiative.",
                "You can't be surprised while you are conscious.",
                "Other creatures don't gain advantage on attack rolls against you as a result of being unseen by you."
            ],
            "prerequisites": None,
            "asi_bonus": False,
            "category": "Origin"
        },
        "Magic Initiate": {
            "description": "Choose a class: Bard, Cleric, Druid, Sorcerer, Warlock, or Wizard. You learn magic from that class:",
            "benefits": [
                "You learn two cantrips of your choice from that class's spell list.",
                "You learn one 1st-level spell of your choice from that class's spell list.",
                "You can cast this feat's 1st-level spell without expending a spell slot once per long rest.",
                "You can also cast the spell using any spell slots you have."
            ],
            "prerequisites": None,
            "asi_bonus": False,
            "category": "Origin",
            "spellcasting": True,
            "spell_class_choice": ["Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"]
        },
        "Savage Attacker": {
            "description": "You've trained to deal particularly damaging strikes:",
            "benefits": [
                "Once per turn when you hit with a weapon attack, you can reroll the weapon's damage dice and use either total."
            ],
            "prerequisites": None,
            "asi_bonus": False,
            "category": "Origin"
        },
        "Skilled": {
            "description": "You gain proficiency in any combination of three skills or tools of your choice:",
            "benefits": [
                "Gain proficiency in three skills of your choice.",
                "Alternatively, gain proficiency in three tools of your choice.",
                "Or any combination of skills and tools totaling three proficiencies."
            ],
            "prerequisites": None,
            "asi_bonus": False,
            "category": "Origin",
            "skill_proficiencies": 3
        }
    },
    "general_feats": {
        "Ability Score Improvement": {
            "description": "Increase your ability scores:",
            "benefits": [
                "Increase one ability score by 2, or",
                "Increase two different ability scores by 1 each."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 2
        },
        "Grappler": {
            "description": "You've developed the skills necessary to hold your own in close-quarters grappling:",
            "benefits": [
                "You have advantage on attack rolls against a creature you are grappling.",
                "You can use your action to try to pin a creature grappled by you.",
                "A pinned creature is restrained until the grapple ends."
            ],
            "prerequisites": ["Strength 13 or higher"],
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1
        },
        "Tough": {
            "description": "Your hit point maximum increases:",
            "benefits": [
                "Your hit point maximum increases by an amount equal to twice your level when you gain this feat.",
                "Whenever you gain a level thereafter, your hit point maximum increases by an additional 2 hit points."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1
        },
        "Lucky": {
            "description": "You have inexplicable luck that seems to kick in at just the right moment:",
            "benefits": [
                "You have 3 luck points.",
                "You can spend a luck point to roll an additional d20 when you make an attack roll, ability check, or saving throw.",
                "You can also spend a luck point when an attack roll is made against you.",
                "You regain your expended luck points when you finish a long rest."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1
        },
        "Resilient": {
            "description": "Choose one ability score. You gain proficiency in saving throws using the chosen ability:",
            "benefits": [
                "Increase the chosen ability score by 1.",
                "You gain proficiency in saving throws using the chosen ability."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1,
            "saving_throw_proficiency": True
        },
        "Fey Touched": {
            "description": "Your exposure to the Feywild's magic has changed you:",
            "benefits": [
                "Increase your Intelligence, Wisdom, or Charisma score by 1.",
                "You learn the misty step spell and one 1st-level spell of your choice from the divination or enchantment school.",
                "You can cast each of these spells without expending a spell slot once per long rest.",
                "You can also cast these spells using spell slots you have of the appropriate level."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1,
            "spellcasting": True
        },
        "Shadow Touched": {
            "description": "Your exposure to the Shadowfell's magic has changed you:",
            "benefits": [
                "Increase your Intelligence, Wisdom, or Charisma score by 1.",
                "You learn the invisibility spell and one 1st-level spell of your choice from the illusion or necromancy school.",
                "You can cast each of these spells without expending a spell slot once per long rest.",
                "You can also cast these spells using spell slots you have of the appropriate level."
            ],
            "prerequisites": None,
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1,
            "spellcasting": True
        },
        "War Caster": {
            "description": "You have practiced casting spells in the midst of combat:",
            "benefits": [
                "You have advantage on Constitution saving throws that you make to maintain your concentration on a spell.",
                "You can perform the somatic components of spells even when you have weapons or a shield in one or both hands.",
                "When a hostile creature's movement provokes an opportunity attack from you, you can use your reaction to cast a spell at the creature."
            ],
            "prerequisites": ["The ability to cast at least one spell"],
            "asi_bonus": True,
            "category": "General",
            "asi_points": 1,
            "spellcasting": True
        }
    },
    "fighting_style_feats": {
        "Archery": {
            "description": "You gain a +2 bonus to attack rolls you make with ranged weapons.",
            "benefits": [
                "+2 bonus to attack rolls with ranged weapons"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        },
        "Defense": {
            "description": "While you are wearing armor, you gain a +1 bonus to AC.",
            "benefits": [
                "+1 bonus to AC while wearing armor"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        },
        "Great Weapon Fighting": {
            "description": "When you roll a 1 or 2 on a damage die for an attack you make with a melee weapon that you are wielding with two hands, you can reroll the die and must use the new roll.",
            "benefits": [
                "Reroll 1s and 2s on damage dice for two-handed melee weapons"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        },
        "Two-Weapon Fighting": {
            "description": "When you engage in two-weapon fighting, you can add your ability modifier to the damage of the second attack.",
            "benefits": [
                "Add ability modifier to damage of off-hand attacks when two-weapon fighting"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        },
        "Dueling": {
            "description": "When you are wielding a melee weapon in one hand and no other weapons, you gain a +2 bonus to damage rolls with that weapon.",
            "benefits": [
                "+2 bonus to damage rolls when wielding a one-handed melee weapon with no other weapons"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        },
        "Protection": {
            "description": "When a creature you can see attacks a target other than you that is within 5 feet of you, you can use your reaction to impose disadvantage on the attack roll.",
            "benefits": [
                "Use reaction to impose disadvantage on attacks against nearby allies"
            ],
            "prerequisites": ["Fighter, Paladin, or Ranger class", "Must be wielding a shield"],
            "asi_bonus": False,
            "category": "Fighting Style",
            "fighting_style": True
        }
    },
    "epic_boon_feats": {
        "Boon of Combat Prowess": {
            "description": "Your combat abilities reach legendary heights:",
            "benefits": [
                "When you miss with an attack roll, you can choose to hit instead.",
                "Once you use this benefit, you can't use it again until you finish a short or long rest."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True
        },
        "Boon of Dimensional Travel": {
            "description": "You can slip through the boundaries between planes:",
            "benefits": [
                "As an action, you can cast the misty step spell, without expending a spell slot.",
                "You can also cast the dimension door spell with this boon, without expending a spell slot.",
                "Once you cast dimension door with this boon, you can't do so again until you finish a long rest."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True,
            "spellcasting": True
        },
        "Boon of Fate": {
            "description": "You can manipulate the threads of fate:",
            "benefits": [
                "When another creature that you can see within 60 feet of you makes an attack roll, an ability check, or a saving throw, you can use your reaction to force that roll to be made with advantage or disadvantage.",
                "Once you use this boon, you can't use it again until you finish a short or long rest."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True
        },
        "Boon of Irresistible Offense": {
            "description": "Your attacks become impossible to resist:",
            "benefits": [
                "When you deal damage to a creature, you can change the damage type to force damage.",
                "When you do so, the creature can't have resistance or immunity to the damage you deal."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True
        },
        "Boon of Spell Recall": {
            "description": "You can recall expended spell energy:",
            "benefits": [
                "You can cast any spell you know or have prepared without expending a spell slot.",
                "Once you use this boon, you can't use it again until you finish a long rest."
            ],
            "prerequisites": ["20th level", "The ability to cast at least one spell"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True,
            "spellcasting": True
        },
        "Boon of the Night Spirit": {
            "description": "You gain the shadowy powers of night spirits:",
            "benefits": [
                "While you are in dim light or darkness, you can become invisible as an action.",
                "You remain invisible until you take an action, a bonus action, or a reaction, or until you enter bright light.",
                "Once you use this boon, you can't use it again until you finish a long rest."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True
        },
        "Boon of Truesight": {
            "description": "You gain supernatural vision:",
            "benefits": [
                "You have truesight out to a range of 60 feet.",
                "Within that range, you can see in normal and magical darkness, see invisible creatures and objects, automatically detect visual illusions and succeed on saving throws against them, and perceive the original form of a shapechanger or a creature that is transformed by magic."
            ],
            "prerequisites": ["20th level"],
            "asi_bonus": False,
            "category": "Epic Boon",
            "epic_boon": True
        }
    }
}

# Flatten feat database for easy lookup
ALL_FEATS = {}
for category_feats in DND_FEAT_DATABASE.values():
    ALL_FEATS.update(category_feats)

# Create a quick lookup for feat names (case-insensitive)
FEAT_LOOKUP = {feat.lower(): feat for feat in ALL_FEATS.keys()}

# Feat availability by level and class
FEAT_AVAILABILITY = {
    "origin_feats": {
        "level_requirement": 1,
        "source": "Background",
        "limit": 1
    },
    "general_feats": {
        "level_requirement": 4,
        "levels": [4, 8, 12, 16, 19],
        "source": "ASI levels",
        "limit": 5
    },
    "fighting_style_feats": {
        "level_requirement": 1,
        "class_requirement": ["Fighter", "Paladin", "Ranger"],
        "source": "Class feature",
        "limit": 1
    },
    "epic_boon_feats": {
        "level_requirement": 20,
        "levels": [20],
        "source": "Epic level",
        "limit": 1
    }
}

# ============================================================================
# FEAT UTILITY FUNCTIONS
# ============================================================================

def is_existing_dnd_feat(feat_name: str) -> bool:
    """Check if a feat name exists in the official D&D 5e feat list."""
    return feat_name.lower() in FEAT_LOOKUP

def find_similar_feats(feat_name: str, max_results: int = 5) -> List[str]:
    """Find feats with similar names to help with feat suggestions."""
    feat_lower = feat_name.lower()
    similar = []
    
    # Exact match first
    if feat_lower in FEAT_LOOKUP:
        return [FEAT_LOOKUP[feat_lower]]
    
    # Partial matches
    for feat in ALL_FEATS.keys():
        if feat_lower in feat.lower() or feat.lower() in feat_lower:
            similar.append(feat)
            if len(similar) >= max_results:
                break
    
    return similar

def get_feat_data(feat_name: str) -> Optional[Dict[str, Any]]:
    """Get complete feat data for a specific feat."""
    return ALL_FEATS.get(feat_name)

def get_available_feats_for_level(level: int, character_class: str = None) -> Dict[str, List[str]]:
    """Get feats available for a character at a specific level."""
    available = {
        "origin_feats": [],
        "general_feats": [],
        "fighting_style_feats": [],
        "epic_boon_feats": []
    }
    
    # Origin feats (available at level 1)
    if level >= 1:
        available["origin_feats"] = list(DND_FEAT_DATABASE["origin_feats"].keys())
    
    # General feats (available at ASI levels)
    general_feat_levels = [4, 8, 12, 16, 19]
    available_general_levels = [l for l in general_feat_levels if l <= level]
    if available_general_levels:
        available["general_feats"] = list(DND_FEAT_DATABASE["general_feats"].keys())
    
    # Fighting style feats (class-dependent)
    if character_class in ["Fighter", "Paladin", "Ranger"] and level >= 1:
        available["fighting_style_feats"] = list(DND_FEAT_DATABASE["fighting_style_feats"].keys())
    
    # Epic boon feats (level 20)
    if level >= 20:
        available["epic_boon_feats"] = list(DND_FEAT_DATABASE["epic_boon_feats"].keys())
    
    return available

def get_appropriate_feats_for_character(character_data: Dict[str, Any], max_feats: int = 5) -> List[Dict[str, Any]]:
    """
    Get appropriate existing D&D 5e feats for a character based on their class, level, and concept.
    Prioritizes existing feats before suggesting custom feat creation.
    """
    feats = []
    level = character_data.get("level", 1)
    classes = character_data.get("classes", {})
    primary_class = list(classes.keys())[0] if classes else "Fighter"
    
    # Get available feats for this character
    available_feats = get_available_feats_for_level(level, primary_class)
    
    # Origin feat (always available at level 1)
    if level >= 1 and not character_data.get("origin_feat"):
        # Choose appropriate origin feat based on class/concept
        if primary_class in ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard"]:
            feat_name = "Magic Initiate"
        elif primary_class in ["Rogue", "Ranger"]:
            feat_name = "Alert"
        elif primary_class in ["Fighter", "Barbarian", "Paladin"]:
            feat_name = "Savage Attacker"
        else:
            feat_name = "Skilled"
        
        feat_data = get_feat_data(feat_name)
        if feat_data:
            feats.append({
                "name": feat_name,
                "category": "Origin",
                "level_gained": 1,
                "source": "D&D 5e Core",
                **feat_data
            })
    
    # General feats (at ASI levels)
    asi_levels = [l for l in [4, 8, 12, 16, 19] if l <= level]
    for asi_level in asi_levels:
        if len([f for f in feats if f["category"] == "General"]) < len(asi_levels):
            # Choose appropriate general feat
            if level <= 8:
                feat_name = "Ability Score Improvement"  # Most common choice
            elif level <= 12:
                feat_name = "Lucky" if primary_class in ["Rogue", "Bard"] else "Tough"
            else:
                feat_name = "War Caster" if primary_class in ["Wizard", "Sorcerer", "Cleric"] else "Resilient"
            
            feat_data = get_feat_data(feat_name)
            if feat_data:
                feats.append({
                    "name": feat_name,
                    "category": "General",
                    "level_gained": asi_level,
                    "source": "D&D 5e Core",
                    **feat_data
                })
    
    # Fighting style feat (class-dependent)
    if primary_class in ["Fighter", "Paladin", "Ranger"] and level >= 1:
        # Choose appropriate fighting style
        if primary_class == "Ranger":
            feat_name = "Archery"
        elif primary_class == "Paladin":
            feat_name = "Defense"
        else:  # Fighter
            feat_name = "Great Weapon Fighting"
        
        feat_data = get_feat_data(feat_name)
        if feat_data:
            feats.append({
                "name": feat_name,
                "category": "Fighting Style",
                "level_gained": 1,
                "source": "D&D 5e Core",
                **feat_data
            })
    
    # Epic boon feat (level 20)
    if level >= 20:
        feat_name = "Boon of Combat Prowess"  # Most universally useful
        feat_data = get_feat_data(feat_name)
        if feat_data:
            feats.append({
                "name": feat_name,
                "category": "Epic Boon",
                "level_gained": 20,
                "source": "D&D 5e Core",
                **feat_data
            })
    
    return feats[:max_feats]

# ============================================================================
# UTILITY FUNCTIONS FOR D&D DATA
# ============================================================================

def is_existing_dnd_spell(spell_name: str) -> bool:
    """Check if a spell name exists in the official D&D 5e spell list."""
    return spell_name.lower() in SPELL_LOOKUP

def find_similar_spells(spell_name: str, max_results: int = 5) -> List[str]:
    """Find spells with similar names to help with spell suggestions."""
    spell_lower = spell_name.lower()
    similar = []
    
    # Exact match first
    if spell_lower in SPELL_LOOKUP:
        return [SPELL_LOOKUP[spell_lower]]
    
    # Partial matches
    for spell in COMPLETE_SPELL_LIST:
        if spell_lower in spell.lower() or spell.lower() in spell_lower:
            similar.append(spell)
            if len(similar) >= max_results:
                break
    
    return similar

def is_existing_dnd_weapon(weapon_name: str) -> bool:
    """Check if a weapon name exists in the official D&D 5e weapon list."""
    return weapon_name.lower() in WEAPON_LOOKUP

def find_similar_weapons(weapon_name: str, max_results: int = 5) -> List[str]:
    """Find weapons with similar names to help with weapon suggestions."""
    weapon_lower = weapon_name.lower()
    similar = []
    
    # Exact match first
    if weapon_lower in WEAPON_LOOKUP:
        return [WEAPON_LOOKUP[weapon_lower]]
    
    # Partial matches
    for weapon in ALL_WEAPONS.keys():
        if weapon_lower in weapon.lower() or weapon.lower() in weapon_lower:
            similar.append(weapon)
            if len(similar) >= max_results:
                break
    
    return similar

def get_weapon_data(weapon_name: str) -> Optional[Dict[str, Any]]:
    """Get complete weapon data for a specific weapon."""
    return ALL_WEAPONS.get(weapon_name)

def get_appropriate_spells_for_character(character_data: Dict[str, Any], max_spells: int = 10) -> List[Dict[str, Any]]:
    """
    Get appropriate existing D&D 5e spells for a character based on their class and level.
    Prioritizes existing spells before suggesting custom spell creation.
    """
    spells = []
    character_level = character_data.get("level", 1)
    classes = character_data.get("classes", {})
    
    if not classes:
        return []
    
    # Get primary spellcasting class
    spellcasting_classes = ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Artificer"]
    primary_class = None
    
    for class_name in classes.keys():
        if class_name in spellcasting_classes:
            primary_class = class_name
            break
    
    if not primary_class:
        return []
    
    # Determine spell slots available based on class and level
    max_spell_level = min(9, (character_level + 1) // 2)  # Simplified calculation
    if primary_class in ["Paladin", "Ranger"]:
        max_spell_level = min(5, (character_level - 1) // 2)  # Half-casters
    
    # Get class spell preferences
    class_info = CLASS_SPELL_LISTS.get(primary_class, CLASS_SPELL_LISTS["Wizard"])
    preferred_schools = class_info["schools"]
    
    # Build spell list starting with cantrips
    if character_level >= 1:
        # Add cantrips
        cantrip_count = min(4, 2 + (character_level // 4))  # 2-4 cantrips based on level
        for school in preferred_schools:
            if len(spells) >= cantrip_count:
                break
            school_cantrips = DND_SPELL_DATABASE["cantrips"].get(school, [])
            for spell_name in school_cantrips[:2]:  # Up to 2 per school
                if len(spells) < cantrip_count:
                    spells.append({
                        "name": spell_name,
                        "level": 0,
                        "school": school,
                        "source": "D&D 5e Core"
                    })
    
    # Add leveled spells
    for spell_level in range(1, max_spell_level + 1):
        level_key = f"level_{spell_level}"
        spells_this_level = min(3, spell_level + 1)  # More spells at higher levels
        
        for school in preferred_schools:
            if len([s for s in spells if s["level"] == spell_level]) >= spells_this_level:
                break
            
            school_spells = DND_SPELL_DATABASE.get(level_key, {}).get(school, [])
            for spell_name in school_spells[:2]:  # Up to 2 per school per level
                if len([s for s in spells if s["level"] == spell_level]) < spells_this_level:
                    spells.append({
                        "name": spell_name,
                        "level": spell_level,
                        "school": school,
                        "source": "D&D 5e Core"
                    })
    
    return spells[:max_spells]

def get_appropriate_weapons_for_character(character_data: Dict[str, Any], max_weapons: int = 5) -> List[Dict[str, Any]]:
    """
    Get appropriate existing D&D 5e weapons for a character based on their class and proficiencies.
    Prioritizes existing weapons before suggesting custom weapon creation.
    """
    weapons = []
    classes = character_data.get("classes", {})
    
    if not classes:
        return []
    
    # Get primary class
    primary_class = list(classes.keys())[0]
    
    # Get class weapon proficiencies
    class_profs = CLASS_WEAPON_PROFICIENCIES.get(primary_class, {})
    
    # Collect appropriate weapons
    for category, category_weapons in DND_WEAPON_DATABASE.items():
        for weapon_name, weapon_data in category_weapons.items():
            # Check if character is proficient with this weapon
            if _is_character_proficient_with_weapon(weapon_name, weapon_data, class_profs):
                weapons.append({
                    "name": weapon_name,
                    "damage": weapon_data["damage"],
                    "damage_type": weapon_data["damage_type"],
                    "properties": weapon_data["properties"],
                    "mastery": weapon_data["mastery"],
                    "weight": weapon_data["weight"],
                    "cost": weapon_data["cost"],
                    "category": weapon_data["category"],
                    "type": weapon_data["type"],
                    "source": "D&D 5e Core"
                })
                
                if len(weapons) >= max_weapons:
                    break
        
        if len(weapons) >= max_weapons:
            break
    
    return weapons

def _is_character_proficient_with_weapon(weapon_name: str, weapon_data: Dict[str, Any], class_profs: Dict[str, Any]) -> bool:
    """Check if a character is proficient with a specific weapon based on class proficiencies."""
    category = weapon_data["category"]
    
    # Check simple weapon proficiency
    if category == "Simple" and class_profs.get("simple", False):
        return True
    
    # Check martial weapon proficiency
    if category == "Martial" and class_profs.get("martial", False):
        return True
    
    # Check specific weapon proficiencies
    specific_weapons = class_profs.get("specific", [])
    if weapon_name in specific_weapons:
        return True
    
    return False

def get_spell_schools_for_class(class_name: str) -> List[str]:
    """Get preferred spell schools for a character class."""
    return CLASS_SPELL_LISTS.get(class_name, CLASS_SPELL_LISTS["Wizard"])["schools"]

def get_spell_schools_for_class(class_name: str) -> List[str]:
    """Get preferred spell schools for a character class."""
    return CLASS_SPELL_LISTS.get(class_name, CLASS_SPELL_LISTS["Wizard"])["schools"]
def get_spell_schools_for_class(class_name: str) -> List[str]:
    """Get preferred spell schools for a character class."""
    return CLASS_SPELL_LISTS.get(class_name, CLASS_SPELL_LISTS["Wizard"])["schools"]

# ============================================================================
# D&D 5e ARMOR DATABASE - PRIORITIZE EXISTING ARMOR
# ============================================================================

# Complete D&D 5e 2024 armor database with AC, cost, weight, and properties
DND_ARMOR_DATABASE = {
    "light_armor": {
        "Padded Armor": {
            "ac_base": 11,
            "dex_modifier": "full",
            "weight": 8.0,
            "cost": "5 GP",
            "stealth": "disadvantage",
            "category": "Light",
            "properties": ["Stealth disadvantage"]
        },
        "Leather Armor": {
            "ac_base": 11,
            "dex_modifier": "full",
            "weight": 10.0,
            "cost": "10 GP",
            "stealth": "normal",
            "category": "Light",
            "properties": []
        },
        "Studded Leather Armor": {
            "ac_base": 12,
            "dex_modifier": "full",
            "weight": 13.0,
            "cost": "45 GP",
            "stealth": "normal",
            "category": "Light",
            "properties": []
        }
    },
    "medium_armor": {
        "Hide Armor": {
            "ac_base": 12,
            "dex_modifier": "max_2",
            "weight": 12.0,
            "cost": "10 GP",
            "stealth": "normal",
            "category": "Medium",
            "properties": []
        },
        "Chain Shirt": {
            "ac_base": 13,
            "dex_modifier": "max_2",
            "weight": 20.0,
            "cost": "50 GP",
            "stealth": "normal",
            "category": "Medium",
            "properties": []
        },
        "Scale Mail": {
            "ac_base": 14,
            "dex_modifier": "max_2",
            "weight": 45.0,
            "cost": "50 GP",
            "stealth": "disadvantage",
            "category": "Medium",
            "properties": ["Stealth disadvantage"]
        },
        "Breastplate": {
            "ac_base": 14,
            "dex_modifier": "max_2",
            "weight": 20.0,
            "cost": "400 GP",
            "stealth": "normal",
            "category": "Medium",
            "properties": []
        },
        "Half Plate Armor": {
            "ac_base": 15,
            "dex_modifier": "max_2",
            "weight": 40.0,
            "cost": "750 GP",
            "stealth": "disadvantage",
            "category": "Medium",
            "properties": ["Stealth disadvantage"]
        }
    },
    "heavy_armor": {
        "Ring Mail": {
            "ac_base": 14,
            "dex_modifier": "none",
            "weight": 40.0,
            "cost": "30 GP",
            "stealth": "disadvantage",
            "category": "Heavy",
            "properties": ["Stealth disadvantage"],
            "strength_requirement": None
        },
        "Chain Mail": {
            "ac_base": 16,
            "dex_modifier": "none",
            "weight": 55.0,
            "cost": "75 GP",
            "stealth": "disadvantage",
            "category": "Heavy",
            "properties": ["Stealth disadvantage"],
            "strength_requirement": 13
        },
        "Splint Armor": {
            "ac_base": 17,
            "dex_modifier": "none",
            "weight": 60.0,
            "cost": "200 GP",
            "stealth": "disadvantage",
            "category": "Heavy",
            "properties": ["Stealth disadvantage"],
            "strength_requirement": 15
        },
        "Plate Armor": {
            "ac_base": 18,
            "dex_modifier": "none",
            "weight": 65.0,
            "cost": "1,500 GP",
            "stealth": "disadvantage",
            "category": "Heavy",
            "properties": ["Stealth disadvantage"],
            "strength_requirement": 15
        }
    },
    "shields": {
        "Shield": {
            "ac_bonus": 2,
            "dex_modifier": 0,  # Shields don't affect dex modifier
            "weight": 6.0,
            "cost": "10 GP",
            "category": "Shield",
            "properties": []
        }
    }
}

# Flatten armor database for easy lookup
ALL_ARMOR = {}
for category_armor in DND_ARMOR_DATABASE.values():
    ALL_ARMOR.update(category_armor)

# Create a quick lookup for armor names (case-insensitive)
ARMOR_LOOKUP = {armor.lower(): armor for armor in ALL_ARMOR.keys()}

# Armor proficiency mappings
CLASS_ARMOR_PROFICIENCIES = {
    "Barbarian": {
        "light": True,
        "medium": True,
        "heavy": False,
        "shields": True
    },
    "Bard": {
        "light": True,
        "medium": False,
        "heavy": False,
        "shields": False
    },
    "Cleric": {
        "light": True,
        "medium": True,
        "heavy": False,
        "shields": True
    },
    "Druid": {
        "light": True,
        "medium": True,
        "heavy": False,
        "shields": True,
        "restrictions": ["No metal armor or shields"]
    },
    "Fighter": {
        "light": True,
        "medium": True,
        "heavy": True,
        "shields": True
    },
    "Monk": {
        "light": False,
        "medium": False,
        "heavy": False,
        "shields": False,
        "special": "Unarmored Defense"
    },
    "Paladin": {
        "light": True,
        "medium": True,
        "heavy": True,
        "shields": True
    },
    "Ranger": {
        "light": True,
        "medium": True,
        "heavy": False,
        "shields": True
    },
    "Rogue": {
        "light": True,
        "medium": False,
        "heavy": False,
        "shields": False
    },
    "Sorcerer": {
        "light": False,
        "medium": False,
        "heavy": False,
        "shields": False
    },
    "Warlock": {
        "light": True,
        "medium": False,
        "heavy": False,
        "shields": False
    },
    "Wizard": {
        "light": False,
        "medium": False,
        "heavy": False,
        "shields": False
    }
}

# ============================================================================
# D&D 5e TOOLS DATABASE - PRIORITIZE EXISTING TOOLS
# ============================================================================

# Complete D&D 5e 2024 tools database organized by category
DND_TOOLS_DATABASE = {
    "artisan_tools": {
        "Alchemist's Supplies": {
            "cost": "50 GP",
            "weight": 8.0,
            "category": "Artisan's Tools",
            "description": "Used to create alchemical items and identify substances",
            "related_skills": ["Arcana", "Investigation", "Medicine"]
        },
        "Brewer's Supplies": {
            "cost": "20 GP",
            "weight": 9.0,
            "category": "Artisan's Tools",
            "description": "Used to brew ales, beers, and other alcoholic beverages",
            "related_skills": ["History", "Medicine", "Persuasion"]
        },
        "Calligrapher's Supplies": {
            "cost": "10 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used for fine writing and document creation",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Carpenter's Tools": {
            "cost": "8 GP",
            "weight": 6.0,
            "category": "Artisan's Tools",
            "description": "Used to construct wooden structures and items",
            "related_skills": ["History", "Investigation", "Perception"]
        },
        "Cartographer's Tools": {
            "cost": "15 GP",
            "weight": 6.0,
            "category": "Artisan's Tools",
            "description": "Used to create accurate maps and charts",
            "related_skills": ["Arcana", "History", "Religion", "Nature"]
        },
        "Cobbler's Tools": {
            "cost": "5 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to make and repair shoes and boots",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Cook's Utensils": {
            "cost": "2 GP",
            "weight": 8.0,
            "category": "Artisan's Tools",
            "description": "Used to prepare meals and identify food quality",
            "related_skills": ["History", "Medicine", "Survival"]
        },
        "Glassblower's Tools": {
            "cost": "30 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to shape molten glass into various forms",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Jeweler's Tools": {
            "cost": "25 GP",
            "weight": 2.0,
            "category": "Artisan's Tools",
            "description": "Used to craft jewelry and identify precious stones",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Leatherworker's Tools": {
            "cost": "5 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to craft leather goods and armor",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Mason's Tools": {
            "cost": "10 GP",
            "weight": 8.0,
            "category": "Artisan's Tools",
            "description": "Used to work with stone and build structures",
            "related_skills": ["History", "Investigation", "Perception"]
        },
        "Painter's Supplies": {
            "cost": "10 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to create paintings and artistic works",
            "related_skills": ["Arcana", "History", "Religion", "Investigation"]
        },
        "Potter's Tools": {
            "cost": "10 GP",
            "weight": 3.0,
            "category": "Artisan's Tools",
            "description": "Used to shape clay into pottery and vessels",
            "related_skills": ["History", "Investigation", "Perception"]
        },
        "Smith's Tools": {
            "cost": "20 GP",
            "weight": 8.0,
            "category": "Artisan's Tools",
            "description": "Used to forge metal items and weapons",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Tinker's Tools": {
            "cost": "50 GP",
            "weight": 10.0,
            "category": "Artisan's Tools",
            "description": "Used to construct and repair clockwork devices",
            "related_skills": ["History", "Investigation", "Perception"]
        },
        "Weaver's Tools": {
            "cost": "1 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to create cloth and fabric items",
            "related_skills": ["Arcana", "History", "Investigation"]
        },
        "Woodcarver's Tools": {
            "cost": "1 GP",
            "weight": 5.0,
            "category": "Artisan's Tools",
            "description": "Used to carve intricate designs in wood",
            "related_skills": ["Arcana", "History", "Nature"]
        }
    },
    "specialist_kits": {
        "Disguise Kit": {
            "cost": "25 GP",
            "weight": 3.0,
            "category": "Specialist Kit",
            "description": "Used to create convincing disguises",
            "related_skills": ["Deception", "Intimidation", "Performance", "Persuasion"]
        },
        "Forgery Kit": {
            "cost": "15 GP",
            "weight": 5.0,
            "category": "Specialist Kit",
            "description": "Used to create false documents and signatures",
            "related_skills": ["Arcana", "Deception", "History", "Investigation"]
        },
        "Herbalism Kit": {
            "cost": "5 GP",
            "weight": 3.0,
            "category": "Specialist Kit",
            "description": "Used to identify and create herbal remedies",
            "related_skills": ["Arcana", "Investigation", "Medicine", "Nature", "Survival"]
        },
        "Navigator's Tools": {
            "cost": "25 GP",
            "weight": 2.0,
            "category": "Specialist Kit",
            "description": "Used for navigation on land and sea",
            "related_skills": ["Nature", "Survival"]
        },
        "Poisoner's Kit": {
            "cost": "50 GP",
            "weight": 2.0,
            "category": "Specialist Kit",
            "description": "Used to create and identify poisons",
            "related_skills": ["History", "Investigation", "Medicine", "Nature", "Perception"]
        },
        "Thieves' Tools": {
            "cost": "25 GP",
            "weight": 1.0,
            "category": "Specialist Kit",
            "description": "Used to pick locks and disarm traps",
            "related_skills": ["History", "Investigation", "Perception"]
        }
    },
    "gaming_sets": {
        "Dice Set": {
            "cost": "1 SP",
            "weight": 0,
            "category": "Gaming Set",
            "description": "A set of dice for gambling games",
            "related_skills": ["Deception", "History", "Insight", "Sleight of Hand"]
        },
        "Dragonchess Set": {
            "cost": "1 GP",
            "weight": 0.5,
            "category": "Gaming Set",
            "description": "A complex strategic board game",
            "related_skills": ["History", "Insight", "Investigation"]
        },
        "Playing Card Set": {
            "cost": "5 SP",
            "weight": 0,
            "category": "Gaming Set",
            "description": "A deck of cards for various games",
            "related_skills": ["Deception", "History", "Insight", "Sleight of Hand"]
        },
        "Three-Dragon Ante Set": {
            "cost": "1 GP",
            "weight": 0,
            "category": "Gaming Set",
            "description": "A popular gambling card game",
            "related_skills": ["Deception", "History", "Insight", "Sleight of Hand"]
        }
    },
    "musical_instruments": {
        "Bagpipes": {
            "cost": "30 GP",
            "weight": 6.0,
            "category": "Musical Instrument",
            "description": "Wind instrument with multiple pipes",
            "related_skills": ["History", "Performance"]
        },
        "Drum": {
            "cost": "6 GP",
            "weight": 3.0,
            "category": "Musical Instrument",
            "description": "Percussion instrument",
            "related_skills": ["History", "Performance"]
        },
        "Dulcimer": {
            "cost": "25 GP",
            "weight": 10.0,
            "category": "Musical Instrument",
            "description": "Stringed instrument played with hammers",
            "related_skills": ["History", "Performance"]
        },
        "Flute": {
            "cost": "2 GP",
            "weight": 1.0,
            "category": "Musical Instrument",
            "description": "Simple wind instrument",
            "related_skills": ["History", "Performance"]
        },
        "Horn": {
            "cost": "3 GP",
            "weight": 2.0,
            "category": "Musical Instrument",
            "description": "Brass wind instrument",
            "related_skills": ["History", "Performance"]
        },
        "Lute": {
            "cost": "35 GP",
            "weight": 2.0,
            "category": "Musical Instrument",
            "description": "Stringed instrument with a long neck",
            "related_skills": ["History", "Performance"]
        },
        "Lyre": {
            "cost": "30 GP",
            "weight": 2.0,
            "category": "Musical Instrument",
            "description": "Small harp-like stringed instrument",
            "related_skills": ["History", "Performance"]
        },
        "Pan Flute": {
            "cost": "12 GP",
            "weight": 2.0,
            "category": "Musical Instrument",
            "description": "Multiple pipes bound together",
            "related_skills": ["History", "Performance"]
        },
        "Shawm": {
            "cost": "2 GP",
            "weight": 1.0,
            "category": "Musical Instrument",
            "description": "Double-reed wind instrument",
            "related_skills": ["History", "Performance"]
        },
        "Viol": {
            "cost": "30 GP",
            "weight": 1.0,
            "category": "Musical Instrument",
            "description": "Bowed stringed instrument",
            "related_skills": ["History", "Performance"]
        }
    }
}

# Flatten tools database for easy lookup
ALL_TOOLS = {}
for category_tools in DND_TOOLS_DATABASE.values():
    ALL_TOOLS.update(category_tools)

# Create a quick lookup for tool names (case-insensitive)
TOOLS_LOOKUP = {tool.lower(): tool for tool in ALL_TOOLS.keys()}

# ============================================================================
# D&D 5e ADVENTURING GEAR DATABASE - PRIORITIZE EXISTING GEAR
# ============================================================================

# Complete D&D 5e 2024 adventuring gear database
DND_ADVENTURING_GEAR_DATABASE = {
    "ammunition": {
        "Arrows": {
            "cost": "1 GP",
            "weight": 1.0,
            "quantity": 20,
            "category": "Ammunition",
            "description": "Arrows for shortbows and longbows",
            "ammunition_type": "Arrow"
        },
        "Bolts": {
            "cost": "1 GP",
            "weight": 1.5,
            "quantity": 20,
            "category": "Ammunition",
            "description": "Bolts for crossbows",
            "ammunition_type": "Bolt"
        },
        "Firearm Bullets": {
            "cost": "3 GP",
            "weight": 2.0,
            "quantity": 10,
            "category": "Ammunition",
            "description": "Bullets for firearms",
            "ammunition_type": "Bullet"
        },
        "Sling Bullets": {
            "cost": "4 CP",
            "weight": 1.5,
            "quantity": 20,
            "category": "Ammunition",
            "description": "Bullets for slings",
            "ammunition_type": "Bullet"
        },
        "Needles": {
            "cost": "1 GP",
            "weight": 1.0,
            "quantity": 50,
            "category": "Ammunition",
            "description": "Needles for blowguns",
            "ammunition_type": "Needle"
        }
    },
    "arcane_focus": {
        "Crystal": {
            "cost": "10 GP",
            "weight": 1.0,
            "category": "Arcane Focus",
            "description": "A crystal used as a spellcasting focus",
            "focus_type": "Arcane"
        },
        "Orb": {
            "cost": "20 GP",
            "weight": 3.0,
            "category": "Arcane Focus",
            "description": "A magical orb used as a spellcasting focus",
            "focus_type": "Arcane"
        },
        "Rod": {
            "cost": "10 GP",
            "weight": 2.0,
            "category": "Arcane Focus",
            "description": "A rod used as a spellcasting focus",
            "focus_type": "Arcane"
        },
        "Wand": {
            "cost": "10 GP",
            "weight": 1.0,
            "category": "Arcane Focus",
            "description": "A wand used as a spellcasting focus",
            "focus_type": "Arcane"
        }
    },
    "druidic_focus": {
        "Druidic Focus": {
            "cost": "0 GP",
            "weight": 0,
            "category": "Druidic Focus",
            "description": "A natural focus like a crystal, branch, staff, totem, wand, or other focus",
            "focus_type": "Druidic"
        }
    },
    "holy_symbol": {
        "Holy Symbol": {
            "cost": "5 GP",
            "weight": 1.0,
            "category": "Holy Symbol",
            "description": "A symbol of divine power used as a spellcasting focus",
            "focus_type": "Divine"
        }
    },
    "consumables": {
        "Acid": {
            "cost": "25 GP",
            "weight": 1.0,
            "category": "Consumable",
            "description": "Vial of acid that deals 2d6 acid damage",
            "damage": "2d6 acid",
            "save": "Dexterity DC 13"
        },
        "Alchemist's Fire": {
            "cost": "50 GP",
            "weight": 1.0,
            "category": "Consumable",
            "description": "Flask of alchemical fire that deals 1d4 fire damage",
            "damage": "1d4 fire",
            "save": "Dexterity DC 13",
            "duration": "2 rounds"
        },
        "Antitoxin": {
            "cost": "50 GP",
            "weight": 0,
            "category": "Consumable",
            "description": "Provides advantage on saving throws against poison for 1 hour",
            "effect": "Advantage vs poison for 1 hour"
        }
    },
    "containers": {
        "Backpack": {
            "cost": "2 GP",
            "weight": 5.0,
            "category": "Container",
            "description": "A leather backpack that can hold 30 pounds of gear",
            "capacity": "1 cubic foot / 30 pounds"
        },
        "Pouch": {
            "cost": "5 SP",
            "weight": 1.0,
            "category": "Container",
            "description": "A small belt pouch that can hold 6 pounds of gear",
            "capacity": "1/5 cubic foot / 6 pounds"
        },
        "Sack": {
            "cost": "2 CP",
            "weight": 0.5,
            "category": "Container",
            "description": "A cloth sack that can hold 30 pounds of gear",
            "capacity": "1 cubic foot / 30 pounds"
        },
        "Chest": {
            "cost": "5 GP",
            "weight": 25.0,
            "category": "Container",
            "description": "A wooden chest that can hold 300 pounds of gear",
            "capacity": "12 cubic feet / 300 pounds"
        }
    },
    "equipment_packs": {
        "Burglar's Pack": {
            "cost": "16 GP",
            "weight": 46.5,
            "category": "Equipment Pack",
            "description": "Includes backpack, bag of 1,000 ball bearings, 10 feet of string, bell, 5 candles, crowbar, hammer, 10 pitons, hooded lantern, 2 flasks of oil, 5 days rations, tinderbox, waterskin, 50 feet of hempen rope",
            "contents": ["Backpack", "Ball bearings (1,000)", "String (10 feet)", "Bell", "Candles (5)", "Crowbar", "Hammer", "Pitons (10)", "Hooded lantern", "Oil (2 flasks)", "Rations (5 days)", "Tinderbox", "Waterskin", "Hempen rope (50 feet)"]
        },
        "Diplomat's Pack": {
            "cost": "39 GP",
            "weight": 46.0,
            "category": "Equipment Pack",
            "description": "Includes chest, 2 cases for maps and scrolls, set of fine clothes, bottle of ink, ink pen, lamp, 2 flasks of oil, 5 sheets of paper, vial of perfume, sealing wax, soap",
            "contents": ["Chest", "Map cases (2)", "Fine clothes", "Ink bottle", "Ink pen", "Lamp", "Oil (2 flasks)", "Paper (5 sheets)", "Perfume", "Sealing wax", "Soap"]
        },
        "Dungeoneer's Pack": {
            "cost": "12 GP",
            "weight": 61.5,
            "category": "Equipment Pack",
            "description": "Includes backpack, crowbar, hammer, 10 pitons, 10 torches, tinderbox, 10 days of rations, waterskin, 50 feet of hempen rope",
            "contents": ["Backpack", "Crowbar", "Hammer", "Pitons (10)", "Torches (10)", "Tinderbox", "Rations (10 days)", "Waterskin", "Hempen rope (50 feet)"]
        },
        "Entertainer's Pack": {
            "cost": "40 GP",
            "weight": 38.0,
            "category": "Equipment Pack",
            "description": "Includes backpack, bedroll, 2 costumes, 5 candles, 5 days of rations, waterskin, disguise kit",
            "contents": ["Backpack", "Bedroll", "Costumes (2)", "Candles (5)", "Rations (5 days)", "Waterskin", "Disguise kit"]
        },
        "Explorer's Pack": {
            "cost": "10 GP",
            "weight": 59.0,
            "category": "Equipment Pack",
            "description": "Includes backpack, bedroll, mess kit, tinderbox, 10 torches, 10 days of rations, waterskin, 50 feet of hempen rope",
            "contents": ["Backpack", "Bedroll", "Mess kit", "Tinderbox", "Torches (10)", "Rations (10 days)", "Waterskin", "Hempen rope (50 feet)"]
        },
        "Priest's Pack": {
            "cost": "19 GP",
            "weight": 24.0,
            "category": "Equipment Pack",
            "description": "Includes backpack, blanket, 10 candles, tinderbox, alms box, 2 blocks of incense, censer, vestments, 2 days of rations, waterskin",
            "contents": ["Backpack", "Blanket", "Candles (10)", "Tinderbox", "Alms box", "Incense (2 blocks)", "Censer", "Vestments", "Rations (2 days)", "Waterskin"]
        },
        "Scholar's Pack": {
            "cost": "40 GP",
            "weight": 20.0,
            "category": "Equipment Pack",
            "description": "Includes backpack, book of lore, bottle of ink, ink pen, 10 sheets of parchment, little bag of sand, small knife",
            "contents": ["Backpack", "Book of lore", "Ink bottle", "Ink pen", "Parchment (10 sheets)", "Sand bag", "Small knife"]
        }
    },
    "adventure_gear": {
        "Rope (50 feet)": {
            "cost": "2 GP",
            "weight": 10.0,
            "category": "Adventure Gear",
            "description": "50 feet of hempen rope, useful for climbing and securing equipment"
        },
        "Rations (5 days)": {
            "cost": "10 GP",
            "weight": 10.0,
            "category": "Adventure Gear",
            "description": "Dry foods suitable for extended travel, lasts 5 days"
        },
        "Waterskin": {
            "cost": "2 GP",
            "weight": 5.0,
            "category": "Adventure Gear",
            "description": "A leather pouch that holds 4 pints of liquid"
        }
    }
}

# Flatten adventuring gear database for easy lookup
ALL_ADVENTURING_GEAR = {}
for category_gear in DND_ADVENTURING_GEAR_DATABASE.values():
    ALL_ADVENTURING_GEAR.update(category_gear)

# Create a quick lookup for gear names (case-insensitive)
ADVENTURING_GEAR_LOOKUP = {gear.lower(): gear for gear in ALL_ADVENTURING_GEAR.keys()}

# Equipment pack mappings by class
CLASS_EQUIPMENT_PREFERENCES = {
    "Barbarian": "Explorer's Pack",
    "Bard": "Entertainer's Pack",
    "Cleric": "Priest's Pack",
    "Druid": "Explorer's Pack",
    "Fighter": "Dungeoneer's Pack",
    "Monk": "Explorer's Pack",
    "Paladin": "Explorer's Pack",
    "Ranger": "Explorer's Pack",
    "Rogue": "Burglar's Pack",
    "Sorcerer": "Dungeoneer's Pack",
    "Warlock": "Scholar's Pack",
    "Wizard": "Scholar's Pack"
}

# ============================================================================
# ARMOR, TOOLS, AND GEAR UTILITY FUNCTIONS
# ============================================================================

def is_existing_dnd_armor(armor_name: str) -> bool:
    """Check if an armor name exists in the official D&D 5e armor list."""
    return armor_name.lower() in ARMOR_LOOKUP

def find_similar_armor(armor_name: str, max_results: int = 5) -> List[str]:
    """Find armor with similar names to help with armor suggestions."""
    armor_lower = armor_name.lower()
    similar = []
    
    # Exact match first
    if armor_lower in ARMOR_LOOKUP:
        return [ARMOR_LOOKUP[armor_lower]]
    
    # Partial matches
    for armor in ALL_ARMOR.keys():
        if armor_lower in armor.lower() or armor.lower() in armor_lower:
            similar.append(armor)
            if len(similar) >= max_results:
                break
    
    return similar

def get_armor_data(armor_name: str) -> Optional[Dict[str, Any]]:
    """Get complete armor data for a specific armor."""
    return ALL_ARMOR.get(armor_name)

def is_existing_dnd_tool(tool_name: str) -> bool:
    """Check if a tool name exists in the official D&D 5e tools list."""
    return tool_name.lower() in TOOLS_LOOKUP

def find_similar_tools(tool_name: str, max_results: int = 5) -> List[str]:
    """Find tools with similar names to help with tool suggestions."""
    tool_lower = tool_name.lower()
    similar = []
    
    # Exact match first
    if tool_lower in TOOLS_LOOKUP:
        return [TOOLS_LOOKUP[tool_lower]]
    
    # Partial matches
    for tool in ALL_TOOLS.keys():
        if tool_lower in tool.lower() or tool.lower() in tool_lower:
            similar.append(tool)
            if len(similar) >= max_results:
                break
    
    return similar

def get_tool_data(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get complete tool data for a specific tool."""
    return ALL_TOOLS.get(tool_name)

def is_existing_dnd_gear(gear_name: str) -> bool:
    """Check if a gear name exists in the official D&D 5e adventuring gear list."""
    return gear_name.lower() in ADVENTURING_GEAR_LOOKUP

def find_similar_gear(gear_name: str, max_results: int = 5) -> List[str]:
    """Find gear with similar names to help with gear suggestions."""
    gear_lower = gear_name.lower()
    similar = []
    
    # Exact match first
    if gear_lower in ADVENTURING_GEAR_LOOKUP:
        return [ADVENTURING_GEAR_LOOKUP[gear_lower]]
    
    # Partial matches
    for gear in ALL_ADVENTURING_GEAR.keys():
        if gear_lower in gear.lower() or gear.lower() in gear_lower:
            similar.append(gear)
            if len(similar) >= max_results:
                break
    
    return similar

def get_gear_data(gear_name: str) -> Optional[Dict[str, Any]]:
    """Get complete gear data for a specific gear item."""
    return ALL_ADVENTURING_GEAR.get(gear_name)

def get_appropriate_armor_for_character(character_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get appropriate existing D&D 5e armor for a character based on their class and proficiencies.
    Prioritizes existing armor before suggesting custom armor creation.
    """
    classes = character_data.get("classes", {})
    if not classes:
        return None
    
    # Get primary class
    primary_class = list(classes.keys())[0]
    
    # Get class armor proficiencies
    class_profs = CLASS_ARMOR_PROFICIENCIES.get(primary_class, {})
    
    # Find appropriate armor based on proficiencies
    if class_profs.get("heavy", False):
        # Can wear heavy armor - choose based on level/wealth
        level = character_data.get("level", 1)
        if level >= 10:
            return get_armor_data("Plate Armor")
        elif level >= 5:
            return get_armor_data("Splint Armor")
        else:
            return get_armor_data("Chain Mail")
    elif class_profs.get("medium", False):
        # Can wear medium armor
        level = character_data.get("level", 1)
        if level >= 8:
            return get_armor_data("Half Plate Armor")
        elif level >= 3:
            return get_armor_data("Breastplate")
        else:
            return get_armor_data("Chain Shirt")
    elif class_profs.get("light", False):
        # Can wear light armor
        level = character_data.get("level", 1)
        if level >= 2:
            return get_armor_data("Studded Leather Armor")
        else:
            return get_armor_data("Leather Armor")
    
    # No armor proficiency or special case (like Monk)
    return None

def get_appropriate_tools_for_character(character_data: Dict[str, Any], max_tools: int = 3) -> List[Dict[str, Any]]:
    """
    Get appropriate existing D&D 5e tools for a character based on their class and background.
    Prioritizes existing tools before suggesting custom tool creation.
    """
    tools = []
    classes = character_data.get("classes", {})
    background = character_data.get("background", "")
    
    if not classes:
        return []
    
    primary_class = list(classes.keys())[0]
    
    # Tools based on class
    class_tools = {
        "Artificer": ["Tinker's Tools", "Smith's Tools"],
        "Barbarian": ["Herbalism Kit"],
        "Bard": ["Lute", "Flute"],
        "Cleric": ["Herbalism Kit"],
        "Druid": ["Herbalism Kit", "Woodcarver's Tools"],
        "Fighter": ["Smith's Tools"],
        "Monk": ["Herbalism Kit", "Calligrapher's Supplies"],
        "Paladin": ["Smith's Tools"],
        "Ranger": ["Herbalism Kit", "Woodcarver's Tools"],
        "Rogue": ["Thieves' Tools", "Forgery Kit"],
        "Sorcerer": ["Arcane Focus"],
        "Warlock": ["Arcane Focus"],
        "Wizard": ["Arcane Focus", "Calligrapher's Supplies"]
    }
    
    # Tools based on background
    background_tools = {
        "Acolyte": ["Herbalism Kit"],
        "Criminal": ["Thieves' Tools", "Gaming Set"],
        "Folk Hero": ["Smith's Tools", "Carpenter's Tools"],
        "Noble": ["Gaming Set"],
        "Sage": ["Alchemist's Supplies", "Calligrapher's Supplies"],
        "Soldier": ["Gaming Set", "Smith's Tools"],
        "Artisan": ["Artisan's Tools"],
        "Entertainer": ["Musical Instrument", "Disguise Kit"],
        "Guild Artisan": ["Artisan's Tools"],
        "Hermit": ["Herbalism Kit", "Alchemist's Supplies"],
        "Outlander": ["Herbalism Kit"],
        "Sailor": ["Navigator's Tools"],
        "Urchin": ["Thieves' Tools", "Disguise Kit"]
    }
    
    # Add class-based tools
    for tool_name in class_tools.get(primary_class, []):
        if tool_name == "Arcane Focus":
            # Choose specific arcane focus
            tool_data = get_gear_data("Crystal")
            if tool_data:
                tools.append({
                    "name": "Crystal",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        elif tool_name == "Musical Instrument":
            # Choose specific instrument
            tool_data = get_tool_data("Lute")
            if tool_data:
                tools.append({
                    "name": "Lute",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        elif tool_name == "Gaming Set":
            # Choose specific gaming set
            tool_data = get_tool_data("Dice Set")
            if tool_data:
                tools.append({
                    "name": "Dice Set",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        elif tool_name == "Artisan's Tools":
            # Choose specific artisan tools
            tool_data = get_tool_data("Smith's Tools")
            if tool_data:
                tools.append({
                    "name": "Smith's Tools",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        else:
            tool_data = get_tool_data(tool_name)
            if tool_data:
                tools.append({
                    "name": tool_name,
                    "source": "D&D 5e Core",
                    **tool_data
                })
        
        if len(tools) >= max_tools:
            break
    
    # Add background-based tools if space remains
    for tool_name in background_tools.get(background, []):
        if len(tools) >= max_tools:
            break
        
        # Skip if already have this tool
        if any(t["name"] == tool_name for t in tools):
            continue
        
        if tool_name == "Musical Instrument":
            tool_data = get_tool_data("Flute")
            if tool_data:
                tools.append({
                    "name": "Flute",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        elif tool_name == "Gaming Set":
            tool_data = get_tool_data("Playing Card Set")
            if tool_data:
                tools.append({
                    "name": "Playing Card Set",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        elif tool_name == "Artisan's Tools":
            tool_data = get_tool_data("Carpenter's Tools")
            if tool_data:
                tools.append({
                    "name": "Carpenter's Tools",
                    "source": "D&D 5e Core",
                    **tool_data
                })
        else:
            tool_data = get_tool_data(tool_name)
            if tool_data:
                tools.append({
                    "name": tool_name,
                    "source": "D&D 5e Core",
                    **tool_data
                })
    
    return tools[:max_tools]

def get_appropriate_equipment_pack_for_character(character_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get appropriate equipment pack for a character based on their class.
    """
    classes = character_data.get("classes", {})
    if not classes:
        return get_gear_data("Explorer's Pack")  # Default pack
    
    primary_class = list(classes.keys())[0]
    pack_name = CLASS_EQUIPMENT_PREFERENCES.get(primary_class, "Explorer's Pack")
    
    return get_gear_data(pack_name)
