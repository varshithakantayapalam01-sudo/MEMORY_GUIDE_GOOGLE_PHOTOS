from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str = "your_gemini_api_key"
    GEMINI_MODEL: str = "gemini-3.8-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    ALLOW_SYNTHETIC_AI: bool = True
    INITIAL_ACTIVE_LIMIT: int = 12

    ANALYTICS_ADMIN_TOKEN: str = "replace_with_secure_random_token"

    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DB_PATH: str = "./data/memory_guide.db"
    TEMP_UPLOAD_DIR: str = "./tmp/research_sessions"

    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        if self.FRONTEND_URL and self.FRONTEND_URL.strip() not in origins:
            origins.append(self.FRONTEND_URL.strip())
        return origins


settings = Settings()
