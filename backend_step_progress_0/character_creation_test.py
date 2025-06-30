#!/usr/bin/env python3
"""
Interactive Character Creation Test - User Experience Testing

A command-line interface for testing D&D character creation step by step.
This lets you experience the character creation process as envisioned.

Usage:
    python character_creation_test.py
    
Or in iPython:
    %run character_creation_test.py
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from character_models import CharacterCore, DnDCondition
    from core_models import ProficiencyLevel
    print("✅ Character models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import character models: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class InteractiveCharacterCreator:
    """Interactive character creation for testing."""
    
    def __init__(self):
        self.character = None
        self.creation_steps = [
            ("Basic Info", self.set_basic_info),
            ("Species", self.set_species),
            ("Background", self.set_background),
            ("Character Classes", self.set_character_classes),
            ("Ability Scores", self.set_ability_scores),
            ("Skills", self.set_skills),
            ("Equipment", self.set_equipment),
            ("Personality", self.set_personality),
            ("Review", self.review_character)
        ]
        
    def start_creation(self):
        """Start the interactive character creation process."""
        print("🎲 D&D Character Creator - Interactive Test")
        print("=" * 50)
        print("Let's create a character step by step!")
        print("(Press Enter to use defaults, or type 'quit' to exit)\n")
        
        # Initialize character
        name = self.get_input("Character Name", "Test Hero")
        if name.lower() == 'quit':
            return
            
        self.character = CharacterCore(name=name)
        print(f"✅ Created character: {self.character.name}\n")
        
        # Walk through creation steps
        for step_name, step_func in self.creation_steps:
            print(f"📋 Step: {step_name}")
            print("-" * 20)
            
            try:
                if not step_func():
                    print("Character creation cancelled.")
                    return
            except KeyboardInterrupt:
                print("\nCharacter creation cancelled.")
                return
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                continue
                
            print()  # Add spacing between steps
        
        print("🎉 Character creation complete!")
        self.display_final_character()
        
    def get_input(self, prompt: str, default: str = "") -> str:
        """Get user input with default value."""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    
    def get_number_input(self, prompt: str, default: int, min_val: int = 1, max_val: int = 30) -> int:
        """Get numeric input with validation."""
        while True:
            try:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
                if user_input.lower() == 'quit':
                    return -1
                    
                value = int(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def set_basic_info(self) -> bool:
        """Set basic character information."""
        # Character name is already set
        print(f"Character: {self.character.name}")
        
        # Alignment
        print("\nAlignment options:")
        alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral", 
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]
        
        for i, alignment in enumerate(alignments, 1):
            print(f"  {i}. {alignment}")
        
        choice = self.get_input("Choose alignment (1-9)", "5")
        if choice.lower() == 'quit':
            return False
            
        try:
            alignment_idx = int(choice) - 1
            if 0 <= alignment_idx < len(alignments):
                alignment_parts = alignments[alignment_idx].split()
                if len(alignment_parts) == 2:
                    self.character.alignment = alignment_parts
                else:
                    self.character.alignment = ["True", "Neutral"]
            else:
                self.character.alignment = ["True", "Neutral"]
        except ValueError:
            self.character.alignment = ["True", "Neutral"]
            
        print(f"✅ Alignment: {' '.join(self.character.alignment)}")
        return True
    
    def set_species(self) -> bool:
        """Set character species."""
        species_options = [
            "Human", "Elf", "Dwarf", "Halfling", "Dragonborn",
            "Gnome", "Half-Elf", "Half-Orc", "Tiefling", "Aasimar"
        ]
        
        print("Species options:")
        for i, species in enumerate(species_options, 1):
            print(f"  {i}. {species}")
        
        choice = self.get_input("Choose species (1-10)", "1")
        if choice.lower() == 'quit':
            return False
            
        try:
            species_idx = int(choice) - 1
            if 0 <= species_idx < len(species_options):
                self.character.species = species_options[species_idx]
            else:
                self.character.species = "Human"
        except ValueError:
            self.character.species = "Human"
            
        print(f"✅ Species: {self.character.species}")
        return True
    
    def set_background(self) -> bool:
        """Set character background."""
        background_options = [
            "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage",
            "Soldier", "Charlatan", "Entertainer", "Guild Artisan", "Hermit"
        ]
        
        print("Background options:")
        for i, bg in enumerate(background_options, 1):
            print(f"  {i}. {bg}")
        
        choice = self.get_input("Choose background (1-10)", "6")
        if choice.lower() == 'quit':
            return False
            
        try:
            bg_idx = int(choice) - 1
            if 0 <= bg_idx < len(background_options):
                self.character.background = background_options[bg_idx]
            else:
                self.character.background = "Soldier"
        except ValueError:
            self.character.background = "Soldier"
            
        print(f"✅ Background: {self.character.background}")
        return True
    
    def set_character_classes(self) -> bool:
        """Set character classes and levels."""
        class_options = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
            "Warlock", "Wizard", "Artificer"
        ]
        
        print("Class options:")
        for i, cls in enumerate(class_options, 1):
            print(f"  {i}. {cls}")
        
        choice = self.get_input("Choose primary class (1-13)", "5")
        if choice.lower() == 'quit':
            return False
            
        try:
            class_idx = int(choice) - 1
            if 0 <= class_idx < len(class_options):
                chosen_class = class_options[class_idx]
            else:
                chosen_class = "Fighter"
        except ValueError:
            chosen_class = "Fighter"
        
        level = self.get_number_input("Character level", 1, 1, 20)
        if level == -1:
            return False
            
        self.character.character_classes = {chosen_class: level}
        print(f"✅ Class: {chosen_class} {level}")
        
        # Ask about multiclassing
        if level > 1:
            multiclass = self.get_input("Add multiclass? (y/n)", "n").lower()
            if multiclass == 'y':
                print("\nSecondary class:")
                for i, cls in enumerate(class_options, 1):
                    if cls != chosen_class:
                        print(f"  {i}. {cls}")
                
                choice2 = self.get_input("Choose secondary class", "")
                if choice2 and choice2.lower() != 'quit':
                    try:
                        class2_idx = int(choice2) - 1
                        if 0 <= class2_idx < len(class_options):
                            chosen_class2 = class_options[class2_idx]
                            if chosen_class2 != chosen_class:
                                level2 = self.get_number_input(f"{chosen_class2} level", 1, 1, level-1)
                                if level2 > 0:
                                    self.character.character_classes[chosen_class2] = level2
                                    # Adjust primary class level
                                    self.character.character_classes[chosen_class] = level - level2
                                    print(f"✅ Multiclass: {chosen_class} {level - level2}, {chosen_class2} {level2}")
                    except ValueError:
                        pass
        
        return True
    
    def set_ability_scores(self) -> bool:
        """Set ability scores."""
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        
        print("Ability Score Assignment")
        print("Choose method:")
        print("  1. Point Buy (27 points)")
        print("  2. Standard Array (15,14,13,12,10,8)")
        print("  3. Manual Entry")
        
        method = self.get_input("Method (1-3)", "2")
        if method.lower() == 'quit':
            return False
        
        if method == "1":
            # Point Buy
            print("\nPoint Buy System (27 points total)")
            print("Cost: 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9 points")
            remaining_points = 27
            
            for i, ability in enumerate(abilities):
                current_score = 8
                while True:
                    cost_map = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}
                    score = self.get_number_input(
                        f"{ability_names[i]} (8-15, {remaining_points} points left)", 
                        current_score, 8, 15
                    )
                    if score == -1:
                        return False
                    
                    cost = cost_map.get(score, 0)
                    if cost <= remaining_points:
                        self.character.set_ability_score(ability, score)
                        remaining_points -= cost
                        print(f"✅ {ability_names[i]}: {score} (cost: {cost})")
                        break
                    else:
                        print(f"Not enough points! Cost: {cost}, Available: {remaining_points}")
                        
        elif method == "2":
            # Standard Array
            standard_scores = [15, 14, 13, 12, 10, 8]
            print(f"\nStandard Array: {standard_scores}")
            print("Assign these scores to abilities:")
            
            used_scores = []
            for i, ability in enumerate(abilities):
                available = [s for s in standard_scores if s not in used_scores]
                print(f"Available scores: {available}")
                
                score = self.get_number_input(f"{ability_names[i]} score", available[0])
                if score == -1:
                    return False
                    
                if score in available:
                    self.character.set_ability_score(ability, score)
                    used_scores.append(score)
                    print(f"✅ {ability_names[i]}: {score}")
                else:
                    print("Score not available, using default")
                    self.character.set_ability_score(ability, available[0])
                    used_scores.append(available[0])
                    print(f"✅ {ability_names[i]}: {available[0]}")
        else:
            # Manual Entry
            print("\nManual Ability Score Entry:")
            for i, ability in enumerate(abilities):
                score = self.get_number_input(f"{ability_names[i]} (3-20)", 10, 3, 20)
                if score == -1:
                    return False
                self.character.set_ability_score(ability, score)
                print(f"✅ {ability_names[i]}: {score}")
        
        # Show modifiers
        print("\nAbility Modifiers:")
        modifiers = self.character.get_ability_modifiers()
        for ability, modifier in modifiers.items():
            ability_score_obj = self.character.get_ability_score(ability)
            score = ability_score_obj.total_score if ability_score_obj else 10
            sign = "+" if modifier >= 0 else ""
            print(f"  {ability.title():13}: {score} ({sign}{modifier})")
        
        return True
    
    def set_skills(self) -> bool:
        """Set skill proficiencies."""
        # This is a simplified version - in a full implementation you'd 
        # check class and background skill options
        skills = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics",
            "Deception", "History", "Insight", "Intimidation",
            "Investigation", "Medicine", "Nature", "Perception",
            "Performance", "Persuasion", "Religion", "Sleight of Hand",
            "Stealth", "Survival"
        ]
        
        print("Skill Proficiencies (choose 2-4 skills)")
        for i, skill in enumerate(skills, 1):
            print(f"  {i:2d}. {skill}")
        
        num_skills = self.get_number_input("Number of skills to choose", 4, 2, 6)
        if num_skills == -1:
            return False
        
        chosen_skills = []
        for i in range(num_skills):
            choice = self.get_input(f"Skill {i+1} (1-{len(skills)})", str(i+1))
            if choice.lower() == 'quit':
                return False
                
            try:
                skill_idx = int(choice) - 1
                if 0 <= skill_idx < len(skills):
                    skill_name = skills[skill_idx].lower().replace(" ", "_")
                    self.character.skill_proficiencies[skill_name] = ProficiencyLevel.PROFICIENT
                    chosen_skills.append(skills[skill_idx])
            except ValueError:
                pass
        
        print(f"✅ Skill Proficiencies: {', '.join(chosen_skills)}")
        return True
    
    def set_equipment(self) -> bool:
        """Set starting equipment."""
        print("Starting Equipment (simplified)")
        
        # Basic equipment based on class
        primary_class = list(self.character.character_classes.keys())[0] if self.character.character_classes else "Fighter"
        
        basic_equipment = {
            "Fighter": ["Longsword", "Shield", "Chain Mail", "Explorer's Pack"],
            "Wizard": ["Quarterstaff", "Spellbook", "Scholar's Pack", "Dagger x2"],
            "Rogue": ["Shortsword", "Shortbow", "Leather Armor", "Thieves' Tools", "Burglar's Pack"],
            "Cleric": ["Mace", "Scale Mail", "Shield", "Holy Symbol", "Priest's Pack"]
        }
        
        equipment = basic_equipment.get(primary_class, basic_equipment["Fighter"])
        
        print(f"Starting equipment for {primary_class}:")
        for item in equipment:
            print(f"  • {item}")
        
        # Ask if they want to customize
        customize = self.get_input("Customize equipment? (y/n)", "n").lower()
        if customize == 'y':
            custom_equipment = []
            print("Enter equipment (one per line, empty line to finish):")
            while True:
                item = input("  Equipment: ").strip()
                if not item:
                    break
                if item.lower() == 'quit':
                    return False
                custom_equipment.append(item)
            
            if custom_equipment:
                equipment = custom_equipment
        
        # Store equipment (simplified - just as a list)
        self.character.custom_content_used.extend(equipment)
        print(f"✅ Equipment: {', '.join(equipment)}")
        return True
    
    def set_personality(self) -> bool:
        """Set personality traits."""
        print("Personality (optional - press Enter to skip)")
        
        trait = self.get_input("Personality Trait", "")
        if trait and trait.lower() != 'quit':
            self.character.personality_traits.append(trait)
            print(f"✅ Personality Trait: {trait}")
        
        ideal = self.get_input("Ideal", "")
        if ideal and ideal.lower() != 'quit':
            self.character.ideals.append(ideal)
            print(f"✅ Ideal: {ideal}")
        
        bond = self.get_input("Bond", "")
        if bond and bond.lower() != 'quit':
            self.character.bonds.append(bond)
            print(f"✅ Bond: {bond}")
        
        flaw = self.get_input("Flaw", "")
        if flaw and flaw.lower() != 'quit':
            self.character.flaws.append(flaw)
            print(f"✅ Flaw: {flaw}")
        
        return True
    
    def review_character(self) -> bool:
        """Review the completed character."""
        print("Character Review - Final Check")
        return True
    
    def display_final_character(self):
        """Display the completed character."""
        print("\n" + "=" * 60)
        print("🎭 CHARACTER SHEET")
        print("=" * 60)
        
        # Basic Info
        print(f"Name: {self.character.name}")
        print(f"Species: {self.character.species}")
        print(f"Background: {self.character.background}")
        print(f"Alignment: {' '.join(self.character.alignment)}")
        
        # Classes
        classes_str = ", ".join([f"{cls} {lvl}" for cls, lvl in self.character.character_classes.items()])
        total_level = sum(self.character.character_classes.values())
        print(f"Class(es): {classes_str} (Total Level: {total_level})")
        
        # Ability Scores
        print("\nAbility Scores:")
        modifiers = self.character.get_ability_modifiers()
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            ability_score_obj = self.character.get_ability_score(ability)
            # Get the actual score value from the AbilityScore object
            score = ability_score_obj.total_score if ability_score_obj else 10
            modifier = modifiers.get(ability, 0)
            sign = "+" if modifier >= 0 else ""
            print(f"  {ability.title():13}: {score:2d} ({sign}{modifier})")
        
        # Skills
        if self.character.skill_proficiencies:
            skills = [skill.replace("_", " ").title() for skill in self.character.skill_proficiencies.keys()]
            print(f"\nSkill Proficiencies: {', '.join(skills)}")
        
        # Equipment
        if self.character.custom_content_used:
            print(f"\nEquipment: {', '.join(self.character.custom_content_used)}")
        
        # Personality
        if self.character.personality_traits:
            print(f"\nPersonality Traits: {', '.join(self.character.personality_traits)}")
        if self.character.ideals:
            print(f"Ideals: {', '.join(self.character.ideals)}")
        if self.character.bonds:
            print(f"Bonds: {', '.join(self.character.bonds)}")
        if self.character.flaws:
            print(f"Flaws: {', '.join(self.character.flaws)}")
        
        print("\n" + "=" * 60)
        print("🎉 Character creation complete! How does this match your vision?")
        print("=" * 60)


def main():
    """Main function for interactive character creation."""
    try:
        creator = InteractiveCharacterCreator()
        creator.start_creation()
    except KeyboardInterrupt:
        print("\n\nCharacter creation cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
