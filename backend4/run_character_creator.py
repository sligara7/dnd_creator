import sys
import os

# Add the project root to the path
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')

# Import required modules
try:
    from llm_service import OllamaLLMService
    from backend4.character_creator import CharacterCreator
    from character_utils import format_character_summary, save_character
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required files are in place:")
    print("- llm_service.py")
    print("- character_creator_v2.py") 
    print("- character_utils.py")
    print("- character_sheet.py")
    sys.exit(1)


def run_character_creator():
    """Run the character creator with progression options."""
    print("=== D&D Character Creator with Progression ===")
    
    # Initialize services
    llm_service = OllamaLLMService(model="llama3")
    creator = CharacterCreator(llm_service)
    
    if not creator.test_connection():
        print("❌ Failed to connect to LLM. Please make sure your LLM service is running.")
        return
    
    print("✅ Successfully connected to LLM service\n")
    
    # Get creation options
    print("Choose an option:")
    print("1. Create character at specific level")
    print("2. Create full character progression (levels 1-20)")
    print("3. Create progression up to specific level")
    
    choice = input("> ").strip()
    
    # Get character description
    print("\nWhat type of character would you like to create?")
    print("Examples:")
    print("- An elven wizard who specializes in illusion magic")
    print("- A dwarven paladin seeking redemption")
    print("- A half-orc barbarian with a gentle heart")
    description = input("> ")
    
    try:
        if choice == "1":
            # Single level creation
            print("\nWhat level should this character be? (1-20)")
            level = int(input("> "))
            level = max(1, min(20, level))
            
            print(f"\nCreating level {level} character...")
            summary = creator.create_character(description, level)
            print("\n" + format_character_summary(summary))
            
        elif choice == "2":
            # Full progression
            print("\nCreating full character progression (levels 1-20)...")
            progression = creator.create_character_progression(description, 20)
            
            # Show progression summary
            print(creator.preview_progression_summary())
            
            # Ask which level to display in detail
            print("Which level would you like to see in detail? (1-20)")
            display_level = int(input("> "))
            character_data = creator.get_character_at_level(display_level)
            creator.populate_character(character_data)
            summary = creator.character.get_character_summary()
            print(f"\n=== Level {display_level} Character ===")
            print(format_character_summary(summary))
            
        elif choice == "3":
            # Progression up to specific level
            print("\nWhat's the maximum level for progression? (1-20)")
            max_level = int(input("> "))
            max_level = max(1, min(20, max_level))
            
            print(f"\nCreating character progression (levels 1-{max_level})...")
            progression = creator.create_character_progression(description, max_level)
            
            print(creator.preview_progression_summary())
            
            # Show final level by default
            character_data = creator.get_character_at_level(max_level)
            creator.populate_character(character_data)
            summary = creator.character.get_character_summary()
            print(f"\n=== Level {max_level} Character ===")
            print(format_character_summary(summary))
            
        else:
            print("Invalid choice. Please run again.")
            return
        
        # Ask to save
        print("\nWould you like to save this character? (yes/no)")
        if input("> ").lower() in ['yes', 'y']:
            if hasattr(creator, 'character_progression') and creator.character_progression:
                print("Character progression saved!")
            else:
                filename = save_character(summary)
                print(f"Character saved to: {filename}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_character_creator()