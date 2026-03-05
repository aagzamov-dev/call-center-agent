"""Application settings loaded from .env"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/agent.db"
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.2
    STT_MODEL: str = "whisper-1"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
