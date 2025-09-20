#!/bin/bash

# Remove SQLAlchemy model files
rm -f \
    src/auth_service/models/base.py \
    src/auth_service/models/user.py \
    src/auth_service/models/role.py \
    src/auth_service/models/session.py \
    src/auth_service/models/api_key.py \
    src/auth_service/models/audit.py

# Remove SQLAlchemy database configuration
rm -f src/auth_service/core/database.py

# Remove alembic migration files and configuration
rm -rf alembic/
rm -f alembic.ini

# Remove any remaining SQLAlchemy files from repositories
rm -f \
    src/auth_service/repositories/base.py \
    src/auth_service/repositories/user.py \
    src/auth_service/repositories/role.py \
    src/auth_service/repositories/session.py \
    src/auth_service/repositories/api_key.py \
    src/auth_service/repositories/audit.py

# Remove database configuration from settings
rm -f src/auth_service/core/settings/database.py

# Clean up cache and temporary files
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -r {} +

# Update code to use only Pydantic models and storage client
find src/auth_service -type f -name "*.py" -exec sed -i \
    -e 's/from sqlalchemy.*//g' \
    -e 's/import sqlalchemy.*//g' \
    -e 's/from alembic.*//g' \
    -e 's/import alembic.*//g' \
    {} +

echo "SQLAlchemy cleanup completed"