# backend/config.py
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RULES_DIR = DATA_DIR / "rules"

# LLM settings
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3")

# Validation settings
VALIDATION_STRICTNESS = os.environ.get("VALIDATION_STRICTNESS", "standard")

# Storage settings
STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "sqlite")
DB_PATH = DATA_DIR / "characters.db"