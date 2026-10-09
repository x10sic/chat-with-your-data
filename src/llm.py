"""Build the chat LLM. Ollama (local) by default; OpenAI/Gemini via env."""
from config import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def get_llm():
    """Return a LangChain chat model for the configured provider."""
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is empty.")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)

    if LLM_PROVIDER == "gemini":
        if not GOOGLE_API_KEY:
            raise RuntimeError("LLM_PROVIDER=gemini but GOOGLE_API_KEY is empty.")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0
        )

    # default: ollama (local, no key)
    from langchain_ollama import ChatOllama

    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
