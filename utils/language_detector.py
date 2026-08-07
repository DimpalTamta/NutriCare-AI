# utils/language_detector.py – Added Marathi
import re

DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")

def detect_language(text: str) -> str:
    if not text:
        return "en"
    # Simple detection – if Devanagari present, assume Hindi or Marathi
    if DEVANAGARI_PATTERN.search(text):
        # Could further differentiate, but we'll default to Hindi
        return "hi"
    return "en"

LANGUAGE_CODES = {"English": "en", "Hindi": "hi", "Marathi": "mr"}