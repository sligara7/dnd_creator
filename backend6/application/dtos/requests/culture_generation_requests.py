# ├── application/                                  # APPLICATION LAYER
# │   ├── dtos/                                     # ✅ EXISTS in your architecture
# │   │   ├── requests/
# │   │   │   └── culture_generation_requests.py    # 🆕 APP - Request DTOs  
# │   │   └── responses/
# │   │       └── culture_generation_responses.py   # 🆕 APP - Response DTOs
# │   ├── use_cases/                                # ✅ EXISTS in your architecture
# │   │   └── generation/                           # ✅ EXISTS in your architecture
# │   │       ├── generate_custom_culture.py        # 🆕 APP - Business Logic Orchestration
# │   │       └── analyze_character_request.py      # 🆕 APP - Parse User Intent
# │   └── services/                                 # ✅ EXISTS in your architecture  
# │       └── culture_orchestrator.py               # 🆕 APP - Culture Generation Coordination

# Request data structures
@dataclass
class CultureGenerationRequest:
    cultural_reference: str
    creativity_level: CreativityLevel
    authenticity_requirements: List[str]
    user_session_id: Optional[str] = None

@dataclass  
class CultureAnalysisRequest:
    character_description: str
    extract_cultural_elements: bool = True