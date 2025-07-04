#!/usr/bin/env python3
"""
Comprehensive Test Script for dev_vision.md Creative Requirements
Tests all D&D character creation requirements including:
- AI-driven character generation with unique concepts
- Iterative refinement capabilities
- Custom content creation (weapons, armor, spells)
- Character validation and sheet generation
- Advanced catalog and equipment management
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

API_BASE = "http://localhost:8000"

class DevVisionTester:
    def __init__(self):
        self.test_results = []
        self.character_ids = []
        self.verbose = True
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API Health Check: {data['message']}")
                return True
            else:
                self.log(f"❌ API Health Check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ API Connection failed: {e}", "ERROR")
            return False

    def test_creative_character_generation(self) -> Dict[str, Any]:
        """Test Requirement 1: AI-Driven Creative Character Generation"""
        self.log("🎭 Testing Creative Character Generation...")
        
        # Test multiple unique and creative character concepts
        creative_concepts = [
            "A crystal-powered artificer from a steampunk sky city who builds mechanical familiars powered by trapped storm clouds",
            "A time-traveling druid who speaks with extinct creatures and can summon prehistoric beasts from temporal echoes",
            "A shadow dancer who weaves darkness into magical weapons and can step between the material and shadow plane",
            "A dragon-touched healer with scales that change color with emotions and breathes healing mist instead of fire",
            "A void monk who fights by temporarily erasing parts of reality and can phase through attacks"
        ]
        
        results = {}
        
        for i, concept in enumerate(creative_concepts):
            self.log(f"  Testing concept {i+1}/5: {concept[:50]}...")
            
            try:
                # Create character using the factory endpoint
                creation_data = {
                    "creation_type": "character",
                    "prompt": concept,
                    "save_to_database": True,
                    "user_preferences": {
                        "level": 3,
                        "detail_level": "high",
                        "verbose_generation": True
                    }
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE}/api/v2/factory/create", 
                    json=creation_data,
                    timeout=300  # 5 minutes for complex generation
                )
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    character_id = data.get('object_id')
                    character_data = data.get('data', {})
                    
                    if character_id:
                        self.character_ids.append(character_id)
                        
                    results[f"concept_{i+1}"] = {
                        "success": True,
                        "character_id": character_id,
                        "generation_time": generation_time,
                        "character_name": character_data.get('core', {}).get('name', 'Unknown'),
                        "species": character_data.get('core', {}).get('species', 'Unknown'),
                        "classes": character_data.get('core', {}).get('classes', {}),
                        "backstory_length": len(character_data.get('core', {}).get('backstory', '')),
                        "has_custom_content": bool(character_data.get('equipment')) or bool(character_data.get('spells')),
                        "verbose_logs": len(data.get('verbose_logs', [])) if data.get('verbose_logs') else 0
                    }
                    
                    self.log(f"    ✅ Created: {results[f'concept_{i+1}']['character_name']} ({generation_time:.1f}s)")
                    
                else:
                    self.log(f"    ❌ Creation failed: {response.status_code} - {response.text}", "ERROR")
                    results[f"concept_{i+1}"] = {"success": False, "error": response.text}
                    
            except Exception as e:
                self.log(f"    ❌ Exception during creation: {e}", "ERROR")
                results[f"concept_{i+1}"] = {"success": False, "error": str(e)}
                
        return results

    def test_iterative_refinement(self) -> Dict[str, Any]:
        """Test Requirement 2: Iterative Character Refinement"""
        if not self.character_ids:
            self.log("❌ No characters available for refinement testing", "ERROR")
            return {"success": False, "error": "No characters available"}
            
        self.log("🔄 Testing Iterative Character Refinement...")
        
        # Use the first successfully created character
        character_id = self.character_ids[0]
        self.log(f"  Using character ID: {character_id}")
        
        # Test multiple refinement iterations
        refinement_prompts = [
            "Make the backstory more detailed and add specific names of places and people",
            "Change the personality to be more mysterious and brooding, with a dark secret",
            "Add unique custom equipment that reflects the character's magical abilities",
            "Enhance the character's magical abilities and add signature spells"
        ]
        
        results = {"character_id": character_id, "refinements": []}
        
        for i, prompt in enumerate(refinement_prompts):
            self.log(f"  Refinement {i+1}/4: {prompt[:50]}...")
            
            try:
                evolution_data = {
                    "creation_type": "character",
                    "character_id": character_id,
                    "evolution_prompt": f"Based on user feedback: '{prompt}' - Please refine the character accordingly while maintaining the core concept.",
                    "preserve_backstory": False,
                    "user_preferences": {
                        "detail_level": "high"
                    }
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE}/api/v2/factory/evolve",
                    json=evolution_data,
                    timeout=180  # 3 minutes for refinement
                )
                refinement_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    results["refinements"].append({
                        "iteration": i + 1,
                        "success": True,
                        "refinement_time": refinement_time,
                        "prompt": prompt,
                        "changes_detected": bool(data.get('data'))
                    })
                    self.log(f"    ✅ Refinement {i+1} completed ({refinement_time:.1f}s)")
                else:
                    self.log(f"    ❌ Refinement {i+1} failed: {response.status_code}", "ERROR")
                    results["refinements"].append({
                        "iteration": i + 1,
                        "success": False,
                        "error": response.text
                    })
                    
            except Exception as e:
                self.log(f"    ❌ Exception in refinement {i+1}: {e}", "ERROR")
                results["refinements"].append({
                    "iteration": i + 1,
                    "success": False,
                    "error": str(e)
                })
                
        results["success"] = any(r.get("success", False) for r in results["refinements"])
        return results

    def test_custom_content_creation(self) -> Dict[str, Any]:
        """Test Requirement 3: Custom Content Generation"""
        self.log("⚔️ Testing Custom Content Creation...")
        
        content_types = [
            ("weapon", "A sentient crystal sword that whispers ancient secrets and can phase through armor"),
            ("armor", "Living bark armor that regenerates and sprouts thorns when the wearer is threatened"),
            ("spell", "Temporal Echo - allows the caster to glimpse and interact with past or future versions of themselves"),
            ("item", "Bottled Storm - a vial containing a miniature thunderstorm that can be released for various effects")
        ]
        
        results = {}
        
        for content_type, description in content_types:
            self.log(f"  Creating {content_type}: {description[:50]}...")
            
            try:
                creation_data = {
                    "creation_type": content_type,
                    "prompt": description,
                    "save_to_database": True,
                    "user_preferences": {
                        "detail_level": "high",
                        "include_mechanics": True
                    }
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE}/api/v2/factory/create",
                    json=creation_data,
                    timeout=120  # 2 minutes for content creation
                )
                creation_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    object_id = data.get('object_id')
                    content_data = data.get('data', {})
                    
                    results[content_type] = {
                        "success": True,
                        "object_id": object_id,
                        "creation_time": creation_time,
                        "name": content_data.get('core', {}).get('name', 'Unknown'),
                        "has_mechanics": bool(content_data.get('mechanics')),
                        "has_lore": bool(content_data.get('core', {}).get('description')),
                        "complexity": len(str(content_data))
                    }
                    
                    self.log(f"    ✅ Created {content_type}: {results[content_type]['name']} ({creation_time:.1f}s)")
                    
                else:
                    self.log(f"    ❌ {content_type} creation failed: {response.status_code}", "ERROR")
                    results[content_type] = {"success": False, "error": response.text}
                    
            except Exception as e:
                self.log(f"    ❌ Exception creating {content_type}: {e}", "ERROR")
                results[content_type] = {"success": False, "error": str(e)}
                
        return results

    def test_character_validation_and_sheets(self) -> Dict[str, Any]:
        """Test Requirement 4: Character Validation and Sheet Generation"""
        if not self.character_ids:
            self.log("❌ No characters available for validation testing", "ERROR")
            return {"success": False, "error": "No characters available"}
            
        self.log("📋 Testing Character Validation and Sheet Generation...")
        
        character_id = self.character_ids[0]
        results = {"character_id": character_id}
        
        # Test character sheet generation
        try:
            self.log("  Testing character sheet generation...")
            response = requests.get(f"{API_BASE}/api/v1/characters/{character_id}/sheet", timeout=30)
            
            if response.status_code == 200:
                sheet_data = response.json()
                results["sheet"] = {
                    "success": True,
                    "has_core_info": bool(sheet_data.get('core')),
                    "has_stats": bool(sheet_data.get('stats')),
                    "has_combat": bool(sheet_data.get('combat')),
                    "has_equipment": bool(sheet_data.get('equipment')),
                    "has_spells": bool(sheet_data.get('spells')),
                    "sheet_completeness": len([k for k in ['core', 'stats', 'combat', 'equipment', 'spells'] if sheet_data.get(k)])
                }
                self.log("    ✅ Character sheet generated successfully")
            else:
                results["sheet"] = {"success": False, "error": response.text}
                self.log(f"    ❌ Sheet generation failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["sheet"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception in sheet generation: {e}", "ERROR")

        # Test character validation
        try:
            self.log("  Testing character validation...")
            response = requests.get(f"{API_BASE}/api/v1/characters/{character_id}/validate", timeout=30)
            
            if response.status_code == 200:
                validation_data = response.json()
                results["validation"] = {
                    "success": True,
                    "is_valid": validation_data.get('is_valid', False),
                    "error_count": len(validation_data.get('errors', [])),
                    "warning_count": len(validation_data.get('warnings', [])),
                    "errors": validation_data.get('errors', []),
                    "warnings": validation_data.get('warnings', [])
                }
                
                if validation_data.get('is_valid'):
                    self.log("    ✅ Character validation passed")
                else:
                    self.log(f"    ⚠️ Character validation found issues: {len(validation_data.get('errors', []))} errors, {len(validation_data.get('warnings', []))} warnings")
                    
            else:
                results["validation"] = {"success": False, "error": response.text}
                self.log(f"    ❌ Validation failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["validation"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception in validation: {e}", "ERROR")

        # Test character state management
        try:
            self.log("  Testing character state management...")
            response = requests.get(f"{API_BASE}/api/v1/characters/{character_id}/state", timeout=30)
            
            if response.status_code == 200:
                state_data = response.json()
                results["state"] = {
                    "success": True,
                    "has_health": bool(state_data.get('health')),
                    "has_resources": bool(state_data.get('resources')),
                    "has_conditions": bool(state_data.get('conditions')),
                    "state_completeness": len([k for k in ['health', 'resources', 'conditions'] if state_data.get(k) is not None])
                }
                self.log("    ✅ Character state retrieved successfully")
            else:
                results["state"] = {"success": False, "error": response.text}
                self.log(f"    ❌ State retrieval failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["state"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception in state retrieval: {e}", "ERROR")
            
        return results

    def test_advanced_catalog_management(self) -> Dict[str, Any]:
        """Test Requirement 5: Advanced Catalog and Equipment Management"""
        self.log("📚 Testing Advanced Catalog and Equipment Management...")
        
        results = {}
        
        # Test spell database
        try:
            self.log("  Testing spell database access...")
            response = requests.get(f"{API_BASE}/api/v1/spells", timeout=30)
            
            if response.status_code == 200:
                spells_data = response.json()
                results["spells"] = {
                    "success": True,
                    "total_spells": len(spells_data.get('spells', [])),
                    "has_search": 'search' in str(response.headers),
                    "sample_spell": spells_data.get('spells', [{}])[0].get('name', 'None') if spells_data.get('spells') else 'None'
                }
                self.log(f"    ✅ Spell database accessible: {results['spells']['total_spells']} spells")
            else:
                results["spells"] = {"success": False, "error": response.text}
                self.log(f"    ❌ Spell database access failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["spells"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception accessing spell database: {e}", "ERROR")

        # Test equipment database
        try:
            self.log("  Testing equipment database access...")
            response = requests.get(f"{API_BASE}/api/v1/equipment", timeout=30)
            
            if response.status_code == 200:
                equipment_data = response.json()
                results["equipment"] = {
                    "success": True,
                    "total_equipment": len(equipment_data.get('equipment', [])),
                    "categories": list(set([item.get('category', 'Unknown') for item in equipment_data.get('equipment', [])]))
                }
                self.log(f"    ✅ Equipment database accessible: {results['equipment']['total_equipment']} items")
            else:
                results["equipment"] = {"success": False, "error": response.text}
                self.log(f"    ❌ Equipment database access failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["equipment"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception accessing equipment database: {e}", "ERROR")

        # Test species/race catalog
        try:
            self.log("  Testing species catalog access...")
            response = requests.get(f"{API_BASE}/api/v1/species", timeout=30)
            
            if response.status_code == 200:
                species_data = response.json()
                results["species"] = {
                    "success": True,
                    "total_species": len(species_data.get('species', [])),
                    "has_custom": any('custom' in str(species).lower() for species in species_data.get('species', []))
                }
                self.log(f"    ✅ Species catalog accessible: {results['species']['total_species']} species")
            else:
                results["species"] = {"success": False, "error": response.text}
                self.log(f"    ❌ Species catalog access failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            results["species"] = {"success": False, "error": str(e)}
            self.log(f"    ❌ Exception accessing species catalog: {e}", "ERROR")
            
        return results

    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("="*80)
        report.append("D&D CHARACTER CREATOR - DEV VISION REQUIREMENTS TEST REPORT")
        report.append("="*80)
        report.append(f"Test executed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_tests = sum(len(v) if isinstance(v, dict) else 1 for v in test_results.values())
        passed_tests = 0
        
        for category, results in test_results.items():
            if isinstance(results, dict):
                if results.get('success'):
                    passed_tests += 1
                elif 'refinements' in results:
                    passed_tests += sum(1 for r in results['refinements'] if r.get('success'))
                else:
                    for key, value in results.items():
                        if isinstance(value, dict) and value.get('success'):
                            passed_tests += 1
            elif results:
                passed_tests += 1
                
        report.append(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        report.append("")
        
        # Detailed results
        for category, results in test_results.items():
            report.append(f"📋 {category.upper().replace('_', ' ')}")
            report.append("-" * 60)
            
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, dict):
                        status = "✅ PASS" if value.get('success') else "❌ FAIL"
                        report.append(f"  {key}: {status}")
                        if not value.get('success') and 'error' in value:
                            report.append(f"    Error: {value['error']}")
                    elif isinstance(value, list) and key == 'refinements':
                        for i, refinement in enumerate(value):
                            status = "✅ PASS" if refinement.get('success') else "❌ FAIL"
                            report.append(f"  Refinement {i+1}: {status}")
                    else:
                        report.append(f"  {key}: {value}")
            else:
                status = "✅ PASS" if results else "❌ FAIL"
                report.append(f"  {status}")
                
            report.append("")
            
        return "\n".join(report)

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute all dev_vision.md requirement tests"""
        self.log("🚀 Starting comprehensive dev_vision.md requirements testing...")
        
        test_results = {}
        
        # Test 1: API Health
        if not self.test_api_health():
            self.log("❌ API health check failed - aborting tests", "ERROR")
            return {"error": "API not available"}
        
        # Test 2: Creative Character Generation
        test_results["creative_character_generation"] = self.test_creative_character_generation()
        
        # Test 3: Iterative Refinement (requires characters from test 2)
        test_results["iterative_refinement"] = self.test_iterative_refinement()
        
        # Test 4: Custom Content Creation
        test_results["custom_content_creation"] = self.test_custom_content_creation()
        
        # Test 5: Character Validation and Sheets
        test_results["character_validation_sheets"] = self.test_character_validation_and_sheets()
        
        # Test 6: Advanced Catalog Management
        test_results["advanced_catalog_management"] = self.test_advanced_catalog_management()
        
        return test_results

def main():
    """Main execution function"""
    print("🎭 D&D Character Creator - Dev Vision Requirements Test")
    print("Testing all creative and technical requirements from dev_vision.md")
    print("=" * 80)
    
    tester = DevVisionTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_report(results)
        print("\n" + report)
        
        # Save detailed results
        with open("dev_vision_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: dev_vision_test_results.json")
        
        # Save report
        with open("dev_vision_test_report.txt", "w") as f:
            f.write(report)
        print(f"📄 Test report saved to: dev_vision_test_report.txt")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
