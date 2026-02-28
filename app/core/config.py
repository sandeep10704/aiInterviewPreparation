from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str | None = None
    LLM_MODEL: str |None = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    TAVILY_API_KEY: str

    FIREBASE_CREDENTIALS: str
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()