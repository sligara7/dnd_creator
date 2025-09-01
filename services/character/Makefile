.PHONY: install format lint test coverage migrate clean build docs

# Development Setup
install:
	poetry install

# Code Quality
format:
	poetry run black .
	poetry run isort .

lint:
	poetry run ruff check .
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check-only .

# Testing
test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml

test-watch:
	poetry run pytest-watch -- --cov=src --cov-report=term-missing

# Database
migrate:
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "$(message)"

migrate-down:
	poetry run alembic downgrade -1

migrate-reset:
	poetry run alembic downgrade base
	poetry run alembic upgrade head

# Development Server
run:
	poetry run uvicorn character_service.main:app --reload

shell:
	poetry run ipython

clean:
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Docker
docker-build:
	docker build -t character-service .

docker-run:
	docker run -p 8000:8000 character-service

docker-compose:
	docker-compose up -d

# Documentation
docs:
	poetry run pdoc --html --output-dir docs src/character_service

# Help
help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make format        Format code"
	@echo "  make lint          Lint code"
	@echo "  make test          Run tests"
	@echo "  make coverage      Run tests with coverage"
	@echo "  make migrate       Run database migrations"
	@echo "  make run           Start development server"
	@echo "  make shell         Start IPython shell"
	@echo "  make clean         Clean build artifacts"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docs          Generate documentation"
