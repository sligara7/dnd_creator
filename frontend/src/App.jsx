import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { characterAPI, apiUtils } from './services/api';
import CharacterCreator from './components/Character/CharacterCreator';
import CharacterList from './components/Character/CharacterList';
import DMDashboard from './components/DM/DMDashboard';
import CreateCharacterPage from './components/pages/CreateCharacterPage';
import UpdateCharacterPage from './components/pages/UpdateCharacterPage';
import CreateItemPage from './components/pages/CreateItemPage';
import CreateSpellPage from './components/pages/CreateSpellPage';
import CreateNPCPage from './components/pages/CreateNPCPage';
import CreateCreaturePage from './components/pages/CreateCreaturePage';
import CharacterSheetPage from './components/pages/CharacterSheetPage';
import JournalEditPage from './components/pages/JournalEditPage';
import CharacterEvolutionPage from './components/pages/CharacterTreePage';
import './App.css';

/**
 * Main D&D Character Creator Application
 * 
 * Features:
 * - AI-driven character creation with LLM integration
 * - Character management (CRUD operations)
 * - DM tools for NPCs, creatures, and content approval
 * - Journal system for character progression
 * - Level up and multiclass functionality
 * - Backend API integration at http://localhost:8000
 */

function App() {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [characters, setCharacters] = useState([]);
  const [currentUser, setCurrentUser] = useState('Player1'); // TODO: Implement proper auth

  // Test backend connection on app load
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const result = await apiUtils.testConnection();
        setIsBackendConnected(result.connected);
        console.log('Backend status:', result.message);
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        setIsBackendConnected(false);
      }
    };

    checkBackendConnection();
  }, []);

  // Load characters on app start
  useEffect(() => {
    if (isBackendConnected) {
      loadCharacters();
    }
  }, [isBackendConnected]);

  const loadCharacters = async () => {
    try {
      const response = await characterAPI.getAll();
      setCharacters(response.data);
    } catch (error) {
      console.error('Failed to load characters:', error);
    }
  };

  return (
    <div className="App">
      <Router>
        <div className="min-h-screen bg-gray-900 text-white">
          {/* Header Navigation */}
          <header className="bg-gray-800 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-6">
                <div className="flex items-center">
                  <h1 className="text-3xl font-bold text-red-500">
                    🐉 D&D Character Creator
                  </h1>
                </div>
                
                {/* Backend Status Indicator */}
                <div className="flex items-center space-x-4">
                  <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                    isBackendConnected 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      isBackendConnected ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <span>
                      {isBackendConnected ? 'Backend Connected' : 'Backend Offline'}
                    </span>
                  </div>
                  <span className="text-gray-300">User: {currentUser}</span>
                </div>
              </div>
              
              {/* Navigation Menu */}
              <nav className="flex space-x-8 pb-4">
                <Link 
                  to="/" 
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </Link>
                <Link 
                  to="/create" 
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Create Character
                </Link>
                <Link 
                  to="/characters" 
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  My Characters
                </Link>
                <Link 
                  to="/dm" 
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  DM Tools
                </Link>
              </nav>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            {!isBackendConnected && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                      Backend Connection Error
                    </h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>
                        Cannot connect to the backend API at http://localhost:8000. 
                        Please ensure the backend is running:
                      </p>
                      <pre className="mt-2 bg-gray-100 p-2 rounded text-xs">
                        cd backend && python main.py
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route 
                path="/create" 
                element={
                  <CharacterCreator 
                    onCharacterCreated={loadCharacters}
                    isBackendConnected={isBackendConnected}
                  />
                } 
              />
              <Route 
                path="/characters" 
                element={
                  <CharacterList 
                    characters={characters}
                    onCharacterUpdated={loadCharacters}
                    isBackendConnected={isBackendConnected}
                  />
                } 
              />
              <Route 
                path="/dm" 
                element={
                  <DMDashboard 
                    isBackendConnected={isBackendConnected}
                  />
                } 
              />
              <Route path="/create-character" element={<CreateCharacterPage />} />
              <Route path="/update-character" element={<UpdateCharacterPage />} />
              <Route path="/create-item" element={<CreateItemPage />} />
              <Route path="/create-spell" element={<CreateSpellPage />} />
              <Route path="/create-npc" element={<CreateNPCPage />} />
              <Route path="/create-creature" element={<CreateCreaturePage />} />
              <Route path="/character-sheet" element={<CharacterSheetPage />} />
              <Route path="/journal-edit" element={<JournalEditPage />} />
              <Route path="/character-evolution" element={<CharacterEvolutionPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

// Home Page Component
function HomePage() {
  return (
    <div className="text-center">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-4xl font-extrabold text-white sm:text-5xl">
          Welcome to D&D Character Creator
        </h2>
        <p className="mt-6 text-xl text-gray-300">
          Create amazing D&D 5e characters with AI assistance, manage your character roster, 
          and access powerful DM tools for NPCs and creatures.
        </p>
        
        <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <FeatureCard
            icon="🎭"
            title="AI Character Creation"
            description="Let our LLM help you create unique characters with rich backstories and balanced abilities."
          />
          <FeatureCard
            icon="📊"
            title="Character Management"
            description="Track character progression, level up, multiclass, and maintain detailed journals."
          />
          <FeatureCard
            icon="🎲"
            title="DM Tools"
            description="Create NPCs, monsters, and custom content. Approve player characters and manage campaigns."
          />
        </div>
        
        <div className="mt-10">
          <Link
            to="/create"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
          >
            Start Creating Characters
          </Link>
        </div>
      </div>
    </div>
  );
}

// Feature Card Component
function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}

export default App;
// # Build container
// podman build -t dnd-backend .

// # Run container  
// podman run -p 8000:8000 -d --name dnd-backend dnd-backend

// # Access API
// curl http://localhost:8000/docs

// Backend structure:

// backend/
// ├── app.py                    # Main FastAPI application ✅
// ├── main.py                   # Uvicorn entry point ✅
// ├── Dockerfile                # Container configuration ✅
// ├── requirements.txt          # Dependencies ✅
// ├── config.py                 # Configuration ✅
// ├── character_models.py       # Character logic ✅
// ├── database_models.py        # Database operations ✅
// ├── llm_service.py           # LLM integration ✅
// ├── items_creation.py        # Item creation API ✅
// ├── npc_creation.py          # NPC creation API ✅
// ├── creature_creation.py     # Creature creation API ✅
// ├── ability_management.py    # Game mechanics ✅
// ├── core_models.py           # Core D&D models ✅
// ├── custom_content_models.py # Custom content ✅
// ├── generators.py            # Content generators ✅
// └── PRODUCTION_READY.md      # Documentation ✅

// ### 4. Container Configuration ✅
// - Dockerfile optimized for production
// - Requirements.txt contains all necessary dependencies
// - Proper entry point: `uvicorn main:app --host 0.0.0.0 --port 8000`
// - Health check configured for container monitoring

// ### 5. API Endpoints ✅
// All creation modules are production-ready with proper API integration:
// - Character management: `/api/v1/characters/`
// - Item creation: `/api/v1/items/`
// - NPC creation: `/api/v1/npcs/`
// - Creature creation: `/api/v1/creatures/`
// - Content generation: `/api/v1/generate/`

// Reference /dnd_char_creator/backend/PRODUCTION_READY.md for detailed documentation on the backend structure, API endpoints, and usage examples.
// Reference /dnd_char_creator/backend/app.py for the main fastapi and endpoints for implementation

// # TODO: check importing an existing character from JSON and updating it (at the current character level), or leveling it up to the next level, or doing a multi-class change (at level up)
// # TODO: this is supposed to be interative - the LLM is supposed to provide an initial character concept, then offer the user the opportunity to modify it (and what they'd like to modify), the LLM should then ingest the previous concept and modify per the user requests.
// # TODO: added ability to create NPCs, creatures (beasts, monsters, fey, and new species), and individual items (weapons, armor, spells).  


// below is the python version of the first thing I want to test the backend with:
// #!/usr/bin/env python3
// """
// AI-Driven Character Creator - Creative Character Generation

// This script uses the LLM service to create unique, non-traditional D&D characters
// based on your prompts and descriptions. It can generate:
// - Custom species and subspecies
// - Unique character classes and subclasses  
// - Custom feats, weapons, armor, and spells
// - Rich backstories and personality traits

// Usage:
//     python ai_character_creator.py
    
// Or in iPython:
//     %run ai_character_creator.py
// """

// import sys
// import json
// import asyncio
// from pathlib import Path
// from typing import Dict, Any, List, Optional

// # Try to import json5 for more lenient JSON parsing
// try:
//     import json5
//     HAS_JSON5 = True
// except ImportError:
//     HAS_JSON5 = False

// # Add backend directory to path
// backend_dir = Path(__file__).parent
// sys.path.insert(0, str(backend_dir))

// try:
//     from character_models import CharacterCore, DnDCondition
//     from core_models import ProficiencyLevel
//     from llm_service_new import create_llm_service, create_ollama_service
//     print("✅ Character and LLM services imported successfully")
//     if HAS_JSON5:
//         print("✅ JSON5 library available for robust JSON parsing")
//     else:
//         print("⚠️  JSON5 not available. Install with: pip install json5")
// except ImportError as e:
//     print(f"❌ Failed to import required modules: {e}")
//     print("Make sure you're running this from the backend directory")
//     sys.exit(1)


// class AICharacterCreator:
//     """AI-driven character creation using LLM services."""
    
//     def __init__(self, debug_mode: bool = False):
//         self.character = None
//         self.llm_service = None
//         self.character_concept = ""
//         self.debug_mode = debug_mode
//         self.generated_content = {
//             "species": None,
//             "classes": {},
//             "background": None,
//             "personality": {},
//             "equipment": [],
//             "abilities": {},
//             "custom_content": {
//                 "feats": [],
//                 "spells": [],
//                 "items": []
//             }
//         }
        
//     def initialize_llm(self):
//         """Initialize the LLM service with increased timeout for slow computers."""
//         print("🤖 Initializing AI service...")
//         try:
//             # Try Ollama first (local) with longer timeout for slow computers
//             self.llm_service = create_ollama_service(timeout=300)  # 5 minutes timeout
//             print("✅ Connected to Ollama LLM service (5 min timeout)")
//             return True
//         except Exception as e:
//             print(f"⚠️  Ollama not available: {e}")
//             try:
//                 self.llm_service = create_llm_service()
//                 print("✅ Connected to default LLM service")
//                 return True
//             except Exception as e2:
//                 print(f"❌ No LLM service available: {e2}")
//                 return False
    
//     async def test_llm_basic_functionality(self):
//         """Test LLM with a simple request to ensure it's working."""
//         print("🧪 Testing LLM with simple request...")
        
//         simple_prompt = """Generate a simple JSON response with a name and age:
//         {"name": "Test Character", "age": 25}
        
//         Please return exactly that JSON format."""
        
//         try {
//             response = await self.llm_service.generate_content(simple_prompt)
//             test_data = self.parse_json_response(response)
            
//             if test_data and "name" in test_data:
//                 print(f"✅ LLM test successful! Generated: {test_data.get('name', 'Unknown')}")
//                 return True
//             else:
//                 print(f"⚠️  LLM test partially successful but JSON parsing failed")
//                 print(f"   Raw response: {response[:100]}...")
//                 return True  # Still proceed, just warn about JSON parsing
//         } catch (error) {
//             print(f"❌ LLM test failed: {error}")
//             return False
    
//     async def start_creation(self):
//         """Start the AI-driven character creation process."""
//         print("🎭 AI-Driven D&D Character Creator")
//         console.log("Describe your character concept and I'll bring it to life!");
//         console.log("I can create non-traditional species, classes, and abilities.\n");
        
//         if (!this.initialize_llm()) {
//             print("❌ Cannot proceed without LLM service.");
//             return;
//         }
        
//         // Test LLM functionality first
//         if (!await this.test_llm_basic_functionality()) {
//             print("❌ LLM test failed. Cannot proceed with character generation.");
//             return;
//         }
        
//         print("🎯 LLM is working! Proceeding with character generation...");
//         console.log("⏱️  Note: Generation may take several minutes on slower computers.\n");
        
//         // Get character concept from user
//         concept = this.get_character_concept();
//         if (!concept) {
//             return;
//         }
            
//         this.character_concept = concept;
        
//         // Generate character using AI
//         print(f"\n🔮 Creating character based on: '{concept}'")
//         print("=" * 50)
        
//         try {
//             await this.generate_basic_info();
//             await this.generate_species_and_classes();
//             await this.generate_abilities();
//             await this.generate_skills_and_background();
//             await this.generate_equipment();
//             await this.generate_custom_content();
//             await this.generate_personality();
            
//             this.create_character_object();
//             this.display_final_character();
            
//         } catch (error) {
//             print(f"❌ Error during character generation: {error}");
//             import traceback
//             traceback.print_exc();
//     }
    
//     def get_character_concept(self) -> str:
//         """Get the character concept from the user."""
//         print("Examples of character concepts:")
//         print("• A crystal-powered artificer from a steampunk sky city")
//         print("• A time-traveling druid who speaks with extinct creatures")
//         print("• A shadow dancer who weaves darkness into magical weapons")
//         print("• A dragon-touched healer with scales that change with emotions")
//         print("• A void monk who fights by erasing parts of reality\n")
        
//         concept = input("Describe your character concept: ").strip()
        
//         if not concept:
//             print("No concept provided. Goodbye!")
//             return ""
        
//         if concept.lower() in ['quit', 'exit']:
//             return ""
            
//         return concept
    
//     async def generate_basic_info(self):
//         """Generate basic character information."""
//         print("📝 Generating basic character info... (this may take a few minutes)")
        
//         prompt = f"""
//         Based on this character concept: "{self.character_concept}"
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Generate a unique D&D character with the following JSON format:
//         {{
//             "name": "Character Name",
//             "alignment": ["Ethical", "Moral"],
//             "age": 25,
//             "height": 68,
//             "weight": 150,
//             "appearance": "Detailed physical description",
//             "voice": "How they speak and sound"
//         }}
        
//         IMPORTANT FORMATTING:
//         - age: integer (years)
//         - height: integer (total inches, e.g. 68 for 5'8")
//         - weight: integer (pounds, no units)
//         - alignment: array with exactly 2 strings
        
//         Make the character interesting and unique. The alignment should be two words like ["Chaotic", "Good"].
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             basic_info = this.parse_json_response(response);
            
//             if (basic_info) {
//                 this.generated_content.update(basic_info);
//                 print(f"✅ Generated: {basic_info.get('name', 'Unknown')}");
//                 print(f"   Alignment: {' '.join(basic_info.get('alignment', ['True', 'Neutral']))}");
//             } else {
//                 print("⚠️  Using fallback basic info");
//                 this.generated_content.update({
//                     "name": "Mysterious Wanderer",
//                     "alignment": ["True", "Neutral"],
//                     "age": 25,
//                     "height": 68,
//                     "weight": 150,
//                     "appearance": "An enigmatic figure with unique features"
//                 });
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating basic info: {error}");
//             this.generated_content.update({
//                 "name": "AI-Generated Hero",
//                 "alignment": ["Chaotic", "Good"],
//                 "age": 30,
//                 "height": 70,
//                 "weight": 180
//             });
//     }
    
//     async def generate_species_and_classes(self):
//         """Generate unique species and class combinations."""
//         print("🧬 Generating species and classes... (this may take a few minutes)")
        
//         prompt = f"""
//         For this character concept: "{self.character_concept}"
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Create a unique species and class combination in JSON format:
//         {{
//             "species": {{
//                 "name": "Species Name",
//                 "description": "What makes this species unique",
//                 "traits": ["Trait 1", "Trait 2", "Trait 3"],
//                 "abilities": {{
//                     "strength": 12,
//                     "dexterity": 14,
//                     "constitution": 13,
//                     "intelligence": 15,
//                     "wisdom": 10,
//                     "charisma": 16
//                 }}
//             }},
//             "primary_class": {{
//                 "name": "Class Name",
//                 "level": 3,
//                 "description": "What this class does",
//                 "features": ["Feature 1", "Feature 2"]
//             }},
//             "secondary_class": {{
//                 "name": "Optional Second Class",
//                 "level": 1,
//                 "description": "Multiclass option"
//             }}
//         }}
        
//         Be creative! Invent new species and class combinations that don't exist in standard D&D.
//         Ability scores should total around 75-80 points.
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             species_classes = this.parse_json_response(response);
            
//             if (species_classes) {
//                 this.generated_content["species"] = species_classes.get("species");
//                 this.generated_content["primary_class"] = species_classes.get("primary_class");
//                 this.generated_content["secondary_class"] = species_classes.get("secondary_class");
                
//                 print(f"✅ Species: {species_classes.get('species', {}).get('name', 'Unknown')}");
//                 print(f"✅ Class: {species_classes.get('primary_class', {}).get('name', 'Unknown')}");
//             } else {
//                 print("⚠️  Using fallback species and class");
//                 this.use_fallback_species_class();
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating species/class: {error}");
//             this.use_fallback_species_class();
//     }
    
//     async def generate_abilities(self):
//         """Generate ability scores based on character concept."""
//         print("💪 Generating ability scores...")
        
//         species_abilities = this.generated_content.get("species", {}).get("abilities", {});
//         if (species_abilities) {
//             this.generated_content["abilities"] = species_abilities;
//             print("✅ Ability scores set from species");
//         } else {
//             // Generate balanced ability scores
//             this.generated_content["abilities"] = {
//                 "strength": 13,
//                 "dexterity": 14,
//                 "constitution": 15,
//                 "intelligence": 12,
//                 "wisdom": 10,
//                 "charisma": 16
//             };
//             print("✅ Generated balanced ability scores");
//     }
    
//     async def generate_skills_and_background(self):
//         """Generate skills and background."""
//         print("🎯 Generating skills and background... (this may take a few minutes)")
        
//         prompt = f"""
//         For this character: "{self.character_concept}"
//         With species: {this.generated_content.get("species", {}).get("name", "Unknown")}
//         And class: {this.generated_content.get("primary_class", {}).get("name", "Unknown")}
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Generate skills and background in JSON format:
//         {{
//             "background": {{
//                 "name": "Background Name",
//                 "description": "What they did before adventuring"
//             }},
//             "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"],
//             "languages": ["Common", "Language 2", "Language 3"],
//             "proficiencies": ["Tool 1", "Tool 2"]
//         }}
        
//         Choose skills that make sense for the character concept.
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             skills_bg = this.parse_json_response(response);
            
//             if (skills_bg) {
//                 this.generated_content["background"] = skills_bg.get("background");
//                 this.generated_content["skills"] = skills_bg.get("skills", []);
//                 this.generated_content["languages"] = skills_bg.get("languages", ["Common"]);
//                 print(f"✅ Background: {skills_bg.get('background', {}).get('name', 'Unknown')}");
//                 print(f"✅ Skills: {', '.join(skills_bg.get('skills', []))}");
//             } else {
//                 this.use_fallback_skills_background();
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating skills/background: {error}");
//             this.use_fallback_skills_background();
//     }
    
//     async def generate_equipment(self):
//         """Generate starting equipment."""
//         print("⚔️ Generating equipment... (this may take a few minutes)")
        
//         prompt = f"""
//         For this character concept: "{self.character_concept}"
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Generate starting equipment in JSON format:
//         {{
//             "weapons": ["Weapon 1", "Weapon 2"],
//             "armor": "Armor type",
//             "tools": ["Tool 1", "Tool 2"],
//             "items": ["Item 1", "Item 2", "Item 3"],
//             "magical_items": ["Magic Item 1"]
//         }}
        
//         Be creative with equipment that matches the character concept.
//         Include both practical and unique items.
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             equipment = this.parse_json_response(response);
            
//             if (equipment) {
//                 this.generated_content["equipment"] = equipment;
//                 print(f"✅ Equipment generated");
//             } else {
//                 this.use_fallback_equipment();
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating equipment: {error}");
//             this.use_fallback_equipment();
//     }
    
//     async def generate_custom_content(self):
//         """Generate custom feats, spells, and items."""
//         print("✨ Generating custom content... (this may take a few minutes)")
        
//         prompt = f"""
//         For this character concept: "{self.character_concept}"
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Create custom D&D content in JSON format:
//         {{
//             "custom_feats": [
//                 {{
//                     "name": "Feat Name",
//                     "description": "What the feat does",
//                     "prerequisites": "Any requirements"
//                 }}
//             ],
//             "custom_spells": [
//                 {{
//                     "name": "Spell Name", 
//                     "level": 1,
//                     "school": "Magic School",
//                     "description": "Spell effect"
//                 }}
//             ],
//             "custom_items": [
//                 {{
//                     "name": "Item Name",
//                     "type": "Item type",
//                     "description": "What makes it special"
//                 }}
//             ]
//         }}
        
//         Create 1-2 items for each category that perfectly match the character concept.
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             custom_content = this.parse_json_response(response);
            
//             if (custom_content) {
//                 this.generated_content["custom_content"] = custom_content;
//                 print("✅ Custom content created");
                
//                 # Show what was created
//                 if (custom_content.get("custom_feats")) {
//                     print(f"   • {len(custom_content['custom_feats'])} custom feats");
//                 }
//                 if (custom_content.get("custom_spells")) {
//                     print(f"   • {len(custom_content['custom_spells'])} custom spells");
//                 }
//                 if (custom_content.get("custom_items")) {
//                     print(f"   • {len(custom_content['custom_items'])} custom items");
//                 }
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating custom content: {error}");
//     }
    
//     async def generate_personality(self):
//         """Generate personality traits and backstory."""
//         print("🎭 Generating personality and backstory... (this may take a few minutes)")
        
//         prompt = f"""
//         For this character concept: "{self.character_concept}"
//         With name: {this.generated_content.get("name", "Unknown")}
        
//         IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
//         Generate personality in JSON format:
//         {{
//             "personality_traits": ["Trait 1", "Trait 2"],
//             "ideals": ["Ideal 1"],
//             "bonds": ["Bond 1"],
//             "flaws": ["Flaw 1"],
//             "backstory": "A rich backstory of 2-3 paragraphs explaining their origin, motivations, and how they became who they are."
//         }}
        
//         Make the personality complex and interesting, with internal conflicts and clear motivations.
//         """
        
//         try {
//             print("   ⏳ Sending request to LLM...")
//             response = await this.llm_service.generate_content(prompt);
//             print("   ⚙️  Processing response...")
//             personality = this.parse_json_response(response);
            
//             if (personality) {
//                 this.generated_content["personality"] = personality;
//                 print("✅ Personality and backstory generated");
//             } else {
//                 this.use_fallback_personality();
//             }
//         } catch (error) {
//             print(f"⚠️  Error generating personality: {error}");
//             this.use_fallback_personality();
//     }
    
//     def parse_json_response(self, response: str) -> Optional[Dict[str, Any]] {
//         """Parse JSON from LLM response with robust extraction and auto-closing."""
//         if (this.debug_mode) {
//             print(f"🔍 DEBUG - Raw LLM Response (full):\n{response}");
//             print(f"   Length: {len(response)} characters");
//         }
//         try {
//             # Robustly find the first '{' and last '}' (ignore leading/trailing whitespace)
//             response_stripped = response.strip();
//             start = response_stripped.find('{');
            
//             # Find the last valid closing brace by counting braces
//             end = -1;
//             brace_count = 0;
//             for (i, char) in enumerate(response_stripped[start:], start) {
//                 if (char == '{') {
//                     brace_count += 1;
//                 } else if (char == '}') {
//                     brace_count -= 1;
//                     if (brace_count == 0) {
//                         end = i + 1;
//                         break;
//                     }
//                 }
//             }

//             if (start != -1 && end > start) {
//                 json_str = response_stripped[start:end];
//                 # --- Auto-close logic for incomplete JSON ---
//                 open_braces = json_str.count('{');
//                 close_braces = json_str.count('}');
//                 open_brackets = json_str.count('[');
//                 close_brackets = json_str.count(']');
//                 # Add missing closing braces/brackets if needed
//                 if (close_braces < open_braces) {
//                     json_str += '}' * (open_braces - close_braces);
//                 }
//                 if (close_brackets < open_brackets) {
//                     json_str += ']' * (open_brackets - close_brackets);
//                 }
//                 if (this.debug_mode) {
//                     print(f"🔍 DEBUG - Extracted JSON string (auto-closed if needed):\n   {json_str}");
//                 }
//                 # Try parsing the extracted JSON
//                 try {
//                     return json.loads(json_str);
//                 } catch (json.JSONDecodeError as e) {
//                     print(f"⚠️  JSON parsing error: {e}");
//                     print(f"   Raw JSON attempt: {json_str[:200]}...");
//                     # Try JSON5 if available
//                     if (HAS_JSON5) {
//                         try {
//                             result = json5.loads(json_str);
//                             print("✅ Recovered JSON using JSON5 parser");
//                             return result;
//                         } catch (Exception as json5_error) {
//                             print(f"   JSON5 also failed: {json5_error}");
//                         }
//                     }
//                     # Try to find and extract multiple JSON objects
//                     json_objects = [];
//                     brace_count = 0;
//                     current_json = "";
//                     for (char in response[start:]) {
//                         current_json += char;
//                         if (char == '{') {
//                             brace_count += 1;
//                         } else if (char == '}') {
//                             brace_count -= 1;
//                             if (brace_count == 0) {
//                                 try {
//                                     obj = json.loads(current_json);
//                                     json_objects.append(obj);
//                                     break;
//                                 } catch {
//                                     continue;
//                                 }
//                             }
//                         }
//                     }
//                     if (json_objects) {
//                         print("✅ Recovered JSON using alternative parsing");
//                         return json_objects[0];
//                     }
//                     # Last resort: try to clean common issues
//                     cleaned_json = this._clean_json_string(json_str);
//                     if (this.debug_mode) {
//                         print(f"🔍 DEBUG - Cleaned JSON: {cleaned_json}");
//                     }
//                     try {
//                         result = json.loads(cleaned_json);
//                         print("✅ Recovered JSON after cleaning");
//                         return result;
//                     } catch (Exception as clean_error) {
//                         # Try JSON5 on the cleaned version too
//                         if (HAS_JSON5) {
//                             try {
//                                 result = json5.loads(cleaned_json);
//                                 print("✅ Recovered JSON using JSON5 after cleaning");
//                                 return result;
//                             } catch (Exception as json5_clean_error) {
//                                 print(f"   JSON5 on cleaned JSON also failed: {json5_clean_error}");
//                             }
//                         }
//                         print(f"❌ All JSON parsing attempts failed");
//                         print(f"   Original error: {e}");
//                         print(f"   Cleaning error: {clean_error}");
//                         if (this.debug_mode) {
//                             print(f"   Full response: {response}");
//                         }
//                         return null;
//                     }
//                 } else {
//                     print("⚠️  No JSON found in response");
//                     print(f"   Full response (for debugging):\n{response}");
//                     return null;
//                 }
//             } catch (Exception as e) {
//                 print(f"⚠️  Unexpected error in JSON parsing: {e}");
//                 print(f"   Full response (for debugging):\n{response}");
//                 return null;
//         }
//     }
    
//     def _clean_json_string(self, json_str: str) -> str {
//         """Clean common JSON formatting issues."""
//         import re
        
//         # Remove markdown code blocks
//         json_str = json_str.replace('```json', '').replace('```', '');
        
//         # Fix the specific issue: unescaped quotes in measurements like "4'10""
//         # This handles cases like "4'10"" -> "4'10\""
//         json_str = re.sub(r'"(\d+\'\d*)"([^,\n\}]*)', r'"\1\\"', json_str);
        
//         # Fix unescaped quotes at end of string values before comma/brace
//         json_str = re.sub(r'([^\\])"([,\}])', r'\1\\"\2', json_str);
        
//         # Remove trailing commas before closing braces/brackets
//         json_str = re.sub(r',(\s*[}\]])', r'\1', json_str);
        
//         # Fix common quote issues
//         json_str = json_str.replace('"', '"').replace('"', '"');
//         json_str = json_str.replace(''', "'").replace(''', "'");
        
//         # Fix unescaped quotes in string values more aggressively
//         # Look for patterns like: "key": "value with "quotes" inside"
//         json_str = re.sub(r':\s*"([^"]*)"([^"]*)"([^"]*)"', r': "\1\\"\2\\"\3"', json_str);
        
//         return json_str.strip();
    
//     def create_character_object(self):
//         """Create the CharacterCore object from generated content."""
//         print("\n🏗️ Building character object...");
        
//         name = this.generated_content.get("name", "AI Hero");
//         this.character = CharacterCore(name=name);
        
//         # Set basic info
//         if ("alignment" in this.generated_content) {
//             this.character.alignment = this.generated_content["alignment"];
//         }
        
//         # Set species
//         species_info = this.generated_content.get("species", {});
//         this.character.species = species_info.get("name", "Custom Species");
        
//         # Set background
//         background_info = this.generated_content.get("background", {});
//         this.character.background = background_info.get("name", "Unique Background");
        
//         # Set classes
//         primary_class = this.generated_content.get("primary_class", {});
//         if (primary_class) {
//             class_name = primary_class.get("name", "Custom Class");
//             class_level = primary_class.get("level", 1);
//             this.character.character_classes[class_name] = class_level;
//         }
        
//         secondary_class = this.generated_content.get("secondary_class", {});
//         if (secondary_class && secondary_class.get("name")) {
//             class_name = secondary_class.get("name", "Second Class");
//             class_level = secondary_class.get("level", 1);
//             this.character.character_classes[class_name] = class_level;
//         }
        
//         # Set ability scores
//         abilities = this.generated_content.get("abilities", {});
//         for (ability, score) in abilities.items() {
//             this.character.set_ability_score(ability, score);
//         }
        
//         # Set skills
//         skills = this.generated_content.get("skills", []);
//         for (skill in skills) {
//             skill_key = skill.lower().replace(" ", "_");
//             this.character.skill_proficiencies[skill_key] = ProficiencyLevel.PROFICIENT;
//         }
        
//         # Set personality and backstory
//         personality = this.generated_content.get("personality", {});
//         this.character.personality_traits = personality.get("personality_traits", []);
//         this.character.ideals = personality.get("ideals", []);
//         this.character.bonds = personality.get("bonds", []);
//         this.character.flaws = personality.get("flaws", []);
        
//         # Use the rich backstory from personality generation, or fallback to basic info summary
//         generated_backstory = personality.get("backstory", "");
//         if (!generated_backstory || generated_backstory.length < 50) {
//             # Create a richer backstory from the generated content
//             species_name = this.generated_content.get("species", {}).get("name", "Unknown");
//             primary_class = this.generated_content.get("primary_class", {}).get("name", "Adventurer");
//             background_name = this.generated_content.get("background", {}).get("name", "Wanderer");
            
//             generated_backstory = `A ${species_name} ${primary_class} with a background as a ${background_name}. `;
//             if (personality.get("personality_traits")) {
//                 generated_backstory += `Known for being ${personality['personality_traits'].slice(0, 2).join(', ')}. `;
//             }
//             if (personality.get("ideals")) {
//                 generated_backstory += `Driven by the ideal: '${personality['ideals'][0]}'. `;
//             }
//             if (personality.get("bonds")) {
//                 generated_backstory += `Bound by: '${personality['bonds'][0]}'. `;
//             }
//         }
        
//         this.character.backstory = generated_backstory;
        
//         print("✅ Character object created!");
//     }
    
//     def display_final_character(self):
//         """Display the complete AI-generated character."""
//         print("\n" + "=" * 80);
//         print("🎭 AI-GENERATED CHARACTER SHEET");
//         print("=" * 80);
        
//         # Basic Info
//         print(`Name: ${this.character.name}`);
//         print(`Species: ${this.character.species}`);
//         print(`Background: ${this.character.background}`);
//         print(`Alignment: ${' '.join(this.character.alignment)}`);
        
//         # Physical Description
//         if ("appearance" in this.generated_content) {
//             print(`Appearance: ${this.generated_content['appearance']}`);
//         }
        
//         # Age, Height, Weight (format nicely)
//         age = this.generated_content.get("age", "Unknown");
//         height = this.generated_content.get("height");
//         weight = this.generated_content.get("weight");
        
//         physical_stats = [];
//         if (age != "Unknown") {
//             physical_stats.append(`Age: ${age}`);
//         }
//         if (height && typeof height === 'number') {
//             feet = Math.floor(height / 12);
//             inches = height % 12;
//             physical_stats.append(`Height: ${feet}'${inches}"`);
//         } else if (height) {
//             physical_stats.append(`Height: ${height}`);
//         }
//         if (weight) {
//             physical_stats.append(`Weight: ${weight} lbs`);
//         }
        
//         if (physical_stats) {
//             print(`Physical: ${physical_stats.join(', ')}`);
//         }
        
//         # Classes
//         if (this.character.character_classes) {
//             classes_str = this.character.character_classes.map(({ cls, lvl }) => `${cls} ${lvl}`).join(', ');
//             total_level = Object.values(this.character.character_classes).reduce((a, b) => a + b, 0);
//             print(`Class(es): ${classes_str} (Total Level: ${total_level})`);
//         }
        
//         # Ability Scores
//         print("\nAbility Scores:");
//         modifiers = this.character.get_ability_modifiers();
//         abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"];
//         for (ability in abilities) {
//             ability_score_obj = this.character.get_ability_score(ability);
//             score = ability_score_obj.total_score if hasattr(ability_score_obj, 'total_score') else 10;
//             modifier = modifiers.get(ability, 0);
//             sign = modifier >= 0 ? "+" : "";
//             print(`  ${ability.title():13}: ${score:2d} (${sign}${modifier})`);
//         }
        
//         # Skills
//         if (this.character.skill_proficiencies) {
//             skills = this.character.skill_proficiencies.keys().map(skill => skill.replace("_", " ").title());
//             print(`\nSkill Proficiencies: ${skills.join(', ')}`);
//         }
        
//         # Equipment
//         equipment = this.generated_content.get("equipment", {});
//         if (equipment) {
//             print(`\nEquipment:`);
//             if (equipment.get("weapons")) {
//                 print(`  Weapons: ${equipment['weapons'].join(', ')}`);
//             }
//             if (equipment.get("armor")) {
//                 print(`  Armor: ${equipment['armor']}`);
//             }
//             if (equipment.get("tools")) {
//                 print(`  Tools: ${equipment['tools'].join(', ')}`);
//             }
//             if (equipment.get("magical_items")) {
//                 print(`  Magic Items: ${equipment['magical_items'].join(', ')}`);
//             }
//         }
        
//         # Custom Content
//         custom = this.generated_content.get("custom_content", {});
//         if (custom) {
//             print(`\nCustom Content:`);
//             
//             if (custom.get("custom_feats")) {
//                 print("  Custom Feats:");
//                 for (feat in custom["custom_feats"]) {
//                     print(`    • ${feat['name']}: ${feat['description']}`);
//                 }
//             }
//             
//             if (custom.get("custom_spells")) {
//                 print("  Custom Spells:");
//                 for (spell in custom["custom_spells"]) {
//                     print(`    • ${spell['name']} (Level ${spell['level']}): ${spell['description']}`);
//                 }
//             }
//             
//             if (custom.get("custom_items")) {
//                 print("  Custom Items:");
//                 for (item in custom["custom_items"]) {
//                     print(`    • ${item['name']}: ${item['description']}`);
//                 }
//             }
//         }
        
//         # Personality
//         print(`\nPersonality:`);
//         if (this.character.personality_traits) {
//             print(`  Traits: ${this.character.personality_traits.join(', ')}`);
//         }
//         if (this.character.ideals) {
//             print(`  Ideals: ${this.character.ideals.join(', ')}`);
//         }
//         if (this.character.bonds) {
//             print(`  Bonds: ${this.character.bonds.join(', ')}`);
//         }
//         if (this.character.flaws) {
//             print(`  Flaws: ${this.character.flaws.join(', ')}`);
//         }
        
//         # Backstory
//         if (this.character.backstory) {
//             print(`\nBackstory:`);
//             print(`  ${this.character.backstory}`);
//         }
        
//         print("\n" + "=" * 80);
//         print("🎉 Your AI-generated character is complete!");
//         print("How does this match your creative vision?");
//         print("=" * 80);
//     }
    
//     # Fallback methods for when AI generation fails
//     def use_fallback_species_class(self):
//         this.generated_content["species"] = {
//             "name": "Variant Human",
//             "abilities": {"strength": 13, "dexterity": 14, "constitution": 15, 
//                          "intelligence": 12, "wisdom": 10, "charisma": 16}
//         };
//         this.generated_content["primary_class"] = {
//             "name": "Custom Adventurer",
//             "level": 3
//         };
    
//     def use_fallback_skills_background(self):
//         this.generated_content["background"] = {"name": "Wanderer"};
//         this.generated_content["skills"] = ["Perception", "Insight", "Athletics", "Investigation"];
    
//     def use_fallback_equipment(self):
//         this.generated_content["equipment"] = {
//             "weapons": ["Longsword", "Shortbow"],
//             "armor": "Studded Leather",
//             "items": ["Explorer's Pack", "Rope", "Torches"]
//         };
    
//     def use_fallback_personality(self):
//         this.generated_content["personality"] = {
//             "personality_traits": ["Curious about the unknown"],
//             "ideals": ["Adventure calls to me"],
//             "bonds": ["I seek my true purpose"],
//             "flaws": ["I act before thinking"],
//             "backstory": "A mysterious figure with an unknown past, driven by curiosity and wanderlust."
//         };
// }


// async def main():
//     """Main function for AI character creation."""
//     try {
//         # Enable debug mode if requested
//         debug_mode = "--debug" in sys.argv || "-d" in sys.argv;
//         if (debug_mode) {
//             print("🔍 DEBUG MODE ENABLED - Will show raw LLM responses");
//         }
        
//         creator = AICharacterCreator(debug_mode=debug_mode);
//         await creator.start_creation();
//     } catch (KeyboardInterrupt) {
//         print("\n\nCharacter creation cancelled. Goodbye!");
//     } catch (error) {
//         print(`\n❌ An error occurred: ${error}`);
//         import traceback
//         traceback.print_exc();
// }


// if (__name__ == "__main__") {
//     asyncio.run(main());
// }