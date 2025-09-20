"""Campaign database module.

This module contains the database models and migration code for the Campaign Service's
data, now managed by the Storage Service.
"""

from .models import Campaign, Chapter
from .client import CampaignDBClient

__all__ = ['Campaign', 'Chapter', 'CampaignDBClient']