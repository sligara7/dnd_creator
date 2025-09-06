# Builder stage for dependencies
FROM python:3.11-slim as builder

# Install Poetry and system dependencies
RUN pip install poetry && \
    apt-get update && \
    apt-get install -y \
        curl \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files only
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m service_user

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set up application
COPY --chown=service_user:service_user . .
USER service_user

CMD ["poetry", "run", "uvicorn", "src.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
