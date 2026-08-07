# llm/llm.py – Fixed API key loading with absolute path
import os
from pathlib import Path
from dotenv import load_dotenv
from utils.utils import get_logger

# Load .env from project root (parent of llm folder)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = get_logger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
_groq_client = None

def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment. Check .env file.")
            return None
        try:
            from groq import Groq
            _groq_client = Groq(api_key=api_key)
            print("✅ Groq client created.")
        except Exception as e:
            print(f"🔥 Groq init error: {e}")
            logger.error("Groq init failed: %s", e)
            _groq_client = None
    return _groq_client

def generate_response(prompt: str) -> str:
    client = _get_groq_client()
    if client:
        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1024,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"🔥 Groq API call error: {e}")
            logger.error("Groq failed: %s", e)
    # Fallback message
    return (
        "I'm currently unable to reach the language model backend. "
        "Please verify your `GROQ_API_KEY` in the `.env` file. "
        "In the meantime, please consult your oncology care team directly."
    )