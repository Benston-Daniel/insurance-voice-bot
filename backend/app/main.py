from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from . import asr, tts, rasa_client

app = FastAPI(title="Insurance Voice Bot Backend")

@app.post('/asr')
async def run_asr(file: UploadFile = File(...)):
    """Accepts an uploaded audio file and returns transcribed text."""
    audio_bytes = await file.read()
    try:
        text = asr.transcribe(audio_bytes)
        return {"text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post('/tts')
async def run_tts(payload: dict):
    """Accepts JSON {"text": "..."} and returns audio (wav) stream."""
    text = payload.get('text', '')
    if not text:
        return JSONResponse(status_code=400, content={"error": "`text` is required"})
    audio_bytes = tts.synthesize(text)
    return StreamingResponse(iter([audio_bytes]), media_type='audio/wav')

@app.post('/rasa')
async def proxy_rasa(payload: dict):
    """Proxy to Rasa server for sending user message and returning bot response."""
    message = payload.get('message')
    if not message:
        return JSONResponse(status_code=400, content={"error": "`message` is required"})
    resp = rasa_client.send_message(message)
    return resp

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
