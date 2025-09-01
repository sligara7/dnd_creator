# Use multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Install Poetry
RUN pip install poetry

# Copy dependencies files
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy requirements from builder stage
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src src/

# Add any additional files needed
COPY alembic.ini ./

# Create non-root user
RUN useradd -m appuser
USER appuser

# Run the application
CMD ["uvicorn", "src.{{ cookiecutter.__project_slug }}.main:app", "--host", "0.0.0.0", "--port", "8000"]
