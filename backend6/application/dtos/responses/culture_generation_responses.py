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

# Response data structures
@dataclass
class CultureGenerationResponse:
    success: bool
    culture_name: str
    culture_instance: Optional[BaseCulture]
    sample_names: Dict[str, List[str]]  
    generation_metadata: Dict[str, Any]
    errors: List[str] = field(default_factory=list)