# Builder stage
FROM python:3.11-slim as builder

# Install Poetry and system dependencies
RUN pip install poetry && \
    apt-get update && \
    apt-get install -y \
        curl \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Poetry
WORKDIR /app
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy dependency files only
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only main --no-root

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m service_user
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Copy application code
COPY --chown=service_user:service_user . .

# Switch to non-root user
USER service_user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application with migrations
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.character_service.main:app --host 0.0.0.0 --port 8000"]
