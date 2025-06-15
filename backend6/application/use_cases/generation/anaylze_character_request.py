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

# Character concept analysis use case  
class AnalyzeCharacterRequestUseCase:
    """Analyzes user character requests to extract cultural elements."""
    
    async def execute(self, request: CultureAnalysisRequest) -> CultureAnalysisResponse:
        """Extract cultural context from character descriptions."""
        # Parse "I want to create Maui from Moana" 
        # -> Extract: Polynesian, demigod, shapeshifter, oceanic
        pass