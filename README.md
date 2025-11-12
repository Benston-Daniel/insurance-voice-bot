<<<<<<< HEAD
<<<<<<< HEAD
# insurance-voice-bot
AI Insurance multi lingual Voice Assistance using RASA NLU
=======
# Insurance Voice Bot (starter)
=======
# Insurance Voice Bot (Bilingual NLU+LLM)
>>>>>>> 8f9c065 (chore: migrate from Rasa; scaffold lightweight NLU/LLM architecture, add nlu_engine, llm_runner, backend, data, scripts)

A lightweight, bilingual (Tamil+English) **insurance voice agent** built with:
- **NLU Engine:** SentenceTransformers embeddings for intent classification
- **LLM Support:** Local LLMs via llama.cpp (CPU) or Transformers (GPU)
- **Backend:** FastAPI with ASR (Whisper) and TTS (Coqui/fallback)
- **No Rasa:** Custom, lightweight NLU+LLM orchestration

## 🎯 Features

- ✅ **Bilingual:** Tamil and English (mixed queries supported)
- ✅ **Voice I/O:** Automatic speech recognition (ASR) + text-to-speech (TTS)
- ✅ **Lightweight:** No heavy frameworks (Rasa removed); embeddings + local LLM
- ✅ **Intent Classification:** SentenceTransformers multilingual embeddings
- ✅ **Flexible LLM:** Mock, llama.cpp (CPU), or Transformers (GPU)
- ✅ **Insurance Domain:** Pre-configured for claim/policy queries
- ✅ **API-First:** REST endpoints for text and voice queries

## 📁 Project Structure

```
insurance-voice-bot/
├─ nlu_engine/                    # Intent classifier + NLU
│  ├─ __init__.py
│  └─ intent_classifier.py        # SentenceTransformers-based classifier
├─ llm_runner/                    # LLM runners (CPU/GPU)
│  ├─ __init__.py
│  └─ llm_interface.py            # LlamaCpp, Transformers, Mock runners
├─ backend/
│  ├─ app/
│  │  ├─ main.py                  # FastAPI server
│  │  ├─ orchestrator.py          # Insurance agent (NLU+LLM)
│  │  ├─ asr.py                   # Whisper wrapper
│  │  ├─ tts.py                   # Coqui TTS wrapper
│  │  └─ utils.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ data/
│  ├─ intents_bilingual.json      # Intent examples (Tamil+English)
│  ├─ mock_policies.json          # Sample policies
│  └─ mock_claims.json            # Sample claims
├─ models/                         # Place downloaded LLMs here
│  └─ README.md                   # Model download + setup guide
├─ scripts/
│  ├─ setup_venv.ps1              # Windows setup
│  └─ setup_venv.sh               # Linux/Mac setup
├─ frontend/
│  ├─ index.html
│  └─ app.js
├─ docker-compose.yml
├─ README.md
├─ .gitignore
└─ backups/
   └─ cleanup_log.md              # Migration log
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- (Optional) NVIDIA GPU for LLM acceleration

### Step 1: Setup Virtual Environment

**Windows (PowerShell):**
```powershell
.\scripts\setup_venv.ps1
```

**Linux/Mac (Bash):**
```bash
chmod +x scripts/setup_venv.sh
./scripts/setup_venv.sh
```

### Step 2: Download Models (Optional)

See [`models/README.md`](models/README.md) for step-by-step instructions.

### Step 3: Run the Backend

```bash
python backend/app/main.py
```

Server starts at `http://localhost:8000`

## 📡 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Text Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my claim status?"}'
```

### 3. Voice Query (ASR + NLU + TTS)
```bash
curl -X POST http://localhost:8000/voice \
  -F "file=@audio.wav" \
  -F "lang=auto"
```

### 4. Interactive Docs
Open `http://localhost:8000/docs` (Swagger UI)

## 🧪 Testing

**Text Query (Tamil):**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "என் பாலிசி நிலை என்ன?"}'
```

## 🐳 Docker

```bash
docker-compose up --build
```

## 📝 Migration Notes

<<<<<<< HEAD
Notes and next steps:
- `backend/app/asr.py` and `backend/app/tts.py` are stubs. Integrate Whisper/Coqui TTS as needed.
- Add tests and improve CI pipeline.
- Secure production deployments and configure credentials.
>>>>>>> 904de86 (Initial commit for dev branch)
=======
- **Rasa Removed:** Custom lightweight NLU replaces Rasa
- **Benefits:** No heavy Rasa server, easier to embed in edge devices
- See `backups/cleanup_log.md` for migration details.
>>>>>>> 8f9c065 (chore: migrate from Rasa; scaffold lightweight NLU/LLM architecture, add nlu_engine, llm_runner, backend, data, scripts)
