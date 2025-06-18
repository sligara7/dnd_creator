# ## **12. `user_interface.py`**
# **Presentation layer for user interaction**
# - **Functions**: `interactive_character_creation`, user input/output functions
# - **Purpose**: User interface, menu system, user interaction
# - **Dependencies**: `character_creation.py`, `formatting.py`, `file_operations.py`

import time
from utilities import determine_level_from_description

def interactive_character_creation():
    """Enhanced interactive character creation with setup checking."""
    print("🎲 D&D Enhanced Character Creator 🎲")
    print("=" * 50)
    
    # Check Ollama setup first
    print("🔍 Checking Ollama setup...")
    setup_status = check_ollama_setup()
    
    if setup_status["issues"]:
        print("\n❌ SETUP ISSUES DETECTED:")
        for issue in setup_status["issues"]:
            print(f"  • {issue}")
        
        print("\n💡 RECOMMENDED SOLUTIONS:")
        for i, solution in enumerate(setup_status["solutions"], 1):
            print(f"  {i}. {solution}")
        
        # Ask if user wants to continue anyway
        if not input("\nTry to continue anyway? (y/n): ").lower().startswith('y'):
            return
    
    try:
        creator = create_character_service()
    except Exception as e:
        print(f"\n❌ Failed to initialize character creator: {e}")
        return
    
    print("✅ Character creation service ready")
    print()
    
    # Get user input
    print("Describe your character concept:")
    print("(Be as detailed as you like - mention personality, background, abilities, level, etc.)")
    description = input("> ")
    
    if not description.strip():
        print("No description provided. Using default...")
        description = "A brave adventurer seeking to make their mark on the world"
    
    # Determine level
    level = determine_level_from_description(description)
    print(f"📊 Determined character level: {level}")
    
    print(f"\n⏰ ESTIMATED TIME: 30-60 seconds total")
    print("- Character data: ~20 seconds")
    print("- Backstory: ~15 seconds") 
    print("- Custom content: ~30 seconds")
    print("\n" + "="*50)
    print("🎭 CREATING YOUR CHARACTER...")
    print("="*50)
    
    # Create character
    start_time = time.time()
    try:
        summary = creator.create_character_iteratively(description, level, generate_custom_content=True)
        end_time = time.time()
        
        print(f"\n⏱️  Total generation time: {end_time - start_time:.1f} seconds")
        
        # Show creation stats
        stats = creator.get_creation_stats()
        print(f"📊 Creation completed in {stats['iterations']} iterations")
        
        print("\n" + format_character_summary(summary))
        
        # Save options
        print("\n" + "="*30)
        print("SAVE OPTIONS")
        print("="*30)
        
        save_choice = input("Save character data? (y/n): ")
        if save_choice.lower().startswith('y'):
            filename = save_character(summary)
            print(f"✅ Character data saved: {filename}")
        
        backstory_choice = input("Save backstory as text file? (y/n): ")
        if backstory_choice.lower().startswith('y'):
            backstory_file = save_backstory_as_text(summary)
            print(f"✅ Backstory saved: {backstory_file}")
        
        sheet_choice = input("Export complete character sheet? (y/n): ")
        if sheet_choice.lower().startswith('y'):
            sheet_file = export_character_sheet(summary)
            print(f"✅ Character sheet exported: {sheet_file}")
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"Character creation failed after {end_time - start_time:.1f} seconds: {e}")
        print(f"❌ Character creation failed: {e}")
        print("💡 Try a simpler character description or check your Ollama connection")