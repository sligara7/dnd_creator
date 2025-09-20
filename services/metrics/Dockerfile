# Builder stage
FROM python:3.11-slim as builder

# Install Poetry
RUN pip install poetry

# Copy dependency files
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m service_user

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=service_user:service_user . .

# Switch to non-root user
USER service_user

# Run application
CMD ["uvicorn", "metrics_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Use a multi-stage build
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
