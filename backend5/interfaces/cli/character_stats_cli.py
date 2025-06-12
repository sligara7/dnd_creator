from typing import Dict, Any
from ...application.use_cases.analyze_character import AnalyzeCharacterUseCase
from .cli_utils import CLIFormatter

class CharacterStatsCLI:
    """CLI interface for character statistics."""
    
    def __init__(self, analyze_use_case: AnalyzeCharacterUseCase, formatter: CLIFormatter):
        self.analyze_use_case = analyze_use_case
        self.formatter = formatter
    
    def show_character_stats(self, character_id: str, analysis_type: str = "comprehensive") -> None:
        """Display character statistics."""
        request = CharacterAnalysisRequest(
            character_id=character_id,
            analysis_type=analysis_type
        )
        
        response = self.analyze_use_case.execute(request)
        
        if response.success:
            self.formatter.print_character_statistics(response.statistics, analysis_type)
        else:
            self.formatter.print_errors(response.errors)