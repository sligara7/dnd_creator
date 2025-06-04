FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /stable-diffusion

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    libgl1 \
    libglib2.0-0 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate Python virtual environment
RUN python3 -m venv /stable-diffusion/venv
ENV PATH="/stable-diffusion/venv/bin:$PATH"

# Clone Stable Diffusion Web UI repository
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git .

# Install basic requirements
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir xformers

# Create directories for models, configs, outputs, and LoRAs
RUN mkdir -p /stable-diffusion/models/Stable-diffusion \
    /stable-diffusion/models/LoRA \
    /stable-diffusion/outputs \
    /stable-diffusion/extensions \
    /stable-diffusion/config

# Copy configuration files
COPY config/sd_config.json /stable-diffusion/config/
COPY loras/ /stable-diffusion/models/LoRA/

# Create a base model download script
RUN echo '#!/bin/bash\n\
if [ ! -f "/stable-diffusion/models/Stable-diffusion/dreamshaper_8.safetensors" ]; then\n\
  echo "Downloading DreamShaper model..."\n\
  wget https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors -O /stable-diffusion/models/Stable-diffusion/dreamshaper_8.safetensors\n\
  echo "Model downloaded successfully!"\n\
else\n\
  echo "DreamShaper model already exists."\n\
fi\n\
\n\
if [ ! -f "/stable-diffusion/models/VAE/vae.pt" ]; then\n\
  echo "Downloading VAE..."\n\
  mkdir -p /stable-diffusion/models/VAE\n\
  wget https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors -O /stable-diffusion/models/VAE/vae.pt\n\
  echo "VAE downloaded successfully!"\n\
fi\n\
\n\
# Install Character Creator LoRA extension\n\
if [ ! -d "/stable-diffusion/extensions/character-creator" ]; then\n\
  echo "Installing Character Creator extension..."\n\
  git clone https://github.com/some-fantasy-character-creator/extension.git /stable-diffusion/extensions/character-creator\n\
fi\n\
' > /stable-diffusion/download_models.sh && chmod +x /stable-diffusion/download_models.sh

# Create startup script
RUN echo '#!/bin/bash\n\
# First, run the model download script\n\
./download_models.sh\n\
\n\
# Start the Stable Diffusion Web UI with API enabled\n\
python launch.py \
  --api \
  --listen \
  --port 7860 \
  --xformers \
  --no-half-vae \
  --medvram \
  --api-auth="$SD_API_USERNAME:$SD_API_PASSWORD" \
  --ui-config-file=/stable-diffusion/config/sd_config.json \
  --extra-model-paths=/stable-diffusion/models/LoRA\n\
' > /stable-diffusion/start.sh && chmod +x /stable-diffusion/start.sh

# Create a configuration for the API
RUN echo '{\n\
  "sd_model_checkpoint": "dreamshaper_8.safetensors",\n\
  "sd_vae": "vae.pt",\n\
  "CLIP_stop_at_last_layers": 2,\n\
  "samples_save": true,\n\
  "samples_format": "png",\n\
  "save_images_add_number": true,\n\
  "save_txt": false,\n\
  "outdir_txt2img_samples": "/stable-diffusion/outputs/txt2img",\n\
  "outdir_img2img_samples": "/stable-diffusion/outputs/img2img",\n\
  "enable_emphasis": true\n\
}' > /stable-diffusion/config/config.json

# Set environment variables for optimization
ENV COMMANDLINE_ARGS="--medvram --no-half-vae --xformers"

# Expose the Web UI port
EXPOSE 7860

# Start the Web UI with API enabled
CMD ["/bin/bash", "/stable-diffusion/start.sh"]