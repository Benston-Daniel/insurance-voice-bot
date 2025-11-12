#!/bin/bash
# Bash setup script for insurance-voice-bot
# Creates a virtual environment and installs dependencies

VENV_NAME="${1:-botenv}"
PYTHON_VERSION="${2:-3.11}"

echo "=== Insurance Voice Bot Setup (Bash) ==="
echo ""

# Create venv
echo "Creating virtual environment '$VENV_NAME'..."
python3 -m venv "$VENV_NAME"

# Activate venv
echo "Activating venv..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install base requirements
echo "Installing base requirements..."
pip install -r backend/requirements.txt

# Install NLU/LLM optional packages
echo ""
echo "Optional: Install NLU/LLM backends:"
echo "  1. SentenceTransformers (for embedding-based NLU)"
echo "  2. llama-cpp-python (for llama.cpp CPU backend)"
echo "  3. Transformers + Torch (for GPU-accelerated LLM)"
echo ""
read -p "Enter choice(s) separated by comma (e.g., 1,2 or leave blank): " choices

if [[ "$choices" == *"1"* ]]; then
    echo "Installing SentenceTransformers..."
    pip install sentence-transformers
fi

if [[ "$choices" == *"2"* ]]; then
    echo "Installing llama-cpp-python..."
    pip install llama-cpp-python
fi

if [[ "$choices" == *"3"* ]]; then
    echo "Installing Transformers, Torch, and bitsandbytes..."
    pip install torch transformers bitsandbytes
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  1. Read models/README.md for model download instructions"
echo "  2. Run: python backend/app/main.py"
echo "  3. API docs: http://localhost:8000/docs"
