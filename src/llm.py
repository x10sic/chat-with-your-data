"""Build the chat LLM. Ollama (local) by default; OpenAI/Gemini via env.

On Streamlit Cloud there is no local Ollama, so when the default provider
can't be reached and a Gemini key is configured, Gemini is used instead.
"""
from functools import lru_cache

from config import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


@lru_cache(maxsize=1)
def ollama_reachable() -> bool:
    """Quick probe: is there an Ollama server at OLLAMA_BASE_URL?"""
    try:
        import requests

        resp = requests.get(OLLAMA_BASE_URL.rstrip("/"), timeout=3)
        return resp.status_code < 500
    except Exception:
        return False


def resolve_provider() -> str:
    """Effective provider: fall back from Ollama to Gemini when Ollama is
    unreachable and a Gemini key is configured. Explicit openai/gemini
    choices are never overridden."""
    if (
        LLM_PROVIDER == "ollama"
        and GOOGLE_API_KEY
        and not ollama_reachable()
    ):
        return "gemini"
    return LLM_PROVIDER


def provider_label() -> str:
    """Human-readable name of the provider actually in use."""
    return {"ollama": f"Ollama ({OLLAMA_MODEL})",
            "openai": f"OpenAI ({OPENAI_MODEL})",
            "gemini": f"Gemini ({GEMINI_MODEL})"}.get(resolve_provider(),
                                                      resolve_provider())


def get_llm():
    """Return a LangChain chat model for the resolved provider."""
    provider = resolve_provider()
    if provider == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is empty.")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)

    if provider == "gemini":
        if not GOOGLE_API_KEY:
            raise RuntimeError("LLM_PROVIDER=gemini but GOOGLE_API_KEY is empty.")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0
        )

    # default: ollama (local, no key)
    from langchain_ollama import ChatOllama

    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
