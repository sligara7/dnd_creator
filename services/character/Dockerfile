FROM ghcr.io/prefix-dev/pixi:latest

# Set working directory
WORKDIR /app

# Copy pixi configuration
COPY pixi.toml ./

# Copy project files
COPY src/ src/
COPY config/ config/
COPY alembic.ini ./
COPY alembic/ alembic/

# Create non-root user
RUN useradd -m -u 1000 character_service

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PROMETHEUS_MULTIPROC_DIR=/tmp

# Create and set permissions for prometheus metrics directory
RUN mkdir -p /tmp \
    && chown -R character_service:character_service /tmp

# Install dependencies using pixi
RUN pixi install

# Switch to non-root user
USER character_service

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

# Command to run migrations and start service
CMD ["sh", "-c", "pixi run alembic upgrade head && pixi run start"]
