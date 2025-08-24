#!/bin/bash
character_id="test-id-123"
new_theme="cyberpunk"

retheme_request=$(cat <<JSONEOF
{
    "creation_type": "character",
    "character_id": "$character_id",
    "evolution_prompt": "Transform this character into cyberpunk",
    "theme": "$new_theme",
    "preserve_backstory": true,
    "save_to_database": true
}
JSONEOF
)

echo "JSON to be sent:"
echo "$retheme_request"
echo ""
echo "Character at position 55-60:"
echo "$retheme_request" | cut -c55-60
echo ""

# Test JSON validity
echo "$retheme_request" | jq . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "JSON is valid"
else
    echo "JSON is invalid"
fi
