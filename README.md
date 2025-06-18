# D&D Character Creator - Backend Development

## Project Status: Core Layer Development (Work in Progress)

A **background-driven creative content framework** for D&D 2024 that generates balanced, thematic, and rule-compliant characters and content based on player-provided background stories and concepts. Currently undergoing architectural development with focus on building a robust core layer foundation.

**Ultimate Vision**: Transform **any character concept** - from "Bill, the single father with bad dad jokes" to "Thor, the Norse god" - into a fully-realized D&D character with custom content that maintains mechanical balance and thematic authenticity.

**Target Output Format**: Complete D&D character sheets as JSON files for each level (1-20), compatible with virtual tabletops like Roll20, D&D Beyond, and FoundryVTT.

## Development Philosophy

Create an intelligent D&D content generation system that:
- **Starts with Story** - Players provide character backgrounds, system generates mechanics
- **Maximum Creative Freedom** - Generate custom species, classes, spells, feats, weapons, and armor
- **Ensures Balance** - All content meets D&D 2024 power level standards
- **Maintains Theme** - Generated content fits character narrative and world consistency
- **Follows Rules** - Strict adherence to official D&D 2024 mechanics and constraints
- **Complete Evolution** - Generate full character progression from levels 1-20 as JSON character sheets

## Current Architecture: Clean Architecture Principles

The system is being built from the ground up following **Clean Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer (Planned)               │
│  • LLM provider integrations • Export services             │
│  • File system management • Content repositories           │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│             Application Layer (In Development)              │
│  • Interactive Character Creation • Character Sheet Gen    │
│  • Creative Translation • Balance Validation               │
│  • Thematic Consistency • Use Case Orchestration          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│              Domain Layer (Planned)                         │
│  • Character Entities • Content Entities                   │
│  • Generation Entities • Balance Services                  │
│  • Content Creation Services • Progression Services        │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│             Core Layer (Currently Developing)               │
│  🚧 Enhanced Culture System  🚧 Comprehensive Enums        │
│  🚧 LLM Provider Abstractions  🚧 Text Processing          │
│  🚧 D&D Utilities  🚧 Character Generation System          │
│  🚧 Testing & Validation Framework                         │
└─────────────────────────────────────────────────────────────┘
```

## Current Development Focus: Core Layer (`/backend6/core/`)

### ✅ Core Layer Components (In Development)

**Enhanced Culture Generation System**
- **EnhancedCreativeCultureGenerator**: Character-optimized culture creation
- **EnhancedCreativeCultureValidator**: Creative validation with constructive feedback
- **CHARACTER_CULTURE_PRESETS**: Gaming table ready culture templates
- **CultureOrchestrator**: Complete culture generation workflow management

**Comprehensive Enum Framework**
- **Culture Generation Enums**: `CultureGenerationType`, `CultureAuthenticityLevel`, `CultureEnhancementCategory`
- **Game Mechanic Enums**: Complete D&D 2024 mechanics coverage
- **Validation Enums**: Assessment categories and validation approaches
- **Enum Utility Functions**: Character generation scoring, optimization recommendations

**LLM Provider Abstraction System**
- **CultureLLMProvider**: Abstract base for culture generation providers
- **StreamingCultureLLMProvider**: Real-time culture generation support
- **BatchCultureLLMProvider**: Multiple culture generation optimization
- **Provider assessment utilities**: Readiness evaluation and capability testing

**Enhanced Text Processing Engine**
- **Cultural awareness**: Context-sensitive text analysis
- **Multi-language support**: International content processing
- **Fantasy terminology extraction**: D&D-specific content processing
- **Complexity assessment**: Readability and accessibility analysis

**Traditional D&D Utilities** (Enhanced)
- **Balance Calculator**: Power level analysis with character generation focus
- **Mechanical Parser**: D&D mechanics extraction and validation
- **Content Utilities**: Rule compliance and content validation
- **Rule Checker**: D&D 2024 rules enforcement

## Planned Character Creation Flow

### Interactive Character Development Process (Target Implementation)

#### Step 1: Initial Character Concept
```
LLM Prompt: "Tell me about the character you'd like to develop. Describe their background, personality, abilities, or any specific vision you have in mind. Be as creative as you want - from everyday people to mythical beings!"

User Response: "I want to play Thor, the Norse god of thunder who was banished to Earth and has to learn humility while still being incredibly powerful."
```

#### Step 2-7: Iterative Development Process
- Initial character generation with complete character sheet
- Character review & preview with progression highlights
- User feedback and refinement requests
- Character refinement with updated abilities
- Iteration until user satisfaction
- Final character generation with complete 20-level progression

### Target Output: Complete Character Progression

Each character will generate:
- **Individual Level Character Sheets**: Complete JSON for levels 1-20
- **Complete Progression File**: Full character evolution with thematic growth
- **Custom Content Package**: New species, classes, spells, feats, equipment
- **VTT-Compatible Exports**: Roll20, D&D Beyond, FoundryVTT formats

## Character Examples (Target Vision)

### Example 1: "Bill, the Single Father with Bad Dad Jokes"
```json
{
  "concept": "Bill, a single father who works as a middle manager and is known for his terrible dad jokes",
  "planned_output": {
    "species": "Human (Suburban Variant)",
    "class": "Bard (College of Dad Jokes)",
    "signature_equipment": ["Briefcase of Holding", "Tie of Protection +1"],
    "custom_spells": ["Groan of Despair", "Summon Lawn Mower"],
    "level_20_capstone": "Ultimate Dad Joke - force all enemies to make Constitution saves or be incapacitated by groaning"
  }
}
```

### Example 2: "Thor, Norse God of Thunder"
```json
{
  "concept": "Thor, the Norse god of thunder and storms",
  "planned_output": {
    "species": "Asgardian (Divine Variant)",
    "class": "Paladin/Storm Sorcerer Multiclass",
    "signature_equipment": ["Mjolnir (Legendary Warhammer)", "Enchanted Mail of the Aesir"],
    "custom_spells": ["Call Lightning Storm", "Divine Thunder Strike"],
    "level_20_capstone": "God-Mode - Transform into avatar of thunder for 1 minute"
  }
}
```

## Tech Stack

### Current Development Stack
- **Backend Core**: Python with clean architecture principles
- **Core Layer**: Enhanced culture system with comprehensive D&D utilities
- **Database**: MongoDB (planned)
- **AI Services**: 
  - LLM provider abstractions (OpenAI, Anthropic support planned)
  - Ollama with Llama 3 (8B) for creative content generation
  - Stable Diffusion for character visualization (future)

### Planned Full Stack
- **Frontend**: React with TailwindCSS
- **Backend**: FastAPI service layer over the core architecture
- **AI Services**: Docker-containerized LLM and image generation instances

## Development Roadmap

### 🚧 Currently In Development
- **Core Layer Foundation**: Culture generation system, enums, LLM abstractions
- **Text Processing Engine**: D&D-aware content processing
- **Testing Framework**: Infrastructure-independent validation

### 📋 Next Development Phases
1. **Domain Layer**: Character entities, content entities, business rules
2. **Application Layer**: Use cases, DTOs, workflow orchestration  
3. **Infrastructure Layer**: LLM integrations, data persistence, external APIs
4. **API Layer**: FastAPI endpoints for character creation flow
5. **Frontend**: React interface for interactive character development

### 🎯 Target Features
- **Creative Freedom vs. Balance Matrix**: Maximum creativity with rigid balance enforcement
- **Interactive Character Development**: Conversational refinement process
- **Complete Character Evolution**: Full 1-20 progression with thematic growth
- **VTT-Ready Output**: JSON exports for all major virtual tabletops
- **Custom Content Generation**: Species, classes, spells, feats, equipment

## Configuration (Planned)

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
```

## Design Principles (Core Architecture)

### 1. Concept-First Design
Every character starts with a story or concept. All mechanics serve the narrative vision.

### 2. Maximum Creative Freedom
Generate any custom content needed to realize the character concept within D&D framework.

### 3. Rigid Balance Enforcement  
Creative freedom never compromises game balance. All content meets power level standards.

### 4. Clean Architecture
Dependencies flow inward, infrastructure-independent core, clear separation of concerns.

### 5. Test-Driven Development
Core layer built with comprehensive testing framework for reliability.

### 6. Extensible Foundation
Plugin-based system supporting multiple LLM providers and content generation approaches.

## Contributing

This project is in active development. Current contribution areas:

### Core Layer Development
- **Enhanced Culture System**: Culture generation, validation, and orchestration
- **Enum Framework**: D&D mechanics coverage and utility functions
- **LLM Abstractions**: Provider-agnostic interfaces and request structures
- **Text Processing**: D&D-aware content analysis and extraction
- **Testing Framework**: Infrastructure-independent validation

### Code Standards
- **Clean Architecture**: Maintain separation of concerns and dependency rules
- **Test Coverage**: All core functionality must be testable independent of infrastructure
- **Documentation**: Comprehensive documentation for all public interfaces
- **Type Safety**: Full type hints and validation for all components

## Setup and Installation (Development)

### Prerequisites
```bash
python 3.11+
pip (Python package manager)
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-repo/dnd-char-creator.git
cd dnd-char-creator

# Install development dependencies
pip install -r requirements-dev.txt

# Run core layer tests
python -m pytest backend6/core/tests/ -v

# Validate core layer interfaces
python backend6/core/validation/validate_core_interfaces.py
```

# D&D Character Creator

A comprehensive web application for creating, managing, and customizing D&D 5e characters with AI assistance.

## 🎲 Features

- **AI-Powered Character Creation**: Uses LLM to help create balanced and interesting characters
- **D&D 5e 2024 Compliant**: Follows the latest D&D rules and guidelines
- **Custom Content Support**: Create custom species, classes, items, spells, and more
- **DM Tools**: Character approval, NPC creation, and campaign management
- **Character Progression**: Level up characters and track their growth
- **Image Generation**: AI-generated character portraits using Stable Diffusion

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Full Stack                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Frontend      │    Backend      │      AI Services        │
│   (React)       │   (FastAPI)     │                         │
│   Port 3000     │   Port 8000     │   ├─ Ollama (11434)    │
│                 │                 │   └─ Stable Diff (7860) │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
                  ┌────────┴─────────┐
                  │    Database      │
                  │  (PostgreSQL)    │
                  │   Port 5432      │
                  └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Podman** and **podman-compose** installed
- **NVIDIA GPU** (optional, for AI image generation)
- **8GB+ RAM** recommended

### Full Application Setup

```bash
# Clone the repository
git clone <repository-url>
cd dnd_char_creator

# Run the full application stack
./deployment/scripts/setup-full.sh

# Access the application
# - Frontend:  http://localhost:3000
# - Backend:   http://localhost:8000
# - API Docs:  http://localhost:8000/docs
```

### Backend Development Only

```bash
# Run only backend services (for development)
./deployment/scripts/setup-backend-dev.sh

# Access backend services
# - Backend:   http://localhost:8000
# - API Docs:  http://localhost:8000/docs
# - Database:  localhost:5432
```

## 📁 Project Structure

```
dnd_char_creator/
├── backend/                 # FastAPI backend application
│   ├── core_models.py      # Core character system models
│   ├── custom_content_models.py  # Custom content management
│   ├── character_creation.py     # Character creation logic
│   ├── fastapi_main_new.py       # FastAPI application
│   └── requirements-new.txt      # Python dependencies
├── frontend/               # React frontend application
│   ├── src/                # React components and pages
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── ai_services/            # AI service containers
│   ├── ollama/             # Local LLM service
│   └── stable_diffusion/   # Image generation service
├── deployment/             # All deployment configurations
│   ├── scripts/            # Setup and management scripts
│   └── compose/            # Environment-specific compose files
└── podman-compose.yml      # Main orchestration file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_PASSWORD=your_secure_password

# API Configuration
SECRET_KEY=your_secret_key

# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3:8b

# External API Keys (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### LLM Providers

1. **Ollama (Default)** - Local, private, free
2. **OpenAI** - Cloud service, requires API key
3. **Anthropic** - Claude AI, requires API key

## 🛠️ Development

### Backend Development

```bash
# Start backend services
./deployment/scripts/setup-backend-dev.sh

# Run tests
podman exec dnd_character_api_dev python -m pytest

# Access container shell
podman exec -it dnd_character_api_dev /bin/bash
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

## 🧪 Testing

```bash
# Backend tests
podman exec dnd_character_api_dev python -m pytest -v

# API health check
curl http://localhost:8000/health

# Test character creation
curl -X POST http://localhost:8000/api/v1/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Character", "species": "human", "class": "fighter"}'
```

## 📖 Documentation

- **[Deployment Guide](deployment/README.md)** - Detailed deployment and management
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[Architecture Guide](architecture.txt)** - System design and architecture

## 🔒 Security

- Environment variables for sensitive data
- Podman secrets for API keys
- CORS configuration for web security
- Database password protection

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 3000, 8000, 5432, 11434 are available
2. **GPU not available**: AI image generation requires NVIDIA GPU
3. **Memory issues**: Ensure sufficient RAM for LLM services

### Getting Help

1. Check service logs: `podman-compose logs -f`
2. Verify service status: `podman-compose ps`
3. Review the [Deployment Guide](deployment/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] Enhanced AI character generation
- [ ] Campaign management tools
- [ ] Character sharing and collaboration
- [ ] Mobile-responsive design
- [ ] Advanced custom content editor
- [ ] Integration with virtual tabletop platforms

---

**Note**: This application uses Podman instead of Docker for container orchestration. Make sure you have Podman and podman-compose installed before running the setup scripts.