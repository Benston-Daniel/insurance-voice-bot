import asyncio
import websockets
import whisper
import tempfile
import os
import numpy  # Whisper relies on numpy
import json  
from llm import RAGAgent  

# --- Configuration ---
SERVER_HOST = "0.0.0.0"  # Listen on all network interfaces
SERVER_PORT = 8765
WHISPER_MODEL = "base"   # Use "base", "small", "medium", or "large". "base" is fastest.
USE_FP16 = True        # Set to True if you have a good NVIDIA GPU and CUDA
# --- End Configuration ---

try:
    # Load the Whisper model once when the server starts
    print(f"Loading Whisper model: '{WHISPER_MODEL}'...")
    model = whisper.load_model(WHISPER_MODEL)
    print(f"Whisper model '{WHISPER_MODEL}' loaded successfully.")
    if USE_FP16 and model.device.type != "cuda":
        print("Warning: USE_FP16 is True but CUDA is not available. Using CPU (fp32).")
        USE_FP16 = False
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    print("Please ensure Whisper is installed (`pip install -U openai-whisper`)")
    exit(1)

# Load the RAG Agent (with LLM and BM25 index) once on startup
try:
    print("Loading RAGAgent (this may take a moment)...")
    rag_agent = RAGAgent()
    print("RAGAgent loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not initialize RAGAgent: {e}")
    print("Please ensure your models and data files are correct in retreive_respond.py")
    exit(1)

# REPLACE the old audio_handler with this new one (around line 43)

async def audio_handler(websocket):
    """
    Handles a single WebSocket connection.
    - Buffers incoming audio bytes.
    - On "STOP", transcribes audio, sends transcription to client,
      gets RAG response, and sends RAG response to client.
    - On text message, treats it as a query, gets RAG response,
      and sends RAG response to client.
    """
    print(f"Client connected from {websocket.remote_address}")
    audio_buffer = bytearray()
    
    try:
        async for message in websocket:
            
            if isinstance(message, bytes):
                # This is binary audio data (a chunk)
                audio_buffer.extend(message)
                
            elif isinstance(message, str):
                # This is a string message, either "STOP" or a text query

                query_text = ""
                
                if message == "STOP":
                    # --- 1. Handle Audio Transcription ---
                    print("STOP signal received. Processing audio...")
                    
                    if not audio_buffer:
                        print("No audio data received. Nothing to transcribe.")
                        continue 

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                        temp_file.write(audio_buffer)
                        temp_filename = temp_file.name

                    try:
                        print(f"Transcribing audio from {temp_filename}...")
                        result = model.transcribe(
                            temp_filename, 
                            fp16=USE_FP16,
                            language=None
                        )
                        transcription = result["text"].strip()
                        detected_lang = result["language"]
                        print(f"Transcription (Detected: {detected_lang}): {transcription}")

                        # Send the user's transcription back to the client
                        await websocket.send(json.dumps({
                            "type": "user",
                            "text": transcription
                        }))
                        
                        query_text = transcription
                        is_audio_query = True

                    except Exception as e:
                        print(f"Error during transcription: {e}")
                        await websocket.send(json.dumps({"type": "ai", "text": f"[Error: {e}]"}))
                    finally:
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)
                        audio_buffer = bytearray() # Clear buffer after processing
                
                else:
                    # --- 2. Handle Typed Text Query ---
                    print(f"Received text query: {message}")
                    query_text = message
                    is_audio_query = False
                    # The client already displayed this text, so no need to send it back.

                
                # --- 3. Get RAG Response (for both audio and text) ---
                if query_text:
                    try:
                        print(f"Getting RAG response for: '{query_text}'")
                        
                        # This calls your RAGAgent class
                        ai_response = rag_agent.answer(query_text)

                        # Send the AI's response back to the client
                        await websocket.send(json.dumps({
                            "type": "ai",
                            "text": ai_response,
                            # Speak only when the query came from audio (STOP)
                            "speak": bool(is_audio_query)
                        }))
                        print("RAG response sent. Ready for next message.")

                    except Exception as e:
                        print(f"Error getting RAG response: {e}")
                        await websocket.send(json.dumps({"type": "ai", "text": f"[Error: {e}]"}))

            # End of message loop

    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client {websocket.remote_address} disconnected normally.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client {websocket.remote_address} connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with {websocket.remote_address}: {e}")
    finally:
        print(f"Handler for {websocket.remote_address} finished.")

async def main():
    print(f"Starting WebSocket server on ws://{SERVER_HOST}:{SERVER_PORT}")
    async with websockets.serve(audio_handler, SERVER_HOST, SERVER_PORT, max_size=None):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down.")