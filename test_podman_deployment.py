#!/usr/bin/env python3
"""
Comprehensive Podman Deployment Test
Tests all dev_vision.md creation aspects via containerized REST API

This script validates:
1. Container builds and runs with Podman
2. All API endpoints work as expected
3. Character creation with existing D&D content
4. Custom content generation capabilities
5. Iterative refinement system
6. Character advancement features
7. NPC and creature creation
8. System performance and reliability
"""

import asyncio
import json
import time
import subprocess
import requests
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PodmanDeploymentTest:
    """Comprehensive test suite for Podman-deployed D&D Character Creator."""
    
    def __init__(self):
        self.container_name = "dnd-character-creator"
        self.base_url = "http://localhost:8000"
        self.container_id = None
        self.test_results = {
            "container_deployment": False,
            "api_health": False,
            "character_creation": False,
            "custom_content": False,
            "refinement_system": False,
            "advancement_system": False,
            "npc_creation": False,
            "performance": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
    
    async def run_full_test_suite(self):
        """Run the complete test suite."""
        logger.info("🚀 Starting Podman Deployment Test Suite")
        logger.info("Testing all dev_vision.md creation aspects via REST API")
        
        try:
            # Phase 1: Container Deployment
            await self.test_container_deployment()
            
            # Phase 2: API Health and Basic Connectivity
            await self.test_api_health()
            
            # Phase 3: Core Character Creation (Priority 1)
            await self.test_character_creation()
            
            # Phase 4: Custom Content Generation (Priority 2)
            await self.test_custom_content_generation()
            
            # Phase 5: Iterative Refinement System (Priority 3)
            await self.test_refinement_system()
            
            # Phase 6: Character Advancement (Priority 4)
            await self.test_advancement_system()
            
            # Phase 7: NPC and Creature Creation (Priority 5)
            await self.test_npc_creation()
            
            # Phase 8: Performance and Reliability
            await self.test_performance()
            
            # Generate final report
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
        finally:
            # Cleanup
            await self.cleanup_container()
    
    async def test_container_deployment(self):
        """Test Podman container build and deployment."""
        logger.info("📦 Testing Podman Container Deployment")
        
        try:
            # Build container with Podman
            logger.info("Building container with Podman...")
            build_result = subprocess.run([
                "podman", "build", 
                "-t", self.container_name,
                "-f", "backend/Dockerfile",
                "."
            ], capture_output=True, text=True, cwd="/home/ajs7/dnd_tools/dnd_char_creator")
            
            if build_result.returncode != 0:
                logger.error(f"Container build failed: {build_result.stderr}")
                self._record_test("container_deployment", False)
                return
            
            logger.info("✅ Container built successfully")
            
            # Run container with Podman
            logger.info("Starting container with Podman...")
            run_result = subprocess.run([
                "podman", "run", "-d",
                "--name", self.container_name,
                "-p", "8000:8000",
                "--userns=keep-id",
                self.container_name
            ], capture_output=True, text=True)
            
            if run_result.returncode != 0:
                logger.error(f"Container run failed: {run_result.stderr}")
                self._record_test("container_deployment", False)
                return
            
            self.container_id = run_result.stdout.strip()
            logger.info(f"✅ Container started with ID: {self.container_id}")
            
            # Wait for container to be ready
            await asyncio.sleep(10)
            
            # Check container status
            status_result = subprocess.run([
                "podman", "ps", "--format", "{{.Status}}", 
                "--filter", f"name={self.container_name}"
            ], capture_output=True, text=True)
            
            if "Up" in status_result.stdout:
                logger.info("✅ Container is running successfully")
                self._record_test("container_deployment", True)
            else:
                logger.error("❌ Container is not running properly")
                self._record_test("container_deployment", False)
                
        except Exception as e:
            logger.error(f"Container deployment test failed: {e}")
            self._record_test("container_deployment", False)
    
    async def test_api_health(self):
        """Test API health and basic connectivity."""
        logger.info("🏥 Testing API Health and Connectivity")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Health endpoint responding")
                self._record_test("api_health", True)
            else:
                logger.error(f"❌ Health endpoint failed: {response.status_code}")
                self._record_test("api_health", False)
                return
            
            # Test root endpoint
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Root endpoint responding")
            else:
                logger.warning(f"⚠️ Root endpoint returned: {response.status_code}")
            
            # Test API documentation
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API documentation available")
            else:
                logger.warning("⚠️ API documentation not accessible")
                
        except Exception as e:
            logger.error(f"API health test failed: {e}")
            self._record_test("api_health", False)
    
    async def test_character_creation(self):
        """Test core character creation functionality."""
        logger.info("🧙 Testing Character Creation (dev_vision.md Priority 1)")
        
        test_cases = [
            {
                "name": "Traditional Fighter",
                "prompt": "Create a human fighter wielding a longsword and shield",
                "level": 1
            },
            {
                "name": "Spellcaster Wizard",
                "prompt": "Create a high elf wizard specializing in evocation magic",
                "level": 3
            },
            {
                "name": "Complex Multiclass",
                "prompt": "Create a half-orc barbarian/ranger who fights with two axes",
                "level": 5
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                logger.info(f"Testing: {test_case['name']}")
                
                response = requests.post(
                    f"{self.base_url}/create/character",
                    json={
                        "prompt": test_case["prompt"],
                        "preferences": {"level": test_case["level"]}
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    character_data = response.json()
                    
                    # Validate required components per dev_vision.md
                    required_fields = [
                        "name", "species", "classes", "level", "background",
                        "ability_scores", "skills", "equipment", "backstory"
                    ]
                    
                    if all(field in character_data for field in required_fields):
                        logger.info(f"✅ {test_case['name']} created successfully")
                        success_count += 1
                    else:
                        logger.error(f"❌ {test_case['name']} missing required fields")
                else:
                    logger.error(f"❌ {test_case['name']} creation failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Character creation test failed for {test_case['name']}: {e}")
        
        self._record_test("character_creation", success_count == len(test_cases))
    
    async def test_custom_content_generation(self):
        """Test custom content generation capabilities."""
        logger.info("🎨 Testing Custom Content Generation (dev_vision.md Priority 2)")
        
        test_cases = [
            {
                "type": "character",
                "prompt": "Create a crystal-being monk from the Elemental Plane of Earth who fights using martial arts enhanced by crystalline powers",
                "expected_custom": ["species", "abilities"]
            },
            {
                "type": "spell",
                "prompt": "Create a spell called Crystal Shard Barrage that launches multiple crystal projectiles",
                "expected_custom": ["spell"]
            },
            {
                "type": "weapon",
                "prompt": "Create a weapon called Voidsteel Katana that can phase through armor",
                "expected_custom": ["weapon"]
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                logger.info(f"Testing custom {test_case['type']}")
                
                endpoint = f"/create/{test_case['type']}"
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={"prompt": test_case["prompt"]},
                    timeout=60
                )
                
                if response.status_code == 200:
                    content_data = response.json()
                    
                    # Check for custom content indicators
                    content_str = json.dumps(content_data).lower()
                    if any(custom_type in content_str for custom_type in ["custom", "unique", "special"]):
                        logger.info(f"✅ Custom {test_case['type']} generated successfully")
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ {test_case['type']} may not be custom")
                        success_count += 0.5  # Partial credit
                else:
                    logger.error(f"❌ Custom {test_case['type']} creation failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Custom content test failed for {test_case['type']}: {e}")
        
        self._record_test("custom_content", success_count >= len(test_cases) * 0.7)
    
    async def test_refinement_system(self):
        """Test iterative refinement system."""
        logger.info("🔄 Testing Refinement System (dev_vision.md Priority 3)")
        
        try:
            # First, create a character to refine
            response = requests.post(
                f"{self.base_url}/create/character",
                json={
                    "prompt": "Create a human rogue",
                    "preferences": {"level": 1}
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error("❌ Failed to create base character for refinement")
                self._record_test("refinement_system", False)
                return
            
            character_data = response.json()
            
            # Test refinement
            refinement_response = requests.post(
                f"{self.base_url}/refine/character",
                json={
                    "character_data": character_data,
                    "refinement_prompt": "Make this rogue more stealthy and add expertise in Stealth and Sleight of Hand"
                },
                timeout=60
            )
            
            if refinement_response.status_code == 200:
                refined_data = refinement_response.json()
                logger.info("✅ Character refinement successful")
                
                # Test level up with journal
                journal_response = requests.post(
                    f"{self.base_url}/levelup/character",
                    json={
                        "character_data": refined_data,
                        "new_level": 2,
                        "journal_entries": [
                            "Successfully infiltrated the thieves' guild",
                            "Learned advanced lockpicking techniques"
                        ]
                    },
                    timeout=60
                )
                
                if journal_response.status_code == 200:
                    logger.info("✅ Journal-based level up successful")
                    self._record_test("refinement_system", True)
                else:
                    logger.error("❌ Journal-based level up failed")
                    self._record_test("refinement_system", False)
            else:
                logger.error("❌ Character refinement failed")
                self._record_test("refinement_system", False)
                
        except Exception as e:
            logger.error(f"Refinement system test failed: {e}")
            self._record_test("refinement_system", False)
    
    async def test_advancement_system(self):
        """Test character advancement features."""
        logger.info("⬆️ Testing Advancement System (dev_vision.md Priority 4)")
        
        try:
            # Create a character at level 3
            response = requests.post(
                f"{self.base_url}/create/character",
                json={
                    "prompt": "Create a dwarf cleric of the forge domain",
                    "preferences": {"level": 3}
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error("❌ Failed to create character for advancement")
                self._record_test("advancement_system", False)
                return
            
            character_data = response.json()
            
            # Test level advancement to 4 (ASI/Feat level)
            advancement_response = requests.post(
                f"{self.base_url}/advance/character",
                json={
                    "character_data": character_data,
                    "new_level": 4,
                    "advancement_choices": {
                        "feat_or_asi": "feat",
                        "selected_feat": "War Caster"
                    }
                },
                timeout=60
            )
            
            if advancement_response.status_code == 200:
                advanced_data = advancement_response.json()
                
                # Verify advancement was applied
                if advanced_data.get("level") == 4:
                    logger.info("✅ Character advancement successful")
                    self._record_test("advancement_system", True)
                else:
                    logger.error("❌ Character advancement data incorrect")
                    self._record_test("advancement_system", False)
            else:
                logger.error("❌ Character advancement failed")
                self._record_test("advancement_system", False)
                
        except Exception as e:
            logger.error(f"Advancement system test failed: {e}")
            self._record_test("advancement_system", False)
    
    async def test_npc_creation(self):
        """Test NPC and creature creation."""
        logger.info("👥 Testing NPC Creation (dev_vision.md Priority 5)")
        
        npc_tests = [
            {
                "type": "npc",
                "prompt": "Create a gruff tavern keeper with secrets",
                "expected_fields": ["name", "role", "personality", "secrets"]
            },
            {
                "type": "creature",
                "prompt": "Create a forest guardian spirit",
                "expected_fields": ["name", "type", "challenge_rating", "abilities"]
            }
        ]
        
        success_count = 0
        
        for test in npc_tests:
            try:
                response = requests.post(
                    f"{self.base_url}/create/{test['type']}",
                    json={"prompt": test["prompt"]},
                    timeout=60
                )
                
                if response.status_code == 200:
                    npc_data = response.json()
                    
                    # Check for expected fields
                    if any(field in str(npc_data).lower() for field in test["expected_fields"]):
                        logger.info(f"✅ {test['type']} creation successful")
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ {test['type']} missing some expected fields")
                        success_count += 0.5
                else:
                    logger.error(f"❌ {test['type']} creation failed")
                    
            except Exception as e:
                logger.error(f"NPC creation test failed for {test['type']}: {e}")
        
        self._record_test("npc_creation", success_count >= len(npc_tests) * 0.7)
    
    async def test_performance(self):
        """Test system performance and reliability."""
        logger.info("⚡ Testing Performance and Reliability")
        
        try:
            # Test response times
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/create/character",
                json={
                    "prompt": "Create a simple human fighter",
                    "preferences": {"level": 1}
                },
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 30:  # dev_vision.md requirement
                logger.info(f"✅ Performance test passed ({response_time:.2f}s)")
                self._record_test("performance", True)
            else:
                logger.error(f"❌ Performance test failed ({response_time:.2f}s)")
                self._record_test("performance", False)
                
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            self._record_test("performance", False)
    
    def _record_test(self, test_name: str, passed: bool):
        """Record test result."""
        self.test_results[test_name] = passed
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
        else:
            self.test_results["failed_tests"] += 1
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("📊 Generating Test Report")
        
        print("\n" + "="*80)
        print("🎯 D&D CHARACTER CREATOR - PODMAN DEPLOYMENT TEST REPORT")
        print("="*80)
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS (per dev_vision.md priorities):")
        test_details = {
            "container_deployment": "📦 Container Deployment",
            "api_health": "🏥 API Health & Connectivity", 
            "character_creation": "🧙 Character Creation (Priority 1)",
            "custom_content": "🎨 Custom Content Generation (Priority 2)",
            "refinement_system": "🔄 Refinement System (Priority 3)",
            "advancement_system": "⬆️ Advancement System (Priority 4)",
            "npc_creation": "👥 NPC Creation (Priority 5)",
            "performance": "⚡ Performance & Reliability"
        }
        
        for test_key, test_desc in test_details.items():
            status = "✅ PASS" if self.test_results[test_key] else "❌ FAIL"
            print(f"{test_desc}: {status}")
        
        print(f"\n🎯 COMPLIANCE WITH dev_vision.md:")
        core_features = [
            "character_creation", "custom_content", "refinement_system", 
            "advancement_system", "npc_creation"
        ]
        
        core_passed = sum(1 for feature in core_features if self.test_results[feature])
        core_compliance = (core_passed / len(core_features)) * 100
        
        print(f"Core Feature Compliance: {core_compliance:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 DEPLOYMENT READY - System meets dev_vision.md requirements!")
        elif success_rate >= 60:
            print("\n⚠️ NEEDS IMPROVEMENT - Some features require attention")
        else:
            print("\n❌ NOT READY - Major issues need resolution")
        
        print("="*80)
    
    async def cleanup_container(self):
        """Clean up Podman container."""
        if self.container_id:
            logger.info("🧹 Cleaning up container")
            try:
                subprocess.run(["podman", "stop", self.container_name], check=False)
                subprocess.run(["podman", "rm", self.container_name], check=False)
                logger.info("✅ Container cleanup completed")
            except Exception as e:
                logger.warning(f"⚠️ Container cleanup failed: {e}")


async def main():
    """Run the comprehensive Podman deployment test."""
    test_suite = PodmanDeploymentTest()
    await test_suite.run_full_test_suite()


if __name__ == "__main__":
    asyncio.run(main())
