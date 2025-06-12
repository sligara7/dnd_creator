from typing import List, Optional, Union, Any
from colorama import init, Fore, Style
import sys

# Initialize colorama for cross-platform colored output
init()

class CLIFormatter:
    """Utility class for formatting CLI output."""
    
    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{text:^50}")
        print(f"{'='*50}{Style.RESET_ALL}\n")
    
    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    
    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    def print_info(self, text: str) -> None:
        """Print info message."""
        print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")
    
    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
    
    def print_examples(self, examples: List[str]) -> None:
        """Print example list."""
        print(f"{Fore.YELLOW}Examples:{Style.RESET_ALL}")
        for example in examples:
            print(f"  • {example}")
    
    def print_errors(self, errors: List[str]) -> None:
        """Print list of errors."""
        for error in errors:
            self.print_error(error)
    
    def print_character_summary(self, character: Any, level: Optional[int] = None) -> None:
        """Print formatted character summary."""
        # This would format the character data nicely
        if level:
            print(f"\n{Fore.CYAN}=== Level {level} Character ==={Style.RESET_ALL}")
        else:
            print(f"\n{Fore.CYAN}=== Character Summary ==={Style.RESET_ALL}")
        
        # Format character details here
        # This is where you'd implement the formatting logic
        print("Character details would be formatted here...")
    
    def print_progression_summary(self, progression: Any) -> None:
        """Print formatted progression summary."""
        print(f"\n{Fore.CYAN}=== Character Progression Summary ==={Style.RESET_ALL}")
        # Format progression details here
        print("Progression summary would be formatted here...")

def display_menu(title: str, options: List[str]) -> None:
    """Display a numbered menu."""
    print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

def get_user_input(prompt: str, 
                  validate_numeric: bool = False,
                  min_val: Optional[int] = None,
                  max_val: Optional[int] = None,
                  yes_no: bool = False) -> Union[str, int, bool]:
    """Get validated user input."""
    while True:
        try:
            response = input(f"\n{prompt}: ").strip()
            
            if yes_no:
                if response.lower() in ['yes', 'y', 'true', '1']:
                    return True
                elif response.lower() in ['no', 'n', 'false', '0']:
                    return False
                else:
                    print("Please enter 'yes' or 'no'")
                    continue
            
            if validate_numeric:
                value = int(response)
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                return value
            
            if not response:
                print("Please provide a value")
                continue
                
            return response
            
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            sys.exit(0)