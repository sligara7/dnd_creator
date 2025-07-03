# D&D Character Creator Backend API
# Podman-optimized container with clean, modular architecture
# Supports complete character creation and refinement system
FROM python:3.11-slim

# Add labels for Podman container management
LABEL maintainer="D&D Character Creator" \
      version="2.0" \
      description="AI-powered D&D 5e 2024 character creation system" \
      org.opencontainers.image.source="https://github.com/user/dnd_char_creator" \
      org.opencontainers.image.title="D&D Character Creator Backend" \
      org.opencontainers.image.description="Complete character creation with clean modular architecture"

# Set working directory
WORKDIR /app

# Set environment variables optimized for Podman and rootless containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src \
    ENV=production \
    PODMAN_USERNS=keep-id \
    HOME=/app \
    TMPDIR=/tmp

# Install system dependencies for LLM services and data processing
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        git \
        sqlite3 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application source code with new modular structure
COPY src/ ./src/
COPY app.py main.py ./
COPY .env.example .env

# Create directories for data, logs, and character storage with Podman-friendly permissions
RUN mkdir -p /app/data /app/logs /app/characters /app/custom_content /app/tests \
    && chmod 755 /app/data /app/logs /app/characters /app/custom_content /app/tests

# Create non-root user for Podman rootless containers
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port for Podman
EXPOSE 8000

# Podman-compatible health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application using uvicorn with Podman-optimized settings
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]
