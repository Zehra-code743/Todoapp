"""
Configuration management for Todo Application Backend
Loads environment variables and provides typed settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # AI Integration
    openai_api_key: str | None = None

    # Server
    port: int = 8000
    env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.env.lower() == "production"


# Global settings instance
settings = Settings()
