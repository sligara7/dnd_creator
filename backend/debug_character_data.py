#!/usr/bin/env python3
"""
Debug script to check actual character data from database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database_models import SessionLocal, Character, init_database
from src.core.config import settings
import uuid

# Initialize database
database_url = settings.effective_database_url
init_database(database_url)

session = SessionLocal()

# Get the last created character (Fighter)
characters = session.query(Character).order_by(Character.created_at.desc()).limit(2).all()

for i, character in enumerate(characters):
    print(f"Character {i+1}:")
    print(f"  ID: {character.id}")
    print(f"  Name: {character.name}")
    print(f"  Classes: {character.character_classes}")
    print(f"  Species: {character.species}")
    
    # Check what fields are available
    print(f"  Available attributes: {[attr for attr in dir(character) if not attr.startswith('_')]}")
    
    # Prepare character data like the service does
    character_data = {
        "character_classes": character.character_classes or {},
        "weapon_proficiencies": getattr(character, 'weapon_proficiencies', []),
        "armor_proficiencies": getattr(character, 'armor_proficiencies', []),
        "tool_proficiencies": getattr(character, 'tool_proficiencies', {}),
        "level": sum((character.character_classes or {}).values()) or 1
    }
    
    print(f"  Prepared data: {character_data}")
    print()

session.close()
