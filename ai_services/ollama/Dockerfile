dnd_char_creator/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── core/
│   │   ├── ability_scores/
│   │   ├── alignment/
│   │   ├── character/
│   │   ├── classes/
│   │   ├── equipment/
│   │   ├── feats/
│   │   ├── personality_and_backstory/
│   │   ├── skills/
│   │   ├── species/
│   │   └── spells/
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py
│   │   │   ├── character.py
│   │   │   └── dm.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── character.py
│   │   │   ├── campaign.py
│   │   │   └── journal.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── character_service.py
│   │   │   ├── ai_integration.py
│   │   │   └── rules_validator.py
│   │   └── db/
│   │       ├── __init__.py
│   │       └── mongodb.py
│   └── tests/
│       └── test_character_creation.py
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Character/
│   │   │   │   ├── CharacterCreation.jsx
│   │   │   │   ├── CharacterSheet.jsx
│   │   │   │   └── CharacterList.jsx
│   │   │   ├── DM/
│   │   │   │   ├── DMDashboard.jsx
│   │   │   │   └── CharacterApproval.jsx
│   │   │   ├── Journal/
│   │   │   │   ├── JournalEditor.jsx
│   │   │   │   └── Waypoints.jsx
│   │   │   └── common/
│   │   │       ├── Navigation.jsx
│   │   │       └── ImageViewer.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── characterService.js
│   │   └── pages/
│   │       ├── Home.jsx
│   │       ├── CharacterCreator.jsx
│   │       ├── DMPortal.jsx
│           └── JournalPage.jsx
├── ai_services/
│   ├── ollama/
│   │   ├── Dockerfile
│   │   ├── prompt_templates/
│   │   │   ├── character_creation.json
│   │   │   ├── rules_validation.json
│   │   │   └── journal_summary.json
│   │   └── rules_data/
│   │       └── dnd_5e_rules.json
│   └── stable_diffusion/
│       ├── Dockerfile
│       ├── config/
│       │   └── sd_config.json
│       └── loras/
└── scripts/
    ├── setup.sh
    └── deploy.sh

Core Features
Web-based character creation guided by LLM through a series of prompts
Docker-containerized service with structured backend
Character balance moderation to ensure fairness between characters
Rules adherence to D&D 5e (2024 edition)
DM approval workflow for character creation
Character management including leveling up
Journals and notes for players and DMs
Character evolution tracking via "waypoints"
LLM-powered summaries of game events
AI image generation of created characters
Customizable components (spells, weapons, species) that adhere to abstract classes

Architecture:
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│    Frontend     │     │                 Backend                      │
│    (React)      │     │               (FastAPI)                      │
│                 │     │                                              │
│  - User Portal  │     │  ┌─────────────────┐    ┌────────────────┐   │
│  - Character    │◄───►│  │   Core Logic    │    │    MongoDB     │   │
│    Creation UI  │     │  │ - Character     │◄──►│  - Characters  │   │
│  - DM Dashboard │     │  │   Controller    │    │  - Campaigns   │   │
│  - Journal      │     │  │ - D&D Ruleset   │    │  - Journals    │   │
│  - Image Viewer │     │  │   Validator     │    └────────────────┘   │
└─────────────────┘     │  └─────────────────┘                         │
                        └───────────┬──────────────────────────────────┘
                                    │
                        ┌───────────▼──────────────────────────────────┐
                        │        Docker-Containerized AI Services      │
                        │                                              │
                        │  ┌────────────────────┐ ┌─────────────────┐  │
                        │  │  Ollama Container  │ │ Stable Diffusion│  │
                        │  │  - Llama 3 (8B)    │ │   Container     │  │
                        │  │  - Character       │ │ - SD Web UI     │  │
                        │  │    Prompt Templates│ │ - Character     │  │
                        │  │  - D&D Rules       │ │   Portrait      │  │
                        │  │    Integration     │ │   Generation    │  │
                        │  └────────────────────┘ └─────────────────┘  │
                        └──────────────────────────────────────────────┘
Refined Technology Stack
Core Components
Frontend: React with TailwindCSS
Backend: FastAPI (Python) for AI integration
Database: MongoDB for character data storage
AI Services:
Ollama with Llama 3 for character creation guidance
Stable Diffusion for character visualization

Implementation Details
Ollama + Llama 3 Integration
Container Config: Docker container with Ollama running Llama 3 8B model
Prompt Engineering: Pre-designed D&D-specific prompts for character development
API Endpoint: /api/ai/character-guidance for accessing Llama 3 suggestions
Context Management: Sessions to maintain character state during creation
Rules Integration: D&D 5e rules embedded in prompts/system messages
Stable Diffusion Integration
Container Config: Lightweight Stable Diffusion with custom fantasy character LoRA
Trigger Events: Image generation after character details are finalized
Portrait Specificity: Generate based on race, class, attributes and description
API Endpoint: /api/ai/generate-portrait
Format Options: Generate multiple angles/poses with consistent character appearance
Performance Considerations
GPU requirements for SD (can work with 4GB+ VRAM)
CPU-only option for Llama 3 8B with optimizations
Cache generated responses during character creation
Batch portrait generation during off-peak times
This architecture balances self-hosted AI with reasonable resource requirements while maintaining all core features from the original specification.

Future features: 
Stable Diffusion creates images of key events in journal to illustrate story.
Stable Diffusion can take prompts from DM to create a map for an upcoming campaign, town, battle map, dungeon

