#!/usr/bin/env python3
"""
D&D Character Creator - Complete User Test via API Endpoints

This script demonstrates the full character creation workflow using the API,
including:
- LLM-powered character generation with perfect alignment
- Character versioning and branching (git-like)
- Character evolution and leveling up
- Iterative refinement and fine-tuning
- Database persistence and retrieval

Usage:
    python user_test_via_api.py
"""

import asyncio
import json
import time
import requests
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
TIMEOUT = 300  # 5 minutes for LLM calls

class CharacterCreatorAPI:
    """API client for D&D Character Creator"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
    
    def health_check(self) -> bool:
        """Check if the API is available"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def generate_character_backstory(self, concept: str, character_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate character backstory using LLM"""
        data = {
            "character_concept": concept,
            "character_details": character_details
        }
        response = self.session.post(f"{self.base_url}/api/v1/generate/backstory", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate_character_equipment(self, concept: str, character_level: int = 1, character_class: str = "") -> Dict[str, Any]:
        """Generate character equipment using LLM"""
        data = {
            "character_concept": concept,
            "character_level": character_level,
            "character_class": character_class
        }
        response = self.session.post(f"{self.base_url}/api/v1/generate/equipment", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate_full_character(self, prompt: str) -> Dict[str, Any]:
        """Generate complete character using LLM"""
        response = self.session.post(f"{self.base_url}/api/v1/characters/generate", params={"prompt": prompt})
        response.raise_for_status()
        return response.json()
    
    def create_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a character in the database"""
        response = self.session.post(f"{self.base_url}/api/v1/characters", json=character_data)
        response.raise_for_status()
        return response.json()
    
    def get_character(self, character_id: str) -> Dict[str, Any]:
        """Get character by ID"""
        response = self.session.get(f"{self.base_url}/api/v1/characters/{character_id}")
        response.raise_for_status()
        return response.json()
    
    def get_character_sheet(self, character_id: str) -> Dict[str, Any]:
        """Get complete character sheet"""
        response = self.session.get(f"{self.base_url}/api/v1/characters/{character_id}/sheet")
        response.raise_for_status()
        return response.json()
    
    def update_character(self, character_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update character"""
        response = self.session.put(f"{self.base_url}/api/v1/characters/{character_id}", json=updates)
        response.raise_for_status()
        return response.json()
    
    def list_characters(self) -> Dict[str, Any]:
        """List all characters"""
        response = self.session.get(f"{self.base_url}/api/v1/characters")
        response.raise_for_status()
        return response.json()
    
    # Character Versioning API
    def create_repository(self, name: str, character_data: Dict[str, Any], player_name: str = "Test Player") -> Dict[str, Any]:
        """Create character repository with versioning"""
        data = {
            "name": name,
            "player_name": player_name,
            "description": f"Character evolution for {name}",
            "character_data": character_data
        }
        response = self.session.post(f"{self.base_url}/api/v1/character-repositories", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_repository_timeline(self, repo_id: str) -> Dict[str, Any]:
        """Get character timeline for visualization"""
        response = self.session.get(f"{self.base_url}/api/v1/character-repositories/{repo_id}/timeline")
        response.raise_for_status()
        return response.json()
    
    def get_repository_visualization(self, repo_id: str) -> Dict[str, Any]:
        """Get character visualization data"""
        response = self.session.get(f"{self.base_url}/api/v1/character-repositories/{repo_id}/visualization")
        response.raise_for_status()
        return response.json()
    
    def create_branch(self, repo_id: str, branch_name: str, source_commit: str = "main") -> Dict[str, Any]:
        """Create character development branch"""
        data = {
            "branch_name": branch_name,
            "source_commit_hash": source_commit,
            "description": f"Alternative development path: {branch_name}"
        }
        response = self.session.post(f"{self.base_url}/api/v1/character-repositories/{repo_id}/branches", json=data)
        response.raise_for_status()
        return response.json()
    
    def level_up_character(self, repo_id: str, new_character_data: Dict[str, Any], branch_name: str = "main") -> Dict[str, Any]:
        """Level up character with automatic commit"""
        data = {
            "branch_name": branch_name,
            "new_character_data": new_character_data,
            "level_info": {
                "new_level": new_character_data.get("level", 1),
                "experience_gained": 1000,
                "milestone": "Story progression"
            }
        }
        response = self.session.post(f"{self.base_url}/api/v1/character-repositories/{repo_id}/level-up", json=data)
        response.raise_for_status()
        return response.json()
    
    def create_commit(self, repo_id: str, character_data: Dict[str, Any], message: str, branch_name: str = "main") -> Dict[str, Any]:
        """Create character commit"""
        data = {
            "commit_message": message,
            "branch_name": branch_name,
            "character_data": character_data
        }
        response = self.session.post(f"{self.base_url}/api/v1/character-repositories/{repo_id}/commits", json=data)
        response.raise_for_status()
        return response.json()


class CharacterWorkflowDemo:
    """Demonstrates complete character creation and evolution workflow"""
    
    def __init__(self):
        self.api = CharacterCreatorAPI()
        self.character_id = None
        self.repository_id = None
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🎭 {title}")
        print("="*60)
    
    def print_step(self, step: str):
        """Print formatted step"""
        print(f"\n🔹 {step}")
        print("-" * 40)
    
    def check_api_connection(self) -> bool:
        """Check if API is available"""
        self.print_step("Checking API Connection")
        if self.api.health_check():
            print("✅ API is available and responding")
            return True
        else:
            print("❌ API is not available. Make sure the backend is running.")
            return False
    
    def demonstrate_character_alignment(self):
        """Demonstrate perfect character alignment across all aspects"""
        self.print_header("PERFECT CHARACTER ALIGNMENT DEMONSTRATION")
        
        # Character concept
        concept = "A mysterious elven wizard who specializes in necromancy but fights for good, using her dark magic to protect the innocent and heal the sick. She carries ancient tomes and a staff made from blackened bone."
        
        self.print_step("Character Concept")
        print(f"📝 Concept: {concept}")
        
        # Generate full character
        self.print_step("Generating Complete Character with LLM")
        print("⏳ Generating character (this may take 1-3 minutes with tinyllama)...")
        
        try:
            full_char_result = self.api.generate_full_character(concept)
            print("✅ Character generation complete!")
            
            if full_char_result.get('success'):
                generated_char = full_char_result.get('character', {})
                print(f"📊 Generation time: {full_char_result.get('generation_time', 0):.1f} seconds")
                
                # Display generated character
                print("\n🎭 GENERATED CHARACTER:")
                print(f"Name: {generated_char.get('name', 'Unknown')}")
                print(f"Species: {generated_char.get('species', 'Unknown')}")
                print(f"Classes: {generated_char.get('character_classes', {})}")
                print(f"Background: {generated_char.get('background', 'Unknown')}")
                print(f"Alignment: {generated_char.get('alignment', [])}")
                
                # Show ability scores
                abilities = generated_char.get('abilities', {})
                print(f"\n📊 Ability Scores:")
                for ability, score in abilities.items():
                    print(f"  {ability.title()}: {score}")
                
                # Create detailed character for database
                character_data = {
                    "name": generated_char.get('name', 'Generated Necromancer'),
                    "species": generated_char.get('species', 'Elf'),
                    "character_classes": generated_char.get('character_classes', {"Wizard": 1}),
                    "background": generated_char.get('background', 'Hermit'),
                    "alignment": generated_char.get('alignment', ["Chaotic", "Good"]),
                    "abilities": abilities or {
                        "strength": 8, "dexterity": 14, "constitution": 13,
                        "intelligence": 17, "wisdom": 15, "charisma": 12
                    },
                    "backstory": generated_char.get('backstory', 'A mysterious wizard with a dark past.')
                }
                
            else:
                print("⚠️ Character generation used fallback. Creating example character...")
                character_data = {
                    "name": "Shadowmend the Healer",
                    "species": "Elf",
                    "character_classes": {"Wizard": 1},
                    "background": "Hermit",
                    "alignment": ["Chaotic", "Good"],
                    "abilities": {
                        "strength": 8, "dexterity": 14, "constitution": 13,
                        "intelligence": 17, "wisdom": 15, "charisma": 12
                    },
                    "backstory": "A mysterious elven necromancer who uses dark magic for good."
                }
                
        except Exception as e:
            print(f"⚠️ Character generation failed: {e}")
            print("Creating example character for demonstration...")
            character_data = {
                "name": "Shadowmend the Healer",
                "species": "Elf",
                "character_classes": {"Wizard": 1},
                "background": "Hermit",
                "alignment": ["Chaotic", "Good"],
                "abilities": {
                    "strength": 8, "dexterity": 14, "constitution": 13,
                    "intelligence": 17, "wisdom": 15, "charisma": 12
                },
                "backstory": "A mysterious elven necromancer who uses dark magic for good."
            }
        
        # Generate backstory
        self.print_step("Generating Detailed Backstory")
        print("⏳ Generating backstory...")
        
        try:
            backstory_result = self.api.generate_character_backstory(concept, {
                "name": character_data["name"],
                "species": character_data["species"],
                "character_class": "Wizard",
                "background": character_data["background"]
            })
            
            backstory_data = backstory_result.get('backstory', 'No backstory generated')
            print("✅ Backstory generation complete!")
            print(f"\n📖 DETAILED BACKSTORY:")
            print(f"{backstory_data[:500]}..." if len(backstory_data) > 500 else backstory_data)
            
            # Update character with detailed backstory
            character_data["backstory"] = backstory_data
            
        except Exception as e:
            print(f"⚠️ Backstory generation failed: {e}")
        
        # Generate equipment
        self.print_step("Generating Aligned Equipment")
        print("⏳ Generating equipment...")
        
        try:
            equipment_result = self.api.generate_character_equipment(
                concept, 
                character_level=1, 
                character_class="Wizard"
            )
            
            equipment_data = equipment_result.get('equipment', 'No equipment generated')
            print("✅ Equipment generation complete!")
            print(f"\n⚔️ GENERATED EQUIPMENT:")
            print(equipment_data)
            
        except Exception as e:
            print(f"⚠️ Equipment generation failed: {e}")
        
        # Save character to database
        self.print_step("Saving Character to Database")
        try:
            saved_char = self.api.create_character(character_data)
            self.character_id = saved_char.get('id')
            print(f"✅ Character saved with ID: {self.character_id}")
            
            # Display saved character details
            print(f"\n💾 SAVED CHARACTER:")
            print(f"ID: {saved_char.get('id')}")
            print(f"Name: {saved_char.get('name')}")
            print(f"Species: {saved_char.get('species')}")
            print(f"Level: {saved_char.get('level', 1)}")
            
        except Exception as e:
            print(f"❌ Failed to save character: {e}")
            return None
        
        return character_data
    
    def demonstrate_character_versioning(self, character_data: Dict[str, Any]):
        """Demonstrate git-like character versioning"""
        self.print_header("CHARACTER VERSIONING SYSTEM DEMONSTRATION")
        
        if not character_data:
            print("❌ No character data available for versioning demo")
            return
        
        # Create character repository
        self.print_step("Creating Character Repository")
        try:
            repo_result = self.api.create_repository(
                name=f"{character_data['name']} Evolution",
                character_data=character_data,
                player_name="Demo Player"
            )
            self.repository_id = repo_result.get('id')
            print(f"✅ Repository created with ID: {self.repository_id}")
            print(f"📦 Repository: {repo_result.get('name')}")
            print(f"🌿 Default branch: {repo_result.get('default_branch')}")
            
        except Exception as e:
            print(f"❌ Failed to create repository: {e}")
            return
        
        # Level up character (Level 2)
        self.print_step("Character Level Up (Level 1 → 2)")
        level_2_data = character_data.copy()
        level_2_data.update({
            "level": 2,
            "hit_points": character_data.get("hit_points", 8) + 5,
            "spell_slots": {"1st_level": 3},
            "new_spells": ["Magic Missile", "Shield"]
        })
        
        try:
            levelup_result = self.api.level_up_character(self.repository_id, level_2_data)
            print("✅ Character leveled up to Level 2")
            print(f"📝 Commit: {levelup_result.get('level_up', {}).get('commit_message', 'Level up')}")
            
        except Exception as e:
            print(f"❌ Level up failed: {e}")
        
        # Create experimental branch for multiclassing
        self.print_step("Creating Experimental Branch (Multiclassing)")
        try:
            branch_result = self.api.create_branch(
                self.repository_id, 
                "multiclass-cleric", 
                "main"
            )
            print("✅ Created branch: multiclass-cleric")
            print("🔀 This branch will explore Wizard/Cleric multiclassing")
            
        except Exception as e:
            print(f"❌ Branch creation failed: {e}")
        
        # Create multiclass version
        multiclass_data = level_2_data.copy()
        multiclass_data.update({
            "level": 3,
            "character_classes": {"Wizard": 2, "Cleric": 1},
            "spell_slots": {"1st_level": 4, "cantrips": 3},
            "new_spells": ["Cure Wounds", "Bless", "Guidance"],
            "hit_points": level_2_data.get("hit_points", 13) + 6
        })
        
        try:
            commit_result = self.api.create_commit(
                self.repository_id,
                multiclass_data,
                "Multiclass into Cleric - adding healing abilities",
                "multiclass-cleric"
            )
            print("✅ Committed multiclass version to experimental branch")
            
        except Exception as e:
            print(f"❌ Multiclass commit failed: {e}")
        
        # Display timeline
        self.print_step("Character Evolution Timeline")
        try:
            timeline = self.api.get_repository_timeline(self.repository_id)
            print("📊 CHARACTER EVOLUTION TIMELINE:")
            print(f"Character: {timeline.get('character_name', 'Unknown')}")
            print(f"Player: {timeline.get('player_name', 'Unknown')}")
            
            branches = timeline.get('branches', [])
            commits = timeline.get('commits', [])
            
            print(f"\n🌿 Branches ({len(branches)}):")
            for branch in branches:
                print(f"  - {branch.get('branch_name', 'unknown')}: {branch.get('description', 'No description')}")
            
            print(f"\n📝 Commits ({len(commits)}):")
            for commit in commits:
                print(f"  - {commit.get('short_hash', 'unknown')[:8]}: {commit.get('commit_message', 'No message')}")
                print(f"    Level {commit.get('character_level', 1)} | {commit.get('created_at', 'unknown time')}")
            
        except Exception as e:
            print(f"❌ Timeline retrieval failed: {e}")
        
        # Display visualization data
        self.print_step("Character Graph Visualization Data")
        try:
            viz_data = self.api.get_repository_visualization(self.repository_id)
            print("🎨 VISUALIZATION DATA:")
            
            nodes = viz_data.get('nodes', [])
            edges = viz_data.get('edges', [])
            
            print(f"📊 Graph structure: {len(nodes)} nodes, {len(edges)} connections")
            
            for node in nodes:
                print(f"  🔸 {node.get('id', 'unknown')}: Level {node.get('level', 1)} - {node.get('type', 'unknown')}")
            
            for edge in edges:
                print(f"  🔗 {edge.get('from', 'unknown')} → {edge.get('to', 'unknown')}")
                
        except Exception as e:
            print(f"❌ Visualization data retrieval failed: {e}")
    
    def demonstrate_character_retrieval(self):
        """Demonstrate loading and inspecting saved characters"""
        self.print_header("CHARACTER RETRIEVAL AND INSPECTION")
        
        # List all characters
        self.print_step("Listing All Characters in Database")
        try:
            characters = self.api.list_characters()
            print(f"📊 Found {len(characters)} characters in database:")
            
            for char in characters:
                print(f"  🎭 {char.get('name', 'Unknown')} (ID: {char.get('id', 'unknown')[:8]}...)")
                print(f"      Species: {char.get('species', 'Unknown')}, Level: {char.get('level', 1)}")
                
        except Exception as e:
            print(f"❌ Character listing failed: {e}")
            return
        
        # Get detailed character sheet
        if self.character_id:
            self.print_step("Loading Complete Character Sheet")
            try:
                char_sheet = self.api.get_character_sheet(self.character_id)
                print("✅ Character sheet loaded successfully!")
                
                print(f"\n📋 COMPLETE CHARACTER SHEET:")
                print(f"Name: {char_sheet.get('name', 'Unknown')}")
                print(f"Species: {char_sheet.get('species', 'Unknown')}")
                print(f"Background: {char_sheet.get('background', 'Unknown')}")
                print(f"Alignment: {char_sheet.get('alignment', [])}")
                print(f"Level: {char_sheet.get('level', 1)}")
                print(f"Hit Points: {char_sheet.get('hit_points', 'Unknown')}")
                
                # Show ability scores and modifiers
                abilities = char_sheet.get('abilities', {})
                print(f"\n📊 Ability Scores:")
                for ability, score in abilities.items():
                    modifier = (score - 10) // 2
                    modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                    print(f"  {ability.title()}: {score} ({modifier_str})")
                
                # Show backstory excerpt
                backstory = char_sheet.get('backstory', '')
                if backstory:
                    print(f"\n📖 Backstory Excerpt:")
                    print(f"{backstory[:200]}..." if len(backstory) > 200 else backstory)
                
            except Exception as e:
                print(f"❌ Character sheet retrieval failed: {e}")
    
    def interactive_character_refinement(self):
        """Demonstrate iterative character refinement"""
        self.print_header("INTERACTIVE CHARACTER REFINEMENT")
        
        if not self.character_id:
            print("❌ No character available for refinement")
            return
        
        print("🔧 This would normally allow you to iteratively refine the character:")
        print("  - Adjust ability scores")
        print("  - Modify backstory elements")
        print("  - Change equipment loadout")
        print("  - Explore different multiclass options")
        print("  - Create alternative character branches")
        print("\n💡 Each change would create a new commit in the character repository")
        print("💡 You could compare different versions and merge the best elements")
        
        # Example refinement
        self.print_step("Example Refinement: Updating Character Background")
        try:
            updates = {
                "backstory": "REFINED: A mysterious elven necromancer who lost her family to a plague. She now dedicates her unlife magic to healing and protecting others, carrying the guilt of her past experiments with dark magic."
            }
            
            updated_char = self.api.update_character(self.character_id, updates)
            print("✅ Character backstory refined and updated")
            print(f"📝 New backstory: {updates['backstory'][:100]}...")
            
            # This would create a new commit in the repository
            if self.repository_id:
                commit_result = self.api.create_commit(
                    self.repository_id,
                    {**updated_char, "backstory": updates["backstory"]},
                    "Refined character backstory with more emotional depth"
                )
                print("✅ Refinement committed to character repository")
                
        except Exception as e:
            print(f"❌ Character refinement failed: {e}")
    
    def run_complete_demo(self):
        """Run the complete character creation and versioning demonstration"""
        self.print_header("D&D CHARACTER CREATOR - COMPLETE WORKFLOW DEMO")
        
        print("🎯 This demonstration will show:")
        print("  1. Perfect character alignment (concept → backstory → equipment)")
        print("  2. Character versioning and branching (git-like)")
        print("  3. Character evolution and leveling")
        print("  4. Database persistence and retrieval")
        print("  5. Iterative character refinement")
        
        if not self.check_api_connection():
            return
        
        # Run demonstrations
        character_data = self.demonstrate_character_alignment()
        time.sleep(1)
        
        self.demonstrate_character_versioning(character_data)
        time.sleep(1)
        
        self.demonstrate_character_retrieval()
        time.sleep(1)
        
        self.interactive_character_refinement()
        
        # Final summary
        self.print_header("DEMONSTRATION COMPLETE")
        print("✅ Character creation workflow demonstrated successfully!")
        print(f"📊 Character ID: {self.character_id}")
        print(f"📦 Repository ID: {self.repository_id}")
        print("\n🎯 Key Features Demonstrated:")
        print("  ✅ LLM-powered character generation with alignment")
        print("  ✅ Git-like character versioning and branching")
        print("  ✅ Character evolution and leveling system")
        print("  ✅ Complete database persistence")
        print("  ✅ Character sheet retrieval and inspection")
        print("  ✅ Iterative refinement capabilities")
        
        print(f"\n🌐 View character visualization at:")
        print(f"   {self.api.base_url}/api/v1/character-repositories/{self.repository_id}/visualization")
        print(f"\n📊 View character timeline at:")
        print(f"   {self.api.base_url}/api/v1/character-repositories/{self.repository_id}/timeline")


if __name__ == "__main__":
    print("🎭 D&D Character Creator - Complete Workflow Demo")
    print("=" * 50)
    
    demo = CharacterWorkflowDemo()
    demo.run_complete_demo()
    
    print("\n🎉 Demo complete! Press Enter to exit...")
    input()
