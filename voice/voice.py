# voice/voice.py – TTS without pygame
import os
import io
from gtts import gTTS
from utils.utils import get_logger, ensure_dir

logger = get_logger(__name__)

def synthesize_speech(text: str, lang: str = "en", output_path: str = "reports/tts_output.mp3") -> str:
    if not text.strip():
        return ""
    try:
        ensure_dir(os.path.dirname(output_path) or ".")
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return output_path
    except Exception as e:
        logger.error("TTS failed: %s", e)
        return ""

def get_speech_bytes(text: str, lang: str = "en") -> bytes:
    """Return speech as bytes for Streamlit audio."""
    if not text.strip():
        return b""
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        logger.error("TTS bytes failed: %s", e)
        return b""
