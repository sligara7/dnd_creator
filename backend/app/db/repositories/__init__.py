"""
Repository package for database access.
Implements the repository pattern to abstract database operations.
"""

from backend.app.db.repositories.base_repository import BaseRepository
from backend.app.db.repositories.character_repository import CharacterRepository
from backend.app.db.repositories.user_repository import UserRepository
from backend.app.db.repositories.campaign_repository import CampaignRepository
from backend.app.db.repositories.npc_repository import NPCRepository
from backend.app.db.repositories.session_repository import SessionRepository
from backend.app.db.repositories.journal_repository import JournalRepository

# Export all repository classes
__all__ = [
    "BaseRepository",
    "CharacterRepository",
    "UserRepository",
    "CampaignRepository",
    "NPCRepository",
    "SessionRepository",
    "JournalRepository"
]

# Create repository instances
character_repo = CharacterRepository()
user_repo = UserRepository()
campaign_repo = CampaignRepository()
npc_repo = NPCRepository()
session_repo = SessionRepository()
journal_repo = JournalRepository()

# Export repository instances
repositories = {
    "character": character_repo,
    "user": user_repo,
    "campaign": campaign_repo,
    "npc": npc_repo,
    "session": session_repo,
    "journal": journal_repo
}

# Add repositories dictionary to exports
__all__.append("repositories")