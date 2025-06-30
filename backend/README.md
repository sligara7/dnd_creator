# D&D Character Creator Backend API

A production-ready FastAPI backend for D&D 5e character creation using a unified factory pattern architecture.

## 🏗️ Architecture

The backend uses a **factory-based pattern** that provides:
- ✅ **Unified Creation API** - Single endpoint for all content types
- ✅ **Factory Pattern** - Centralized creation logic with type-specific specialization  
- ✅ **LLM Integration** - OpenAI/Anthropic/Ollama support for AI-generated content
- ✅ **D&D 5e 2024 Rules** - Latest official ruleset compliance
- ✅ **Character Versioning** - Git-like character evolution tracking

## 🚀 Quick Start with Podman

### 1. Build & Run
```bash
./build.sh
```

### 2. Manual Container Commands
```bash
# Build
podman build -t dnd-character-creator-backend:latest .

# Run
podman run -d --name dnd-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  dnd-character-creator-backend:latest

# View logs
podman logs -f dnd-backend
```

### 3. Access API
- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📡 API Endpoints

### Factory Pattern (Primary Interface)
- `POST /api/v2/factory/create` - Create any D&D content type
- `POST /api/v2/factory/evolve` - Evolve character with history 
- `POST /api/v2/factory/level-up` - Character leveling
- `GET /api/v2/factory/types` - Available content types

### Character Management
- `POST /api/v1/characters` - Create character
- `GET /api/v1/characters` - List characters  
- `GET /api/v1/characters/{id}` - Get character
- `PUT /api/v1/characters/{id}` - Update character
- `DELETE /api/v1/characters/{id}` - Delete character

### Generation Workflows
- `POST /api/v1/generate/content` - Unified content generation
- `POST /api/v1/generate/character-complete` - Complete character workflow

## 🎯 Usage Examples

### Create a Character
```bash
curl -X POST "http://localhost:8000/api/v2/factory/create" \
  -H "Content-Type: application/json" \
  -d '{
    "creation_type": "character",
    "prompt": "Create a halfling rogue from a criminal background",
    "save_to_database": true
  }'
```

### Create Equipment
```bash
curl -X POST "http://localhost:8000/api/v2/factory/create" \
  -H "Content-Type: application/json" \
  -d '{
    "creation_type": "weapon", 
    "prompt": "A magical longsword that glows with inner fire"
  }'
```

### Create NPCs
```bash
curl -X POST "http://localhost:8000/api/v2/factory/create" \
  -H "Content-Type: application/json" \
  -d '{
    "creation_type": "npc",
    "prompt": "A wise old tavern keeper with secrets"
  }'
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Database (SQLite by default)
DATABASE_URL=  # Leave empty for SQLite
SQLITE_PATH=data/dnd_characters.db

# LLM Service (Optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Server
ENV=production
DEBUG=false
```

### Volume Mounts
- `/app/data` - Database and persistent data
- `/app/logs` - Application logs (optional)

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure
```
backend/
├── app.py              # Main FastAPI application
├── main.py             # Entry point
├── creation_factory.py # Factory pattern implementation
├── creation.py         # Creation logic (unified)
├── character_models.py # D&D character models
├── database_models.py  # Database schemas
├── config.py          # Configuration
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container definition
├── data/             # Database and persistent data
├── docs/             # Documentation
└── examples/         # Example code and demos
```

## 📚 Documentation

- **API Docs:** Available at `/docs` when running
- **Factory Pattern:** See `docs/FACTORY_PATTERN_RECOMMENDATIONS.md`
- **Phase 4 Migration:** See `docs/PHASE_4_CLEANUP_COMPLETE.md`
- **Production Guide:** See `docs/PRODUCTION_READY.md`

## 🛠️ Content Types Supported

Via the factory pattern (`/api/v2/factory/create`):
- **Characters** - Full D&D 5e character sheets
- **NPCs** - Non-player characters with roles and stats
- **Monsters** - Creatures with stat blocks and abilities
- **Weapons** - Magical and mundane weapons
- **Armor** - All armor types and magical variants
- **Spells** - Custom spells with proper mechanics
- **Other Items** - Potions, scrolls, tools, etc.

## 🔒 Security

- ✅ Non-root container user
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configuration for frontend integration
- ✅ Health check endpoints for monitoring

## 📊 Monitoring

- **Health Check:** `GET /health`
- **Metrics:** Available via container logs
- **Status:** `GET /` returns service status

## 🏷️ Version

**Current Version:** 2.0.0 (Factory Pattern Architecture)  
**Previous Versions:** Legacy individual creator endpoints removed in Phase 4

