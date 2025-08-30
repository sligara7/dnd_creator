"""
Campaign Creation Models Package
==============================

Comprehensive models for D&D campaign creation including:
- Core D&D mechanics and utilities
- Campaign creation API models  
- Database models and access layer
"""

# Core D&D models and utilities
from .core_models import (
    # Enums
    AbilityScore, Skill, DamageType, CreatureSize, CreatureType,
    Environment, EncounterDifficulty,
    
    # Classes
    ChallengeRating, AbilityScoreUtils, EncounterBuilder,
    CharacterStatistics, CampaignBalanceUtils
)

# Campaign creation API models
from .campaign_creation_models import (
    CampaignCreationType, BaseCampaignRequest, CampaignFromScratchRequest,
    CampaignSkeletonRequest, ChapterContentRequest, CampaignRefinementRequest,
    PsychologicalExperimentRequest, SettingThemeRequest,
    CharacterForCampaignRequest, CampaignCreationResponse, CampaignRefinementResponse
)

# Database models (import key classes)
from .database_models import CampaignDB

__all__ = [
    # Core models
    'AbilityScore', 'Skill', 'DamageType', 'CreatureSize', 'CreatureType',
    'Environment', 'EncounterDifficulty', 'ChallengeRating', 'AbilityScoreUtils',
    'EncounterBuilder', 'CharacterStatistics', 'CampaignBalanceUtils',
    
    # Campaign creation models
    'CampaignCreationType', 'BaseCampaignRequest', 'CampaignFromScratchRequest',
    'CampaignSkeletonRequest', 'ChapterContentRequest', 'CampaignRefinementRequest',
    'PsychologicalExperimentRequest', 'SettingThemeRequest',
    'CharacterForCampaignRequest', 'CampaignCreationResponse', 'CampaignRefinementResponse',
    
    # Database access
    'CampaignDB'
]
