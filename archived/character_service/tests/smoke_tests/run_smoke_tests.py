"""
Smoke Test Runner

This script runs basic smoke tests against the character service to verify
that core functionality is working as expected.
"""

import os
import sys
import pytest
import logging
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_smoke_tests(test_path: str) -> bool:
    """Run smoke tests in the specified path."""
    logger.info(f"Running smoke tests from {test_path}")
    
    # Set up test arguments
    test_args = [
        test_path,
        "-v",  # Verbose output
        "--tb=short",  # Shorter tracebacks
        "-m", "not slow"  # Skip slow tests
    ]
    
    try:
        # Run tests
        result = pytest.main(test_args)
        success = result == 0
        
        if success:
            logger.info("All smoke tests passed!")
        else:
            logger.error("Some smoke tests failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Error running smoke tests: {e}")
        return False

if __name__ == "__main__":
    # Get the directory this script is in
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the smoke tests
    success = run_smoke_tests(current_dir)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
