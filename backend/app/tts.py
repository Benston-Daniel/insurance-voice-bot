"""Simple TTS wrapper module.
Provides `synthesize` which returns wav bytes for given text.
This is a fallback stub; replace with Coqui TTS or other engines later.
"""

import io

# Small silent WAV header for placeholder (1-second silence, 16kHz, 16-bit mono)
# NOTE: For real TTS, call Coqui or similar and return real audio bytes.

def synthesize(text: str) -> bytes:
    if not text:
        return b''
    # Return a tiny placeholder WAV file header + empty frames
    # This is NOT a real TTS; replace it with actual TTS output.
    wav_silence = (
        b'RIFF\x24\x00\x00\x00WAVEfmt '  # header
        b'\x10\x00\x00\x00\x01\x00\x01\x00'  # PCM, mono
        b'\x80<\x00\x00\x00\x7d\x00\x02\x00\x10\x00'  # sample rate 16000
        b'data\x00\x00\x00\x00'
    )
    return wav_silence
