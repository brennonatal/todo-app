"""Application settings using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "TODO App"

    # Database
    database_url: str = "postgresql://todo:todo@localhost:5432/tododb"
    database_echo: bool = False

    # Docker database (used in Docker Compose)
    postgres_user: str = "todo"
    postgres_password: str = "todo"
    postgres_db: str = "tododb"


# Global settings instance
settings = Settings()
