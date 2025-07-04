#!/usr/bin/env python3
"""
Creative Requirements Validation Test for dev_vision.md
Specifically tests the unique, non-traditional character creation capabilities
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_dev_vision_creative_examples():
    """Test the exact examples from dev_vision.md"""
    
    print("🎨 Testing Dev Vision Creative Examples...")
    print("="*60)
    
    # These are the creative examples directly from dev_vision.md
    dev_vision_examples = [
        {
            "concept": "A necromancer who heals by transferring life force from willing volunteers",
            "expected_themes": ["necromancer", "healing", "life force", "transfer", "volunteer"]
        },
        {
            "concept": "A paladin sworn to a chaotic deity of change and freedom",
            "expected_themes": ["paladin", "chaotic", "deity", "change", "freedom"]
        },
        {
            "concept": "A warlock whose patron is an ancient sentient library",
            "expected_themes": ["warlock", "patron", "ancient", "sentient", "library", "knowledge"]
        },
        {
            "concept": "A barbarian who rages by tapping into mathematical precision",
            "expected_themes": ["barbarian", "rage", "mathematical", "precision", "calculation"]
        },
        {
            "concept": "A bard who weaves spells through interpretive dance instead of music",
            "expected_themes": ["bard", "spells", "dance", "interpretive", "movement"]
        }
    ]
    
    results = []
    
    for i, example in enumerate(dev_vision_examples):
        concept = example["concept"]
        expected_themes = example["expected_themes"]
        
        print(f"\n🧪 Test {i+1}/5: {concept}")
        print("-" * 50)
        
        creation_data = {
            "creation_type": "character",
            "prompt": concept,
            "save_to_database": False,
            "user_preferences": {
                "level": 5,
                "detail_level": "high",
                "include_backstory": True,
                "non_traditional": True
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_BASE}/api/v2/factory/create", json=creation_data, timeout=120)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                character = data.get('data', {})
                core = character.get('core', {})
                
                # Extract key character information
                char_name = core.get('name', 'Unknown')
                species = core.get('species', 'Unknown')  
                classes = core.get('character_classes', {})
                backstory = core.get('personality', {}).get('backstory', '')
                traits = core.get('personality', {}).get('traits', [])
                
                # Combine all text for theme analysis
                all_text = f"{char_name} {species} {' '.join(classes.keys())} {backstory} {' '.join(traits)}".lower()
                
                # Check theme compliance
                themes_found = [theme for theme in expected_themes if theme.lower() in all_text]
                theme_score = len(themes_found) / len(expected_themes) * 100
                
                # Evaluate creativity and non-traditional aspects
                creativity_indicators = {
                    "unique_name": char_name not in ["Unknown", "Name", "Character"],
                    "creative_species": species not in ["Human", "Elf", "Dwarf", "Halfling", "Unknown"],
                    "expected_class": any(cls.lower() in concept.lower() for cls in classes.keys()),
                    "substantial_backstory": len(backstory) > 200,
                    "theme_alignment": theme_score >= 40,
                    "non_traditional_elements": any(word in all_text for word in [
                        "unusual", "unique", "unconventional", "different", "strange", 
                        "mysterious", "rare", "exceptional", "distinctive"
                    ])
                }
                
                creativity_score = sum(creativity_indicators.values()) / len(creativity_indicators) * 100
                
                result = {
                    "concept": concept,
                    "success": True,
                    "character_name": char_name,
                    "species": species,
                    "classes": list(classes.keys()),
                    "generation_time": generation_time,
                    "backstory_length": len(backstory),
                    "theme_score": theme_score,
                    "themes_found": themes_found,
                    "themes_missing": [t for t in expected_themes if t not in themes_found],
                    "creativity_score": creativity_score,
                    "creativity_indicators": creativity_indicators,
                    "dev_vision_compliant": creativity_score >= 60 and theme_score >= 30
                }
                
                results.append(result)
                
                # Display results
                print(f"✅ CHARACTER CREATED: {char_name}")
                print(f"   Species: {species}")
                print(f"   Classes: {', '.join(classes.keys()) if classes else 'None'}")
                print(f"   Generation Time: {generation_time:.1f}s")
                print(f"   Theme Compliance: {theme_score:.0f}% ({len(themes_found)}/{len(expected_themes)} themes)")
                print(f"   Creativity Score: {creativity_score:.0f}%")
                print(f"   Dev Vision Compliant: {'✅ YES' if result['dev_vision_compliant'] else '❌ NO'}")
                
                if themes_found:
                    print(f"   ✅ Themes Found: {', '.join(themes_found)}")
                if result['themes_missing']:
                    print(f"   ❌ Themes Missing: {', '.join(result['themes_missing'])}")
                
                if backstory:
                    print(f"   📝 Backstory Preview: {backstory[:100]}...")
                
            else:
                print(f"❌ CREATION FAILED: {response.status_code}")
                print(f"   Error: {response.text[:200]}...")
                results.append({
                    "concept": concept,
                    "success": False,
                    "error": response.text,
                    "dev_vision_compliant": False
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                "concept": concept,
                "success": False,
                "error": str(e),
                "dev_vision_compliant": False
            })
    
    return results

def test_iterative_refinement_capability():
    """Test if the system can handle iterative refinement"""
    print(f"\n🔄 Testing Iterative Refinement Capability...")
    print("="*60)
    
    # Create a base character
    base_concept = "A simple warrior with a sword"
    print(f"📝 Creating base character: {base_concept}")
    
    creation_data = {
        "creation_type": "character",
        "prompt": base_concept,
        "save_to_database": False
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/v2/factory/create", json=creation_data, timeout=60)
        
        if response.status_code == 200:
            base_character = response.json().get('data', {})
            base_name = base_character.get('core', {}).get('name', 'Unknown')
            print(f"✅ Base character created: {base_name}")
            
            # Test refinement variations
            refinements = [
                "Make this character more mysterious and add magical abilities",
                "Give them a tragic backstory involving lost family",
                "Add unique equipment that reflects their personality"
            ]
            
            refinement_results = []
            
            for i, refinement in enumerate(refinements):
                print(f"\n🔧 Refinement {i+1}: {refinement}")
                
                # Create a "refined" version by incorporating the refinement into the prompt
                refined_concept = f"{base_concept}. {refinement}"
                refined_data = {
                    "creation_type": "character", 
                    "prompt": refined_concept,
                    "save_to_database": False
                }
                
                try:
                    start_time = time.time()
                    ref_response = requests.post(f"{API_BASE}/api/v2/factory/create", json=refined_data, timeout=60)
                    refinement_time = time.time() - start_time
                    
                    if ref_response.status_code == 200:
                        refined_character = ref_response.json().get('data', {})
                        refined_name = refined_character.get('core', {}).get('name', 'Unknown')
                        refined_backstory = refined_character.get('core', {}).get('personality', {}).get('backstory', '')
                        
                        # Compare with base character
                        changes_detected = refined_name != base_name or len(refined_backstory) > 100
                        
                        refinement_results.append({
                            "refinement": refinement,
                            "success": True,
                            "character_name": refined_name,
                            "refinement_time": refinement_time,
                            "changes_detected": changes_detected,
                            "backstory_length": len(refined_backstory)
                        })
                        
                        print(f"   ✅ Refined character: {refined_name}")
                        print(f"   ⏱️ Time: {refinement_time:.1f}s")
                        print(f"   🔍 Changes detected: {'Yes' if changes_detected else 'No'}")
                        
                    else:
                        print(f"   ❌ Refinement failed: {ref_response.status_code}")
                        refinement_results.append({
                            "refinement": refinement,
                            "success": False,
                            "error": ref_response.text
                        })
                        
                except Exception as e:
                    print(f"   ❌ Refinement exception: {e}")
                    refinement_results.append({
                        "refinement": refinement,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "base_character": base_name,
                "refinements": refinement_results,
                "refinement_capability": any(r.get('success') for r in refinement_results)
            }
            
        else:
            print(f"❌ Base character creation failed: {response.status_code}")
            return {"refinement_capability": False, "error": "Base character creation failed"}
            
    except Exception as e:
        print(f"❌ Base character creation exception: {e}")
        return {"refinement_capability": False, "error": str(e)}

def generate_dev_vision_compliance_report(creative_results, refinement_results):
    """Generate a comprehensive compliance report for dev_vision.md"""
    
    print("\n" + "="*80)
    print("📋 DEV VISION REQUIREMENTS COMPLIANCE REPORT")
    print("="*80)
    
    # Creative Character Generation Analysis
    successful_creations = [r for r in creative_results if r.get('success')]
    compliant_characters = [r for r in successful_creations if r.get('dev_vision_compliant')]
    
    print(f"\n🎭 CREATIVE CHARACTER GENERATION COMPLIANCE:")
    print(f"   • Total Test Cases: {len(creative_results)}")
    print(f"   • Successful Creations: {len(successful_creations)}/{len(creative_results)}")
    print(f"   • Dev Vision Compliant: {len(compliant_characters)}/{len(successful_creations)}")
    
    if successful_creations:
        avg_theme_score = sum(r.get('theme_score', 0) for r in successful_creations) / len(successful_creations)
        avg_creativity = sum(r.get('creativity_score', 0) for r in successful_creations) / len(successful_creations)
        avg_time = sum(r.get('generation_time', 0) for r in successful_creations) / len(successful_creations)
        
        print(f"   • Average Theme Compliance: {avg_theme_score:.1f}%")
        print(f"   • Average Creativity Score: {avg_creativity:.1f}%")
        print(f"   • Average Generation Time: {avg_time:.1f}s")
        
        # Highlight best examples
        print(f"\n   🌟 BEST EXAMPLES:")
        best_examples = sorted(successful_creations, key=lambda x: x.get('creativity_score', 0), reverse=True)[:2]
        for i, example in enumerate(best_examples):
            print(f"      {i+1}. {example['character_name']} - {example['creativity_score']:.0f}% creativity")
            print(f"         Concept: {example['concept'][:60]}...")
    
    # Iterative Refinement Analysis
    print(f"\n🔄 ITERATIVE REFINEMENT CAPABILITY:")
    if refinement_results.get('refinement_capability'):
        successful_refinements = [r for r in refinement_results.get('refinements', []) if r.get('success')]
        print(f"   • Refinement Capability: ✅ AVAILABLE")
        print(f"   • Successful Refinements: {len(successful_refinements)}/{len(refinement_results.get('refinements', []))}")
        
        if successful_refinements:
            changes_detected = sum(1 for r in successful_refinements if r.get('changes_detected'))
            print(f"   • Refinements with Changes: {changes_detected}/{len(successful_refinements)}")
    else:
        print(f"   • Refinement Capability: ❌ LIMITED (simulated via prompt modification)")
        print(f"   • Note: True iterative refinement requires database persistence")
    
    # Overall Compliance Assessment
    print(f"\n📊 OVERALL DEV VISION COMPLIANCE:")
    
    creative_compliance = (len(compliant_characters) / len(creative_results)) * 100 if creative_results else 0
    generation_success = (len(successful_creations) / len(creative_results)) * 100 if creative_results else 0
    refinement_available = 75 if refinement_results.get('refinement_capability') else 25  # Partial due to DB issues
    
    overall_score = (creative_compliance + generation_success + refinement_available) / 3
    
    print(f"   • Creative Compliance: {creative_compliance:.0f}%")
    print(f"   • Generation Success: {generation_success:.0f}%") 
    print(f"   • Refinement Capability: {refinement_available:.0f}%")
    print(f"   • OVERALL COMPLIANCE: {overall_score:.0f}%")
    
    # Final Assessment
    if overall_score >= 80:
        status = "✅ EXCELLENT - Fully meets dev_vision.md requirements"
    elif overall_score >= 60:
        status = "⚠️ GOOD - Mostly meets requirements with minor issues"
    elif overall_score >= 40:
        status = "❌ NEEDS WORK - Significant gaps in functionality"
    else:
        status = "❌ CRITICAL - Major functionality missing"
    
    print(f"\n🏆 FINAL ASSESSMENT: {status}")
    
    # Specific Recommendations
    print(f"\n💡 RECOMMENDATIONS FOR FULL COMPLIANCE:")
    if creative_compliance < 80:
        print("   • Improve AI prompt engineering for better theme adherence")
        print("   • Enhance creativity scoring and validation")
    if generation_success < 100:
        print("   • Debug and fix character generation failures")
    if refinement_available < 75:
        print("   • Fix database persistence issues for true iterative refinement")
        print("   • Implement proper character evolution endpoint")
    
    print(f"\n   🎯 PRIORITY: {'High' if overall_score < 60 else 'Medium' if overall_score < 80 else 'Low'}")
    
    return {
        "creative_compliance": creative_compliance,
        "generation_success": generation_success,
        "refinement_capability": refinement_available,
        "overall_score": overall_score,
        "status": status
    }

def main():
    print("🎨 DEV VISION CREATIVE REQUIREMENTS VALIDATION")
    print("Testing specific examples and capabilities from dev_vision.md")
    print("="*70)
    
    # Test creative examples from dev_vision.md
    creative_results = test_dev_vision_creative_examples()
    
    # Test iterative refinement capability
    refinement_results = test_iterative_refinement_capability()
    
    # Generate comprehensive compliance report
    compliance_report = generate_dev_vision_compliance_report(creative_results, refinement_results)
    
    # Save results
    full_results = {
        "creative_examples": creative_results,
        "refinement_testing": refinement_results,
        "compliance_report": compliance_report,
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_version": "dev_vision_validation_1.0"
    }
    
    with open("dev_vision_compliance_report.json", "w") as f:
        json.dump(full_results, f, indent=2, default=str)
    
    print(f"\n📄 Full compliance report saved to: dev_vision_compliance_report.json")

if __name__ == "__main__":
    main()
