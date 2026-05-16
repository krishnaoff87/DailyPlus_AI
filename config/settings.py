"""
Secure configuration loader for DailyPlus_AI PoC.
Validates environment variables at boot time.
"""

from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with Pydantic validation."""

    ANTHROPIC_API_KEY: str

    model_config = SettingsConfigDict(
        env_file="config/.env", env_file_encoding="utf-8", extra="ignore"
    )


# Load .env file from config directory
config_dir = Path(__file__).parent.resolve()
env_path = config_dir / ".env"

load_dotenv(dotenv_path=env_path)

# Create settings instance
try:
    settings = Settings()
except Exception as e:
    raise ValueError(
        "ANTHROPIC_API_KEY is missing or empty!\n\n"
        "Setup Instructions:\n"
        "1. Copy 'config/.env.example' to 'config/.env'\n"
        "2. Add your Anthropic API key to 'config/.env'\n"
        "3. Get your API key from: https://console.anthropic.com/\n"
    ) from e

# Export settings instance
__all__ = ["settings"]

# Made with Bob
