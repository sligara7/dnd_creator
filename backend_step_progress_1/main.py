#!/usr/bin/env python3
"""
Main entry point for the D&D Character Creator Backend API.
This file provides a standard entry point for the FastAPI application.
"""

from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
