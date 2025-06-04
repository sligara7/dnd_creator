D&D Character Creator
An AI-enhanced D&D character creator that helps players build balanced characters while adhering to D&D 5e rules (2024 edition).

Overview
This project combines modern web technologies with AI capabilities to create an immersive D&D character creation experience. The system guides players through character creation using AI prompts, validates rule adherence, and generates character portraits.

Features
AI-Guided Character Creation: Step-by-step creation process with Llama 3 guidance
Rules Adherence: Automatic validation against D&D 5e (2024) ruleset
Character Portrait Generation: AI-generated character visualization using Stable Diffusion
DM Approval Workflow: Streamlined process for DM review and approval
Character Management: Full lifecycle support including leveling up
Journal System: Track character evolution through "waypoints" and game events
AI-Powered Summaries: LLM-generated summaries of gameplay events
Tech Stack
Frontend: React with TailwindCSS
Backend: FastAPI (Python)
Database: MongoDB
AI Services:
Ollama with Llama 3 (8B) for character creation guidance
Stable Diffusion for character visualization
Architecture
The system consists of three main components:

Frontend: React-based UI for character creation, DM dashboard, and journals
Backend: FastAPI service handling core logic and database interactions
AI Services: Docker-containerized Ollama and Stable Diffusion instances
Setup and Installation
Prerequisites
Docker and Docker Compose
4GB+ VRAM for Stable Diffusion (CPU-only option available for Llama 3)
Installation
Clone the repository:

Run the setup script:

Start the services:

API Endpoints
/api/ai/character-guidance: Access Llama 3 suggestions for character creation
/api/ai/generate-portrait: Generate character portraits based on character details
Future Features
Journal event illustrations using Stable Diffusion
DM tools for generating maps, towns, battle scenes, and dungeons with AI
Development
Check architecture.txt for detailed information about the project structure and components.

Testing backend/core functions:
cd /home/ajs7/dnd_tools/dnd_char_creator
python -m pytest backend/tests

For specific tests:
python -m pytest backend/tests/test_character_creation.py