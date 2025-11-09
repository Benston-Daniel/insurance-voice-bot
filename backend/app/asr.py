"""Simple ASR wrapper module.
This file provides a `transcribe` function that accepts raw audio bytes
and returns a transcribed string. It's a lightweight stub so you can
plug in Whisper or any other ASR engine later.
"""

import io

def transcribe(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text.

    Currently returns a placeholder string. Replace with Whisper or
    other ASR call.
    """
    # TODO: integrate Whisper or external ASR here
    if not audio_bytes:
        return ""
    # naïve placeholder (in real usage, decode audio and pass to ASR)
    return "[transcribed text placeholder]"
