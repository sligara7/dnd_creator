# Builder stage
FROM python:3.11-slim as builder

# Install Poetry
RUN pip install poetry

# Copy dependency files
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Export dependencies
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m service_user

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set up application
COPY --chown=service_user:service_user . .

# Switch to non-root user
USER service_user

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.game_session.main:app", "--host", "0.0.0.0", "--port", "8000"]