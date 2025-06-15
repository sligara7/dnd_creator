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

# Use case orchestration
class GenerateCustomCultureUseCase:
    """Orchestrates custom culture generation workflow."""
    
    def __init__(
        self, 
        culture_service: DynamicCultureService,
        culture_repository: CultureRepository,
        llm_provider: CultureLLMProvider
    ):
        self.culture_service = culture_service
        self.culture_repository = culture_repository  
        self.llm_provider = llm_provider
    
    async def execute(self, request: CultureGenerationRequest) -> CultureGenerationResponse:
        """Execute the culture generation use case."""
        # 1. Validate request
        # 2. Check cache
        # 3. Generate culture via domain service
        # 4. Store result
        # 5. Return response
        pass