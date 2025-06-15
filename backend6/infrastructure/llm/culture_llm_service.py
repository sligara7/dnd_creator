# └── infrastructure/                               # INFRASTRUCTURE LAYER
#     ├── llm/                                      # ✅ EXISTS in your architecture
#     │   ├── culture_llm_service.py                # 🆕 INFRA - LLM Provider Implementation
#     │   ├── openai_culture_client.py              # 🆕 INFRA - OpenAI Implementation
#     │   └── claude_culture_client.py              # 🆕 INFRA - Claude Implementation  
#     ├── repositories/                             # ✅ EXISTS in your architecture
#     │   └── culture_repository.py                 # 🆕 INFRA - Culture Storage
#     └── cache/
#         └── culture_cache.py                      # 🆕 INFRA - Cache Generated Cultures

# Concrete LLM provider implementation
class CultureLLMService(CultureLLMProvider):
    """Infrastructure implementation of culture LLM provider."""
    
    def __init__(self, primary_client: Any, fallback_client: Any):
        self.primary_client = primary_client
        self.fallback_client = fallback_client
    
    async def generate_culture_content(self, prompt: str) -> str:
        """Implementation with fallback logic."""
        try:
            return await self.primary_client.generate(prompt)
        except Exception:
            return await self.fallback_client.generate(prompt)