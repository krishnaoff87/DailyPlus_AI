"""
Secure configuration loader for DailyPlus_AI PoC.
Validates environment variables at boot time.
Provides environment detection and Streamlit config path resolution.
"""

from pathlib import Path
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with Pydantic validation.

    Environment Variables:
        GEMINI_API_KEY: Google Gemini API key (required, must start with 'AIza')
        NVIDIA_API_KEY: NVIDIA NIM API key (optional, must start with 'nvapi-')
        ENVIRONMENT: Deployment environment ('development' or 'production')
        MOCK_DATA_PATH: Path to mock data file for testing
        STREAMLIT_SERVER_PORT: Port for Streamlit server (default: 8501)

    Usage:
        from config.settings import settings

        # Access settings
        api_key = settings.GEMINI_API_KEY
        is_prod = settings.is_production()

        # Get appropriate Streamlit config
        config_path = settings.get_streamlit_config_path()
    """

    GEMINI_API_KEY: str
    NVIDIA_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    MOCK_DATA_PATH: str = "data/mock_daily_context.json"
    STREAMLIT_SERVER_PORT: int = 8501

    def is_production(self) -> bool:
        """Check if running in production environment.

        Returns:
            bool: True if ENVIRONMENT is 'production', False otherwise
        """
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment.

        Returns:
            bool: True if ENVIRONMENT is 'development', False otherwise
        """
        return self.ENVIRONMENT.lower() == "development"

    def get_streamlit_config_path(self) -> Path:
        """Get the appropriate Streamlit configuration file path.

        Returns the path to the environment-specific Streamlit config file:
        - Development: .streamlit/config.toml (or config.development.toml)
        - Production: .streamlit/config.production.toml

        Returns:
            Path: Absolute path to the Streamlit configuration file

        Example:
            # In your startup script:
            from config.settings import settings
            config_path = settings.get_streamlit_config_path()

            # Use with Streamlit CLI:
            # streamlit run app/main.py --server.port {settings.STREAMLIT_SERVER_PORT}
        """
        project_root = Path(__file__).parent.parent.resolve()

        if self.is_production():
            config_file = project_root / ".streamlit" / "config.production.toml"
        else:
            # Development: use base config.toml (already configured for dev)
            config_file = project_root / ".streamlit" / "config.toml"

        return config_file

    def get_environment_info(self) -> dict:
        """Get current environment configuration information.

        Returns:
            dict: Environment details including mode, config path, and security settings
        """
        config_path = self.get_streamlit_config_path()

        return {
            "environment": self.ENVIRONMENT,
            "is_production": self.is_production(),
            "streamlit_config": str(config_path),
            "streamlit_port": self.STREAMLIT_SERVER_PORT,
            "cors_enabled": self.is_production(),  # CORS enabled in production
            "xsrf_protection": self.is_production(),  # XSRF enabled in production
        }

    model_config = SettingsConfigDict(
        env_file="config/.env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """Validate that GEMINI_API_KEY starts with 'AIza'."""
        if not v.startswith("AIza"):
            raise ValueError(
                "Invalid GEMINI_API_KEY format!\n\n"
                "The API key must start with 'AIza'.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        return v

    @field_validator("NVIDIA_API_KEY")
    @classmethod
    def validate_nvidia_key(cls, v: str) -> str:
        """Validate that NVIDIA_API_KEY starts with 'nvapi-' if provided."""
        if v and not v.startswith("nvapi-"):
            raise ValueError(
                "Invalid NVIDIA_API_KEY format!\n\n"
                "The API key must start with 'nvapi-'.\n"
                "Get your API key from: https://build.nvidia.com/"
            )
        return v

    @classmethod
    def validate_settings(cls) -> None:
        """Validate settings and halt boot if invalid."""
        try:
            # Load .env file from config directory
            config_dir = Path(__file__).parent.resolve()
            env_path = config_dir / ".env"
            load_dotenv(dotenv_path=env_path)
            cls()
        except Exception as e:
            raise SystemExit(
                f"❌ CONFIGURATION ERROR:\n{str(e)}\n\n"
                "Setup Instructions:\n"
                "1. Copy 'config/.env.example' to 'config/.env'\n"
                "2. Add your Gemini API key to 'config/.env'\n"
                "3. Ensure the key starts with 'AIza'\n"
                "4. Get your API key from: https://aistudio.google.com/app/apikey"
            ) from e


# Load .env file from config directory
config_dir = Path(__file__).parent.resolve()
env_path = config_dir / ".env"

load_dotenv(dotenv_path=env_path)

# Create settings instance
try:
    settings = Settings()
except Exception as e:
    raise ValueError(
        "GEMINI_API_KEY is missing or invalid!\n\n"
        "Setup Instructions:\n"
        "1. Copy 'config/.env.example' to 'config/.env'\n"
        "2. Add your Gemini API key to 'config/.env'\n"
        "3. Ensure the key starts with 'AIza'\n"
        "4. Get your API key from: https://aistudio.google.com/app/apikey"
    ) from e

# Export settings instance
__all__ = ["settings", "Settings"]

# Made with Bob
