# voice/voice.py
import os
import json
import io
import wave
from utils.utils import get_logger, ensure_dir

logger = get_logger(__name__)

# ---------- Text-to-Speech (gTTS) ----------
def synthesize_speech(text: str, lang: str = "en", output_path: str = "reports/tts_output.mp3") -> str:
    if not text.strip():
        return ""
    try:
        from gtts import gTTS
        ensure_dir(os.path.dirname(output_path) or ".")
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        return output_path
    except Exception as e:
        logger.error("TTS failed: %s", e)
        return ""

# ---------- Speech-to-Text (Vosk) ----------
VOSK_MODEL_PATHS = {
    "en": "models/vosk-model-small-en-us-0.15",
    "hi": "models/vosk-model-small-hi-0.22",
}
_vosk_models = {}

def _load_vosk_model(lang: str = "en"):
    global _vosk_models
    if lang in _vosk_models:
        return _vosk_models[lang]
    model_path = VOSK_MODEL_PATHS.get(lang, VOSK_MODEL_PATHS["en"])
    if not os.path.isdir(model_path):
        logger.warning("Vosk model not found at %s. Download from https://alphacephei.com/vosk/models", model_path)
        _vosk_models[lang] = None
        return None
    try:
        from vosk import Model
        model = Model(model_path)
        _vosk_models[lang] = model
        return model
    except Exception as e:
        logger.error("Vosk load failed: %s", e)
        _vosk_models[lang] = None
        return None

def transcribe_audio(wav_bytes: bytes, lang: str = "en") -> str:
    model = _load_vosk_model(lang)
    if model is None:
        return ""
    try:
        from vosk import KaldiRecognizer
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            return ""
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)
        result_text = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                result_text.append(res.get("text", ""))
        final = json.loads(recognizer.FinalResult())
        result_text.append(final.get("text", ""))
        return " ".join(t for t in result_text if t).strip()
    except Exception as e:
        logger.error("Transcription failed: %s", e)
        return ""