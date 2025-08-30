#!/usr/bin/env python3
"""
Main entry point for the D&D Character Creator Backend API.
This file provides a standard entry point for the FastAPI application.
"""

import sys
from pathlib import Path

# Add src directory to path for clean imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
