"""Simple TTS wrapper module.
Provides `synthesize` which returns wav bytes for given text.
This is a fallback stub; replace with Coqui TTS or other engines later.
"""

import os, uuid
from pathlib import Path

def tts_synthesize(text, out_dir, lang_hint="en"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{uuid.uuid4().hex}.wav"
    # Simple fallback: use Coqui TTS if available, else use OS TTS
    try:
        from TTS.api import TTS
        # choose a model that supports english/tamil if available, else default
        tts = TTS("tts_models/en/vctk/vits")  # example; you can pick a better one
        tts.tts_to_file(text=text, file_path=str(out_path))
        return str(out_path)
    except Exception as e:
        # fallback: save silence or return pre-recorded phrase
        # for now, create a short WAV using python-soundfile with generated speech
        from gtts import gTTS
        t = gTTS(text=text, lang="en")
        tmpfile = str(out_path.with_suffix(".mp3"))
        t.save(tmpfile)
        # convert mp3->wav using pydub
        from pydub import AudioSegment
        AudioSegment.from_mp3(tmpfile).export(out_path, format="wav")
        os.remove(tmpfile)
        return str(out_path)

