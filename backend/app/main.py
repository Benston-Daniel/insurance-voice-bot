"""FastAPI server for Insurance Voice Bot (bilingual NLU+LLM backend)."""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import sys

# Add parent directories to path so we can import nlu_engine, llm_runner
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.app.orchestrator import InsuranceAgent
from backend.app import asr, tts, utils

app = FastAPI(title="Insurance Voice Bot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
intents_path = os.path.join(os.path.dirname(__file__), "../../data/intents_bilingual.json")
llm_backend = os.getenv("LLM_BACKEND", "mock")  # mock, llama-cpp, or transformers
agent = InsuranceAgent(intents_path, llm_backend=llm_backend)

# Ensure work directories
WORKDIR = os.path.join(os.path.dirname(__file__), "../../tmp")
LOGDIR = os.path.join(os.path.dirname(__file__), "../../logs")
utils.ensure_dir(WORKDIR)
utils.ensure_dir(LOGDIR)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "insurance-voice-bot", "llm_backend": llm_backend}


@app.post("/query")
async def query_text(payload: dict):
    """Process a text query (bilingual: Tamil/English).
    
    Input: {"message": "What is my claim status?"}
    Output: {"intent": "...", "response": "...", ...}
    """
    message = payload.get("message", "")
    if not message:
        return JSONResponse(status_code=400, content={"error": "message is required"})
    
    try:
        result = agent.process_query(message)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/voice")
async def voice_query(file: UploadFile = File(...), lang: str = "auto"):
    """Process audio query: ASR -> NLU -> LLM -> TTS.
    
    Returns: {"text": "...", "response": "...", "audio_file": "..."}
    """
    # Save uploaded audio
    ext = os.path.splitext(file.filename)[1] or ".wav"
    fname = f"{uuid.uuid4().hex}{ext}"
    audio_path = os.path.join(WORKDIR, fname)
    
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # 1. ASR (speech to text)
        transcript = asr.transcribe(audio_path, lang=lang)
        
        # 2. NLU + LLM (query processing)
        agent_result = agent.process_query(transcript)
        response_text = agent_result.get("response", "Sorry, I couldn't process your request.")
        
        # 3. TTS (text to speech)
        audio_out = tts.synthesize(response_text)
        
        return {
            "transcript": transcript,
            "intent": agent_result.get("intent"),
            "response": response_text,
            "audio_data": audio_out.hex() if audio_out else None
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
