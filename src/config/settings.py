"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Evolution API
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE_NAME: str = "pangeia_bot"

    # Notion API
    NOTION_API_KEY: str
    NOTION_DATABASE_ID: str

    # OpenAI / LangChain
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7

    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Webhook
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook/evolution"

    # Timezone
    TIMEZONE: str = "America/Sao_Paulo"

    # Agent Configuration
    AGENT_TEMPERATURE: float = 0.7
    AGENT_MAX_ITERATIONS: int = 5
    AGENT_MEMORY_KEY: str = "chat_history"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
