"""
D&D Character Creator - Root Package

A background-driven creative content framework for D&D 2024 that generates 
balanced, thematic, and rule-compliant characters and content.
"""

__version__ = "0.1.0-dev"
__author__ = "D&D Character Creator Team"
__description__ = "Background-driven D&D character creation with custom content generation"

# Project metadata
PROJECT_NAME = "dnd-char-creator"
PROJECT_VERSION = __version__
SUPPORTED_DND_VERSION = "2024"

# Core configuration constants
DEFAULT_BACKEND_VERSION = "backend6"
CORE_LAYER_PATH = f"{DEFAULT_BACKEND_VERSION}/core"

class ProjectInfo:
    """Project information and metadata."""
    
    @staticmethod
    def get_project_info():
        """Get project information dictionary."""
        return {
            "name": PROJECT_NAME,
            "version": PROJECT_VERSION,
            "description": __description__,
            "dnd_version": SUPPORTED_DND_VERSION,
            "backend_version": DEFAULT_BACKEND_VERSION,
            "status": "Core Layer Development (Work in Progress)"
        }
    
    @staticmethod
    def get_development_status():
        """Get current development status."""
        return {
            "phase": "Core Layer Development",
            "backend_focus": DEFAULT_BACKEND_VERSION,
            "architecture": "Clean Architecture",
            "completion": {
                "core_layer": "In Development",
                "domain_layer": "Planned",
                "application_layer": "Planned", 
                "infrastructure_layer": "Planned"
            }
        }

# Export project info for easy access
def get_project_info():
    """Get project information."""
    return ProjectInfo.get_project_info()

def get_development_status():
    """Get development status."""
    return ProjectInfo.get_development_status()

# Note: Specific backend implementations should be imported directly
# Example: from backend6.core import CoreLayerInterface