#!/bin/bash

# Fix backend imports in all Python files
cd /home/ajs7/dnd_tools/dnd_char_creator/backend

# Replace "from backend." with "from "
find . -name "*.py" -exec sed -i 's/from backend\./from /g' {} \;

echo "All backend imports fixed"
