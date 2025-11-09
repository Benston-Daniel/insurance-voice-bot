# Insurance Voice Bot (starter)

This repository contains a starter layout for an insurance voice bot:
- `backend/` - FastAPI backend with simple ASR/TTS stubs and a Rasa client
- `rasa_project/` - example Rasa project (NLU, stories, domain, actions)
- `frontend/` - small static web UI to demo text messages
- `.github/workflows/ci.yml` - basic CI syntax check
- `docker-compose.yml` - compose file to run backend + Rasa

Quick start (development):

1. Build and run with Docker Compose:

```powershell
cd insurance-voice-bot
docker-compose up --build
```

2. Backend will be at http://localhost:8000
   Rasa server will be at http://localhost:5005

Notes and next steps:
- `backend/app/asr.py` and `backend/app/tts.py` are stubs. Integrate Whisper/Coqui TTS as needed.
- Add tests and improve CI pipeline.
- Secure production deployments and configure credentials.
