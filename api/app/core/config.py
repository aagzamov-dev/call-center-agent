"""Application settings loaded from .env"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/agent.db"
    LLM_MODEL: str = "gpt-4.1-mini"
    LLM_FAST_MODEL: str = "gpt-4.1-nano"
    LLM_TEMPERATURE: float = 0.1
    EVAL_THRESHOLD: float = 0.4
    STT_MODEL: str = "whisper-1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
