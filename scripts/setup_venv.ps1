# PowerShell setup script for insurance-voice-bot
# Creates a virtual environment and installs dependencies

param(
    [string]$VenvName = "botenv",
    [string]$PythonVersion = "3.11"
)

Write-Host "=== Insurance Voice Bot Setup (PowerShell) ===" -ForegroundColor Cyan

# Create venv
Write-Host "Creating virtual environment '$VenvName'..." -ForegroundColor Green
python -m venv $VenvName

# Activate venv
Write-Host "Activating venv..." -ForegroundColor Green
& ".\$VenvName\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install base requirements
Write-Host "Installing base requirements..." -ForegroundColor Green
pip install -r backend/requirements.txt

# Install NLU/LLM optional packages (user-selectable)
Write-Host "" -ForegroundColor White
Write-Host "Optional: Install NLU/LLM backends:" -ForegroundColor Yellow
Write-Host "  1. SentenceTransformers (for embedding-based NLU)" -ForegroundColor White
Write-Host "  2. llama-cpp-python (for llama.cpp CPU backend)" -ForegroundColor White
Write-Host "  3. Transformers + Torch (for GPU-accelerated LLM)" -ForegroundColor White

$choice = Read-Host "Enter choice(s) separated by comma (e.g., 1,2 or leave blank): "

if ($choice -match "1") {
    Write-Host "Installing SentenceTransformers..." -ForegroundColor Green
    pip install sentence-transformers
}

if ($choice -match "2") {
    Write-Host "Installing llama-cpp-python..." -ForegroundColor Green
    pip install llama-cpp-python
}

if ($choice -match "3") {
    Write-Host "Installing Transformers, Torch, and bitsandbytes..." -ForegroundColor Green
    pip install torch transformers bitsandbytes
}

Write-Host "" -ForegroundColor White
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Read models/README.md for model download instructions" -ForegroundColor White
Write-Host "  2. Run: python backend/app/main.py" -ForegroundColor White
Write-Host "  3. API docs: http://localhost:8000/docs" -ForegroundColor White
