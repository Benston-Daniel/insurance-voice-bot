"""Simple ASR wrapper module.
This file provides a `transcribe` function that accepts raw audio bytes
and returns a transcribed string. It's a lightweight stub so you can
plug in Whisper or any other ASR engine later.
"""

import whisper

import os

# Add ffmpeg path explicitly
os.environ["PATH"] += os.pathsep + r"C:/Users/Benzten/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0-full_build/bin"

# load model once
_model = whisper.load_model("tiny")  # switch to "medium" or "base" depending on specs

def transcribe_audio(path, lang="auto"):
    # whisper returns dict
    # set language='ta' for Tamil if you want to force language
    opts = {}
    if lang and lang != "auto":
        opts['language'] = lang
    res = _model.transcribe(path, **opts)
    return res.get("text","").strip()
