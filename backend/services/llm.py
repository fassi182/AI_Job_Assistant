"""
Thin wrapper around the Groq LLM via LangChain.
All LangGraph nodes call get_llm() so tracing/config stays centralized.
"""
from langchain_groq import ChatGroq
from config import settings

_llm = None


def get_llm(temperature: float = 0.3) -> ChatGroq:
    """Return a cached ChatGroq client. LangSmith tracing is picked up
    automatically from the LANGCHAIN_* environment variables."""
    global _llm
    if _llm is None or _llm.temperature != temperature:
        _llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=temperature,
        )
    return _llm
