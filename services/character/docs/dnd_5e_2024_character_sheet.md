# D&D 5e (2024) Complete Character Sheet Fields Reference

## Basic Character Information

### Character Name
- **Type**: Independent variable
- **Range**: Any string
- **Notes**: Player's choice

### Class & Level
- **Class**: Independent variable (chosen from available classes)
- **Level**: Independent variable
- **Range**: 1-20
- **Effects**: Determines proficiency bonus, features, spell slots, etc.

### Background
- **Type**: Independent variable
- **Range**: Any official background or custom background
- **Effects**: Provides skill proficiencies, languages, equipment

### Player Name
- **Type**: Independent variable
- **Range**: Any string

### Race
- **Type**: Independent variable
- **Range**: Any official race/species
- **Effects**: Provides ability score increases, traits, resistances, etc.

### Alignment
- **Type**: Independent variable
- **Range**: Nine alignments (LG, NG, CG, LN, N, CN, LE, NE, CE)

### Experience Points
- **Type**: Independent variable
- **Range**: 0-355,000+
- **Notes**: Used for leveling up

## Core Ability Scores

### Strength (STR)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

### Dexterity (DEX)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

### Constitution (CON)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

### Intelligence (INT)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

### Wisdom (WIS)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

### Charisma (CHA)
- **Type**: Independent variable (base) + modifiers
- **Base Range**: 1-20 (can exceed with magic items/spells, max 30)
- **Modifier Calculation**: (Score - 10) ÷ 2 (rounded down)

## Derived Statistics

### Proficiency Bonus
- **Type**: Calculated field
- **Calculation**: Based on character level
  - Levels 1-4: +2
  - Levels 5-8: +3
  - Levels 9-12: +4
  - Levels 13-16: +5
  - Levels 17-20: +6

### Armor Class (AC)
- **Type**: Calculated field
- **Base Calculation**: 10 + Dex modifier + armor bonus + shield bonus + other modifiers
- **Range**: Typically 8-30+

### Initiative
- **Type**: Calculated field
- **Calculation**: Dex modifier + other modifiers
- **Range**: Typically -5 to +15

### Speed
- **Type**: Base from race + modifiers
- **Base Range**: Usually 25-35 feet (varies by race)
- **Modifiers**: Armor, spells, features, conditions

### Hit Point Maximum
- **Type**: Calculated field
- **Calculation**: 
  - Level 1: Class hit die maximum + Con modifier
  - Levels 2+: Previous total + (hit die roll or average) + Con modifier per level
- **Range**: 1+ (minimum 1 per level)

### Current Hit Points
- **Type**: Variable field
- **Range**: 0 to Hit Point Maximum
- **Effects**: At 0 HP, character is unconscious and making death saves

### Temporary Hit Points
- **Type**: Variable field
- **Range**: 0+
- **Notes**: Don't stack, take highest value

### Hit Dice
- **Type**: Based on class and level
- **Calculation**: Number equal to character level, die type based on class
- **Usage**: Short rest healing

## Saving Throws

### Strength Saving Throw
- **Type**: Calculated field
- **Calculation**: Str modifier + (proficiency bonus if proficient)

### Dexterity Saving Throw
- **Type**: Calculated field
- **Calculation**: Dex modifier + (proficiency bonus if proficient)

### Constitution Saving Throw
- **Type**: Calculated field
- **Calculation**: Con modifier + (proficiency bonus if proficient)

### Intelligence Saving Throw
- **Type**: Calculated field
- **Calculation**: Int modifier + (proficiency bonus if proficient)

### Wisdom Saving Throw
- **Type**: Calculated field
- **Calculation**: Wis modifier + (proficiency bonus if proficient)

### Charisma Saving Throw
- **Type**: Calculated field
- **Calculation**: Cha modifier + (proficiency bonus if proficient)

## Skills

Each skill has the same calculation pattern: **Ability modifier + (proficiency bonus if proficient) + other bonuses**

### Strength-Based Skills
- **Athletics**: Str modifier + (prof. bonus if proficient)

### Dexterity-Based Skills
- **Acrobatics**: Dex modifier + (prof. bonus if proficient)
- **Sleight of Hand**: Dex modifier + (prof. bonus if proficient)
- **Stealth**: Dex modifier + (prof. bonus if proficient)

### Intelligence-Based Skills
- **Arcana**: Int modifier + (prof. bonus if proficient)
- **History**: Int modifier + (prof. bonus if proficient)
- **Investigation**: Int modifier + (prof. bonus if proficient)
- **Nature**: Int modifier + (prof. bonus if proficient)
- **Religion**: Int modifier + (prof. bonus if proficient)

### Wisdom-Based Skills
- **Animal Handling**: Wis modifier + (prof. bonus if proficient)
- **Insight**: Wis modifier + (prof. bonus if proficient)
- **Medicine**: Wis modifier + (prof. bonus if proficient)
- **Perception**: Wis modifier + (prof. bonus if proficient)
- **Survival**: Wis modifier + (prof. bonus if proficient)

### Charisma-Based Skills
- **Deception**: Cha modifier + (prof. bonus if proficient)
- **Intimidation**: Cha modifier + (prof. bonus if proficient)
- **Performance**: Cha modifier + (prof. bonus if proficient)
- **Persuasion**: Cha modifier + (prof. bonus if proficient)

## Passive Scores

### Passive Perception
- **Type**: Calculated field
- **Calculation**: 10 + Perception skill bonus
- **Effects**: Used for noticing hidden creatures/objects without rolling

### Passive Investigation
- **Type**: Calculated field
- **Calculation**: 10 + Investigation skill bonus
- **Effects**: Used for noticing details without actively searching

### Passive Insight
- **Type**: Calculated field
- **Calculation**: 10 + Insight skill bonus
- **Effects**: Used for detecting lies/motives without rolling

## Proficiencies

### Languages
- **Type**: Independent variable
- **Source**: Race, background, class, feats
- **Range**: Any official languages

### Tool Proficiencies
- **Type**: Independent variable
- **Source**: Race, background, class, feats
- **Calculation**: Ability modifier + proficiency bonus (when using tools)

### Weapon Proficiencies
- **Type**: Independent variable
- **Source**: Race, class, feats
- **Effects**: Can add proficiency bonus to attack rolls

### Armor Proficiencies
- **Type**: Independent variable
- **Source**: Class, feats
- **Effects**: No disadvantage when wearing proficient armor

## Combat Statistics

### Attack Bonuses (per weapon)
- **Type**: Calculated field
- **Melee Calculation**: Str modifier + proficiency bonus (if proficient) + magic bonus
- **Ranged Calculation**: Dex modifier + proficiency bonus (if proficient) + magic bonus
- **Finesse Weapons**: Can use Dex instead of Str for melee

### Damage Bonuses (per weapon)
- **Type**: Calculated field
- **Melee Calculation**: Str modifier + magic bonus + other bonuses
- **Ranged Calculation**: Dex modifier + magic bonus + other bonuses
- **Finesse Weapons**: Can use Dex instead of Str for melee

## Conditions (and their effects)

### Blinded
- **Effects**: 
  - Can't see, automatically fails sight-based checks
  - Attack rolls have disadvantage
  - Attack rolls against you have advantage

### Charmed
- **Effects**:
  - Can't attack the charmer or target them with harmful abilities/spells
  - Charmer has advantage on social interaction checks

### Deafened
- **Effects**:
  - Can't hear, automatically fails hearing-based checks

### Frightened
- **Effects**:
  - Disadvantage on ability checks and attack rolls while source of fear is within line of sight
  - Can't willingly move closer to source of fear

### Grappled
- **Effects**:
  - Speed becomes 0, can't benefit from speed bonuses
  - Ends if grappler is incapacitated or moved away

### Incapacitated
- **Effects**:
  - Can't take actions or reactions

### Invisible
- **Effects**:
  - Impossible to see without special means
  - Attack rolls have advantage
  - Attack rolls against you have disadvantage

### Paralyzed
- **Effects**:
  - Incapacitated and can't move or speak
  - Automatically fails Str and Dex saves
  - Attack rolls have advantage
  - Critical hits if attacked within 5 feet

### Petrified
- **Effects**:
  - Transformed to solid inanimate substance
  - Incapacitated, can't move or speak
  - Unaware of surroundings
  - Automatically fails Str and Dex saves
  - Resistance to all damage
  - Immune to poison and disease

### Poisoned
- **Effects**:
  - Disadvantage on attack rolls and ability checks

### Prone
- **Effects**:
  - Can only crawl or use action to stand
  - Disadvantage on attack rolls
  - Advantage on attack rolls against you within 5 feet
  - Disadvantage on attack rolls against you beyond 5 feet

### Restrained
- **Effects**:
  - Speed becomes 0
  - Disadvantage on attack rolls and Dex saves
  - Attack rolls against you have advantage

### Stunned
- **Effects**:
  - Incapacitated and can't move
  - Can speak falteringly
  - Automatically fails Str and Dex saves
  - Attack rolls against you have advantage

### Unconscious
- **Effects**:
  - Incapacitated and can't move or speak
  - Unaware of surroundings
  - Drops whatever it's holding and falls prone
  - Automatically fails Str and Dex saves
  - Attack rolls have advantage
  - Critical hits if attacked within 5 feet

### Exhaustion (6 levels)
- **Level 1**: Disadvantage on ability checks
- **Level 2**: Speed halved
- **Level 3**: Disadvantage on attack rolls and saving throws
- **Level 4**: Hit point maximum halved
- **Level 5**: Speed reduced to 0
- **Level 6**: Death

## Death Saves

### Death Save Successes
- **Type**: Variable field
- **Range**: 0-3
- **Effects**: 3 successes = stabilized at 1 HP

### Death Save Failures
- **Type**: Variable field
- **Range**: 0-3
- **Effects**: 3 failures = death

## Spellcasting (if applicable)

### Spellcasting Ability
- **Type**: Determined by class
- **Values**: Wisdom, Intelligence, or Charisma

### Spell Save DC
- **Type**: Calculated field
- **Calculation**: 8 + proficiency bonus + spellcasting ability modifier

### Spell Attack Bonus
- **Type**: Calculated field
- **Calculation**: Proficiency bonus + spellcasting ability modifier

### Spell Slots (by level)
- **Type**: Calculated field based on class and level
- **Levels**: 1st through 9th level slots
- **Calculation**: Varies by class progression

### Spells Known/Prepared
- **Type**: Variable based on class
- **Calculation**: Varies by class (some know all, others prepare limited number)

### Cantrips Known
- **Type**: Based on class progression
- **Range**: 0-4+ depending on class and level

## Resources

### Hit Dice (detailed)
- **Type**: Based on class
- **Die Types by Class**:
  - d6: Sorcerer, Wizard
  - d8: Artificer, Bard, Cleric, Druid, Monk, Rogue, Warlock
  - d10: Fighter, Paladin, Ranger
  - d12: Barbarian
- **Usage**: Spend during short rests for healing

### Short Rest Resources
- Various class features that recharge on short rest

### Long Rest Resources
- Various class features that recharge on long rest

## Equipment & Inventory

### Weapons
- **Attack Bonus**: Str/Dex modifier + prof. bonus (if proficient) + magic bonus
- **Damage**: Weapon die + Str/Dex modifier + magic bonus
- **Properties**: Light, Heavy, Two-handed, Versatile, Finesse, etc.

### Armor
- **AC Calculation**: Base AC + Dex modifier (limited by armor type) + magic bonus
- **Types**: Light, Medium, Heavy, Shield

### Currency
- **Copper Pieces (CP)**: Independent variable, range 0+
- **Silver Pieces (SP)**: Independent variable, range 0+
- **Electrum Pieces (EP)**: Independent variable, range 0+
- **Gold Pieces (GP)**: Independent variable, range 0+
- **Platinum Pieces (PP)**: Independent variable, range 0+

### Other Equipment
- **Type**: Independent variable
- **Effects**: Various based on item type

## Features & Traits

### Racial Traits
- **Type**: Fixed based on race choice
- **Effects**: Vary by race (darkvision, resistance, bonus actions, etc.)

### Class Features
- **Type**: Fixed based on class and level
- **Effects**: Vary by class (rage, spellcasting, sneak attack, etc.)

### Background Features
- **Type**: Fixed based on background choice
- **Effects**: Vary by background

### Feats (if using optional rule)
- **Type**: Independent variable
- **Source**: Variant Human/Custom Lineage at 1st level, or in place of ASI
- **Effects**: Vary by feat

## Inspiration

### Inspiration
- **Type**: Variable field
- **Range**: 0-1 (you either have it or don't)
- **Usage**: Advantage on one ability check, attack roll, or saving throw

## Additional Mechanics

### Concentration
- **Type**: Status (concentrating or not)
- **Effects**: Can only concentrate on one spell at a time
- **Saves**: Constitution save when taking damage (DC 10 or half damage, whichever is higher)

### Advantage/Disadvantage
- **Type**: Temporary modifier
- **Effects**: Roll twice, take higher (advantage) or lower (disadvantage)
- **Sources**: Various conditions, spells, features

### Cover
- **Half Cover**: +2 AC and Dex saves
- **Three-Quarters Cover**: +5 AC and Dex saves
- **Total Cover**: Can't be targeted directly

## Lifestyle & Downtime

### Lifestyle Expenses
- **Type**: Independent variable
- **Options**: Wretched, Squalid, Poor, Modest, Comfortable, Wealthy, Aristocratic
- **Cost**: 0-10+ GP per day

## Magic Items

### Attunement Slots
- **Type**: Limited resource
- **Range**: 0-3 slots maximum
- **Usage**: Required for certain magic items

### Magic Item Properties
- **Rarity**: Common, Uncommon, Rare, Very Rare, Legendary, Artifact
- **Requirements**: Class, race, alignment, or ability restrictions
- **Effects**: Vary by item

## Multiclassing (Optional Rule)

### Multiclass Requirements
- **Type**: Ability score prerequisites
- **Requirements**: Must meet ability score minimums for both current and new class

### Spell Slot Calculation (Multiclass)
- **Type**: Calculated field
- **Calculation**: Complex formula based on caster levels from different classes

## Epic Boons (Level 20+)

### Epic Boon
- **Type**: Independent variable (gained at level 20+)
- **Effects**: Powerful abilities beyond normal progression

## Notes & Additional Information

### Character Appearance
- **Age**: Independent variable
- **Height**: Independent variable
- **Weight**: Independent variable
- **Eyes**: Independent variable
- **Skin**: Independent variable
- **Hair**: Independent variable

### Character Backstory
- **Personality Traits**: Independent variable (usually 2)
- **Ideals**: Independent variable (usually 1)
- **Bonds**: Independent variable (usually 1)
- **Flaws**: Independent variable (usually 1)

### Allies & Organizations
- **Type**: Independent variable
- **Effects**: Story/roleplay implications

### Additional Features & Traits
- **Type**: Various sources (feats, magic items, boons)
- **Effects**: Highly variable

## Tool Proficiencies (Detailed)

### Artisan's Tools
- **Types**: Various (smith's tools, carpenter's tools, etc.)
- **Calculation**: Ability modifier + proficiency bonus (usually Int, sometimes others)

### Gaming Sets
- **Calculation**: Usually Wis modifier + proficiency bonus

### Musical Instruments
- **Calculation**: Usually Cha modifier + proficiency bonus

### Thieves' Tools
- **Calculation**: Dex modifier + proficiency bonus

### Vehicles
- **Land/Water Vehicles**: Usually Dex modifier + proficiency bonus

## Important Maximums and Limits

- **Ability Score Maximum**: 30 (20 without magic)
- **Proficiency Bonus Maximum**: +6
- **Character Level Maximum**: 20 (Epic Boons beyond)
- **Spell Level Maximum**: 9th level
- **Attunement Slots**: 3 maximum
- **Exhaustion Levels**: 6 (death at level 6)
- **Inspiration**: 1 maximum at a time

## Variable Tracking Fields

### Spell Slots Used
- **Type**: Variable (0 to maximum per slot level)

### Class Resource Usage
- **Examples**: Rage uses, Bardic Inspiration uses, Sorcery Points, etc.
- **Recharge**: Varies (short rest, long rest, dawn, etc.)

### Ammunition
- **Type**: Variable field
- **Examples**: Arrows, bolts, darts, etc.

This comprehensive list covers all major fields on a D&D 5e (2024) character sheet, including calculations, ranges, effects, and subfields. The 2024 rules maintain most of the same structure as the 2014 rules but with some refinements and clarifications.