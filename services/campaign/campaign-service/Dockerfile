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
