#!/bin/bash
# Fix imports in the reorganized backend structure

echo "Fixing imports in backend files..."

# Fix imports in service files
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from backend\./from /g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from backend import/from src.core import/g' {} \;

# Fix specific module imports in services
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from enums/from src.core.enums/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from creation_factory/from src.services.creation_factory/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from creation/from src.services.creation/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from creation_validation/from src.services.creation_validation/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from character_models/from src.models.character_models/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from core_models/from src.models.core_models/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from custom_content_models/from src.models.custom_content_models/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from database_models/from src.models.database_models/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from llm_service/from src.services.llm_service/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from ability_management/from src.services.ability_management/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from generators/from src.services.generators/g' {} \;
find /home/ajs7/dnd_tools/dnd_char_creator/backend/src/services -name "*.py" -exec sed -i 's/from dnd_data/from src.services.dnd_data/g' {} \;

echo "Import fixes completed."
