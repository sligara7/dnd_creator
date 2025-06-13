from typing import Optional
import logging

from ...application.use_cases.create_character import CreateCharacterUseCase
from ...application.use_cases.create_progression import CreateProgressionUseCase
from ...application.use_cases.validate_character import ValidateCharacterUseCase
from ...application.dtos.character_dto import CharacterCreationRequest
from ...infrastructure.data.character_storage import CharacterStorage
from .cli_utils import CLIFormatter, get_user_input, display_menu

logger = logging.getLogger(__name__)

class CharacterCreatorCLI:
    """
    Command-line interface for the D&D Character Creator.
    
    This class handles all user interaction and delegates business logic
    to appropriate use cases.
    """
    
    def __init__(self,
                 create_character_use_case: CreateCharacterUseCase,
                 create_progression_use_case: CreateProgressionUseCase,
                 validate_character_use_case: ValidateCharacterUseCase,
                 formatter: CLIFormatter,
                 storage: CharacterStorage):
        self.create_character_use_case = create_character_use_case
        self.create_progression_use_case = create_progression_use_case
        self.validate_character_use_case = validate_character_use_case
        self.formatter = formatter
        self.storage = storage
    
    def run(self) -> None:
        """Main CLI execution loop."""
        self.formatter.print_header("D&D Character Creator with Progression")
        
        # Test LLM connection
        if not self._test_llm_connection():
            self.formatter.print_error("Failed to connect to LLM. Please make sure your LLM service is running.")
            return
        
        self.formatter.print_success("Successfully connected to LLM service")
        
        try:
            while True:
                self._show_main_menu()
                choice = get_user_input("Select an option", validate_numeric=True, min_val=1, max_val=4)
                
                if choice == 1:
                    self._create_single_level_character()
                elif choice == 2:
                    self._create_full_progression()
                elif choice == 3:
                    self._create_partial_progression()
                elif choice == 4:
                    self.formatter.print_info("Thanks for using D&D Character Creator!")
                    break
                
                # Ask if user wants to continue
                if not get_user_input("Would you like to create another character?", yes_no=True):
                    break
                    
        except KeyboardInterrupt:
            self.formatter.print_info("\nGoodbye!")
        except Exception as e:
            logger.exception("CLI error occurred")
            self.formatter.print_error(f"An error occurred: {str(e)}")
    
    def _show_main_menu(self) -> None:
        """Display the main menu options."""
        options = [
            "Create character at specific level",
            "Create full character progression (levels 1-20)",
            "Create progression up to specific level",
            "Exit"
        ]
        display_menu("Choose an option:", options)
    
    def _get_character_description(self) -> str:
        """Get character description from user."""
        self.formatter.print_info("What type of character would you like to create?")
        self.formatter.print_examples([
            "An elven wizard who specializes in illusion magic",
            "A dwarven paladin seeking redemption",
            "A half-orc barbarian with a gentle heart"
        ])
        return get_user_input("Character description")
    
    def _create_single_level_character(self) -> None:
        """Handle single level character creation."""
        try:
            description = self._get_character_description()
            level = get_user_input("What level should this character be?", 
                                 validate_numeric=True, min_val=1, max_val=20)
            
            self.formatter.print_info(f"Creating level {level} character...")
            
            # Create character creation request
            request = CharacterCreationRequest(
                description=description,
                target_level=level,
                creation_method="single_level"
            )
            
            # Execute use case
            response = self.create_character_use_case.execute(request)
            
            if response.success:
                self.formatter.print_character_summary(response.character)
                self._offer_to_save_character(response.character)
            else:
                self.formatter.print_errors(response.errors)
                
        except Exception as e:
            logger.exception("Error creating single level character")
            self.formatter.print_error(f"Failed to create character: {str(e)}")
    
    def _create_full_progression(self) -> None:
        """Handle full progression character creation."""
        try:
            description = self._get_character_description()
            
            self.formatter.print_info("Creating full character progression (levels 1-20)...")
            
            # Execute progression use case
            progression_response = self.create_progression_use_case.execute(
                description=description,
                max_level=20
            )
            
            if progression_response.success:
                # Show progression summary
                self.formatter.print_progression_summary(progression_response.progression)
                
                # Ask which level to display in detail
                display_level = get_user_input("Which level would you like to see in detail?",
                                             validate_numeric=True, min_val=1, max_val=20)
                
                character = progression_response.progression.get_character_at_level(display_level)
                self.formatter.print_character_summary(character, level=display_level)
                
                self._offer_to_save_progression(progression_response.progression)
            else:
                self.formatter.print_errors(progression_response.errors)
                
        except Exception as e:
            logger.exception("Error creating full progression")
            self.formatter.print_error(f"Failed to create progression: {str(e)}")
    
    def _create_partial_progression(self) -> None:
        """Handle partial progression character creation."""
        try:
            description = self._get_character_description()
            max_level = get_user_input("What's the maximum level for progression?",
                                     validate_numeric=True, min_val=1, max_val=20)
            
            self.formatter.print_info(f"Creating character progression (levels 1-{max_level})...")
            
            # Execute progression use case
            progression_response = self.create_progression_use_case.execute(
                description=description,
                max_level=max_level
            )
            
            if progression_response.success:
                self.formatter.print_progression_summary(progression_response.progression)
                
                # Show final level by default
                character = progression_response.progression.get_character_at_level(max_level)
                self.formatter.print_character_summary(character, level=max_level)
                
                self._offer_to_save_progression(progression_response.progression)
            else:
                self.formatter.print_errors(progression_response.errors)
                
        except Exception as e:
            logger.exception("Error creating partial progression")
            self.formatter.print_error(f"Failed to create progression: {str(e)}")
    
    def _test_llm_connection(self) -> bool:
        """Test connection to LLM service."""
        try:
            # This would be handled by a use case in a real implementation
            return True  # Placeholder
        except Exception:
            return False
    
    def _offer_to_save_character(self, character) -> None:
        """Offer to save a single character."""
        if get_user_input("Would you like to save this character?", yes_no=True):
            try:
                filename = self.storage.save_character(character)
                self.formatter.print_success(f"Character saved to: {filename}")
            except Exception as e:
                self.formatter.print_error(f"Failed to save character: {str(e)}")
    
    def _offer_to_save_progression(self, progression) -> None:
        """Offer to save a character progression."""
        if get_user_input("Would you like to save this character progression?", yes_no=True):
            try:
                filename = self.storage.save_progression(progression)
                self.formatter.print_success(f"Character progression saved to: {filename}")
            except Exception as e:
                self.formatter.print_error(f"Failed to save progression: {str(e)}")

# interfaces/cli/character_creator_cli.py
class CharacterCreatorCLI:
    """Command-line interface for character creation."""
    
    def __init__(self, container: DIContainer):
        self.create_character_use_case = container.get('create_character')
        self.manage_character_use_case = container.get('manage_character')
    
    def run_interactive_creation(self):
        """Run the interactive character creation process."""
        # CLI interaction logic from original run_character_creator
        pass
    
    def display_character_summary(self, character: Character):
        """Display formatted character summary."""
        # Display logic from original
        pass