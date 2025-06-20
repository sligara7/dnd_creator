// needs to interface with the backend api to fetch data. 

// here are the backend details:
// # Build container
// podman build -t dnd-backend .

// # Run container  
// podman run -p 8000:8000 -d --name dnd-backend dnd-backend

// # Access API
// curl http://localhost:8000/docs

// Backend structure:

// backend/
// ├── app.py                    # Main FastAPI application ✅
// ├── main.py                   # Uvicorn entry point ✅
// ├── Dockerfile                # Container configuration ✅
// ├── requirements.txt          # Dependencies ✅
// ├── config.py                 # Configuration ✅
// ├── character_models.py       # Character logic ✅
// ├── database_models.py        # Database operations ✅
// ├── llm_service.py           # LLM integration ✅
// ├── items_creation.py        # Item creation API ✅
// ├── npc_creation.py          # NPC creation API ✅
// ├── creature_creation.py     # Creature creation API ✅
// ├── ability_management.py    # Game mechanics ✅
// ├── core_models.py           # Core D&D models ✅
// ├── custom_content_models.py # Custom content ✅
// ├── generators.py            # Content generators ✅
// └── PRODUCTION_READY.md      # Documentation ✅