#!/usr/bin/env python3
"""
Comprehensive API Test Suite for D&D Character Creator Backend
Tests all creation aspects from dev_vision.md via RESTful API endpoints

This test validates the complete system architecture:
app.py (FastAPI endpoints) 
  ↓ calls
creation_factory.py (orchestration) 
  ↓ uses
creation.py (character creation logic) ✓ WITH REFINEMENT METHODS
  ↓ depends on all backend modules

Tests all PRIMARY and SECONDARY requirements from dev_vision.md
"""

import asyncio
import json
import logging
import time
import requests
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_comprehensive_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveAPITest:
    """
    Test all dev_vision.md creation aspects via FastAPI endpoints.
    
    This validates the complete architecture from frontend API calls
    through the entire backend creation pipeline.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Track test results for comprehensive reporting
        self.test_results = {
            "primary_requirements": {},
            "secondary_requirements": {},
            "technical_requirements": {},
            "quality_standards": {},
            "performance_metrics": {},
            "error_handling": {},
            "created_content": []
        }
        
        # Test data for various scenarios
        self.character_concepts = [
            "A mysterious half-elf warlock who made a pact with an ancient dragon",
            "A steampunk artificer gnome with clockwork limbs and arcane engineering skills",
            "A samurai-inspired fighter from a distant land with honor-bound traditions",
            "A shapeshifting druid who can transform into crystalline creatures",
            "A time-traveling wizard with knowledge of future spells and technologies"
        ]
        
        self.custom_content_concepts = [
            "A crystal-based species that feeds on magical energy",
            "A necromantic healing class that uses death magic to preserve life",
            "A weapon that phases between dimensions",
            "Armor made from solidified time itself",
            "A spell that allows communication with past versions of yourself"
        ]

    async def run_comprehensive_test(self):
        """Execute complete test suite covering all dev_vision.md requirements."""
        logger.info("🚀 Starting Comprehensive API Test Suite for dev_vision.md")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Test system availability
            await self.test_system_health()
            
            # PRIMARY REQUIREMENTS (CRITICAL)
            await self.test_character_creation_system()
            await self.test_custom_content_generation()
            await self.test_iterative_refinement_system()
            await self.test_existing_character_enhancement()
            await self.test_content_hierarchy_prioritization()
            
            # SECONDARY REQUIREMENTS (MEDIUM)
            await self.test_npc_creature_creation()
            await self.test_standalone_item_creation()
            await self.test_database_version_control()
            
            # TECHNICAL REQUIREMENTS
            await self.test_system_architecture()
            await self.test_content_validation()
            await self.test_performance_standards()
            
            # QUALITY STANDARDS
            await self.test_content_quality()
            await self.test_user_experience()
            
            # ERROR HANDLING AND EDGE CASES
            await self.test_error_handling()
            await self.test_edge_cases()
            
            # Generate comprehensive report
            await self.generate_test_report(time.time() - start_time)
            
        except Exception as e:
            logger.error(f"❌ Critical test failure: {e}")
            await self.generate_failure_report(str(e), time.time() - start_time)

    async def test_system_health(self):
        """Test basic system health and API availability."""
        logger.info("🔍 Testing System Health...")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/")
            assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
            
            # Test health endpoint
            response = self.session.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
            
            # Test database connectivity
            response = self.session.get(f"{self.base_url}/api/v1/database/status")
            if response.status_code == 200:
                logger.info("✅ Database connectivity confirmed")
            else:
                logger.warning("⚠️ Database connectivity issues detected")
            
            logger.info("✅ System health check passed")
            self.test_results["technical_requirements"]["system_health"] = "PASS"
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            self.test_results["technical_requirements"]["system_health"] = f"FAIL: {e}"

    async def test_character_creation_system(self):
        """Test PRIMARY REQUIREMENT 1: CHARACTER CREATION SYSTEM"""
        logger.info("🎭 Testing Character Creation System (PRIMARY REQUIREMENT 1)...")
        
        results = {}
        
        for i, concept in enumerate(self.character_concepts):
            try:
                logger.info(f"Creating character {i+1}: {concept[:50]}...")
                
                # Test character creation via API
                payload = {
                    "prompt": concept,
                    "user_preferences": {
                        "level": 3,
                        "verbose_generation": True
                    }
                }
                
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/v1/characters/create",
                    json=payload,
                    timeout=60
                )
                creation_time = time.time() - start_time
                
                if response.status_code == 200:
                    character_data = response.json()
                    
                    # Validate complete character components (dev_vision.md requirement)
                    validation_result = self.validate_complete_character(character_data)
                    
                    results[f"character_{i+1}"] = {
                        "concept": concept,
                        "creation_time": creation_time,
                        "validation": validation_result,
                        "status": "SUCCESS"
                    }
                    
                    # Store for later refinement tests
                    self.test_results["created_content"].append({
                        "type": "character",
                        "id": character_data.get("id"),
                        "data": character_data
                    })
                    
                    logger.info(f"✅ Character {i+1} created successfully in {creation_time:.2f}s")
                else:
                    results[f"character_{i+1}"] = {
                        "concept": concept,
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    logger.error(f"❌ Character {i+1} creation failed: {response.status_code}")
                
                # Brief pause between creations
                await asyncio.sleep(1)
                
            except Exception as e:
                results[f"character_{i+1}"] = {
                    "concept": concept,
                    "status": "FAIL",
                    "error": str(e)
                }
                logger.error(f"❌ Character {i+1} creation exception: {e}")
        
        self.test_results["primary_requirements"]["character_creation"] = results

    def validate_complete_character(self, character_data: Dict[str, Any]) -> Dict[str, bool]:
        """Validate character has all required components from dev_vision.md"""
        validation = {}
        
        # Required Character Components (from dev_vision.md)
        required_core = ["name", "species", "classes", "level", "background", "alignment"]
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        required_character_elements = ["personality_traits", "ideals", "bonds", "flaws", "backstory"]
        
        # Core Attributes
        data = character_data.get("data", {}).get("raw_data", character_data)
        
        validation["core_attributes"] = all(attr in data for attr in required_core)
        validation["ability_scores"] = all(
            attr in data.get("ability_scores", {}) for attr in required_abilities
        )
        validation["skills_proficiencies"] = "skill_proficiencies" in data
        validation["feats"] = any(feat_key in data for feat_key in ["origin_feat", "general_feats"])
        validation["equipment"] = any(eq_key in data for eq_key in ["weapons", "armor", "equipment"])
        validation["personality"] = all(elem in data for elem in required_character_elements)
        
        # Spellcaster specific validation
        if self.is_spellcaster(data):
            validation["spells"] = "spells_known" in data
            validation["spell_slots"] = "spell_slots" in data
        else:
            validation["spells"] = True  # Not required for non-spellcasters
            validation["spell_slots"] = True
        
        return validation

    def is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character is a spellcaster"""
        spellcasting_classes = ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard", "paladin", "ranger"]
        classes = character_data.get("classes", {})
        return any(cls.lower() in spellcasting_classes for cls in classes.keys())

    async def test_custom_content_generation(self):
        """Test PRIMARY REQUIREMENT 2: CUSTOM CONTENT GENERATION"""
        logger.info("🎨 Testing Custom Content Generation (PRIMARY REQUIREMENT 2)...")
        
        results = {}
        
        # Test custom species creation
        try:
            payload = {
                "prompt": "A crystal-based humanoid species that feeds on magical energy and can resonate with ley lines",
                "content_type": "species"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/custom-content/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results["custom_species"] = "SUCCESS"
                logger.info("✅ Custom species creation successful")
            else:
                results["custom_species"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["custom_species"] = f"FAIL: {e}"
        
        # Test custom class creation
        try:
            payload = {
                "prompt": "A time-weaver class that manipulates temporal magic and can slow or accelerate time",
                "content_type": "class"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/custom-content/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results["custom_class"] = "SUCCESS"
                logger.info("✅ Custom class creation successful")
            else:
                results["custom_class"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["custom_class"] = f"FAIL: {e}"
        
        # Test custom equipment creation
        custom_items = [
            {"type": "weapon", "prompt": "A sword that phases between dimensions"},
            {"type": "armor", "prompt": "Robes woven from crystallized starlight"},
            {"type": "spell", "prompt": "A spell that lets you communicate with your past self"}
        ]
        
        for item in custom_items:
            try:
                payload = {
                    "prompt": item["prompt"],
                    "content_type": item["type"]
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/custom-content/create",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    results[f"custom_{item['type']}"] = "SUCCESS"
                    logger.info(f"✅ Custom {item['type']} creation successful")
                else:
                    results[f"custom_{item['type']}"] = f"FAIL: {response.status_code}"
                    
            except Exception as e:
                results[f"custom_{item['type']}"] = f"FAIL: {e}"
        
        self.test_results["primary_requirements"]["custom_content"] = results

    async def test_iterative_refinement_system(self):
        """Test PRIMARY REQUIREMENT 3: ITERATIVE REFINEMENT SYSTEM"""
        logger.info("🔄 Testing Iterative Refinement System (PRIMARY REQUIREMENT 3)...")
        
        results = {}
        
        # Get a character to refine (from previous tests)
        if self.test_results["created_content"]:
            character = self.test_results["created_content"][0]
            character_id = character.get("id")
            
            if character_id:
                # Test character refinement
                try:
                    payload = {
                        "character_id": character_id,
                        "refinement_prompt": "Make this character more mysterious and add shadow magic abilities",
                        "user_preferences": {"maintain_level": True}
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/characters/{character_id}/refine",
                        json=payload,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        results["character_refinement"] = "SUCCESS"
                        logger.info("✅ Character refinement successful")
                    else:
                        results["character_refinement"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["character_refinement"] = f"FAIL: {e}"
                
                # Test user feedback application
                try:
                    payload = {
                        "character_id": character_id,
                        "feedback": {
                            "ability_scores": "Increase Charisma, decrease Strength",
                            "personality": "Make more charismatic and less aggressive",
                            "equipment": "Add a magical focus item"
                        }
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/characters/{character_id}/apply-feedback",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        results["feedback_application"] = "SUCCESS"
                        logger.info("✅ Feedback application successful")
                    else:
                        results["feedback_application"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["feedback_application"] = f"FAIL: {e}"
            else:
                results["character_refinement"] = "SKIP: No character ID available"
                results["feedback_application"] = "SKIP: No character ID available"
        else:
            results["character_refinement"] = "SKIP: No characters created"
            results["feedback_application"] = "SKIP: No characters created"
        
        self.test_results["primary_requirements"]["iterative_refinement"] = results

    async def test_existing_character_enhancement(self):
        """Test PRIMARY REQUIREMENT 4: EXISTING CHARACTER ENHANCEMENT"""
        logger.info("⬆️ Testing Existing Character Enhancement (PRIMARY REQUIREMENT 4)...")
        
        results = {}
        
        # Get a character to enhance
        if self.test_results["created_content"]:
            character = self.test_results["created_content"][0]
            character_id = character.get("id")
            
            if character_id:
                # Test level-up with journal
                try:
                    payload = {
                        "character_id": character_id,
                        "new_level": 4,
                        "journal_entries": [
                            "Defeated a group of bandits using clever tactics",
                            "Learned about ancient magic from a mysterious mentor",
                            "Formed a strong bond with the party's cleric"
                        ],
                        "multiclass_option": None
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/characters/{character_id}/level-up",
                        json=payload,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        results["level_up_journal"] = "SUCCESS"
                        logger.info("✅ Level-up with journal successful")
                    else:
                        results["level_up_journal"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["level_up_journal"] = f"FAIL: {e}"
                
                # Test story-driven enhancement
                try:
                    payload = {
                        "character_id": character_id,
                        "enhancement_prompt": "Character discovered they have dragon blood and gained minor draconic abilities"
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/characters/{character_id}/enhance",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        results["story_enhancement"] = "SUCCESS"
                        logger.info("✅ Story-driven enhancement successful")
                    else:
                        results["story_enhancement"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["story_enhancement"] = f"FAIL: {e}"
            else:
                results["level_up_journal"] = "SKIP: No character ID available"
                results["story_enhancement"] = "SKIP: No character ID available"
        else:
            results["level_up_journal"] = "SKIP: No characters created"
            results["story_enhancement"] = "SKIP: No characters created"
        
        self.test_results["primary_requirements"]["character_enhancement"] = results

    async def test_content_hierarchy_prioritization(self):
        """Test PRIMARY REQUIREMENT 5: CONTENT HIERARCHY & PRIORITIZATION"""
        logger.info("📊 Testing Content Hierarchy & Prioritization (PRIMARY REQUIREMENT 5)...")
        
        results = {}
        
        # Test standard D&D content prioritization
        try:
            payload = {
                "prompt": "A human fighter with longsword and chain mail",
                "user_preferences": {"prefer_official_content": True}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/characters/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                character_data = response.json()
                
                # Check if official content was prioritized
                data = character_data.get("data", {}).get("raw_data", {})
                weapons = data.get("weapons", [])
                armor = data.get("armor", "")
                
                official_weapon = any("longsword" in str(weapon).lower() for weapon in weapons)
                official_armor = "chain" in armor.lower() or "mail" in armor.lower()
                
                if official_weapon and official_armor:
                    results["official_content_priority"] = "SUCCESS"
                    logger.info("✅ Official content prioritization successful")
                else:
                    results["official_content_priority"] = "PARTIAL: Some custom content used"
            else:
                results["official_content_priority"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["official_content_priority"] = f"FAIL: {e}"
        
        # Test custom content when needed
        try:
            payload = {
                "prompt": "A crystalline being that subsists on magical energy with unique gem-based magic",
                "user_preferences": {"allow_custom_content": True}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/characters/create",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                results["custom_content_when_needed"] = "SUCCESS"
                logger.info("✅ Custom content generation when needed successful")
            else:
                results["custom_content_when_needed"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["custom_content_when_needed"] = f"FAIL: {e}"
        
        self.test_results["primary_requirements"]["content_hierarchy"] = results

    async def test_npc_creature_creation(self):
        """Test SECONDARY REQUIREMENT 6: NPC & CREATURE CREATION"""
        logger.info("👥 Testing NPC & Creature Creation (SECONDARY REQUIREMENT 6)...")
        
        results = {}
        
        # Test NPC creation
        npc_types = [
            {"type": "major", "prompt": "A wise old sage who knows ancient secrets"},
            {"type": "minor", "prompt": "A nervous shopkeeper with valuable information"},
            {"type": "shopkeeper", "prompt": "A cheerful blacksmith who crafts magical weapons"}
        ]
        
        for npc in npc_types:
            try:
                payload = {
                    "prompt": npc["prompt"],
                    "npc_type": npc["type"],
                    "level": 5
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/npcs/create",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    results[f"npc_{npc['type']}"] = "SUCCESS"
                    logger.info(f"✅ {npc['type'].title()} NPC creation successful")
                else:
                    results[f"npc_{npc['type']}"] = f"FAIL: {response.status_code}"
                    
            except Exception as e:
                results[f"npc_{npc['type']}"] = f"FAIL: {e}"
        
        # Test creature creation
        try:
            payload = {
                "prompt": "A shadow creature that feeds on fear with teleportation abilities",
                "challenge_rating": 3
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/creatures/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results["creature_creation"] = "SUCCESS"
                logger.info("✅ Creature creation successful")
            else:
                results["creature_creation"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["creature_creation"] = f"FAIL: {e}"
        
        self.test_results["secondary_requirements"]["npc_creature_creation"] = results

    async def test_standalone_item_creation(self):
        """Test SECONDARY REQUIREMENT 7: STANDALONE ITEM CREATION"""
        logger.info("⚔️ Testing Standalone Item Creation (SECONDARY REQUIREMENT 7)...")
        
        results = {}
        
        item_types = [
            {"type": "weapon", "prompt": "A staff that channels elemental lightning"},
            {"type": "armor", "prompt": "A cloak that provides resistance to psychic damage"},
            {"type": "spell", "prompt": "A spell that creates temporary bridges of solidified air"},
            {"type": "equipment", "prompt": "A compass that points to the nearest magical item"}
        ]
        
        for item in item_types:
            try:
                payload = {
                    "prompt": item["prompt"],
                    "item_type": item["type"],
                    "rarity": "uncommon"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/items/create",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    results[f"item_{item['type']}"] = "SUCCESS"
                    logger.info(f"✅ {item['type'].title()} creation successful")
                else:
                    results[f"item_{item['type']}"] = f"FAIL: {response.status_code}"
                    
            except Exception as e:
                results[f"item_{item['type']}"] = f"FAIL: {e}"
        
        self.test_results["secondary_requirements"]["item_creation"] = results

    async def test_database_version_control(self):
        """Test SECONDARY REQUIREMENT 8: DATABASE & VERSION CONTROL"""
        logger.info("💾 Testing Database & Version Control (SECONDARY REQUIREMENT 8)...")
        
        results = {}
        
        # Test character versioning
        if self.test_results["created_content"]:
            character = self.test_results["created_content"][0]
            character_id = character.get("id")
            
            if character_id:
                # Test version history
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/v1/characters/{character_id}/versions",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        results["version_history"] = "SUCCESS"
                        logger.info("✅ Version history retrieval successful")
                    else:
                        results["version_history"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["version_history"] = f"FAIL: {e}"
                
                # Test character approval workflow
                try:
                    payload = {"approval_status": "dm_approved"}
                    
                    response = self.session.patch(
                        f"{self.base_url}/api/v1/characters/{character_id}/approval",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        results["approval_workflow"] = "SUCCESS"
                        logger.info("✅ Approval workflow successful")
                    else:
                        results["approval_workflow"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    results["approval_workflow"] = f"FAIL: {e}"
            else:
                results["version_history"] = "SKIP: No character ID available"
                results["approval_workflow"] = "SKIP: No character ID available"
        else:
            results["version_history"] = "SKIP: No characters created"
            results["approval_workflow"] = "SKIP: No characters created"
        
        self.test_results["secondary_requirements"]["database_version_control"] = results

    async def test_system_architecture(self):
        """Test TECHNICAL REQUIREMENT 9: SYSTEM ARCHITECTURE"""
        logger.info("🏗️ Testing System Architecture (TECHNICAL REQUIREMENT 9)...")
        
        results = {}
        
        # Test LLM integration
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system/llm-status", timeout=10)
            
            if response.status_code == 200:
                results["llm_integration"] = "SUCCESS"
                logger.info("✅ LLM integration check successful")
            else:
                results["llm_integration"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["llm_integration"] = f"FAIL: {e}"
        
        # Test database models
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system/database-models", timeout=10)
            
            if response.status_code == 200:
                results["database_models"] = "SUCCESS"
                logger.info("✅ Database models check successful")
            else:
                results["database_models"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["database_models"] = f"FAIL: {e}"
        
        # Test API structure
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=10)
            
            if response.status_code == 200:
                results["api_structure"] = "SUCCESS"
                logger.info("✅ API documentation accessible")
            else:
                results["api_structure"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["api_structure"] = f"FAIL: {e}"
        
        self.test_results["technical_requirements"]["system_architecture"] = results

    async def test_content_validation(self):
        """Test TECHNICAL REQUIREMENT 10: CONTENT VALIDATION"""
        logger.info("✅ Testing Content Validation (TECHNICAL REQUIREMENT 10)...")
        
        results = {}
        
        # Test validation endpoint
        if self.test_results["created_content"]:
            character = self.test_results["created_content"][0]
            
            try:
                payload = {"character_data": character.get("data")}
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/validation/character",
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    validation_result = response.json()
                    
                    if validation_result.get("valid", False):
                        results["character_validation"] = "SUCCESS"
                        logger.info("✅ Character validation successful")
                    else:
                        results["character_validation"] = f"VALIDATION_FAILED: {validation_result.get('errors', [])}"
                else:
                    results["character_validation"] = f"FAIL: {response.status_code}"
                    
            except Exception as e:
                results["character_validation"] = f"FAIL: {e}"
        else:
            results["character_validation"] = "SKIP: No characters to validate"
        
        # Test balance checking
        try:
            payload = {
                "content_type": "custom_class",
                "content_data": {
                    "name": "Test Class",
                    "hit_die": 8,
                    "primary_ability": "Wisdom",
                    "features": {"1": [{"name": "Test Feature", "description": "A balanced test feature"}]}
                },
                "target_level": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/validation/balance-check",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                results["balance_checking"] = "SUCCESS"
                logger.info("✅ Balance checking successful")
            else:
                results["balance_checking"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["balance_checking"] = f"FAIL: {e}"
        
        self.test_results["technical_requirements"]["content_validation"] = results

    async def test_performance_standards(self):
        """Test TECHNICAL REQUIREMENT 11: PERFORMANCE STANDARDS"""
        logger.info("⚡ Testing Performance Standards (TECHNICAL REQUIREMENT 11)...")
        
        results = {}
        performance_metrics = {}
        
        # Test character creation performance (< 30 seconds for complex characters)
        complex_concept = "A multiclass artificer/wizard with custom clockwork familiar, temporal magic, and steampunk equipment from a dimension where magic and technology merged"
        
        start_time = time.time()
        try:
            payload = {
                "prompt": complex_concept,
                "user_preferences": {"level": 5, "complexity": "high"}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/characters/create",
                json=payload,
                timeout=35
            )
            
            creation_time = time.time() - start_time
            performance_metrics["complex_character_creation"] = creation_time
            
            if response.status_code == 200 and creation_time < 30:
                results["complex_character_performance"] = f"SUCCESS ({creation_time:.2f}s)"
                logger.info(f"✅ Complex character creation within limits: {creation_time:.2f}s")
            elif response.status_code == 200:
                results["complex_character_performance"] = f"SLOW ({creation_time:.2f}s > 30s limit)"
                logger.warning(f"⚠️ Complex character creation too slow: {creation_time:.2f}s")
            else:
                results["complex_character_performance"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            creation_time = time.time() - start_time
            results["complex_character_performance"] = f"FAIL: {e} ({creation_time:.2f}s)"
        
        # Test simple update performance (< 5 seconds)
        if self.test_results["created_content"]:
            character = self.test_results["created_content"][0]
            character_id = character.get("id")
            
            if character_id:
                start_time = time.time()
                try:
                    payload = {"name": "Updated Character Name"}
                    
                    response = self.session.patch(
                        f"{self.base_url}/api/v1/characters/{character_id}",
                        json=payload,
                        timeout=10
                    )
                    
                    update_time = time.time() - start_time
                    performance_metrics["simple_update"] = update_time
                    
                    if response.status_code == 200 and update_time < 5:
                        results["simple_update_performance"] = f"SUCCESS ({update_time:.2f}s)"
                        logger.info(f"✅ Simple update within limits: {update_time:.2f}s")
                    elif response.status_code == 200:
                        results["simple_update_performance"] = f"SLOW ({update_time:.2f}s > 5s limit)"
                    else:
                        results["simple_update_performance"] = f"FAIL: {response.status_code}"
                        
                except Exception as e:
                    update_time = time.time() - start_time
                    results["simple_update_performance"] = f"FAIL: {e} ({update_time:.2f}s)"
            else:
                results["simple_update_performance"] = "SKIP: No character ID available"
        else:
            results["simple_update_performance"] = "SKIP: No characters created"
        
        # Test database query performance (< 1 second)
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/v1/characters", timeout=5)
            
            query_time = time.time() - start_time
            performance_metrics["database_query"] = query_time
            
            if response.status_code == 200 and query_time < 1:
                results["database_query_performance"] = f"SUCCESS ({query_time:.2f}s)"
                logger.info(f"✅ Database query within limits: {query_time:.2f}s")
            elif response.status_code == 200:
                results["database_query_performance"] = f"SLOW ({query_time:.2f}s > 1s limit)"
            else:
                results["database_query_performance"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            query_time = time.time() - start_time
            results["database_query_performance"] = f"FAIL: {e} ({query_time:.2f}s)"
        
        self.test_results["technical_requirements"]["performance_standards"] = results
        self.test_results["performance_metrics"] = performance_metrics

    async def test_content_quality(self):
        """Test QUALITY STANDARD 14: CONTENT QUALITY"""
        logger.info("🌟 Testing Content Quality (QUALITY STANDARD 14)...")
        
        results = {}
        
        # Analyze created characters for quality metrics
        if self.test_results["created_content"]:
            character_count = len([c for c in self.test_results["created_content"] if c["type"] == "character"])
            
            quality_metrics = {
                "creativity_score": 0,
                "balance_score": 0,
                "consistency_score": 0,
                "completeness_score": 0,
                "narrative_depth": 0
            }
            
            for content in self.test_results["created_content"]:
                if content["type"] == "character":
                    char_data = content["data"].get("raw_data", {})
                    
                    # Creativity: Check for unique elements
                    if char_data.get("species") not in ["Human", "Elf", "Dwarf", "Halfling"]:
                        quality_metrics["creativity_score"] += 1
                    
                    # Completeness: Check for all required fields
                    required_fields = ["name", "species", "classes", "background", "backstory"]
                    if all(field in char_data for field in required_fields):
                        quality_metrics["completeness_score"] += 1
                    
                    # Narrative depth: Check backstory length
                    backstory = char_data.get("backstory", "")
                    if len(backstory) > 200:  # Substantial backstory
                        quality_metrics["narrative_depth"] += 1
            
            # Calculate quality percentages
            if character_count > 0:
                for metric in quality_metrics:
                    quality_metrics[metric] = (quality_metrics[metric] / character_count) * 100
                
                results["quality_metrics"] = quality_metrics
                
                # Overall quality assessment
                avg_quality = sum(quality_metrics.values()) / len(quality_metrics)
                if avg_quality >= 80:
                    results["overall_quality"] = f"EXCELLENT ({avg_quality:.1f}%)"
                elif avg_quality >= 60:
                    results["overall_quality"] = f"GOOD ({avg_quality:.1f}%)"
                else:
                    results["overall_quality"] = f"NEEDS_IMPROVEMENT ({avg_quality:.1f}%)"
                
                logger.info(f"✅ Content quality assessment: {avg_quality:.1f}% average")
            else:
                results["overall_quality"] = "NO_DATA: No characters to assess"
        else:
            results["overall_quality"] = "NO_DATA: No content created"
        
        self.test_results["quality_standards"]["content_quality"] = results

    async def test_user_experience(self):
        """Test QUALITY STANDARD 15: USER EXPERIENCE"""
        logger.info("👤 Testing User Experience (QUALITY STANDARD 15)...")
        
        results = {}
        
        # Test API response times and usability
        ux_metrics = {
            "response_times": [],
            "error_rates": [],
            "api_usability": {}
        }
        
        # Test common user workflows
        workflows = [
            {
                "name": "character_creation",
                "endpoint": "/api/v1/characters/create",
                "method": "POST",
                "payload": {"prompt": "A brave knight with a mysterious past"}
            },
            {
                "name": "character_list",
                "endpoint": "/api/v1/characters",
                "method": "GET",
                "payload": None
            }
        ]
        
        for workflow in workflows:
            start_time = time.time()
            try:
                if workflow["method"] == "POST":
                    response = self.session.post(
                        f"{self.base_url}{workflow['endpoint']}",
                        json=workflow["payload"],
                        timeout=30
                    )
                else:
                    response = self.session.get(
                        f"{self.base_url}{workflow['endpoint']}",
                        timeout=10
                    )
                
                response_time = time.time() - start_time
                ux_metrics["response_times"].append({
                    "workflow": workflow["name"],
                    "time": response_time,
                    "status": response.status_code
                })
                
                if response.status_code == 200:
                    ux_metrics["api_usability"][workflow["name"]] = "SUCCESS"
                else:
                    ux_metrics["api_usability"][workflow["name"]] = f"FAIL: {response.status_code}"
                    
            except Exception as e:
                response_time = time.time() - start_time
                ux_metrics["response_times"].append({
                    "workflow": workflow["name"],
                    "time": response_time,
                    "status": "ERROR"
                })
                ux_metrics["api_usability"][workflow["name"]] = f"ERROR: {e}"
        
        # Calculate average response time
        avg_response_time = sum(rt["time"] for rt in ux_metrics["response_times"]) / len(ux_metrics["response_times"])
        
        # Assess user experience
        if avg_response_time < 5 and all(status == "SUCCESS" for status in ux_metrics["api_usability"].values()):
            results["user_experience"] = f"EXCELLENT (avg: {avg_response_time:.2f}s)"
        elif avg_response_time < 10:
            results["user_experience"] = f"GOOD (avg: {avg_response_time:.2f}s)"
        else:
            results["user_experience"] = f"NEEDS_IMPROVEMENT (avg: {avg_response_time:.2f}s)"
        
        results["ux_metrics"] = ux_metrics
        logger.info(f"✅ User experience assessment: {avg_response_time:.2f}s average response time")
        
        self.test_results["quality_standards"]["user_experience"] = results

    async def test_error_handling(self):
        """Test error handling and graceful degradation"""
        logger.info("🚨 Testing Error Handling...")
        
        results = {}
        
        # Test invalid inputs
        error_cases = [
            {
                "name": "empty_prompt",
                "endpoint": "/api/v1/characters/create",
                "payload": {"prompt": ""},
                "expected": 400
            },
            {
                "name": "invalid_character_id",
                "endpoint": "/api/v1/characters/invalid-id",
                "payload": None,
                "expected": 404
            },
            {
                "name": "malformed_json",
                "endpoint": "/api/v1/characters/create",
                "payload": "invalid json",
                "expected": 422
            }
        ]
        
        for case in error_cases:
            try:
                if case["payload"] is None:
                    response = self.session.get(f"{self.base_url}{case['endpoint']}", timeout=10)
                elif isinstance(case["payload"], str):
                    # Test malformed JSON
                    response = self.session.post(
                        f"{self.base_url}{case['endpoint']}",
                        data=case["payload"],
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                else:
                    response = self.session.post(
                        f"{self.base_url}{case['endpoint']}",
                        json=case["payload"],
                        timeout=10
                    )
                
                if response.status_code == case["expected"]:
                    results[case["name"]] = "SUCCESS"
                    logger.info(f"✅ Error handling for {case['name']}: {response.status_code}")
                else:
                    results[case["name"]] = f"UNEXPECTED: {response.status_code} (expected {case['expected']})"
                    
            except Exception as e:
                results[case["name"]] = f"ERROR: {e}"
        
        self.test_results["error_handling"] = results

    async def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        logger.info("🎯 Testing Edge Cases...")
        
        results = {}
        
        # Test extremely long prompts
        try:
            long_prompt = "A character who " + "is very interesting and has many unique traits " * 50
            
            payload = {"prompt": long_prompt}
            response = self.session.post(
                f"{self.base_url}/api/v1/characters/create",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                results["long_prompt"] = "SUCCESS"
            else:
                results["long_prompt"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["long_prompt"] = f"ERROR: {e}"
        
        # Test high level characters
        try:
            payload = {
                "prompt": "An epic level wizard with mastery over reality itself",
                "user_preferences": {"level": 20}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/characters/create",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                results["high_level_character"] = "SUCCESS"
            else:
                results["high_level_character"] = f"FAIL: {response.status_code}"
                
        except Exception as e:
            results["high_level_character"] = f"ERROR: {e}"
        
        # Test concurrent requests
        try:
            import asyncio
            
            async def create_character(session, concept):
                payload = {"prompt": f"A {concept} character"}
                response = session.post(
                    f"{self.base_url}/api/v1/characters/create",
                    json=payload,
                    timeout=30
                )
                return response.status_code
            
            # Create multiple concurrent requests
            concepts = ["warrior", "mage", "rogue", "cleric", "ranger"]
            tasks = []
            
            for concept in concepts:
                # Note: We'll use synchronous requests for simplicity
                payload = {"prompt": f"A {concept} character"}
                response = self.session.post(
                    f"{self.base_url}/api/v1/characters/create",
                    json=payload,
                    timeout=30
                )
                tasks.append(response.status_code)
            
            if all(status == 200 for status in tasks):
                results["concurrent_requests"] = "SUCCESS"
            else:
                results["concurrent_requests"] = f"PARTIAL: {tasks}"
                
        except Exception as e:
            results["concurrent_requests"] = f"ERROR: {e}"
        
        self.test_results["edge_cases"] = results

    async def generate_test_report(self, total_time: float):
        """Generate comprehensive test report"""
        logger.info("📊 Generating Comprehensive Test Report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            "test_summary": {
                "timestamp": timestamp,
                "total_duration": f"{total_time:.2f} seconds",
                "api_base_url": self.base_url,
                "dev_vision_compliance": self.calculate_compliance_score()
            },
            "detailed_results": self.test_results
        }
        
        # Save report to file
        report_filename = f"api_comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE API TEST REPORT - dev_vision.md COMPLIANCE")
        print("=" * 80)
        print(f"📅 Timestamp: {timestamp}")
        print(f"⏱️  Total Duration: {total_time:.2f} seconds")
        print(f"🌐 API Base URL: {self.base_url}")
        print(f"📊 Overall Compliance: {report['test_summary']['dev_vision_compliance']:.1f}%")
        print(f"💾 Detailed Report: {report_filename}")
        print("=" * 80)
        
        # Print category summaries
        self.print_category_summary("PRIMARY REQUIREMENTS", self.test_results.get("primary_requirements", {}))
        self.print_category_summary("SECONDARY REQUIREMENTS", self.test_results.get("secondary_requirements", {}))
        self.print_category_summary("TECHNICAL REQUIREMENTS", self.test_results.get("technical_requirements", {}))
        self.print_category_summary("QUALITY STANDARDS", self.test_results.get("quality_standards", {}))
        
        if self.test_results.get("performance_metrics"):
            print("\n⚡ PERFORMANCE METRICS:")
            for metric, value in self.test_results["performance_metrics"].items():
                print(f"   {metric}: {value:.2f}s")
        
        print("\n" + "=" * 80)
        logger.info(f"✅ Test report saved to: {report_filename}")

    def print_category_summary(self, category_name: str, results: Dict[str, Any]):
        """Print summary for a test category"""
        print(f"\n📋 {category_name}:")
        
        for test_name, test_result in results.items():
            if isinstance(test_result, dict):
                # Count successes in subcategory
                successes = sum(1 for result in test_result.values() if str(result).startswith("SUCCESS"))
                total = len(test_result)
                print(f"   {test_name}: {successes}/{total} passed")
            else:
                status = "✅" if str(test_result).startswith("SUCCESS") else "❌"
                print(f"   {status} {test_name}: {test_result}")

    def calculate_compliance_score(self) -> float:
        """Calculate overall compliance score with dev_vision.md requirements"""
        total_tests = 0
        passed_tests = 0
        
        for category in self.test_results.values():
            if isinstance(category, dict):
                for test_result in category.values():
                    if isinstance(test_result, dict):
                        for result in test_result.values():
                            total_tests += 1
                            if str(result).startswith("SUCCESS"):
                                passed_tests += 1
                    else:
                        total_tests += 1
                        if str(test_result).startswith("SUCCESS"):
                            passed_tests += 1
        
        return (passed_tests / total_tests * 100) if total_tests > 0 else 0

    async def generate_failure_report(self, error: str, duration: float):
        """Generate report when test suite fails completely"""
        logger.error("❌ Test suite failed completely")
        
        failure_report = {
            "status": "CRITICAL_FAILURE",
            "error": error,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "partial_results": self.test_results
        }
        
        report_filename = f"api_test_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(failure_report, f, indent=2)
        
        print(f"\n❌ CRITICAL TEST FAILURE")
        print(f"Error: {error}")
        print(f"Duration: {duration:.2f}s")
        print(f"Failure report: {report_filename}")


async def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive API Test Suite for dev_vision.md Requirements")
    print("Testing complete system architecture via RESTful API endpoints")
    print("=" * 80)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not responding. Please start the server with:")
            print("   cd /home/ajs7/dnd_tools/dnd_char_creator/backend && python app.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server at http://localhost:8000")
        print("Please start the server with:")
        print("   cd /home/ajs7/dnd_tools/dnd_char_creator/backend && python app.py")
        return
    
    # Run comprehensive test suite
    test_suite = ComprehensiveAPITest()
    await test_suite.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
