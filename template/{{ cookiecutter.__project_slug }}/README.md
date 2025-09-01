# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Development Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install Poetry:
   ```bash
   pip install poetry
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

## Running the Service

### Development
```bash
# Run with auto-reload
poetry run uvicorn src.{{ cookiecutter.__project_slug }}.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Lint
poetry run ruff check .
poetry run mypy .
```

### Production
```bash
# Run with multiple workers
poetry run uvicorn src.{{ cookiecutter.__project_slug }}.main:app --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
src/{{ cookiecutter.__project_slug }}/
├── api/          # API endpoints
├── core/         # Business logic
├── db/           # Database models and migrations
└── utils/        # Utility functions
```

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback last migration
poetry run alembic downgrade -1
```

{% if cookiecutter.use_celery == "yes" %}
## Celery Tasks

```bash
# Run Celery worker
poetry run celery -A src.{{ cookiecutter.__project_slug }}.workers.tasks worker --loglevel=info
```
{% endif %}

## Docker Support

```bash
# Build image
docker build -t {{ cookiecutter.__project_slug }} .

# Run container
docker run -p 8000:8000 {{ cookiecutter.__project_slug }}

# Development with docker-compose
docker-compose up -d
```

## Contributing

1. Create a new branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

This project is licensed under the terms of the {{ cookiecutter.license }} license.
