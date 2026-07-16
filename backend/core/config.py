from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    qdrant_url: str
    openai_api_key: str

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]#["http://localhost:3000"]

    # Resend API key
    resend_api_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()