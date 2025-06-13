# D&D Character Creator - Backend6

## Overview

A **background-driven creative content framework** for D&D 2024 that generates balanced, thematic, and rule-compliant characters and content based on player-provided background stories and concepts. Transform **any character concept** - from "Bill, the single father with bad dad jokes" to "Thor, the Norse god" - into a fully-realized D&D character with custom content that maintains mechanical balance and thematic authenticity.

**Output Format**: Complete D&D character sheets as JSON files for each level (1-20), compatible with virtual tabletops like Roll20, D&D Beyond, and FoundryVTT.

## Vision

Create an intelligent D&D content generation system that:
- **Starts with Story** - Players provide character backgrounds, system generates mechanics
- **Maximum Creative Freedom** - Generate custom species, classes, spells, feats, weapons, and armor
- **Ensures Balance** - All content meets D&D 2024 power level standards
- **Maintains Theme** - Generated content fits character narrative and world consistency
- **Follows Rules** - Strict adherence to official D&D 2024 mechanics and constraints
- **Complete Evolution** - Generate full character progression from levels 1-20 as JSON character sheets

## Character Creation Flow

### Interactive Character Development Process

#### Step 1: Initial Character Concept
**User Input**: Conversational character description
```
LLM Prompt: "Tell me about the character you'd like to develop. Describe their background, personality, abilities, or any specific vision you have in mind. Be as creative as you want - from everyday people to mythical beings!"

User Response: "I want to play Thor, the Norse god of thunder who was banished to Earth and has to learn humility while still being incredibly powerful."
```

#### Step 2: Initial Character Generation
**System Output**: Complete character sheet at appropriate starting level
```json
{
  "character_preview": {
    "name": "Thor Odinson",
    "concept": "Banished Norse god learning humility",
    "suggested_starting_level": 5,
    "species": "Asgardian (Custom Divine Heritage)",
    "classes": {
      "paladin": 3,
      "storm_sorcerer": 2
    },
    "signature_abilities": [
      "Divine Strength (Variant Powerful Build)",
      "Storm's Call (Thunder damage bonus)",
      "Mjolnir Bond (Weapon returns when thrown)"
    ],
    "signature_equipment": [
      "Mjolnir (Awakening) - +1 Warhammer with Thunder damage",
      "Asgardian Mail - Chain mail with lightning resistance"
    ]
  }
}
```

#### Step 3: Character Review & Preview
**System Output**: Level 5 character sheet + progression highlights
```json
{
  "level_5_character_sheet": {
    "basic_info": {
      "name": "Thor Odinson",
      "level": 5,
      "experience_points": 6500,
      "species": "Asgardian (Divine Heritage)",
      "background": "Exiled Noble",
      "classes": {"paladin": 3, "storm_sorcerer": 2}
    },
    "ability_scores": {
      "strength": {"score": 18, "modifier": 4, "save_proficient": false},
      "dexterity": {"score": 12, "modifier": 1, "save_proficient": false},
      "constitution": {"score": 16, "modifier": 3, "save_proficient": true},
      "intelligence": {"score": 10, "modifier": 0, "save_proficient": false},
      "wisdom": {"score": 14, "modifier": 2, "save_proficient": true},
      "charisma": {"score": 16, "modifier": 3, "save_proficient": false}
    },
    "combat_stats": {
      "armor_class": 18,
      "hit_points": 52,
      "hit_point_maximum": 52,
      "speed": 30,
      "proficiency_bonus": 3
    },
    "equipment": {
      "armor": {
        "name": "Asgardian Mail",
        "type": "Chain Mail",
        "ac": 16,
        "properties": ["Lightning Resistance"]
      },
      "weapons": [
        {
          "name": "Mjolnir (Awakening)",
          "type": "Warhammer",
          "damage": "1d8+4 bludgeoning + 1d4 thunder",
          "properties": ["Versatile", "Thrown (20/60)", "Returns to hand", "Magic +1"]
        }
      ]
    },
    "spells": {
      "paladin_spells": {
        "1st_level": ["Divine Favor", "Thunderous Smite", "Cure Wounds"]
      },
      "sorcerer_spells": {
        "cantrips": ["Thaumaturgy", "Shocking Grasp", "Prestidigitation"],
        "1st_level": ["Magic Missile", "Shield", "Thunderwave"]
      },
      "spell_slots": {
        "1st_level": 4,
        "2nd_level": 2
      }
    }
  },
  "progression_highlights": {
    "level_6": "Aura of Protection (Divine presence strengthens allies)",
    "level_10": "Mjolnir Fully Awakens (+2 weapon, can summon lightning)",
    "level_15": "Avatar of Thunder (Transform for 1 minute)",
    "level_20": "God-King Ascension (Legendary actions, immunity to lightning)"
  }
}
```

#### Step 4: User Feedback
**User Input**: Refinement requests
```
User: "This looks great, but I think Thor should be more focused on lightning magic and less on healing. Can you make him more of a storm-focused character? Also, I'd like Mjolnir to be more powerful earlier on."
```

#### Step 5: Character Refinement
**System Output**: Updated character with changes
```json
{
  "updated_character_preview": {
    "changes_made": [
      "Replaced Paladin healing spells with Storm-themed alternatives",
      "Enhanced Mjolnir's early-game power (+1 becomes +2 at level 5)",
      "Added Storm Magic feature for bonus lightning spells",
      "Adjusted spell list to focus on weather/storm magic"
    ],
    "updated_signature_abilities": [
      "Storm Magic (Bonus lightning/thunder spells known)",
      "Mjolnir Mastery (Enhanced weapon progression)",
      "Thunder God's Presence (Intimidation advantage)"
    ],
    "updated_spells": {
      "replaced_healing_focus": "Storm focus - Call Lightning, Gust of Wind, etc.",
      "new_storm_cantrips": ["Thunderclap", "Druidcraft (weather)"]
    }
  }
}
```

#### Step 6: Iteration Process
**Repeat Steps 3-5**: Continue refining until user satisfaction

#### Step 7: Final Character Generation
**System Output**: Complete 20-level progression + character sheet files

```json
{
  "character_generation_complete": {
    "character_name": "Thor Odinson",
    "concept": "Banished Norse god of thunder learning humility",
    "files_generated": [
      "thor_odinson_level_01.json",
      "thor_odinson_level_02.json",
      "... (all 20 levels)",
      "thor_odinson_level_20.json",
      "thor_odinson_complete_progression.json",
      "thor_odinson_custom_content.json"
    ],
    "character_evolution_summary": {
      "levels_1_5": {
        "theme": "Discovering Mortality",
        "key_features": ["Basic divine strength", "Learning to work with mortals", "Mjolnir partially awakened"],
        "power_level": "Strong but restrained by banishment"
      },
      "levels_6_10": {
        "theme": "Growing Wisdom",
        "key_features": ["Protective auras develop", "Storm magic strengthens", "Leadership abilities emerge"],
        "power_level": "Regional hero level"
      },
      "levels_11_15": {
        "theme": "Embracing Responsibility",
        "key_features": ["Mjolnir fully awakened", "Weather control", "Divine presence"],
        "power_level": "Legendary hero"
      },
      "levels_16_20": {
        "theme": "God-King Reborn",
        "key_features": ["Avatar transformation", "Cosmic awareness", "Legendary actions"],
        "power_level": "Mythic/Godlike"
      }
    },
    "custom_content_created": {
      "species": "Asgardian (Divine Heritage)",
      "spells": ["Call Thunder Storm", "Mjolnir's Return", "Divine Lightning Strike"],
      "magic_items": ["Mjolnir (Legendary Weapon)", "Asgardian Royal Armor"],
      "feats": ["Storm Lord", "Divine Presence", "Hammer Mastery"]
    }
  }
}
```

## Output Format Specification

### Individual Level Character Sheets
Each level generates a complete D&D character sheet as JSON:

```json
{
  "character_info": {
    "name": "Thor Odinson",
    "level": 10,
    "experience_points": 85000,
    "species": "Asgardian",
    "background": "Exiled Noble",
    "alignment": "Chaotic Good",
    "concept": "Banished god learning humility"
  },
  "ability_scores": {
    "strength": {"score": 20, "modifier": 5, "save_proficient": false},
    "dexterity": {"score": 14, "modifier": 2, "save_proficient": false},
    "constitution": {"score": 18, "modifier": 4, "save_proficient": true}
  },
  "combat_stats": {
    "armor_class": 20,
    "hit_points": 142,
    "hit_point_maximum": 142,
    "speed": 30,
    "proficiency_bonus": 4,
    "initiative": 2
  },
  "classes": {
    "paladin": {
      "level": 6,
      "hit_die": "d10",
      "features": ["Divine Sense", "Lay on Hands", "Aura of Protection"]
    },
    "storm_sorcerer": {
      "level": 4,
      "hit_die": "d6", 
      "features": ["Storm Magic", "Tempestuous Magic"]
    }
  },
  "skills": {
    "athletics": {"proficient": true, "expertise": false, "bonus": 9},
    "intimidation": {"proficient": true, "expertise": false, "bonus": 7},
    "insight": {"proficient": true, "expertise": false, "bonus": 6}
  },
  "equipment": {
    "armor": {
      "name": "Asgardian Royal Mail",
      "type": "Splint Armor", 
      "ac": 17,
      "properties": ["Lightning Resistance", "Advantage on Intimidation"]
    },
    "weapons": [
      {
        "name": "Mjolnir (Awakened)",
        "type": "Legendary Warhammer",
        "attack_bonus": 11,
        "damage": "1d8+7 bludgeoning + 2d6 thunder",
        "properties": ["Versatile (1d10)", "Thrown (30/120)", "Returns to hand", "+2 Magic Weapon"],
        "special_abilities": ["Lightning Strike (1/day)", "Worthiness Enchantment"]
      }
    ]
  },
  "spellcasting": {
    "spell_slots": {"1st": 4, "2nd": 3, "3rd": 2},
    "spells_known": {
      "paladin": {
        "1st_level": ["Divine Favor", "Thunderous Smite"],
        "2nd_level": ["Misty Step", "Hold Person"]
      },
      "sorcerer": {
        "cantrips": ["Thunderclap", "Prestidigitation", "Thaumaturgy", "Shocking Grasp"],
        "1st_level": ["Magic Missile", "Shield", "Thunderwave"],
        "2nd_level": ["Misty Step", "Scorching Ray", "Gust of Wind"]
      }
    },
    "spell_save_dc": 15,
    "spell_attack_bonus": 7
  },
  "features_and_traits": {
    "racial_traits": [
      {"name": "Divine Heritage", "description": "Resistance to lightning and thunder damage"},
      {"name": "Powerful Build", "description": "Count as one size larger for carrying capacity"}
    ],
    "class_features": [
      {"name": "Aura of Protection", "description": "Allies within 10 feet add CHA modifier to saves"},
      {"name": "Storm Magic", "description": "Know additional storm/weather spells"}
    ],
    "custom_features": [
      {"name": "Mjolnir Bond", "description": "Hammer returns when thrown, grants flight for 1 minute/day"}
    ]
  },
  "personality": {
    "traits": ["Speaks in grand, archaic manner", "Protective of innocents"],
    "ideals": ["Honor above all", "Strength should protect the weak"],
    "bonds": ["Mjolnir is my most trusted companion", "Must prove worthy of Asgard"],
    "flaws": ["Pride sometimes clouds judgment", "Impatient with mortal limitations"]
  }
}
```

### Complete Progression File
```json
{
  "character_summary": {
    "name": "Thor Odinson",
    "final_level": 20,
    "concept": "Banished Norse god of thunder",
    "creation_date": "2024-06-13",
    "custom_content_count": 12
  },
  "level_progression": {
    "1": { /* Level 1 complete character sheet */ },
    "2": { /* Level 2 complete character sheet */ },
    "...": "/* All levels 1-20 */",
    "20": { /* Level 20 complete character sheet */ }
  },
  "custom_content": {
    "species": [/* Custom Asgardian species definition */],
    "spells": [/* Custom storm/thunder spells */],
    "magic_items": [/* Mjolnir progression, Asgardian armor */],
    "feats": [/* Custom divine/storm feats */]
  },
  "thematic_evolution": {
    "tier_1": "Learning mortality and humility",
    "tier_2": "Embracing heroic responsibility", 
    "tier_3": "Ascending to divine kingship",
    "tier_4": "Cosmic protector and god-king"
  }
}
```

## File Export Options

### Standard Formats
- **JSON Character Sheets**: Native format, all VTT compatible
- **D&D Beyond**: Import-ready JSON format
- **Roll20**: Character sheet JSON format
- **FoundryVTT**: Actor data format
- **PDF**: Printable character sheets (generated from JSON)

### API Endpoints

#### Character Creation Flow
```http
POST /api/v1/characters/interactive-creation
{
    "conversation_id": "uuid",
    "user_input": "I want to create Thor, the Norse god of thunder"
}
```

#### Character Refinement
```http
PUT /api/v1/characters/interactive-creation/{conversation_id}
{
    "feedback": "Make him more storm-focused, less healing",
    "requested_changes": ["enhance_lightning_magic", "reduce_healing_focus"]
}
```

#### Generate Complete Character
```http
POST /api/v1/characters/generate-complete/{conversation_id}
{
    "export_format": ["json", "dnd_beyond", "roll20"],
    "include_custom_content": true,
    "output_directory": "./generated_characters/"
}
```

Response:
```json
{
    "success": true,
    "character_name": "Thor Odinson",
    "files_generated": {
        "character_sheets": [
            "./generated_characters/thor_odinson_level_01.json",
            "./generated_characters/thor_odinson_level_02.json",
            "... (all 20 levels)"
        ],
        "complete_progression": "./generated_characters/thor_odinson_complete.json",
        "custom_content": "./generated_characters/thor_odinson_custom_content.json",
        "summary_pdf": "./generated_characters/thor_odinson_summary.pdf"
    },
    "vtt_formats": {
        "dnd_beyond": "./generated_characters/thor_odinson_dndb.json",
        "roll20": "./generated_characters/thor_odinson_roll20.json",
        "foundry": "./generated_characters/thor_odinson_foundry.json"
    }
}
```

## Key Features

### 🎭 Unlimited Character Concepts
- **Any Character Vision**: From mundane ("Bill, the overworked accountant") to mythic ("Thor, Norse god of thunder")
- **Creative Translation**: LLM intelligently translates any concept into D&D mechanics
- **Thematic Authenticity**: Generated content remains true to original character vision
- **Custom Content Generation**: Create new species, classes, spells, feats, weapons, and armor as needed

### 📈 Complete Character Evolution (Levels 1-20)
- **Full Progression Planning**: Generate complete character development from level 1 to 20
- **JSON Character Sheets**: Each level produces a complete, VTT-ready character sheet
- **Thematic Consistency**: Ensure character growth aligns with background story
- **Balance Maintenance**: Each level meets appropriate power benchmarks

### ⚖️ Flexible Content Creation with Rigid Balance
- **Maximum Creative Freedom**: 
  - Species: Custom traits, abilities, and cultural features
  - Classes: New class archetypes and progression paths  
  - Spells: Thematic magic aligned with character concept
  - Feats: Custom abilities that fit character narrative
  - Weapons/Armor: Signature equipment (lightsabers, Mjolnir, etc.)
- **Minimum Flexibility Areas** (for D&D compatibility):
  - Core mechanics (AC, HP, saving throws)
  - Action economy (action, bonus action, reaction)
  - Spell slot progression and casting rules
  - Ability score system (6 core abilities)
  - Skills (translate to existing 18 D&D skills where possible)

### 📖 Intelligent Rule Compliance
- **D&D 2024 Framework**: All custom content follows core D&D mechanics
- **Balance Analysis**: Real-time power level calculations for all content
- **Automatic Adjustment**: Suggestions for overpowered/underpowered content
- **Modular Integration**: Generated characters fit seamlessly into existing D&D campaigns

### 🔧 Extensible Architecture
- Clean Architecture with Domain-Driven Design
- Plugin-based content generation system
- Configurable creativity vs. balance parameters
- Multiple LLM provider support (OpenAI, Anthropic)

## Character Examples

### Example 1: "Bill, the Single Father with Bad Dad Jokes"
```json
{
  "concept": "Bill, a single father who works as a middle manager and is known for his terrible dad jokes",
  "output_files": {
    "character_sheets": "bill_thompson_level_01.json through bill_thompson_level_20.json",
    "custom_content": {
      "species": "Human (Suburban Variant)",
      "class": "Bard (College of Dad Jokes)",
      "signature_equipment": ["Briefcase of Holding", "Tie of Protection +1"],
      "custom_spells": ["Groan of Despair", "Summon Lawn Mower"],
      "level_20_capstone": "Ultimate Dad Joke - force all enemies to make Constitution saves or be incapacitated by groaning"
    }
  }
}
```

### Example 2: "Thor, Norse God of Thunder"
```json
{
  "concept": "Thor, the Norse god of thunder and storms",
  "output_files": {
    "character_sheets": "thor_odinson_level_01.json through thor_odinson_level_20.json",
    "custom_content": {
      "species": "Asgardian (Divine Variant)",
      "class": "Paladin/Storm Sorcerer Multiclass",
      "signature_equipment": ["Mjolnir (Legendary Warhammer)", "Enchanted Mail of the Aesir"],
      "custom_spells": ["Call Lightning Storm", "Divine Thunder Strike"],
      "level_20_capstone": "God-Mode - Transform into avatar of thunder for 1 minute"
    }
  }
}
```

## Architecture

The system follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Application Layer                      │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │            Domain Layer                     │   │   │
│  │  │  ┌─────────────────────────────────────┐   │   │   │
│  │  │  │          Core Layer                 │   │   │   │
│  │  │  │                                     │   │   │   │
│  │  │  │  • Enums & Constants               │   │   │   │
│  │  │  │  • Utilities & Interfaces          │   │   │   │
│  │  │  │  • Base Exceptions                 │   │   │   │
│  │  │  └─────────────────────────────────────┘   │   │   │
│  │  │                                             │   │   │
│  │  │  • Entities & Value Objects                │   │   │
│  │  │  • Domain Services & Specifications        │   │   │
│  │  │  • Business Rules & Events                 │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │  • Use Cases & Orchestration                       │   │
│  │  • DTOs & Application Services                     │   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  • Repositories & External Services                        │
│  • Configuration & Web Framework                           │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Core Layer (`/core/`)
**Infrastructure-independent foundations**
- Content type definitions (species, classes, spells, weapons, armor)
- D&D mechanics constants (action types, damage types, spell schools)
- Creative constraints (balance thresholds, generation limits)
- Abstract interfaces for content creation and validation
- Base exception types for generation and validation errors

#### Domain Layer (`/domain/`)
**Pure business logic - D&D rules + creative content generation**
- **Character Entities**: Full character progression (levels 1-20) with custom content
- **Content Entities**: Custom species, classes, spells, feats, weapons, armor
- **Generation Entities**: Character concepts, creative constraints, thematic requirements
- **Balance Services**: Power level analysis, content adjustment, comparative evaluation
- **Content Creation Services**: LLM-driven custom content generation with D&D compliance
- **Progression Services**: Level-by-level character development planning
- **Character Sheet Services**: JSON generation for each level

#### Application Layer (`/application/`)
**Use case orchestration for creative content generation**
- **Interactive Character Creation**: Conversational character development workflow
- **Character Sheet Generation**: JSON export for all levels and VTT formats
- **Creative Translation**: Convert any concept into D&D-compatible mechanics
- **Balance Validation**: Ensure all custom content meets power level requirements
- **Thematic Consistency**: Maintain character vision throughout all generated content

#### Infrastructure Layer (`/infrastructure/`)
**External concerns**
- LLM provider integrations for creative content generation
- Character sheet export services (JSON, D&D Beyond, Roll20, FoundryVTT)
- File system management for character sheet storage
- Content repositories for storing custom species, classes, spells, etc.

## Configuration

### Creative Generation Settings
```bash
# Creativity Levels
DEFAULT_CREATIVITY_LEVEL=standard  # conservative, standard, high, maximum
ALLOW_CUSTOM_SPECIES=true
ALLOW_CUSTOM_CLASSES=true  
ALLOW_SIGNATURE_EQUIPMENT=true
MAX_CUSTOM_CONTENT_PER_CHARACTER=10

# Balance Controls  
DEFAULT_BALANCE_LEVEL=standard     # permissive, standard, strict
ENFORCE_POWER_LEVEL_CAPS=true
AUTO_ADJUST_OVERPOWERED_CONTENT=true
COMPARE_TO_OFFICIAL_CONTENT=true

# Progression Settings
GENERATE_FULL_PROGRESSION=true     # Always generate levels 1-20
INCLUDE_MILESTONE_EXPLANATIONS=true
SHOW_THEMATIC_EVOLUTION=true

# Export Settings
DEFAULT_EXPORT_FORMAT=json
ENABLE_VTT_FORMATS=true
AUTO_GENERATE_PDF_SUMMARY=true
```

### LLM Provider Configuration
```bash
# Primary LLM (Creative Content Generation)
PRIMARY_LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
CREATIVE_MODEL=gpt-4-turbo

# Secondary LLM (Balance Analysis)
BALANCE_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
BALANCE_MODEL=claude-3-sonnet

# Fallback Configuration
ENABLE_LLM_FALLBACK=true
MAX_GENERATION_RETRIES=3
```

## Creative Freedom vs. Balance Matrix

| Content Type | Creative Freedom | Balance Flexibility | Notes |
|-------------|------------------|-------------------|-------|
| **Species** | Maximum | Medium | New traits allowed, must follow racial bonus patterns |
| **Classes** | Maximum | Medium | New progressions allowed, must match power curves |
| **Spells** | Maximum | Low | New effects allowed, strict spell level compliance |
| **Feats** | Maximum | Low | Thematic abilities allowed, ASI/power balance enforced |
| **Weapons** | Maximum | Low | Signature weapons allowed, damage/properties standardized |
| **Armor** | High | Low | Custom appearance/lore, AC values must be standard |
| **Skills** | Medium | None | Translate to existing 18 skills where possible |
| **Abilities** | None | None | Must use STR/DEX/CON/INT/WIS/CHA |
| **Core Mechanics** | None | None | AC, HP, saves, action economy unchanged |

## Design Principles

### 1. Concept-First Design
Every character starts with a story or concept. All mechanics serve the narrative vision.

### 2. Maximum Creative Freedom
Generate any custom content needed to realize the character concept within D&D framework.

### 3. Rigid Balance Enforcement  
Creative freedom never compromises game balance. All content meets power level standards.

### 4. Complete Character Evolution
Every character includes full 1-20 progression showing thematic growth and mechanical development.

### 5. Interactive Development Process
Users collaborate with LLM to refine characters through conversational feedback loops.

### 6. VTT-Ready Output
All character sheets export as JSON compatible with major virtual tabletops.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/cosmic-guardian-class`)
3. Follow Clean Architecture principles
4. Maintain creative freedom while enforcing balance
5. Add comprehensive tests for custom content
6. Ensure all generated content integrates with D&D 2024
7. Submit pull request

### Code Standards
- **Creative Content**: Must be thematically consistent and mechanically balanced
- **Custom Classes**: Follow official class power curves and progression patterns
- **Custom Species**: Balance racial traits against existing species
- **Signature Equipment**: Unique flavor with standard mechanical effects
- **Character Progression**: Each level must feel meaningful and thematic
- **JSON Output**: Must be valid and VTT-compatible

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for D&D 2024 rules compatibility
- Inspired by unlimited creative character concepts
- Designed for seamless campaign integration
- Powered by advanced LLM content generation
- Compatible with major virtual tabletop platforms

---

**Note**: This is a creative content generation framework that translates any character concept into D&D-compatible mechanics. All D&D content remains property of Wizards of the Coast. Generated content is for personal use only and should be approved by your DM before use in campaigns.