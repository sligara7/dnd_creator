#!/usr/bin/env python3
"""
Service Generator Script

This script generates a new service with the standard structure defined in
SERVICE_TEMPLATE.md.

Usage:
    python generate_service.py service_name [options]

Example:
    python generate_service.py character-service --port 8000 --database postgresql
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional

def create_directory_structure(service_name: str, base_dir: Path) -> None:
    """Create the service directory structure."""
    service_dir = base_dir / service_name
    
    # Create main directories
    directories = [
        "src",
        f"src/{service_name}",
        f"src/{service_name}/api",
        f"src/{service_name}/api/v1",
        f"src/{service_name}/core",
        f"src/{service_name}/db",
        f"src/{service_name}/db/repositories",
        f"src/{service_name}/db/migrations",
        f"src/{service_name}/utils",
        f"src/{service_name}/workers",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "deployment",
        "deployment/k8s",
        "deployment/monitoring",
    ]
    
    for directory in directories:
        (service_dir / directory).mkdir(parents=True, exist_ok=True)
        (service_dir / directory / "__init__.py").touch()

def create_pixi_toml(
    service_name: str,
    service_dir: Path,
    port: int,
    database: Optional[str] = None,
    use_redis: bool = False,
    use_celery: bool = False
) -> None:
    """Create the pixi.toml file."""
    content = f"""[project]
name = "{service_name}"
version = "0.1.0"
description = "Service for D&D Character Creator"
authors = ["Your Name <your.email@example.com>"]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "win-64"]

[tasks]
start = "uvicorn {service_name}.main:app --host 0.0.0.0 --port {port} --reload"
test = "pytest tests/ --cov={service_name} --cov-report=term-missing --cov-report=xml -v"
format = {{ cmd = ["black", ".", "isort", "."] }}
lint = {{ cmd = ["ruff", "check", ".", "black", "--check", ".", "isort", "--check-only", "."] }}
type-check = "mypy ."
migrate = {{ cmd = ["alembic", "upgrade", "head"] }}
create-migration = {{ cmd = ["alembic", "revision", "--autogenerate", "-m"] }}
shell = "ipython"

[dependencies]
python = "==3.11"
fastapi = "*"
uvicorn = "*"
pydantic = "*"
pydantic-settings = "*"
python-json-logger = "*"
prometheus-client = "*"

# Database dependencies
{f'sqlmodel = "*"' if database == 'postgresql' else ''}
{f'asyncpg = "*"' if database == 'postgresql' else ''}
{f'alembic = "*"' if database == 'postgresql' else ''}

# Redis dependencies
{f'aioredis = "*"' if use_redis else ''}
{f'redis = "*"' if use_redis else ''}

# Celery dependencies
{f'celery = "*"' if use_celery else ''}

[dev-dependencies]
pytest = "*"
pytest-cov = "*"
pytest-asyncio = "*"
black = "*"
isort = "*"
ruff = "*"
mypy = "*"
ipython = "*"
httpx = "*"
factory-boy = "*"

[feature.dev]
dependencies = [
    "pytest",
    "pytest-cov",
    "pytest-asyncio",
    "black",
    "isort",
    "ruff",
    "mypy",
    "ipython",
    "httpx",
    "factory-boy"
]

[feature.prod]
dependencies = [
    "gunicorn",
    "uvicorn[standard]"
]

[environments]
default = "dev"

[environments.dev]
features = ["dev"]

[environments.prod]
features = ["prod"]
"""
    
    with open(service_dir / "pixi.toml", "w") as f:
        f.write(content)

def create_dockerfile(service_name: str, service_dir: Path) -> None:
    """Create the Dockerfile."""
    content = f"""# Use a multi-stage build
FROM python:3.11-slim as builder

# Install Pixi
RUN curl -fsSL https://pixi.sh/install.sh | bash

# Copy configuration files
COPY pixi.toml ./

# Install dependencies
RUN pixi install

# Final stage
FROM python:3.11-slim

# Copy Pixi environment
COPY --from=builder /root/.pixi ./root/.pixi

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Start the application
CMD ["pixi", "run", "start"]
"""
    
    with open(service_dir / "Dockerfile", "w") as f:
        f.write(content)

def create_docker_compose(service_name: str, service_dir: Path, port: int) -> None:
    """Create the docker-compose.yml file."""
    content = f"""version: '3.8'

services:
  {service_name}:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{service_name}
      - MESSAGE_HUB_URL=http://message-hub:8200
      - AUTH_SERVICE_URL=http://auth-service:8300
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    networks:
      - dnd_network

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={service_name}
    volumes:
      - {service_name}_data:/var/lib/postgresql/data
    networks:
      - dnd_network

  redis:
    image: redis:7
    networks:
      - dnd_network

volumes:
  {service_name}_data:

networks:
  dnd_network:
    external: true
"""
    
    with open(service_dir / "deployment" / "docker-compose.yml", "w") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Generate a new service.")
    parser.add_argument("service_name", help="Name of the service")
    parser.add_argument("--port", type=int, help="Service port", required=True)
    parser.add_argument("--database", choices=["postgresql", "none"], default="postgresql")
    parser.add_argument("--redis", action="store_true", help="Use Redis")
    parser.add_argument("--celery", action="store_true", help="Use Celery")
    
    args = parser.parse_args()
    
    base_dir = Path("services")
    service_dir = base_dir / args.service_name
    
    # Create directory structure
    create_directory_structure(args.service_name, base_dir)
    
    # Create configuration files
    create_pixi_toml(args.service_name, service_dir, args.port, args.database, args.redis, args.celery)
    create_dockerfile(args.service_name, service_dir)
    create_docker_compose(args.service_name, service_dir, args.port)
    
    print(f"Service {args.service_name} created successfully!")

if __name__ == "__main__":
    main()
