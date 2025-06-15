# └── infrastructure/                               # INFRASTRUCTURE LAYER
#     ├── llm/                                      # ✅ EXISTS in your architecture
#     │   ├── culture_llm_service.py                # 🆕 INFRA - LLM Provider Implementation
#     │   ├── openai_culture_client.py              # 🆕 INFRA - OpenAI Implementation
#     │   └── claude_culture_client.py              # 🆕 INFRA - Claude Implementation  
#     ├── repositories/                             # ✅ EXISTS in your architecture
#     │   └── culture_repository.py                 # 🆕 INFRA - Culture Storage
#     └── cache/
#         └── culture_cache.py                      # 🆕 INFRA - Cache Generated Cultures