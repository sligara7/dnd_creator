"""
Main entry point for the D&D Character Creator application.
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from container import DIContainer
from interfaces.cli.character_creator_cli import CharacterCreatorCLI

def main():
    """Main application entry point."""
    try:
        # Initialize dependency injection container
        container = DIContainer()
        
        # Get CLI interface
        cli = container.get('character_creator_cli')
        
        # Run the application
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Thanks for using D&D Character Creator!")
    except Exception as e:
        print(f"❌ Application error: {e}")
        logging.exception("Unhandled application error")
        sys.exit(1)

if __name__ == "__main__":
    main()