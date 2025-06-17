# 1. Character Sheet Core Components
# /core/entities/character_sheet/
# Purpose: Break down the monolithic CharacterSheet into focused components

# character_core.py
# Class: CharacterCore
# Class: AbilityScore
# Enum: ProficiencyLevel
# Content: Core independent variables set during character creation/leveling (species, classes, ability scores, proficiencies)
# character_state.py
# Class: CharacterState
# Content: In-game independent variables that change during gameplay (current HP, spell slots, equipment, conditions)
# character_stats.py
# Class: CharacterStats
# Content: Dependent variables calculated from core and state (AC, initiative, spell save DC, passive scores)
# character_sheet.py
# Class: CharacterSheet
# Content: Main orchestrator that combines core, state, and stats with validation integration