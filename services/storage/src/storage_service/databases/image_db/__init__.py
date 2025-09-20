"""Image database module.

This module contains the database models and migration code for the Image Service's
data, now managed by the Storage Service.
"""

from .models import Image, Overlay
from .client import ImageDBClient

__all__ = ['Image', 'Overlay', 'ImageDBClient']