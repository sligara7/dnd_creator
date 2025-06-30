#!/bin/bash

# Quick test of just the v1 generation endpoints that were failing
BASE_URL=${1:-"http://localhost:8000"}

echo "Testing v1 Generation Endpoints Fix"
echo "====================================="

# Test Generate Content (v1)
echo "Testing Generate Content (v1)..."
response1=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/generate/content?content_type=character&prompt=A%20noble%20paladin%20seeking%20redemption&save_to_database=true")
status1=$(echo "$response1" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
body1=$(echo "$response1" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')

if [[ "$status1" == "200" ]]; then
    echo "✅ Generate Content (v1): PASS"
else
    echo "❌ Generate Content (v1): FAIL (Status: $status1)"
    echo "   Response: ${body1:0:200}..."
fi

# Test Generate Character Complete (v1)
echo "Testing Generate Character Complete (v1)..."
response2=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/generate/character-complete?prompt=A%20mysterious%20wizard%20from%20distant%20lands&level=2&include_equipment=true&include_backstory=true")
status2=$(echo "$response2" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
body2=$(echo "$response2" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')

if [[ "$status2" == "200" ]]; then
    echo "✅ Generate Character Complete (v1): PASS"
else
    echo "❌ Generate Character Complete (v1): FAIL (Status: $status2)"
    echo "   Response: ${body2:0:200}..."
fi

echo ""
echo "Summary:"
if [[ "$status1" == "200" && "$status2" == "200" ]]; then
    echo "🎉 Both v1 generation endpoints are working correctly!"
    exit 0
else
    echo "❌ Some endpoints still have issues."
    exit 1
fi
