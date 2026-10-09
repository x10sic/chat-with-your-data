"""Central settings, read from environment (see .env.example)."""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # env vars still work; .env file just won't auto-load

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_sales.csv")
