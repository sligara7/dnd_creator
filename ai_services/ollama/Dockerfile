FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Install any additional required utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for any pre/post processing scripts
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip3 install --no-cache-dir -r requirements.txt; fi

# Create directories for Ollama data and models
RUN mkdir -p /root/.ollama/models

# Copy prompt templates and rules data into the container
COPY prompt_templates/ /app/prompt_templates/
COPY rules_data/ /app/rules_data/

# Create a startup script
RUN echo '#!/bin/bash\n\
# Wait for Ollama server to start\n\
function wait_for_ollama {\n\
  echo "Waiting for Ollama server..."\n\
  while ! curl -s http://localhost:11434/api/tags >/dev/null; do\n\
    sleep 1\n\
  done\n\
  echo "Ollama server is running!"\n\
}\n\
\n\
# Start Ollama server in the background\n\
nohup ollama serve &\n\
\n\
# Wait for server to be available\n\
wait_for_ollama\n\
\n\
# Pull Llama 3 8B model if not already available\n\
if ! ollama list | grep -q "llama3"; then\n\
  echo "Pulling llama3 model..."\n\
  ollama pull llama3\n\
  echo "Model downloaded successfully!"\n\
else\n\
  echo "llama3 model already available."\n\
fi\n\
\n\
# Keep container running and handle graceful shutdown\n\
echo "Ollama service is ready to handle requests!"\n\
exec "$@" || trap "echo Shutting down...; pkill -f ollama" SIGTERM SIGINT\n\
tail -f /dev/null\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the Ollama API port
EXPOSE 11434

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models

# Run the startup script when the container launches
CMD ["/app/start.sh"]