# D&D Character Creator Backend - Engineering Requirements

## CORE MISSION
Create an AI-powered D&D 5e 2024 character creation system that enables users to bring ANY character concept to life through:
- **Creative Freedom**: Generate non-traditional characters beyond standard D&D constraints
- **Custom Content Creation**: Automatically create new classes, species, feats, spells, weapons, and armor
- **Deep Storytelling**: Generate compelling backstories aligned with character concepts
- **Iterative Development**: Collaborative character refinement through user feedback
- **Traditional Foundation**: Prioritize existing D&D content when appropriate, create custom when needed

## PRIMARY REQUIREMENTS

### 1. CHARACTER CREATION SYSTEM
**PRIORITY: CRITICAL**
- **Input**: User provides character concept description (text prompt)
- **Output**: Complete D&D 5e 2024 character sheet with full attributes
- **Process**: LLM translates concept → validates content → generates complete character
- **Flexibility**: Support ANY character concept, even if requiring completely custom content

**Required Character Components:**
- Core Attributes: Name, Species, Class(es), Level, Background, Alignment
- Ability Scores: STR, DEX, CON, INT, WIS, CHA (properly calculated)
- Skills & Proficiencies: Class/species/background appropriate selections
- Feats: Origin feat (level 1) + general feats (levels 4,8,12,16,19) + fighting styles + epic boons
- Equipment: Weapons, armor, tools, general equipment (class/background appropriate)
- Spells: For spellcasters, appropriate spell selection with spell slots
- Backstory: Deep, compelling narrative aligned with character concept
- Personality: Traits, ideals, bonds, flaws that bring character to life

### 2. CUSTOM CONTENT GENERATION
**PRIORITY: CRITICAL**
- **Custom Species**: New races with balanced traits, abilities, and lore
- **Custom Classes**: New classes with level progression, features, and spellcasting
- **Custom Feats**: Unique abilities that enhance character concepts
- **Custom Spells**: Thematic spells that fit character concepts
- **Custom Weapons**: Unique weapons with appropriate damage and properties
- **Custom Armor**: Armor types that fit character themes and protection needs
- **Balance Requirement**: All custom content must be balanced for D&D 5e play

### 3. ITERATIVE REFINEMENT SYSTEM
**PRIORITY: HIGH**
- User describes desired changes to generated character
- System updates character while maintaining consistency
- Process continues until user approves final character
- Track all iterations for version history

### 4. EXISTING CHARACTER ENHANCEMENT
**PRIORITY: HIGH**
- Import existing characters from database
- Level-up characters using journal entries as context for how character is actually played
- Multi-class characters based on play patterns and user preferences
- Maintain character consistency during advancement

### 5. CONTENT HIERARCHY & PRIORITIZATION
**PRIORITY: HIGH**
```
1. FIRST PRIORITY: Use existing D&D 5e 2024 official content when appropriate
2. SECOND PRIORITY: Adapt existing content to fit concept
3. THIRD PRIORITY: Create custom content when concept requires it
4. BALANCE REQUIREMENT: All content must be balanced for level-appropriate play
```

## SECONDARY REQUIREMENTS

### 6. NPC & CREATURE CREATION
**PRIORITY: MEDIUM**
- Reuse character creation foundation for NPCs and creatures
- Generate appropriate challenge ratings for creatures
- Create roleplay-focused NPCs with motivations, secrets, and relationships
- Support various NPC types: major, minor, shopkeeper, quest-giver, etc.

### 7. STANDALONE ITEM CREATION
**PRIORITY: MEDIUM**
- Create individual spells, weapons, armor for DM use
- Generate items for in-game discovery and rewards
- Maintain thematic consistency with campaign setting

### 8. DATABASE & VERSION CONTROL
**PRIORITY: MEDIUM**
- UUID tracking for all created content
- Git-like branching for character evolution
- Character approval workflow (tentative → DM approved)
- Persistent storage of custom content for reuse

## TECHNICAL REQUIREMENTS

### 9. SYSTEM ARCHITECTURE
**PRIORITY: CRITICAL**
- **LLM Integration**: OpenAI/Ollama services for content generation
- **D&D 5e Compliance**: Full compatibility with 2024 rules; rules found at https://roll20.net/compendium/dnd5e/Rules:Free%20Basic%20Rules%20(2024)
- **Database Models**: Comprehensive character and content storage
- **API Structure**: RESTful endpoints for all creation operations
- **Error Handling**: Graceful fallbacks when generation fails

### 10. CONTENT VALIDATION
**PRIORITY: HIGH**
- Validate all generated content against D&D 5e rules
- Ensure mathematical correctness of character attributes
- Verify spell slot calculations, AC, HP, proficiency bonuses
- Balance check custom content against existing power levels

### 11. PERFORMANCE STANDARDS
**PRIORITY: MEDIUM**
- Character creation: < 30 seconds for complex characters
- Simple updates: < 5 seconds
- Database queries: < 1 second response time
- Concurrent user support: 10+ simultaneous creations

## IN-GAME PLAY REQUIREMENTS

### 12. CHARACTER SHEET MANAGEMENT
**PRIORITY: MEDIUM**
- Load complete character sheets for play
- Real-time attribute calculations based on conditions
- HP tracking, exhaustion levels, temporary effects
- Automatic updates when character state changes

### 13. JOURNAL & EXPERIENCE SYSTEM
**PRIORITY: LOW**
- Add journal entries to character sheets
- Track XP and prompt for level-up when appropriate
- Use journal data to inform character advancement decisions

## QUALITY STANDARDS

### 14. CONTENT QUALITY
- **Creativity**: Support unique, memorable character concepts
- **Balance**: All content appropriate for specified character level
- **Consistency**: Character elements work together thematically
- **Completeness**: Every character has full D&D 5e attribute set
- **Narrative Depth**: Rich backstories that enhance roleplay

### 15. USER EXPERIENCE
- **Intuitive**: Simple concept description creates complete character
- **Flexible**: Support iteration and refinement
- **Reliable**: Consistent quality across different character types
- **Feedback**: Clear communication of what was generated and why

## IMPLEMENTATION PRIORITY ORDER
1. **Core character creation with existing D&D content**
2. **Custom content generation (species, classes, items)**
3. **Iterative refinement system**
4. **Character advancement and leveling**
5. **NPC and creature creation**
6. **Database persistence and versioning**
7. **In-game play features**

---

## CONTEXT FOR AI ASSISTANTS
When working on this system, remember:
- **Primary Goal**: Enable ANY character concept through creative D&D content generation
- **Balance First**: All content must be playable and balanced
- **User-Centric**: Prioritize ease of use and creative freedom
- **D&D Foundation**: Build on 5e 2024 rules while extending beyond traditional limits
- **Iterative Design**: Support collaborative character development process


## BACKEND How files work together:
app.py (FastAPI endpoints) 
  ↓ calls
creation_factory.py (orchestration) 
  ↓ uses
creation.py (character creation logic)
  ↓ depends on
- dnd_data.py (official D&D content)
- custom_content_models.py (custom content)
- character_models.py (data structures)
- core_models.py (D&D mechanics)
- creation_validation.py (balance checking)
- content_coordinator.py (complex workflows)