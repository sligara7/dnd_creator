.PHONY: install format lint test coverage migrate run

install:
	poetry install

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run ruff check .
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check-only .

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml

migrate:
	poetry run alembic upgrade head

run:
	poetry run uvicorn src.{{ cookiecutter.__project_slug }}.main:app --reload

shell:
	poetry run ipython

docker-build:
	docker build -t {{ cookiecutter.__project_slug }} .

docker-run:
	docker run -p 8000:8000 {{ cookiecutter.__project_slug }}

docker-compose:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
