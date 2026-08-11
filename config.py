from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

__version__ = "0.1.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    database_url: str = "sqlite+aiosqlite:///./foodop.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
