#!/usr/bin/env python3
"""
Test Runner for D&D Character Creator Backend

This script runs all available tests in the backend directory,
providing a comprehensive overview of system functionality.

Usage:
    python run_all_tests.py                    # Run all tests
    python run_all_tests.py --comprehensive    # Run comprehensive test only
    python run_all_tests.py --individual       # Run individual test files only
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Available test files
TEST_FILES = [
    "test_comprehensive.py",
    "test_backend.py", 
    "test_character_setters.py",
    "test_creativity.py",
    "test_interactive.py",
    "test_llm_diagnostic.py",
    "test_llm_ollama.py",
    "test_versioning_api.py",
    "test_xp_system.py"
]

def run_python_command(command: str, description: str):
    """Run a Python command with proper environment setup."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    # Use conda environment if available
    conda_prefix = "/home/ajs7/miniconda3/bin/conda run -p /home/ajs7/miniconda3 --no-capture-output"
    python_wrapper = "/home/ajs7/.vscode/extensions/ms-python.python-2025.8.0-linux-x64/python_files/get_output_via_markers.py"
    
    full_command = f"{conda_prefix} python {python_wrapper} {command}"
    
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def run_comprehensive_test():
    """Run the comprehensive test suite."""
    return run_python_command(
        "test_comprehensive.py",
        "Running Comprehensive Backend Test Suite"
    )

def run_individual_tests():
    """Run individual test files."""
    results = {}
    
    for test_file in TEST_FILES:
        if test_file == "test_comprehensive.py":
            continue  # Skip comprehensive test in individual mode
            
        test_path = backend_dir / test_file
        if test_path.exists():
            print(f"\n📋 Running {test_file}...")
            success = run_python_command(
                test_file,
                f"Running {test_file}"
            )
            results[test_file] = success
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False
            
    return results

def print_summary(comprehensive_result=None, individual_results=None):
    """Print test summary."""
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    if comprehensive_result is not None:
        status = "✅ PASSED" if comprehensive_result else "❌ FAILED"
        print(f"Comprehensive Test Suite: {status}")
        
    if individual_results:
        passed = sum(1 for result in individual_results.values() if result)
        total = len(individual_results)
        print(f"\nIndividual Tests: {passed}/{total} passed")
        
        for test_file, success in individual_results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {test_file}")
            
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
    print(f"{'='*60}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run D&D Character Creator Backend Tests"
    )
    parser.add_argument(
        "--comprehensive", 
        action="store_true",
        help="Run only the comprehensive test suite"
    )
    parser.add_argument(
        "--individual",
        action="store_true", 
        help="Run only individual test files"
    )
    
    args = parser.parse_args()
    
    print("🧪 D&D Character Creator Backend Test Runner")
    print("=" * 60)
    
    comprehensive_result = None
    individual_results = None
    
    if args.comprehensive:
        comprehensive_result = run_comprehensive_test()
    elif args.individual:
        individual_results = run_individual_tests()
    else:
        # Run both by default
        comprehensive_result = run_comprehensive_test()
        individual_results = run_individual_tests()
        
    print_summary(comprehensive_result, individual_results)

if __name__ == "__main__":
    main()
