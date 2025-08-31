FROM ghcr.io/prefix-dev/pixi:latest

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (using next available UID)
RUN useradd -m character_service

# Set working directory and create application directories
WORKDIR /app
RUN mkdir -p /app/src /app/config /app/alembic /tmp \
    && chown -R character_service:character_service /app /tmp

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PROMETHEUS_MULTIPROC_DIR=/tmp \
    HOME=/home/character_service

# Switch to non-root user for pixi operations
USER character_service

# Copy pixi configuration first to leverage layer caching
COPY --chown=character_service:character_service pixi.toml ./

# Install dependencies using pixi
RUN pixi install

# Copy application files
COPY --chown=character_service:character_service src/ src/
COPY --chown=character_service:character_service config/ config/
COPY --chown=character_service:character_service prometheus.yml ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

# Command to run migrations and start service
CMD ["sh", "-c", "cd src/character_service && pixi run alembic upgrade head && cd /app && pixi run start"]
