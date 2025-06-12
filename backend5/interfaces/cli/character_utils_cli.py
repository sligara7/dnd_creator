from typing import Optional
from ...application.use_cases.character_utilities import CharacterUtilitiesUseCase
from ...core.utils.character_utils import CharacterFormatter
from .cli_utils import CLIFormatter

class CharacterUtilitiesCLI:
    """CLI interface for character utilities."""
    
    def __init__(self, utilities_use_case: CharacterUtilitiesUseCase, 
                 formatter: CLIFormatter):
        self.utilities_use_case = utilities_use_case
        self.formatter = formatter
    
    def save_character(self, character_id: str, filename: Optional[str] = None) -> None:
        """Save character to file via CLI."""
        response = self.utilities_use_case.save_character_to_file(character_id, filename)
        
        if response.success:
            self.formatter.print_success(response.message)
        else:
            self.formatter.print_errors(response.errors)
    
    def show_character_summary(self, character_id: str) -> None:
        """Display formatted character summary."""
        # Implementation using CharacterFormatter
        pass