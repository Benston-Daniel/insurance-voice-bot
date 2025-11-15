# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install System Dependencies
# This is the magic step that fixes all your friend's problems.
# - build-essential & cmake: Fixes the C++ build errors for llama-cpp-python
# - ffmpeg: Installs ffmpeg for Whisper
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-tam \
    libsndfile1 \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
# Copy the requirements file
# Use the backend requirements file (project stores Python deps under backend/)
COPY backend/requirements.txt ./requirements.txt

# Force llama-cpp-python to build for CPU ONLY
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=OFF"
ENV FORCE_CMAKE=1
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Application Code
# Copy all your project files (main_server.py, .html, etc.) into the container
COPY . .

# 4. Download the AI Model
# This runs the download script *inside* the container during the build.
## Download AI model during build (script lives under backend/src)
RUN python backend/src/download_model.py || true

# 5. Expose the WebSocket port
EXPOSE 8765

# Declare mount point for models so users can `-v $(pwd)/models:/app/models`
VOLUME ["/app/models"]

# 6. Set the default command to run when the container starts
CMD ["python", "backend/src/main_server.py"]