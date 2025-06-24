#!/bin/bash

# D&D Character Creator API Testing Script Hub
# Usage: ./test_api_endpoints.sh [BASE_URL] [TEST_TYPE]
# TEST_TYPE: quick (default), full, or original

BASE_URL=${1:-"http://localhost:8000"}
TEST_TYPE=${2:-"quick"}

echo "🧪 D&D Character Creator API Testing Hub"
echo "========================================"
echo "Available test suites:"
echo "  quick - Fast core functionality tests (7 tests, ~5 seconds)"
echo "  full  - Comprehensive all-endpoint tests (35 tests, ~30 seconds)"
echo ""

case "$TEST_TYPE" in
    "quick")
        echo "Running QUICK test suite..."
        ./test_api_quick.sh "$BASE_URL"
        ;;
    "full")
        echo "Running COMPREHENSIVE test suite..."
        ./test_api_endpoints_refactored.sh "$BASE_URL"
        ;;
    *)
        echo "Invalid test type: $TEST_TYPE"
        echo "Usage: $0 [BASE_URL] [quick|full]"
        echo ""
        echo "Examples:"
        echo "  $0                              # Quick tests on localhost:8000"
        echo "  $0 http://localhost:8001 quick  # Quick tests on port 8001"
        echo "  $0 http://localhost:8000 full   # Full comprehensive tests"
        exit 1
        ;;
esac
