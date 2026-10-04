import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = int(os.getenv("PORT", 8000))
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://carcheck-kg.onrender.com")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
