"""
Application configuration loaded from environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # LangSmith
    langchain_tracing_v2: bool = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "ai-job-application-assistant")
    langchain_endpoint: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

    # Backend
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

    # File storage
    upload_dir: str = os.getenv("UPLOAD_DIR", "storage/uploads")
    output_dir: str = os.getenv("OUTPUT_DIR", "storage/outputs")

    class Config:
        env_file = str(Path(__file__).resolve().parents[1] / ".env")
        extra = "ignore"


settings = Settings()

# Export LangSmith env vars so LangChain/LangGraph pick them up automatically.
# If no LangChain API key is configured, disable tracing to avoid unauthorized
# LangSmith logging attempts.
if settings.langchain_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
    os.environ["LANGSMITH_API_KEY"] = settings.langchain_api_key
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ.pop("LANGCHAIN_API_KEY", None)
    os.environ.pop("LANGCHAIN_PROJECT", None)
    os.environ.pop("LANGCHAIN_ENDPOINT", None)
    os.environ.pop("LANGSMITH_API_KEY", None)

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
